---
title: "型チェッカーを変える前に、設定差を製品差から消す"
emoji: "🧪"
type: "tech"
topics: ["python", "typechecking", "ci", "testing", "developerexperience"]
published: false
---

新しい型チェッカーを試して「Aは2/5、Bは5/5」と出たら、Bへ移行したくなる。

私はそこで一度、結論を間違えた。

同じPyrefly 1.2.0、同じ5つのroot faultでも、`basic` presetでは **2/5**、`default` presetでは **5/5** だった。製品を変えなくても、設定だけで結果が3件動いた。

だから比較表を作る前にやることがある。

**version・preset・config・scope・blocking severityを固定し、設定差を製品差から先に取り除く。**

## 2/5から5/5へ動いた

固定fixtureは5 failure classだけに絞った。

- syntax failure
- incompatible argument type
- incompatible return type
- undefined name
- async misuse

同じPyrefly 1.2.0の結果はこうだった。

| configuration | detected |
|---|---:|
| no config → `basic` | 2/5 |
| `basic` | 2/5 |
| `default` | 5/5 |

raw evidence:
https://github.com/KAFKA2306/articles/blob/822be109de61e5915799fcf7d79e6345dff4f6b1/benchmarks/verification-stack-v2/results/controlled/pyrefly-preset-calibration.json

Pyrefly公式も、設定のないprojectでは`basic`を使い、高confidenceなdiagnosticへ絞ると説明している。`default`や`strict`は別のdiagnostic surfaceを持つ。

https://pyrefly.org/en/docs/configuration/

つまり「Pyreflyは2/5だった」という書き方では情報が欠ける。正しくは、**Pyrefly 1.2.0をbasic presetで、この5 faultへ当てたとき2/5だった**だ。

## 私が捨てた比較方法

```text
pyrefly: 2/5
pyright: 5/5
↓
pyrightの方が強い
```

この比較は、両者へ何をblockさせたかが揃っていないと製品比較にならない。

修復後、同じ5 mutantに対するtested configurationでは、mypy / Pyright / ty / Pyreflyはいずれも5/5だった。

https://github.com/KAFKA2306/articles/blob/822be109de61e5915799fcf7d79e6345dff4f6b1/benchmarks/verification-stack-v2/results/controlled/summary.json

ここから「4製品は同等」とも言えない。5件しか測っていない。消えたのは、旧2/5対5/5を**製品固有の差だとする根拠**だけだ。

## 比較を6段階にする

型チェッカーを移行するときは次の順で十分だった。

1. repoで絶対にblockしたいfailureを1 root faultずつfixture化する
2. clean baselineを用意する
3. tool versionを固定する
4. preset / mode / config / scope / severityを固定する
5. `clean=pass && fault=block`だけを成功として数える
6. correctnessを満たした候補だけ速度・導入コスト・保守量を比べる

最後の段階で機能と運用性が同等なら、**LOC、設定ファイル、dependency、CI commandが少ない方を選ぶ**。複雑性は有効なtie-breakerだが、設定の違う候補を無理に同点扱いするためには使わない。

## benchmark結果と一緒に残す最小メモ

```text
checker: pyrefly 1.2.0
preset: default
config: pyproject.toml
scope: src + tests
python: 3.12
blocking severity: error
```

この6項目があれば、半年後でも「製品を比較したのか、設定を比較したのか」を追いやすい。

## 証拠の境界

今回の5 mutantはtyping全体のaccuracyを証明しない。editor behavior、third-party stubs、incremental analysis、大規模repoも未評価だ。

それでも比較手順を変える理由にはなった。**同一binary・同一version・同一fixtureで、presetだけを変えると2/5→5/5になった**からだ。

型チェッカーを選ぶ前に、まず比較対象から設定差を消す。それから初めて、製品差と複雑性を比べる。