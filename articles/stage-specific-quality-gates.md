---
title: "同じ品質条件を2回判定しない。AI時代の品質ゲートは「追加」より「一本化」する"
emoji: "🚦"
type: "tech"
topics: ["typescript", "githubactions", "testing", "ai"]
published: false
---

品質を上げようとすると、検査を追加したくなる。

lint、audit、smoke、verifier、harness、score、receipt。

一つずつには理由がある。しかしAIが高速に実装を足せるようになると、別の失敗が起きる。

**同じ事実を複数の場所で判定し始める。**

`yt3` の現在の公開コードを見直すと、その兆候が実際にある。

## 現在のコードには、すでに2つの「通った」がある

`ScriptIntegrityLinter` は各checkについて `OK / WARN / FAIL` を返し、同時に `score` と `passed` も返す。

現在の `passed` は次で決まる。

```ts
passed: totalScore >= 70 && !checks.some((c) => c.status === "FAIL")
```

一次情報:

- https://github.com/KAFKA2306/yt3/blob/main/src/io/utils/qa/script_linter.ts

ところがcontent生成側は、その `passed` をそのまま使わない。

`Artifact` layerを除外したうえで、残ったcheckに `FAIL` がないかをもう一度計算している。

```ts
const relevantChecks = auditRes.checks.filter(
  (c) => c.layer !== "Artifact",
);
const passed = relevantChecks.every((c) => c.status !== "FAIL");
```

一次情報:

- https://github.com/KAFKA2306/yt3/blob/main/src/domain/agents/content.ts

つまり同じlinter resultに対して、少なくとも次の2種類の判定が存在する。

```text
linter自身
  score >= 70 AND FAILなし

content生成
  Artifactを除いてFAILなし
```

これは直ちにbugという意味ではない。生成途中と公開前でblocking条件が違うこと自体はあり得る。

問題は、**その差を表現するために判定ロジックを何層増やすか**である。

## 以前の案は、さらに `GatePolicy` を足そうとしていた

この記事の旧版では、ここへ新しい `GatePolicy` abstractionを追加し、工程ごとに `minScore` や `blockOn` を設定する案を出していた。

それは局所的にはきれいに見える。

しかしrepository全体を「AIが増やした判断コスト」という観点で見直すと、優先順位が逆だった。

現在すでに、

- linterがcheckを作る
- linterが全体 `passed` を作る
- content側が別の `passed` を作る
- retryがその結果を次のpromptへ戻す

という経路がある。

ここへ新しいpolicy objectを足す前に、**どこを唯一の判定場所にするか**を決めるべきだった。

## まず「観測」と「停止」を分ける。ただし仕組みは増やさない

必要なのは新しいframeworkではない。

最小形は二つしかない。

```text
観測
  checkごとの事実を返す

停止
  その工程を続けるか決める
```

たとえばlinterを観測器として使うなら、返す中心は `checks` と必要なら `score` でよい。

```ts
type AuditResult = {
  score: number;
  checks: Array<{
    layer: string;
    status: "OK" | "WARN" | "FAIL";
    message: string;
  }>;
};
```

そしてblocking条件は、実際に停止する境界で一度だけ決める。

```ts
const blocking = result.checks.some((c) => c.status === "FAIL");
if (blocking) throw new Error("quality check failed");
```

逆に、linter自身が最終合否まで所有する設計を選ぶなら、利用側は `auditRes.passed` を再計算しない。

大事なのはどちらが絶対に正しいかではない。

**同じ意味のbooleanを複数箇所で作らないこと**だ。

## WARNを止めるかどうかより、所有者が何人いるかを見る

旧版では「生成中はWARNを許容し、公開前は厳しくする」というstage-specific policyを中心にしていた。

この考え自体は使える。

ただし、stageごとの差を理由に次々と

```text
linter
↓
policy
↓
gate
↓
audit
↓
CI adapter
```

を作ると、品質を証明する仕組みそのものが大きくなる。

先に確認すべきなのは次の三点だけでよい。

1. 同じ事実をどこで観測しているか。
2. その事実から停止を決める場所はどこか。
3. 別の場所でも同じ停止条件を再計算していないか。

工程差が本当に必要なら、既存の一つの判定点へ最小の入力差として表現する。

新しいclass、score体系、policy vocabularyを作るのは、その方法で表現できないことが確認できてからでよい。

## retryも品質ゲートの一部として監査する

`content.ts` は現在、生成を最大3回試行する。

- https://github.com/KAFKA2306/yt3/blob/main/src/domain/agents/content.ts

retryは生成AIでは有効なことがあるが、「失敗したら再試行する」だけでは原因を隠すこともある。

たとえば同じ決定的なvalidation failureを3回繰り返しても、正しさは増えない。

したがって監査では、retry回数そのものではなく次を見る。

```text
再試行で入力または条件が変わるか
変わらないなら同じ失敗を繰り返していないか
最終失敗が元の原因を保持しているか
```

`yt3` のcontent生成は、失敗したcheckを `lastErrorFeedback` として次試行へ渡しているため、単純な同一入力再実行ではない。一方で、このfeedback経路も含めて「本当に3回必要か」は実測で判断すべきである。

## GitHub Actionsでは最後だけbinaryにする

CIのjobは最終的にsuccess / failureへ落とす必要がある。

GitHub ActionsのJavaScript actionでは、終了コード0がsuccess、非0がfailureとして扱われる。

- https://docs.github.com/en/actions/how-tos/create-and-publish-actions/set-exit-codes

だからbinary化は必要である。

ただし、**binary化が必要なのは境界であって、repositoryのあらゆるlayerに `passed` を持たせる理由にはならない。**

## 結論：品質ゲートを増やす前に、同じ判定を消す

品質事故を防ぐためのtestやvalidationは必要である。

しかし「安全のため」という理由は、検証経路を無制限に増やしてよい理由にはならない。

GoogleのCode Review Guideは、over-engineeringを「現在必要以上の一般化や、まだ必要でない機能」として警戒し、system全体のcomplexityが増えていないかを見るよう求めている。

- https://google.github.io/eng-practices/review/reviewer/looking-for.html

AIが実装を高速に増やせる環境では、この原則をvalidation codeにも適用する必要がある。

品質ゲートの監査で最初に聞く問いは、

> 「WARNを何点にするか？」

ではない。

> **「この事実は、すでに別の場所で判定していないか？」**

である。

同じ正しさを保てるなら、判定経路が少ない方を選ぶ。
