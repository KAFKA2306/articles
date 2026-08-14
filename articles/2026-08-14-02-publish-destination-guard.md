---
title: "公開先を環境変数だけで決めない：誤配信を止めるDestination Guard"
emoji: "🛡️"
type: "tech"
topics: ["typescript", "youtube", "automation", "testing", "security"]
published: false
---

自動投稿の事故で怖いのは、アップロード自体が失敗することより、**正常に成功したまま別の公開先へ出ること**です。

複数チャンネルを1つのリポジトリから運用すると、`ENV_FILE`、OAuth token、channel profile、runの用途が別々の場所で決まりやすくなります。各設定が単独では正しくても、組み合わせがずれると「動画生成は正しい、認証も通る、APIも成功する、しかし投稿先が違う」という事故が成立します。

この記事では、公開GitHub上の実装を例に、公開直前で次の3つを一致させる設計を整理します。

1. **何を公開するrunか** — bucket
2. **どの公開先を選んだか** — profile
3. **実際にOAuthで認証されている相手は誰か** — remote identity

結論は単純です。

> **公開先は設定値として読むだけでなく、公開直前に「用途・設定・実認証先」の一致をfail-closeで検証する。**

## 問題：設定ファイルが正しくても、組み合わせは正しいとは限らない

たとえば3つのYouTubeチャンネルを1つの自動化基盤で扱うとします。

```text
run bucket     = byosan_money
profile        = byosan
env file       = config/.env.byosan
OAuth channel  = 秒算マネー
```

この4つが揃っていれば意図は一貫しています。

しかし、次のような入力も構文上は成立します。

```text
run bucket     = byosan_money
profile        = humanity
env file       = config/.env
OAuth channel  = 人類観測所
```

API clientの初期化だけを見れば、後者でも認証済みtokenを持っていれば通信できます。問題は「認証できるか」ではなく、**その認証先へ今回のrunを公開してよいか**です。

`KAFKA2306/yt3` の公開実装では、profile registryに `profileName`、`bucket`、`envFile`、期待するchannel ID/title/handleをまとめ、`PublishAgent` がrun bucketとprofile bucketを比較しています。さらにOAuth後、YouTube APIから現在のchannel identityを取得し、期待するchannel IDと一致しなければ例外で停止します。

一次情報:

- https://github.com/KAFKA2306/yt3/blob/849592ae98ce4ea1ea179ae5dd8997b227301791/src/domain/youtube_profiles.ts
- https://github.com/KAFKA2306/yt3/blob/849592ae98ce4ea1ea179ae5dd8997b227301791/src/domain/agents/publish.ts

## 原因：公開先が「文字列の集合」になっている

誤配信しやすい設計では、同じ意味を持つ値が独立した文字列として散らばります。

```text
.env
Taskfile
CLI argument
workflow config
OAuth cache path
publish script
```

それぞれに `byosan` や `humanity` のような名前を書くだけでは、値同士の関係は型にも実行時契約にもなりません。

壊れ方は3種類あります。

### 1. profileとrun用途がずれる

動画は「A向け」なのに、profileだけBを指定するケースです。

### 2. profileとcredentialがずれる

profileはAなのに、読み込まれたrefresh tokenがBのchannelを指しているケースです。

### 3. launcherとregistryがずれる

TaskfileではA用envを読むつもりでも、profile registryでは別envを期待しているケースです。

つまり本質は「値が間違っている」ではなく、**関係が検証されていない**ことです。

## 設計判断：公開先を1つの識別子ではなく契約として持つ

`yt3` の実装では、profileを単なるchannel名ではなく、複数フィールドを束ねる契約として扱っています。

```text
profile
 ├─ bucket
 ├─ envFile
 ├─ tokenPath
 ├─ expectedChannelId
 ├─ expectedChannelTitle
 └─ expectedChannelHandle
```

ここで重要なのは、`expectedChannelId` を実認証先の強い照合キーとして使っている点です。実装ではtitleとhandleの不一致はwarningですが、channel IDの不一致はthrowされます。

この差は合理的です。表示名やhandleは運用上変更されることがあります。一方、公開先そのものを識別する契約では、実装が採用しているchannel IDをblocking keyにできます。

### 代替案A：env fileだけで公開先を決める

実装は簡単ですが、env fileとOAuth先が本当に一致している保証がありません。

### 代替案B：profile名だけをCLIで渡す

launcherは簡潔になりますが、run用途とprofileの対応が別の暗黙知になります。

### 代替案C：upload後にchannelを確認する

検出はできますが、誤配信はすでに発生しています。公開系では遅すぎます。

### 採用する形：preflight + runtime verification

公開前に静的な対応関係を検査し、runtimeでも実認証先を確認します。

```text
static/preflight
  Task -> envFile -> profile -> expected bucket

runtime
  run bucket -> profile
  OAuth -> actual channel ID -> expected channel ID

all match
  -> upload
otherwise
  -> stop
```

## 実装：3段階でfail-closeする

### 1. launcherでenvとprofileを同時に固定する

`Taskfile.yml` の専用publish taskは、env fileとprofileを同じcommandで指定しています。

例として `publish:byosan` は `config/.env.byosan` と `YOUTUBE_CHANNEL_PROFILE=byosan`、`publish:yawa` は `config/.env.yawa` と `YOUTUBE_CHANNEL_PROFILE=yawa` を組にしています。

一次情報:

- https://github.com/KAFKA2306/yt3/blob/849592ae98ce4ea1ea179ae5dd8997b227301791/Taskfile.yml

この段階の目的は、operatorが2つの値を別々に組み立てる余地を減らすことです。

### 2. PublishAgentでrun用途とprofileを照合する

`PublishAgent` は選択されたprofileを取得したあと、runの `state.bucket` とprofileの `bucket` を比較します。不一致ならupload処理へ進みません。

実装上は、`daily_pulse` と `daily_pulse_nlm` のような明示的な互換ケースだけ例外として許可されています。重要なのは「何となく似た名前なら許す」のではなく、許可する互換関係をコードに書いていることです。

### 3. OAuth後に実channelをread-backする

profileとbucketが合っていても、credentialが別channelのものならまだ危険です。

そこで `fetchCurrentChannelIdentity()` はYouTube APIの `channels.list` を `mine: true` で呼び、認証済みchannelのID・title・handleを取得します。その後 `assertYouTubeChannelMatchesProfile()` がprofileの期待値と比較し、channel IDが違えば停止します。

この段階で初めて、「設定上Aを選んだ」ではなく「**実際にAへ接続している**」ことを確認できます。

## 検証：設定の対応関係そのものをテスト対象にする

runtime guardだけでは、launcherやexample envが将来ずれる可能性があります。

`audit_publish_routing.ts` は次を独立して検査しています。

- profile registryに期待するprofileが存在する
- profileごとの `bucket` / `envFile` / channel identityが期待値と一致する
- `publish:byosan` などのtask commandが正しいenv fileとprofileをpinしている
- example envが正しい `YOUTUBE_CHANNEL_PROFILE` を含む
- deprecatedな `YOUTUBE_EXPECTED_*` フィールドが残っていない

一次情報:

- https://github.com/KAFKA2306/yt3/blob/849592ae98ce4ea1ea179ae5dd8997b227301791/src/scripts/audit_publish_routing.ts

ここで面白いのは、audit側にも期待値を持たせている点です。重複を完全に避けるのではなく、**正準registryとは別の検査器が同じ契約を再確認する**ことで、registryの書き換えだけで誤設定を正当化しにくくしています。

これはテストコードで期待値を別に持つのと同じ考え方です。

## 壊れた失敗例：profileだけ切り替える

再現用の失敗例を単純化します。

```text
state.bucket = "byosan_money"
YOUTUBE_CHANNEL_PROFILE = "humanity"
```

profile registry上、`humanity` のbucketは `humanity_observatory` です。

したがって `PublishAgent` のbucket checkで不一致となり、upload前に例外になります。

この例で重要なのは、OAuth credentialが有効かどうかは関係ないことです。credentialが完全に正常でも、用途との対応が違えば止めるべきです。

## 改善後の例：用途・profile・実認証先を全部見る

改善後は次の順で判断します。

```text
1. run bucket = byosan_money
2. profile = byosan
3. profile.bucket = byosan_money
4. envFile = config/.env.byosan
5. OAuthでchannel identityを取得
6. actual channel ID == expected channel ID
7. upload
```

どこか1つでも一致しなければ公開しません。

これにより、公開処理の成功条件が

```text
APIが200を返す
```

から

```text
意図したrunを、意図したprofileで、意図した実channelへ公開できる
```

へ変わります。

## 失敗と学び：認証成功を安全性の証明にしない

認証は「そのcredentialでAPIを使える」ことしか証明しません。

複数公開先を持つシステムでは、認証成功とrouting正当性は別の性質です。

```text
authentication
  誰としてAPIへ接続できるか

routing authorization
  今回の成果物をその公開先へ送ってよいか
```

この2つを同じチェックにすると、強いcredentialほど誤配信時の影響が大きくなります。

もう1つの学びは、**human-readable nameだけをblocking keyにしない**ことです。実装ではtitle/handle mismatchをwarningにし、channel ID mismatchをblockしています。変更されやすい表示情報と、公開先同一性の判定を分ける設計です。

## 読者が試せる最小再現

YouTube APIを実際に呼ばなくても、routing contractの考え方は数十行で再現できます。

```ts
type Profile = {
  bucket: string;
  destinationId: string;
};

const profiles: Record<string, Profile> = {
  alpha: { bucket: "report_alpha", destinationId: "DEST_A" },
  beta: { bucket: "report_beta", destinationId: "DEST_B" },
};

function assertDestination(
  runBucket: string,
  profileName: string,
  actualDestinationId: string,
) {
  const profile = profiles[profileName];
  if (!profile) throw new Error("unknown profile");
  if (runBucket !== profile.bucket) throw new Error("bucket mismatch");
  if (actualDestinationId !== profile.destinationId) {
    throw new Error("destination mismatch");
  }
}

assertDestination("report_alpha", "alpha", "DEST_A"); // pass
assertDestination("report_alpha", "beta", "DEST_B");  // bucket mismatch
assertDestination("report_alpha", "alpha", "DEST_B"); // destination mismatch
```

実務ではさらに、launcherに対する静的auditを追加します。

```text
launcher config
  ↓
profile registry
  ↓
preflight audit
  ↓
runtime bucket check
  ↓
remote identity read-back
  ↓
publish
```

## まとめ

複数の公開先を持つ自動化で、最も危険なのは「失敗すること」ではなく「別の場所へ正常終了すること」です。

そのため公開処理では、公開先を単一の環境変数として扱わず、最低でも次の3点を契約にします。

- run用途とprofileが一致している
- launcher設定とprofile registryが一致している
- 実認証先のimmutableに近いIDがprofile期待値と一致している

そして、この対応関係をruntime guardだけでなく独立auditでも検査します。

**認証できたから公開するのではなく、意図した相手だとread-backできたときだけ公開する。**

このパターンはYouTubeに限りません。複数のS3 bucket、Slack workspace、GitHub repository、クラウドproject、メール送信tenantなど、「credentialは有効だが送り先を間違える」種類のシステムにそのまま応用できます。

## 一次情報

- `PublishAgent` のbucket照合・実channel確認: https://github.com/KAFKA2306/yt3/blob/849592ae98ce4ea1ea179ae5dd8997b227301791/src/domain/agents/publish.ts
- profile registryとchannel ID照合: https://github.com/KAFKA2306/yt3/blob/849592ae98ce4ea1ea179ae5dd8997b227301791/src/domain/youtube_profiles.ts
- publish routing audit: https://github.com/KAFKA2306/yt3/blob/849592ae98ce4ea1ea179ae5dd8997b227301791/src/scripts/audit_publish_routing.ts
- env/profileをpinするTaskfile: https://github.com/KAFKA2306/yt3/blob/849592ae98ce4ea1ea179ae5dd8997b227301791/Taskfile.yml
- 変更を含む公開commit: https://github.com/KAFKA2306/yt3/commit/d1e2c42cfdfdb18d9962d15c38b87bab919df285
