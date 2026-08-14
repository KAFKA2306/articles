---
title: "全部成功したのに、違うチャンネルへ投稿される。その事故を3点照合で止める"
emoji: "🛡️"
type: "tech"
topics: ["typescript", "youtube", "automation", "testing", "security"]
published: false
---

自動投稿で一番怖いのは、API errorではない。

**全部成功したまま、違う公開先へ出ること**だ。

動画生成は成功。

OAuthも成功。

YouTube APIも成功。

CIもgreen。

それでも、投稿先が違えば事故である。

`KAFKA2306/yt3` を見直していたとき、実際に気になる差分があった。

ADR 0038では `byosan` profile のbucketが `daily_pulse`、current registryと静的監査では `byosan_money` になっていた。

- ADR: https://github.com/KAFKA2306/yt3/blob/main/docs/adr/0038-publish-destination-guard.md
- registry: https://github.com/KAFKA2306/yt3/blob/main/src/domain/youtube_profiles.ts
- audit: https://github.com/KAFKA2306/yt3/blob/main/src/scripts/audit_publish_routing.ts

これは実際の誤投稿事故を示す証拠ではない。

しかし、**「認証先が正しい」だけでは投稿意図まで証明できない**ことをはっきり示していた。

そこでpublish直前に、次の3点を一致させるようにした。

1. **何を公開するrunか** — bucket
2. **どの公開先を選んだか** — profile
3. **実際にOAuthで認証されている相手は誰か** — remote identity

この記事で扱うのはYouTube APIの使い方ではない。

**人が毎回宛先確認しなくても、自動投稿を安心して任せられるrouting contract**について書く。

## 認証できることと、そこへ投稿してよいことは別

例えば、次の状態なら意図は揃っている。

```text
run bucket     = byosan_money
profile        = byosan
env file       = config/.env.byosan
OAuth channel  = 秒算マネー
```

しかし次も、API clientとしては成立し得る。

```text
run bucket     = byosan_money
profile        = humanity
env file       = config/.env
OAuth channel  = 人類観測所
```

認証済みtokenがあれば、通信自体は成功する。

問題は、

> 認証できるか

ではなく、

> **今回のrunを、その認証先へ公開してよいか**

である。

この2つを同じbooleanへ潰すと、「認証成功」がそのまま「routing成功」に昇格する。

## hardening前は、identityは見ていたがrunの出自を見ていなかった

旧 `PublishAgent` でも投稿先確認は存在した。

profileを明示し、投稿前に認証済みchannelのtitleまたはchannel IDを期待値と比較していた。

しかし、`state.bucket` とprofile bucketの対応は最終gateへ入っていなかった。

```text
認証情報 ──> remote channel ──> identity確認

run bucket ────────────────────> 投稿先判定に未接続
```

つまり、

- 正しいchannelへ認証している
- しかし今回のrunは別用途から来た

という組み合わせを、最後のpublish境界では十分に止められない。

hardening commitでは、run bucketも照合対象へ入った。

https://github.com/KAFKA2306/yt3/commit/d1e2c42cfdfdb18d9962d15c38b87bab919df285

## 3点照合にすると、責務が分かりやすくなる

### 1. bucket — この成果物は何のために作られたか

runの出自を表す。

例えば `byosan_money` なら、このrunは秒算マネー用の成果物である。

### 2. profile — どの公開先設定を選んだか

profile registryには、少なくとも次を持たせる。

```text
profileName
bucket
envFile
expected channel ID
expected title / handle
```

設定値を別々の文字列として散らさない。

**1つの公開先profileとして束ねる。**

### 3. remote identity — 実際にどこへ認証されているか

OAuth後にYouTube APIからcurrent channel identityを取得する。

そして期待channel IDと一致するかを見る。

これで、

```text
intent
configuration
actual remote identity
```

の3つを別々に確認できる。

## 最終gateは「文字列が揃っている」ではなく、関係が揃っているを見る

設定項目を増やすだけでは不十分だった。

例えば、

```text
ENV_FILE=config/.env.byosan
PROFILE=byosan
```

がそれぞれ正しくても、そのrunが本当に `byosan_money` 由来かは別である。

そこで最終判定を、値の存在ではなく関係の整合性として考える。

```text
run.bucket == profile.bucket
AND
selected profile == intended profile
AND
remote channel ID == profile.expected_channel_id
```

どれか1つでも違えばpublishしない。

このfail-closeは、投稿を成功させるためではなく、**間違った成功を作らないため**にある。

## 自動投稿で人が毎回確認していたことを、machine contractへ移す

手動運用なら、投稿直前に人間が画面を見て確認できる。

```text
この動画は秒算マネー用
ログイン中のアカウントも秒算マネー
投稿画面のchannel名も秒算マネー
```

複数channelを自動化すると、この確認が毎回の摩擦になる。

人が覚えている限り安全、という状態は自動化と相性が悪い。

そこで、**人が頭の中でやっていた3点確認をコードへ移す。**

これにより自動化の価値は「投稿ボタンを押さなくてよい」だけではなくなる。

**宛先確認まで委任できる。**

## remote identityを取れないなら、投稿しない

fail-openにすると危険である。

例えばYouTube APIからchannel identityを取得できなかったとき、

```text
identity check unavailable
→ とりあえずpublish
```

にはしない。

```text
identity check unavailable
→ publish blocked
```

にする。

公開系automationでは、確認できないこと自体が重要なstateである。

`unknown` を `match` に変換しない。

## profile registryを正準にすると、CLIやTaskfileも薄くできる

publish taskごとにenv、channel ID、bucketを個別に書くと、設定driftが起こりやすい。

そこでregistryを正準にし、TaskfileやCLIはprofile名だけを渡す形へ寄せる。

```text
publish:byosan
   ↓
profile = byosan
   ↓
registry
   ├─ bucket
   ├─ env file
   └─ expected remote identity
```

こうすると、公開先の意味情報が1か所に集まる。

ADRやdocsが古くなっても、runtime contractがどこにあるか分かりやすい。

今回ADRとの差分を見つけたこと自体も、**文書と正準runtime stateを別物として監査する必要性**を示している。

## この設計はYouTube以外でも使える

本質は動画投稿ではない。

例えば、

- X / Blueskyへの自動投稿
- 複数AWS accountへのdeploy
- staging / production環境へのrelease
- 複数顧客tenantへのdata delivery
- 複数bucketへのartifact upload

でも同じである。

```text
what is this run for?
which destination profile was selected?
what destination is actually authenticated/connected?
```

この3問が一致するかを見る。

## 3点照合だけでも防げないこと

この設計はrouting mismatchを減らす。

しかし、

- 内容自体が誤っている
- 同じchannel内でplaylistを間違える
- 公開日時を間違える
- OAuth account自体が侵害されている

といった問題は別である。

だから「3点照合があるから安全」ではなく、**投稿先という1つのfailure modeを機械的に閉じる**ためのcontractと考える。

## まず1つのpublish jobへ入れるなら

現在の自動publish処理で、次を記録する。

```yaml
run_intent: byosan_money
selected_profile: byosan
remote_identity: UCxxxxxxxx
```

そしてpublish直前に一致を確認する。

```text
intent ↔ profile
profile ↔ remote identity
```

それだけでも、「認証が通ったから投稿する」から一段強くなる。

自動化を増やすほど、成功率だけを上げるのでは足りない。

**間違った場所へ成功しないこと**も、同じくらい重要だ。
