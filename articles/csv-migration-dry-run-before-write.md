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

```text
1Q84村上春樹
animal farmオーウェル
インベスターZ(1)
To LOVEる―とらぶる― モノクロ版【期間限定無料】 1 (ジャンプコミックスDIGITAL)
1984 / Kindle
一九八四年 / 紙
```

メモ、OCR、購入履歴、CSV、XML、Webサービスのexport。

人間には意味が分かるが、そのままでは検索にも集計にもAIにも使いにくいデータが大量に残る。

ここでLLMはかなり役に立つ。

表記揺れを見つける。タイトルと著者を分ける。巻・版・シリーズらしき情報を抽出する。似たレコードを候補として並べる。構造化候補をJSONとして返す。

OpenAIのStructured Outputsも、JSON Schemaに沿った構造化出力をモデルへ要求できる仕組みを公式に提供している。

https://developers.openai.com/api/docs/guides/structured-outputs

しかし、**構造化できたことと、正しいデータになったことは別である。**

LLMがもっともらしく整えたタイトルをそのまま正準DBへ書けば、誤った補完、別版の混同、既存レコードとの衝突まで高速に量産できる。

そこで `KAFKA2306/books` では、雑な入力を一気に「きれいなCSV」にするのではなく、

```text
雑な入力
↓
候補化・構造化
↓
一次情報で同定
↓
正準モデルへ分解
↓
重複・衝突・意味を機械検証
↓
安全なものだけ採用
↓
APIとして再利用
```

というデータ基盤に変えていった。

この記事の主題はCSV importerではない。

**LLM/AIを使って、雑な個人データや業務データを「再利用できるデータ資産」へ変えるとき、どこをAIに任せ、どこから先を機械検証と一次情報に任せるべきか**である。

ケーススタディの一次情報はすべて公開している。

- Repository: https://github.com/KAFKA2306/books
- 初期データモデル: https://github.com/KAFKA2306/books/pull/2
- OCR由来60件の統合: https://github.com/KAFKA2306/books/pull/3
- Kindle XML 685件の統合: https://github.com/KAFKA2306/books/pull/16
- NDL/NDC分類: https://github.com/KAFKA2306/books/pull/18
- 書誌表示正規化: https://github.com/KAFKA2306/books/pull/46
- collision audit: https://github.com/KAFKA2306/books/pull/52
- 非衝突データだけを採用した例: https://github.com/KAFKA2306/books/pull/53
- 書き込み前診断: https://github.com/KAFKA2306/books/pull/43

## 最初にあったのは「DB」ではなく、455件の雑な入力だった

最初の本棚データには455件の入力があった。

PR #2では、それを414作品へ統合した。

https://github.com/KAFKA2306/books/pull/2

ここで重要なのは、455行を455冊としてDBへ入れなかったことだ。

同じ作品でも、

- 上下巻
- 版違い
- 雑誌号
- 電子版
- 紙版

が混ざる。

そこで最初から、

```text
Work    = 作品
Edition = ISBN・版・形式
Holding = 実際の所蔵
```

へ分けた。

後にKindle履歴を取り込む段階では `Acquisition` も分離した。

このモデルがあることで、

```text
作品として同じ
≠
同じ版
≠
実際に所有している
≠
一度取得履歴がある
```

を区別できる。

**AIでデータ整理を始める前に、何を同一とみなすかを決める。**

ここが最初のデータ基盤設計だった。

## OCRの60冊を入れたら、24件は「追加しない」が正解だった

次にKindle蔵書スクリーンショット由来の60件を追加した。

結果は、60件追加ではなかった。

PR #3の確定値では、

- 60件を処理
- 24件は既存所蔵との重複として停止
- 36件を新規所蔵として追加
- 35件の新規Workを作成
- 61件のISBNを検証済みEditionとして登録

となった。

https://github.com/KAFKA2306/books/pull/3

OCRには誤りもあった。

PRには、`メタスキル`、`宗教認知科学入門`、`身体性認知とは何か`、`投資は金利が9割`、`世界大激変` などの修正が記録されている。

ここで得た教訓は単純だった。

**AI/OCRが60件読めたとしても、DBへ60件追加してよいとは限らない。**

AIの価値は入力速度を上げることにある。

データ基盤の価値は、追加しない24件を正しく止められることにある。

## LLMには「正解」ではなく「候補」を作らせる

雑な入力に対してLLMが得意なのは、意味を推測して候補を作ることだ。

例えば、

```text
1Q84村上春樹
```

から、

```json
{
  "title_candidate": "1Q84",
  "author_candidate": "村上春樹"
}
```

という候補を作ることはできる。

しかし、これをそのままcanonicalへ書かない。

`books` の継続正規化Issueでは、推測による一括置換を禁止し、ISBN、出版社公式、国立国会図書館などで1冊ずつ確認するルールにした。

https://github.com/KAFKA2306/books/issues/25

実際に、

- `1Q84村上春樹` → `1Q84` / 著者 `村上春樹`
- `animal farmオーウェル` → `Animal Farm` / 著者 `ジョージ・オーウェル`
- `5路盤問題集、囲碁文庫` → `画期的囲碁上達法 五路盤問題集`

のような正規化が記録されている。

一方で、版を一意に決められない、同名異書がある、略称しかない場合は保留する。

つまりauthorityは、

```text
LLMの推測
< 一次書誌
< 正準モデルの整合性
< CIで検証された現在状態
```

である。

LLMは強力なcandidate generatorだが、master data authorityにはしない。

## 一次情報を引くと、「タイトルをきれいにする」以上の設計が必要になる

国立国会図書館の2026年版メタデータ流通ガイドラインでは、タイトル、巻次、シリーズタイトル、版を別項目として扱う。

https://ndlsearch.ndl.go.jp/guideline/main

DC-NDL（RDF）ver.3.0でも、`title`、`volume`、`seriesTitle`、`edition` は別の書誌要素として定義されている。

https://ndlsearch.ndl.go.jp/renkei/dcndl/version3

これは今回のデータ整理と一致した。

例えば、

```text
To LOVEる―とらぶる― モノクロ版【期間限定無料】 1 (ジャンプコミックスDIGITAL)
```

を、単に文字列置換して短くするのではない。

PR #53では、出版社公式書誌で確認したうえで、表示上のWork名を `To LOVEる―とらぶる―` へ正規化した。

https://github.com/KAFKA2306/books/pull/53

「期間限定無料」「1」「ジャンプコミックスDIGITAL」は、作品そのもののidentityとは別の情報である。

**雑な文字列をきれいにするのではなく、意味の違う情報を別フィールドへ戻す。**

これが正規化の本体である。

## Kindle XML 690行も、そのまま690冊にはしなかった

さらにKindleの実データを投入した。

PR #16の入力監査では、raw XMLの `meta_data` が690件あった。

そこから完全重複5件を除き、685レコードになった。

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

ここでも「685件の本」とは扱っていない。

PurchaseだけをHoldingへ反映し、Sample / Prime / Dictionary / unknownはAcquisitionとして履歴を残した。

Sampleを「持っている本」と解釈してしまえば、データ件数は増える。

しかし意味は壊れる。

LLM時代のデータ整備では、この問題がさらに重要になる。

モデルは曖昧なデータにも何らかの答えを返せる。

だからこそ、**null、unknown、review、ambiguousを消さないデータモデル**が必要になる。

## AIで分類するより、一次情報から分類を生成する

本のカテゴリ分類にも同じ境界を置いた。

PR #18では、国立国会図書館サーチのOpenSearch APIからNDCを取得し、明示的なNDC→カテゴリmappingで分類している。

https://github.com/KAFKA2306/books/pull/18

一次API仕様はこちら。

https://ndlsearch.ndl.go.jp/help/api/specifications

ISBNが確認済みならISBN一致を優先する。

ISBNがない場合は書名類似度0.97以上のみ採用する。

候補カテゴリが競合した場合は `ambiguous` として未分類のまま残す。

これはLLM分類より地味である。

しかし、後から

```text
なぜこの本が「投資・金融」なのか
```

を追跡できる。

AIが便利になるほど、**説明可能な決定論レイヤーをどこに残すか**がデータ基盤の品質を決める。

## 一次情報で正しくても、そのまま書くと壊れることがある

もっと重要な失敗もあった。

書誌を確認して、正しいタイトルへ直す。

それでも安全とは限らなかった。

PR #52では、正規化候補を適用すると既存Workと `title_key` が衝突するケースが見つかった。

https://github.com/KAFKA2306/books/pull/52

そこで修正を強行せず、collision diagnosticを追加した。

続くPR #53では、出版社公式書誌で確認した5候補のうち、`寄生獣` だけが既存の正準Workと衝突したため採用しなかった。

https://github.com/KAFKA2306/books/pull/53

これは重要である。

```text
一次情報で正しい
```

と

```text
現在のDBへ安全に適用できる
```

は別問題だ。

LLMに一次情報検索までさせても、この最後の整合性検査は消えない。

## だからdry-runは記事の主役ではなく、最後の安全弁になる

以前は、この仕組みを「CSV migrationのdry-run」として説明していた。

しかし本質的には、これはもっと大きなパイプラインの最後にある。

`books` には、入力CSVをcanonicalへ書き込まずに、各行が

```text
existing_holding
safe_new_work
safe_new_edition
invalid_isbn
insufficient_metadata
duplicate_in_batch
review_similar_title
```

のどれになるかを返す診断がある。

実装:
https://github.com/KAFKA2306/books/blob/main/src/migration-diagnosis.mjs

テスト:
https://github.com/KAFKA2306/books/blob/main/tests/migration-diagnosis.test.mjs

Browser版:
https://github.com/KAFKA2306/books/pull/43

Browser版は選択したCSVをbrowser memory内で処理し、公開catalogだけを取得する。ユーザーのCSV自体をuploadしない。

dry-runの価値は「CSV importerが安全」だからではない。

**AIや自動処理が作った候補を、正準データへ入れる直前にもう一度止められる**ことにある。

## 最終的に作りたいのは「きれいなデータ」ではなく、再利用できる基盤

正規化したデータを一度UIで表示して終わりにはしなかった。

PR #4では、同じ正準catalogからversioned JSON/CSV APIを生成し、件数・bytes・SHA-256をmanifestで監査する構成にした。

https://github.com/KAFKA2306/books/pull/4

さらにPR #46では、書名・著者・カテゴリのraw値を残しながら、公開API/UI用のdisplay fieldを正規化した。

https://github.com/KAFKA2306/books/pull/46

つまり、

```text
raw
↓
normalized candidate
↓
verified canonical
↓
API / UI / agent / analysis
```

という再利用経路ができる。

ここまで来ると、本棚アプリの話ではない。

CRMの顧客名、設備台帳、研究データ、商品マスタ、経費履歴、写真メタデータ、社内Excelでも同じ構造になる。

## LLM時代のデータ基盤は、この7層にすると扱いやすい

今回の実装から、一般化すると次の7層になる。

### 1. Rawを確保する

メモ、OCR、CSV、XML、画像、exportをまず入力として扱う。

### 2. LLMに候補を作らせる

抽出、分割、表記揺れ検出、検索query生成、schemaへの変換を任せる。

### 3. 一次情報でidentityを確定する

ISBN、公式ID、出版社、行政・公的APIなどをauthorityにする。

### 4. Canonical modelへ分解する

1行を1entityと決めつけず、意味ごとにWork / Edition / Holding / Acquisitionのように分ける。

### 5. 決定論的gateを通す

duplicate、ID validity、referential integrity、collision、thresholdをコードで検証する。

### 6. Ambiguousを無理に埋めない

unknown / review / ambiguousを正規状態として残す。

### 7. APIとprovenanceへ変える

誰が見ても、AIが再利用しても、同じ意味を取得できる形で配布する。

この順番なら、LLMはデータ整備の速度を大きく上げられる。

一方でLLMの誤りが、そのまま正準DBの誤りになることを防げる。

## AIに全部任せるのではなく、AIが働ける土台を作る

LLMが登場する前、雑なデータをきれいにする仕事はコストが高すぎた。

タイトルを1件ずつ確認し、フィールドを分け、重複を探し、外部書誌を引き、分類し直す。

その多くをAIは高速化できる。

だから今まで放置していたExcel、CSV、メモ、OCR、exportにも、再び価値が出てくる。

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
