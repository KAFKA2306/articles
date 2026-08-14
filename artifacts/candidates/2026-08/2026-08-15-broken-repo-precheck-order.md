<!-- pipeline_meta: {"idea_source":"public-github-engineering","idea_only":true,"raw_private_content_persisted":false,"topic":{"title":"コードを書く速度より、検証する速度が問題になった――2026年の開発品質スタックを組み直す","audience":"AI coding agent、GitHub Actions、Python/TypeScript、monorepoを運用するTech Lead・Platform Engineer・開発者","central_question":"コード生成が高速化した環境で、どの検証を誰に任せれば、変更速度を落とさず信頼性を上げられるか","surprising_finding":"壊れた実repositoryでRuff 1,076 findingsとPyrefly 723 findingsを得たが、Pyreflyの508 parse-errorはRuffの508 invalid-syntaxと同じ上流failureを反映していた。checkerを増やすだけではsignalは加算されない","initial_hypothesis":"高速なcheckerを増やせば、短時間でより多くの独立した欠陥を発見できる","hypothesis_update":"検証基盤はtool listではなくauthority mapとして設計すべき。source hygiene、static semantics、runtime boundary、workspace graph、local triggerを別責務として配置し、同じ責務を二重blockingしない","stakes":"AIがコード量を増やすほど、重複diagnostic、遅いCI、曖昧なauthorityは人間とagent双方の修復速度を落とす","story_type":"verification-bottleneck","reader_before":"最新toolの名前は知っているが、Ruff/Pyrefly/Pydantic、Biome/Oxlint/tsc/Zod、prek、Nx/Turborepoをどう組み合わせるべきか判断できない","reader_after":"自分のrepoで各検証責務のauthorityを決め、single repoとmonorepoで必要な層だけ導入できる","design_philosophy":"one responsibility, one authority。速いtoolを集めるのではなく、最も安い場所で最も信頼できるfailureを返す。runtime validationとworkspace graphは必要な境界だけに置く","why_this_article":"壊れた公開repositoryの固定commitでRuff/Pyrefly/ty/pre-commit/prekを実測し、raw diagnosticsとpatchを比較した。そのうえでGoogle Researchと各tool公式docsだけから2026年8月時点の役割分担を再構成している","proof_of_value":"KAFKA2306/DeepCode@088059855d2c9187c51d674db02a06f70c37f087、Actions run 31812751114、Ruff 1,076 findings、Pyrefly 723 findings、syntax系最大categoryが双方508、pre-commit/prekの生成patch SHA-256一致","desired_reader_action":"formatter/linter/type/runtime boundary/workspace graph/local triggerのauthority mapを作り、重複checkを減らしてPR feedbackを短くする","non_goal":"未実測toolの性能ランキングを作らない。Pydantic/Zodをlinter扱いしない。Nx/Turborepoを小規模repoへ理由なく入れない。既存Pyright/ESLintを無条件に削除しない"},"public_evidence":["https://github.com/KAFKA2306/articles/actions/runs/31812751114","https://github.com/KAFKA2306/DeepCode/commit/088059855d2c9187c51d674db02a06f70c37f087","https://research.google/pubs/tricorder-building-a-program-analysis-ecosystem/","https://www.oreilly.com/radar/ai-is-writing-our-code-faster-than-we-can-verify-it/","https://www.oreilly.com/radar/ai-demands-more-engineering-discipline-not-less/","https://docs.astral.sh/ruff/","https://pyrefly.org/blog/v1.0/","https://docs.pydantic.dev/2.10/concepts/validation_decorator/","https://biomejs.dev/formatter/","https://oxc.rs/docs/guide/usage/linter/type-aware.html","https://oxc.rs/docs/guide/usage/linter/config-file-reference","https://www.typescriptlang.org/tsconfig/noEmit.html","https://zod.dev/basics","https://prek.j178.dev/compatibility/","https://nx.dev/docs/features/enforce-module-boundaries","https://nx.dev/docs/kb/what-is-a-monorepo","https://turborepo.dev/docs/core-concepts/package-and-task-graph","https://turborepo.dev/docs/crafting-your-repository/caching","https://turborepo.dev/docs/reference/boundaries"]} -->

# コードを書く速度より、検証する速度が問題になった――2026年の開発品質スタックを組み直す

AI coding agentで、コードを書くコストは急速に下がっています。

一方で、生成された変更を**信じてよいか判断する仕事**は消えていません。むしろ、変更量が増えるほど検証側の設計がボトルネックになります。

O'Reilly Radarでも2026年に「AIがコードを書く速度が検証速度を上回る」「AI時代ほどengineering disciplineが必要になる」という問題設定が前面に出ています。

- https://www.oreilly.com/radar/ai-is-writing-our-code-faster-than-we-can-verify-it/
- https://www.oreilly.com/radar/ai-demands-more-engineering-discipline-not-less/

では、検証側は何を標準にすればよいのか。

Ruff、Pyrefly、Pydantic、Biome、Oxlint、TypeScript compiler、Zod、prek。monorepoならNxやTurborepoも候補に入ります。

この選択を「どのtoolが一番速いか」だけで決めると、設計を誤ります。

## 先に結論

2026年8月時点で、greenfieldなら私は次の役割分担から始めます。

| 責務 | 第一候補 | authorityとしての意味 |
|---|---|---|
| Python source hygiene | **Ruff** | format / lint |
| Python static semantics | **Pyrefly** | blocking type check |
| Python runtime boundary | **Pydantic** | 外部値のvalidation |
| JS/TS formatting | **Biome formatter** | formatting |
| JS/TS lint | **Oxlint** | lint / type-aware lint |
| TypeScript semantics | **`tsc --noEmit`** | compiler/type authority |
| TS runtime boundary | **Zod** | `unknown`のvalidation |
| local Git hook | **prek** | checkを起動するrunner |
| governance-heavy monorepo | **Nx** | project graph / affected / architecture policy |
| lean JS/TS monorepo | **Turborepo** | task graph / cache |

これは「10個入れれば最強」という意味ではありません。

むしろ逆です。

**同じ責務を複数toolに持たせないための表**です。

## 1,799件見つけて、最初の考えが崩れた

この設計を考えるきっかけになったのは、きれいなbenchmarkではなく、実際に壊れていた公開repositoryでした。

対象は `KAFKA2306/DeepCode` の固定commitです。

```text
088059855d2c9187c51d674db02a06f70c37f087
```

実験run:
https://github.com/KAFKA2306/articles/actions/runs/31812751114

RuffとPyreflyを当てると、最初はこう見えました。

```text
Ruff      1,076 findings
Pyrefly     723 findings
```

合計1,799件。

Ruffのscan観測は99 ms、Pyreflyは361 msでした。

これだけ見ると「高速なcheckerを増やせば、短時間でより広い故障面が得られる」と考えたくなります。

しかしraw diagnosticsを分類すると、最大categoryはこうでした。

```text
Ruff     invalid-syntax  508
Pyrefly  parse-error     508
```

Pyreflyの723件中508件はparse errorです。

つまり、**723件の独立したtype defectが追加で見つかったわけではありません。** 同じ壊れたsyntaxが、後段の解析器にも伝播していました。

ここで「diagnostic総数」を品質指標にする考えを捨てました。

GoogleのTricorderも、program analysisを単体toolの競争ではなく、複数解析をdeveloper workflowへ統合するplatform問題として扱っています。

https://research.google/pubs/tricorder-building-a-program-analysis-ecosystem/

必要なのはcheckerのカタログではなく、**どのfailureを誰が最終判定するかというauthority map**です。

## Layer 1: source hygieneは安く、速く、議論なく返す

PythonではRuffを第一候補にします。

Ruffはlinterとformatterを同じtoolchainに持ち、Flake8系、isort、pyupgradeなど広い責務を統合しています。

https://docs.astral.sh/ruff/

価値は「何倍速いか」だけではありません。

複数のformat/lint authorityを一つに減らせることが重要です。

```text
Black
isort
Flake8 + plugins
pyupgrade
...
```

を別々に運用すると、version、config、ignore、autofixの責任が分散します。

Ruffはこの層をかなり圧縮できます。

TypeScript側ではBiomeをformatter authorityに置きます。

Biomeは意図的にoptionを絞るopinionated formatterです。style debateをtool config debateへ置き換えない、という設計思想が明示されています。

https://biomejs.dev/formatter/

この層の目的は高度なバグ発見ではありません。

**レビューから機械的なstyle議論を消し、壊れたsyntaxや明白なsource problemを早く返すこと**です。

## Layer 2: static semanticsは一つのauthorityにする

Python type checkerはPyreflyをblocking authority候補にします。

Pyreflyは2026年5月にstable v1へ到達し、production useにreadyだと公式に表明しています。

https://pyrefly.org/blog/v1.0/

今回の実験では大量のparse errorに汚染されたため、723件という数字をPyreflyの「検出力score」には使いません。

ただしproductionのblocking type checkerを今ひとつ選ぶ、という判断ではstable境界が明確です。

TypeScriptでは、Oxlintと`tsc`を同じものとして扱いません。

Oxlintのtype-aware lintingはTypeScriptのtype informationを使い、現在59/61のtype-aware typescript-eslint rulesをカバーしています。

https://oxc.rs/docs/guide/usage/linter/type-aware.html

一方、compiler diagnosticsを統合する`typeCheck`は公式config referenceでまだexperimentalです。

https://oxc.rs/docs/guide/usage/linter/config-file-reference

したがって現時点では、

```text
Oxlint       = lint authority
tsc --noEmit = TypeScript compiler/type authority
```

と分けます。

`noEmit`はTypeScriptをsource code type-checkerとして使い、JavaScript等の出力を生成しない公式optionです。

https://www.typescriptlang.org/tsconfig/noEmit.html

Oxlintのtype-check機能が成熟すれば将来この二重program構築を統合できる可能性はあります。しかし**experimentalな機能へ最終authorityを急いで移す理由はありません。**

## Layer 3: PydanticとZodはprecheckではない

ここを混ぜると設計が崩れます。

PydanticとZodはlinterではありません。

static checkerが保証できるのは、code上で想定した型関係です。productionではその外から値が入ります。

```text
HTTP
JSON / YAML
CSV
DB result
environment variable
user input
AI model output
```

Pydanticの`validate_call`もruntimeで引数をvalidationし、公式docsはそのvalidationにperformance costがあることを明示しています。

https://docs.pydantic.dev/2.10/concepts/validation_decorator/

Zodもschemaに対してruntime inputを`.parse()` / `.safeParse()`し、validated dataと推論されたTypeScript typeを得る仕組みです。

https://zod.dev/basics

だから配置はこうです。

```text
untrusted value
      ↓
Pydantic / Zod
      ↓
validated application core
```

すべての内部functionへvalidationを追加するのではなく、**trust boundaryにだけ置く**のが基本です。

## Layer 4: prekはpolicyではなくtrigger

local commitでcheckをどう起動するかは別問題です。

今回、既存の同じ`.pre-commit-config.yaml`を`pre-commit 4.6.2`と`prek 0.4.11`で実行しました。

単発観測では、

```text
pre-commit measured total  10,299 ms
prek measured total         2,619 ms
```

でした。

別runnerなので普遍的な「3.93倍高速」という結論にはしません。

より重要なのは、両者が生成したworking-tree patchのSHA-256が一致したことです。

```text
30275602cf6b35644199d3a7fe949c038a10eaa9e6685074de4f7c8d62b36bf1
```

prek公式も既存`.pre-commit-config.yaml`との互換を主要目的にしています。

https://prek.j178.dev/compatibility/

このfixtureでは、runnerだけ交換して同じ修正結果を得られました。

ただし、品質policy自体をprekへ埋め込みません。

```text
quality policy != hook runner
```

repository command、tool config、CI contractが正準で、prekはそれをcommit時に起動するだけ、という構造にします。

## Layer 5: Nx / Turborepoはcheckerの上にある

monorepoになると、問題が変わります。

RuffやOxlintが答えるのは、主に「このsourceに問題があるか」です。

workspaceではさらに、

```text
何が変わったか
どのprojectが影響を受けるか
どのtaskを再実行すべきか
何をcacheから戻してよいか
どのprojectがどこへ依存してよいか
```

を解かなければなりません。

Nxはgraph-aware toolingとして、affected detection、caching、module boundariesなどを前面に置いています。

https://nx.dev/docs/kb/what-is-a-monorepo

architecture governanceを重視するworkspaceならNxが強い理由はここです。

ただし実務上の注意があります。

Nx OSSのJavaScript/TypeScript向けmodule boundary enforcementは`@nx/enforce-module-boundaries`というESLint ruleです。language-agnosticなConformanceはEnterprise機能です。

https://nx.dev/docs/features/enforce-module-boundaries

したがって、Oxlintへ移行するからといってESLintを機械的に削除すると、**lint設定ではなくarchitecture policyまで消す可能性があります。**

Turborepoはよりtask execution寄りです。

package graphからtask graphを作り、DAGとしてtask dependencyを扱います。

https://turborepo.dev/docs/core-concepts/package-and-task-graph

cacheはtask inputのfingerprintから結果を再利用し、remote cacheでteam/CI間共有もできます。

https://turborepo.dev/docs/crafting-your-repository/caching

JS/TS中心で既存package scriptsを活かしながらtask graphとcacheを足したいなら自然です。

一方、`turbo boundaries`は現在もExperimentalです。

https://turborepo.dev/docs/reference/boundaries

そのため現時点では、

```text
architecture governanceを強く持つ → Nx
leanなJS/TS task graph + cache     → Turborepo
```

と判断します。

NxとTurborepoを同じworkspaceへ競合するtask-graph authorityとして両方入れる必要はありません。

## 最終的なstackは「一本のpipeline」ではない

`Ruff → Pyrefly → Pydantic` のように一直線で描くと、少し誤解があります。

実際には、**時間軸と責務軸の二次元**です。

```text
EDITOR / SAVE
  Ruff / Biome
  Pyrefly LSP
  Oxlint LSP

COMMIT
  changed-file format/lint
  cheap syntax/config checks
  triggered by prek

PR CI
  full Ruff
  full Pyrefly
  Oxlint --type-aware
  tsc --noEmit
  contract fixtures
  unit tests

RUNTIME BOUNDARY
  Pydantic / Zod

MONOREPO CONTROL PLANE
  Nx OR Turborepo

HEAVIER CI
  integration / E2E / security / repository-wide audits
```

これなら、安いfailureは早く返り、重い検証だけCIへ送れます。

そして一つの責務に複数のblocking authorityを持たせません。

## 「最強tool」はある。でも最強stackはtool listではない

個別の採用判断はかなり明確です。

- Python format/lint: **Ruff**
- Python type: **Pyrefly**
- Python external data: **Pydantic**
- JS/TS format: **Biome formatter**
- JS/TS lint: **Oxlint**
- TypeScript type: **`tsc --noEmit`**
- TS external data: **Zod**
- local hook runner: **prek**
- governance-heavy monorepo: **Nx**
- lean JS/TS monorepo: **Turborepo**

しかし、今回いちばん大きかった発見はtool名ではありません。

Ruff 1,076件とPyrefly 723件は、どちらも正しい観測でした。

間違っていたのは、それを1,799個の独立した価値だと解釈したことです。

AIで生成速度が上がるほど、検証基盤にも同じ問題が起きます。

**checkerを増やすことは簡単です。何を信じるかを一意にすることの方が難しい。**

コード生成が豊富になった時代に希少になるのは、syntaxを書く能力ではなく、変更を短時間で「通してよい」と判断できる検証設計です。

次に測るべきなのは、さらにtoolを増やしたときの総diagnostic数ではありません。

- syntax修復前後でtype diagnosticがどれだけ減るか
- dependencyを正しく入れた後に何件が残るか
- TypeScript実repoでBiome/Oxlint/tscがどこまで補完・重複するか
- monorepoでNx/TurborepoがPR feedback timeとCI実行量をどれだけ変えるか

です。

**検証速度は、toolのbenchmarkではなく、信頼できる判断までの時間で測る。**
