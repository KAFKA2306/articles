---
title: "Cohen's dが0.76でも「判定できる」とは言わない。数字と利用許可を分ける"
emoji: "📏"
type: "tech"
topics: ["python", "statistics", "dataengineering", "testing"]
published: false
published_at: 2026-08-13 21:00
---

探索分析で **Cohen's d ≈ -0.760** が出た。

数字だけを見ると、かなり差がありそうに見える。

ここで次のコードを書きたくなる。

```python
if abs(cohen_d) > 0.7:
    result["year_signal"] = True
```

しかし今回、それはしなかった。

`KAFKA2306/detective` のpilotは、2022年と2026年から各12件、先頭1000文字を解析した小規模な探索だった。

- 2022 mean: 12.0
- 2026 mean: 6.5833
- pooled SD: 約7.125
- Cohen's d: 約-0.760

観測された差は残す。

一方で、

```text
年代を判定できる
AI生成が原因である
未知記事へ一般化できる
```

とは言わない。

この記事で扱うのは効果量の計算方法ではない。

**派手な数字が出ても、証拠の強さを超えて意思決定へ昇格させない分析UX**について書く。

- script: https://github.com/KAFKA2306/detective/blob/main/scripts/summarize_2026_oss_distribution_shift.py
- artifact: https://github.com/KAFKA2306/detective/blob/main/reports/zenn_2026_oss_distribution_shift.json
- commit: https://github.com/KAFKA2306/detective/commit/64bf09e86ddf76601a4378ac95d7d4d7cb7ffc4e

## 数字を消すのではなく、権限を狭くする

探索結果を過大解釈したくないなら、数字を出さない方法もある。

しかし、それでは比較や次の仮説づくりに使える情報まで失う。

そこで、

```text
measurement
```

と、

```text
allowed interpretation
```

を別々に保存する。

```json
{
  "status": "descriptive_pilot_only",
  "effect": {
    "cohen_d": -0.760
  },
  "interpretation_gate": {
    "use_for_year_inference": false,
    "multiple_testing_claims": false,
    "causal_ai_claim": false
  }
}
```

この形なら「差が観測された」は残る。

その一方で、「年代判定に使える」へ勝手に昇格しない。

**弱い証拠を捨てるのではなく、使える範囲だけ開ける。**

## 計算できることと、判断に使えることは別

効果量の式が正しいことは重要である。

しかし、用途妥当性には別の問題がある。

今回のpilotには、少なくとも次の制約がある。

- 各年12件
- 1000文字の固定window
- feature自体が日本語用途で十分にvalidationされていない
- topicやformatting差を拾っている可能性がある
- multiple testingやcausal inferenceを目的に設計していない

だから、`d = -0.760` の正確な計算から、直接 `year_signal = true` とは言えない。

**metric correctnessとdecision validityは別contract**である。

## 「何に使えるか」をmachine-readableにする

READMEへ「参考値です」と書くだけでも警告にはなる。

ただし後段の自動処理は、その文章を無視できる。

そこで用途をfieldとして持たせる。

```yaml
allowed_use:
  exploratory_comparison: true
  feature_ranking: limited
  year_classification: false
  causal_ai_claim: false
```

これならreport generatorやLLM prompt側でも、禁止用途を確認できる。

例えば、

```python
if not result["allowed_use"]["year_classification"]:
    raise ValueError("This pilot cannot be used for year classification")
```

と後段で止められる。

**注意書きをデータ契約へ昇格させる。**

## 大きな値ほど、用途gateが必要になる

小さな差なら慎重になりやすい。

逆に大きな差が出ると、「これは使えそうだ」という心理が強くなる。

そこが危ない。

```text
大きなeffect size
→ 興味深い観測
```

まではよい。

しかし、

```text
大きなeffect size
→ 予測できる
→ 原因が分かった
```

には追加証拠が必要である。

この昇格をコード上で別stageへすると、分析者の気分に左右されにくい。

## feature自身が意味を持つかも確認する

今回の実装では、入力長を1000文字へ固定したため常に同じになる `char_count` を `eligible_for_interpretation: false` として扱っている。

これは小さいが重要な例である。

数値として計算できても、実験設計上意味がないfeatureならrankingへ入れない。

```text
calculated
≠
meaningful
≠
decision-ready
```

この3段階を混ぜない。

## testすべきなのは、禁止用途が開いていないこと

分析pipelineでは「計算が成功した」testだけを書きがちである。

しかし今回守りたいのは、解釈境界も含む。

```python
assert output["status"] == "descriptive_pilot_only"
assert output["interpretation_gate"]["use_for_year_inference"] is False
assert output["interpretation_gate"]["multiple_testing_claims"] is False
assert output["interpretation_gate"]["causal_ai_claim"] is False
```

このnegative contractがあると、将来reportを便利にする変更で禁止用途が勝手に開くのを防げる。

## 企業分析やA/B testでも同じ

この考え方は文章特徴量だけではない。

例えば、

- 企業AとBのmargin差
- 製造条件別の不良率差
- UI A/B testのconversion差
- ML model間のscore差

でも、観測値と意思決定権限を分けられる。

最小schemaなら次でよい。

```yaml
metric:
  name: cohen_d
  value: -0.760

evidence_strength:
  status: exploratory
  sample_size: 24

allowed_use:
  exploration: true
  production_decision: false
```

読者や下流systemは、数字だけでなく「どこまで使える数字か」を同時に見られる。

## この設計で欲しいのは、慎重さより分析速度

用途gateを入れると保守的に見える。

しかし実際には、探索を速くできる。

弱いpilotでも、

```text
探索用途なら保存してよい
```

と明示できるからだ。

すべてをproduction-grade validationまで待つ必要はない。

- 観測は残す
- 仮説を作る
- 次の実験を決める
- 判断用途だけは閉じる

この分離により、**探索の速度を落とさず、過剰解釈だけを止める**ことができる。

Cohen's dが0.76だったことより重要なのは、その数字にどの権限を与えたかだった。
