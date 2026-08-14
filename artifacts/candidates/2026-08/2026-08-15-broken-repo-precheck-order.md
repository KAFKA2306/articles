<!-- pipeline_meta: {"idea_source":"public-github-engineering","idea_only":true,"raw_private_content_persisted":false,"topic":{"title":"1,799件見つかった。でも1,799件の問題ではなかった――Ruff/PyreflyからNxまで、2026年の品質基盤を組み直す","audience":"GitHub Actions、AI coding agent、monorepo/複数repositoryを運用する開発者・Tech Lead・Platform Engineer","central_question":"最新の高速checkerを増やせば品質基盤は強くなるのか。それとも、各層のauthorityとdiagnostic依存関係を設計する方が重要なのか","surprising_finding":"Ruff 1,076 findingsとPyrefly 723 findingsは独立した1,799欠陥ではなかった。Pyreflyの723件中508件はparse-errorで、Ruffの508 invalid-syntaxと同じ前段failureに依存していた","initial_hypothesis":"Ruff、Pyrefly、tyなど高速checkerを横並びで増やせば、短時間で広く独立した故障面を得られる","hypothesis_update":"quality stackの強さはtool数ではなく、one concern / one authority、root failureから下流diagnosticへの依存関係、feedback latency、runtime trust boundary、workspace graphの設計で決まる","stakes":"AI agentやCIが大量diagnosticを返す環境では、件数を品質指標にすると修正順序を誤り、二重rule・CI待ち・architecture driftを増やす","story_type":"falsified-ranking-premise","reader_before":"Ruff、Pyrefly、Biome、Oxlint、tsc、Pydantic、Zod、prek、Nx、Turborepoの名前は知っているが、どれを標準化し、どの責務を誰に持たせるべきか判断できない","reader_after":"Python/TypeScript/monorepoの各層で第一候補とauthorityを決め、未実証・Beta・Experimentalを区別しながら自分の品質基盤を設計できる","design_philosophy":"最強toolを集めない。各責務に一つのauthorityを置き、前段failureほど早く安く返し、runtime validationはtrust boundaryだけ、workspace orchestrationはgraph問題があるときだけ導入する","why_this_article":"実際に壊れていた公開repositoryの固定commitへRuff/Pyrefly/ty/pre-commit/prekを実行し、raw diagnosticsと生成patchを比較した。その結果をGoogle Researchと各toolの公式仕様で再解釈している","proof_of_value":"KAFKA2306/DeepCode@088059855d2c9187c51d674db02a06f70c37f087、GitHub Actions run 31812751114、Ruff 1,076 findings、Pyrefly 723 findings、双方の最大syntax系category 508、pre-commit/prek生成patch SHA-256一致","desired_reader_action":"自分のrepoでformatter/linter/type/runtime-contract/workspace-orchestratorのauthority mapを作り、重複authorityとroot failure由来のdiagnostic noiseを減らす","non_goal":"単発速度から普遍的なtoolランキングを作らない。未実測のPydantic/Biome/Oxlint/tsc/Zod/Nx/Turborepoを実測済みとは扱わない。既存Pyright/ESLint/monorepo基盤を根拠なく置換しない"},"public_evidence":["https://github.com/KAFKA2306/articles/pull/115","https://github.com/KAFKA2306/articles/actions/runs/31812751114","https://github.com/KAFKA2306/DeepCode/commit/088059855d2c9187c51d674db02a06f70c37f087","https://research.google/pubs/tricorder-building-a-program-analysis-ecosystem/","https://research.google/pubs/lessons-from-building-static-analysis-tools-at-google/","https://docs.astral.sh/ruff/","https://pyrefly.org/blog/v1.0/","https://docs.astral.sh/ty/","https://docs.pydantic.dev/2.10/concepts/validation_decorator/","https://prek.j178.dev/compatibility/","https://biomejs.dev/formatter/","https://oxc.rs/docs/guide/usage/linter/type-aware.html","https://oxc.rs/docs/guide/usage/linter/config-file-reference","https://www.typescriptlang.org/tsconfig/noEmit.html","https://zod.dev/basics","https://nx.dev/docs/features/ci-features/affected","https://nx.dev/docs/features/enforce-module-boundaries","https://turborepo.dev/docs/core-concepts/package-and-task-graph","https://turborepo.dev/docs/crafting-your-repository/caching","https://turborepo.dev/docs/reference/boundaries"]} -->

# 1,799件見つかった。でも1,799件の問題ではなかった――Ruff/PyreflyからNxまで、2026年の品質基盤を組み直す

*Ruff / Pyrefly / Pydantic / Biome / Oxlint / tsc / Zod / prek / Nx / Turborepo。名前を並べるのではなく、壊れたrepositoryの実測から「誰に何を任せるか」を決め直した。*

最初は、単純に考えていました。

```text
速いcheckerを増やす
        ↓
より多くの問題が見つかる
        ↓
品質基盤が強くなる
```

そこで、実際に状態の悪かった公開repositoryへ2026年のprecheck候補を当てました。

最初の数字は派手でした。

```text
Ruff      1,076 findings
Pyrefly     723 findings
```

合計1,799件。

しかもscan部分はRuff 99 ms、Pyrefly 361 msでした。

「1秒未満で1,799件の問題を見つけた」と書けば、強そうに見えます。

でもraw diagnosticsを分類した瞬間、その解釈は崩れました。

```text
Ruff     invalid-syntax  508
Pyrefly  parse-error     508
```

Pyreflyの723件のうち、508件はparse errorでした。

**新しいtype checkerが独立した問題を723件追加発見したわけではありません。同じ壊れた構文が、後段の解析器へ伝播していました。**

この508件が、今回いちばん重要な数字です。

## 実験したのは「きれいなbenchmark repo」ではない

対象は `KAFKA2306/DeepCode` の固定commitです。

```text
088059855d2c9187c51d674db02a06f70c37f087
```

実験run:
https://github.com/KAFKA2306/articles/actions/runs/31812751114

各toolは別のGitHub Actions jobで実行し、version、install time、scan time、exit code、raw diagnostics、working-tree diffを保存しました。

| tool | version | scan observation | output |
|---|---:|---:|---:|
| Ruff | 0.16.3 | 99 ms | 1,076 findings |
| ty | 0.0.71 | 264 ms | 952 concise lines |
| Pyrefly | 1.2.0 | 361 ms | 723 findings |
| prek | 0.4.11 | 2,326 ms | existing hook config, exit 1 |
| pre-commit | 4.6.2 | 8,765 ms | same hook config, exit 1 |

この時間は別runner VMでの単発観測なので、普遍的な速度ランキングには使いません。

見るべきだったのは「何msだったか」より、**何がroot failureで、何がその派生diagnosticだったか**でした。

Ruffの上位categoryはこうでした。

| category | count |
|---|---:|
| `invalid-syntax` | **508** |
| `UP006` | 147 |
| `BLE001` | 143 |
| `I001` | 44 |
| `RUF010` | 42 |

Pyreflyはこうです。

| category | count |
|---|---:|
| `parse-error` | **508** |
| `unknown-name` | 108 |
| `missing-import` | 86 |
| `invalid-syntax` | 12 |
| `unexpected-keyword` | 9 |
| **total** | **723** |

`1,076 + 723 = 1,799 independent defects` ではありません。

構文とenvironmentが壊れたままなら、type checkerの総件数をそのまま「型品質」と読むこともできません。

## ここで「最強tool比較」をやめた

Google ResearchのTricorderが扱っているのも、analyzer単体の勝敗ではありません。

複数の解析を大規模codebaseとdeveloper workflowへ統合し、日常的に使われるsystemへすることが中心です。

- https://research.google/pubs/tricorder-building-a-program-analysis-ecosystem/
- https://research.google/pubs/lessons-from-building-static-analysis-tools-at-google/

この視点に立つと、品質toolの評価軸は変わります。

```text
semantic authority   最後に誰を信じるか
signal density       本当に独立してactionableか
feedback latency     context switch前に返るか
trust boundary       runtimeの実値をどこで止めるか
graph awareness      変更影響とtask依存を理解できるか
migration cost       既存運用を壊さずtool debtを減らせるか
stability boundary   stable / beta / experimentalを区別できるか
```

「rules数が多い」「速い」だけでは足りません。

**同じ責務を二つのtoolに持たせないことの方が重要です。**

## 先に結論：2026年8月なら、私はこう置く

### Python

```text
Ruff
  ↓
Pyrefly
  ↓
Pydantic @ untrusted runtime boundary
```

### TypeScript

```text
Biome formatter
  ↓
Oxlint
  ↓
tsc --noEmit
  ↓
Zod @ untrusted runtime boundary
```

### local commit orchestration

```text
prek
```

ただしprek自身を品質policyにはしません。

### monorepoだけ追加

```text
governance-heavy / heterogeneous workspace → Nx
lean JS/TS task graph + cache              → Turborepo
```

NxとTurborepoを同じworkspaceの競合task-graph authorityにはしません。

そしてsingle-project repoに、理由なくどちらかを追加することもしません。

## Python：Ruff + Pyrefly + Pydantic

### Ruffは「速い」より「authorityを減らせる」ことが強い

Ruffはlinterとformatterを同じtoolchainに持ち、Flake8系、isort、pyupgradeなど複数の既存責務を統合できます。

- https://docs.astral.sh/ruff/
- https://docs.astral.sh/ruff/linter/
- https://docs.astral.sh/ruff/formatter/

professional environmentで大きいのは、100 msか200 msかより、

```text
Black
isort
Flake8
pyupgrade
...
```

という複数version・複数config・複数exceptionを減らせることです。

**greenfield Pythonなら、format/lint authorityはRuffを第一候補にします。**

### Pyreflyはblocking type authority候補

Pyreflyは2026年5月にstable v1へ到達し、公式にproduction-readyとしています。

https://pyrefly.org/blog/v1.0/

今回のDeepCodeでは723件の大部分がparse failureに汚染されていたので、723という数字を「検出力score」にはしません。

それでも、現時点でproductionのblocking authorityを一つ選ぶならPyreflyを第一候補にします。

### tyは「負け」ではない。challengerに置く

今回の単発scan observationでは、tyは264 ms、Pyreflyは361 msでした。

ただしtyは現在もBetaです。

https://docs.astral.sh/ty/

だから、

```text
blocking CI             → Pyrefly
shadow / editor trial   → ty
```

とします。

両方を永久にblocking CIへ入れるのは、通常はauthority duplicationです。

### Pydanticはrepository-wide checkerではない

Pydanticの役割は、HTTP、JSON、CSV、environment、AI outputなど、code外から来る実値のvalidationです。

https://docs.pydantic.dev/2.10/concepts/validation_decorator/

```text
untrusted value
      ↓
  Pydantic
      ↓
validated application object
```

内部functionまで何でもPydantic化すると、runtime costとschema duplicationが増えます。

**trust boundaryだけに置く**のが基本です。

## TypeScript：Biome + Oxlint + tsc + Zod

### Biomeはformatter authorityに絞る

Biomeはlinterも持っています。

それでもこの構成ではformatter authorityへ役割を絞ります。

https://biomejs.dev/formatter/

理由はBiomeが弱いからではありません。

Oxlintもlint authorityとして採用するなら、同じrule domainを二重blockingしないためです。

### Oxlintはlint authority。ただしcompiler authorityまでは渡さない

Oxlintはtype-aware lintingを持ち、2026年時点ではかなり有力です。

https://oxc.rs/docs/guide/usage/linter/type-aware.html

一方、Oxlintの`typeCheck`は現在の公式config referenceでexperimental扱いです。

https://oxc.rs/docs/guide/usage/linter/config-file-reference

そのため現時点では、

```text
Oxlint         = lint authority
tsc --noEmit   = type authority
```

と分けます。

https://www.typescriptlang.org/tsconfig/noEmit.html

### Zodもboundaryだけ

Zodは`unknown`なruntime valueをschemaで検証し、validated valueへ変換する層です。

https://zod.dev/basics

Pydanticと同じく、static type checkerの代替ではありません。

## prek：今回いちばん直接比較できた置換

同じ `.pre-commit-config.yaml` を `pre-commit 4.6.2` と `prek 0.4.11` で実行しました。

単発観測はこうでした。

```text
pre-commit measured total  10,299 ms
prek measured total         2,619 ms
```

ただし別runnerなので「常に3.93倍」とは言いません。

より強い証拠は生成patchです。

```text
SHA-256(pre-commit patch)
30275602cf6b35644199d3a7fe949c038a10eaa9e6685074de4f7c8d62b36bf1

SHA-256(prek patch)
30275602cf6b35644199d3a7fe949c038a10eaa9e6685074de4f7c8d62b36bf1
```

このfixtureではbyte-identicalでした。

https://prek.j178.dev/compatibility/

つまり今回の範囲では、**既存hook semanticsを保ったままrunnerだけ交換できる可能性が高い**という結果です。

ただし設計上は、

```text
quality policy != prek
```

にします。

hook runnerを変えたら品質意味論まで変わる構成にはしません。

## Nx / Turborepoはcheckerの上に置く

ここで視点をrepository内部からworkspaceへ上げます。

RuffやOxlintは「このsourceが正しいか」を見ます。

Nx/Turborepoが見るのは、

```text
どのprojectが変わったか
どのtaskがその変更に依存するか
何を再実行すべきか
何をcacheから戻せるか
```

です。

### Nx：governanceをgraphへ持ちたいとき

Nxの`affected`はGit差分とproject graphから、変更の影響を受ける最小project集合を求めます。

https://nx.dev/docs/features/ci-features/affected

さらにproject tagを使ってarchitecture boundaryを宣言できます。

https://nx.dev/docs/features/enforce-module-boundaries

ここには実務上の重要な注意があります。

OSSのJavaScript/TypeScript向けmodule-boundary enforcementは `@nx/enforce-module-boundaries` というESLint ruleです。

つまりOxlintへ移行するからといってESLintを機械的に削除すると、**lint ruleではなくarchitecture policyまで消す可能性があります。**

language-agnosticなConformanceはEnterprise側です。

Nxを選ぶ理由は「buildが速い」だけではなく、**workspace architectureをproject graphへ持ちたいか**です。

### Turborepo：task DAGとcacheを薄く入れたいとき

Turborepoはpackage graphからtask graphを組み、DAGとしてtask dependencyを扱います。

https://turborepo.dev/docs/core-concepts/package-and-task-graph

cacheはinput fingerprintに基づき、local/remoteで再利用できます。

https://turborepo.dev/docs/crafting-your-repository/caching

JS/TS中心で、既存package scriptsを大きく変えずtask executionとcacheを強くしたいなら自然です。

ただし `turbo boundaries` は現在もExperimentalです。

https://turborepo.dev/docs/reference/boundaries

したがって、architecture governanceを最重要要件にするなら現時点ではNxの方が成熟しています。

## 「全部commit時に走らせる」もやめる

強いtoolを選んでも、配置を間違えるとdeveloper experienceを壊します。

私はfeedback topologyをこう分けます。

```text
EDITOR / SAVE
  Ruff / Biome
  Pyrefly or ty LSP
  Oxlint LSP

COMMIT
  changed-file format/lint
  cheap syntax/config validation

PR CI
  full Ruff
  full Pyrefly
  Oxlint --type-aware
  tsc --noEmit
  contract fixtures
  unit tests

HEAVIER / SCHEDULED
  integration / E2E
  dependency/security audit
  expensive repository-wide checks
```

速さの価値はbenchmark順位ではありません。

**人間やagentが次の行動へ移る前に、十分に信頼できるfailureを返せること**です。

## だから「最強」は一個ではない

現時点の第一候補をもう一度まとめます。

| concern | authority |
|---|---|
| Python format/lint | **Ruff** |
| Python type | **Pyrefly** |
| Python runtime contract | **Pydantic @ boundary** |
| JS/TS format | **Biome formatter** |
| JS/TS lint | **Oxlint** |
| TypeScript type | **`tsc --noEmit`** |
| TS runtime contract | **Zod @ boundary** |
| local hook runner | **prek** |
| governance-heavy monorepo | **Nx** |
| lean JS/TS monorepo execution | **Turborepo** |

ただし、この表だけをコピーするのがこの記事の結論ではありません。

今回、最初に見た1,799という数字は全部正しい観測でした。

間違っていたのは、**その1,799を1,799個の独立した問題だと解釈したこと**です。

quality platformでも同じです。

強いtoolを10個集めても、10個の独立した価値にはなりません。

責務が重なればnoiseになり、graphを理解しなければ無駄なCIになり、trust boundaryを間違えればruntime defectは残ります。

> **最強の品質基盤は、最強toolの寄せ集めではない。各failureを、最も早く・最も信頼できるauthorityへ一度だけ割り当てる設計である。**

次の実験では、508件のsyntax failureを先に除去してPyreflyを再実行し、723件がどこまで減るかを測ります。

その次に、実際に状態の悪いTypeScript monorepoを固定し、Biome / Oxlint / tsc と Nx / Turborepoのaffected/cache behaviorまで同じ基準で実測します。
