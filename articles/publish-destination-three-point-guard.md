---
title: "認証が合っていても、投稿先はまだ確定しない。3点照合で誤配信を止める"
emoji: "🧭"
type: "tech"
topics: ["typescript", "youtube", "cicd", "security"]
published: true
---

公開前の設計書を読み直していて、妙な差分を見つけました。

`KAFKA2306/yt3` の ADR 0038 では、`byosan` profile の bucket が `daily_pulse` と書かれています。一方、現在の profile registry と静的監査コードは `byosan_money` を正としていました。

- ADR 0038: https://github.com/KAFKA2306/yt3/blob/main/docs/adr/0038-publish-destination-guard.md
- profile registry: https://github.com/KAFKA2306/yt3/blob/main/src/domain/youtube_profiles.ts
- routing audit: https://github.com/KAFKA2306/yt3/blob/main/src/scripts/audit_publish_routing.ts

最初は単なる文書の追従漏れに見えます。しかし、自動投稿の安全性を考えると、この差分はもっと重要な問いを突きつけます。

**認証済みのYouTubeチャンネルが正しくても、その動画を「今この実行から、そのチャンネルへ送ってよい」とは限らないのではないか。**

GitHub API上で `2026-08-12T16:48:28Z`（JSTでは2026年8月13日01:48:28）に記録された hardening commit より前の `PublishAgent` は、認証先の title / channel ID を環境変数と照合していましたが、`state.bucket` と投稿先 profile の対応は検査していませんでした。現在は、bucket、profile、認証済み channel ID を結び、どれかがずれれば `videos.insert` より前に停止します。

- hardening commit: https://github.com/KAFKA2306/yt3/commit/d1e2c42cfdfdb18d9962d15c38b87bab919df285
- hardening前の `publish.ts`: https://github.com/KAFKA2306/yt3/blob/79829b95ca7acd68d60bdd460e5211bffafc67d9/src/domain/agents/publish.ts
- 現在の `publish.ts`: https://github.com/KAFKA2306/yt3/blob/main/src/domain/agents/publish.ts

この記事では、この差分を「複数の公開先を持つ自動投稿システムで、認証と投稿意図をどう分離するか」という設計問題として整理します。なお、公開GitHub上で実際の誤投稿事故を確認できたわけではありません。以下は、公開コードで確認できる予防的hardeningと、そのコードパスから再現できる失敗条件の話です。

## 1. 問題：正しい認証情報だけでは、正しい投稿先にならない

YouTubeへの自動投稿には、少なくとも2つの問いがあります。

1. **このOAuth credentialは、どのチャンネルを操作しているか**
2. **このrunで作った動画は、そのチャンネルへ送るべきか**

前者は認証先のidentityです。後者はアプリケーション側のrouting intentです。

この2つを同じものとして扱うと、credential自体は正しくても、別用途のrunをそのcredentialで投稿できる経路が残ります。

### 実際の入力・状況

現在の `yt3` では、profile registryに次のような対応が置かれています。

```ts
byosan: {
  profileName: "byosan",
  bucket: "byosan_money",
  envFile: "config/.env.byosan",
  expectedChannelId: "...",
}
```

出典: https://github.com/KAFKA2306/yt3/blob/main/src/domain/youtube_profiles.ts

そして `Taskfile.yml` の `publish:byosan` は、`ENV_FILE=config/.env.byosan` と `YOUTUBE_CHANNEL_PROFILE=byosan` を同時に固定します。

https://github.com/KAFKA2306/yt3/blob/main/Taskfile.yml

ここで重要なのは、profile名だけではないことです。run側には `state.bucket` があり、現在の `PublishAgent` はその値もprofileのbucketと照合します。

```ts
const bucketAllowed =
  state.bucket === profile.bucket ||
  (profile.bucket === "daily_pulse" && state.bucket === "daily_pulse_nlm");

if (!bucketAllowed) {
  throw new Error(...);
}
```

https://github.com/KAFKA2306/yt3/blob/main/src/domain/agents/publish.ts

つまり「byosan credentialで認証できた」だけでは投稿できません。「このrunはbyosan向けbucketから来た」という文脈も必要です。

## 2. 原因：identityとintentが別の変数なのに、以前は結び付いていなかった

hardening前の実装も、無防備だったわけではありません。

旧 `PublishAgent` は初期化時に `YOUTUBE_CHANNEL_PROFILE` を必須にし、さらに `YOUTUBE_EXPECTED_CHANNEL_TITLE` または `YOUTUBE_EXPECTED_CHANNEL_ID` を要求していました。投稿前には `channels.list({ mine: true })` で認証済みチャンネルを取得し、期待値と比較しています。

https://github.com/KAFKA2306/yt3/blob/79829b95ca7acd68d60bdd460e5211bffafc67d9/src/domain/agents/publish.ts

ただし、このコードには `state.bucket` とprofileを結び付ける判定がありませんでした。

概念的には、旧経路は次の状態です。

```text
credential ── verify ──> channel identity
profile env ────────────> expected identity
run bucket ─────────────> （投稿先判定に未接続）
```

ここでの問題はOAuthではありません。**routingに必要な値が複数の独立した設定として存在し、runの出自が最終ゲートへ入っていないこと**です。

### 壊れた失敗例

旧コードでは、次の条件を満たす設定を考えられます。

```text
YOUTUBE_CHANNEL_PROFILE = 任意の非default文字列
YOUTUBE_EXPECTED_CHANNEL_ID = 実際の認証先channelId
state.bucket = 別用途のrun bucket
```

旧実装はprofile文字列が明示され、認証先channelIdが期待値と一致すれば、`state.bucket` の用途を検査せず `videos.insert` へ進むコードパスでした。

これは「実際に誤投稿が起きた」という意味ではありません。**公開されている旧コードに、bucket不一致を停止する条件が存在しなかった**という限定した指摘です。

## 3. 設計判断と代替案：何をhard gateにするか

今回の設計から一般化できる選択肢は3つあります。

### 代替案A：表示名やhandleを見る

人間には分かりやすい方法です。ただし現在の実装は、titleとhandleを最終ゲートにしていません。`assertYouTubeChannelMatchesProfile` では、titleやhandleの不一致は `console.warn` ですが、channel IDの不一致だけは例外になります。

https://github.com/KAFKA2306/yt3/blob/main/src/domain/youtube_profiles.ts

表示用の属性と機械的なidentityを分ける判断です。

### 代替案B：期待channel IDをenvに置く

旧実装がこの形でした。単一チャンネルなら分かりやすい一方、profile名、env file、期待channel IDが別々に編集できるため、対応関係そのものを別途検証する必要があります。

### 採用案：canonical profile + run context + authenticated identity

現在はprofile registryに、少なくとも以下をまとめています。

```text
profileName
bucket
envFile
tokenPath
expectedChannelTitle
expectedChannelHandle
expectedChannelId
```

そのうえで投稿経路を、次の順に狭めています。

```text
run bucket
   │ exact mapping
   ▼
canonical profile
   │ expected channelId
   ▼
authenticated channel
   │ match
   ▼
videos.insert
```

この構造なら、credentialの正しさとrunの投稿意図を別々に検査できます。

## 4. 実装：API呼び出しの前に3点を結ぶ

実装上の要点は、**副作用の直前までに必要な照合を終える**ことです。

### 4.1 profileを自由文字列にしない

`getYouTubeProfile` は、`byosan | yawa | humanity` のregistry key以外を拒否します。

```ts
const profile = YOUTUBE_PROFILES[normalizedName] ?? null;
if (!profile) {
  throw new Error(...);
}
```

https://github.com/KAFKA2306/yt3/blob/main/src/domain/youtube_profiles.ts

### 4.2 run bucketとprofile bucketを照合する

現在の `uploadToYouTube` では、YouTube clientを生成する前にbucket mismatchを拒否します。

```ts
const profile = getYouTubeProfile(
  process.env.YOUTUBE_CHANNEL_PROFILE?.trim(),
);

if (!bucketAllowed) {
  throw new Error(...);
}
```

その後にOAuth clientを作り、認証済みchannelを検証します。

https://github.com/KAFKA2306/yt3/blob/main/src/domain/agents/publish.ts

### 4.3 認証先channel IDをhard gateにする

`fetchCurrentChannelIdentity` は `channels.list` を `mine: true` で呼び、認証済みchannelのID、title、handleを取得します。

```ts
const response = await youtube.channels.list({
  mine: true,
  part: ["snippet"],
  maxResults: 1,
});
```

取得後、`channelId !== expectedChannelId` なら例外です。

```ts
if (actual.channelId !== profile.expectedChannelId) {
  throw new Error(...);
}
```

https://github.com/KAFKA2306/yt3/blob/main/src/domain/youtube_profiles.ts

`videos.insert` はこの検証の後にしか呼ばれません。

https://github.com/KAFKA2306/yt3/blob/main/src/domain/agents/publish.ts

### 4.4 runtimeだけでなく設定面も静的監査する

`audit_publish_routing.ts` は、少なくとも次を検査します。

- canonical registryの期待値
- `publish:byosan` / `publish:yawa` / `publish:humanity` の `ENV_FILE`
- 同taskの `YOUTUBE_CHANNEL_PROFILE`
- env exampleに対応profileが固定されていること
- deprecatedな `YOUTUBE_EXPECTED_*` がenv exampleへ戻っていないこと

https://github.com/KAFKA2306/yt3/blob/main/src/scripts/audit_publish_routing.ts

つまりruntime guardだけでなく、**起動コマンドを作る設定面にもgateを置く**構成です。

## 5. 検証：改善後はどこで止まるか

改善後のコードパスを、公開実装だけから確認します。

### 改善後の例

たとえば次の入力を考えます。

```text
YOUTUBE_CHANNEL_PROFILE=byosan
state.bucket=humanity_observatory
```

現在の `PublishAgent` では、profile registryから `byosan` のbucketを取得した直後、`state.bucket` との不一致で例外になります。`createYouTubeClient()` より前なので、`videos.insert` には到達しません。

逆に、bucketとprofileが一致しても、認証済みchannel IDがregistryの `expectedChannelId` と違えば `assertYouTubeChannelMatchesProfile` が例外を投げます。ここでも `videos.insert` より前です。

したがって現在の公開コード上では、少なくとも次の2つを別gateとして確認できます。

```text
Gate 1: run bucket == profile bucket
Gate 2: authenticated channelId == profile expectedChannelId
```

さらにprofile自体がregistry exact keyでなければ初期化段階で拒否されます。これを含めると、運用上は **bucket / profile / channelId の3点照合**になります。

hardeningが1つのcommitに入ったことも公開履歴で確認できます。

https://github.com/KAFKA2306/yt3/commit/d1e2c42cfdfdb18d9962d15c38b87bab919df285

## 6. 失敗と学び：設計書もまたdriftする

今回いちばん興味深かったのは、guardの実装そのものより、ADRと実装の差でした。

ADR 0038の対応表では `byosan` のbucketが `daily_pulse`、現在の `YOUTUBE_PROFILES` と `audit_publish_routing.ts` では `byosan_money` です。

- ADR: https://github.com/KAFKA2306/yt3/blob/main/docs/adr/0038-publish-destination-guard.md
- registry: https://github.com/KAFKA2306/yt3/blob/main/src/domain/youtube_profiles.ts
- audit: https://github.com/KAFKA2306/yt3/blob/main/src/scripts/audit_publish_routing.ts

この差から言えることは限定的です。ADRが古いのか、コード側の命名変更が未反映なのかは、これらの公開ファイルだけでは断定しません。

ただし、**安全性を文書の正しさだけに依存させない**という設計判断の価値は、この差分そのもので説明できます。

現在の静的auditはADR本文ではなく、registry、Taskfile、env exampleを実行可能な契約として照合します。文書は「なぜ」を残し、機械が止めるべき条件はコードとauditにする。この分離が重要です。

一方で、`audit_publish_routing.ts` 自体にも期待profile値が別定義されています。これはregistry driftを検出するtest oracleになりますが、更新箇所が増える代償もあります。安全側の重複を置くなら、**どちらがsource of truthで、どちらが独立検査器なのか**を明示した方が保守しやすくなります。

## 7. 再現方法：秘密情報なしでrouting guardを試す

同じ考え方はYouTube APIを呼ばなくても試せます。Node.jsで次を `routing-guard.mjs` として保存してください。

```js
const profiles = {
  alpha: { bucket: "news", expectedChannelId: "channel-A" },
  beta: { bucket: "archive", expectedChannelId: "channel-B" },
};

function assertPublishDestination({ bucket, profileName, actualChannelId }) {
  const profile = profiles[profileName];
  if (!profile) throw new Error("unknown profile");

  if (bucket !== profile.bucket) {
    throw new Error(`bucket mismatch: ${bucket} != ${profile.bucket}`);
  }

  if (actualChannelId !== profile.expectedChannelId) {
    throw new Error(
      `channel mismatch: ${actualChannelId} != ${profile.expectedChannelId}`,
    );
  }

  return "publish allowed";
}

const cases = [
  { bucket: "news", profileName: "alpha", actualChannelId: "channel-A" },
  { bucket: "archive", profileName: "alpha", actualChannelId: "channel-A" },
  { bucket: "news", profileName: "alpha", actualChannelId: "channel-B" },
];

for (const input of cases) {
  try {
    console.log(input, assertPublishDestination(input));
  } catch (error) {
    console.log(input, "BLOCKED:", error.message);
  }
}
```

実行します。

```bash
node routing-guard.mjs
```

期待する挙動は、1件目だけ許可され、2件目はbucket mismatch、3件目はchannel mismatchで止まることです。

この小さな例のポイントは、`profileName` だけを見ていないことです。

```text
content context ── bucket ─┐
                           ├─ canonical profile ── expected identity
runtime credential ────────┴────────────────────── actual identity
```

**公開という不可逆な副作用の直前では、「誰として認証したか」だけでなく、「何を、どの経路から、どこへ出そうとしているか」を同じ契約で照合する。**

複数アカウントへ自動投稿するCLI、SNS bot、クラウドdeploy、artifact uploadでも、この形はそのまま使えます。credential、environment、artifactの3つが独立して選べるシステムほど、最終副作用の前に対応関係を機械検査する価値が上がります。

## 公開一次情報

この記事で事実確認に使った公開実装は以下です。

- hardening commit: https://github.com/KAFKA2306/yt3/commit/d1e2c42cfdfdb18d9962d15c38b87bab919df285
- 現在のPublishAgent: https://github.com/KAFKA2306/yt3/blob/main/src/domain/agents/publish.ts
- hardening前のPublishAgent: https://github.com/KAFKA2306/yt3/blob/79829b95ca7acd68d60bdd460e5211bffafc67d9/src/domain/agents/publish.ts
- canonical profile registry: https://github.com/KAFKA2306/yt3/blob/main/src/domain/youtube_profiles.ts
- publish routing audit: https://github.com/KAFKA2306/yt3/blob/main/src/scripts/audit_publish_routing.ts
- Taskfile publish entries: https://github.com/KAFKA2306/yt3/blob/main/Taskfile.yml
- ADR 0038: https://github.com/KAFKA2306/yt3/blob/main/docs/adr/0038-publish-destination-guard.md
