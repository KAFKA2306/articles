---
title: "型チェックが通っても、外部入力は安全にならない"
emoji: "🚧"
type: "tech"
topics: ["python", "typescript", "pydantic", "zod", "testing"]
published: false
---

CIで型チェックがgreenでも、API、JSON、環境変数、ファイルから来る値まで安全になったわけではない。

今回、PythonとTypeScriptで外部入力のfailureを1件ずつ固定し、static checkとruntime validationを分けて観測した。PydanticとZodは各runtime mutantを拒否し、validationなしのcontrol pathは拒否しなかった。

ここから得た実務上の結論は、製品選びではない。

> **外部入力は、runtime boundaryで最後に検証する。**

## どこで事故が起きるのか

典型例はこれだ。

```text
HTTP / JSON / env / file
        ↓
アプリ内部の型付きコード
```

内部コードが型安全でも、境界から入る値は実行時にしか存在しない。

TypeScript公式は、compile後にtype annotationをeraseしてJavaScriptを生成すると説明している。

https://www.typescriptlang.org/docs/handbook/typescript-from-scratch.html

つまり`unknown`を正しく扱うことと、その値をruntimeで検証することは別である。

Zodはruntime schema validationを提供する。

https://zod.dev/

Pythonでも同じ分離がある。PyreflyはPydantic v2を静的解析できるが、Pydantic自身のruntime validationとは別の責務だ。

https://pyrefly.org/en/docs/pydantic/
https://docs.pydantic.dev/latest/concepts/validation_decorator/

## 固定fixtureで何が起きたか

今回のcontrolled fixtureでは次の2ケースだけを扱った。

- Python: staticに受理可能だがruntime contractへ違反する外部値
- TypeScript: compile可能な`unknown` payloadだがruntime schemaへ違反する値

結果は次だった。

| language | runtime validator | fixed runtime fault | unvalidated control |
|---|---|---:|---:|
| Python | Pydantic | reject | accept |
| TypeScript | Zod | reject | accept |

summary:
https://github.com/KAFKA2306/articles/blob/4c111d27ea193a72238d5ee97d145770cec2109e/benchmarks/verification-stack-v2/results/controlled/summary.json

各言語1件なので「accuracy 100%」とは言わない。実証したのは、**static passでは止まらず、runtime contractで初めて止められるfailure classが両fixtureに存在した**ことだけだ。

## 壊れた設計

```text
request.json()
  ↓
型注釈を付ける
  ↓
そのままbusiness logicへ渡す
```

型注釈は入力値そのものを検証しない。

## 改善後

```text
external input
  ↓
runtime schema / parser
  ↓
validated value
  ↓
application code + static type checker
```

ここでruntime validatorとtype checkerは競合しない。

- static checker: コード上の型整合性
- runtime validator: 実際に到着した値のcontract

## どこに置くべきか

外部入力の直後に置く。

対象は最低でも次だ。

- HTTP request body
- webhook payload
- environment variables
- config file
- CSV / JSON import
- message queue payload
- LLM structured output

内部処理の奥深くでvalidationするより、境界直後でunknownをvalidated valueへ変換する方がfailure locationを狭くできる。

## 読者向けチェックリスト

1. 外部から入る値を列挙する
2. 各入力が最初に`unknown`として扱われる場所を探す
3. runtime schemaを境界直後に置く
4. validation後の型だけを内部へ渡す
5. invalid payloadのtestを1件以上固定する
6. static checkerがgreenでもruntime boundary testを削除しない

## 証拠の境界

この記事は「Pydantic/Zodがすべての入力事故を防ぐ」とは言わない。今回測ったruntime mutantは各言語1件だけで、schema designの完全性も測っていない。

言えるのはもっと実務的なことだ。

**型チェックのgreenを、外部入力のvalidation済みと読み替えない。**

外から来る値には、実際の値を判定するruntime authorityを置く。