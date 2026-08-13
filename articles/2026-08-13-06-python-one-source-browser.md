---
title: "計算式を2か所に書かない。Pythonをブラウザでも使う"
emoji: "🐍"
type: "tech"
topics: ["python", "javascript", "webassembly", "architecture"]
published: false
published_at: 2026-08-14 00:20
---

Pythonで検証した計算ロジックをWeb UIへ載せるとき、よく起きるのが「Python版とJavaScript版を両方持つ」状態です。最初は同じ式でも、丸め、例外処理、単位変換、入力検証のどれかが片方だけ変わると、同じデータに対して結果がずれます。

2026年8月13日に `KAFKA2306/finBI` で行った再設計では、この問題を避けるために **計算はPythonだけに置き、ブラウザ側はWeb Worker内のPyodideから同じPythonファイルを実行する** 構成にしました。JavaScriptは入力、表示、SVG描画、Workerとの通信だけを担当します。

この記事では、金融BI固有の話ではなく、**既存のPythonロジックを静的Web UIへ載せるときに「式を複製しない」ための設計**として一般化します。

一次情報:

- https://github.com/KAFKA2306/finBI/commit/bc928ab7806c727086992df838f8ccae62f58040
- https://github.com/KAFKA2306/finBI/blob/main/code/static_bi.py
- https://github.com/KAFKA2306/finBI/blob/main/web/worker.mjs
- https://github.com/pyodide/pyodide/blob/main/docs/project/changelog.md
- https://developer.mozilla.org/en-US/docs/Web/API/Worker/postMessage

## 1. 問題

たとえばPython側に次の計算があるとします。

```python
delta = end_value - start_value
basis_points = round(delta * 100, 4)
```

Web画面から同じ比較をしたくなったとき、最短ではJavaScriptにも同じ式を書けます。

```js
const delta = endValue - startValue;
const basisPoints = Math.round(delta * 100 * 10000) / 10000;
```

一見すると問題ありません。しかし、実際の業務ロジックは式だけでは終わりません。

- 入力データのschemaは正しいか
- 選択日が存在するか
- 開始日と終了日の順序は正しいか
- 値は数値か
- 単位がPercentのときだけbasis pointsへ変換するか
- timestampにtimezoneが含まれるか
- provenanceが欠けていないか

こうした条件が増えるほど、PythonとJavaScriptの2実装を同時に正しく保つコストが上がります。

### 実際の状況

`finBI` の `code/static_bi.py` は、単なる差分計算ではありません。snapshot schema、source metadata、availability evidence、timestamp、観測順序、重複日付、数値型を検証し、異常時は例外で停止します。そのうえで、2日を比較し、差分、basis points、方向、暦日差、source URLを返します。

一方 `web/worker.mjs` には金融計算式を置いていません。Workerは同一repositoryの `code/static_bi.py` を取得し、Pyodideへ読み込んで `compare_dates_json(...)` を呼び出します。

つまり、ブラウザ表示を追加しても計算規則の正準実装は1つのままです。

## 2. 原因

計算ロジックが二重化する原因は、**UI層と計算層を「使用言語」で分けてしまうこと**です。

典型的には次の発想になります。

```text
backend / tests = Python
browser         = JavaScript
```

この分け方自体は自然ですが、「browserで動くものはJavaScriptで再実装する」と決めると、ドメインロジックまでUI側へ流れ込みます。

本当に分けたい境界は言語ではなく責務です。

```text
計算・検証 = canonical domain logic
入力・操作 = UI
描画       = UI
非同期実行 = runtime boundary
```

WebAssembly上でPythonを実行できるPyodideを使うと、この責務分離を保ったままPythonの正準ロジックをブラウザへ持ち込めます。

Pyodideの公式changelogでは、現在のruntimeがES moduleとして扱われ、classic workerではなくmodule-type workerを使う構成へ移っていることが確認できます。Web Worker側との通信は標準の `postMessage()` で構成できます。

## 3. 設計判断と代替案

### 案A: PythonとJavaScriptに同じ式を書く

小規模な式なら最も簡単です。

ただし、入力検証や例外条件まで増えると二重実装になります。片方だけ修正されても型チェックやsyntax checkは通るため、意味のずれを別途テストしなければなりません。

### 案B: Python APIサーバーを置く

Pythonを正準に保ちやすく、重い処理やprivate dataにも向きます。

一方、静的Pagesだけで完結させたい用途では、server運用、認証、CORS、稼働監視など別の責務が増えます。`finBI` は保存済みの小さなsnapshotを比較する用途なので、この追加runtimeを持たない判断をしました。

### 案C: Pythonロジックを別言語へ生成する

共通schemaやcode generationで差を減らす方法もあります。ただし生成系そのものが新しいbuild契約になり、生成物の同期確認が必要です。

### 案D: Pyodide + Web Workerで同じPythonを実行する

今回の採用案です。

```text
browser UI
   |
   | postMessage(input)
   v
module Web Worker
   |
   | load code/static_bi.py
   v
Pyodide
   |
   | compare_dates_json(...)
   v
canonical Python logic
```

この形なら、Python unit testで検証した関数をそのままブラウザから呼べます。

## 4. 実装

最小構成は3層です。

### 4.1 Pythonを純粋な入出力に寄せる

ブラウザから呼ぶ関数は、DOMやfilesystemへ依存させず、JSON化しやすい値を受け取ってJSON化しやすい値を返す形にします。

`finBI` では次の薄いadapterを置いています。

```python
def compare_dates_json(snapshot_json: str, start_date: str, end_date: str) -> str:
    result = compare_dates(json.loads(snapshot_json), start_date, end_date)
    return json.dumps(result, ensure_ascii=False, sort_keys=True)
```

重要なのは、ここで計算を新しく書かないことです。`compare_dates_json` はdeserializeとserializeだけを担当し、実処理は `compare_dates` に委譲します。

### 4.2 WorkerでPython sourceを1回だけloadする

`finBI` の実装は次の形です。

```js
import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.2/full/pyodide.mjs";

const runtimePromise = loadPyodide();
const sourcePromise = fetch("./code/static_bi.py").then((response) => {
  if (!response.ok) throw new Error(`Python source fetch failed: ${response.status}`);
  return response.text();
});
let coreLoaded = false;
```

runtimeとsourceの取得をPromiseとして保持し、Python sourceは初回だけ読み込みます。

```js
async function getRuntime() {
  const pyodide = await runtimePromise;
  if (!coreLoaded) {
    pyodide.runPython(await sourcePromise);
    coreLoaded = true;
  }
  return pyodide;
}
```

### 4.3 UIとはmessageで接続する

MDNの `Worker.postMessage()` 仕様では、Workerへ送るデータはstructured clone algorithmで扱えるJavaScript objectとして渡せます。

Worker側では入力だけPython globalsへ渡します。

```js
self.onmessage = async (event) => {
  try {
    const pyodide = await getRuntime();
    pyodide.globals.set("snapshot_json", JSON.stringify(event.data.snapshot));
    pyodide.globals.set("start_date", event.data.startDate);
    pyodide.globals.set("end_date", event.data.endDate);

    const output = pyodide.runPython(
      "compare_dates_json(snapshot_json, start_date, end_date)"
    );

    self.postMessage({ result: JSON.parse(output) });
  } catch (error) {
    self.postMessage({ error: String(error) });
  }
};
```

JavaScriptは計算結果を受け取るだけです。

## 5. 検証

この構成では、テストを3種類に分けると単純になります。

### Python unit test

最重要です。

正準計算、入力validation、例外条件をPythonだけで網羅します。ブラウザを起動せずに高速に検証できます。

### JavaScript syntax / contract test

WorkerとUIのJavaScriptが構文的に壊れていないか、正しいpathを読んでいるか、message contractが維持されているかを見ます。

`finBI` のCIでは `node --check web/app.js` と `node --check web/worker.mjs` を実行しています。

### 静的配信のsmoke test

Python fileがrepositoryに存在していても、Pages buildへcopyし忘れるとWorkerは404になります。

そこで `finBI` のCIはpublic rootを組み立て、HTTP serverを起動して `code/static_bi.py` を含む配信routeへ実際にアクセスします。

この3層に分けると、失敗の意味が明確です。

```text
Python test fail   -> domain logic / validation
JS check fail      -> browser adapter
HTTP smoke fail    -> build / deployment packaging
```

## 6. 失敗と学び

### 壊れた例: browser側にも単位変換を書く

たとえばPythonに次があるとします。

```python
basis_points = round(delta * 100, 4) if unit.casefold() == "percent" else None
```

UI側で表示を急いで、JavaScriptに次を追加するとします。

```js
const bp = (end - start) * 100;
```

この時点で2つの意味が違います。

- PythonはunitがPercentのときだけ変換する
- JavaScriptはunitを見ず常に100倍する
- Pythonは小数4桁へ丸める
- JavaScriptは丸めない

画面が正しく見える入力だけでは、この差は見つからないかもしれません。

### 改善後: JavaScriptには結果の表示だけを書く

```js
resultNode.textContent =
  result.basis_points == null
    ? "bp換算なし"
    : `${result.basis_points >= 0 ? "+" : ""}${result.basis_points.toFixed(2)} bp`;
```

ここでは `basis_points` を**計算していません**。Pythonが返した意味を表示形式へ変えているだけです。

この違いをレビュー規則として言語化すると有効です。

> JavaScriptでdomain valueを導出しない。JavaScriptはcanonical resultのformattingだけを行う。

## 7. 再現方法

最小構成なら、金融データを使わずに試せます。

### `core.py`

```python
import json


def calculate_json(payload_json: str) -> str:
    payload = json.loads(payload_json)
    left = float(payload["left"])
    right = float(payload["right"])
    if right < left:
        raise ValueError("right must be >= left")
    return json.dumps({"delta": right - left})
```

### `worker.mjs`

```js
import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.2/full/pyodide.mjs";

const pyodide = await loadPyodide();
const source = await fetch("./core.py").then((r) => r.text());
pyodide.runPython(source);

self.onmessage = (event) => {
  try {
    pyodide.globals.set("payload_json", JSON.stringify(event.data));
    const output = pyodide.runPython("calculate_json(payload_json)");
    self.postMessage({ result: JSON.parse(output) });
  } catch (error) {
    self.postMessage({ error: String(error) });
  }
};
```

### UI側

```js
const worker = new Worker("./worker.mjs", { type: "module" });
worker.postMessage({ left: 10, right: 13 });
worker.onmessage = ({ data }) => console.log(data);
```

`right: 5` に変えると、Python側のvalidationがそのままbrowser実行でも効くことを確認できます。

### 確認したいこと

1. Pythonだけに計算式がある
2. WorkerはPython sourceをloadして呼ぶだけ
3. UIは入力を送り、結果を表示するだけ
4. Python testで異常系を検証できる
5. static buildにPython sourceを含める

## まとめ

Pythonで確立した計算をWebへ載せるとき、必ずしもJavaScriptへ翻訳する必要はありません。

今回の実装から再利用できる最小contractは次の4点です。

1. domain calculationはPythonを唯一の正準実装にする
2. browser adapterはmodule Web Workerへ隔離する
3. Pythonとの境界はJSONなど単純なmessage contractにする
4. Python test、JS check、HTTP smokeを別々に検証する

Pyodideを入れること自体が目的ではありません。**同じ業務規則を2言語で保守しないこと**が目的です。

小さな静的UIで、既存Pythonロジックをそのまま利用できるなら、サーバーを増やさず、計算式も複製しない構成は十分実用的です。
