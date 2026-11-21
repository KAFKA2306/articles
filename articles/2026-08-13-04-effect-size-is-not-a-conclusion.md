---
title: "記事の年代別比較で、効果量と年代判定の可否を別々に記録する"
emoji: "📏"
type: "tech"
topics: ["python", "statistics", "dataengineering", "testing"]
published: false
published_at: 2026-08-13 21:00
created_at: "2026-08-14"
updated_at: "2026-11-21"
---

**大きな効果量が出たという理由で、未検証の自動判定を許可するな。**

[detectiveの探索](https://github.com/KAFKA2306/detective/commit/64bf09e86ddf76601a4378ac95d7d4d7cb7ffc4e)では2022年と2026年の記事各12件、先頭1000文字を比較し、Cohen's dは約 **-0.760** だった。平均12.0と6.5833、pooled SD約7.125で計算できる。しかし24件の差から未知の記事の年代を判定したり、AI生成が原因と決めつけたりはできない。

[計算スクリプト](https://github.com/KAFKA2306/detective/blob/main/scripts/summarize_2026_oss_distribution_shift.py)と[結果](https://github.com/KAFKA2306/detective/blob/main/reports/zenn_2026_oss_distribution_shift.json)は残す。それでも汎用規律は **「数字を観測する権利と、それを判断に使う権限を分けよ」**。正しい計算でも、不適切な用途での自信は作れる。

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

## -0.760を元の平均と標準偏差から検算する

本文のpilotは2022年と2026年の各12件、記事の先頭1000文字だけを対象にした。平均12.0と6.5833、pooled SD約7.125を使うと次の値になる。

```python
mean_2022 = 12.0
mean_2026 = 6.5833
pooled_sd = 7.125
d = (mean_2026 - mean_2022) / pooled_sd
print(round(d, 3))  # -0.760
```

ここで`-0.760`を計算できても、未知の記事が何年のものか、AIが差を生んだかは分からない。`7.125`はこの24件のばらつきであり、母集団の年代識別能力を保証しない。[元の実装・調査](https://github.com/KAFKA2306/detective/commit/64bf09e86ddf76601a4378ac95d7d4d7cb7ffc4e)

このpilotの結果を下流の分類器へ渡す場合は、`allowed_use.production_decision: false`を確認して止める。数式の再計算、用途の合否、未知データでの性能実測を**別々の検証**として扱う。

## 企業分析やA/B testでも同じ

この考え方は文章特徴量だけではない。

例えば、

- 企業AとBのmargin差
- 製造条件別の不良率差
- UI A/B testのconversion差
- ML model間のscore差

でも、観測値と意思決定権限を分けられる。

手元の探索結果を一つ選び、比較した集団、各集団の件数、指標、次にその値を使いたい判断を書き出す。下のように結果と用途を一緒に保存し、後段で、許可した用途だけが実行できることを確かめる。

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

この例の `-0.760` は、2022年と2026年の各12件を比べた記録として読める。未知記事の年代を判定する処理に渡したときは、用途の確認で止まるのが期待する結果だ。

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


## この規律が適用できる条件と撤回条件

広告A/Bテストの効果、モデルのベンチマーク、金融の特徴量でも、探索用の観測と自動採否を分ける判断を試せる。これらは**応用仮説**であり三分野で性能を測った結果ではない。

独立した検証データと誤判定コストの比較で、特定用途に十分な性能が示せたなら、その用途に限って自動判断へ進める。規律は「数字を永久に使うな」ではない。**何が計算できたかと、何を決めてよいかを別の欄に残す。**
