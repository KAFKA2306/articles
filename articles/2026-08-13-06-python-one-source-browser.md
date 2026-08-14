---
title: "ブラウザとテストで答えが違うをなくす。業務計算の正解を1つだけにした"
emoji: "🐍"
type: "tech"
topics: ["python", "javascript", "webassembly", "architecture"]
published: false
published_at: 2026-08-14 00:20
---

同じデータを見ているのに、Pythonのテストとブラウザ画面で答えが違う。

こういう事故は、難しいアルゴリズムより、**同じ計算を2回書いたこと**から起きやすい。

`KAFKA2306/finBI` では、金融データの比較ロジックをPythonへ置いていた。

Web UIを作るとき、最短ならJavaScriptにも同じ式を書ける。

```python
basis_points = round(delta * 100, 4)
```

```js
const basisPoints = Math.round(delta * 10000) / 100;
```

最初は同じ答えが出る。

しかし業務計算は式だけではない。

- 入力schema
- 日付存在確認
- 単位
- timezone
- 欠損値
- 丸め
- provenance
- 例外条件

のどれかを片方だけ修正すると、**正解が2つになる。**

そこで `finBI` では、計算をPythonだけに置き、browserはWeb Worker内のPyodideから同じPython moduleを呼ぶ構成にした。

JavaScriptは入力、表示、SVG描画、Worker通信だけを担当する。

この記事で扱うのは「Pythonをブラウザで動かす方法」ではない。

**テストとUIで同じ入力なら同じ答えになる状態を、どう維持するか**である。

- PR: https://github.com/KAFKA2306/finBI/pull/9
- 正準計算: https://github.com/KAFKA2306/finBI/blob/71d228ad35228a58d6330896a691bf144bc87f7b/code/static_bi.py
- Browser Worker: https://github.com/KAFKA2306/finBI/blob/71d228ad35228a58d6330896a691bf144bc87f7b/web/worker.mjs
- Offline tests: https://github.com/KAFKA2306/finBI/blob/71d228ad35228a58d6330896a691bf144bc87f7b/code/tests/test_static_bi.py

## 1つのfixtureを、テストとUIの両方の正解にする

公開テストには、保存済みsnapshotについて次の比較が固定されている。

```python
result = compare_dates(data, "2026-07-20", "2026-07-24")
self.assertAlmostEqual(result["delta"], 0.09)
self.assertAlmostEqual(result["basis_points"], 9.0)
self.assertEqual(result["direction"], "up")
self.assertEqual(result["calendar_days"], 4)
```

このfixtureの価値は、unit testがあることだけではない。

browser UIも同じ `compare_dates()` へ到達するため、

```text
2026-07-20 → 2026-07-24
```

という入力の正解は1つだけになる。

```text
offline test ──┐
               ├─> static_bi.py
browser UI ────┘
```

**UI向けの別実装を持たない。**

これが中心のcontractである。

## 二重実装が危険なのは、式より「条件」が増えたとき

`static_bi.py` は単純な差分計算だけではない。

例えば、

- snapshot schemaは正しいか
- source metadataがあるか
- timestampがあるか
- 観測順序は正しいか
- 重複日付がないか
- 値が数値か
- 選択日が存在するか
- unitがPercentか

などを確認する。

JavaScriptへ移植するときに一番漏れやすいのは、この周辺条件である。

例えばPython側だけ、

> `unit == Percent` のときだけbasis pointsを返す

へ変えたとする。

JS側が古い式のままなら、Pythonでは `None`、browserでは数値が表示される可能性がある。

利用者から見れば、

> どちらを信じればいいのか

という問題になる。

だから、計算式ではなく**判断全体をsingle sourceにする。**

## frontendを薄くすると、変更責任が分かりやすくなる

browser側の責務は次へ絞った。

```text
input
  ↓
Workerへ送る
  ↓
Python結果を受け取る
  ↓
表示 / SVG描画
```

Workerは、

```text
Pyodideをロード
  ↓
canonical Python moduleをロード
  ↓
入力を渡す
  ↓
結果をJSON化して返す
```

だけを担当する。

これにより、

- 計算を直す → Python
- UIを直す → JavaScript/CSS
- browser実行境界を直す → Worker

と責務が分かれる。

**frontendのコード量を減らすことより、どこを直せば正解が変わるかが1か所になること**が重要だった。

## Pyodideを使うこと自体は目的ではない

この構成にはコストがある。

- 初回loadが重い
- browserでWASM runtimeを動かす
- package compatibility制約がある
- native extensionやOS依存処理は向かない
- 小さな式ならJS一実装の方が単純なこともある

だから、

```text
Pythonが好きだからPyodide
```

では採用しない。

採用理由は、**すでに検証済みのPython業務ロジックがあり、それをbrowser向けに再実装するdrift costが大きい**からである。

## 使うべき場面

このpatternが効きやすいのは、

- Pythonで既にunit testが充実している
- 計算条件が多い
- frontendでも同じ結果が必要
- 静的siteやclient-side UIで使いたい
- server APIを増やしたくない

という場合である。

例えば、

- 金融計算
- 科学計算
- engineering calculator
- pricing logic
- data validation
- scoring logic

などが候補になる。

## 使わない方がよい場面

逆に、

- 計算が数行だけ
- JS側だけで完結する
- package loadが大きすぎる
- server-side secretが必要
- native library依存が強い
- mobile環境で初期loadが許容できない

なら、無理にbrowser Pythonへ寄せない。

**single source of truthを守る手段はPyodideだけではない。**

shared WASM、server API、code generationなど別の方法もある。

大事なのは「正解を2か所に置かない」ことである。

## UIへ載せる前に確認する3つ

既存Python logicをbrowserへ持っていくなら、まず次を確認する。

### 1. 何をcanonicalにするか

単なる式ではなく、validationと例外も含めた関数境界を決める。

### 2. UIが独自判断を持っていないか

例えば、

```js
if (!value) return 0;
```

のような補正がfrontend側にあると、すぐに二つ目の仕様になる。

### 3. 同じfixtureを両経路で通せるか

```text
canonical test fixture
   ├─ offline Python test
   └─ browser E2E
```

同じ入力で同じoutputを確認する。

## browser runtimeが失敗したときも、計算結果を捏造しない

Pyodideのloadに失敗した場合、fallbackとしてJavaScript版計算をこっそり使うとsingle source contractが壊れる。

```text
Python unavailable
→ JS fallbackで似た計算
```

ではなく、

```text
Python unavailable
→ calculation unavailableを表示
```

にする方がよい。

利用者には不便だが、**異なるロジックを同じ機能名で返すより安全**である。

## この構成で得たいのは、保守性より「結果への信頼」

single source of truthは開発者向けの美しいarchitectureに見える。

しかし利用者側の価値はもっと単純だ。

**テストで確認した計算と、画面に出ている計算が同じである。**

そのために、

- Pythonをcanonicalにする
- JSへ式を複製しない
- Workerはbridgeにする
- 同じfixtureを使う
- runtime failureを別ロジックで隠さない

という設計を採った。

UIが増えても、正解は増やさない。

業務計算をWebへ出すとき、最初に守りたいのはそこだった。
