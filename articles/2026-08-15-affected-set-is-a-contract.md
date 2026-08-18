---
title: "CIが速くなった。必要なテストを消しただけかもしれない"
emoji: "🧭"
type: "tech"
topics: ["monorepo", "ci", "nx", "turborepo", "testing"]
published: true
published_at: 2026-08-17 19:11
---

CIが30秒短くなった。数字だけ見れば成功だ。

でも、その30秒が**「不要な処理を消した時間」ではなく「必要なテストを消した時間」**だったら、最適化ではない。

affected executionは対象を減らすほど速くなる。だから誤判定まで性能改善に見える。

そこで私は、toolを選ぶ前に「この変更なら何を絶対に実行するか」を3ケースだけ固定した。

- `core`変更 → `core`, `ui`, `web`, `api`
- `ui`変更 → `ui`, `web`
- `docs`変更 → `docs`

Nxのproject-level affected setは、この3/3でground truthと一致した。

この記事の結論はNx推奨ではない。**CI時間より先に、落としてはいけない実行対象をfixture化する**という評価順序だ。

## なぜ秒数を最初に見ると危ないのか

```text
変更
  ↓
affected判定を誤る
  ↓
必要なtest/buildを飛ばす
  ↓
CI時間は短くなる
  ↓
greenなので成功に見える
```

速度だけでは、正しく省略したのか、誤って省略したのかを区別できない。

だから先に次をrepository contractにする。

```text
f(change) -> expected projects
```

## 今回の3ケース

| change | expected | Nx observed |
|---|---|---|
| core | core, ui, web, api | core, ui, web, api |
| ui | ui, web | ui, web |
| docs | docs | docs |

raw evidence:
https://github.com/KAFKA2306/articles/blob/f7368d064d1840a5f66d92563d16deaabb5b3285/benchmarks/verification-stack-v2/results/controlled/workspace.json

Nx公式も、affectedはGitでchanged filesを求め、project graphから所属projectとdependent projectを導くと説明している。

https://nx.dev/docs/features/ci-features/affected

## Turborepoと勝敗を付けなかった理由

同じ実験ではTurborepoの`turbo run build --affected --dry=json`も観測した。ただしこちらはbuild task planで、Nxで見たproject集合と同じ出力surfaceではなかった。

https://turborepo.com/docs/crafting-your-repository/constructing-ci

同じ「affected」という言葉でも、次は別物だ。

- changed files
- affected projects
- affected tasks
- task cache
- architecture boundaries

違う対象を同じaccuracy表へ押し込むと、製品ランキングは作れても意思決定は弱くなる。

## 導入順序を逆にする

壊れやすい順序:

```text
1. 速そうなtoolを選ぶ
2. affectedを有効化
3. CIが短くなったので成功
```

改善後:

```text
1. shared/core変更の期待集合を書く
2. leaf変更の期待集合を書く
3. 独立docs/package変更の期待集合を書く
4. candidateの出力を照合する
5. false negativeがない候補だけ残す
6. その後に速度・cache・運用costを測る
```

## 同等なら、最後は小さい構成を選ぶ

correctness、必要機能、運用性、UI/UXが同等まで揃った候補なら、次は少ない方がよい。

- CI command数
- config file数
- dependency数
- custom scriptのLOC / file数
- 二重に存在する判定authority

ただし、これは最後のtie-breakerだ。必要なtestを落として作った「小さいCI」は最適化ではない。

## 自分のrepoで10分で試す

代表変更を3つ選び、各ケースで次を1行ずつ書く。

```text
change: packages/core/**
must_include: core, ui, web, api
must_exclude: docs
```

その後、Nx、Turborepo、独自scriptなど実際に使いたいsurfaceを実行し、期待集合との差を見る。速度計測は一致した候補だけで行う。

## 証拠の境界

今回の3ケースから、Nxが一般にTurborepoより正確とも、Turborepoが一般に速いとも言えない。real repositoryで同じ差が出ることも証明していない。

変えられるのは評価順序だ。

**CI高速化では、秒数より先に「何を落としてはいけないか」を固定する。速さは、その契約を守った候補同士で比べる。**