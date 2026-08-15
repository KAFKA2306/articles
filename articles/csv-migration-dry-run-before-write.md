---
title: "LLMで雑データを整えると、なぜ壊れる？ 455件→414件、60件中24件を止めた実例"
emoji: "🧠"
type: "tech"
topics: ["llm", "dataengineering", "ai", "testing"]
published: false
published_at: 2026-08-12 12:30
---

生成AIを使えば、OCR、CSV、Excel、メール、自由記述からJSONを作るのは、かなり簡単になった。

でも、そこで終わると危ない。

難しいのはJSONを作ることではない。

**LLMが作った「それっぽい候補」のうち、どれを事実としてデータ基盤に入れていいのか。**

ここが本題だ。

今回のケーススタディでは、実際にこんな結果になった。

| 実処理 | 入力 | 採用・統合 | 止めた / 別扱いにした |
|---|---:|---:|---:|
| 初期データ統合 | 455件 | 414 Work | 41件を同一作品側へ統合 |
| OCR由来データ追加 | 60件 | 36件を新規追加 | 24件を重複として停止 |
| Kindle XML取込 | 690行 | 685 records | 完全重複5行を除去 |
| NDL分類の直近batch | 25件 | 9件を採用 | 16件は自動採用しなかった |
| 書誌タイトル修正 | 5候補 | 4件を採用 | 1件をcollisionで停止 |

60件中24件、つまり40%を止めた処理がある。

分類では25件中9件しか自動採用していない。

一次情報で確認できた修正候補ですら、5件中1件はDB側の衝突で止めた。

この「止めた数」は失敗ではない。

**正準データを壊さなかった数だ。**

この記事では、LLMで雑データを整えるとき、なぜ「全部自動化」が危ないのかを、文献と実データの両方から見ていく。

ケーススタディ:

- Repository: https://github.com/KAFKA2306/books
- 455件→414 Work: https://github.com/KAFKA2306/books/pull/2
- OCR 60件の統合: https://github.com/KAFKA2306/books/pull/3
- Kindle XML 690行の取込: https://github.com/KAFKA2306/books/pull/16
- NDL/NDC分類: https://github.com/KAFKA2306/books/pull/18
- 直近の分類25件レポート: https://github.com/KAFKA2306/books/blob/main/data/category-enrichment-report.json
- collision gate: https://github.com/KAFKA2306/books/pull/52
- 5候補中4件だけを採用した例: https://github.com/KAFKA2306/books/pull/53

## LLMで安くなったのは「候補を作るところ」

以前は、雑なデータを整えるだけでもかなり手間がかかった。

1行ずつ読み、列を分け、表記揺れを探し、検索し、似たレコードを比べる。

LLMはここをかなり安くできる。

OpenAIのStructured Outputsも、非構造入力からJSON Schemaに沿った出力を作る用途を明示している。

https://openai.com/index/introducing-structured-outputs-in-the-api/

ただし、OpenAI自身が大事な注意書きを置いている。

> “Structured Outputs doesn’t prevent all kinds of model mistakes.”

Schemaに合っていても、JSONの**値そのもの**は間違うことがある、という話だ。

つまり、

```text
unstructured data
→ LLM
→ valid JSON
```

まではかなり楽になった。

でも、

```text
valid JSON
→ true fact
→ safe write
```

は別問題だ。

**schema-valid と fact-valid は違う。**

そしてもう一段ある。

**fact-valid と safe-to-apply も違う。**

後で出てくる5候補中1件のcollisionは、まさにこの3段目で止まった。

LLMが候補を速く作れるようになったからこそ、次に詰まるのは検証になる。

## まず難しいのは「同じもの」を決めること

たとえば、

```text
株式会社ABC
(株)ABC
ABC Co., Ltd.
```

は同じ会社かもしれない。

では、これはどうか。

```text
AB-0123
AB0123
0123
```

見た目は似ている。

でも、同じ品番とは限らない。

旧品番かもしれない。工場ごとのlocal codeかもしれない。親品番と子部品かもしれない。

LLMは「たぶん同じ」と候補を出せる。

データ基盤は、それだけでは統合できない。

別物を誤って1つにまとめると、その後の履歴、集計、JOIN、学習データまでつながってしまうからだ。

重複を残すなら、あとで統合できる。

でも、誤って統合したデータを元に戻すのはずっと難しい。

だから問いは、

> **表記をどう揃えるか？**

ではなく、

> **どの証拠が揃えば、2つを同じentityとして扱ってよいか？**

になる。

## 「きれいな1行」にしても、意味が混ざったままなら弱い

次のような記録があったとする。

```text
ABC-1200 / 3号機 / 2026-08-01 / 圧力異常 / 要確認
```

空白や記号を整えるだけなら簡単だ。

でも、それだけでは後で使いにくい。

必要なのは、たとえばこう分けることだ。

```text
asset_id
equipment_model
machine_no
event_date
event_type
review_state
source_record_id
```

つまり、雑データを整えるとは、文字列をきれいにすることではない。

**一つのセルに混ざっていた意味を、元の構造へ戻すこと**だ。

本なら、

```text
作品 ≠ 版 ≠ 所有 ≠ 取得履歴
```

製造なら、

```text
製品 ≠ 品番 ≠ Lot ≠ 測定 ≠ 判定
```

営業なら、

```text
顧客 ≠ 商談 ≠ 見積 ≠ 受注 ≠ 請求
```

になる。

この境界を決めるのは、LLMというよりdata modelingの仕事だ。

## LLMは「分からない」も埋められてしまう

ここも従来のETLと少し違う。

普通の変換処理なら、分からない値はnullやerrorになりやすい。

LLMは、情報が足りなくてもそれらしい値を返せる。

たとえば、

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

を作ることはできる。

でも、年は本当に2026年なのか。

3号機は設備番号なのか、Line番号なのか。

入力だけでは決められないかもしれない。

そんなとき、良いデータ基盤は全部の穴を埋めない。

```text
unknown
ambiguous
no_candidate
provider_error
review
```

を、そのまま正しい状態として持てる。

**欠損率が下がったからといって、事実性が上がったとは限らない。**

## 1件の誤りは、その1件で終わらない

データの怖さはここにある。

一度masterへ誤った値が入ると、それが下流で何度も使われる。

```text
master
→ 集計
→ API
→ dashboard
→ ML feature
→ RAG
→ agent action
```

入力1件の誤りが、利用先の数だけ再利用される。

Google ResearchのSambasivanらは、53人のhigh-stakes AI practitionerへの調査から、この連鎖を **Data Cascades** と呼んだ。

論文の表現はかなり強い。

> “pervasive (92% prevalence), invisible, delayed, but often avoidable.”

https://research.google/pubs/everyone-wants-to-do-the-model-work-not-the-data-work-data-cascades-in-high-stakes-ai/

今回の本棚DBはhigh-stakes AIではない。

でも構造は同じだ。

正準データへ誤りを1件入れれば、API、UI、分析、agentが同じ誤りを再利用する。

だから、OCR 60件中24件を止めたことは単なる「重複除去」ではない。

**24件を下流へ流さなかった**ということでもある。

GoogleのData Validation研究も同じ方向を向いている。

同研究はtraining / serving dataをアルゴリズムやインフラと並ぶ **“important production asset”** と位置づけ、Googleのhundreds of product teamsでproduction dataの継続監視に使われたvalidation systemを報告している。

https://research.google/pubs/data-validation-for-machine-learning/

要するに、データ整備は前処理ではない。

**下流systemの品質を決めるproduction engineeringだ。**

## 「きれいな値」だけ残すと、あとで困る

もう一つ重要なのがprovenanceだ。

LLMが

```text
raw text
→ canonical value
```

へ変換したとして、最後の値だけ保存すると後で困る。

知りたくなるのは、むしろこちらだ。

- 元入力は何だったか
- どのmodel / ruleが変換したか
- どの外部sourceで確認したか
- いつ判断したか
- なぜ自動採用されたか

W3C PROVはprovenanceを、データを生み出したentity、activity、peopleについての情報として定義している。

そして、その情報はデータの **“quality, reliability or trustworthiness”** を評価するために使えるとしている。

https://www.w3.org/TR/prov-overview/

これはLLM時代には特に重要だ。

modelもpromptも外部APIもruleも変わるからだ。

だから、

```text
source
→ candidate
→ evidence
→ decision
→ canonical result
```

までつないでおく。

そうすれば、後から判断をやり直せる。

## では、実データではどれくらい止まったのか

ここからは `KAFKA2306/books` の実測を見る。

題材は書誌データだが、やっていることはmaster統合、identity resolution、provenance、重複検査、分類、API配布だ。

顧客master、設備台帳、商品master、研究データにもかなり近い。

## 455件を、455件の「正解」にはしなかった

最初にあった入力は455件。

それをそのまま455 entityとして登録せず、414 Workへ統合した。

- 入力: 455件
- Work: 414件
- 統合された入力: 41件

https://github.com/KAFKA2306/books/pull/2

41 / 455、約9%は「入力行数」と「実体数」が一致しなかった。

これは単なる文字列重複ではない。

同じ作品でも、版、形式、所蔵状態が違う。

そこで、

```text
Work        作品そのもの
Edition     ISBN・版・形式
Holding     実際の所蔵
Acquisition 取得履歴
```

へ分けた。

ここでのポイントは単純だ。

**LLMに文字列を直させる前に、何を同じものとして数えるかを決める。**

## OCRで60件読めた。でも24件は追加しなかった

次に、スクリーンショットから構造化した60件を既存catalogへ入れた。

結果はこうだった。

| 判定 | 件数 | 構成比 |
|---|---:|---:|
| 入力 | 60 | 100% |
| 既存所蔵として追加停止 | 24 | 40% |
| 新規所蔵として追加 | 36 | 60% |
| 新規Work | 35 | - |

https://github.com/KAFKA2306/books/pull/3

OCRで60件読めた。

でも、60件入れてよいわけではなかった。

40%は既存データと重複していた。

もし入力成功をそのまま登録成功と見なしていたら、24件を二重登録していたことになる。

このケースでは、OCR精度よりも**書く前に止めるprecheck**の方が重要だった。

OpenAIの注意書きと並べると、意味が分かりやすい。

```text
schema-valid
≠ fact-valid
≠ safe-to-apply
```

LLMでも、

```text
LLM output = canonical data
```

にはしない。

```text
LLM output = candidate
```

にする。

## XML 690行は、685件になった。さらに5種類の意味に分かれた

次はKindle XML。

rawの `meta_data` は690行あった。

- raw: 690行
- 完全重複: 5行
- 正規化後: 685 records

https://github.com/KAFKA2306/books/pull/16

重複除去だけを見ると、5 / 690で約0.7%。

でも、面白いのはその後だ。

685 recordsの中身はこう分かれた。

| origin | 件数 | 扱い |
|---|---:|---|
| purchase | 455 | 所有としてHoldingへ反映 |
| sample | 204 | Acquisitionのみ |
| prime | 10 | Acquisitionのみ |
| kindle_dictionary | 1 | Acquisitionのみ |
| unknown | 15 | Acquisitionのみ |

Purchaseは455件、約66%。

Sampleだけで204件、約30%あった。

もし「XMLにある = 所有」と扱っていたら、少なくとも204件を誤って所有扱いしていた。

業務データなら、

```text
見積 = 受注
問い合わせ = 契約
アラート = 故障
試験実施 = 合格
```

と決めつけるのに近い。

**雑データを整えるとは、欠損を埋めることではなく、意味を分けることだ。**

## 25件分類して、自動採用は9件だった

カテゴリ分類では、LLMに自由分類させず、国立国会図書館サーチからNDCを取得し、明示ruleでカテゴリへ変換した。

実装:
https://github.com/KAFKA2306/books/pull/18

NDL Search API:
https://ndlsearch.ndl.go.jp/help/api/specifications

直近の25件batchはこうなった。

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

残り16件、64%はそのrunでは正準カテゴリへ上げなかった。

ここで大事なのは、16件を全部同じ「失敗」にしなかったことだ。

`provider_error` は外部providerの失敗。

`ambiguous` は候補が競合した状態。

`no_candidate` は根拠になる候補が見つからない状態。

意味が違う。

だから状態も分けて残す。

**「分からない」を消さない。**

これはLLMを安全に使うための地味だが重要な設計になる。

## 一次情報で確認できた5件でも、1件は止めた

もっと分かりやすい例もある。

一次情報で確認できたタイトル修正候補が5件あった。

普通なら、そのまま5件直したくなる。

でも、1件は既存Workと `title_key` が衝突した。

PR #52でcollision diagnosticを追加し、PR #53では非衝突の4件だけを採用した。

- source-backed candidates: 5
- applied: 4
- collisionで停止: 1

https://github.com/KAFKA2306/books/pull/52
https://github.com/KAFKA2306/books/pull/53

つまり、

```text
LLMがもっともらしい
↓
一次情報で確認できた
↓
それでもDB整合性で止まることがある
```

ここが重要だ。

**正しい値であることと、安全に書き込めることは別。**

## LLMには候補生成を任せる

ここまで来ると、LLMの役割はかなりはっきりする。

任せやすいのは、たとえば次だ。

- OCRや自由記述からfield候補を抜く
- 表記揺れ候補を出す
- entity分割候補を作る
- 検索queryを作る
- JSON Schemaへ合わせる
- review理由を説明する

一方、正準データへ上げる条件は別layerへ置く。

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

この形なら、LLMを入れ替えてもmaster dataのauthorityは変わらない。

## 「全部自動化」をKPIにしない

今回の実測を並べると、共通点がある。

```text
455 inputs
→ 414 Works
→ 41 inputsは別entityとして増やさなかった

60 OCR records
→ 36 added
→ 24 duplicates blocked

690 XML rows
→ 685 records
→ 455 purchase / 204 sample / 26 other

25 classification attempts
→ 9 accepted
→ 16 not auto-promoted

5 verified normalization candidates
→ 4 applied
→ 1 collision blocked
```

もしKPIを「何件自動処理できたか」だけにすると、危ない方向へ進む。

見るべきなのは、むしろこちらだ。

- generated candidates
- automatically accepted
- duplicate blocked
- ambiguous / review
- evidence unavailable
- provider error
- collision blocked
- human-reviewed
- later reverted

**拒否率や保留率も品質指標になる。**

自動化率100%は、品質100%ではない。

Google ResearchのData Cascadesが示したように、データの問題は後から、別の場所で、複合的に効いてくる。

だから「今どれだけ通したか」だけでは足りない。

**何を止めたかも記録する。**

## 雑な過去データは、LLMで再評価しやすくなった

ここまで書くとLLMに厳しく見えるが、逆だ。

雑データにとって、LLMはかなり大きなチャンスだと思う。

これまでなら、人間が数百・数千件を1件ずつ読み、分割し、検索し、比較するしかなかった。

そのコストが高すぎて、古いExcel、CSV、OCR、XML、メールは放置されがちだった。

LLMは候補生成、分割、検索query作成、レビュー補助をかなり安くできる。

だから、今まで「汚すぎて使えない」と諦めていたデータを、もう一度見直せる。

ただし、LLMだけではデータ基盤にはならない。

```text
LLMが候補を作る
×
一次情報でidentityを確かめる
×
canonical schemaで意味を分ける
×
deterministic gateで危険な変更を止める
×
provenanceを残す
×
継続的にvalidationする
```

この組み合わせが必要になる。

今回の実データでは、60件中24件を止めた。

25件中16件を自動分類しなかった。

一次情報で確認済みの5件でも、1件はcollisionで止めた。

文献側から見ても、これは特殊な思想ではない。

- OpenAI: schemaに従っても値の誤りは残る
- Google Research: データ問題は下流へcascadeする
- Google Data Validation: データはproduction assetとして継続監視する
- W3C PROV: 根拠を追えるprovenanceはquality / reliability / trustworthinessの評価に使える

そして、今回の実測はその抽象論を具体的な数字にした。

だから最後に残る結論はシンプルだ。

**AI時代のデータ基盤で大事なのは、全部埋めることではない。分からないものを分からないまま残し、根拠が揃ったものだけを安全に昇格させることだ。**
