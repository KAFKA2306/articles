---
title: "速いCIより、正しいaffected setを先に測る"
emoji: "🧭"
type: "tech"
topics: ["monorepo", "ci", "nx", "turborepo", "testing"]
published: false
---

モノレポのCI改善では、最初に「何秒短くなったか」を見たくなる。しかし、affected executionで先に決めるべきなのは速度ではない。**変更したprojectから、実行対象に含めるべきproject集合を正しく導けるか**である。

この順序を逆にすると、速いCIが単に必要な検証を飛ばしているだけでも成功に見える。

## 先にground truthを固定した

今回のfixtureは4つの依存projectと、独立したdocs projectからなる。比較前に、変更点ごとの期待affected setを固定した。

- `core`変更 → `core`, `ui`, `web`, `api`
- `ui`変更 → `ui`, `web`
- `docs`変更 → `docs`

これはbenchmark結果から作った期待値ではない。fixtureの依存関係から事前に定義したground truthである。1 mutant = 1 root fault、raw diagnostics != defect count、correctness before speedという既存protocolも維持した。

再現用fixtureとraw evidenceは `benchmarks/verification-stack-v2/` に固定している。

- protocol: https://github.com/KAFKA2306/articles/blob/f7368d064d1840a5f66d92563d16deaabb5b3285/benchmarks/verification-stack-v2/PROTOCOL.md
- ground truth: https://github.com/KAFKA2306/articles/blob/f7368d064d1840a5f66d92563d16deaabb5b3285/benchmarks/verification-stack-v2/workspace/ground-truth.json
- raw workspace result: https://github.com/KAFKA2306/articles/blob/f7368d064d1840a5f66d92563d16deaabb5b3285/benchmarks/verification-stack-v2/results/controlled/workspace.json

## 同じ「affected」でも、観測対象は同じとは限らない

controlled runでは、Nxの `nx show projects --affected` は3変更すべてで事前ground truthと一致した。

| change | expected | Nx observed |
| --- | --- | --- |
| core | core, ui, web, api | core, ui, web, api |
| ui | ui, web | ui, web |
| docs | docs | docs |

一方、Turborepoの `turbo run build --affected --dry=json` は `core` 変更では期待した4 build packageを含んだが、`ui` 変更では `core, ui, web` を返し、事前ground truth `ui, web` より `core` が1つ多かった。

ここで「Nxの方が優秀」と結論してはいけない。両コマンドは同じauthority surfaceではないからだ。

Nx公式はaffected計算について、Gitで変更fileを特定し、project graphで所属projectと依存projectを導く、と説明している。

https://nx.dev/docs/features/ci-features/affected

Nxはproject graphとtask graphを別概念として公開している。`nx show projects --affected` はproject集合を観測するsurfaceである。

https://nx.dev/docs/features/explore-graph

対して今回のTurborepo観測は `run build --affected --dry=json` の**task plan**である。つまり「affected project集合そのもの」と「その変更から実際にbuildするtask集合」を、名前が似ているからといって同じmetricにしてはいけない。

TurborepoのCI documentation:

https://turborepo.com/docs/crafting-your-repository/constructing-ci

## 速度比較をheadlineにしなかった理由

同じcontrolled artifactにはelapsed timeも残っている。たとえば `core` 変更の単発観測ではNx commandは約518 ms、Turborepo dry-runは約63 msだった。

しかし、この数字を「TurborepoはNxより8倍速い」とは書けない。

理由は3つある。

1. 実行したcommandの責務が違う。
2. これは同一runnerでのpaired timingではない。
3. project-set correctnessとtask-plan生成時間を混ぜると、速さがauthorityの正しさを上書きする。

この実験protocolではcorrectnessが速度より先である。速度は、同じ責務を満たしたsurvivor同士で初めて意思決定材料になる。

## 3つの物語を同じ証拠で反証した

### 1. 「NxはTurborepoより正確だ」

棄却する。

今回、Nxではproject affected setを、Turborepoではbuild task planを観測した。異なるauthority surfaceの出力差を製品accuracyへ一般化できない。

### 2. 「Turborepoの方が速いからCIにはTurborepoを選ぶ」

棄却する。

単発かつ異なるcommandのelapsed timeであり、same-runner paired timing条件を満たさない。さらに速度はground-truth correctnessの代替にならない。

### 3. 「affected setを先に契約として固定し、orchestratorの出力をその契約に照合する」

これだけが残る。

モノレポtoolを選ぶ前に、repository側が「この変更なら何が影響を受けるべきか」を少数の代表caseで宣言できる。toolはその契約を満たす実装候補であり、tool名そのものがground truthではない。

## NxとTurborepoのauthorityを分ける

Nx公式はproject graphをworkspace projectと依存関係のgraphとして扱い、affected commandはGit historyとproject graphから影響projectを求める。

https://nx.dev/docs/features/ci-features/affected

そのため、**project/affected graphそのものを意思決定に使いたい**場合、Nxには明示的なauthority surfaceがある。

一方、Turborepoを採用する理由は「Nxより軽いから」ではなく、既存JS/TS workspaceで必要なのがtask graph、cache、affected task executionである場合に置くべきだ。project-level architectural boundaryまで必要なら、それは別のcapabilityとして検証する。

この分離は「全部入りtoolを選べ」という話ではない。逆である。**足りないauthorityだけを追加する**ための分離だ。

## 読者が先に決めるべきもの

新しいorchestratorを導入する前に、最低でも次を区別する。

- changed filesを知りたいのか
- affected projectsを知りたいのか
- 実行すべきtasksを知りたいのか
- task結果をcacheしたいのか
- architecture boundaryを強制したいのか

これらは同じ「monorepo高速化」ではない。

特にCI削減では、`f(change) -> expected projects` を数caseだけでもfixture化すると、速度benchmarkより先にfalse negativeと不要なover-runを検出できる。

## 今回、証明していないこと

このfixtureだけから次は言えない。

- Nxが一般にTurborepoより正確である
- Turborepoが一般にNxより速い
- どちらか一方がすべてのmonorepoに適する
- real repositoryで同じaffected差が再現する
- task cache hit率やremote cache性能の優劣

real repository観測はexternal validityであり、controlled ground truthの代わりにはしない。

## 何が起きれば判断を反転するか

Turborepo側で、今回と同じ**project affected set**を直接かつ同じ意味論で取得する公式surfaceを固定し、それが3 caseすべてでground truthと一致するなら、「project affected authorityのためにNxが必要」という判断は弱くなる。

逆に、必要なのがbuild/test taskの選択とcacheだけで、project-level impactやarchitecture boundaryを意思決定に使わないrepositoryなら、Nxを追加する理由も弱い。

重要なのはブランドではない。

**CIを速くする前に、「何を実行すべきか」をrepository自身の契約として固定する。orchestratorはその契約に従う側である。**
