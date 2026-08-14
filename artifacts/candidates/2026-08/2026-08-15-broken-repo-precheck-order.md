<!-- pipeline_meta: {"idea_source":"public-github-engineering","idea_only":true,"raw_private_content_persisted":false,"topic":{"title":"2026年の品質toolは結局どれを選ぶ？ 壊れたrepoで実測し、Nx/Turborepoまで公式設計を比較した","audience":"GitHub Actions、AI coding agent、monorepo/複数repositoryを運用する開発者・Tech Lead・Platform Engineer","central_question":"2026年のPython/TypeScript開発で、個別checkerからmonorepo orchestrationまで含めて何を標準化すべきか","surprising_finding":"Ruff 1,076件とPyrefly 723件は独立した1,799欠陥ではなく、Pyreflyの723件中508件がparse errorでRuffの508 invalid-syntaxと同じ前段failureに依存していた。さらに公式設計を追うと、checker選定だけではworkspace規模のaffected/cache/architecture問題を解けず、analysis authorityとtask/project graph authorityを分ける必要があった","initial_hypothesis":"高速な最新checkerを横並びで積めば、広く速いprecheck stackになる","hypothesis_update":"professionalな標準はone concern, one authority。PythonはRuff+Pyrefly+boundaryだけPydantic、TypeScriptはBiome formatter+Oxlint+tsc+boundaryだけZod、prekは交換可能なcommit trigger。monorepoならさらにNxまたはTurborepoを上位に1つだけ置き、Nxはgovernance、Turborepoはlean JS/TS executionを主目的に選ぶ","stakes":"tool数を増やすだけではdiagnostic noise、CI待ち、二重ルール、cache不整合、architecture driftが増える。役割とgraphを分離すればAI agentを含む変更速度を上げながらcode healthを維持できる","story_type":"architecture-after-falsified-ranking","reader_before":"Ruff、Pyrefly、Biome、Oxlint、tsc、Pydantic、Zod、prek、Nx、Turborepoの名前は知っているが、結局どれを標準化し、どれを重複させず、どの規模で導入すべきか判断できない","reader_after":"役割別の第一候補、stable/experimental境界、single-repo/monorepoの選択基準を使って自分のrepositoryにquality architectureを設計できる","design_philosophy":"checkerのブランドではなくauthority mapを設計する。同じ責務を二重blockingせず、前段failureほど早く安く返し、workspace規模ではproject/task graphを使ってaffected実行とcacheを制御する","why_this_article":"実際に壊れていた公開repositoryの固定commitでRuff/Pyrefly/ty/pre-commit/prekを実測し、raw diagnosticsと生成patchまで確認したうえで、Google Research、Ruff、Pyrefly、Astral、Pydantic、Biome、Oxc、TypeScript、Zod、prek、Nx、Turborepo/Vercelの公式一次情報だけで2026年8月の採用判断へ落としている","proof_of_value":"KAFKA2306/DeepCode@088059855d2c9187c51d674db02a06f70c37f087、GitHub Actions run 31812751114、Ruff 1,076 findings、Pyrefly 723 findings、そのうちparse-error 508、pre-commit/prek生成patch SHA-256一致。公式レビューはartifacts/reports/2026-08/precheck-bad-repo/2026-08-15-official-toolchain-review.mdに固定","desired_reader_action":"自分のrepoでformatter/linter/type/runtime-contract/workspace-orchestratorのauthority mapを作り、monorepoでなければNx/Turboを入れず、monorepoならgovernanceかlean executionかで1つ選ぶ","non_goal":"単発速度で普遍的なtoolランキングを作らない。未実測toolを実測済みと扱わない。既存Pyright/ESLint/monorepo基盤を根拠なく一括置換しない"},"public_evidence":["https://github.com/KAFKA2306/articles/pull/115","https://github.com/KAFKA2306/articles/actions/runs/31812751114","https://github.com/KAFKA2306/DeepCode/commit/088059855d2c9187c51d674db02a06f70c37f087","https://research.google/pubs/tricorder-building-a-program-analysis-ecosystem/","https://research.google/pubs/lessons-from-building-static-analysis-tools-at-google/","https://docs.astral.sh/ruff/","https://pyrefly.org/blog/v1.0/","https://docs.astral.sh/ty/","https://docs.pydantic.dev/2.10/concepts/validation_decorator/","https://prek.j178.dev/compatibility/","https://biomejs.dev/formatter/","https://biomejs.dev/linter/","https://oxc.rs/docs/guide/usage/linter/type-aware.html","https://oxc.rs/docs/guide/usage/linter/config-file-reference","https://www.typescriptlang.org/tsconfig/noEmit.html","https://zod.dev/basics","https://nx.dev/docs/features/explore-graph","https://nx.dev/docs/features/ci-features/affected","https://nx.dev/docs/features/enforce-module-boundaries","https://turborepo.dev/docs/core-concepts/package-and-task-graph","https://turborepo.dev/docs/crafting-your-repository/caching","https://turborepo.dev/docs/reference/boundaries","https://vercel.com/docs/monorepos/turborepo"]} -->

# 2026年の品質toolは結局どれを選ぶ？ 壊れたrepoで実測し、Nx/Turborepoまで公式設計を比較した

「RuffとPyreflyを入れるべきか」「BiomeとOxlintは競合しないか」「`tsc --noEmit`はまだ必要か」「pre-commitをprekへ替えるべきか」。

さらにmonorepoなら、TurborepoとNxまで候補に入ってきます。

2026年の開発toolはかなり速くなりました。しかし、速いtoolを全部入れるだけではprofessionalな品質systemにはなりません。

Tech LeadやPlatform Engineerが本当に知りたいのは、**結局どれを標準にするのか**です。

先に結論を書きます。

## 結論：2026年8月時点の第一候補

| concern | 第一候補 | 判断 |
|---|---|---|
| Python format / lint | **Ruff** | greenfieldなら標準候補 |
| Python static type | **Pyrefly** | blocking authority候補 |
| Python type challenger | **ty** | Beta。shadow評価向き |
| Python runtime contract | **Pydantic** | trust boundaryだけ |
| JS/TS format | **Biome formatter** | formatter authority |
| JS/TS lint | **Oxlint** | modern TSなら第一候補 |
| TypeScript type | **`tsc --noEmit`** | 当面のcompiler authority |
| TS runtime contract | **Zod** | trust boundaryだけ |
| local Git hooks | **prek** | 強い置換候補。ただしpolicy本体ではない |
| lean JS/TS monorepo | **Turborepo** | task graph/cacheを薄く導入したいとき |
| governance-heavy monorepo | **Nx** | project graph/affected/architecture policy重視 |

つまり、私ならこう置きます。

```text
single repo
  ├─ Python: Ruff → Pyrefly → Pydantic at runtime boundaries
  ├─ TS:     Biome(format) → Oxlint → tsc --noEmit → Zod at runtime boundaries
  └─ commit: prek

monorepo
  ├─ governance / heterogeneous workspace → Nx
  └─ lean JS/TS task execution             → Turborepo
          ↓
     上記language authoritiesを実行
```

**NxとTurborepoは同じworkspaceへ両方入れません。**

また、小さなsingle-project repoへ「強そうだから」という理由でNx/Turborepoを追加することもしません。

この結論に至った理由は、壊れたrepoでの実測と、各toolの公式設計を合わせて見ると分かります。

## 最初は「速いcheckerを全部積めば強い」と考えた

固定した対象は `KAFKA2306/DeepCode` の次のcommitです。

```text
088059855d2c9187c51d674db02a06f70c37f087
```

実験run:
https://github.com/KAFKA2306/articles/actions/runs/31812751114

最初の結果は派手でした。

```text
Ruff      1,076 findings
Pyrefly     723 findings
```

Ruffのscan観測は99 ms、Pyreflyは361 msでした。

一見すると「1秒未満で1,799件の問題を見つけた」と言いたくなります。

しかしraw diagnosticsを分類すると違いました。

| Ruff | count |
|---|---:|
| `invalid-syntax` | **508** |
| `UP006` | 147 |
| `BLE001` | 143 |
| `I001` | 44 |
| `RUF010` | 42 |

| Pyrefly | count |
|---|---:|
| `parse-error` | **508** |
| `unknown-name` | 108 |
| `missing-import` | 86 |
| `invalid-syntax` | 12 |
| `unexpected-keyword` | 9 |

Ruffの`invalid-syntax`とPyreflyの`parse-error`が、どちらも508件でした。

したがって、

```text
1,076 + 723 = 1,799 independent defects
```

ではありません。

**同じ前段failureが複数の解析器へ伝播していました。**

ここで「どのtoolが一番多く見つけるか」という見方を捨てました。

## Googleのprofessional static analysisも「件数ランキング」ではない

Google ResearchのTricorderは、static analyzerを単体で競わせる話ではなく、複数解析を大規模codebaseとdeveloper workflowへどう統合するかを扱っています。

その後のGoogleのproduction static-analysis報告でも、重要なのは実際に日常利用され、engineerがcheck-in前に問題を修正するsystemになっていることです。

- https://research.google/pubs/tricorder-building-a-program-analysis-ecosystem/
- https://research.google/pubs/lessons-from-building-static-analysis-tools-at-google/

さらにstatic-analysis toolが使われない理由を調べた研究では、false positiveやwarningの提示方法自体が障壁になります。

- https://research.google/pubs/why-dont-software-developers-use-static-analysis-tools-to-find-bugs/

つまりprofessionalな評価軸は、少なくとも次です。

```text
semantic authority      最後に誰を信じるか
signal density          出力が独立してactionableか
feedback latency        context switch前に返るか
trust boundary          runtime inputをどこで止めるか
graph awareness         変更影響・task依存を理解できるか
migration cost          運用tool debtを減らせるか
stability boundary      stable / beta / experimentalを区別できるか
```

この軸で見ると、toolの役割が整理できます。

## Python：Ruff + Pyrefly + Pydantic

### Ruff — format/lintの第一候補

Ruff公式は、linterをFlake8と多数plugin、isort、pyupgrade、autoflake等の置換として位置づけ、formatterも同じCLIへ統合しています。現在900超のfirst-party lint rulesを持ちます。

- https://docs.astral.sh/ruff/
- https://docs.astral.sh/ruff/linter/
- https://docs.astral.sh/ruff/formatter/

強さは単純な速度だけではありません。

```text
Black
isort
Flake8
pyupgrade
...
```

という複数authorityを減らせることが大きい。

**greenfield PythonならRuffをformat/lint authorityにする**、でよいと判断します。

### Pyrefly — blocking type authority

Pyreflyは2026年5月にstable v1へ到達し、公式にproduction-readyとしています。

https://pyrefly.org/blog/v1.0/

今回のbroken repoでは723件のうち508件がparse errorだったため、723をそのまま「型欠陥検出力」とは評価しません。

それでもproductionのblocking type authorityを今選ぶなら、stable境界が明確なPyreflyを第一候補に置きます。

### ty — 捨てない。challengerとして残す

今回の単発観測では、ty 0.0.71は264 ms、Pyrefly 1.2.0は361 msでした。

Astralのtyはfine-grained incremental analysisを中心設計にし、editor feedbackで特に強い方向を狙っています。

- https://docs.astral.sh/ty/
- https://astral.sh/blog/ty

一方、公式には現在もBetaです。Astral自身はmotivated production usersへ推奨していますが、Stableは今後のmilestoneです。

だから現時点では、

```text
blocking CI → Pyrefly
shadow / editor evaluation → ty
```

から始めます。

両方を永久にblockingするのはauthority duplicationです。

### Pydantic — linterではなくruntime boundary

Pydanticはstatic checkerの追加枠ではありません。

HTTP、JSON、CSV、environment、AI outputなど、**code外から来る実値**を検証する層です。

公式の`validate_call` documentationもruntime validationにはcostがあり、strongly typed languageの代替ではないと説明しています。

https://docs.pydantic.dev/2.10/concepts/validation_decorator/

したがって、

```text
external / untrusted data
        ↓
     Pydantic
        ↓
validated application object
```

のboundaryだけに置きます。

## TypeScript：Biome formatter + Oxlint + tsc + Zod

### Biome — formatter authorityとして採用

Biome formatterは意図的にoptionを絞り、style debateを増やさないphilosophyを明示しています。

https://biomejs.dev/formatter/

Biome自身のlinterも弱くありません。現在の公式docsでは518 rulesを持ち、monorepoもv2からout-of-the-box supportがあります。

- https://biomejs.dev/linter/
- https://biomejs.dev/guides/big-projects/

それでも今回の標準ではBiomeをformatterに絞ります。

理由は**one concern, one authority**です。

```text
Biome = format
Oxlint = lint
```

とした方が組織標準として説明しやすい。

### Oxlint — dedicated lintの第一候補

Oxlintのtype-aware lintingは2026年7月にstable化し、現在59/61のtypescript-eslint type-aware rulesをサポートしています。

- https://oxc.rs/blog/2026-07-22-type-aware-linting-stable.html
- https://oxc.rs/docs/guide/usage/linter/type-aware.html

ただし重要な制約があります。

- TypeScript 7+が必要
- legacy `tsconfig` optionにはmigrationが必要
- very large codebaseではmemory注意

したがってgreenfieldには強く、legacyには先にcompatibility auditが必要です。

### `tsc --noEmit` — まだtype authorityから外さない

Oxlint公式guideは、`--type-aware --type-check`でTypeScript compiler diagnosticsもまとめ、別の`tsc --noEmit`を置換できる例を示しています。

しかし同じ現在のconfig referenceでは、`typeCheck`は**experimental**です。

https://oxc.rs/docs/guide/usage/linter/config-file-reference

TypeScript公式の`noEmit`は、compilerをsource-code type checkerとして使う正式な用途です。

https://www.typescriptlang.org/tsconfig/noEmit.html

したがって2026年8月の保守的な判断は、

```text
Oxlint          lint authority
TypeScript tsc  type authority
```

です。

Oxlint type-checkがexperimentalを外れた時点で、重複analysisを削れるか再評価します。

### Zod — TypeScript側のruntime boundary

Zodは`.parse()` / `.safeParse()`でruntime inputをvalidateし、同じschemaからstatic typeをinferできます。

https://zod.dev/basics

Pydanticと同じく、repository-wide lint件数へ加算するものではありません。

## prek — 強い。ただし一番上には置かない

今回もっとも直接比較できたのがpre-commitとprekです。

同じ`.pre-commit-config.yaml`を使いました。

```text
pre-commit 4.6.2
  install 1,534 ms
  scan    8,765 ms

prek 0.4.11
  install   293 ms
  scan    2,326 ms
```

別runnerなので「常に3.93倍速い」とは主張しません。

重要なのは、実行後patchがbyte-identicalだったことです。

```text
30275602cf6b35644199d3a7fe949c038a10eaa9e6685074de4f7c8d62b36bf1
```

prek公式も既存`.pre-commit-config.yaml`の実用的drop-in replacementを目指し、0.4.5でpre-commitのlanguage coverage parityを完了したとしています。

- https://prek.j178.dev/compatibility/
- https://prek.j178.dev/changelog/

ただしstrict upstream portabilityが必要なら、公式もYAMLを維持しprek-only extensionを避けるよう説明しています。

だからprekは、

```text
quality policy = repository commands/config/CI
prek           = local trigger
```

とします。

hook runnerを変えただけで品質定義が変わってはいけません。

## ここまでではまだ視座が低い。monorepoでは「何を実行するか」自体を制御する

Ruff/Oxlint/tscは、渡されたcodeを検査します。

しかし大きなworkspaceでは次の問題が出ます。

```text
この変更で、どのpackageが影響を受ける？
どのtestを走らせれば十分？
何をcacheして再利用できる？
package Aはpackage Bへ依存してよい？
```

これはlinterの責任ではありません。

ここでNx/Turborepoという**workspace graph layer**が必要になります。

## Nx — 「最強monorepo runner」ではなくgovernance platformとして見る

NxはProject GraphとTask Graphを明示的に持ちます。

Project Graphはproject dependencyを、Task Graphは実行taskと依存順を表します。

https://nx.dev/docs/features/explore-graph

`nx affected`は変更から影響を受ける最小project集合を求め、そのprojectだけtaskを実行します。

https://nx.dev/docs/features/ci-features/affected

cacheもtask input/outputをhashし、local/remoteで再利用できます。

https://nx.dev/docs/features/cache-task-results

さらにproject tagsを使ったarchitecture boundaryがあります。

https://nx.dev/docs/features/enforce-module-boundaries

このためNxは、単に`lint`を高速に起動するtoolではなく、

```text
project graph
  ↓
affected scope
  ↓
task graph
  ↓
cache / distribution
  ↓
architecture policy
```

を持つ点が強い。

### ただしNx + Oxlintには見落としやすい境界がある

Nxの公式module-boundary docsを見ると、JavaScript/TypeScript向けのopen-source enforcementは`@nx/enforce-module-boundaries`という**ESLint rule**です。

language-agnosticなgraph-level ConformanceはPowerpack/Enterprise側です。

つまり、

```text
ESLintを完全削除
Oxlintへ全面移行
Nxのmodule boundariesも当然そのまま使える
```

とは限りません。

ここはprofessionalなmigrationで必ずinventoryすべき点です。

無料OSS構成でNx boundary enforcementを重視するなら、architecture rule専用に最小ESLintを残す判断もあり得ます。EnterpriseならConformanceを評価できます。

**tool統一のためにarchitecture policyを落とすのは本末転倒です。**

## Turborepo — leanなtask graph/cache layerとして強い

TurborepoもPackage GraphからTask Graphを作り、DAGとしてtask依存を理解します。

https://turborepo.dev/docs/core-concepts/package-and-task-graph

deterministic taskのoutput/logをcacheし、remote cacheでteam/CI間に共有できます。

https://turborepo.dev/docs/crafting-your-repository/caching

VercelもTurborepoをJavaScript/TypeScript codebase向けhigh-performance build systemとして位置づけています。

https://vercel.com/docs/monorepos/turborepo

この薄さは長所です。

「既存package scriptsを中心に、task graphとcacheだけ強くしたい」ならTurborepoは非常に自然です。

### Turborepo Boundariesはまだ同じ重さで評価しない

Turborepoにも`turbo boundaries`があり、

- package外file import
- undeclared workspace dependency
- tag-based dependency rule

を検査できます。

ただし現行公式referenceは**Experimental**と明記しています。

https://turborepo.dev/docs/reference/boundaries

したがって、Nxの成熟したgovernance機能と同列には置きません。

## NxかTurborepoか

ここは「どちらが総合点で上か」ではなく、problem statementで選べます。

### Turborepoを選ぶ

```text
JS/TS中心
package.json scriptsを活かしたい
設定を薄くしたい
task DAG + cache + Vercel integrationが主目的
architecture governanceは別途でよい
```

### Nxを選ぶ

```text
workspaceが大きい
affected scopeをproject graphから厳密に扱いたい
architecture boundaryをsystemとして管理したい
複数project/technologyを同じgraphで扱いたい
CI orchestration自体をplatform化したい
```

### どちらも入れない

```text
single project
CIが十分短い
project graphを持つほどの依存構造がない
cache/orchestration overheadの方が大きい
```

これも重要な選択です。

## 最終的な「2026 quality control plane」

個別tool listではなく、こう見ると整理できます。

```text
Organization / repository policy
              │
              ▼
Workspace graph authority (必要な場合だけ)
  Nx OR Turborepo
              │
              ▼
Language authorities
  Python
    Ruff → Pyrefly → Pydantic at trust boundaries

  TypeScript
    Biome(format) → Oxlint → tsc --noEmit → Zod at trust boundaries
              │
              ▼
Developer trigger
  prek
              │
              ▼
PR CI / integration / E2E
```

ここで大事なのは、**orchestratorとcheckerを混同しないこと**です。

- Ruff/Oxlintは「codeの何が悪いか」を見る
- Pyrefly/tscは「programの型が成立するか」を見る
- Pydantic/Zodは「runtime dataがcontractを満たすか」を見る
- prekは「commit前に何を起動するか」を見る
- Nx/Turborepoは「workspaceで何を、どの順序・範囲・cacheで実行するか」を見る

これらは競合ではありません。

同じ責務へ2つ置いたときに初めて競合になります。

## 今回の実験で一番変わった考え

最初は、

```text
速いtoolを全部入れる
        ↓
たくさんdiagnosticが出る
        ↓
品質が上がる
```

と考えていました。

今はこうです。

```text
one concern
  ↓
one authority
  ↓
最も早い有効feedback point
  ↓
workspaceならgraphでaffectedを絞る
  ↓
trust boundaryでruntime validation
  ↓
full CI / integrationでsystem correctness
```

Ruff 508件とPyrefly 508件の重複parse failureは、小さな実例でした。

**toolが増えるほど品質が上がるのではなく、failure domainごとにauthorityを1つ決め、上位graphが必要な仕事だけを流すときに品質systemになる。**

だから2026年8月の私の答えは、単なる「Ruffが最強」「Nxが最強」ではありません。

> Pythonなら **Ruff + Pyrefly + boundaryだけPydantic**。TypeScriptなら **Biome formatter + Oxlint + `tsc --noEmit` + boundaryだけZod**。local hookは **prek**。monorepoでは **governance重視ならNx、leanなJS/TS executionならTurborepo**。

ここまでは、実repoの直接測定と各projectの公式仕様から言える範囲です。

未実証範囲も残っています。DeepCodeで直接測ったのはRuff/Pyrefly/ty/pre-commit/prekで、Pydantic/Biome/Oxlint/tsc/Zod/Nx/Turborepoは今回のfixtureではまだ公式仕様レビューです。

次は状態の悪いTypeScript monorepoを固定し、`Biome → Oxlint → tsc`と`Nx/Turborepo`のaffected/cache効果を同じ方法で測ります。