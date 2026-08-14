---
title: "2026年のprecheckは何を選ぶべきか。壊れたrepoで試して見えた標準構成"
emoji: "🧪"
type: "tech"
topics: ["python", "typescript", "ruff", "ci", "staticanalysis"]
published: false
---

Ruff、Pyrefly、ty、Pydantic、Biome、Oxlint、Zod、prek。

2026年の開発toolはかなり速くなった。

その結果、別の問題が出てきた。

**結局、どれを標準にすればいいのか。**

「何倍速い」「何rulesある」「何件見つけた」を並べれば比較表は作れる。しかしTech Leadが決めたいのはbenchmark一位ではない。

> このtoolchainを標準化したとき、変更速度を落とさず、productionへ流出する欠陥を減らし、数年後も運用できるか。

Googleが大規模static analysis platformのTricorderで扱ったのも、単体analyzerの性能だけではなかった。複数解析をどうdeveloper workflowへ統合し、実際に使われるsystemにするかが中心だった。

- Tricorder: https://research.google/pubs/tricorder-building-a-program-analysis-ecosystem/
- Google Engineering Practices: https://google.github.io/eng-practices/review/reviewer/standard.html

そこで今回は、実際にCIが壊れていた公開repositoryの固定commitへ2026年のprecheck候補を当てた。

対象:

```text
KAFKA2306/DeepCode
088059855d2c9187c51d674db02a06f70c37f087
```

実験:
https://github.com/KAFKA2306/articles/actions/runs/31812751114

最初の数字は派手だった。

```text
Ruff      1,076 findings
Pyrefly     723 findings
```

しかしraw diagnosticsを分類すると、Pyreflyの723件中508件が`parse-error`だった。Ruffにも508件の`invalid-syntax`があった。

つまり、

```text
1,076 + 723 = 1,799 independent defects
```

ではない。

同じ壊れた構文が複数の解析層へ伝播していた。

ここで問いを変えた。

**「最強のlinterはどれか」ではなく、「どのtoolを、どの責任の唯一のauthorityにして、どのタイミングで走らせるか」。**

これがprofessionalなtoolchain設計だと考える。

## 先に結論：2026年8月ならこうする

新規repositoryなら、第一候補は次だ。

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
  prek                  local hook runner
```

| concern | 第一候補 | 判断 |
|---|---|---|
| Python format/lint | **Ruff** | 強く採用 |
| Python type | **Pyrefly** | production標準候補 |
| Python typeの速度最優先 | **ty** | challenger。Beta |
| Python runtime contract | **Pydantic** | boundaryがある場合だけ |
| JS/TS format | **Biome** | formatter authority |
| JS/TS lint | **Oxlint** | lint authority |
| TypeScript type | **`tsc --noEmit`** | compiler authority |
| TS runtime contract | **Zod 4** | boundaryがある場合だけ |
| Git hook | **prek** | orchestration。品質規則そのものではない |

この構成が強い理由は、tool数ではない。

**責務が重なりにくい。**

## 「最強」を5軸で評価する

### 1. Semantic authority — 最後に誰を信じるか

同じ責務を複数toolに持たせると、結果が食い違った瞬間に運用コストが跳ね上がる。

```text
formatterは誰が正しい？
linterは誰が正しい？
type errorは誰が正しい？
runtime inputは誰が正しい？
```

これを一つずつ決める。

Pythonならformat/lintはRuff、typeはPyrefly。

TypeScriptならformatはBiome、lintはOxlint、typeの最終authorityはTypeScript compilerの`tsc`。

Oxlintは2026年7月にtype-aware lintingをstable化し、59/61のtypescript-eslint type-aware rulesをサポートしている。

https://oxc.rs/docs/guide/usage/linter/type-aware.html

一方、Oxlintの`typeCheck`は現行config referenceでexperimentalとされている。

https://oxc.rs/docs/guide/usage/linter/config-file-reference

だから現時点では、

```text
Oxlint = lint authority
tsc     = type authority
```

と分ける。

「toolを1個減らせる」ことより、**誰が最終判定者かが明確であること**を優先する。

### 2. Signal density — diagnostic数ではなく、直す価値を見る

今回のbroken repoで、件数ランキングが危険だと分かった。

Ruff 0.16.3は47 filesから1,076 findingsを返した。

| Ruff category | count |
|---|---:|
| `invalid-syntax` | **508** |
| `UP006` | 147 |
| `BLE001` | 143 |
| `I001` | 44 |
| `RUF010` | 42 |

Pyrefly 1.2.0は723 findingsだった。

| Pyrefly category | count |
|---|---:|
| `parse-error` | **508** |
| `unknown-name` | 108 |
| `missing-import` | 86 |
| `invalid-syntax` | 12 |
| `unexpected-keyword` | 9 |

最大categoryが508対508で一致した。

つまりPyreflyが「Ruffでは見えなかった723個の型欠陥」を追加発見したわけではない。

**前段のsyntax failureが、後段のtype diagnosticを汚染していた。**

CIやAI agentへ返すなら、こう分類した方がよい。

```text
ROOT / BLOCKING
  syntax: 508

DOWNSTREAM / lower confidence until root is repaired
  unknown-name: 108
  missing-import: 86
  ...
```

AI coding agent時代は特に、1,000件を列挙するより「最初のroot causeを直せば何件消えるか」を示す方が価値が高い。

### 3. Feedback latency — 速度は人間のflowを守るために使う

今回の単発Actions observationは次だった。

| tool | version | scan observation |
|---|---:|---:|
| Ruff | 0.16.3 | 99 ms |
| ty | 0.0.71 | 264 ms |
| Pyrefly | 1.2.0 | 361 ms |
| prek | 0.4.11 | 2,326 ms |
| pre-commit | 4.6.2 | 8,765 ms |

jobは別々のGitHub-hosted runner VMで動いたため、これは一般性能比ではない。

それでも設計上の示唆はある。

sub-second classのanalysisはdeveloper loopへ寄せられる。

Google Engineering Practicesも、code healthを守る一方でdeveloperが前進できることをtrade-offとして扱っている。

https://google.github.io/eng-practices/review/reviewer/standard.html

ここでやってはいけないのは、**速いtoolを全部pre-commitへ詰め込むこと**だ。

私ならfeedback topologyを分ける。

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

最速toolを選ぶ目的はCIランキングではない。

**feedbackが遅すぎてdeveloperやagentが別の仕事へ移る前に返すこと**だ。

### 4. Trust boundary — static typeが守れない入力を止める

PydanticとZodはlinterではない。

productionで壊れる値はcodeの外から来る。

```text
HTTP response
JSON / YAML
CSV
DB row
environment variable
AI model output
user input
```

static type checkerは、この値が実際にcontractを満たして届くことまでは保証しない。

そこでboundaryにruntime schemaを置く。

Python:

```text
external data
    ↓
Pydantic
    ↓
validated object
    ↓
application core
```

TypeScript:

```text
unknown
  ↓
Zod
  ↓
validated typed value
  ↓
application core
```

Zod 4はstableで、schema parsingとTypeScript type inferenceを同じschemaから扱える。

https://zod.dev/packages/zod

Pydanticもruntime validationを担う。

ただし全内部functionをPydantic/Zodで包むのは違う。

**Pydantic/Zodはrepository-wide precheckではなく、trust boundary contractだ。**

この違いを理解せずtool一覧へ並べると、設計が幼くなる。

### 5. Migration cost — replacementでoperational debtが減るか

Ruffが強い理由は速度だけではない。

RuffはFlake8系、isort、pyupgrade、autoflake等の広いlint責務を統合し、formatterも同じtoolchainに持つ。

https://docs.astral.sh/ruff/

つまり、

```text
Black
isort
Flake8
pyupgrade
...
```

を別々にversion管理するoperational costを圧縮できる。

TypeScript側も同じだ。

Biome自身にも500を超えるlint ruleとcross-file lintingがある。

https://biomejs.dev/blog/biome-v2-5/

しかし今回の標準案では、あえて

```text
Biome = formatter
Oxlint = linter
```

へ責務を絞る。

Biomeが弱いからではない。

**同じ責務のblocking authorityを二つ持たないためだ。**

professionalなplatform設計では、feature richnessよりgovernanceの単純さが勝つ場面がある。

## PythonはRuff + Pyrefly + Pydanticでよいか

### Ruff — 強く推奨

今回の実repoでも、最初に直すべきsyntax root failureを安い層で露出した。

さらにlint/format/import整理のtoolchainを圧縮できる。

新規Python repositoryなら第一候補にする。

### Pyrefly — production標準候補

Pyreflyは2026年5月にstable v1へ到達し、公式にproduction readyとされている。

https://pyrefly.org/blog/v1.0/

Meta側ではInstagramを含むproduction codebaseでの利用も説明されている。

今回の723件はparse failureの影響を強く受けたため、「検出力723件」というscoreにはしない。

それでもstable status、IDE/CLI、段階導入、real-world adoptionを考えると、production blocking type checkerとして選びやすい。

### ty — 重要なchallenger

今回のscan observationではty 0.0.71が264 ms、Pyrefly 1.2.0が361 msだった。

Astralのtyはincremental analysisを中心設計にしており、developer feedback latencyでは非常に有力だ。

https://astral.sh/blog/ty

ただし2026年8月現在もBeta。

Astral自身はmotivated usersへproduction利用を勧めているが、stable milestoneは今後だ。

今なら私は、

```text
production blocking authority → Pyrefly
shadow / evaluation / speed-sensitive editor → ty
```

から始める。

両方を永久にblocking CIで走らせることはしない。

### Pydantic — 採用。ただしboundaryだけ

API、設定、データfile、AI outputなど外部contractがあるrepoでは強い。

pure libraryでuntrusted runtime inputがほぼないなら、必須ではない。

「Python repoだからPydantic」は判断基準にならない。

## TypeScriptはBiome + Oxlint + tsc + Zodでよいか

### Biome formatter — 採用候補

Biome formatterはopinionatedでoptionを絞り、style debateを減らす思想を明示している。

https://biomejs.dev/formatter/

formatterの価値は美しさより、**人間がstyle reviewをしなくてよくなること**にある。

その用途ならかなり強い。

### Oxlint — 2026年に評価が上がった

type-aware lintingは2026年7月にstable化した。

https://oxc.rs/docs/guide/usage/linter/type-aware.html

ただしtype-aware modeはTypeScript 7系を前提にし、一部legacy tsconfig optionはmigrationが必要になる。

したがって、

```text
greenfield → 強く検討
legacy monorepo → compatibility auditを先に
```

となる。

### tsc --noEmit — まだ外さない

Oxlintは`--type-check`でcompiler diagnosticsも統合でき、公式docsでは別`tsc --noEmit`を置換できる形も示している。

しかし現行config referenceでは`typeCheck`はexperimentalだ。

そのため2026年8月時点では`tsc --noEmit`を残す。

https://www.typescriptlang.org/tsconfig/noEmit.html

理由は保守的だからではない。

**semantic authorityをexperimental featureへ移す便益が、まだ十分に大きくないからだ。**

### Zod — boundaryがあるなら採用

Zod 4はstable。

frontend/backend/API boundaryで`unknown`をvalidated dataへ変える用途なら自然だ。

内部domain objectまで全部Zod schemaで包む必要はない。

## prekはどうだったか

ここは実験で最も直接比較できた。

同じ`.pre-commit-config.yaml`を、`pre-commit 4.6.2`と`prek 0.4.11`へ渡した。

```text
pre-commit measured total  10,299 ms
prek measured total         2,619 ms
```

別runner VMなので「常に3.93倍速い」とは主張しない。

それより重要なのは生成patchだった。

```text
SHA-256(pre-commit patch)
30275602cf6b35644199d3a7fe949c038a10eaa9e6685074de4f7c8d62b36bf1

SHA-256(prek patch)
30275602cf6b35644199d3a7fe949c038a10eaa9e6685074de4f7c8d62b36bf1
```

このfixtureではbyte-identicalだった。

既存`.pre-commit-config.yaml`を保ちながらrunnerだけ差し替えるmigration pathとしては良い結果だ。

ただし設計上、prekは交換可能であるべきだ。

```text
quality policy != prek

quality policy =
  repository commands
  configs
  CI contract
```

hook runnerを変えただけで品質判定が変わるsystemにはしない。

## GreenfieldとLegacyでは答えが違う

### Greenfield Python

```text
Ruff
Pyrefly
Pydantic only at trust boundaries
prek for local orchestration
```

かなり強く推奨する。

### Greenfield TypeScript

```text
Biome formatter
Oxlint --type-aware
tsc --noEmit
Zod only at trust boundaries
prek if hook standardization is useful
```

2026年8月なら第一候補に置く。

### Legacy Python

Ruff migrationは有力。

しかし既にPyright/mypyが安定運用されているなら、Pyreflyへ移すこと自体をKPIにしない。

shadow runで、

```text
false positives
coverage
feedback latency
config migration cost
```

を測ってから切り替える。

### Legacy TypeScript

Oxlint導入前に、ESLint plugin dependencyとTypeScript/tsconfig compatibilityをinventoryする。

unsupported pluginやlegacy TypeScript requirementがあるrepoで、標準化のためだけにmigration scopeを膨らませるのは逆効果だ。

## 最後に：最強toolより、最強toolを邪魔させない

最初はこう考えていた。

```text
速いtoolを全部入れる
        ↓
たくさん見つかる
        ↓
品質が上がる
```

実測後は違う。

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

今回の508件の重複parse failureは、その小さな実例だった。

precheck platformのKPIを`diagnostic総数`にすると失敗する。

見るべきなのは、たとえば次だ。

```text
time to first actionable failure
ignored / false-positive rate
PR feedback latency
production escape rate
number of overlapping authorities
migration / config maintenance cost
```

この視点なら、Ruff、Pyrefly、Pydantic、Biome、Oxlint、tsc、Zod、prekはかなり良い材料だ。

しかし価値を生むのはtool listではない。

**それらをquality control planeとして配置するarchitectureである。**

次は状態の悪いTypeScript repositoryへ同じ方法を適用し、Biome / Oxlint / tsc / Zodについても、速度ではなくこの5軸で実測する。