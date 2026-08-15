---
title: "雑なメモ・OCR・CSVを、LLMと一次情報で信頼できるデータ基盤に変える"
emoji: "🧠"
type: "tech"
topics: ["llm", "dataengineering", "ai", "testing"]
published: false
published_at: 2026-08-12 12:30
---

手元のデータが最初からきれいなら、データ基盤づくりはそれほど難しくない。

実際にはそうならない。

例えば業務データなら、同じ対象がこんな形で混在する。

```text
customer_name: 株式会社ABC
customer_name: (株)ABC
customer_name: ABC Co., Ltd.

part_no: AB-0123
part_no: AB0123
part_no: 0123

equipment: Line-3
machine: 3号機
asset_name: LINE03

result: OK
result: 合格
result: PASS
result: 1
```

これは異常なデータではない。

Excel、CSV、OCR、旧システム、メール添付、手入力、外部サービスのexportを数年つなげれば、普通にこうなる。

人間には同じ意味だと分かる。しかしそのままでは、検索、集計、JOIN、重複除去、機械学習、AIエージェントの入力には使いにくい。

ここでLLMはかなり役に立つ。

表記揺れを見つける。自由記述をフィールドへ分解する。候補となるIDやカテゴリを抽出する。似たレコードをまとめる。JSON Schemaに合わせて構造化候補を返す。

OpenAI APIもStructured Outputsとして、JSON Schemaに沿う構造化出力を公式に提供している。

https://platform.openai.com/docs/api-reference

しかし、**構造化できたことと、正しいデータになったことは別である。**

LLMがもっともらしく `AB0123` と `0123` を同じ品番だと判断しても、本当に同一品かは別問題だ。旧番と新番かもしれないし、工場ごとに意味が違うかもしれない。

LLMの出力をそのまま正準DBへ書けば、誤った補完や誤統合を高速に量産できる。

そこで今回のケーススタディでは、雑な入力を一気に「きれいなCSV」にするのではなく、

```text
雑な入力
↓
LLM / OCRで候補化・構造化
↓
一次情報でidentityを確認
↓
正準モデルへ分解
↓
重複・衝突・参照整合を機械検証
↓
安全なものだけ採用
↓
APIとして再利用
```

という順番でデータ基盤を作った。

この記事の主題はCSV importerではない。

**LLM/AIを使って、長年たまった雑なデータを「再利用できるデータ資産」へ変えるとき、どこをAIに任せ、どこから先を一次情報と機械検証に任せるべきか**である。

ケーススタディには、公開リポジトリ `KAFKA2306/books` を使う。題材は書誌データだが、扱っている問題はマスタ統合、identity、provenance、重複、分類、配布APIであり、顧客マスタ、設備台帳、商品マスタ、研究データにもそのまま持ち出せる。

一次情報:

- Repository: https://github.com/KAFKA2306/books
- 初期データモデル: https://github.com/KAFKA2306/books/pull/2
- OCR由来60件の統合: https://github.com/KAFKA2306/books/pull/3
- Kindle XML 685件の統合: https://github.com/KAFKA2306/books/pull/16
- NDL/NDC分類: https://github.com/KAFKA2306/books/pull/18
- 書誌表示正規化: https://github.com/KAFKA2306/books/pull/46
- collision audit: https://github.com/KAFKA2306/books/pull/52
- 非衝突データだけを採用: https://github.com/KAFKA2306/books/pull/53
- 書き込み前診断: https://github.com/KAFKA2306/books/pull/43

## 最初に決めるのは「AIモデル」ではなく、何を同一とみなすか

最初のデータには455件の入力があった。

PR #2では、それを414作品へ統合した。

https://github.com/KAFKA2306/books/pull/2

ここで重要なのは、455行を455entityとしてDBへ入れなかったことだ。

同じ対象でも、作品そのもの、版、実際の所蔵は意味が違う。

そこで最初から、

```text
Work    = 作品
Edition = ISBN・版・形式
Holding = 実際の所蔵
```

へ分けた。

後にKindle履歴を取り込む段階では `Acquisition` も分離した。

```text
作品として同じ
≠
同じ版
≠
実際に所有している
≠
取得履歴がある
```

これは業務データでも同じである。

```text
企業
≠
事業所
≠
設備
≠
設備に対する保全履歴
```

```text
製品
≠
品番
≠
Lot
≠
検査結果
```

**AIで正規化を始める前に、identityの境界を決める。**

ここが最初のデータ基盤設計だった。

## OCRで60件読めても、60件追加してはいけない

次にOCR由来の60件を追加した。

結果は「60件追加」ではなかった。

PR #3の確定値では、

- 60件を処理
- 24件は既存所蔵との重複として追加停止
- 36件を新規所蔵として追加
- 35件の新規Workを作成
- 61件のISBNを検証済みEditionとして登録

となった。

https://github.com/KAFKA2306/books/pull/3

ここで重要なのは、OCR精度そのものではない。

**AI/OCRが60件を読めたとしても、正準DBへ60件追加してよいとは限らない。**

入力を高速化するのがAIの価値なら、追加してはいけない24件を止めるのがデータ基盤の価値である。

企業マスタなら同一法人、設備台帳なら同一asset、商品マスタなら旧品番と新規登録候補の衝突が同じ問題になる。

## LLMには「正解」ではなく「候補」を作らせる

雑な自由記述を構造化する仕事はLLMと相性がいい。

例えば、次は説明用の架空例である。

```text
ABC-1200 3号機 8/1 圧力異常 要確認
```

LLMに、

```json
{
  "equipment_model_candidate": "ABC-1200",
  "machine_no_candidate": 3,
  "date_candidate": "2026-08-01",
  "event_candidate": "圧力異常",
  "status_candidate": "review"
}
```

のような候補を作らせることはできる。

ここまではLLMに向いている。

しかし、`ABC-1200` がasset master上のどのequipment_idなのか、3号機がライン番号なのか装置番号なのか、8/1が何年なのかは、周辺データや一次情報なしには確定できない。

だからcandidateとcanonicalを分ける。

`books` の継続正規化でも、一括の推測置換を禁止し、ISBN、出版社公式、国立国会図書館などで確認できるものだけを採用する運用にしている。

https://github.com/KAFKA2306/books/issues/25

一意に決められない場合は保留する。

authorityは、

```text
LLMの候補
< 一次情報
< 正準モデルの整合性
< CIで検証された現在状態
```

とした。

LLMは強力なcandidate generatorだが、master data authorityにはしない。

## 「文字列をきれいにする」だけではデータ基盤にならない

国立国会図書館のメタデータ流通ガイドラインは、タイトル、巻次、シリーズタイトル、版を独立した項目として扱う。

https://ndlsearch.ndl.go.jp/guideline/main

DC-NDL（RDF）ver.3.0も、書誌情報を構造化された項目として定義している。

https://ndlsearch.ndl.go.jp/renkei/dcndl/version3

つまり正規化は、

```text
汚い文字列
→
きれいな文字列
```

だけでは足りない。

本質は、

```text
一つのセルに混ざった複数の意味
→
意味ごとのフィールド / entityへ分離
```

である。

業務データなら、

```text
"ABC-1200 / 3号機 / 2026-08-01 / 圧力異常"
```

を単に整形するのではなく、

```text
asset_id
machine_no
event_date
event_type
source_record_id
```

へ分ける。

この境界を決めるのがschemaであり、LLMはそのschemaへ入力を寄せる補助になる。

## 690行の履歴も、そのまま690件の「所有物」にはしなかった

さらにKindleの実データを投入した。

PR #16の入力監査では、raw XMLの `meta_data` が690件あった。

完全重複5件を除き、685レコードになった。

内訳は、

```text
purchase           455
sample             204
prime               10
kindle_dictionary    1
unknown              15
```

だった。

https://github.com/KAFKA2306/books/pull/16

ここでも685件を同じ意味で扱っていない。

PurchaseだけをHoldingへ反映し、Sample / Prime / Dictionary / unknownはAcquisitionとして履歴を残した。

これは一般化できる。

```text
問い合わせ
≠ 契約

見積
≠ 受注

試験実施
≠ 合格

検知
≠ 故障確定
```

LLMは曖昧な入力にも何らかのラベルを返せる。

だからこそ、**null、unknown、review、ambiguousを正規状態として残せるデータモデル**が必要になる。

## AIで分類するより、一次情報から分類を生成できるならその方が強い

カテゴリ分類にも同じ境界を置いた。

PR #18では、国立国会図書館サーチのAPIからNDCを取得し、明示的なNDC→カテゴリmappingで分類する実装を追加した。

https://github.com/KAFKA2306/books/pull/18

NDL Search API仕様:

https://ndlsearch.ndl.go.jp/help/api/specifications

ISBNが確認済みならISBN一致を優先する。

ISBNがない場合は書名類似度0.97以上のみ採用する。

候補カテゴリが競合した場合は `ambiguous` として未分類のまま残す。

これはLLMに「分類して」と頼むより地味である。

しかし、後から

```text
なぜこのレコードはこのカテゴリになったのか
```

を追跡できる。

AIが便利になるほど、**説明可能な決定論レイヤーをどこに残すか**がデータ基盤の品質を決める。

## 一次情報で正しくても、そのまま書くと壊れることがある

もっと重要な失敗もあった。

一次書誌で確認できた正しい正規化候補でも、既存データへ適用するとidentity collisionが起きるケースがあった。

PR #52では、正規化候補によって既存Workの `title_key` が衝突する問題を検出し、修正を強行せずcollision diagnosticを追加した。

https://github.com/KAFKA2306/books/pull/52

続くPR #53では、一次情報で確認した候補をcollision auditに通し、衝突しないものだけを採用した。

https://github.com/KAFKA2306/books/pull/53

つまり、

```text
一次情報で正しい
```

と

```text
現在のDBへ安全に適用できる
```

は別問題である。

LLMに検索や照合を任せても、この最後の整合性検査は消えない。

## dry-runは主役ではなく、最後の安全弁

`books` には、入力CSVをcanonicalへ書き込まずに、各行がどの状態になるかを返す診断がある。

```text
existing_holding
safe_new_work
safe_new_edition
invalid_isbn
insufficient_metadata
duplicate_in_batch
review_similar_title
```

実装:
https://github.com/KAFKA2306/books/blob/main/src/migration-diagnosis.mjs

テスト:
https://github.com/KAFKA2306/books/blob/main/tests/migration-diagnosis.test.mjs

Browser版:
https://github.com/KAFKA2306/books/pull/43

Browser版は選択したCSVをbrowser memory内で処理し、公開catalogだけを取得する。ユーザーのCSV自体をuploadしない。

dry-runの価値は「CSV importerが安全」だからではない。

**LLMや自動処理が大量に作った候補を、正準データへ入れる直前にもう一度止められる**ことにある。

## 最終的に作りたいのは「きれいなCSV」ではなく、再利用できる基盤

正規化したデータをUIで表示して終わりにはしなかった。

PR #4では、同じ正準catalogからversioned JSON/CSV APIを生成し、件数、bytes、SHA-256をmanifestで監査する構成にした。

https://github.com/KAFKA2306/books/pull/4

PR #46では、raw値を残しながら公開API/UI用のdisplay fieldを正規化した。

https://github.com/KAFKA2306/books/pull/46

```text
raw
↓
candidate
↓
verified canonical
↓
API / UI / agent / analysis
```

という再利用経路ができる。

ここまで来ると、本棚アプリ固有の話ではない。

CRMの顧客名、設備台帳、商品マスタ、研究データ、経費履歴、文書OCR、社内Excelでも同じ構造になる。

## LLM時代のデータ基盤は、この7層にすると扱いやすい

今回の実装を一般化すると、次の7層になる。

### 1. Rawを確保する

CSV、Excel、XML、画像、OCR、ログ、exportを入力として扱う。元データの由来を失わない。

### 2. LLMに候補を作らせる

抽出、分割、表記揺れ検出、検索query生成、schemaへの変換を任せる。

### 3. 一次情報でidentityを確定する

公式ID、マスタ、出版社、公的API、メーカー仕様など、その領域のauthorityを使う。

### 4. Canonical modelへ分解する

1行を1entityと決めつけず、意味ごとにentityとrelationへ分ける。

### 5. 決定論的gateを通す

duplicate、ID validity、referential integrity、collision、thresholdをコードで検証する。

### 6. Ambiguousを無理に埋めない

unknown / review / ambiguousを正規状態として残す。

### 7. APIとprovenanceへ変える

人間が見ても、分析コードが読んでも、AIエージェントが再利用しても、同じ意味を取得できる形で配布する。

この順番なら、LLMはデータ整備の速度を上げられる。

一方でLLMの誤りが、そのまま正準DBの誤りになることを防げる。

## AIに全部任せるのではなく、AIが働ける土台を作る

LLMが登場する前、雑なデータを整える仕事はコストが高かった。

表記揺れを探し、フィールドを分け、重複を調べ、外部マスタを照合し、分類し、例外を人間へ戻す。

その多くをAIは高速化できる。

だから今まで放置していたExcel、CSV、OCR、旧システムexportにも、再び価値が出てくる。

ただし、LLMへ全部渡して「きれいなJSONが返ったから完成」とすると、データ基盤にはならない。

必要なのは、

```text
AIが候補を大量に作れること
×
一次情報で確定できること
×
コードが危険な変更を止めること
×
provenanceを後から追えること
```

である。

**AI時代に価値が上がるのは、データを生成する能力だけではない。雑な過去データを、AIが安全に使える正準データへ変換する能力である。**