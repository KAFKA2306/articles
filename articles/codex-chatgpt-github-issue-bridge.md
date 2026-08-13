---
title: "AIにPCを触らせる橋は、どこまで信用していい？ Codex workerの権限境界を作った"
emoji: "🔁"
type: "tech"
topics: ["chatgpt", "codex", "github", "security", "automation"]
published: true
published_at: 2026-08-12 17:02
---

# AIにPCを触らせる橋は、どこまで信用していい？ Codex workerの権限境界を作った

private GitHub Issueをtask queueにして、ローカルPC上のCodex workerへ指示を渡す仕組みを作りました。

```text
controller
  ↓
private GitHub Issue
  ↓
local worker
  ↓
Codex
  ↓
result
```

最初は「private repositoryなら十分安全では？」と考えました。

しかしIssue commentをローカル実行へ接続した瞬間、そのqueueに書ける主体は**ローカルPC上のAIへ命令できる主体**になります。

つまり安全境界はGitHub Issueそのものではありません。

この記事では、bridgeの導入手順ではなく、**AI workerへローカル操作権限を渡すときに、何を明示的に狭めたか**だけを扱います。

公開実装:
https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge

E2E検証記録:
https://github.com/KAFKA2306/KAFKA2306/blob/9f9c05d10ae2c10109ba4ad1d460057a85779a80/scripts/codex-chatgpt-bridge/VERIFICATION.md

## private queueはsecurity boundaryではない

private repositoryにすれば、公開インターネットから誰でもtaskを書ける状態は避けられます。

しかし、privateであることだけでは次を防げません。

```text
認証済みだが想定外のuserがtaskを書く
cwdをPC内の任意場所へ向ける
強すぎるsandboxを要求する
workerへ危険なpromptを送る
resultへlocal情報を大量に返す
```

したがってbridge側では、queueのprivacyとは別に実行契約を持たせました。

```text
queue      = private
controller = configured GitHub login
cwd        = AllowedRoot配下
sandbox    = read-only | workspace-write
default    = read-only
full access = reject
```

ここで中心になるのは**権限を追加するより、受け付ける命令の集合を狭くすること**です。

## 1. 誰のtaskを実行するか

「Issueにcontroller markerがある」だけでは足りません。

workerはcontroller commentのauthorを、installer時に固定したGitHub loginと照合します。

```text
comment exists
AND protocol marker is valid
AND author == configured controller
```

この条件を通らないcommentは実行対象にしません。

queueをprivateにすることと、**queue内のどのidentityを信頼するか**は別問題だからです。

## 2. どのdirectoryを触れるか

workerへ`cwd`を渡せる設計は便利ですが、そのままではPC全体が作業対象になります。

そこでinstaller時に`AllowedRoot`を固定し、task側の`cwd`はその配下だけ許可します。

```text
AllowedRoot = D:\dev

OK
D:\dev\project-a
D:\dev\project-b

REJECT
C:\Users\...
D:\private-data
```

この境界を入れると、promptに別pathが書かれていても、task contract自体で止められます。

filesystem permissionを自然言語promptだけへ委ねないことが重要です。

## 3. sandboxをtaskごとに無制限に選ばせない

bridgeでは受け付けるsandboxを2種類へ絞りました。

```text
read-only
workspace-write
```

既定値は`read-only`です。

調査だけならwrite permissionを与えず、修正が必要なtaskだけ明示的に`workspace-write`へします。

「workerが必要そうなら自分で権限を上げる」という設計にはしません。

この原則はCodex固有というより、local agent一般のleast privilegeです。

## 4. 普段のCodex環境をそのままdaemonへ持ち込まない

bring-up中の最初のsmoke testでは、queue transportではなく、Codexが本体応答へ到達する前に追加MCP/app層のOAuth要求で止まりました。

検証記録にも、この失敗と修正が残っています。

https://github.com/KAFKA2306/KAFKA2306/blob/9f9c05d10ae2c10109ba4ad1d460057a85779a80/scripts/codex-chatgpt-bridge/VERIFICATION.md

そこでautonomous workerでは、interactive利用時の追加app/plugin discoveryをそのまま引き継がない構成へ変更しました。

理由はsecurityだけではありません。daemonに不要な外部依存を持ち込むと、

```text
認証要求
MCP初期化
plugin discovery
外部service停止
```

までworker availabilityの失敗要因になります。

自律workerの能力は、普段のinteractive environmentのスーパーセットではなく、**taskに必要な最小subset**へします。

## 5. 成功判定を「daemonが起動した」にしない

権限境界を作っても、実際にtask→worker→resultが通らなければbridgeは完成していません。

公開verification recordでは、2026-08-12のE2Eで次が記録されています。

```text
worker exit_code = 0
final message     = BRIDGE_OK
```

また同記録では、Scheduled Task登録、daemon process開始、controller comment作成だけでは成功証拠にしないと明記しています。

一次証拠:
https://github.com/KAFKA2306/KAFKA2306/blob/9f9c05d10ae2c10109ba4ad1d460057a85779a80/scripts/codex-chatgpt-bridge/VERIFICATION.md

つまりcompletion contractは、

```text
transport exists
!=
worker executed successfully
```

です。

## 6. resultにも境界が必要

AI workerの出力は便利ですが、そのまま公開queueへ返す設計は避けました。

実際のbridge resultには、local path、repository state、task outputなどが含まれ得ます。そのためraw queueはprivateのままにし、公開verificationにはsmoke testに必要な最小情報だけを残しています。

これは「input permission」だけでなく「output disclosure」もsecurity boundaryだからです。

```text
input boundary
  who / cwd / sandbox

execution boundary
  worker capability

output boundary
  what may leave the machine
```

## ChatGPTのGitHub接続とwrite権限を混同しない

OpenAI公式Helpでは、ChatGPTのGitHub appはrepositoryを読み取り、分析・検索する用途として説明されており、コードの生成・編集・pushはCodex側の機能として分けられています。

公式:
https://help.openai.com/en/articles/11145903

したがって、

```text
ChatGPTからrepositoryが見える
```

ことと、

```text
ChatGPTが任意のIssueへ書き込める
```

ことは同義ではありません。

bridge設計では、controller transportを「どのChatGPT環境でも当然write可能」と仮定しません。

## 最小security contract

同種のlocal worker bridgeを作るなら、少なくとも次をコード上の契約にします。

```yaml
queue:
  visibility: private

controller:
  allowed_login: fixed

filesystem:
  allowed_root: fixed

execution:
  default_sandbox: read-only
  allowed_sandboxes:
    - read-only
    - workspace-write

completion:
  require_exit_code_zero: true
  require_expected_result: true

output:
  raw_result_visibility: private
```

ここまでを自然言語の「気をつける」ではなく、reject conditionとして実装するのが重要です。

## まとめ

private GitHub Issueは便利なtransportです。しかし、それ自体をsecurity boundaryとして扱うと危険です。

AI workerへPC操作権限を渡すなら、少なくとも、

- 誰のtaskを実行するか
- どのdirectoryを触れるか
- どのsandboxを許すか
- interactive環境の何を持ち込まないか
- 何を成功証拠とするか
- どのresultを外へ出すか

を別々のcontractとして固定する必要があります。

今回のbridgeで一番重要だったのはIssue pollingではありませんでした。

**transportを作ることより、workerができることを狭く定義すること。**

そこが、AIにローカルPCを触らせる仕組みの本体でした。

## 一次情報・実装証拠

- Bridge implementation: https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge
- E2E verification: https://github.com/KAFKA2306/KAFKA2306/blob/9f9c05d10ae2c10109ba4ad1d460057a85779a80/scripts/codex-chatgpt-bridge/VERIFICATION.md
- Hardened daemon commit: https://github.com/KAFKA2306/KAFKA2306/commit/864774f15d7fc6522572a8e326dfa78573b0df74
- OpenAI — Connecting GitHub to ChatGPT: https://help.openai.com/en/articles/11145903
