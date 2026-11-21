---
title: "「動いた」を「使ってよい」と呼ぶな"
emoji: "🧪"
type: "tech"
topics: ["python", "machinelearning", "nlp", "testing"]
published: true
published_at: 2026-08-14 16:00
created_at: "2026-08-14"
updated_at: "2026-11-21"
---

**結果が返ったというだけで、その結果を判断へ使うな。**

`stylometric-ai-detector` 0.2.4は日本語記事60件へ値を返した。しかし、正解ラベルで照合していないので日本語の判定精度は不明だ。一方、別の検出器は英語spaCyモデル`en_core_web_sm`がないとimport時点で止まった。

[detectiveの検証](https://github.com/KAFKA2306/detective)で分けるべきだったのは`installed`、`runnable`、`validated`、`allowed_use`である。**プログラムの実行成功は、現実の用途で正しい答えを返す証拠ではない。**

## `success` という1語が強すぎる

外部toolの導入では、少なくとも4つの状態がある。

```text
1. INSTALLED
   依存関係が揃った

2. RUNNABLE
   対象入力で処理が完走した

3. VALIDATED
   対象言語・domain・用途で妥当性を確認した

4. ALLOWED_USE
   その結果を具体的な意思決定へ使ってよい
```

この4つを `success: true` に潰すと、

```text
importできた
→ 動いた
→ 精度も十分
→ 業務判断に使える
```

と意味が勝手に昇格する。

**runtime successは、validationの代わりにならない。**

## Case 1: 日本語を試す前に、英語model依存で止まった

`explain_ai_generated_text` 0.1.1.1.7を調べたとき、日本語入力そのものへ到達する前にimport時点で停止した。

原因はspaCyの `en_core_web_sm` model依存だった。

- https://github.com/KAFKA2306/detective/commit/554cec387761da2e292e1d8800b86c97eddbc268
- https://github.com/KAFKA2306/detective/commit/0d2f2da1d064c45fe8c5554cb314b712d102976d
- https://github.com/ShushantaTUD/Explain_AI_Generated_Text/blob/78b7d674e03cd2b4fdde065bfef493854f43c2f1/src/explain_ai_generated_text/utils.py
- https://github.com/ShushantaTUD/Explain_AI_Generated_Text/blob/78b7d674e03cd2b4fdde065bfef493854f43c2f1/pyproject.toml

この時点で分かるのは、

> 日本語で性能が悪い

ではない。

まだ、

> **評価環境がruntime compatibilityの入口を通っていない**

だけである。

失敗理由をここで止めると、未検証を低性能へ誤変換しないで済む。

## Case 2: 60件すべて処理できても、利用許可は出さなかった

別のpilotでは `stylometric-ai-detector` 0.2.4を日本語技術記事へ適用した。

2022〜2026年を各12件、合計60件に固定し、1000文字windowで特徴量と予測値を記録した。

処理自体は完走した。

実測では、2022年の12件はすべてupstream labelが `AI`、2024年は11件が `AI`、1件が `Human` だった。

ここで「2022年の日本語技術記事はAI生成だった」と結論したら、かなり危険である。

upstreamは英語単一dataset由来のbaselineであり、日本語・別domain・別generation modelへのgeneralizationを保証していない。

そのためartifactは、

```text
measured_not_validated
```

として保存した。

- `use_for_ai_authorship: false`
- `use_for_year_inference: false`

値が返ったことは捨てない。

しかし、**値が返ったからといって、その意味まで自動で与えない。**

## 「対応しています」ではなく「ここまで確認済み」を表示する

利用者にとって重要なのは、toolが使える / 使えないのbinaryではない。

例えばUIやreportで次のように出せる。

| State | Result |
|---|---|
| Dependency ready | yes |
| English control runnable | yes |
| Japanese probe runnable | yes |
| Japanese semantic validity | not validated |
| Use for authorship decision | no |

これなら、利用者は「値は見られるが、判断には使えない」と分かる。

**unknownをfailureにもsuccessにも潰さない。**

この中間状態があるだけで、外部OSSを大胆に試しながら、業務判断だけは慎重にできる。

## validationは、用途ごとに違う

「日本語でvalidated」という1フラグでもまだ粗い。

同じモデルでも、

```text
exploratory visualization
feature research
ranking
human review assistance
automated rejection
high-stakes decision
```

では必要な証拠が違う。

そこで最終的には `allowed_use` を用途単位で持つ方が扱いやすい。

```yaml
allowed_use:
  exploratory_analysis: true
  feature_research: true
  ai_authorship_decision: false
  automatic_rejection: false
```

これなら、検証途中の成果を全部捨てずに済む。

**使える範囲だけ開ける。**

## probeはcontrolと未知入力を分ける

未知言語や別domainを試すとき、対象入力だけを投げると、失敗原因が分かりにくい。

そこで、

```text
english_control
japanese_probe
```

のようにcontrolを置く。

もし両方失敗するなら、依存関係や環境の可能性が高い。

controlは通るがJapaneseだけ失敗するなら、入力互換性の問題へ近づく。

両方値を返しても、semantic validityはまだ別である。

```text
dependency
   ↓
runtime control
   ↓
unknown-input probe
   ↓
semantic validation
   ↓
allowed use
```

この順序にすると、失敗理由を一段ずつ狭められる。

## 「高いscoreが出た」をvalidationにしない

外部modelを試していると、0.91のような強い確率値が返ることがある。

```json
{
  "label": "AI",
  "probability": 0.91
}
```

しかし、この0.91は**model内部の出力**であって、日本語で91%正しいという意味ではない。

validationに必要なのは、

- ground truth
- target distribution
- evaluation protocol
- sample size
- relevant metric
- failure analysis

など別の証拠である。

model confidenceとmodel validityを混ぜない。

## 外部OSSを導入するときの最小report

大きなML governance基盤がなくても、次の形なら始められる。

```yaml
tool: some-detector
version: 0.2.4

dependency_ready: true
runtime_compatible: true
semantic_validation: not_done

allowed_use:
  exploratory: true
  automated_decision: false

reason:
  - upstream validation scope does not cover Japanese
  - local pilot measured outputs but has no ground truth
```

このreportがあれば、後からvalidationを追加してstateを更新できる。

## 「使えない」で終わらせないのも大事

慎重にしすぎると、外部OSSを一切試せなくなる。

今回のようなpilotにも価値はある。

- 依存関係が見える
- 特徴量schemaが分かる
- latencyやmemoryが測れる
- 出力distributionを観測できる
- validation計画を作れる

だから、

```text
not validated
```

は、

```text
useless
```

ではない。

**探索は続ける。判断利用だけを閉じる。**

この分離があると、研究速度と安全性を両立しやすい。

## ML以外のSDKやAPIでも同じ

この考え方はNLPだけではない。

- 新しいOCR library
- 画像分類model
- translation API
- vector database
- browser automation SDK
- financial data provider

でも同じである。

```text
接続できた
≠
対象データで動いた
≠
意味的に正しい
≠
業務判断へ使ってよい
```

外部toolの導入で失敗しやすいのは、動かないことだけではない。

**動いたことで安心しすぎること**でもある。

## 日本語60件に値が返っても、正解率は未測定

本文の`stylometric-ai-detector` 0.2.4は、日本語記事60件へ結果を返した。しかし正解ラベルと照合していないなら、正解率や誤判定率は計算できない。

```text
tool/version: stylometric-ai-detector 0.2.4
language: Japanese
sample_count: 60
runnable: YES（値が返った）
validated: NO（日本語での判定の妥当性は未実証）
allowed_use: 探索の観測に限定
forbidden: 作者やAI生成の断定
```

これは[元の検証リポジトリ](https://github.com/KAFKA2306/detective)で記録された到達範囲を説明する表で、60件に正解ラベルがあったという主張ではない。作者判定に使う前には、人間執筆とAI生成の**正解が分かる別データ**を用意し、誤陽性と見逃しを別に数える。調整に使ったデータを同じ精度評価へ再利用しない。

## まず1つのOSS評価から変えるなら

検出ツールを試すときは、対象の言語と用途を一つ決め、既に動く入力と、使いたい言語の入力を用意する。書き手を判定する用途まで調べるなら、正解が分かっている評価データも用意する。

最低限、

```text
installed
runnable
validated
allowed_use
```

へ分ける。

先に既に動く入力を通し、その後で対象言語を試す。両方で値が出た段階では `runnable` を記録する。対象データで判定の妥当性まで確かめてから `validated` を更新し、`allowed_use` には根拠がそろった用途を書き込む。

OSSを速く試しながら、**どこまで信用してよいかを利用者へ正確に伝える**ことができる。


## 汎用規律の移植と撤回条件

OCR、検索モデル、外部APIでも、動作確認と目的に沿った品質検査を別にする設計を試せる。これは**応用仮説**であって、他分野の精度測定ではない。

正解が分かる独立評価データで誤判定率と費用を測り、用途ごとの合格条件を満たせば`allowed_use`を広げられる。この規律は「永遠に使うな」ではない。**60件の動作実績と60件の妥当性の証明を混同しない。**
