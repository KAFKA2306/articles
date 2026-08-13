---
title: "同じ計算を2か所に書いたら、どちらが正しい？ Pythonをブラウザでもそのまま使う"
emoji: "🧮"
type: "tech"
topics: ["python", "javascript", "webworker", "testing"]
published: false
published_at: 2026-08-13 15:06
---

同じ数字を出す画面なのに、バックエンドとブラウザで答えが違う。

こういう事故は、難しいアルゴリズムよりも「同じ計算式を2回書いた」ことから起きやすい。

`KAFKA2306/finBI` の直近の公開実装では、金融データの比較ロジックを `code/static_bi.py` にだけ置き、オフラインテストもブラウザUIも同じPythonを使う構成に変えている。ブラウザ側は Web Worker 内でそのPythonを読み込み、入力を渡して結果だけ受け取る。

一次情報:

- PR: https://github.com/KAFKA2306/finBI/pull/9
- 正準計算: https://github.com/KAFKA2306/finBI/blob/71d228ad35228a58d6330896a691bf144bc87f7b/code/static_bi.py
- Browser Worker: https://github.com/KAFKA2306/finBI/blob/71d228ad35228a58d6330896a691bf144bc87f7b/web/worker.mjs
- オフラインテスト: https://github.com/KAFKA2306/finBI/blob/71d228ad35228a58d6330896a691bf144bc87f7b/code/tests/test_static_bi.py
- Web Workers API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API

この記事では、この構成を「Pythonをブラウザで動かす方法」ではなく、**業務計算を1か所だけに残し、テストとUIで同じ実装を使う設計**として整理する。

## 1. 問題：同じ計算式をPythonとJavaScriptに持つと、正解が2つできる

### 実際の入力・状況

`finBI` の公開テストには、保存済みの金利snapshotについて次の比較が固定されている。

```python
result = compare_dates(data, "2026-07-20", "2026-07-24")
self.assertAlmostEqual(result["delta"], 0.09)
self.assertAlmostEqual(result["basis_points"], 9.0)
self.assertEqual(result["direction"], "up")
self.assertEqual(result["calendar_days"], 4)
```

出典:
https://github.com/KAFKA2306/finBI/blob/71d228ad35228a58d6330896a691bf144bc87f7b/code/tests/test_static_bi.py

この例では、2つの日付の値を比較し、差分、basis points、方向、暦日差を返す。

もしPython側に

```python
basis_points = round(delta * 100, 4)
```

があり、JavaScript側にも

```js
const basisPoints = Math.round(delta * 10000) / 100;
```

のような別実装を書くと、最初は同じ答えでも、丸め規則、単位条件、欠損値処理、日付境界のどれかを片方だけ修正した時点で結果が分岐する。

### 壊れた失敗例

たとえばPython側だけ「`unit` が `Percent` のときだけbasis pointsを計算する」と修正し、JavaScript側の式を残したとする。

すると、Pythonでは非Percent系列の `basis_points` が `None` なのに、UIでは数値が出る可能性がある。

これは実際の事故報告ではなく、公開されている現在の条件分岐から再現できる破損パターンである。現在のPython実装は次の条件を持つ。

```python
basis_points = (
    round(delta * 100, 4)
    if snapshot["unit"].casefold() == "percent"
    else None
)
```

出典:
https://github.com/KAFKA2306/finBI/blob/71d228ad35228a58d6330896a691bf144bc87f7b/code/static_bi.py

問題は「JavaScriptの計算精度が低い」ことではない。**同じ業務規則を複数言語へ複製すると、変更点が複数になる**ことだ。

## 2. 原因：UIと計算を分けても、計算式まで複製してしまう

典型的なWebアプリでは、サーバー側とブラウザ側の責務を分ける。

この分離自体は必要だが、次のように考えると計算規則まで二重化しやすい。

```text
Python
  └─ テスト用の正しい計算

JavaScript
  └─ 画面表示用に同じ計算を再実装
```

一見すると、UIが自律していて便利に見える。

しかし、金融、料金、税率、スコア、集計、単位変換のように「同じ入力なら同じ答えでなければならない」処理では、実装が2つあること自体が同期コストになる。

`finBI` の現在の公開実装は逆に、正準計算を `code/static_bi.py` へ集中させている。

`compare_dates()` は次を一度に決める。

- 入力snapshotの妥当性
- 指定日がsnapshot内にあるか
- 開始日と終了日の順序
- 差分
- 上昇 / 低下 / 横ばい
- Percent系列だけのbasis points
- 暦日差
- provenanceの返却

出典:
https://github.com/KAFKA2306/finBI/blob/71d228ad35228a58d6330896a691bf144bc87f7b/code/static_bi.py

このまとまりをJavaScriptへもう一度移植すると、単なる四則演算ではなく、入力契約まで複製することになる。

## 3. 設計判断と代替案：計算は1つ、実行場所だけ増やす

採用された構造は次のように読める。

```text
committed snapshot
      ↓
code/static_bi.py
      ├─ Python unit tests
      └─ browser Web Worker
             ↓
          JavaScript UI
```

ここで増やすのは「計算実装」ではなく「実行経路」だけである。

### 代替案A：JavaScriptへ計算式を移植する

最も軽量に見える。ブラウザ依存も少ない。

ただし、PythonテストとブラウザUIが別実装になる。変更時には少なくとも2か所を同期する必要がある。

### 代替案B：APIサーバーを立て、Python計算をHTTPで呼ぶ

計算実装は1つにできる。

一方、静的Pagesだけで配信したい小規模ツールでは、サーバー、認証、監視、デプロイ、障害点が増える。

### 代替案C：ブラウザ側で同じPythonを実行する

`finBI` のPR #9はこの方式を採用している。

`web/worker.mjs` は `code/static_bi.py` をfetchし、runtimeへ読み込んだ後、`compare_dates_json()` を呼び出す。

```js
const sourcePromise = fetch("./code/static_bi.py").then((response) => {
  if (!response.ok) throw new Error(`Python source fetch failed: ${response.status}`);
  return response.text();
});

pyodide.runPython(await sourcePromise);

const output = pyodide.runPython(
  "compare_dates_json(snapshot_json, start_date, end_date)",
);
```

出典:
https://github.com/KAFKA2306/finBI/blob/71d228ad35228a58d6330896a691bf144bc87f7b/web/worker.mjs

JavaScriptは計算式を知らない。入力を渡し、結果をJSONで受け取るだけになる。

この設計は全アプリに適するわけではない。runtimeサイズや初期化時間が問題になるケースではAPI方式やJavaScript実装のほうが適切である。

判断基準は「Pythonをブラウザで動かせるか」ではなく、**二重実装を消す価値が追加runtimeのコストを上回るか**である。

## 4. 実装：関数をJSON境界で呼べる形にする

ブラウザから既存Pythonを使うために、業務ロジックそのものを書き換える必要はない。

重要なのは、外部境界を単純にすることだ。

`finBI` では通常のPython関数に加え、JSON文字列を受け取ってJSON文字列を返す薄いadapterがある。

```python
def compare_dates_json(
    snapshot_json: str,
    start_date: str,
    end_date: str,
) -> str:
    result = compare_dates(
        json.loads(snapshot_json),
        start_date,
        end_date,
    )
    return json.dumps(
        result,
        ensure_ascii=False,
        sort_keys=True,
    )
```

出典:
https://github.com/KAFKA2306/finBI/blob/71d228ad35228a58d6330896a691bf144bc87f7b/code/static_bi.py

このadapterにより、正準関数 `compare_dates()` はPythonのdictを扱ったまま維持できる。

Worker側では、受け取ったデータをPython runtimeへ設定する。

```js
pyodide.globals.set("snapshot_json", JSON.stringify(event.data.snapshot));
pyodide.globals.set("start_date", event.data.startDate);
pyodide.globals.set("end_date", event.data.endDate);
```

そして結果をUIへ返す。

```js
self.postMessage({ result: JSON.parse(output) });
```

MDNのWeb Workers APIでも、main threadとworkerは `postMessage()` / `onmessage` でデータを交換する構造が公式に説明されている。

https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API

### 改善後の例

この構成なら、basis point条件を変更する場所は `static_bi.py` の1か所になる。

オフラインテストもブラウザも、次の同じ関数へ到達する。

```python
compare_dates(snapshot, start_date, end_date)
```

UIのJavaScriptへ同じ条件分岐を追加する必要はない。

## 5. 検証：テストした実装と画面で使う実装が同じかを見る

「コードが1ファイルにある」だけでは不十分である。

本当に確認すべきなのは、テスト経路とUI経路が同じ関数へ到達しているかだ。

### オフライン側

公開テストは `compare_dates()` を直接importしている。

```python
from static_bi import compare_dates, validate_snapshot
```

そして、2026-07-20から2026-07-24の比較について次を固定する。

- `delta == 0.09`
- `basis_points == 9.0`
- `direction == "up"`
- `calendar_days == 4`

出典:
https://github.com/KAFKA2306/finBI/blob/71d228ad35228a58d6330896a691bf144bc87f7b/code/tests/test_static_bi.py

さらに異常系として、次もテストされている。

- 開始日と終了日の逆転を拒否
- source URL欠落を拒否
- observation順序の破損を拒否

### ブラウザ側

Workerは同じrepository pathの `./code/static_bi.py` をfetchし、その中の `compare_dates_json()` を呼ぶ。

出典:
https://github.com/KAFKA2306/finBI/blob/71d228ad35228a58d6330896a691bf144bc87f7b/web/worker.mjs

PR #9のCI変更でも、公開artifactへ `code/static_bi.py` をコピーしたうえでHTTP smoke test対象にしている。

出典:
https://github.com/KAFKA2306/finBI/pull/9

ここまで確認して初めて、**テスト対象と配信対象が同じPython sourceである**と言える。

## 6. 失敗と学び：Single Source of Truthは「ファイル数」ではなく「変更理由の数」で考える

「計算式を1ファイルにまとめた」だけでは設計は終わらない。

たとえば、次の構成ではまだ危険が残る。

```text
static_bi.py
  ├─ compare_dates()
  └─ browser用に似た処理を別関数で再実装
```

ファイルは1つでも、変更理由は2つある。

逆に今回のように、

```text
compare_dates()
  ├─ unit testから直接呼ぶ
  └─ compare_dates_json()という薄いadapter越しにbrowserから呼ぶ
```

なら、業務規則の本体は1つに保てる。

もう1つの学びは、ブラウザ実行を採用しても「すべてをPythonにする」必要はないことだ。

`finBI` のPR説明では、JavaScriptはI/Oとrenderingを担当し、金融計算はPythonへ残す方針が明示されている。

https://github.com/KAFKA2306/finBI/pull/9

役割分担は次のように単純化できる。

```text
Python: 正しさを持つ
JavaScript: 操作と表示を持つ
Worker: 2つをつなぐ
```

Web Workerを使うことで処理をmain execution threadから分離できることはMDNにも記載されている。

https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API

ただし、この記事では「Workerを使えば性能が必ず良くなる」とは主張しない。公開実装から確認できるのは、Worker境界でPythonを実行し、メッセージで結果を返していることまでである。

## 7. 再現方法：30行程度で「同じPythonを2経路から使う」を試す

読者が試す場合、金融データは不要である。

まず `calc.py` を作る。

```python
import json


def calculate(payload: dict) -> dict:
    left = float(payload["left"])
    right = float(payload["right"])
    return {
        "sum": left + right,
        "difference": right - left,
    }


def calculate_json(payload_json: str) -> str:
    result = calculate(json.loads(payload_json))
    return json.dumps(result, sort_keys=True)
```

Python側では正準関数を直接テストする。

```python
from calc import calculate

assert calculate({"left": 2, "right": 5}) == {
    "sum": 7.0,
    "difference": 3.0,
}
```

次にブラウザruntime側では `calc.py` を読み込み、`calculate_json()` だけを境界として呼ぶ。

重要なのは、JavaScriptに次を書かないことだ。

```js
// 書かない
const sum = left + right;
const difference = right - left;
```

ブラウザ側は入力の受け渡しと表示だけにする。

検証時は、最低でも次の4点を見る。

1. Python unit testが正準関数を直接呼ぶ
2. browser runtimeが同じPython sourceを読み込む
3. JavaScriptに業務計算式が複製されていない
4. 異常入力の拒否もPython側だけに存在する

### 読者が試せる再現例

最初に `difference = right - left` でテストを通す。

次に仕様を変え、Python側だけ絶対差へ変更する。

```python
"difference": abs(right - left)
```

ブラウザ側に計算式を複製していなければ、UI側のコードを変更しなくても同じ新仕様になる。

一方、JavaScriptにも同じ式を持っていた場合は、そこを直し忘れるだけでテスト結果と画面表示が分岐する。

この差が、Single Source of Truthを導入する実務上の価値である。

## 公開証拠から確認できる範囲

この記事で断定しているのは、2026-08-13時点で公開GitHubから確認できる次の事項だけである。

- `finBI` PR #9は、金融計算を `code/static_bi.py` に置き、JavaScriptはrendering側とする変更を含む
- `static_bi.py` はsnapshot validation、日付比較、delta、basis points、direction、calendar daysを実装している
- `test_static_bi.py` は2026-07-20→2026-07-24について `delta=0.09`、`basis_points=9.0` を検証している
- `worker.mjs` は同じ `code/static_bi.py` をfetchし、`compare_dates_json()` を実行している
- Web Workers APIはmain threadとworkerの間でmessageを送受信できる

性能改善量、初期化時間、全ブラウザでの実測互換性、Pages本番公開成功については、この記事では確認済み事実として扱わない。

## LAPRAS 5軸セルフレビュー

- 論理性: 「二重実装→drift→正準関数1つ→2実行経路」という因果を一つに限定した
- 実用性: Python関数・JSON adapter・Worker境界・最小再現例まで落とした
- 読みやすさ: Pyodide自体の紹介ではなく「計算式を2回書かない」という一般問題から入った
- 独自性: 公開テスト値 `0.09 / 9.0bp` と、同じPython sourceをoffline/browserで共有する実装を具体例にした
- 明確性: 実測性能や本番Pages成功は未確認として除外し、公開コードから確認できる範囲だけを断定した
