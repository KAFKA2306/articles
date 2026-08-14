---
title: "差が大きく見えても結論にしない。効果量を記述で止める"
emoji: "📏"
type: "tech"
topics: ["python", "statistics", "dataengineering", "testing"]
published: false
published_at: 2026-08-13 21:00
---

2群の平均値を比較して大きな差が出ると、すぐに「年代を判定できる」「原因はAIだ」と言いたくなる。しかし、小規模な探索データから計算した効果量は、まず**記述統計として保存し、推論・因果・分類へ自動昇格させない**方が安全である。

この記事では、公開リポジトリ `KAFKA2306/detective` の実装を具体例に、計算結果と解釈権限を別フィールドで管理する方法を扱う。

一次情報:

- https://github.com/KAFKA2306/detective/blob/main/scripts/summarize_2026_oss_distribution_shift.py
- https://github.com/KAFKA2306/detective/blob/main/reports/zenn_2026_oss_distribution_shift.json
- https://github.com/KAFKA2306/detective/commit/64bf09e86ddf76601a4378ac95d7d4d7cb7ffc4e

## 1. 問題

実際の入力は、2022年と2026年から各12件、先頭1000文字を解析したpilotである。公開artifactでは `title_case_count` の平均が2022年12.0、2026年6.5833、pooled SDが約7.125、Cohen's d（2026−2022）が約-0.760と記録されている。

数字だけを見ると差は目立つ。しかし、この1値から「2026年の記事を判定できる」とは言えない。

壊れた例は次のような実装である。

```python
if abs(cohen_d) > 0.7:
    result["year_signal"] = True
```

これは効果量という**記述値**へ、未検証の分類能力を勝手に付与している。

## 2. 原因

原因は、計算可能性と解釈可能性を同じものとして扱うことにある。

`detective` の公開scriptは2群の平均とpooled standard deviationからCohen's dを計算できる。一方、同じ実装は入力が各年12件のdescriptive pilotであること、上流featureが日本語で妥当性確認されていないことを理由に、年推論・multiple testing claim・AI因果claimを明示的に禁止している。

つまり、**数値を正しく計算できることは、その数値を意思決定へ使ってよい証拠ではない**。

## 3. 設計判断と代替案

代替案は3つある。

1. 効果量が閾値を超えたら自動で意味ラベルを付ける。単純だが、閾値自体が用途妥当性を保証しない。
2. 効果量を計算せず、生データだけ保存する。過剰解釈は減るが、探索時の比較可能性まで失う。
3. 効果量は計算・保存するが、解釈権限を別のgateとして保存する。

ここでは3を採る。`detective` のartifactは `status: descriptive_pilot_only` とし、さらに `interpretation_gate` に `use_for_year_inference: false`、`multiple_testing_claims: false`、`causal_ai_claim: false` を保存している。

重要なのは「弱いデータだから捨てる」ことではない。**観測結果は残し、許可されていない用途だけを閉じる**。

## 4. 実装

最小構成は、数値と権限を分離するだけでよい。

```python
result = {
    "status": "descriptive_pilot_only",
    "effect": {
        "cohen_d": d,
        "absolute_cohen_d": abs(d),
    },
    "interpretation_gate": {
        "use_for_year_inference": False,
        "multiple_testing_claims": False,
        "causal_ai_claim": False,
    },
}
```

`detective` の実装ではさらに、入力長を1000文字へ固定しているため常に同じになる `char_count` を `eligible_for_interpretation: false` としてranking対象から除外している。

改善後の例では、`title_case_count` の `absolute_cohen_d` 約0.760という観測値は残る。一方で、それを年代分類やAI原因説へ使う経路は閉じたままになる。

## 5. 検証

守るべきcontractは「効果量が計算できる」だけではない。**禁止した解釈が出力上でも禁止されたままか**をtestする。

```python
assert output["status"] == "descriptive_pilot_only"
assert output["interpretation_gate"]["use_for_year_inference"] is False
assert output["interpretation_gate"]["multiple_testing_claims"] is False
assert output["interpretation_gate"]["causal_ai_claim"] is False
assert output["features"]["char_count"]["eligible_for_interpretation"] is False
```

公開workflowも、固定pilotの測定後にsummary scriptを実行し、measurement JSONとdistribution-shift JSONの両方をevidenceとしてcommitする構成になっている。

## 6. 失敗と学び

失敗は「大きそうな効果量」を「強い結論」と読み替えることである。

今回の公開artifact自身が、各年12件、1000文字window、descriptive pilotという制約を持つ。またinterpretation gateのreasonには、日本語で未検証のfeatureがtopic・formatting・English-tokenization artifactを拾う可能性が明記されている。

したがって、観測された差を消す必要はないが、そこから年代推論やAI因果へ飛ぶべきでもない。

学びは、analysis pipelineの出力に**「何が分かったか」だけでなく「何には使ってはいけないか」もmachine-readableに保存する**ことである。READMEの注意書きだけより、後段コードが誤用を検出しやすい。

## 7. 再現方法

読者は次の最小例で、計算と解釈gateの分離を試せる。

```python
import math

A = {"n": 12, "mean": 12.0, "std": 7.0}
B = {"n": 12, "mean": 6.6, "std": 7.2}

variance = (
    (A["n"] - 1) * A["std"] ** 2
    + (B["n"] - 1) * B["std"] ** 2
) / (A["n"] + B["n"] - 2)
pooled_sd = math.sqrt(variance)
d = (B["mean"] - A["mean"]) / pooled_sd

output = {
    "cohen_d": d,
    "use_for_classification": False,
    "causal_claim": False,
}

assert isinstance(output["cohen_d"], float)
assert output["use_for_classification"] is False
assert output["causal_claim"] is False
print(output)
```

ここで確認するのはdの大小ではない。**計算結果が存在しても、未検証の用途が自動的にtrueにならない**ことである。

実務ではこのgateをJSON Schemaや型へ昇格させ、後段のclassifier・report generator・LLM promptが `descriptive_pilot_only` を無視できないようにするとよい。

## まとめ

探索分析では、数値を出さないことより、数値の権限を狭く保つことが重要になる。

- 効果量は観測値として保存する
- 入力設計上意味のないfeatureはrankingから外す
- 推論・multiple testing・因果claimの可否を別gateにする
- 未検証用途をmachine-readableなfalseとして残す

この分離を入れると、探索結果を捨てずに残しながら、後段の自動化が「差がある」から「判定できる」「原因が分かった」へ勝手に飛躍するのを防げる。
