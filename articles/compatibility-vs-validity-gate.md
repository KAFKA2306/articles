---
title: "OSSが動いたのに、判定には使えない。互換性確認と妥当性確認を分離する"
emoji: "🧪"
type: "tech"
topics: ["python", "machinelearning", "testing", "opensource"]
published: true
published_at: 2026-08-13 12:00
---

外部OSSを評価するとき、最も危ない成功は「例外なく動いた」です。

APIが呼べた。値も返った。CIもgreen。ここまで揃うと、その出力をそのまま業務判断へ使いたくなります。しかし、**実行できることと、その出力を解釈してよいことは別の契約**です。

`KAFKA2306/detective` では、2026年8月13日に `stylometric-ai-detector` 0.2.4 を日本語の技術記事サンプルへ適用するpilotを実装しました。パッケージは実行でき、年別集計も作れました。一方、upstreamはこのモデルを英語単一データセット由来のbaselineと明記し、言語・domain・AI model generationをまたぐgeneralizationを保証していません。

そこで実装側では、結果が返っても `use_for_ai_authorship: false`、`use_for_year_inference: false` とする **interpretation gate** を別に置きました。

この記事では、この設計を一般化して、外部モデル・SDK・推論API・評価器を導入するときに使える「互換性」と「妥当性」の二段ゲートとして整理します。

## 1. 問題：`success` が強すぎる

外部ライブラリを試す最初のコードは、たいてい次のようになります。

```python
from some_detector import predict

result = predict(text)
print(result)
```

例外が出ず、`{"label": "AI", "probability": 0.91}` のような値が返れば、技術的には成功です。

しかし、この `success` には少なくとも3種類が混ざっています。

1. importできた
2. 対象入力で関数が実行できた
3. 返値を目的の判断に使ってよい

1と2はruntime compatibilityです。3はvalidationです。ここを同じbooleanで表すと、**「動いた」が「正しい」に昇格**します。

### 実際の状況

`detective` のpilotは、日本語記事を1000文字の固定windowへ正規化し、`stylometric-ai-detector` の8特徴量と予測値を記録します。2022〜2026年を各12件、合計60件に固定し、入力件数がずれれば処理を止める実装です。

実装証拠:

- https://github.com/KAFKA2306/detective/commit/a7f7872e45665022a4ee77bf51362f78c97f53bd
- https://github.com/KAFKA2306/detective/blob/main/reports/zenn_stylometric_ai_detector_2026_measurement.json

この実測では、2022年の12件はすべてupstream labelが `AI`、2024年は11件が `AI`、1件が `Human` でした。**ここから「2022年の日本語技術記事はAI生成だった」と結論してはいけません。** レポート自体も `status: measured_not_validated` とし、用途を明示的に閉じています。

## 2. 原因：モデルの適用範囲と、こちらの入力分布が違う

upstream READMEは、このモデルについて次を明記しています。

- Random Forestによるbaseline
- 8個のsurface-level stylometric featuresを使用
- 単一の英語データセットで学習
- pre-2024 dataで学習
- domain、language、AI model generationをまたぐgeneralizationを保証しない
- production detectorではなくbenchmark用途を想定

一次情報:

- https://github.com/dinis-a/stylometric-ai-detector/blob/main/README.md

つまり、日本語入力で `predict()` が例外なく返値を出すことは、**Python APIの互換性**しか証明していません。

学習分布外であっても、文字数・句読点数・大文字語数のような特徴量は数値化できます。Random Forestにも数値は渡せます。したがって、runtime errorが起きないことと、統計的に妥当な判定ができることは独立です。

ここが壊れやすいポイントです。

```text
関数が呼べる
  ↓
特徴量が返る
  ↓
確率が返る
  ↓
それっぽいラベルが返る
  ↓
「使える」と誤認する
```

最後の矢印だけは、APIが保証してくれません。

## 3. 設計判断と代替案：gateを2つに分ける

採用した設計は、compatibility gateとinterpretation gateを分離することです。

```json
{
  "status": "measured_not_validated",
  "interpretation_gate": {
    "use_for_ai_authorship": false,
    "use_for_year_inference": false,
    "reason": "upstream generalization to Japanese is not established"
  }
}
```

### Gate A: compatibility

ここでは機械的事実だけを確認します。

- importできるか
- 指定versionか
- 想定する引数を受け取るか
- return typeが契約どおりか
- 対象入力で例外なく完走するか
- 入力件数・window長などの前処理契約が固定されているか

### Gate B: interpretation

こちらは「この結果から何を言ってよいか」を管理します。

- 学習言語と入力言語が一致するか
- domainが一致するか
- 学習時期が現在の対象を含むか
- upstreamがproduction用途を許容しているか
- 自前validation setで性能を確認したか
- 因果・年代推定・authorship判定へ用途を拡張していないか

### 代替案1：動いたら採用する

最も簡単ですが、不採用です。distribution shiftを検知できず、成功したAPI callがそのまま意思決定へ流れます。

### 代替案2：未検証だから一切実行しない

安全ですが、これも弱いです。互換性、返値schema、feature挙動、失敗条件といった**観測可能な事実まで捨てる**ことになります。

### 代替案3：確率値だけ保存し、解釈は人間に任せる

これも不十分です。下流がそのJSONを再利用した瞬間に、元の注意書きが失われます。

そのため、**値と同じartifactに「何へ使ってはいけないか」を機械可読で保存する**設計を採用しました。

## 4. 実装：観測値と禁止用途を同じJSONへ固定する

実装の中心は、結果を成功/失敗だけで終わらせないことです。

```python
report = {
    "status": "blocked",
    "samples": {},
    "interpretation_gate": {
        "use_for_ai_authorship": False,
        "use_for_year_inference": False,
        "reason": (
            "Compatibility probe only; "
            "upstream generalization to Japanese is not assumed."
        ),
    },
}
```

日本語probeの初期実装でも、最初から用途制限をartifactへ含めています。

実装証拠:

- https://github.com/KAFKA2306/detective/commit/554cec387761da2e292e1d8800b86c97eddbc268

さらに60件pilotでは、入力契約もfail-closeにしています。

```python
if len(source_rows) != 60:
    raise RuntimeError(f"expected fixed 60-row pilot, got {len(source_rows)}")

if len(normalized) < ANALYSIS_WINDOW_CHARS:
    raise RuntimeError("normalized text shorter than fixed window")

if not isinstance(features, dict) or not isinstance(prediction, dict):
    raise RuntimeError("unexpected upstream return type")
```

ここで重要なのは、**モデルの妥当性が未確認だからといって、測定処理まで曖昧にしない**ことです。

未検証なものほど、入力・version・件数・前処理・hash・return typeを厳格に固定したほうが、後からvalidationを追加しやすくなります。

## 5. 検証：何を確認し、何を確認していないかを分ける

このpilotで確認できたのは次です。

```text
stylometric-ai-detector 0.2.4
        ↓
日本語1000文字window
        ↓
8特徴量を抽出できる
        ↓
predict() がdictを返す
        ↓
60件の観測値を年別に集計できる
```

一方、確認していないものは次です。

```text
日本語でのAI/Human識別精度
年代推定精度
2022→2026変化の原因
生成AI普及との因果関係
他domainへの一般化
```

この境界をコードにも残しています。2022年と2026年の特徴量差をCohen's dで要約する後段処理でも、出力statusは `descriptive_pilot_only` です。また、`use_for_year_inference: false`、`causal_ai_claim: false`、`multiple_testing_claims: false` を固定しています。

実装証拠:

- https://github.com/KAFKA2306/detective/commit/541320e61b5444d89cb43c4a958864209717dfbc

これは「統計値を計算しない」のではなく、**計算できることと主張できることを分離する**設計です。

## 6. 失敗と学び：もっとも危険なのは、壊れずにもっともらしい値を返すこと

### 壊れた失敗例

次のような実装は、CIでは成功しやすい一方で、用途境界を失います。

```python
result = predict(japanese_text)

if result["label"] == "AI":
    mark_as_ai_generated()
```

問題は、例外が起きないことです。

対象外言語でも、特徴量抽出器が数値を作れればclassifierは結果を返せます。`0.91` のような小数は精密に見えるため、人間にも下流コードにも強い説得力を持ちます。

しかしupstreamが英語単一dataset由来で、language generalizationを保証していない以上、その確率値を日本語authorship判定へ直結させる根拠はありません。

### 改善後の例

```python
result = predict(japanese_text)

artifact = {
    "runtime_status": "success",
    "result": result,
    "interpretation_gate": {
        "validated_for_target_language": False,
        "allow_decision_use": False,
    },
}

if artifact["interpretation_gate"]["allow_decision_use"]:
    apply_decision(result)
```

この形なら、**実行成功を保存しつつ、意思決定への昇格だけを止められます。**

学びは単純です。

> 未検証の外部モデルは「使う/使わない」の二択ではない。まず測れるものを測り、解釈権限だけを閉じる。

## 7. 再現方法：10分で二段ゲートを試す

読者が手元で再現するなら、実モデルでなくても構造は試せます。

### Step 1: compatibility probeを書く

```python
from dataclasses import asdict, dataclass

@dataclass
class InterpretationGate:
    validated_for_target_language: bool
    allow_decision_use: bool
    reason: str


def run_probe(predict, text: str) -> dict:
    result = predict(text)
    if not isinstance(result, dict):
        raise TypeError("predict() must return dict")

    gate = InterpretationGate(
        validated_for_target_language=False,
        allow_decision_use=False,
        reason="runtime compatibility only",
    )

    return {
        "runtime_status": "success",
        "result": result,
        "interpretation_gate": asdict(gate),
    }
```

### Step 2: fake predictorで成功経路を確認する

```python
def fake_predict(_: str) -> dict:
    return {"label": "AI", "probability": 0.93}

artifact = run_probe(fake_predict, "これは日本語のテスト入力です。")

assert artifact["runtime_status"] == "success"
assert artifact["result"]["probability"] == 0.93
assert artifact["interpretation_gate"]["allow_decision_use"] is False
```

ここで見るべきなのは、**0.93が返ってもdecision gateが開かない**ことです。

### Step 3: validation完了後だけgateを変更する

対象言語・domain・datasetで別途validationし、受入基準を満たした場合にだけ、設定を変更します。

```python
"interpretation_gate": {
    "validated_for_target_language": True,
    "allow_decision_use": True,
    "validation_report": "reports/ja-domain-v1.json"
}
```

重要なのは、この変更を「担当者の判断」ではなく、validation reportへ紐づけることです。

## 実務へ持ち帰る最小ルール

外部モデルや評価器を導入するときは、次の4点だけでも効果があります。

1. `runtime_status` と `decision_use` を別fieldにする
2. upstreamのlimitationsをartifactへ写経せず、URLで固定する
3. 未検証時はfail-openで解釈しない
4. validationが終わるまで、観測値は「測定値」であって「判定根拠」ではない

APIの成功は便利です。しかし、**「この値を何に使ってよいか」までAPIが決めてくれることはほとんどありません。**

だから境界をコードにする必要があります。

## 一次情報

- `stylometric-ai-detector` upstream README: https://github.com/dinis-a/stylometric-ai-detector/blob/main/README.md
- 日本語compatibility probe実装: https://github.com/KAFKA2306/detective/commit/554cec387761da2e292e1d8800b86c97eddbc268
- 60件pilot測定実装: https://github.com/KAFKA2306/detective/commit/a7f7872e45665022a4ee77bf51362f78c97f53bd
- 2022 vs 2026 descriptive summary実装: https://github.com/KAFKA2306/detective/commit/541320e61b5444d89cb43c4a958864209717dfbc
- pilot測定artifact: https://github.com/KAFKA2306/detective/blob/main/reports/zenn_stylometric_ai_detector_2026_measurement.json
