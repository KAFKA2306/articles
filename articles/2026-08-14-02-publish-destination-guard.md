---
title: "YouTubeの自動投稿先を、投稿直前に3点で照合する"
emoji: "🛡️"
type: "tech"
topics: ["typescript", "youtube", "automation", "testing", "security"]
published: false
---

**認証に成功した相手を、意図した投稿先だと思い込むな。**

動画生成、OAuth、YouTube API、CIが全部成功しても、違うチャンネルへ投稿したら事故になる。[yt3のADR 0038](https://github.com/KAFKA2306/yt3/blob/main/docs/adr/0038-publish-destination-guard.md)では`byosan` profileのbucketが`daily_pulse`、[現行registry](https://github.com/KAFKA2306/yt3/blob/main/src/domain/youtube_profiles.ts)と[routing監査](https://github.com/KAFKA2306/yt3/blob/main/src/scripts/audit_publish_routing.ts)では`byosan_money`だった。

これは**実際の誤投稿事故を観測した証拠ではない**。しかし認証は「誰としてアクセスできるか」を示すだけで、「このrunがそこへ投稿する意図か」を保証しない。そこでpublish直前に**runの目的・選択profile・remote identity**を照合する。

汎用規律は **「書き込みができるかより先に、そこへ書いてよいかを確かめよ」**。

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

## アップロードせずに投稿先を3ケースで試す

`byosan_money`を用途とする実行から、投稿前のrouting checkだけを切り出す。以下は**dry-runの期待結果**であり、実際のYouTubeチャンネルIDや秘密情報は含まない。

| 入力 | 期待結果 | 根拠 |
| --- | --- | --- |
| `bucket=byosan_money`、`profile=byosan`、登録済みremote ID | 通過 | 用途・profile・認証先の対応が一致 |
| `bucket=byosan_money`、`profile=humanity` | 拒否 | runの用途とprofileが食い違う |
| `bucket=byosan_money`、`profile=byosan`、remote ID取得失敗 | 拒否 | 実際の宛先が不明 |

三つとも**アップロードAPIを呼ばない**。実行ID、選んだprofileの版、ID照合の成否、拒否理由を記録する。正常ケースが通っても動画の内容、公開日時、再生リストが正しいとは限らない。3点照合の完了を「投稿全体が安全」とは言わない。

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

自動投稿処理から、投稿前の実行データ、選んだ公開先の設定、認証済みチャンネルのIDを一つずつ取り出す。

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

照合だけを試し、投稿は呼ばない。三つが対応する例は先へ進み、別用途の実行データ、別チャンネルのID、IDの取得失敗はそれぞれ停止することを確認する。

自動化を増やすほど、成功率だけを上げるのでは足りない。

**間違った場所へ成功しないこと**も、同じくらい重要だ。


## 他の宛先でも使う条件と撤回条件

メール送信、クラウドストレージへの保存、決済先の指定も、成功応答が正しい宛先を保証しないときには同じ設計を検討できる。これは**応用仮説**であり、それらの事故が減った実績ではない。

目的と認証先が技術的に一対一に固定され、不一致が起こらないことを実環境と検査で証明できるなら、投稿直前の3点照合は簡素化できる。一方、remote identityの取得に失敗したとき、直前の値へ黙って戻すと誤投稿を見逃す。**目的を証明できなければ書き込まない。**
