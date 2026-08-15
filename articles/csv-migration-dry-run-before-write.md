---
title: "雑データをLLM時代のデータ基盤に変える。455件→414件、60件中24件を止めた実例"
emoji: "🧠"
type: "tech"
topics: ["llm", "dataengineering", "ai", "testing"]
published: false
published_at: 2026-08-12 12:30
---

生成AIを使えば、汚いCSVやOCRをJSONにすること自体はかなり簡単になった。

しかし、データ基盤づくりで本当に難しいのはそこではない。

**AIが作った「もっともらしい候補」を、何件まで正準データとして採用してよいのか。**

今回のケーススタディ `KAFKA2306/books` では、実データを処理した結果がかなり分かりやすかった。

| 実処理 | 入力 | 自動処理・採用 | 止めた / 別扱いにした |
|---|---:|---:|---:|
| 初期データ統合 | 455件 | 414 Work | 41件を同一作品側へ統合 |
| OCR由来データ追加 | 60件 | 36件を新規所蔵として追加 | 24件を既存所蔵として追加停止 |
| Kindle XML取込 | 690行 | 685 acquisition records | 完全重複5行を除去 |
| NDL分類の直近25件バッチ | 25件 | 9件を採用 | 16件は自動採用しなかった |
| 書誌タイトル修正候補 | 5件 | 4件を採用 | 1件をidentity collisionで停止 |

重要なのは、AIや自動化で**採用件数を最大化したことではない**。

60件中24件、つまり40%を「追加しない」と判断した処理がある。

直近の分類バッチでも25件中9件、36%しか自動採用していない。残り16件、64%は曖昧・候補なし・分類コードなし・provider errorとして確定を見送った。

これがこの記事の主題である。

> **LLM時代のデータ基盤では、AIに正解を生成させる能力より、AIが作った候補を正準データへ昇格させない能力が重要になる。**

ケーススタディ:

- Repository: https://github.com/KAFKA2306/books
- 455件→414 Work: https://github.com/KAFKA2306/books/pull/2
- OCR 60件の統合: https://github.com/KAFKA2306/books/pull/3
- Kindle XML 690行の取込: https://github.com/KAFKA2306/books/pull/16
- NDL/NDC分類実装: https://github.com/KAFKA2306/books/pull/18
- 直近の分類25件レポート: https://github.com/KAFKA2306/books/blob/main/data/category-enrichment-report.json
- collision gate: https://github.com/KAFKA2306/books/pull/52
- 5候補中4件だけを採用した実例: https://github.com/KAFKA2306/books/pull/53

## 455件を「455件の正解」にしなかった

最初にあったのは455件の入力だった。

PR #2では、この455件をそのまま455件のentityとして登録せず、**414 Workへ統合した**。

- 入力: 455件
- Work: 414件
- 統合された入力: 41件

https://github.com/KAFKA2306/books/pull/2

41 / 455、約9%は「入力行数」と「実体数」が一致しなかったことになる。

原因は単なる重複文字列ではない。

同じ作品でも、巻、版、形式、所蔵状態が異なる。

そこで、

```text
Work        作品そのもの
Edition     ISBN・版・形式
Holding     実際の所蔵
Acquisition 取得履歴
```

へ意味を分離した。

これは本に限らない。

```text
顧客 ≠ 契約 ≠ 請求 ≠ 問い合わせ
製品 ≠ 品番 ≠ Lot ≠ 検査結果
設備 ≠ 部品 ≠ 故障イベント ≠ 保全作業
```

という業務データと同じ問題である。

**LLMに表記揺れを直させる前に、「何を同一entityとみなすか」を決めないと、きれいな誤データができる。**

## OCRで60件取れた。しかし40%は追加してはいけなかった

次に、スクリーンショットから構造化した60件を既存カタログへ統合した。

PR #3の実測結果はこうだった。

| 判定 | 件数 | 構成比 |
|---|---:|---:|
| 入力 | 60 | 100% |
| 既存所蔵として追加停止 | 24 | 40% |
| 新規所蔵として追加 | 36 | 60% |
| 新規Work | 35 | - |

https://github.com/KAFKA2306/books/pull/3

もし「OCRで60件読めた」ことを成功条件にして、そのまま60件を書き込んでいたら、24件は二重登録側へ進んでいた。

つまりこのケースでは、**入力精度よりprecheckの方がデータ品質への寄与が大きい**。

LLMも同じである。

Structured Outputsを使えば、非構造データをJSON Schemaへ合わせて出力させることができる。OpenAIも非構造データからの構造化を主要ユースケースとして説明している。

https://openai.com/index/introducing-structured-outputs-in-the-api/

ただしOpenAI自身も、Structured OutputsはJSON Schemaへの適合を強くできても、**JSON内部の値そのものの誤りまでは防がない**と明記している。

だから、

```text
LLM output
=
canonical data
```

にはしない。

```text
LLM output
=
candidate
```

とする。

## 690行を685件にしただけではない。685件を5種類の意味へ分けた

次の実例はKindle XMLだった。

PR #16では、raw XMLの `meta_data` が690行あった。

- raw: 690行
- 完全重複: 5行
- 正規化後: 685 records

https://github.com/KAFKA2306/books/pull/16

完全重複の除去率だけなら5 / 690、約0.7%しかない。

しかし、この処理の価値は重複除去ではない。

685 recordsの意味を調べると、次のように分かれた。

| origin | 件数 | 扱い |
|---|---:|---|
| purchase | 455 | 所有としてHoldingへ反映 |
| sample | 204 | Acquisitionのみ |
| prime | 10 | Acquisitionのみ |
| kindle_dictionary | 1 | Acquisitionのみ |
| unknown | 15 | Acquisitionのみ |

685件中、Purchaseは455件で約66%。Sampleだけで204件、約30%あった。

もし「Kindle XMLに存在する = 所有」と単純化すると、少なくともSample 204件を所有物として誤分類する。

これは業務データなら、

```text
見積 = 受注
問い合わせ = 契約
アラート = 故障
試験実施 = 合格
```

と扱うのと同じである。

**雑データを整えるとは、欠損を埋めることではない。異なる意味を分離することである。**

## 「AIなら全部分類できる」は、実データ25件で成立しなかった

カテゴリ分類では、LLMの自由分類ではなく、国立国会図書館サーチからNDCを取得し、明示ルールでカテゴリへ変換する経路を作った。

実装:
https://github.com/KAFKA2306/books/pull/18

NDL Search API公式仕様:
https://ndlsearch.ndl.go.jp/help/api/specifications

国立国会図書館は2026年3月31日付の外部提供インタフェース仕様書 第1.4版を掲載しており、OpenSearchを含む検索APIを提供している。

直近の `data/category-enrichment-report.json` は2026-08-15に生成された25件バッチで、結果はこうだった。

| outcome | 件数 |
|---|---:|
| attempted | 25 |
| accepted | 9 |
| ambiguous | 1 |
| no_ndc | 1 |
| no_candidate | 7 |
| provider_error | 7 |

https://github.com/KAFKA2306/books/blob/main/data/category-enrichment-report.json

自動採用は9 / 25 = **36%**。

逆に16 / 25 = **64%は、そのrunでは正準カテゴリへ自動昇格しなかった**。

ここで `provider_error` 7件を「データが間違っている」とは扱っていない。外部providerが失敗しただけなので、失敗状態を残して再試行できるようにする。

`ambiguous` も無理に多数決で埋めない。

`no_candidate` もLLMに推測させて穴埋めしない。

データ基盤では、

```text
unknown
ambiguous
no_candidate
provider_error
review
```

も正常な状態である。

## 一次情報で正しい5候補でも、1件は書き込めなかった

さらに重要なのが、書誌タイトルの修正で起きたcollisionである。

出版社公式などの一次情報で確認した5候補を適用しようとしたところ、1候補が既存の正準Workと `title_key` で衝突した。

PR #52では、この種の衝突をfail-closedで検出するdiagnosticを追加した。

https://github.com/KAFKA2306/books/pull/52

続くPR #53では、5候補中、非衝突の4件だけを採用し、1件は適用しなかった。

- source-backed candidates: 5
- applied: 4
- collisionで停止: 1

https://github.com/KAFKA2306/books/pull/53

つまり、**一次情報で正しいことと、現在のDBへ安全に書けることも別問題**である。

```text
LLMがもっともらしい
↓
一次情報で確認できた
↓
それでもDB整合性で止まることがある
```

ここまでgateを分けて初めて、AIをデータ整備へ安全に組み込める。

## LLMには「候補生成」を任せる

ここでLLMの役割が明確になる。

得意なのは、例えば次である。

- OCRや自由記述からfield candidateを抽出する
- 表記揺れ候補を列挙する
- entity分割候補を作る
- 検索queryを作る
- JSON Schemaへ合わせる
- 人間レビューが必要な候補を説明する

一方、正準データへの昇格条件は別レイヤーに置く。

```text
raw / OCR / CSV / XML
        ↓
LLM candidate
        ↓
primary-source lookup
        ↓
canonical schema
        ↓
duplicate / ID / collision / reference gate
        ↓
safe write or review
        ↓
API / UI / agent
```

国立国会図書館のDC-NDL（RDF）ver.3.0も、書誌情報と個体情報を区別し、構造化されたメタデータ項目として表現している。

https://ndlsearch.ndl.go.jp/renkei/dcndl/version3

2026年4月1日からver.3系の提供が開始されている。

https://ndlsearch.ndl.go.jp/news/20260401_dcndl_ver3

ここから得られる一般則は、**1セルをきれいにするのではなく、1セルに混ざっていた意味を別entity・別fieldへ戻す**ことである。

## 実測値を見ると、「全部自動化」がKPIではない

今回の5つの実測を並べると、共通点が見える。

```text
455 inputs
→ 414 Works
→ 41 inputsは別entityとして増やさなかった

60 OCR records
→ 36 added
→ 24 duplicates blocked

690 XML rows
→ 685 acquisition events
→ 455 purchase / 204 sample / 26 other

25 classification attempts
→ 9 accepted
→ 16 not auto-promoted

5 verified normalization candidates
→ 4 applied
→ 1 collision blocked
```

データ整備AIのKPIを「何件自動処理できたか」だけにすると、危険な方向へ最適化される。

見るべきなのは少なくとも、

- candidate数
- automatically accepted数
- duplicateとして止めた数
- ambiguousとして保留した数
- external evidenceが取れなかった数
- collisionで止めた数
- 人間reviewへ送った数

である。

**拒否率・保留率も品質指標になる。**

## 雑な過去データは、AI時代になって価値が上がった

以前なら、数百・数千件のExcel、OCR、CSV、XML、メール由来データを人間が一件ずつ整理するコストは高かった。

LLMによって、候補生成のコストは急激に下げられる。

だから、これまで放置されていたデータを再利用できる可能性は大きくなった。

ただし、価値を作るのはLLM単体ではない。

```text
LLMが候補を大量に作る
×
一次情報でidentityを確認する
×
canonical schemaで意味を分離する
×
deterministic gateが危険な変更を止める
×
provenanceを残す
```

という組み合わせである。

今回の実データでは、60件中24件を止め、25件中16件を自動分類せず、一次情報で確認済みの5修正候補のうち1件もcollisionで止めた。

**AI時代のデータ基盤で重要なのは、「全部埋められること」ではない。分からないものを分からないまま残し、確定できるものだけを正準データへ昇格させられることだ。**
