---
title: "型チェッカー比較で先に固定すべきなのは、製品名ではなく設定"
emoji: "🧪"
type: "tech"
topics: ["python", "typechecking", "ci", "testing", "developerexperience"]
published: false
---

型チェッカーを比較して「Aは5件中2件、Bは5件中5件だった」と出たら、製品差だと思いたくなる。

今回、それを誤った。

同じPyrefly 1.2.0、同じ5つのroot faultでも、`basic` presetでは2/5、`default` presetでは5/5だった。つまり最初に見えていた差の一部は、**製品差ではなく実行設定の差**だった。

この失敗から得た実務上の結論は単純だ。

> 型チェッカーを比較する前に、version・preset・config・scope・severityを固定する。

## なぜこの失敗は起きるのか

CIではbinary名だけが記録されがちだ。

```text
pyrefly
pyright
mypy
```

しかし実際にblocking authorityとして動くのはbinary名ではなく、次の組み合わせである。

```text
authority =
  tool version
  + preset / mode
  + config
  + project scope
  + runtime environment
  + blocking severity policy
```

Pyrefly公式は、設定のないprojectでは`basic` presetを合成し、`default`や`strict`とはdiagnostic surfaceが異なると説明している。

https://pyrefly.org/en/docs/configuration/

Pyrightも`off` / `basic` / `standard` / `strict`の`typeCheckingMode`を持つ。

https://github.com/microsoft/pyright/blob/main/docs/configuration.md

製品名だけ揃えても、比較条件は揃っていない。

## 実際に何が変わったか

固定fixtureでは次の5 failure classを1件ずつ用意した。

- syntax failure
- incompatible argument type
- incompatible return type
- undefined name
- async misuse

同じPyrefly 1.2.0で観測した結果はこうだった。

| tested mode | detected |
|---|---:|
| no config → basic | 2/5 |
| `basic` | 2/5 |
| `default` | 5/5 |

raw calibration:
https://github.com/KAFKA2306/articles/blob/822be109de61e5915799fcf7d79e6345dff4f6b1/benchmarks/verification-stack-v2/results/controlled/pyrefly-preset-calibration.json

修復後の同じ5 mutantでは、mypy / Pyright / ty / Pyreflyのtested configurationはいずれも5/5だった。

summary:
https://github.com/KAFKA2306/articles/blob/822be109de61e5915799fcf7d79e6345dff4f6b1/benchmarks/verification-stack-v2/results/controlled/summary.json

ここから「4製品は同等」とは言えない。5 mutantしか測っていないからだ。言えるのは、**旧2/5対5/5を製品固有のcoverage差として扱えなかった**ことだけである。

## 壊れた比較

```text
A: 2/5
B: 5/5
↓
Bの方が強い
```

この推論には、AとBが同じpolicy surfaceで走ったという確認が抜けている。

## 改善した比較

比較を次の順序に変える。

1. repoで絶対にblockしたいfailure classをfixture化する
2. clean baselineを保存する
3. version / preset / config / scopeをpinする
4. cleanとmutantを同じexecution contractで走らせる
5. `clean=pass && mutant=block` のときだけcreditを与える
6. correctness survivorだけを速度やmigration costへ進める

これなら「設定が強いだけ」を「製品が強い」と誤読しにくい。

## 読者が持ち帰るべきもの

型チェッカー導入時に比較表を作る前に、CI logへ次を残す。

```text
checker: pyrefly 1.2.0
preset: default
config: pyproject.toml
scope: src + tests
python: 3.12
blocking severity: error
```

この記録がないbenchmarkは、後から再現できても「何を比較したのか」が曖昧になる。

## 証拠の境界

今回の5 mutantはtyping全体のaccuracy benchmarkではない。editor behavior、third-party stubs、incremental analysis、large-repo behaviorも測っていない。

それでも、設定を固定しない比較が危険だという判断には十分だった。なぜなら、**同一binary・同一version・同一fixtureでpresetだけを変えたとき、結果が2/5から5/5へ変わった**からだ。

製品比較は最後でいい。

最初に固定すべきなのは、**その製品に実際どの判定権限を与えたのか**である。