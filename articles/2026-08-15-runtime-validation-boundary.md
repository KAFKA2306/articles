---
title: "型チェックを通っても、APIから届くJSONは実行時に検証する"
emoji: "🚧"
type: "tech"
topics: ["python", "typescript", "pydantic", "zod", "testing"]
published: false
---

**型がついているという理由で、外から来た値を信用するな。**

PythonとTypeScriptでruntime-boundary faultをそれぞれ一件ずつ試した。validationなしの経路では不正値が通り、PydanticとZodを置くと拒否した。型チェックのgreenと、ネットワーク越しの実値が正しいことは別問題だ。

汎用規律は **「信用できない入力は、内部の値へ変換する最初の境界で検証せよ」**。型注釈は開発時の約束であり、HTTPで受け取ったJSONが業務制約を守っている証拠ではない。今回確認したのは各言語一件で、すべての入力事故が防げるという実測ではない。

## 何が実際に起きたか

固定fixtureでは次の2ケースだけを測った。

| language | runtime validator | invalid input | validationなし |
|---|---|---|---|
| Python | Pydantic | reject | accept |
| TypeScript | Zod | reject | accept |

raw summary:
https://github.com/KAFKA2306/articles/blob/4c111d27ea193a72238d5ee97d145770cec2109e/benchmarks/verification-stack-v2/results/controlled/summary.json

各言語1件なので、Pydantic/Zodのaccuracyを100%と呼ぶ証拠ではない。確認できたのは、**static checkだけでは止まらずruntime validationで初めて止まるfailure classが両fixtureにあった**ことだ。

## なぜ型注釈だけでは足りないのか

TypeScript公式は、compile後に型をeraseしてJavaScriptを生成し、型によってruntime behaviorを変えないと説明している。

https://www.typescriptlang.org/docs/handbook/typescript-from-scratch.html

Zodは`parse` / `safeParse`で実際の値をschemaへ照合する。

https://zod.dev/basics

PythonでもPydanticの`validate_call()`は、function call前に実際の引数をparse/validateする。

https://docs.pydantic.dev/latest/concepts/validation_decorator/

つまり、static checkerとruntime validatorは代替関係ではない。

```text
external value
    ↓
runtime validation
    ↓
validated value
    ↓
typed application code
```

## 置く場所を迷ったら「最初の信用境界」を探す

runtime validationを置く候補は、外部世界から値が入る場所だ。

- HTTP request / webhook
- environment variables
- JSON / CSV / config file
- message queue
- LLM structured output

内部の深い関数で毎回validateする必要はない。**境界で1回、明示的に信用できる値へ変える**方が、失敗箇所と責務を狭くできる。

## 壊れた形と改善後

壊れやすい形:

```text
request.json()
  ↓
型注釈を付ける
  ↓
business logic
```

改善後:

```text
request.json()
  ↓
schema.parse / model validation
  ↓
validated value
  ↓
business logic
```

## 導入するときの6問

1. 外部から値が入る入口はどこか
2. 入口では値を`unknown`相当として扱っているか
3. schema/modelは境界直後にあるか
4. validation後の値だけを内部へ渡しているか
5. invalid payloadのregression testが最低1件あるか
6. static checkerがgreenでも、そのruntime testを削除していないか

まず実際の入力口と、有効な入力を一件用意する。記事の試験では、正の整数が必要な `count` に対して、正常な `{"count": 2}` と、JSONとしては正しい `{"count": -1}` を同じ入口へ渡した。手元でも、正常値が通ることと、業務上無効な値が内部の処理へ入る前に拒否されることを組にして確かめる。

## 正常入力と不正入力を同じ境界に渡す

PythonとPydantic v2なら、本文の`count`を次のコードで再現できる。これは**独立した最小再現例**で、記事の元ベンチマークを再実行したログではない。

```python
from pydantic import BaseModel, Field, ValidationError

class Request(BaseModel):
    count: int = Field(gt=0)

assert Request.model_validate({"count": 2}).count == 2

try:
    Request.model_validate({"count": -1})
except ValidationError:
    print("invalid count rejected")
else:
    raise AssertionError("invalid count accepted")
```

`{"count": -1}`は正しいJSONで、`int`型としても成立するが、業務要件の「正の整数」を満たさない。HTTP入口ならボディ取得直後に`Request.model_validate`を呼び、**検証済みの値だけ**を内部処理へ渡す。正常値を通す検査と、負の値を拒否する検査は両方必要。Pydanticが未導入なら依存と版を先に決め、未実行を実測済みと記録しない。[Pydantic Field](https://docs.pydantic.dev/latest/concepts/fields/)

## 証拠の境界

この記事は、Pydantic/Zodがすべての入力事故を防ぐとは主張しない。schema自体が間違っていればvalidationも間違うし、今回測ったfaultは各言語1件だけだ。

それでも運用判断は変えられる。

**型チェックのgreenを「外部入力も検証済み」と読み替えない。外から来る値は、最初の信用境界で実際の値を検証する。**

## 転用と撤回の条件

HTTPに限らず、CSV取り込み、外部DB、AIが生成したJSONにも、検証しない値が内部の前提を破るなら同じ構造がある。これは**応用仮説**であって各経路での実測ではない。正常入力を通し、意図的に不正な入力を拒否する一組を試してから採用する。

すべての値が同じプロセスの検証済み構造体から生成され、追加の実行時検証で異常を検出できないと実測できた場合は、冗長な境界を減らせる。検証schema自体が誤っていれば、この規律も安全を保証しない。**検証の回数ではなく、値を信用する理由を固定する。**
