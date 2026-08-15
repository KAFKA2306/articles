---
title: "CIを速くしたのに、必要なテストまで消えていないか"
emoji: "🧭"
type: "tech"
topics: ["monorepo", "ci", "nx", "turborepo", "testing"]
published: false
---

CI短縮で最初に見るべきなのは秒数ではない。

**変更したとき、本当に実行すべきprojectを落としていないか**である。

affected executionは強力だが、対象集合を間違えると「速くなった」のではなく「必要な検証を飛ばした」だけでもgreenになる。

今回、toolを選ぶ前にrepository側の期待affected setを固定した。

- `core`変更 → `core`, `ui`, `web`, `api`
- `ui`変更 → `ui`, `web`
- `docs`変更 → `docs`

この3ケースをground truthとして、orchestratorの出力を照合した。

## 速さより先に集合を固定する理由

CI時間は観測しやすい。一方、false negativeは見えにくい。

```text
変更
  ↓
affected判定を誤る
  ↓
必要なtest/buildを実行しない
  ↓
CIは速くgreenになる
```

最悪なのは、性能改善として成功に見えることだ。

だから先に次のcontractを作る。

```text
f(change) -> expected projects
```

代表caseが3件でも、速度benchmarkより先に「落としてはいけない対象」を検証できる。

## 今回の観測

Nxの`nx show projects --affected`は、固定した3 caseでproject-level ground truthと一致した。

| change | expected | Nx observed |
|---|---|---|
| core | core, ui, web, api | core, ui, web, api |
| ui | ui, web | ui, web |
| docs | docs | docs |

raw evidence:
https://github.com/KAFKA2306/articles/blob/f7368d064d1840a5f66d92563d16deaabb5b3285/benchmarks/verification-stack-v2/results/controlled/workspace.json

Nx公式はaffected計算を、Gitで変更fileを特定し、project graphから影響projectを求める仕組みとして説明している。

https://nx.dev/docs/features/ci-features/affected

一方、今回Turborepoで観測した`turbo run build --affected --dry=json`はbuild task planだった。project集合そのものとtask planを同じaccuracy metricへ押し込むと比較を壊す。

https://turborepo.com/docs/crafting-your-repository/constructing-ci

## ここで製品ランキングをしない

同じartifactにはelapsed timeも残っている。しかし「NxよりTurborepoが何倍速い」のようなheadlineには使わなかった。

理由は簡単だ。

- 観測したcommandの責務が違う
- paired timingではない
- 正しさを満たしていない候補の速さは意味がない

速度は、**同じ責務を正しく満たしたsurvivor同士**で初めて比較する。

## 壊れた導入順序

```text
1. fastest toolを選ぶ
2. affectedを有効化
3. CIが短くなったので成功
```

この順序では、何を落としてはいけないかが未定義である。

## 改善した導入順序

```text
1. dependency graphから代表変更caseを選ぶ
2. expected affected setをrepoに固定する
3. candidate toolの出力を照合する
4. false negativeがない候補だけ残す
5. その後に速度・cache・運用costを測る
```

## 読者が最初に区別する5つ

monorepo高速化では、次を同じものとして扱わない。

- changed files
- affected projects
- affected tasks
- task cache
- architecture boundaries

必要なのがbuild/test taskの絞り込みだけなら、project-level architecture authorityまで追加する必要はない。逆にimpact analysisを人間の判断にも使うなら、project集合を直接観測できるsurfaceが重要になる。

## 最小の再現方法

自分のrepoで3ケース作ればよい。

1. shared/core packageを変更する
2. leafに近いpackageを変更する
3. 独立package/docsを変更する

各ケースで「絶対に含む」「絶対に含まない」projectを先に書く。その後でNx、Turborepo、独自scriptなど候補の出力を照合する。

## 証拠の境界

今回のfixtureだけからNxが一般にTurborepoより正確とも、Turborepoが一般に速いとも言えない。real repositoryで同じ差が再現することも証明していない。

ただし、CI高速化の評価順序は変えられる。

**秒数を測る前に、実行対象集合をrepositoryのcontractとして固定する。**

CIが速くなったとき、「必要なものを落とさず速くなった」と言えるようにするためだ。