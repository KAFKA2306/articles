---
title: "型チェックはgreen。それでも壊れたJSONは通る"
emoji: "🚧"
type: "tech"
topics: ["python", "typescript", "pydantic", "zod", "testing"]
published: false
---

型チェックが全部greenでも、APIから壊れたJSONが来れば、その値は普通に実行時へ入ってくる。

今回、PythonとTypeScriptでruntime-boundary faultを1件ずつ固定した。結果は単純だった。**validationなしでは両方通過し、Pydantic/Zodを置いた経路だけが拒否した。**

つまり、型安全に見えるコードでも「外から来る値をどこで信用するか」を決めていなければ、最後の境界が抜ける。

この記事で持ち帰る判断は1つだけだ。

**外部値は、入ってきた瞬間に`unknown → validated value`へ変換する。**

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

この6問で、型チェックと入力検証を同じ「型安全」という言葉に潰さずに済む。

## 証拠の境界

この記事は、Pydantic/Zodがすべての入力事故を防ぐとは主張しない。schema自体が間違っていればvalidationも間違うし、今回測ったfaultは各言語1件だけだ。

それでも運用判断は変えられる。

**型チェックのgreenを「外部入力も検証済み」と読み替えない。外から来る値は、最初の信用境界で実際の値を検証する。**