---
title: "LLMで雑データを整えると、なぜデータ基盤が壊れるのか。455件→414件、60件中24件を止めた実例"
emoji: "🧠"
type: "tech"
topics: ["llm", "dataengineering", "ai", "testing"]
published: false
published_at: 2026-08-12 12:30
---

生成AIを使えば、OCR、CSV、Excel、メール、自由記述からJSONを作ること自体はかなり簡単になった。

しかし、それはデータ基盤の入口を安くしただけである。

本当に難しいのは、その次だ。

**LLMが作った「もっともらしい候補」のうち、どれを事実として正準データへ昇格させてよいのか。**

この問題は、単なるdata cleaningではない。

- 同じ文字列は同じentityなのか
- 違う文字列でも同じentityなのか
- 1行に複数の意味が混ざっていないか
- 欠損を補完してよいのか、それともunknownのまま残すべきか
- 外部情報で正しいと確認できても、既存masterと衝突しないか
- その値がどの入力・根拠・変換から生まれたか後から説明できるか

という、**identity、semantics、provenance、write policyの問題**である。

## LLMは「データ整備」を楽にしたのではなく、検証をボトルネックにした

従来、雑なデータの整備で高かったのは候補を作るコストだった。

人間が1行ずつ読み、列へ分け、表記揺れを探し、検索し、似たレコードを比較する必要があった。

LLMはこの部分を大幅に安くできる。

OpenAIのStructured Outputsは、非構造入力からJSON Schemaに沿った構造化出力を生成する用途を明示している。

https://openai.com/index/introducing-structured-outputs-in-the-api/

一方でOpenAI自身も、Structured Outputsはschemaへの適合を保証できても、**JSON内部の値そのものの誤りまでは防がない**と明記している。

つまり、

```text
unstructured data
→ LLM
→ valid JSON
```

までが簡単になっても、

```text
valid JSON
→ true fact
→ safe canonical write
```

は別問題として残る。

むしろ候補を毎分何百件も生成できるようになるほど、誤った候補を止める仕組みの重要性は上がる。

**候補生成のスループットが上がると、verification capacityが新しい制約になる。**

## 問題1: 表記揺れより危険なのは「identityを間違えて統合すること」

例えば、

```text
株式会社ABC
(株)ABC
ABC Co., Ltd.
```

は同一法人かもしれない。

しかし、

```text
AB-0123
AB0123
0123
```

が同じ品番とは限らない。

工場ごとのlocal codeかもしれない。旧品番かもしれない。上位品番と子部品かもしれない。

LLMは文脈から「同じ可能性が高い」と候補を作れる。しかしmaster dataで最も危険なのは、別entityを誤って1つへ潰すことだ。

重複を残すfalse splitは後から統合できる場合がある。一方、false mergeは履歴、集計、JOIN、学習データまで一つのentityとして汚染する。

だから問題は「表記を統一できるか」ではなく、

> **どの証拠が揃えば、2つのrecordを同一entityと宣言してよいか**

になる。

## 問題2: 1行をきれいにしても、意味が混ざったままなら使えない

雑データでは、1行や1セルが1つの意味とは限らない。

```text
ABC-1200 / 3号機 / 2026-08-01 / 圧力異常 / 要確認
```

を、単に整形して

```text
ABC-1200 3号機 2026-08-01 圧力異常 要確認
```

にしてもデータ基盤にはならない。

必要なのは、

```text
asset_id
equipment_model
machine_no
event_date
event_type
review_state
source_record_id
```

のように、**意味の境界へ戻すこと**である。

本棚なら、

```text
作品
≠ 版
≠ 所有
≠ 取得履歴
```

製造なら、

```text
製品
≠ 品番
≠ Lot
≠ 測定
≠ 判定
```

営業なら、

```text
顧客
≠ 商談
≠ 見積
≠ 受注
≠ 請求
```

である。

**dirty stringをclean stringへ変えるだけではなく、混ざっていたsemanticsをentityとfieldへ分離する。**

ここがdata modelingの仕事になる。

## 問題3: AIは「分からない」を、それらしい値で埋められてしまう

従来のETLなら、変換できなければnullやerrorになることが多かった。

LLMは違う。

情報が足りなくても、もっともらしい候補を返せる。

これは便利だが、master dataでは危険でもある。

例えば、

```text
8/1 3号機 圧力異常
```

から、

```json
{
  "date": "2026-08-01",
  "machine_no": 3,
  "event": "pressure_anomaly"
}
```

という候補は作れる。

しかし年が入力に無ければ `2026-08-01` は推測かもしれない。3号機が設備番号かLine番号かも確定していない。

このとき良いデータ基盤は、穴を全部埋める基盤ではない。

```text
unknown
ambiguous
no_candidate
provider_error
review
```

を正常な状態として保存できる基盤である。

**欠損率を下げることと、事実性を上げることは同じではない。**

## 問題4: 誤りはその行で終わらず、下流へ連鎖する

Google ResearchのSambasivanらは、53人のhigh-stakes AI practitionerへの調査から、データ問題が下流で複合的な悪影響を生む現象を **Data Cascades** と呼んだ。

対象となった調査では、Data Cascadesは92%のprevalenceで観測され、invisible、delayed、compoundingになりやすいと報告されている。

https://research.google/pubs/everyone-wants-to-do-the-model-work-not-the-data-work-data-cascades-in-high-stakes-ai/

今回の記事はhigh-stakes AIそのものを扱うわけではない。しかし、問題の構造は同じである。

一度masterへ誤ったentity統合を入れると、その後の

```text
集計
→ API
→ dashboard
→ ML feature
→ RAG
→ agent action
```

が同じ誤りを再利用する。

入力1件の誤りが、利用者の数だけ増幅される。

Googleのproduction MLに関するData Validation研究も、入力データの誤りはtraining/inferenceの速度や精度改善の利益を打ち消し得るとして、**データをalgorithmやinfrastructureと同格のproduction assetとして扱う**べきだと論じている。

このvalidation systemはGoogle内のhundreds of product teamsで使われ、production dataを継続監視する設計として報告されている。

https://research.google/pubs/data-validation-for-machine-learning/

つまり、データ整備は「モデルを作る前の前処理」ではない。

**下流systemの品質を決めるproduction engineeringである。**

## 問題5: cleanな値だけ残すと、後から正しさを再評価できない

LLMが

```text
raw text
→ canonical value
```

へ変換したとき、canonical valueだけを保存すると、後から

- 元入力は何だったか
- どのmodel / ruleが変換したか
- どの外部sourceで確認したか
- いつ判断したか
- なぜ自動採用されたか

を追えなくなる。

W3C PROVはprovenanceを、dataを生み出すentity・activity・person等に関する情報として定義し、quality、reliability、trustworthinessを評価するために利用できるとしている。

https://www.w3.org/TR/prov-overview/

これはLLM時代にはさらに重要になる。

モデル、prompt、外部API、正規化ruleは将来変わる。

正準値だけではなく、

```text
source
candidate
evidence
decision
canonical result
```

をつなげておけば、後から再判定できる。

## だから課題は「AIで何件整形できるか」ではない

ここまでをまとめると、LLMによる雑データ整備の課題は次になる。

```text
候補を作れるか？
```

ではない。

```text
何を同一entityとみなすか？
どの値をfactへ昇格させるか？
曖昧なものを保留できるか？
既存masterを壊さず書けるか？
判断根拠を後から追えるか？
```

である。

Googleの「Hidden Technical Debt in Machine Learning Systems」も、ML systemではdata dependencies、boundary erosion、undeclared consumersなどが継続的なtechnical debtを生むと指摘している。

https://papers.nips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html

一度だけCSVをcleanにして終わりではなく、**新しいデータが来るたびに同じ意味・同じ品質基準で判断できる仕組み**が必要になる。

NIST AI RMFも、AIのtrustworthinessをdesign/developmentだけでなくdeployment、use、test/evaluationを含むlifecycle全体で扱う枠組みを示している。

https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10

この観点から見ると、LLM data cleaningの完成条件は「JSONができた」ではない。

**継続的に検証できるdata productになったこと**である。

## では、実データではどれくらい止まるのか

ここからは公開リポジトリ `KAFKA2306/books` をケーススタディにする。

題材は書誌データだが、扱っている問題はmaster統合、identity、provenance、重複、分類、配布APIであり、顧客master、設備台帳、商品master、研究データにも持ち出せる。

実際に処理した数字は次の通りだった。

| 実処理 | 入力 | 自動処理・採用 | 止めた / 別扱いにした |
|---|---:|---:|---:|
| 初期データ統合 | 455件 | 414 Work | 41件を同一作品側へ統合 |
| OCR由来データ追加 | 60件 | 36件を新規所蔵として追加 | 24件を既存所蔵として追加停止 |
| Kindle XML取込 | 690行 | 685 acquisition records | 完全重複5行を除去 |
| NDL分類の直近25件バッチ | 25件 | 9件を採用 | 16件は自動採用しなかった |
| 書誌タイトル修正候補 | 5件 | 4件を採用 | 1件をidentity collisionで停止 |

一次情報:

- Repository: https://github.com/KAFKA2306/books
- 455件→414 Work: https://github.com/KAFKA2306/books/pull/2
- OCR 60件の統合: https://github.com/KAFKA2306/books/pull/3
- Kindle XML 690行の取込: https://github.com/KAFKA2306/books/pull/16
- NDL/NDC分類実装: https://github.com/KAFKA2306/books/pull/18
- 直近の分類25件レポート: https://github.com/KAFKA2306/books/blob/main/data/category-enrichment-report.json
- collision gate: https://github.com/KAFKA2306/books/pull/52
- 5候補中4件だけを採用した実例: https://github.com/KAFKA2306/books/pull/53

この数字で重要なのは、**自動化率が100%ではないことではなく、100%を目指していないこと**だ。

60件中24件、40%を「追加しない」と判断した処理がある。

直近の分類バッチでも25件中9件、36%しか自動採用していない。

一次情報で確認済みの修正候補ですら、5件中1件をDB整合性で止めた。

> **LLM時代のデータ基盤では、候補生成能力と同じくらい「正準データへ昇格させない能力」が重要になる。**

## 455件を「455件の正解」にしなかった

最初にあったのは455件の入力だった。

PR #2では、この455件をそのまま455 entityとして登録せず、414 Workへ統合した。

- 入力: 455件
- Work: 414件
- 統合された入力: 41件

https://github.com/KAFKA2306/books/pull/2

41 / 455、約9%は「入力行数」と「実体数」が一致しなかった。

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

**LLMに表記揺れを直させる前に、「何を同一entityとみなすか」を決めないと、きれいな誤データができる。**

## OCRで60件取れた。しかし40%は追加してはいけなかった

次に、スクリーンショットから構造化した60件を既存catalogへ統合した。

PR #3の実測結果はこうだった。

| 判定 | 件数 | 構成比 |
|---|---:|---:|
| 入力 | 60 | 100% |
| 既存所蔵として追加停止 | 24 | 40% |
| 新規所蔵として追加 | 36 | 60% |
| 新規Work | 35 | - |

https://github.com/KAFKA2306/books/pull/3

もし「OCRで60件読めた」を成功条件にして、そのまま60件を書き込んでいたら、24件は二重登録側へ進んでいた。

このケースでは、**入力速度を上げることより、書いてはいけない24件を止めることの方がmaster data品質には重要だった。**

Structured Outputsでschemaを守らせても、この重複判定は解決しない。

だから、

```text
LLM output = canonical data
```

にはせず、

```text
LLM output = candidate
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

685 recordsの意味は次のように分かれた。

| origin | 件数 | 扱い |
|---|---:|---|
| purchase | 455 | 所有としてHoldingへ反映 |
| sample | 204 | Acquisitionのみ |
| prime | 10 | Acquisitionのみ |
| kindle_dictionary | 1 | Acquisitionのみ |
| unknown | 15 | Acquisitionのみ |

685件中、Purchaseは455件で約66%。Sampleだけで204件、約30%あった。

もし「XMLに存在する = 所有」と単純化すると、少なくともSample 204件を所有物として誤分類する。

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

カテゴリ分類では、LLMの自由分類ではなく、国立国会図書館サーチからNDCを取得し、明示ruleでカテゴリへ変換する経路を作った。

実装:
https://github.com/KAFKA2306/books/pull/18

NDL Search API公式仕様:
https://ndlsearch.ndl.go.jp/help/api/specifications

直近の `data/category-enrichment-report.json` は2026-08-15に生成された25件batchで、結果はこうだった。

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

ここで `provider_error` 7件を「データが間違っている」とは扱わない。外部providerが失敗した状態として残し、再試行できるようにする。

`ambiguous` も無理に多数決で埋めない。

`no_candidate` もLLMに推測させて穴埋めしない。

このfail-closedな設計が、候補生成と正準化を分ける。

## 一次情報で正しい5候補でも、1件は書き込めなかった

さらに重要なのが、書誌タイトル修正で起きたidentity collisionである。

出版社公式などの一次情報で確認した5候補を適用しようとしたところ、1候補が既存の正準Workと `title_key` で衝突した。

PR #52では、この種の衝突をfail-closedで検出するdiagnosticを追加した。

https://github.com/KAFKA2306/books/pull/52

続くPR #53では、5候補中、非衝突の4件だけを採用し、1件は適用しなかった。

- source-backed candidates: 5
- applied: 4
- collisionで停止: 1

https://github.com/KAFKA2306/books/pull/53

つまり、

```text
LLMがもっともらしい
↓
一次情報で確認できた
↓
それでもDB整合性で止まることがある
```

**一次情報で正しいことと、現在のDBへ安全に適用できることも別問題**である。

## LLMには「候補生成」を任せる

ここまででLLMの役割が明確になる。

得意なのは、例えば次である。

- OCRや自由記述からfield candidateを抽出する
- 表記揺れ候補を列挙する
- entity分割候補を作る
- external search queryを作る
- JSON Schemaへ合わせる
- 人間reviewが必要な理由を説明する

一方、正準データへの昇格条件は別layerへ置く。

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

この構成なら、LLMを交換してもmaster dataのauthorityは変わらない。

## 「全部自動化」をKPIにしない

今回の実測を並べると共通点がある。

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

- generated candidates
- automatically accepted
- duplicate blocked
- ambiguous / review
- evidence unavailable
- provider error
- collision blocked
- human-reviewed
- later reverted

である。

**拒否率・保留率・rollback率も品質指標になる。**

自動化率100%は、品質100%を意味しない。

## 雑な過去データは、LLMによって初めて「再評価可能な資産」になった

以前なら、数百・数千件のExcel、OCR、CSV、XML、メール由来データを人間が一件ずつ整理するコストは高かった。

LLMによって、候補生成・分割・検索query作成・レビュー補助のコストは下げられる。

その結果、これまで「汚すぎて移行できない」と放置されていたデータを再評価できる範囲が広がった。

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
×
継続的にvalidationする
```

という組み合わせである。

今回の実データでは、60件中24件を止め、25件中16件を自動分類せず、一次情報で確認済みの5修正候補のうち1件もcollisionで止めた。

この「止めた数」は失敗数ではない。

**正準データを壊さなかった数である。**

AI時代のデータ基盤で重要なのは、「全部埋められること」ではない。

**分からないものを分からないまま残し、根拠が揃ったものだけを、既存データを壊さず、後から説明できる形で正準データへ昇格させられることだ。**
