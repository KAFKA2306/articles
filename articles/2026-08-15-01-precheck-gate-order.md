---
title: "1,799件のエラーは1,799個の欠陥ではない"
emoji: "🧪"
type: "tech"
topics: ["python", "typescript", "ruff", "ci", "staticanalysis"]
published: false
---

AIでコードを書く速度が上がると、品質toolを増やしたくなる。

Ruff、Pyrefly、ty、Pydantic、Biome、Oxlint、`tsc`、Zod、prek。候補はいくらでもある。

しかし、toolを増やせば独立した欠陥がその分だけ見つかるとは限らない。

実際に壊れた公開repositoryへ複数のprecheckを当てると、最初に見えた数字はこうだった。

```text
Ruff      1,076 findings
Pyrefly     723 findings
----------------------
raw sum   1,799
```

この `1,799` を「1,799個の欠陥」と読むのは間違いだった。

Pyreflyの723件のうち508件は `parse-error`。Ruffにも508件の `invalid-syntax` があった。同じ壊れた構文が、後段の解析面へ伝播していた。

この記事で扱うのは「どのlinterが最強か」ではない。

**品質toolを何個入れるかではなく、各toolにどの判定権限を持たせ、どの順番で結果を信じるか**である。

## まず、何が実証済みか

実験対象は公開repositoryの固定commitである。

```text
repository: KAFKA2306/DeepCode
commit:     088059855d2c9187c51d674db02a06f70c37f087
runner:     Ubuntu 24.04.4
Python:     3.12.13
uv:         0.12.4
```

実験run:

https://github.com/KAFKA2306/articles/actions/runs/31812751114

再現性のため、対象commitを固定した。ここから先で「観測した」と書く数値は、このrunに由来する。

### 観測1: Ruffは1,076件を返した

Ruff 0.16.3は47 filesから1,076件を返した。

| code | count |
|---|---:|
| `invalid-syntax` | 508 |
| `UP006` | 147 |
| `BLE001` | 143 |
| `I001` | 44 |
| `RUF010` | 42 |
| `UP045` | 33 |
| `UP035` | 29 |
| `S110` | 28 |
| `ASYNC230` | 21 |

508件のsyntax findingは14 filesに集中していた。

### 観測2: Pyreflyは723件を返した

Pyrefly 1.2.0の内訳は次だった。

| name | count |
|---|---:|
| `parse-error` | 508 |
| `unknown-name` | 108 |
| `missing-import` | 86 |
| `invalid-syntax` | 12 |
| `unexpected-keyword` | 9 |
| **total** | **723** |

ここで重要なのは、Ruffの `invalid-syntax=508` とPyreflyの `parse-error=508` が一致したことだ。

この一致だけから「同一diagnosticが1対1対応する」とまでは断定できない。しかし少なくとも、

```text
1,076 + 723 = 1,799 independent defects
```

とは扱えない。

大量のsyntax failureが存在する状態で、後段のtype checkerが返すdiagnosticを独立欠陥として単純加算する根拠がないからだ。

### 観測3: 実行時間も順位表にはしない

同じrunで得られた単発観測は以下だった。

| tool | version | install_ms | scan_ms | exit |
|---|---:|---:|---:|---:|
| Ruff | 0.16.3 | 356 | 99 | 1 |
| ty | 0.0.71 | 683 | 264 | 1 |
| Pyrefly | 1.2.0 | 326 | 361 | 1 |
| prek | 0.4.11 | 293 | 2,326 | 1 |
| pre-commit | 4.6.2 | 1,534 | 8,765 | 1 |

ただしjobは別々のGitHub-hosted runner VMで動いている。pre-commit / prekのscan intervalにはhook environment準備も含まれる。

したがって、この記事ではこの数字を一般的な性能ランキングには使わない。

観測できたのは「このfixture、このrunではこうだった」までである。

### 観測4: pre-commitとprekは同じpatchを作った

同じ `.pre-commit-config.yaml` をpre-commit 4.6.2とprek 0.4.11で実行したところ、working-tree patchのSHA-256は一致した。

```text
pre-commit.diff.patch
30275602cf6b35644199d3a7fe949c038a10eaa9e6685074de4f7c8d62b36bf1

prek.diff.patch
30275602cf6b35644199d3a7fe949c038a10eaa9e6685074de4f7c8d62b36bf1
```

これは「prekは常にpre-commitと完全互換」という証明ではない。

このrepository、この設定、このrunでは同じpatchになった、という限定された互換性証拠である。

## 次に、各toolは何をauthorityとして持つのか

品質toolを選ぶ前に、責任を分解する。

同じ責任にblocking authorityを複数置くと、結果が食い違ったときに「どちらを直せばmergeできるのか」が曖昧になる。

そこで、tool名ではなく判定対象から見る。

| concern | authorityとして持たせるもの | authorityにしないもの |
|---|---|---|
| source syntax / Python lint / format | Ruff | runtime data validation |
| Python static types | Pyreflyなどのtype checker | formatter |
| Python runtime input | Pydantic | repository-wide lint |
| JS/TS formatting | Biome formatterなど | type correctness |
| JS/TS lint | Oxlintなど | runtime schema |
| TypeScript compiler types | `tsc --noEmit` | formatter |
| TS runtime input | Zod | compiler diagnostics |
| local hook execution | prek / pre-commit | 品質規則そのもの |
| monorepo task graph | Nx / Turborepo | source semantics |

ここからは、実験で直接測定した事実ではなく、各projectの公式documentが定義する責任範囲を使う。

### Ruff: Python source hygieneのauthority

Ruff公式は、linterとformatterを同じtoolchainとして提供している。

- https://docs.astral.sh/ruff/
- https://docs.astral.sh/ruff/linter/
- https://docs.astral.sh/ruff/formatter/

今回のfixtureでは、type checkerより前に大量のinvalid syntaxを露出した。

だから「Ruffのfinding数が多いから勝ち」ではない。

**parse可能なsourceへ戻す最初のgateとして使える**ことが重要である。

### Pyrefly / ty: Python static semanticsのauthority候補

Pyreflyは2026年5月にv1へ到達し、公式にproduction readyと説明している。

https://pyrefly.org/blog/v1.0/

一方、tyの公式documentationは現在Betaとして扱っている。

https://docs.astral.sh/ty/

この違いはbenchmark順位より重要だ。

blocking CIのauthorityを決めるなら、速度だけでなくstability boundaryも判断材料になる。

今回の実験で測ったのはPyreflyとtyの壊れたfixture上の挙動だけであり、「どちらがより正確か」は実証していない。

### Pydantic: static type checkerではなくruntime boundary

Pydanticの責任は、実行時に入ってくる値をschema/typeに沿ってvalidateすることだ。

https://docs.pydantic.dev/latest/concepts/validators/

たとえば、

```text
HTTP / JSON / CSV / env / AI output
              ↓
          Pydantic
              ↓
      application core
```

の境界で使う。

内部のすべてのfunctionをPydanticで包むこととは別問題である。

### Biome / Oxlint / tsc / Zod: TypeScriptでも責任を混ぜない

今回のbroken-repo実験はPython repositoryなので、以下は**実測結果ではない**。公式仕様上の責任分解だけを書く。

Biome formatter:
https://biomejs.dev/formatter/

Oxlint:
https://oxc.rs/docs/guide/usage/linter/

TypeScript `noEmit`:
https://www.typescriptlang.org/tsconfig/noEmit.html

Zod:
https://zod.dev/basics

この4つは同じ問題を解いていない。

```text
Biome      formatting
Oxlint     lint semantics
tsc        compiler/type semantics
Zod        runtime unknown input
```

Oxlintにはtype-aware lintingがあり、公式documentationでは2026年7月にstable化したと説明されている。

https://oxc.rs/docs/guide/usage/linter/type-aware.html

一方、現行config referenceでは `typeCheck` はexperimentalと記載されている。

https://oxc.rs/docs/guide/usage/linter/config-file-reference

そのため、現時点で「Oxlintを入れたので `tsc --noEmit` を外せる」と一般化はしない。

repositoryごとにcompiler diagnostic parityを検証してからauthorityを移すべきである。

### prek: authorityではなくtrigger

prek公式は、既存 `.pre-commit-config.yaml` とのcompatibilityを説明している。

https://prek.j178.dev/compatibility/

しかしhook runnerはlint ruleやtype semanticsの所有者ではない。

```text
prek
  ├─ Ruffを起動する
  ├─ type checkerを起動する
  └─ repository commandを起動する
```

という位置づけであり、quality policyのauthorityは各repository command / config / CI側に残す方が交換可能性が高い。

### Nx / Turborepo: source checkerではなくgraph authority

monorepoになると、別のauthorityが必要になる。

「どのprojectがどのprojectに依存するか」「変更でどのtaskを再実行するか」「何をcacheできるか」というworkspace graphである。

Nx:

- https://nx.dev/docs/features/explore-graph
- https://nx.dev/docs/features/ci-features/affected
- https://nx.dev/docs/features/cache-task-results

Turborepo:

- https://turborepo.dev/docs/core-concepts/package-and-task-graph
- https://turborepo.dev/docs/crafting-your-repository/caching

小さなsingle-project repoにNxやTurborepoを追加しても、Ruffや`tsc`の代わりにはならない。

解いている問題が違う。

## 読者が判断できるべきこと

ここまでの情報から、toolの採用判断は「人気」「速さ」「finding数」ではなく、次の順で行える。

### 1. いま壊れている最上流の層はどこか

今回のfixtureならsyntaxだった。

大量のparse failureが残る間は、下流diagnosticの総数をKPIにしない。

```text
syntax broken
    ↓
source names / imports / types が二次的に乱れる
    ↓
raw finding countが膨らむ
```

最初に直すべき層が変われば、後段のsignalも変わる。

### 2. その責任のblocking authorityは誰か

たとえばPythonなら、

```text
format/lint → Ruff
static type → 1つのtype checker
runtime input → Pydantic where needed
```

のように責務を分ける。

重要なのは具体的なvendor名より、**同じ責任の最終判定者を増殖させないこと**だ。

### 3. そのtoolは「検査」か「起動」か「graph制御」か

prekはtriggerであり、Ruffはsource analyzerであり、Nx/Turborepoはworkspace graphを扱う。

これらを同じ比較表の1列へ並べて「最強」を決めても意味が薄い。

### 4. 未実証の推奨を実測値のように書いていないか

今回直接測定したのは次だけである。

```text
Ruff 0.16.3
Pyrefly 1.2.0
ty 0.0.71
prek 0.4.11
pre-commit 4.6.2
```

Pydantic、Biome、Oxlint、`tsc --noEmit`、Zod、Nx、Turborepoについては、この記事では公式仕様から責任範囲を整理しただけである。

「公式に機能がある」と「このrepositoryで有効だった」は別のclaimとして扱う。

## 壊れたrepoのprecheckは、直列チェーンではなくstaged gateにする

今回の観測から再現可能なのは、toolの固定セットではなくgateの考え方である。

### Gate 0: sourceがparseできるか

syntax errorが大量にあるなら、まずここで止める。

下流toolを禁止する必要はないが、そのdiagnostic数を独立欠陥として扱わない。

### Gate 1: deterministic source hygiene

parse可能になった後でformatter / lintを安定させる。

PythonならRuff、JS/TSなら選んだformatter/linter authorityを使う。

### Gate 2: static semantics

import/dependency contextを有効にした上でtype checkingする。

今回Pyreflyには `missing-import=86` が含まれた。zero-dependency discovery environmentの影響があるため、dependency contextを直さずに「86個のcode defect」とは断定できない。

### Gate 3: runtime boundaries

外部入力がある箇所だけ、PydanticやZodのfixture / contract testを置く。

source lintとruntime validationを同じdiagnosticランキングに混ぜない。

### Gate 4: tests / integration / graph-aware CI

最後にunit / integration / E2E、必要ならaffected executionやcacheを使う。

ここでNxやTurborepoが必要になるのは、workspace graphの問題が実在するときだけである。

## 再現方法

同じ観測を確認したい場合は、対象commitを固定し、各toolのversionとcommandを記録する。

今回のbenchmark harnessはPR #115にある。

https://github.com/KAFKA2306/articles/pull/115

最低限、保存するべき証拠は以下である。

```text
target repository
target commit SHA
tool version
exact command
exit code
machine-readable diagnostics
working-tree diff
runner / language runtime
```

そして、raw totalだけでなくdiagnostic categoryを分類する。

```python
# 例: machine-readable diagnosticsをcategoryごとに数える
from collections import Counter

counts = Counter(item["code"] for item in diagnostics)
print(counts.most_common())
```

目的はtool同士の件数勝負ではない。

**上流failureが下流signalをどれだけ汚しているかを見つけること**である。

## 次に測るべき実験

今回の結果だけでは、type checkerの独立検出力は比較できない。

次に必要なのは、同じfrozen targetから段階的にfailure sourceを除去する実験である。

```text
A. 元のbroken commit
B. syntaxだけ修復
C. declared dependenciesも導入
D. type checker再実行
```

A→BでPyreflyの508 parse errorsがどう変わるか。

B→Cで `unknown-name` / `missing-import` がどこまで減るか。

ここまで測れば、はじめて「syntax由来」「environment由来」「残ったstatic semantic defect」を分離できる。

TypeScript側も別のunhealthy repositoryでBiome / Oxlint / `tsc --noEmit` / Zodを実測する必要がある。

## 結論

品質stackを作るとき、toolを増やすこと自体は難しくない。

難しいのは、出てきたsignalをどう解釈するかである。

今回の公開実験で確認できたのは、Ruff 1,076件とPyrefly 723件を足して1,799 independent defectsとは扱えない、ということだった。Pyreflyの723件中508件はparse errorで、Ruffにも508件のinvalid syntaxがあった。

だからprecheck設計で最初に決めるべきものは製品一覧ではない。

**どのfailure layerを先に解消し、各責任について誰の判定をauthorityとして扱うか。**

それが決まってから、Ruff、Pyrefly、Biome、Oxlint、prek、Nx、Turborepoを選べばよい。

toolは増やせる。

判定権限は、むしろ減らした方が運用しやすい。

## 一次情報

- 実験run: https://github.com/KAFKA2306/articles/actions/runs/31812751114
- frozen target: https://github.com/KAFKA2306/DeepCode/commit/088059855d2c9187c51d674db02a06f70c37f087
- Google Tricorder: https://research.google/pubs/tricorder-building-a-program-analysis-ecosystem/
- Ruff: https://docs.astral.sh/ruff/
- Pyrefly v1: https://pyrefly.org/blog/v1.0/
- ty: https://docs.astral.sh/ty/
- Pydantic validators: https://docs.pydantic.dev/latest/concepts/validators/
- Biome formatter: https://biomejs.dev/formatter/
- Oxlint: https://oxc.rs/docs/guide/usage/linter/
- Oxlint type-aware linting: https://oxc.rs/docs/guide/usage/linter/type-aware.html
- TypeScript `noEmit`: https://www.typescriptlang.org/tsconfig/noEmit.html
- Zod basics: https://zod.dev/basics
- prek compatibility: https://prek.j178.dev/compatibility/
- Nx project graph: https://nx.dev/docs/features/explore-graph
- Turborepo task graph: https://turborepo.dev/docs/core-concepts/package-and-task-graph
