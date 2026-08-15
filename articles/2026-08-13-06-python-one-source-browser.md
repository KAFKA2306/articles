---
title: "業務ロジックをUIにコピーするな。GoogleとO'Reillyに学ぶ「正解を1か所に置く」設計"
emoji: "🎯"
type: "tech"
topics: ["architecture", "python", "javascript", "webassembly"]
published: false
published_at: 2026-08-14 00:20
---

画面が増えるほど、**正解まで増えてはいけない。**

たとえば、同じ金利データを比較した結果が、Pythonのテストでは `11 bp`、ブラウザでは別の値になったとする。

利用者にとって問題なのは、PythonかJavaScriptかではない。

> この数字は信じてよいのか。

それだけである。

この問題を「PyodideでPythonをブラウザ実行した話」と捉えると、対象読者は狭い。

しかし設計原則まで引き上げると、金融、価格計算、製造条件、スコアリング、KPI、AIの判断根拠まで同じ問題になる。

**同じ意味を持つ業務判断を複数箇所へ手書きで複製すると、変更のたびにauthorityが分裂する。**

`KAFKA2306/finBI` では、この問題に対して「検証済みPythonを正準ロジックにし、ブラウザは同じPythonを呼ぶ」という小さな実装を採った。

そして改めてGoogleとO'Reillyの一次情報で監査すると、結論はかなり近かった。ただし、重要な補足もある。

**Single Source of Truthは「必ず同じソースファイルを実行しろ」という意味ではない。重要なのは、正しい意味を決めるauthorityを1つにすることである。**

## GoogleとO'Reillyは本当に同じ方向を向いているか

### Google: SSOTは「誰が変更できるか」を1つにする

GoogleのAndroid公式アーキテクチャガイドは、データ型ごとにSingle Source of Truth（SSOT）を割り当て、そのSSOTだけがデータを変更できる構成を推奨している。

公式説明では、この設計によって変更を1か所へ集中させ、追跡可能性を高め、他のコンポーネントによる勝手な変更を防げるとしている。

- Guide to app architecture: https://developer.android.com/topic/architecture
- Data layer / Source of truth: https://developer.android.com/topic/architecture/data-layer

さらにGoogleは、再利用されるbusiness logicをdomain layerへ集約する理由として、**code duplicationを避け、変更を中央の1か所へ適用でき、単体テストしやすくすること**を挙げている。

- Domain layer: https://developer.android.com/topic/architecture/domain-layer

UIについても、business logicとUI behavior logicを分けている。異なるform factorでもbusiness logicは同じであり得る一方、表示やnavigationのようなUI logicは異なってよい、という整理である。

- UI events: https://developer.android.com/topic/architecture/ui-layer/events

つまりGoogleの視点は、

```text
business meaning / mutation authority
              ↓
      data / domain layer
              ↓
           UI state
              ↓
             UI
```

であり、**UIに業務判断を散らさない**という点で `finBI` の狙いと一致する。

### O'Reilly: 「定義が複数ある」は保守問題ではなくbusiness risk

O'Reilly Radarは2026年5月7日の記事で、売上などのmetric definitionがTableau、Power BI、Python notebookなどに別々に存在する状態を、単なる開発上の不便ではなく、accuracy・governance・change managementのリスクとして扱っている。

そこでsemantic layerを、metric definition、business logic、calculationを一か所で管理し、複数の利用ツールから同じ定義を参照するための仕組みとして論じている。

- O'Reilly Radar, *The Best Risk Mitigation Strategy in Data? A Single Source of Truth* (2026-05-07): https://www.oreilly.com/radar/the-best-risk-mitigation-strategy-in-data-a-single-source-of-truth/

O'Reillyから刊行されている *Learning Domain-Driven Design* でも、business logicがUIやdatabaseへ拡散したり、複数コンポーネントへ重複したりすると、変更時に修正箇所が分からなくなり、保守コストが上がるという問題が説明されている。

- *Learning Domain-Driven Design*, Chapter 8: https://www.oreilly.com/library/view/learning-domain-driven-design/9781098100124/ch08.html

O'Reilly側の視点を一言で言えば、

```text
同じmetric / business ruleを複数箇所で定義する
                    ↓
               driftが起きる
                    ↓
      数字への信頼と変更能力を失う
```

である。

これは `finBI` で避けたかった事故そのものだった。

## 共通点と、混同してはいけない点

Google、O'Reilly、今回の実装を並べると、共通点は明確である。

| 視点 | 1か所に置くもの | 目的 |
| --- | --- | --- |
| Google | data ownership / reusable business logic | consistency、traceability、testability |
| O'Reilly | metric definition / business logic / calculation | accuracy、governance、change management |
| finBI | 金融比較のvalidationとcalculation | offline testとbrowser resultのdrift防止 |

ただし、ここで**「SSOT = 1ファイル」へ短絡してはいけない。**

Google自身、異なるrepositoryが異なるsource of truthを持つ場合を説明している。O'Reillyのsemantic layerも、すべての処理を1プロセスへ押し込む話ではない。

正確には、

> **1つの意味に対して、変更authorityを1つにする。**

である。

実行場所は複数でもよい。

- server APIを唯一の計算authorityにする
- shared WASMを複数frontendから呼ぶ
- schema / code generationで複数言語へ生成する
- semantic layerをBI、Excel、Python、AIから共有する
- 今回のように同じPython moduleをbrowserでも実行する

問題なのは、**同じ意味を人間が複数箇所へ別々に実装し、どれが正準か分からなくなること**である。

## `finBI` では何を1つにしたのか

現在の正準ロジックは `code/static_bi.py` にある。

- Current implementation: https://github.com/KAFKA2306/finBI/blob/main/code/static_bi.py
- Browser Worker: https://github.com/KAFKA2306/finBI/blob/main/web/worker.mjs
- Browser UI: https://github.com/KAFKA2306/finBI/blob/main/web/app.js
- Offline tests: https://github.com/KAFKA2306/finBI/blob/main/code/tests/test_static_bi.py
- 実装の起点となったPR: https://github.com/KAFKA2306/finBI/pull/9

`static_bi.py` が持つのは、単なる引き算ではない。

現在は少なくとも、

- snapshot schema version
- source metadata
- availability evidence
- timestampとtimezone
- observationの時系列順序
- 重複日付
- 数値型
- 選択日の存在
- start / endの順序
- unitがPercentかどうか
- delta
- basis points
- direction
- calendar days
- provenance

を同じ境界で扱っている。

つまり正準化したのは「式」ではなく、**その数字を正しいと判定する条件一式**である。

## 現在の実証値

現行の公開テストでは、保存済みsnapshotに対して次が固定されている。

```python
result = compare_dates(data, "2026-07-20", "2026-07-23")

self.assertAlmostEqual(result["delta"], 0.11)
self.assertAlmostEqual(result["basis_points"], 11.0)
self.assertEqual(result["direction"], "up")
self.assertEqual(result["calendar_days"], 3)
```

このfixtureは、単にunit testの期待値ではない。

browser側のWorkerも同じrepositoryの `static_bi.py` をロードし、`compare_dates_json()` を呼ぶ。

```text
offline test ─────┐
                  │
                  ├──> static_bi.py ──> compare_dates()
                  │
browser Worker ───┘
```

ブラウザ側のJavaScriptは、入力、Worker通信、表示、SVG描画を担当する。

計算に失敗した場合も、JavaScript版の似た計算へfallbackしない。エラーとして表示する。

これにより、**runtime failureとbusiness answerを混同しない。**

## なぜPythonをブラウザへ持ってきたのか

ここでPyodideは目的ではなく、選択肢の1つである。

今回の条件は、

1. すでに検証済みPython実装がある
2. 静的Web UIでも同じ結果が必要
3. server APIを増やす必要はない
4. ロジックの二重実装を避けたい

だった。

そのため、Python runtimeをbrowserへ持ってくるコストより、PythonとJavaScriptの2実装を長期同期するコストを大きいと判断した。

Pyodideの公式ドキュメントも、長時間のPython処理をmain threadで行うとUIをblockし得るため、Web Workerで実行する方法を案内している。

- Pyodide / Using Pyodide in a web worker: https://pyodide.org/en/stable/usage/webworker.html

一方でPyodideにはWebAssembly環境固有の制約があり、一部の標準libraryやthreading、multiprocessing、socket等には制約がある。

- Pyodide Python compatibility: https://pyodide.org/en/stable/usage/wasm-constraints.html

したがって、

```text
Pythonが好き
→ Pyodide
```

ではない。

```text
既存の検証済みauthorityを複製せずbrowserから使う価値
>
browser runtimeを追加するコスト
```

のときだけ採用する。

## では、どの実装方式を選ぶべきか

「正解を1か所にする」という原則と、「Pythonをbrowserで動かす」は分離して考えるべきである。

| 条件 | 選択肢 |
| --- | --- |
| 検証済みPythonがあり、client-onlyで再利用したい | Pyodide |
| 複数言語・高性能runtimeで同じcoreを共有したい | shared WASM |
| secret、DB、権限制御が必要 | server API |
| 多数のBI / notebook / AIが同じmetricを使う | semantic layer |
| schema起点で複数言語に同じcontractを配りたい | code generation |
| UI内だけの単純なロジック | JavaScript / TypeScriptだけで完結 |

**重要なのは技術選定より先にauthorityを決めること**である。

## UIに残してよいロジック、残してはいけないロジック

Googleの区分は実務で使いやすい。

### UIに残してよい

- 文字列format
- responsive layout
- focus
- animation
- navigation
- SVG描画
- 表示上のselection state

### UIへコピーしない

- 金額計算
- 金利差
- price rule
- eligibility
- scoring
- validation
- rounding policy
- 欠損値policy
- unit conversionの業務定義
- provenance判定

境界は、

> **そのロジックが変わると、利用者に提示する「意味」や「判断」が変わるか。**

で考えるとよい。

変わるなら、それはpresentationではなくauthority側へ置く候補である。

## 1つの正解を守るための5つの確認

業務ロジックをWeb、mobile、BI、AI agentへ展開するときは、最低限これを確認する。

### 1. authorityはどこか

「この値の定義を変更するとき、最初に直す場所」を1つ答えられるか。

### 2. UIが独自のbusiness ruleを持っていないか

```js
if (!value) return 0;
```

のような一見便利な補正が、第二の仕様になっていないか。

### 3. validationとerror policyも共有されているか

式だけ一致していても、欠損、丸め、単位、期間、例外条件が違えば答えは分裂する。

### 4. 同じfixtureを複数経路で検証できるか

```text
canonical fixture
   ├─ unit test
   ├─ API contract test
   └─ browser / app integration test
```

という形で、同じ入力と期待値を使えるか。

### 5. fallbackが別仕様を発明していないか

正準runtimeが失敗したとき、「似たロジック」で成功したふりをするより、利用不能としてfail-closeする方が安全な領域は多い。

## 得られるのは保守性ではなく、変更可能性と信頼である

Single Source of Truthは、コードをきれいにするためだけの設計原則ではない。

Googleは、変更を一か所へ集中させ、追跡とテストをしやすくする設計として扱う。

O'Reillyは、metricとbusiness logicの分裂をaccuracy、governance、change managementのbusiness riskとして扱う。

`finBI` の実装は、その考え方を小さな金融UIで実証した例にすぎない。

本質はもっと広い。

```text
画面が増える
利用者が増える
AI agentが増える
配信先が増える

でも

正解を決めるauthorityは増やさない
```

これができると、変更は一度で済み、テストした意味と利用者が見る意味を一致させやすい。

**ソフトウェアが増えても、真実の定義は増やさない。**

それが、ブラウザPythonより長く使える設計原則である。
