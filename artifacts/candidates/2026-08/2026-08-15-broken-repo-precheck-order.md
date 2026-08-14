<!-- pipeline_meta: {"idea_source":"public-github-engineering","idea_only":true,"raw_private_content_persisted":false,"topic":{"title":"2026年のprecheckは何を選ぶべきか。壊れたrepoで見えた「最強tool」より重要な設計","audience":"複数repository、GitHub Actions、AI coding agentを運用する開発者・Tech Lead","central_question":"2026年のPython/TypeScript repositoryで、品質を落とさず変更速度を上げるprecheck control planeはどう設計すべきか","surprising_finding":"Ruff 1,076件とPyrefly 723件を足しても独立欠陥1,799件にはならなかった。Pyreflyの723件中508件はparse errorで、Ruffの508 invalid-syntaxと同じ前段failureに依存していた。toolの検出数ではなく、semantic authority、signal、feedback latency、trust boundary、migration costで役割を分ける必要があった","initial_hypothesis":"高速な最新toolを横並びで増やせば、広い故障面を短時間で得られる","hypothesis_update":"professionalな標準構成はPython=Ruff+Pyrefly+必要箇所だけPydantic、TypeScript=Biome formatter+Oxlint+tsc+必要箇所だけZod、prek=交換可能なorchestrator。各toolを同じ重さで全commitに走らせず、editor→commit→PR CI→runtime/integrationのfeedback topologyを設計する","stakes":"toolを増やすだけではdiagnostic noise、CI待ち時間、二重ルール、migration debtが増える。品質systemとして設計すればAI agentを含む変更速度を上げつつcode healthを守れる","story_type":"architecture-after-falsified-ranking","reader_before":"Ruff、Pyrefly、ty、Biome、Oxlint、Pydantic、Zod、prekなどの候補は知っているが、結局どれを標準化し、どれを捨て、どこで実行すべきか判断できない","reader_after":"tool単体ランキングではなく、authority・signal・latency・boundary・migrationの5軸でstackを設計し、新規repo/legacy repoそれぞれの採用判断ができる","design_philosophy":"one responsibility, one authority。formatter、linter、type authority、runtime contract、orchestrationを分離し、同じ責務を二重にblockingしない。前段failureほど早く安く返し、重い検査ほどPR CI側へ送る","why_this_article":"実際に壊れていた公開repositoryの固定commitでRuff/Pyrefly/ty/pre-commit/prekを同一Actions harnessから実行し、raw diagnosticsと生成patchまで比較した上で、Googleのstatic-analysis/platform engineering原則と2026年の各tool公式仕様に照らして採用architectureへ落としている","proof_of_value":"KAFKA2306/DeepCode@088059855d2c9187c51d674db02a06f70c37f087、GitHub Actions run 31812751114、Ruff 1,076 findings、Pyrefly 723 findings、そのうちparse-error 508、pre-commit/prek生成patch SHA-256一致","desired_reader_action":"自分のrepoでformatter/linter/type/runtime validation/orchestratorのauthority mapを作り、重複toolを減らし、fast feedbackとfull CIを分離する","non_goal":"単発速度で普遍的なtoolランキングを作らない。Pydantic/Biome/Oxlint/tsc/Zodを今回のDeepCode実験で実測済みとは扱わない。既存Pyright/ESLintを根拠なく一括置換しない"},"public_evidence":["https://github.com/KAFKA2306/articles/pull/115","https://github.com/KAFKA2306/articles/actions/runs/31812751114","https://github.com/KAFKA2306/DeepCode/commit/088059855d2c9187c51d674db02a06f70c37f087","https://research.google/pubs/tricorder-building-a-program-analysis-ecosystem/","https://google.github.io/eng-practices/review/reviewer/standard.html","https://docs.astral.sh/ruff/","https://pyrefly.org/blog/v1.0/","https://astral.sh/blog/ty","https://pyrefly.org/en/docs/pydantic/","https://prek.j178.dev/compatibility/","https://biomejs.dev/formatter/","https://oxc.rs/docs/guide/usage/linter/type-aware.html","https://oxc.rs/docs/guide/usage/linter/config-file-reference","https://www.typescriptlang.org/tsconfig/noEmit.html","https://zod.dev/packages/zod"]} -->

# 2026年のprecheckは何を選ぶべきか。壊れたrepoで見えた「最強tool」より重要な設計

Ruff、Pyrefly、ty、Pydantic、Biome、Oxlint、Zod、prek。

2026年の開発toolはかなり速くなりました。

だからこそ、選び方を間違えやすい。

「何倍速いか」「何rulesあるか」「何件見つけたか」を並べると、どのtoolも強く見えます。

しかしTech Leadが決めたいのはbenchmark一位ではありません。

**このtoolchainを標準化したとき、変更速度を落とさず、productionへ流出する欠陥を減らし、5年後も運用できるか。**

Googleが大規模static analysis platformのTricorderで扱った問題も、単体analyzerの性能だけではありませんでした。複数の解析をどう開発者workflowへ統合し、実際に使われるsystemにするかが中心です。

- Tricorder: https://research.google/pubs/tricorder-building-a-program-analysis-ecosystem/
- Google Engineering Practices: https://google.github.io/eng-practices/review/reviewer/standard.html

そこで、実際に壊れていた公開repositoryを使ってprecheckを試しました。

最初に見えた数字は派手でした。

```text
Ruff      1,076 findings
Pyrefly     723 findings
```

ところがraw diagnosticsを分類すると、Pyreflyの723件中508件がparse errorでした。

Ruffにも508件の`invalid-syntax`がありました。

つまり、

```text
1,076 + 723 = 1,799 independent defects
```

ではありません。

**同じ壊れた構文が、複数の解析層へ伝播していました。**

ここからtool選定の問いを変えました。

「最強のlinterはどれか」ではなく、

> **どのtoolを、どの責任の唯一のauthorityにして、どのタイミングで走らせるべきか。**

これがこの記事の問いです。

## 結論：2026年8月時点で私ならこうする

新規repositoryなら、第一候補は次です。

```text
Python
  Ruff                  syntax / format / lint
  Pyrefly               static type authority
  Pydantic              untrusted runtime boundary only

TypeScript
  Biome formatter       formatting authority
  Oxlint                lint authority
  tsc --noEmit          type authority
  Zod                   untrusted runtime boundary only

Orchestration
  prek                  local hook runner; quality semanticsは持たせない
```

表にするとこうです。

| concern | 第一候補 | 位置づけ |
|---|---|---|
| Python format/lint | **Ruff** | 採用 |
| Python type | **Pyrefly** | production標準候補 |
| Python experimental fast type | **ty** | 有力だがBeta |
| Python runtime contract | **Pydantic** | 必要なboundaryだけ |
| JS/TS format | **Biome** | formatter authority |
| JS/TS lint | **Oxlint** | lint authority |
| TypeScript type | **`tsc --noEmit`** | compiler authority |
| TS runtime contract | **Zod 4** | 必要なboundaryだけ |
| Git hook orchestration | **prek** | transport / orchestration |

ただし重要なのは製品名ではありません。

この構成が強い理由は、**責務が重なりにくいこと**です。

## professionalなtoolchain評価は5軸で見る

今回、toolを次の5軸で見直しました。

### 1. Semantic authority — 最後に誰を信じるか

同じ責務を複数toolへ持たせると、差分が出た瞬間に運用が破綻します。

```text
formatterは誰が正しい？
linterは誰が正しい？
type errorは誰が正しい？
runtime inputは誰が正しい？
```

これを一つずつ決めます。

Pythonなら、format/lintはRuff、typeはPyrefly。

TypeScriptなら、formatはBiome、lintはOxlint、typeの最終authorityはTypeScript compilerである`tsc`。

Oxlintは2026年7月にtype-aware lintingをstable化し、TypeScript semanticsを利用したruleを実行できます。

一方、Oxlintの`typeCheck`自体は現行config referenceでexperimentalです。

- type-aware linting: https://oxc.rs/docs/guide/usage/linter/type-aware.html
- config reference: https://oxc.rs/docs/guide/usage/linter/config-file-reference

だから現時点では、Oxlintにcompiler authorityまで渡しません。

```text
Oxlint = lint authority
TypeScript compiler = type authority
```

この分離の方がmigration riskを制御できます。

### 2. Signal density — 件数ではなく、直す価値があるか

static analysisは多く警告すれば強いわけではありません。

今回のbroken repoでそれを実測しました。

対象:

```text
KAFKA2306/DeepCode
088059855d2c9187c51d674db02a06f70c37f087
```

実験:
https://github.com/KAFKA2306/articles/actions/runs/31812751114

Ruff 0.16.3は47 filesから1,076 findingsを返しました。

| Ruff category | count |
|---|---:|
| `invalid-syntax` | **508** |
| `UP006` | 147 |
| `BLE001` | 143 |
| `I001` | 44 |
| `RUF010` | 42 |

Pyrefly 1.2.0は723 findingsでした。

| Pyrefly category | count |
|---|---:|
| `parse-error` | **508** |
| `unknown-name` | 108 |
| `missing-import` | 86 |
| `invalid-syntax` | 12 |
| `unexpected-keyword` | 9 |

最大categoryが508対508で一致しました。

この時点では、Pyreflyが「新しい型欠陥を723件追加発見した」とは言えません。

**syntax failureを直す前のtype diagnosticは、confidenceが低いものを含む。**

そのためCI UIやagentへ返す結果も、総件数ではなくdependencyを持たせるべきです。

```text
ROOT / BLOCKING
  syntax: 508

DOWNSTREAM / lower confidence until root is repaired
  missing-import: 86
  unknown-name: 108
  ...
```

AI coding agent時代には特に重要です。

1,000 diagnosticsを渡すより、最初のroot causeを1つ渡した方が修復能力は高くなります。

### 3. Feedback latency — 速さはCI代ではなく人間の認知負荷に効く

速度は重要です。

ただし「benchmarkで勝つため」ではありません。

速いanalysisは、developerがcontext switchする前にfeedbackを返せます。

Google Engineering Practicesでも、code healthを守る一方でdeveloperが前進できることを明確にtrade-offとして扱っています。

https://google.github.io/eng-practices/review/reviewer/standard.html

今回の単発Actions observationは次でした。

| tool | version | scan observation |
|---|---:|---:|
| Ruff | 0.16.3 | 99 ms |
| ty | 0.0.71 | 264 ms |
| Pyrefly | 1.2.0 | 361 ms |
| prek | 0.4.11 | 2,326 ms |
| pre-commit | 4.6.2 | 8,765 ms |

これは別runner VMなので一般benchmarkにはしません。

ただし、Ruff/Pyrefly/tyのようなsub-second classのanalysisをdeveloper loopへ寄せる設計自体は合理的です。

ここで重要なのは、**全checkをpre-commitへ詰め込まないこと**です。

私ならfeedback topologyをこう分けます。

```text
EDITOR / SAVE
  Ruff / Biome
  Pyrefly or ty LSP
  Oxlint LSP

COMMIT
  deterministic formatter/lint on changed files
  cheap syntax/config validation

PR CI
  full Ruff
  full Pyrefly
  Oxlint --type-aware
  tsc --noEmit
  contract fixtures
  unit tests

HEAVIER CI / scheduled
  integration / E2E
  dependency/security
  expensive repository-wide audits
```

`prek`はこの中のCOMMIT層を便利にするtoolであって、architectureの中心ではありません。

### 4. Trust boundary — static typeで守れない入力をどこで止めるか

ここでPydanticとZodの意味が出ます。

これらはlinterではありません。

production systemでは、codeの外から値が入ります。

```text
HTTP response
JSON / YAML
CSV
DB row
environment variable
AI model output
user input
```

static type checkerは、この値が実際にcontractを満たして届くことまでは保証できません。

そこでboundaryだけruntime schemaを置きます。

Python:

```text
external data
    ↓
Pydantic
    ↓ validated object
application core
```

TypeScript:

```text
unknown
  ↓
Zod
  ↓ typed validated value
application core
```

Zod 4はstableで、schema parsingとTypeScript type inferenceを同じschemaから扱います。

https://zod.dev/packages/zod

Pydanticもruntime validationを担います。

一方、すべての内部functionへPydantic validationを付けるのは逆です。

validation costとschema duplicationを増やすだけです。

**Pydantic/Zodはrepository-wide precheckではなく、trust boundary contractです。**

ここは前のstack案から重要な修正です。

### 5. Migration cost — replacementはtool数ではなくoperational debtを減らせるか

Ruffが強い最大の理由の一つは速度だけではありません。

RuffはFlake8系、isort、pyupgrade、autoflake等の広いlint責務を統合し、formatterも同じtoolchainに持ちます。

https://docs.astral.sh/ruff/

これは、

```text
Black
isort
Flake8
pyupgrade
...
```

を長期で別version管理するoperational costを圧縮できるという意味があります。

TypeScript側でも同じです。

ただしBiomeとOxlintを両方lint authorityにすると、また二重化します。

だからこの構成では、

```text
Biome = formatter
Oxlint = linter
```

へ意図的に絞ります。

Biome 2.5自身は500を超えるlint ruleとcross-file lintingを持ちます。

https://biomejs.dev/blog/biome-v2-5/

つまりBiomeが弱いからlintを使わないのではありません。

**組織のstandardとしてauthorityを一つにするために、あえて責務を限定する。**

これがtool-centricとplatform-centricの違いです。

## Ruff + Pyrefly + Pydanticはどうだったか

### Ruff — 強く推奨

今回の実repoでも有効でした。

Ruffはsyntax root failureを最初の安い層で露出し、lint/format関連toolを集約できます。

新規Python repositoryなら第一候補です。

### Pyrefly — production標準候補

Pyreflyは2026年5月にstable v1へ到達し、公式にproduction readyとされています。

https://pyrefly.org/blog/v1.0/

Meta側ではInstagramを含むproduction codebaseで使われていると説明されています。

今回のDeepCodeでは大量parse errorの影響を受けたので、723件という件数そのものを検出力scoreにはしません。

それでも、stable status、IDE/CLI、段階導入、Pydantic supportを考えると、production標準のtype authority候補として扱いやすいです。

### ty — かなり重要。ただし今はchallenger

今回のscan observationでは264 msでPyreflyの361 msより短かったです。

Astralのtyはincremental analysisを中心設計にしており、developer feedback latencyでは非常に有力です。

https://astral.sh/blog/ty

ただし2026年8月現在もBetaです。

Astral自身はmotivated usersへproduction利用を勧めていますが、stableは今後のmilestoneです。

したがって私なら、

```text
production blocking authority → Pyrefly
shadow / evaluation / speed-sensitive editor → ty
```

から始めます。

stable化後に再評価します。

両方を永久にblocking CIで走らせるのは、通常はしません。

### Pydantic — 採用。ただしprecheckではない

外部data contractがあるrepositoryでは強い。

しかし「Python repoだから必ずPydantic」は違います。

pure libraryやruntime inputを持たないtoolでは不要な場合があります。

## Biome + Oxlint + tsc + Zodはどうか

### Biome formatter — 採用候補

Biome formatterはopinionatedでoptionを絞り、style debateを減らす思想を明示しています。

https://biomejs.dev/formatter/

professional environmentでは、formatterの価値は美しさより**人間がstyle reviewをしなくてよくなること**です。

その用途ならかなり適しています。

### Oxlint — 2026年に評価が上がった

Oxlintのtype-aware lintingは2026年7月にstableになりました。

現在59/61のtypescript-eslint type-aware rulesをサポートし、multi-file analysisも持ちます。

https://oxc.rs/docs/guide/usage/linter/type-aware.html

ただしtype-aware modeはTypeScript 7系を前提とし、legacy tsconfig optionにはmigration requirementがあります。

つまり新規repoと既存large monorepoで導入難度が違います。

**greenfieldなら強い。legacyならcompatibility auditが先。**

### tsc --noEmit — まだ外さない

Oxlintは`--type-check`でcompiler diagnosticsも統合でき、公式docsは別`tsc --noEmit`を置換できる形も示しています。

一方、config referenceは`typeCheck`をexperimentalとしています。

だから2026年8月時点では私は`tsc --noEmit`を残します。

https://www.typescriptlang.org/tsconfig/noEmit.html

これは速度より、**semantic authorityをexperimental featureへ移す必要がまだない**という判断です。

### Zod — boundaryがあるなら採用

Zod 4はstableです。

frontend/backend/API boundaryで`unknown`をvalidated dataへ変える用途なら非常に自然です。

ただし内部domain objectまで全部Zod schemaで包む必要はありません。

## prekはどうだったか

今回最も直接比較できたのがここです。

同じ`.pre-commit-config.yaml`を、`pre-commit 4.6.2`と`prek 0.4.11`へ渡しました。

```text
pre-commit measured total  10,299 ms
prek measured total         2,619 ms
```

runner条件が異なるので普遍的な3.93倍とは主張しません。

重要だったのは生成patchです。

```text
SHA-256(pre-commit patch)
30275602cf6b35644199d3a7fe949c038a10eaa9e6685074de4f7c8d62b36bf1

SHA-256(prek patch)
30275602cf6b35644199d3a7fe949c038a10eaa9e6685074de4f7c8d62b36bf1
```

このfixtureではbyte-identicalでした。

既存configを保ちながらrunnerだけ差し替えるmigration pathとしてはかなり良い結果です。

ただし設計上、prekは**交換可能であるべき**です。

```text
quality policy
    ≠ prek

quality policy
    = repository commands / configs / CI contract
```

hook runnerを変えただけでquality semanticsが変わる構成にはしません。

## だから「最強stack」の答えはこうなる

### Greenfield Python

```text
Ruff
Pyrefly
Pydantic only at trust boundaries
prek for local orchestration
```

かなり強く推奨します。

### Greenfield TypeScript

```text
Biome formatter
Oxlint --type-aware
tsc --noEmit
Zod only at trust boundaries
prek if Git hook standardization is useful
```

2026年8月なら第一候補に置きます。

### Legacy Python

Ruff migrationは有力です。

一方、既にPyright/mypyが安定運用されているなら、Pyreflyへ移すこと自体をKPIにしません。

shadow runでfalse positive、coverage、latency、config migration costを測ってから切り替えます。

### Legacy TypeScript

Oxlint導入前に、ESLint plugin dependencyとTypeScript/tsconfig compatibilityをinventoryします。

unsupported pluginやlegacy TypeScript requirementがあるrepoで、tool標準化のためだけにmigration scopeを膨らませるのは逆効果です。

## 今回の実験で本当に変わった考え

最初はこう考えていました。

```text
速いtoolを全部入れる
        ↓
たくさん見つかる
        ↓
品質が上がる
```

今は違います。

```text
one concern
  ↓
one authority
  ↓
fastest useful feedback point
  ↓
trust boundaryでruntime validation
  ↓
full CIでsystem correctness
```

最強のtoolを選ぶこと自体は重要です。

しかし、それ以上に重要なのは、**強いtoolを互いに邪魔させないこと**です。

今回の508件の重複parse failureは、その最小の実例でした。

precheck platformのKPIを「diagnostic総数」にすると失敗します。

見るべきなのは、たとえば次です。

```text
time to first actionable failure
false-positive / ignored-diagnostic rate
PR feedback latency
production escape rate
number of overlapping authorities
migration / config maintenance cost
```

この視点なら、Ruff、Pyrefly、Pydantic、Biome、Oxlint、tsc、Zod、prekはかなり良い材料です。

しかし価値を生むのはtool listではなく、**それらをquality control planeとして配置するarchitecture**です。

次の実験では、このarchitectureをTypeScriptの実際に状態の悪いrepositoryへ適用し、Biome/Oxlint/tsc/Zodについても同じ基準で実測します。