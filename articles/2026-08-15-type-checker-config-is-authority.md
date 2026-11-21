---
title: "ツールの優劣を語る前に、設定差を消せ"
emoji: "🧪"
type: "tech"
topics: ["python", "typechecking", "ci", "testing", "developerexperience"]
published: false
created_at: "2026-08-15"
updated_at: "2026-11-21"
---

**異なる設定の測定値を、製品の優劣として比べるな。**

同じPyrefly 1.2.0、同じ五つの故障入力で、`basic`は **2/5**、`default`は **5/5** を検出した。ツールを一つも変えず、presetだけで三件増えた。「別製品が優秀だった」と説明してしまえば、設定の効果を製品の手柄にできる。

規律は **「道具を比較する前に、入力・版・設定・検査対象を固定せよ」**。実際に測ったのはこの一製品の設定差であり、別の型チェッカーの優劣や本番repoでの有効性ではない。

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

型チェッカーを移行するときは、現在CIが読む設定ファイルと、必ず検出したい失敗を用意する。各失敗は別々のサンプルにし、同じファイル群をすべての候補に渡す。

1. repoで絶対にblockしたいfailureを1 root faultずつfixture化する
2. clean baselineを用意する
3. tool versionを固定する
4. preset / mode / config / scope / severityを固定する
5. `clean=pass && fault=block`だけを成功として数える
6. correctnessを満たした候補だけ速度・導入コスト・保守量を比べる

同じ候補で検出数が変わったら、どの失敗がどの設定で通ったかを記録し、既定の設定も調べる。必須の失敗を拾い、正常時の動作もそろった候補同士で、速度や設定・依存関係の維持にかかる手間を比べる。

## 製品比較の表を、同一ツールの設定比較に戻す

今回固定した5件はsyntax、引数型、戻り値型、未定義名、async誤用だった。Pyrefly 1.2.0で`basic`は2/5、`default`は5/5。どちらも**同一製品**なので、結論は「製品が違う」ではなく「設定で停止する診断が違う」である。[raw evidence](https://github.com/KAFKA2306/articles/blob/822be109de61e5915799fcf7d79e6345dff4f6b1/benchmarks/verification-stack-v2/results/controlled/pyrefly-preset-calibration.json)

```text
tool/version: Pyrefly 1.2.0
input:        同じ5件のfault + 正常な入力
A:            preset=basic   → 2/5
B:            preset=default → 5/5
conclusion:   設定差を記録し、製品の優劣とはしない
```

例えば`def f() -> int: return "text"`は戻り値の型を意図的に壊した例として使える。ただし、**この例が実験のどのpresetで検出されたかは本文からは推測しない**。それは上記の成果物に戻って確かめる。実際のコードベース・Python版・設定・対象範囲まで一致してから旧チェックの削除を決める。

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

## この規律が適用できる条件と撤回条件

データベースの速度、LLMの費用、画像圧縮の品質も、入力や設定が違えば「製品差」という説明は危うい。これらは比較手順の**応用仮説**であり各分野の評価を実行した結果ではない。

設定・入力・対象・計測方法をそろえてなお差が残るなら、初めて製品側の違いを検討できる。製品ごとに対応設定が根本的に異なる場合は「同じ構成の比較」とは呼ばず、実際の運用構成を含む比較だと明記する。**比較の結論より、比較できる条件を先に作る。**
