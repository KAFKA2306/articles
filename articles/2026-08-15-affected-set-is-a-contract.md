---
title: "CIを速くする前に、変更ごとに必要なテストを決める"
emoji: "🧭"
type: "tech"
topics: ["monorepo", "ci", "nx", "turborepo", "testing"]
published: false
published_at: 2026-08-17 19:11
---

**テストを減らして速くなったCIを、それだけで「改善」と呼ぶな。**

affected executionは実行対象を減らすほど速くなる。誤って必要なテストを落としても、秒数だけ見れば性能向上だ。そこで先に「`core`変更→`core, ui, web, api`」「`ui`変更→`ui, web`」「`docs`変更→`docs`」の3ケースを固定した。Nxのproject-level affected setは、この3件では **3/3で一致**した。[入力と観測](https://github.com/KAFKA2306/articles/blob/f7368d064d1840a5f66d92563d16deaabb5b3285/benchmarks/verification-stack-v2/results/controlled/workspace.json)

ここからの汎用規律は **「速さを競う前に、省いてはいけない仕事を先に固定せよ」**。CIが仮に30秒速くても、その代償に必要な`api`の検査が欠ければ採用しない。

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

CIで使う比較元と変更後のコミットを一組用意する。共有コード、下流の少ないコード、独立した文書から代表変更を選び、依存関係を見て次のように書く。

```text
change: packages/core/**
must_include: core, ui, web, api
must_exclude: docs
```

候補は同じコミット間の差分で動かし、案件ごとに実行対象を保存する。`must_include` の欠落が一つでもあれば、時間が縮んでも採用を保留する。`must_exclude` が含まれたら、なぜ余分に走ったかを調べる。速度は、比較対象としたプロジェクトやタスクの集合が一致した候補で測る。

## 必須の1件を省いた結果を不合格にする

本文の`core`変更では、`core, ui, web, api`の4プロジェクトが必須だ。もしツールが`core, ui, web`だけを返したら、3件は正しくても`api`のテストを落としている。これは**意図的に作った反例**で、記事で報告したNxの実測3/3とは別の入力である。

```python
required = {"core", "ui", "web", "api"}
observed = {"core", "ui", "web"}  # apiが欠落した反例
missing = required - observed
assert missing == {"api"}
print(sorted(missing))  # ['api']
```

30秒速くなっても、この入力では採用しない。実リポジトリの検証では比較元と変更後のSHA、変更したパス、実際に発火すべきprojectとtask、ツールの出力を同じ表に残す。project集合とbuild task集合は別物なので混ぜない。[固定した3ケースの実測](https://github.com/KAFKA2306/articles/blob/f7368d064d1840a5f66d92563d16deaabb5b3285/benchmarks/verification-stack-v2/results/controlled/workspace.json)

## 証拠の境界

今回の3ケースから、Nxが一般にTurborepoより正確とも、Turborepoが一般に速いとも言えない。real repositoryで同じ差が出ることも証明していない。

変えられるのは評価順序だ。

**CI高速化では、秒数より先に「何を落としてはいけないか」を固定する。速さは、その契約を守った候補同士で比べる。**

## この原則を他の仕事で試す・撤回する条件

ETLの差分更新、検索インデックスの部分再構築、監視対象の絞り込みでも、処理を減らすと時間を短縮できる。**別分野への応用仮説**は「必須対象を先に確定し、抜けのない方式だけで時間を比べる」こと。実証済みなのは今回固定した3ケースに限る。

毎回全件実行するコストが小さく、対象選別器を導入する利益がない場合は、わざわざ複雑な選別を追加しない。別repoで今回の必須集合が守れないと確認されれば、今回の成功を根拠とした採用判断も撤回する。**対象の正しさと実行時間は別々に測る。**
