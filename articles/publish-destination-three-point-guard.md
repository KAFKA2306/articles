---
title: "認証が合っていても、投稿先はまだ確定しない。3点照合で誤配信を止める"
emoji: "🧭"
type: "tech"
topics: ["typescript", "youtube", "cicd", "security"]
published: false
published_at: 2026-08-13 13:06
---

公開前の設計書を読み直していて、妙な差分を見つけた。

`KAFKA2306/yt3` の ADR 0038 では `byosan` profile の bucket が `daily_pulse`、現在の profile registry と静的監査コードでは `byosan_money` になっている。

- ADR: https://github.com/KAFKA2306/yt3/blob/main/docs/adr/0038-publish-destination-guard.md
- registry: https://github.com/KAFKA2306/yt3/blob/main/src/domain/youtube_profiles.ts
- audit: https://github.com/KAFKA2306/yt3/blob/main/src/scripts/audit_publish_routing.ts

文書の追従差分に見えるが、自動投稿では重要な問いになる。

**認証済みチャンネルが正しくても、そのrunを本当にそこへ投稿してよいのか。**

GitHub APIで `2026-08-12T16:48:28Z`、JSTでは2026年8月13日01:48:28に記録されたhardening commitでは、投稿先の確認にrunのbucketを加えた。以前の実装は認証先のtitle / channel IDを期待値と照合していたが、`state.bucket` とprofileの対応は検査していなかった。

- commit: https://github.com/KAFKA2306/yt3/commit/d1e2c42cfdfdb18d9962d15c38b87bab919df285
- 変更前: https://github.com/KAFKA2306/yt3/blob/79829b95ca7acd68d60bdd460e5211bffafc67d9/src/domain/agents/publish.ts
- 現在: https://github.com/KAFKA2306/yt3/blob/main/src/domain/agents/publish.ts

公開GitHub上で実際の誤投稿事故は確認していない。この記事で扱うのは、公開コードから確認できる予防的hardeningと、その設計を他の自動投稿へ再利用する方法である。

## 1. 問題：認証先と投稿意図は別物

自動投稿には2つの問いがある。

1. この認証情報はどのチャンネルを操作しているか
2. このrunで作った成果物はそのチャンネルへ送るべきか

1はidentity、2はrouting intentだ。

### 実際の入力・状況

現在のregistryでは `byosan` profileに `bucket: "byosan_money"` が定義されている。

https://github.com/KAFKA2306/yt3/blob/main/src/domain/youtube_profiles.ts

`Taskfile.yml` の `publish:byosan` も、対応するenv fileとprofileを同じtask内で固定する。

https://github.com/KAFKA2306/yt3/blob/main/Taskfile.yml

そして `PublishAgent` はrun側の `state.bucket` とprofile側のbucketを比較する。つまり「正しいprofileで起動した」だけでは足りず、「正しい用途のrunから来た」ことも要求する。

## 2. 原因：以前はrunの出自が最終ゲートへ入っていなかった

hardening前も投稿先確認は存在した。旧 `PublishAgent` は明示profileを要求し、投稿前に認証済みチャンネルのtitleまたはchannel IDを期待値と比較していた。

https://github.com/KAFKA2306/yt3/blob/79829b95ca7acd68d60bdd460e5211bffafc67d9/src/domain/agents/publish.ts

ただし旧コードには、`state.bucket` とprofileの対応を確認する条件がない。

```text
認証情報 ──> 認証先チャンネル ──> identity確認
run bucket ────────────────────> 投稿先判定に未接続
```

### 壊れた失敗例

旧コードでは、認証先identityの期待値が一致していても、別用途の `state.bucket` を拒否する分岐はなかった。これは実事故の記録ではなく、旧ソースにそのチェックが存在しなかったというコード上の事実である。

問題はOAuthの成否ではない。**成果物の出自と公開先identityが別管理なのに、その対応を副作用の前に結んでいなかったこと**だ。

## 3. 設計判断と代替案

### 代替案A：表示名やhandleをhard gateにする

現在の実装は採用していない。`assertYouTubeChannelMatchesProfile` ではtitleやhandleの不一致はwarningだが、channel IDの不一致は例外になる。

https://github.com/KAFKA2306/yt3/blob/main/src/domain/youtube_profiles.ts

人が読む名前と機械が使うidentityを分離している。

### 代替案B：期待channel IDを各envへ置く

旧実装に近い。小規模なら単純だが、profile、env、期待identityの対応関係が複数箇所へ分散する。

### 採用案：canonical profileを中心に3点を照合する

現在はregistryがprofileごとにbucket、env file、token path、期待channel情報をまとめる。その上で運用上は次の3点を検査する。

```text
run bucket
    ↓
profile exact key
    ↓
authenticated channelId
    ↓
publish API
```

profileが不明なら初期化で止まり、bucketが違えば投稿処理の前半で止まり、認証済みchannel IDが違えばAPI投稿前に止まる。

## 4. 実装：副作用より前に照合を終える

### 4.1 profileをregistry exact keyに限定する

`getYouTubeProfile` は現在 `byosan | yawa | humanity` の定義済みkey以外を拒否する。

https://github.com/KAFKA2306/yt3/blob/main/src/domain/youtube_profiles.ts

### 4.2 bucketを照合する

`uploadToYouTube` はprofile取得後、`state.bucket` が許可されたbucketでなければ例外を投げる。この判定はYouTube client生成より前に置かれている。

https://github.com/KAFKA2306/yt3/blob/main/src/domain/agents/publish.ts

### 4.3 認証済みchannel IDを照合する

`fetchCurrentChannelIdentity` は認証済みchannelを取得し、`assertYouTubeChannelMatchesProfile` がregistryの `expectedChannelId` と比較する。不一致なら例外になる。

https://github.com/KAFKA2306/yt3/blob/main/src/domain/youtube_profiles.ts

`videos.insert` はこれらの検証後に呼ばれる。

https://github.com/KAFKA2306/yt3/blob/main/src/domain/agents/publish.ts

### 4.4 起動設定も静的監査する

`audit_publish_routing.ts` はregistry、publish task、env exampleの整合を検査する。publish taskに期待するenv fileとprofileが含まれること、env exampleにprofileが固定されること、旧形式の期待channel設定が戻っていないことを確認する。

https://github.com/KAFKA2306/yt3/blob/main/src/scripts/audit_publish_routing.ts

runtime guardだけでなく、**runを起動する設定面にもgateを置く**のがポイントだ。

## 5. 検証：改善後はどこで止まるか

### 改善後の例

次の組み合わせを考える。

```text
profile = byosan
state.bucket = humanity_observatory
```

現在のregistryでは `byosan` のbucketは `byosan_money` なので、`PublishAgent` はbucket mismatchで例外になる。コード順ではYouTube client生成より前であり、投稿APIには到達しない。

逆にbucketとprofileが一致しても、認証済みchannel IDがregistryの期待値と異なれば、channel照合で停止する。

したがって公開実装から確認できる境界は次の通りである。

```text
Gate 0: profileがregistryに存在する
Gate 1: run bucketがprofile bucketに合う
Gate 2: authenticated channelIdがexpectedChannelIdに合う
```

hardening差分は次のcommitで確認できる。

https://github.com/KAFKA2306/yt3/commit/d1e2c42cfdfdb18d9962d15c38b87bab919df285

## 6. 失敗と学び：設計書もdriftする

ここで冒頭の差分へ戻る。

ADR 0038の対応表では `byosan` のbucketが `daily_pulse`、現在のregistryとauditでは `byosan_money` である。

この公開情報だけでは、ADRが古いのか、後続の命名変更が文書へ未反映なのかは断定できない。確認できない因果は書かない。

ただし、この差から1つだけ実務的な学びを得られる。

**安全性を文書の正しさだけに依存させない。**

現在の静的auditはADR本文ではなく、registry、Taskfile、env exampleを機械的に照合する。文書は設計意図を残し、止めるべき条件は実行可能な契約へ落とす。

一方、audit側にも期待profile値が独立定義されている。これはregistry driftを検知できる反面、更新箇所が増える。意図的に値を重複させるなら、source of truthとtest oracleの役割を分けておく必要がある。

## 7. 再現方法：秘密情報なしで試す

YouTube APIなしで同じ考え方を再現できる。次を `routing-guard.mjs` として保存する。

```js
const profiles = {
  alpha: { bucket: "news", channelId: "channel-A" },
  beta: { bucket: "archive", channelId: "channel-B" },
};

function guard({ bucket, profileName, actualChannelId }) {
  const profile = profiles[profileName];
  if (!profile) throw new Error("unknown profile");
  if (bucket !== profile.bucket) throw new Error("bucket mismatch");
  if (actualChannelId !== profile.channelId) throw new Error("channel mismatch");
  return "publish allowed";
}

const cases = [
  ["news", "alpha", "channel-A"],
  ["archive", "alpha", "channel-A"],
  ["news", "alpha", "channel-B"],
];

for (const [bucket, profileName, actualChannelId] of cases) {
  try {
    console.log(guard({ bucket, profileName, actualChannelId }));
  } catch (e) {
    console.log("BLOCKED:", e.message);
  }
}
```

```bash
node routing-guard.mjs
```

1件目だけ `publish allowed`、2件目は `bucket mismatch`、3件目は `channel mismatch` になる。

この形はYouTube固有ではない。複数環境へのdeploy、複数bucketへのartifact upload、複数アカウントへのSNS投稿でも、**credential / artifact context / destination identityを副作用の前に同じ契約へ束ねる**という設計として再利用できる。

## 公開一次情報

- hardening commit: https://github.com/KAFKA2306/yt3/commit/d1e2c42cfdfdb18d9962d15c38b87bab919df285
- 現在のPublishAgent: https://github.com/KAFKA2306/yt3/blob/main/src/domain/agents/publish.ts
- hardening前のPublishAgent: https://github.com/KAFKA2306/yt3/blob/79829b95ca7acd68d60bdd460e5211bffafc67d9/src/domain/agents/publish.ts
- profile registry: https://github.com/KAFKA2306/yt3/blob/main/src/domain/youtube_profiles.ts
- routing audit: https://github.com/KAFKA2306/yt3/blob/main/src/scripts/audit_publish_routing.ts
- Taskfile: https://github.com/KAFKA2306/yt3/blob/main/Taskfile.yml
- ADR 0038: https://github.com/KAFKA2306/yt3/blob/main/docs/adr/0038-publish-destination-guard.md
