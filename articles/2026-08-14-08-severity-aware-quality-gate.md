---
title: "自動生成物の品質検査で、警告と公開を止める欠陥を分ける"
emoji: "🚦"
type: "tech"
topics: ["testing", "ci", "typescript", "quality"]
published: false
created_at: "2026-08-14"
updated_at: "2026-11-21"
---

**重大な欠陥を、ほかの項目の加点で相殺するな。**

自動生成した文章が100点満点で90点でも、出典にない数値が混ざればそのまま公開できない。一方、語尾の違和感ひとつで公開を止め続ければ検査が使われなくなる。どちらも種類の違う失敗を一つのscoreに混ぜた結果だ。

[yt3のscript linter](https://github.com/KAFKA2306/yt3/blob/849592ae98ce4ea1ea179ae5dd8997b227301791/src/io/utils/qa/script_linter.ts)は`OK/WARN/FAIL`を分け、[監査への統合](https://github.com/KAFKA2306/yt3/blob/849592ae98ce4ea1ea179ae5dd8997b227301791/src/domain/agents/audit.ts)でscoreとは別にblockingを扱う。[起点commit](https://github.com/KAFKA2306/yt3/commit/d1e2c42cfdfdb18d9962d15c38b87bab919df285)

汎用規律は **「合計点で契約違反を帳消しにするな。止める欠陥と改善の助言を分離せよ」**。

## 問題: 1個のscoreだけでは重大度を表せない

たとえば100点満点で70点以上を合格とする。

```ts
const passed = score >= 70;
```

この設計では、重大な欠陥が1件あっても、他が十分よければ通ってしまう。

```text
未検証の数値: -20
構成:          100
重複:          100
文体:          100
-----------------
総合:           80 → PASS
```

逆方向の失敗もある。

文体上の軽い違和感や「数字が少し多い」といったreview候補まで即 `FAIL` にすると、自動化は簡単に止まりすぎる。

必要なのは、**品質の大きさ** と **停止すべき重大度** を分離することだ。

## 実装例: statusとscoreを別々に持つ

`yt3` の `DiscomfortLinterResultSchema` は、各checkに `OK / WARN / FAIL` を持たせている。

```ts
z.object({
  layer: z.string(),
  status: z.enum(["OK", "WARN", "FAIL"]),
  message: z.string(),
})
```

同じ実装では、各checkに応じてscoreも減点する。

実際のルールには、たとえば次がある。

- `MetricDensity`: `WARN` の場合 `-10`
- `Repetition`: `FAIL` の場合 `-30`
- `Structure`: `FAIL` の場合 `-20`
- `Dialogue`: `WARN` の場合 `-10`
- `MetadataLeakage`: `FAIL` の場合 `-20`

そして最終判定は、単純なscore閾値ではない。

```ts
passed: totalScore >= 70 && !checks.some((c) => c.status === "FAIL")
```

つまり条件は2つある。

```text
score >= threshold
AND
blocking failure == 0
```

ここが設計の中心である。

## 壊れた例: WARNをFAILとして扱う

数字密度を例にする。

`yt3` の実装では、1文あたりの数字数が閾値を超えた場合は `WARN` であり、即blockingではない。

```ts
if (density > 0.8) {
  return {
    layer: "MetricDensity",
    status: "WARN",
    message: "Extremely high metric density detected (plausible fake pattern)",
  };
}
```

これを次のように実装すると、少し数字の多い文章がすべて停止する。

```ts
if (density > 0.8) {
  throw new Error("quality gate failed");
}
```

数字の多さは「レビューする価値がある兆候」ではあっても、単独では必ずしも生成物の破損を意味しない。

一方、完全に同じ文の重複は別扱いである。同じ実装では15文字を超える完全重複文があれば `Repetition: FAIL` にする。

```ts
if (duplicates.length > 0) {
  return {
    layer: "Repetition",
    status: "FAIL",
    message: "Exact sentence repetition detected (Generative failure)",
  };
}
```

**同じ検査器の中でも、兆候と破損を同じ重大度にしない。**

## 改善後: severityを先に設計する

品質ルールを追加するとき、私は先に次の3分類を置くのがよいと考える。

```ts
type Severity = "OK" | "WARN" | "FAIL";
```

判定基準はこうする。

```text
OK
  問題を観測していない

WARN
  品質低下の兆候はある
  しかし単独では成果物の不正・破損を証明しない

FAIL
  契約違反、欠落、矛盾、再現可能な破損がある
```

たとえば、一般的な記事生成pipelineなら次のように分けられる。

```text
WARN
- 1段落が長すぎる
- 数字密度が高い
- 同じ接続表現が多い
- titleが少し長い

FAIL
- frontmatter欠落
- 出典URLのない重要数値
- 同一段落の完全重複
- privacy禁止語の実値検出
- 必須artifact欠落
```

重要なのは「厳しいルール = FAIL」ではない。

**その検査だけで公開を止めるだけの証拠があるか** で決める。

## 原因: scoreは順序尺度ではなく合算値になりやすい

scoreは便利だが、異質なエラーを足し算すると意味が曖昧になる。

```text
-10 文体
-10 数字密度
-20 出典欠落
```

この `-40` が、

```text
-40 必須ファイル欠落
```

と同じ意味とは限らない。

そこでscoreは「品質の劣化量」、severityは「停止条件」と役割を分ける。

```ts
const blocking = checks.some((c) => c.status === "FAIL");
const qualityEnough = score >= MIN_SCORE;
const passed = qualityEnough && !blocking;
```

これなら、scoreを改善指標として使いながら、重大な欠陥を相殺できない。

## GitHub Actionsへ接続するとき

GitHub公式ドキュメントでは、status checkはbuild、test、code scanningなどの検証結果を示し、required status checkを設定した場合はmerge前に成功が必要になる。

- https://docs.github.com/en/pull-requests/reference/status-checks
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches

またGitHub Actionsでは、exit code `0` はsuccess、非0はfailureとして扱われる。

- https://docs.github.com/en/actions/how-tos/create-and-publish-actions/set-exit-codes

したがって、内部の `WARN` をそのままprocess exit `1` に変換すると、CI上はblocking failureになる。

境界を明示する。

```ts
const result = audit(input);

printWarnings(result.checks.filter((x) => x.status === "WARN"));

if (result.checks.some((x) => x.status === "FAIL")) {
  process.exit(1);
}

process.exit(0);
```

WARNはログ・annotation・artifactに残し、FAILだけをblocking exitへ昇格させる。

## 検証: 4ケースをfixtureにする

severity設計は境界値をfixtureにすると壊れにくい。

```ts
const cases = [
  { score: 100, fail: 0, expected: true },
  { score: 80,  fail: 1, expected: false },
  { score: 60,  fail: 0, expected: false },
  { score: 70,  fail: 0, expected: true },
];

for (const c of cases) {
  const actual = c.score >= 70 && c.fail === 0;
  console.assert(actual === c.expected);
}
```

これで少なくとも次の退行を検出できる。

- FAILがscoreで相殺される
- WARNだけでblockingされる
- threshold境界がずれる

## 失敗と学び

品質ゲートを強くしようとすると、ruleを増やすことに意識が向きやすい。

しかしrule数より重要なのは、**そのruleが何を証明したときに停止するのか** である。

`yt3` の実装では、Metric DensityやDialogue Template Reuseは `WARN`、RepetitionやStructure、Metadata Leakageは `FAIL` と分けられている。さらに `score >= 70` と `FAILなし` を両方要求する。

この構造にすると、品質改善の信号と公開停止の信号を同じchannelに押し込まずに済む。

## 再現方法

自分の検査に適用する前に、まず軽い警告が一つある原稿と、完全な重複文がある原稿を選ぶ。既存の判定関数が判断しづらければ、下のコードを `quality-check.mjs` に保存し、Node.jsで結果だけを試す。

```js
function evaluate(checks) {
  const score = Math.max(
    0,
    100 - checks.reduce((sum, check) => sum + check.penalty, 0),
  );

  const blocking = checks.some((check) => check.status === "FAIL");

  return {
    score,
    passed: score >= 70 && !blocking,
  };
}

console.log(
  evaluate([
    { name: "metric-density", status: "WARN", penalty: 10 },
    { name: "repetition", status: "OK", penalty: 0 },
  ]),
);

console.log(
  evaluate([{ name: "repetition", status: "FAIL", penalty: 30 }]),
);
```

```bash
node quality-check.mjs
```

警告だけなら `score: 90, passed: true`。完全な重複に相当する `FAIL` があれば、点数が合格ラインの70に届いても `passed: false` になる。

この2ケースを通せれば、最低限「品質score」と「blocking severity」を別の概念として実装できている。

## まとめ

品質ゲートを単純にするなら、検査を減らすより **出力の意味を3段階に揃える** 方が効く。

```text
検査
  ↓
OK / WARN / FAIL
  ↓          ↓
score      blocking
  \          /
   最終判定
```

再利用したい原則は1つである。

**WARNは改善の信号、FAILは契約違反の証拠として扱い、scoreでFAILを相殺しない。**

この分離をしておくと、品質ルールを増やしても「厳しすぎて何も通らないCI」と「点数だけ高ければ重大欠陥も通るCI」の両方を避けやすくなる。


## 別分野での利用と撤回条件

データ公開、決算報告、プログラム生成でも、**発生してはいけない違反**と**改善したい品質差**が共存するときにこの分離を試せる。これはyt3以外への応用仮説であり、事故率改善を実測したわけではない。

すべての検査項目が同じ損失へ正しく換算でき、相殺しても重大事故の見逃しが増えないと確認できれば単一scoreで十分かもしれない。逆に小さな問題をFAILにして稼働を止め続けるならseverityの定義を見直す。**何を止めるかは、点数でなく失敗時の実害から決める。**
