<!-- pipeline_meta: {"idea_source":"public-github-engineering","idea_only":true,"raw_private_content_persisted":false,"topic":{"title":"Codexの結果コピペをやめたくて、private GitHub IssueをAI間のメッセージキューにした","audience":"ChatGPTとローカルCodex CLIを併用するエンジニア","central_question":"ChatGPTとローカルCodex CLIの間で、結果のコピペをせず、安全に実行結果を受け渡せるか","surprising_finding":"難所はCodex実行ではなく、ChatGPT側のGitHub write可否、Codexの追加app/plugin初期化、実行権限境界の3点だった","initial_hypothesis":"private Issueをqueueにすれば単純なpollingだけで成立する","hypothesis_update":"queue自体は単純だが、read-only標準経路・設定隔離・cwd allowlist・smoke testを先に設計しないと自律実行器として危険または不安定になる","stakes":"ローカルagentの結果をChatGPTへ戻す手作業を減らしつつ、credentialや任意ディレクトリ実行を公開しない","story_type":"unexpected-boundary","public_evidence":["https://github.com/KAFKA2306/KAFKA2306/blob/815bcb8ae7086cc4eb558be73d5f0a1b469d788a/scripts/install-codex-chatgpt-bridge.ps1","https://github.com/KAFKA2306/KAFKA2306/blob/0e70df6041cc78f59727a53cee9b09671b56ed10/scripts/codex-chatgpt-bridge/bridge-daemon.ps1","https://github.com/KAFKA2306/KAFKA2306/blob/0e7f6b6b8344a19ad4ce350a0d19e84cc10f7f86/scripts/codex-chatgpt-bridge/README.md","https://github.com/openai/codex","https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt","https://cli.github.com/manual/gh_auth_login"]}} -->

# Codexの結果コピペをやめたくて、private GitHub IssueをAI間のメッセージキューにした

ローカルの Codex CLI に調査や修正を任せたあと、最後の出力を ChatGPT に貼り直す。

数回なら気になりません。しかし、調査 → 修正 → テスト → 次の指示、と往復するほど、毎回のコピー＆ペーストがワークフローそのものになります。

そこで考えたのが、**private GitHub Issue を ChatGPT とローカル Codex の受け渡し場所にする**方法でした。

最初の想定は単純でした。

```text
ChatGPT
  ↓
private GitHub Issue
  ↓
local daemon
  ↓
Codex CLI
  ↓
private GitHub Issue
  ↓
ChatGPT
```

Issue comment を queue にするだけなら、RedisもWebhook serverも公開APIもいりません。

しかし、実装を進めると、本当に難しかったのは queue ではありませんでした。

1. ChatGPT から GitHub に「書ける」とは限らない
2. Codex の本体処理と、普段使っている app / plugin / MCP の初期化を分けないといけない
3. ローカル agent にどこまで書き込みを許すかを queue より先に決めないと危険

この3点を分離した結果、公開版は **1コマンド installer + private queue + Windows daemon + read-only既定 + cwd allowlist + end-to-end smoke test** という構成になりました。

公開実装:
https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge

> **公開昇格条件**
> この原稿は記事候補です。最新公開bundleを実機で再installし、installer末尾の `BRIDGE_OK` と worker payload の `exit_code: 0` を確認するまで、`articles/` へは昇格しません。

## まず前提を壊した：ChatGPTのGitHub appは標準ではread-only

最初は「ChatGPT が Issue に task を書き、Codex が結果を書き戻す」完全双方向を標準形にするつもりでした。

ところが OpenAI の GitHub app 公式Helpは、通常の GitHub app について **repositoryを読み取り、分析・検索するためのもの**と説明し、コード更新やPR pushは Codex 製品側の機能だと明記しています。

公式:
https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt

つまり、ChatGPTでGitHubが見えていることと、Issue commentを書けることは同義ではありません。

ここで設計を2つに分けました。

```text
A. Result bridge（標準）
local send-task.ps1
  → private Issue
  → local Codex
  → private Issue
  → ChatGPT reads result

B. Bidirectional bridge（任意）
write-capable GitHub action/plugin
  → private Issue
  → local Codex
  → private Issue
  → ChatGPT
```

標準線を A に置けば、GitHub write action がないChatGPT環境でも、**「Codexの結果をチャットへ貼り直す」作業だけは消せます**。

これが最初の仮説更新でした。

## なぜGitHub Issueなのか

用途はmessage brokerに近いですが、今回ほしい要件はかなり小さいです。

- controller task が残る
- worker result が残る
- private にできる
- `gh` CLI から読める
- ChatGPT から読み取れる環境がある
- task ID で重複処理を防げる
- 失敗時に人間がブラウザから監査できる

GitHub CLI は公式に browser-based login flow を提供しています。

公式:
https://cli.github.com/manual/gh_auth_login

そのため、bridge独自のGitHub token管理を追加する必要はありません。

公開 installer も `gh auth status` を確認し、未認証時だけ公式の `gh auth login --web` へ進みます。

実装:
https://github.com/KAFKA2306/KAFKA2306/blob/815bcb8ae7086cc4eb558be73d5f0a1b469d788a/scripts/install-codex-chatgpt-bridge.ps1

## protocolはMarkdown comment + JSONだけにした

controller側は、Issue comment に機械判定用markerとJSONを置きます。

````md
<!-- codex-bridge:v1 role=controller task=task-20260812-001 -->

```json
{
  "cwd": "D:\\dev\\example",
  "sandbox": "read-only",
  "prompt": "失敗しているテストの原因だけを調べて"
}
```
````

workerは同じ task ID で結果を返します。

```md
<!-- codex-bridge:v1 role=worker task=task-20260812-001 -->
```

結果には final message だけでなく、次も添えます。

- exit code
- sandbox
- absolute cwd
- Git repository root
- HEAD SHA
- bounded `git status --porcelain=v1`

ここで重要なのは、**自然言語だけを返さない**ことです。

「直しました」だけでは、本当に成功したのか、どのrepositoryを触ったのか、未commit差分が残っているのかを次のagentが判断できません。

## 2つ目の失敗：Codex本体ではなく追加機能の初期化で落ちる

non-interactive実行には OpenAI 公式の `codex exec` を使えます。

公式Codex repository:
https://github.com/openai/codex

公開daemonでは最終応答をファイルへ取り出し、JSON event stream はローカルだけに残します。

```powershell
$promptText | & codex exec `
  --ignore-user-config `
  --disable apps `
  --disable plugins `
  --sandbox $sandbox `
  --json `
  --output-last-message $lastMessage `
  -
```

実装:
https://github.com/KAFKA2306/KAFKA2306/blob/0e70df6041cc78f59727a53cee9b09671b56ed10/scripts/codex-chatgpt-bridge/bridge-daemon.ps1

ここは開発中に想定を変えた部分です。

自律daemonに必要なのは、普段の対話型Codex環境を完全再現することではありません。むしろ、普段利用している追加appやpluginの認証・初期化に引きずられると、bridgeのsmoke testまで失敗要因が増えます。

そこで autonomous run だけを user config / app / plugin discovery から分離し、interactive Codex の設定そのものは変更しない構成にしました。

この判断は「便利な環境を全部引き継ぐ」より、**bridgeの依存面を意図的に小さくする**ためのものです。

## 3つ目の問題：private queueでも、任意コマンド実行器にしてはいけない

private repository を使えば安全、ではありません。

Issue comment をローカル実行へ直結すると、queueに書ける主体はローカルPC上の agent に指示を出せます。

そのため公開版では、少なくとも次を固定しました。

```text
queue must be PRIVATE
controller author == configured GitHub login
cwd ∈ AllowedRoot
sandbox ∈ {read-only, workspace-write}
default sandbox = read-only
danger-full-access = rejected
```

特に `AllowedRoot` は重要です。

installer を `D:\dev` で実行したなら、bridge task から `C:\Users\...` や別driveへ勝手に移動できないようにします。

また、調査taskは既定 `read-only` にし、修正が必要なときだけ `workspace-write` を明示します。

OpenAIのCodex CLIもsandboxを実行境界として提供しています。bridge側では、その選択肢をさらに2種類へ絞っています。

## 「インストール成功」をdaemon起動にしない

この種の仕組みは、Scheduled Task が登録できただけでは意味がありません。

そこで installer 自身が最後に temporary Git repository を作り、Issue経由で次のtaskを流します。

```text
This is an end-to-end transport smoke test.
Do not create, modify, or delete any files.
Reply with exactly: BRIDGE_OK
```

成功条件は2つだけです。

```text
final message contains BRIDGE_OK
exit_code == 0
```

3分以内にworker resultが返らない、あるいはexit codeが0でなければinstallerは失敗として停止します。

「daemonを配置できた」と「ChatGPTまで結果を戻せる」は別の状態だからです。

## 1コマンドでどこまで作るか

公開bootstrapは、秘密のrepositoryをcloneしません。

公開bundleをcommit hash固定で取得し、その後の installer が利用者自身のGitHub accountに private queue repository を作ります。

```powershell
$bootstrap = Join-Path $env:TEMP 'install-codex-chatgpt-bridge.ps1'
Invoke-WebRequest -UseBasicParsing `
  -Uri 'https://raw.githubusercontent.com/KAFKA2306/KAFKA2306/815bcb8ae7086cc4eb558be73d5f0a1b469d788a/scripts/install-codex-chatgpt-bridge.ps1' `
  -OutFile $bootstrap
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $bootstrap
```

導入後は、local senderからtaskを投入できます。

```powershell
$send = Join-Path $env:LOCALAPPDATA 'OpenAI\CodexChatGPTBridge\send-task.ps1'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $send `
  -Prompt 'このrepositoryを読み、テスト失敗の原因だけを報告して' `
  -Cwd 'D:\dev\example'
```

公開ガイド:
https://github.com/KAFKA2306/KAFKA2306/blob/0e7f6b6b8344a19ad4ce350a0d19e84cc10f7f86/scripts/codex-chatgpt-bridge/README.md

## この設計で「自律」と呼ばないもの

ここも重要です。

通常のChatGPT GitHub appがread-onlyなら、ChatGPT自身からcontroller taskを書き込む経路は標準機能だけでは成立しません。

また、ChatGPT Scheduled Tasks は connected app を利用できる場合がありますが、利用可否や権限はplan・workspace設定・app設定に依存します。

公式:
https://help.openai.com/en/articles/10291617-tasks-inchatgpt

そのため公開版では、次を分けて表現します。

- **result transport**: private IssueへCodex結果を返す
- **result observation**: ChatGPTがGitHub appから結果を読む
- **task submission**: local sender、またはwrite actionを持つ環境
- **periodic observation**: Scheduled Tasksが利用可能なら追加可能

全部を「完全自律」と一語でまとめません。

## まとめ：queueより先に境界を設計する

今回、最初に作ろうとしたのは「Issueを30秒ごとにpollしてCodexを呼ぶ小さなdaemon」でした。

しかし実装の中心になったのはpollingではありませんでした。

```text
transport boundary
  private Issue + task id

identity boundary
  configured GitHub login only

filesystem boundary
  AllowedRoot

execution boundary
  read-only by default

configuration boundary
  ignore user config / disable app + plugin discovery

completion boundary
  BRIDGE_OK + exit_code 0
```

ローカルAI agentを別のAIから扱うとき、便利な接続経路を作ることより、**どの状態なら成功と呼び、どこから先は実行させないか**を先に決める方が重要でした。

そして、private GitHub Issue は、その境界を人間にも読める形で残せる、かなり小さなtransportになりました。

## 一次情報・実装証拠

- OpenAI Codex: https://github.com/openai/codex
- OpenAI Help — Connecting GitHub to ChatGPT: https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt
- OpenAI Help — Scheduled Tasks: https://help.openai.com/en/articles/10291617-tasks-inchatgpt
- GitHub CLI — `gh auth login`: https://cli.github.com/manual/gh_auth_login
- 公開bootstrap: https://github.com/KAFKA2306/KAFKA2306/blob/815bcb8ae7086cc4eb558be73d5f0a1b469d788a/scripts/install-codex-chatgpt-bridge.ps1
- 公開daemon: https://github.com/KAFKA2306/KAFKA2306/blob/0e70df6041cc78f59727a53cee9b09671b56ed10/scripts/codex-chatgpt-bridge/bridge-daemon.ps1
- 公開guide: https://github.com/KAFKA2306/KAFKA2306/blob/0e7f6b6b8344a19ad4ce350a0d19e84cc10f7f86/scripts/codex-chatgpt-bridge/README.md
