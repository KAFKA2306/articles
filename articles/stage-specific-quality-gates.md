---
title: "警告まで止めると、自動化は使えなくなる。品質ゲートを段階ごとに分ける"
emoji: "🚦"
type: "tech"
topics: ["typescript", "cicd", "automation", "quality"]
published: false
published_at: 2026-08-13 14:08
---

品質チェックを増やすほど安全になる、とは限らない。

`KAFKA2306/yt3` の台本生成コードを追っていて、同じ `ScriptIntegrityLinter` の結果を「生成中」と「監査・運用」で同じ意味にしていないことに気づいた。

- linter本体: https://github.com/KAFKA2306/yt3/blob/main/src/io/utils/qa/script_linter.ts
- 生成段階の利用側: https://github.com/KAFKA2306/yt3/blob/main/src/domain/agents/content.ts
- 日次監査の利用側: https://github.com/KAFKA2306/yt3/blob/main/src/scripts/audit_today.ts
- 変更を含む公開commit: https://github.com/KAFKA2306/yt3/commit/d1e2c42cfdfdb18d9962d15c38b87bab919df285

linterは `OK / WARN / FAIL` の3段階を返す。一方、生成段階では `FAIL` が1件でもあれば再生成するが、`WARN` だけなら通す。これは単なる実装差ではなく、**同じ検査結果でも、どの工程で使うかによって「止める条件」を変える**という設計判断である。

GitHub Actions自体は、actionの終了コード `0` をsuccess、非0をfailureとして扱う。つまりCIへ接続する最後の境界では、アプリケーション内部の多段階評価を最終的に「通す / 止める」へ射影する必要がある。

https://docs.github.com/en/actions/how-tos/create-and-publish-actions/set-exit-codes

## 1. 問題：WARNとFAILを同じ条件で止めると改善ループが詰まる

### 実際の入力・状況

現在の `ScriptIntegrityLinter` は、検査ごとに `OK / WARN / FAIL` を返し、100点から減点する。

たとえば公開コードでは、次のように扱われている。

- `MetricDensity` が `WARN` なら -10
- `DialogueTemplateReuse` が `WARN` なら -10
- `AuthorityMixing` が `WARN` なら -10
- `ScopeOverload` が `WARN` なら -10
- `Wording` が `WARN` なら -10
- `Repetition` が `FAIL` なら -30
- `FactPlausibility` が `FAIL` なら -20

linter全体の `passed` は次の条件で決まる。

```ts
passed: totalScore >= 70 && !checks.some((c) => c.status === "FAIL")
```

出典: https://github.com/KAFKA2306/yt3/blob/main/src/io/utils/qa/script_linter.ts

ここで重要なのは、スコアとseverityが別軸になっていることだ。

`WARN` が4件あれば、FAILがなくても100点から40点引かれて60点になる。その場合、linter単体の `passed` は `false` になる。

しかし生成段階の `content.ts` は `auditRes.passed` をそのまま使っていない。`Artifact` を除外した後、次の条件を独自に計算する。

```ts
const passed = relevantChecks.every((c) => c.status !== "FAIL");
```

出典: https://github.com/KAFKA2306/yt3/blob/main/src/domain/agents/content.ts

つまり生成中は、**WARNは改善材料だが、単独では再生成を強制しない**。

## 2. 原因：品質スコアとblocking severityは目的が違う

品質スコアは「どれくらい良いか」を連続値で表すのに向いている。一方、severityは「この状態で次へ進めてよいか」を表す。

この2つを1本のbooleanへ潰すと、次の問題が起こる。

### 壊れた失敗例

生成段階で次のように書くとする。

```ts
const result = await linter.audit(state);
if (!result.passed) {
  regenerate();
}
```

この実装では、FAILがゼロでもWARNの累積でscoreが70未満になると再生成する。

たとえばWARNが4件、それぞれ-10ならscoreは60になる。公開されている現在の減点規則から、この状態は成立しうる。

問題は「60点だから悪い」ことではない。生成ループでは最大試行回数が3回に制限されており、`content.ts` は3回で通らなければ例外にする。

```ts
const maxAttempts = 3;
```

出典: https://github.com/KAFKA2306/yt3/blob/main/src/domain/agents/content.ts

WARNまでblockingにすると、致命的でない違和感のために有限の再生成予算を消費する。

## 3. 設計判断と代替案：判定を「検査」と「工程ポリシー」に分ける

採用すべき分離は次の2層である。

```text
検査器: 事実を返す
  └─ OK / WARN / FAIL / score / details

工程ポリシー: その工程で何を止めるか決める
  ├─ generation: FAILのみblock
  ├─ review: WARNも可視化
  └─ publish/CI: 必須条件をbinaryへ射影
```

### 代替案A：全工程で `result.passed` を共有する

実装は簡単だが、工程ごとの目的を表現できない。生成中の「改善できる警告」と公開直前の「出してはいけない失敗」が同じ扱いになる。

### 代替案B：scoreだけで閾値判定する

`score >= 70` のような条件だけでは、重大なFAILが1件あっても他が高得点なら通る設計になり得る。現在のlinterが `score >= 70` に加えて `FAILがないこと` も要求しているのは、この問題を避ける形になっている。

### 採用案：検査結果は共通、blocking条件は工程側で持つ

現在の `content.ts` はこの形に近い。linterの詳細結果を受け取り、生成工程ではFAILだけをblockingにする。

さらに `audit_today.ts` は、監査全体の `decision === "PASS"` と、個別の `Discomfort` 警告を別々に保存している。

出典: https://github.com/KAFKA2306/yt3/blob/main/src/scripts/audit_today.ts

この分離により、警告を消さずに運用へ残しつつ、すべての警告を即停止条件にすることも避けられる。

## 4. 実装：GatePolicyを検査器の外へ出す

他のプロジェクトへ移植するなら、severity判定をlinter内部へ埋め込まず、工程ごとのadapterにする。

```ts
type Severity = "OK" | "WARN" | "FAIL";

type Check = {
  name: string;
  status: Severity;
  message: string;
};

type AuditResult = {
  score: number;
  checks: Check[];
};

type GatePolicy = {
  minScore?: number;
  blockOn: Severity[];
};

function evaluateGate(result: AuditResult, policy: GatePolicy) {
  const blockedChecks = result.checks.filter((check) =>
    policy.blockOn.includes(check.status),
  );

  const scoreBlocked =
    policy.minScore !== undefined && result.score < policy.minScore;

  return {
    passed: blockedChecks.length === 0 && !scoreBlocked,
    blockedChecks,
    scoreBlocked,
  };
}
```

生成工程なら次のようにする。

```ts
const generationGate: GatePolicy = {
  blockOn: ["FAIL"],
};
```

公開前の厳しい工程では、必要ならscore条件も追加できる。

```ts
const publishGate: GatePolicy = {
  minScore: 70,
  blockOn: ["FAIL"],
};
```

CIへつなぐときだけ、最終結果を終了コードへ変換する。

```ts
const gate = evaluateGate(result, publishGate);
process.exitCode = gate.passed ? 0 : 1;
```

GitHub Actionsでは終了コード0がsuccess、非0がfailureになるため、このbinary化は境界で1回だけ行う。

公式仕様: https://docs.github.com/en/actions/how-tos/create-and-publish-actions/set-exit-codes

## 5. 検証：同じWARN集合を2つの工程へ通す

次の入力を使う。

```ts
const result: AuditResult = {
  score: 60,
  checks: [
    { name: "metric", status: "WARN", message: "dense" },
    { name: "template", status: "WARN", message: "reused" },
    { name: "scope", status: "WARN", message: "wide" },
    { name: "wording", status: "WARN", message: "awkward" },
  ],
};
```

生成工程では通る。

```ts
evaluateGate(result, { blockOn: ["FAIL"] }).passed === true;
```

公開前にscore 70以上を要求するなら止まる。

```ts
evaluateGate(result, {
  minScore: 70,
  blockOn: ["FAIL"],
}).passed === false;
```

### 改善後の例

さらにFAILを1件追加する。

```ts
result.checks.push({
  name: "fact",
  status: "FAIL",
  message: "unverified numeric claim",
});
```

すると生成工程でも公開工程でも止まる。

この挙動なら、WARNは改善候補として保持され、FAILだけは工程をまたいで確実にblockingへできる。

## 6. 失敗と学び：共通linterだから共通boolean、ではない

最初にやりがちな設計は、linter自身へ唯一の `passed` を持たせ、全工程がそれだけを見ることだ。

しかし公開コードを見ると、同じ `ScriptIntegrityLinter` でも利用側が必要とする意味は異なる。

- linter本体: score閾値とFAIL不在を組み合わせる
- content生成: Artifactを除き、FAIL不在だけを見る
- 日次監査: audit全体のPASSと個別警告を別々に表示する

出典:

- https://github.com/KAFKA2306/yt3/blob/main/src/io/utils/qa/script_linter.ts
- https://github.com/KAFKA2306/yt3/blob/main/src/domain/agents/content.ts
- https://github.com/KAFKA2306/yt3/blob/main/src/scripts/audit_today.ts

学びは、**検査器は観測事実を返し、止める権限は工程側が持つ**、ということだ。

severityを増やす目的は、判定を複雑にすることではない。binaryに潰す場所を遅らせることで、改善可能な警告と致命的な失敗を別の速度で扱えるようにすることにある。

## 7. 再現方法：10分で試せる最小例

Node.js 20以降を想定し、`gate.mjs` を作る。

```js
function evaluateGate(result, policy) {
  const blockedChecks = result.checks.filter((check) =>
    policy.blockOn.includes(check.status),
  );
  const scoreBlocked =
    policy.minScore !== undefined && result.score < policy.minScore;
  return {
    passed: blockedChecks.length === 0 && !scoreBlocked,
    blockedChecks,
    scoreBlocked,
  };
}

const result = {
  score: 60,
  checks: [
    { name: "metric", status: "WARN" },
    { name: "template", status: "WARN" },
    { name: "scope", status: "WARN" },
    { name: "wording", status: "WARN" },
  ],
};

const generation = evaluateGate(result, { blockOn: ["FAIL"] });
const publish = evaluateGate(result, {
  minScore: 70,
  blockOn: ["FAIL"],
});

console.log({ generation, publish });
```

実行する。

```bash
node gate.mjs
```

期待する結果は、`generation.passed === true`、`publish.passed === false` である。

次に1件だけ `FAIL` を追加し、両方が `false` になることを確認する。

この最小例をGitHub Actionsへ入れる場合は、最後に `process.exitCode` を設定すればよい。終了コードとcheck run statusの対応はGitHub公式ドキュメントで確認できる。

https://docs.github.com/en/actions/how-tos/create-and-publish-actions/set-exit-codes

## 公開コードから確認できる範囲

この記事で断定しているのは、公開GitHub上で確認できる現在の実装だけである。

- linterが `OK / WARN / FAIL` とscoreを返す
- 全体passedはscore 70以上かつFAILなし
- content生成は最大3回試行する
- content生成ではFAILだけをblockingにする
- 日次監査では全体PASSとDiscomfort警告を別に扱う
- GitHub Actionsは終了コード0をsuccess、非0をfailureとして扱う

実際にWARNの過剰blockingで公開障害が起きた、という事故記録は確認していない。そのため、この記事の「壊れた失敗例」は現在の公開ルールから作った再現可能な反例であり、過去事故としては扱っていない。
