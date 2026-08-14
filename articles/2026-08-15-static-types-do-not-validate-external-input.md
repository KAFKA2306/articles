---
title: "型チェックが通っても、外部入力は検証されていない"
emoji: "🚧"
type: "tech"
topics: ["python", "typescript", "pydantic", "zod", "testing"]
published: false
---

型チェッカーをstrictにした。CIもgreenになった。ではAPI、JSON、環境変数、ファイルから来る値も安全になったのか。

**ならない。少なくとも、今回固定したPython/TypeScriptの2つのruntime-boundary mutantでは、static authorityとruntime authorityは別の仕事だった。**

これは「PydanticやZodを使おう」という製品記事ではない。どのgateに最終判定権を持たせるか、という話だ。

## 先にground truthを固定した

比較後に都合のよい失敗例を選ばないため、Verification Stack v2ではtool実行前にfixtureを凍結した。

- `PY-RUNTIME-001`: 外部由来の値がruntime contractに違反する。ただしparse前のコード自体はsyntax/type上受理可能。
- `TS-RUNTIME-001`: `unknown` の外部payloadがcompileを通るがruntime schemaに違反する。
- 1 mutant = 1 root fault。
- raw diagnostic数はdefect数として数えない。
- runtime validatorをlinterやtype checkerとの「勝敗」には使わない。

Protocol: https://github.com/KAFKA2306/articles/blob/4c111d27ea193a72238d5ee97d145770cec2109e/benchmarks/verification-stack-v2/PROTOCOL.md

Fixture design: https://github.com/KAFKA2306/articles/blob/4c111d27ea193a72238d5ee97d145770cec2109e/benchmarks/verification-stack-v2/FIXTURE_DESIGN.md

## 観測結果は2対2だった

controlled resultでは、runtime boundaryだけを見ると次の結果になった。

| mutant | runtime authority | detected | unvalidated control |
|---|---|---:|---:|
| `PY-RUNTIME-001` | Pydantic | 1 / 1 | 0 / 1 |
| `TS-RUNTIME-001` | Zod | 1 / 1 | 0 / 1 |

この数字を「Pydantic/Zodのaccuracy 100%」とは読まない。各言語1 mutantしかないからだ。ここで実証したのはもっと狭い。

**静的に受理可能な外部payloadでも、runtime contractを実行すれば拒否できるfailure classが、PythonとTypeScriptの両fixtureで1件ずつ存在した。**

Raw summary: https://github.com/KAFKA2306/articles/blob/4c111d27ea193a72238d5ee97d145770cec2109e/benchmarks/verification-stack-v2/results/controlled/summary.json

## TypeScriptはruntimeで型を持ち続けない

TypeScript公式Handbookは、compilerがcheckingを終えると型をeraseしてJavaScriptを生成し、型推論によってruntime behaviorを変えないと説明している。

https://www.typescriptlang.org/docs/handbook/typescript-from-scratch.html

つまり、`unknown` を正しく置くことは重要だが、それだけでは外部payloadをruntimeで検証する処理にはならない。

Zodは公式に「TypeScript-first validation library」とされ、schemaでuntrusted dataをparse/validateする例を示している。

https://zod.dev/

したがって責務はこう分かれる。

```text
external bytes / JSON
        |
        v
runtime schema  <-- 実際に来た値を判定するauthority
        |
        v
validated value
        |
        v
static type checker / compiler <-- コード上の型整合性を判定するauthority
```

これはどちらか一方を選ぶ競争ではない。

## Pythonでも「Pydanticを理解する型チェッカー」と「Pydanticを実行する」は別

ここは特に混同しやすい。

Pyreflyは現在、Pydantic v2のbuilt-in supportを持ち、`BaseModel`、`Field`、strict/lax modeなどを静的解析へ反映する。公式docs自身も、この機能をstatic type checking / IDE integrationとして説明し、Pydanticにはruntime data validationがあると分けている。

https://pyrefly.org/en/docs/pydantic/

一方Pydanticの`validate_call()`は、実際に渡された引数をfunction call前にparse/validateし、失敗時には`ValidationError`を発生させる。

https://docs.pydantic.dev/latest/concepts/validation_decorator/

したがって「type checkerがPydanticを理解するようになったからruntime validationを削除できる」とは、この証拠からは言えない。

## 3つの物語を同じ証拠で潰した

結果を見たあと、少なくとも次の3命題を競合させた。

1. **runtime validatorはtype checkerより優秀だ** — 棄却。責務が違い、head-to-headのground truthを置いていない。
2. **static checkerが強くなればruntime validatorは不要になる** — 今回の2 mutantとTypeScriptのerased-types契約に反する。
3. **外部入力の最終authorityはruntime boundaryに置く** — 今回の証拠と矛盾せず、実装判断を変える。

残ったのは3だけだった。

## gate orderingは「速い順」ではなく「authority順」に考える

実務では、source hygiene、static semantics、runtime boundaryを一つの巨大な`quality` gateとして扱うと責務が曖昧になる。

今回の結果から言える最小の設計は次だ。

```text
source/lint gate
    -> static type gate
        -> runtime boundary validation
            -> tests / application behavior
```

これは必ずこの順番でprocessを直列実行せよ、という意味ではない。CIでは並列化できる。重要なのは**失敗を誰の責任として扱うか**だ。

- Ruff/Biome/Oxlint: source/lint/formatのうち有効化したpolicy。
- Pyright/Pyrefly/mypy/ty/`tsc`: static semantics/type consistency。
- Pydantic/Zod: 実行時に到着した外部値のcontract。
- hook runner: これらを起動するtriggerでありpolicyそのものではない。

Ruff公式もlinterとformatterを独立して利用できると明記している。

https://docs.astral.sh/ruff/faq/

Pyrightも`off/basic/standard/strict`というtype-checking rule setを提供するstatic checkerである。

https://github.com/microsoft/pyright/blob/main/docs/configuration.md

## 再現する

この主張を追試するなら、製品を増やす前に1つのboundary mutantを作る。

1. 外部入力を`unknown`相当として受け取る。
2. コード自体はstatic checkを通る状態にする。
3. schemaに違反する値を1つだけ入れる。
4. static gateとruntime schemaを別々に実行する。
5. mutantのroot faultを事前に1つへ固定する。
6. diagnostic件数ではなく、そのroot faultを正しく止めたかだけを記録する。

このrepositoryではfixture、protocol、raw summaryを固定commitで残しているため、そのまま監査できる。

https://github.com/KAFKA2306/articles/tree/4c111d27ea193a72238d5ee97d145770cec2109e/benchmarks/verification-stack-v2

## 何を測っていないか

今回のruntime corpusはPython 1件、TypeScript 1件だけである。複雑なnested schema、custom validator、coercion、performance、error UX、schema evolution、API compatibilityは比較していない。PydanticとZodを相互比較もしていない。

また、real repository stageはground truthが未知なのでrecall証明には使っていない。Protocolでもreal repoはcompatibility、latency、migration frictionなどのexternal validityに限定している。

## 何が起きれば結論を反転するか

このrecommendationは永遠の原則ではない。

**実際の外部payloadをruntimeで観測し、その値がcontractを満たすかをstatic authorityだけで完全に判定できる実行モデル**が対象systemに存在し、同じpredeclared runtime mutantsを追加validatorなしで拒否できるなら、runtime authorityを別に置く理由は弱くなる。

今回、そのcounterfactualは観測されなかった。

だから現時点の判断は単純だ。

**型チェックがgreenでも、外部入力のgateまでgreenとは限らない。外部値を受け取る場所には、runtime contractを実行する別のauthorityを置く。**
