---
title: "同じ日付のrunが混ざる。run IDをdomainで区切る"
emoji: "🧭"
type: "tech"
topics: ["typescript", "backend", "workflow", "design"]
published: false
---

複数のworkflowが同じ保存先を使うとき、`2026-08-14` やUUIDのような「一意そうなrun ID」だけでは足りない。

IDが衝突しなくても、**そのrunがどのdomainのものかをID自身から判定できない**と、設定・保存先・監査・再実行で別domainの状態を読む余地が残る。

2026年8月13日に公開された `KAFKA2306/yt3` の実装では、run IDを `domain_id/run_id` にし、入口と保存層の両方で境界を検証している。

一次情報:

- implementation entrypoint: https://github.com/KAFKA2306/yt3/blob/849592ae98ce4ea1ea179ae5dd8997b227301791/src/index.ts
- storage boundary: https://github.com/KAFKA2306/yt3/blob/849592ae98ce4ea1ea179ae5dd8997b227301791/src/io/core.ts
- originating commit: https://github.com/KAFKA2306/yt3/commit/d1e2c42cfdfdb18d9962d15c38b87bab919df285
- workflow run history reference: https://docs.github.com/en/actions/how-tos/monitor-workflows/view-workflow-run-history

この記事の狙いはUUIDの作り方ではない。**run IDを名前空間として使い、誤ったdomainの設定やartifactへ到達する前に止める方法**を、再利用できる最小設計に落とすことだ。

## 読む前と読んだ後

読む前は、run IDを「重複しなければよい識別子」と考えているかもしれない。

読んだ後は、複数domainを1つのrunner・storage・audit基盤で扱うときに、次を実装できる。

1. `domain/run` を正準IDにする
2. 実行時domainとID prefixを照合する
3. storage層でも形式を再検証する
4. mismatch時は推測で補正せず停止する

設計思想は **一意性ではなく境界の可視化** である。

## 問題: 一意なIDでもdomainは分からない

次の2つのrunを考える。

```text
byosan_money       + 2026-08-14
humanity_observatory + 2026-08-14
```

保存キーを日付だけにすると、どちらも同じ見た目になる。

```text
runs/2026-08-14/
```

UUIDへ変えれば衝突確率の問題は小さくできるが、別の問題は残る。

```text
runs/4d0d.../
runs/91a2.../
```

この文字列だけ見ても、どちらのdomainか分からない。

障害調査、再実行、設定選択、artifact参照のたびに、外側の状態からdomainを復元する必要がある。

## 実際の入力例

`yt3` のentrypointは `BUCKET` と `RUN_ID` を別々に受け取る。

公開実装では、たとえば `BUCKET=humanity_observatory` のとき、prefixのないrun IDは次の形に正規化される。

```text
入力:
BUCKET=humanity_observatory
RUN_ID=2026-08-14

正規run ID:
humanity_observatory/2026-08-14
```

`src/index.ts` は、その正規化後の値を `AssetStore` とworkflow stateの両方へ渡している。

```ts
const initialState = {
  run_id: runId,
  bucket: BUCKET,
  mission_file: MISSION_FILE,
};
```

重要なのは、保存先だけdomain付きにするのではなく、**state自身も同じrun IDを持つ**ことだ。

## 壊れた失敗例: BUCKETとprefixが食い違う

次は一見すると両方とも有効な文字列である。

```text
BUCKET=humanity_observatory
RUN_ID=daily_pulse/2026-08-14
```

しかし意味は矛盾している。

`yt3` の公開実装は、このケースを自動補正しない。`RUN_ID` に `/` が含まれ、期待prefixと一致しない場合に例外を投げる。

```ts
if (RUN_ID.includes("/") && !RUN_ID.startsWith("humanity_observatory/")) {
  throw new Error(
    `Domain mismatch: BUCKET is ${BUCKET} but RUN_ID starts with a different prefix: ${RUN_ID}`,
  );
}
```

ここで「BUCKETを優先してprefixを書き換える」のは危険である。

誤入力なのか、別domainのrunを意図的に再実行したかったのかを機械側では確定できないからだ。

**曖昧な矛盾は修復ではなく停止させる。**

## 原因: domainを外部コンテキストにだけ持たせる

壊れやすい設計は、run IDとdomainを独立したまま最後まで運ぶ。

```ts
run("2026-08-14", { bucket: "humanity_observatory" });
```

この設計では、呼び出し先が増えるたびに2値の整合性確認が必要になる。

```text
scheduler
  ↓ run_id + bucket
workflow
  ↓ run_id + bucket
storage
  ↓ run_id + bucket
logger
  ↓ run_id + bucket
audit
```

どこか1か所で `bucket` を落としたり、default値へ戻したりすると、run IDだけでは異常を発見しにくい。

## 設計判断: IDをnamespace付きの正準値にする

正準値を次の形にする。

```text
<domain>/<run>
```

例:

```text
byosan_money/2026-08-14
humanity_observatory/2026-08-14
```

すると、下流はrun IDからdomainを復元できる。

`yt3` の `AssetStore` はこの前提をさらにstorage層で検証している。

```ts
constructor(runId: string) {
  if (!runId.includes("/")) {
    throw new Error(
      `CRITICAL: Naming Boundary Violation. runId must be 'domain_id/run_id', got: '${runId}'`,
    );
  }

  const [domainId, id] = runId.split("/");
  if (!domainId || !id) {
    throw new Error(`CRITICAL: Malformed runId: '${runId}'`);
  }

  this.domainId = domainId;
  const c = loadConfig(domainId);
  this.cfg = c;
  this.runDir = path.join(ROOT, c.workflow.paths.runs_dir, domainId, id);
}
```

ここには3つの効果がある。

- domainなしIDを保存層へ到達させない
- domainから設定を選ぶ
- directoryも `runs_dir/domain/id` に固定する

## なぜ入口とstorageの2段階で検証するのか

入口だけで検証すると、将来別のCLI、batch、test helperが `AssetStore` を直接呼び出したときに境界を迂回できる。

逆にstorageだけで検証すると、workflowをかなり進めた後で初めて不整合が見つかる可能性がある。

そこで責務を分ける。

```text
entrypoint
  BUCKET ↔ RUN_ID prefix の意味整合性を検証

storage
  domain/run 形式と保存先構造を検証
```

これは同じcheckの重複ではない。

入口は **意味** を、storageは **構造** を守っている。

## 代替案1: UUIDだけ使う

```text
550e8400-e29b-41d4-a716-446655440000
```

一意性には有効だが、そのID単体からdomainは分からない。

複数domainで同じstorage・監査・再実行機構を共有するなら、別途metadata lookupが必要になる。

## 代替案2: directoryだけdomainで分ける

```text
runs/humanity_observatory/<uuid>
```

保存先としては十分に見える。

ただし、loggerやqueue messageに `<uuid>` だけを渡すと、directoryを離れた瞬間にnamespace情報が失われる。

そのため、この記事ではpathだけでなく **識別子そのものをnamespace付きにする** 方を採る。

## 代替案3: mismatchを自動修復する

```ts
const runId = `${bucket}/${inputRunId.split("/").at(-1)}`;
```

実装は短いが、矛盾を隠す。

誤ったdomainのrunを別domainとして再解釈する危険があるため、入力がすでにprefix付きならfail-closeの方が監査しやすい。

## 改善後の最小実装

実務で再利用するなら、まずこの程度でよい。

```ts
function normalizeRunId(domain: string, raw: string): string {
  if (!domain) throw new Error("domain is required");
  if (!raw) throw new Error("run id is required");

  if (raw.includes("/")) {
    if (!raw.startsWith(`${domain}/`)) {
      throw new Error(`domain mismatch: ${domain} vs ${raw}`);
    }
    return raw;
  }

  return `${domain}/${raw}`;
}
```

storage側も独立して検証する。

```ts
function parseRunId(runId: string) {
  const parts = runId.split("/");
  if (parts.length !== 2 || !parts[0] || !parts[1]) {
    throw new Error("runId must be domain/run");
  }

  return {
    domain: parts[0],
    id: parts[1],
  };
}
```

## 検証: 正常系より境界ケースを先に書く

最低限、次の4ケースを固定する。

```ts
import assert from "node:assert/strict";

assert.equal(
  normalizeRunId("alpha", "2026-08-14"),
  "alpha/2026-08-14",
);

assert.equal(
  normalizeRunId("alpha", "alpha/2026-08-14"),
  "alpha/2026-08-14",
);

assert.throws(() =>
  normalizeRunId("alpha", "beta/2026-08-14"),
);

assert.throws(() => parseRunId("2026-08-14"));
```

特に3つ目が重要だ。

```text
期待domain: alpha
入力prefix: beta
```

という **両方が単体では妥当だが組み合わせが不正** なケースを検証する。

## 再現方法

Node.jsで次を `run-id.mjs` として保存する。

```js
function normalizeRunId(domain, raw) {
  if (raw.includes("/")) {
    if (!raw.startsWith(`${domain}/`)) {
      throw new Error(`domain mismatch: ${domain} vs ${raw}`);
    }
    return raw;
  }
  return `${domain}/${raw}`;
}

for (const [domain, id] of [
  ["alpha", "2026-08-14"],
  ["alpha", "alpha/2026-08-14"],
  ["alpha", "beta/2026-08-14"],
]) {
  try {
    console.log(normalizeRunId(domain, id));
  } catch (error) {
    console.error(error.message);
  }
}
```

実行する。

```bash
node run-id.mjs
```

期待結果は次の通り。

```text
alpha/2026-08-14
alpha/2026-08-14
domain mismatch: alpha vs beta/2026-08-14
```

この再現例は外部libraryを必要としない。

## 失敗と学び

この設計から得られる学びは、ID設計を「重複しない文字列を作る問題」だけにしないことだ。

複数のdomainが同じ基盤を共有するとき、本当に守りたいのは次である。

```text
一意性
+ 所属domain
+ 設定選択
+ 保存先
+ audit trace
```

`domain/run` にすると、1本の文字列がこの境界を運べる。

ただし、prefixを付けるだけでは不十分である。**呼び出し側のdomainと一致するかを検証し、保存層でも形式を再検証する**ところまでが1セットになる。

## 実務へ持ち込むときの判断基準

この方式が特に効くのは、次の条件があるsystemだ。

- 複数product・tenant・channel・pipelineが同じrunnerを使う
- run artifactを同じroot directoryへ保存する
- 過去runをID指定で再実行する
- audit/logからartifactへ遡る
- domainごとに設定が異なる

逆に、domainが1つしかなく、保存先も完全に分離されている小さなbatchなら、namespace prefixは過剰設計になり得る。

重要なのはprefixという記法そのものではない。

**曖昧な所属を下流へ流さず、入口で矛盾を止め、保存層で境界を再確認すること**が再利用できる設計判断である。
