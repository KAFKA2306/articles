---
title: "private GitHub IssueをAI間キューにした。最初のsmokeで壊れたのはqueueではなくCodexの初期化だった"
emoji: "🔁"
type: "tech"
topics: ["chatgpt", "codex", "github", "powershell", "automation"]
published: false
published_at: 2026-08-12 17:02
---

ローカルの Codex CLI に調査や修正を任せたあと、最後の出力を ChatGPT に貼り直す。

このコピー＆ペーストを消すために、private GitHub Issueをtask/resultの受け渡し場所にしました。

```text
ChatGPT / local sender
  ↓
private GitHub Issue
  ↓
local daemon
  ↓
Codex CLI
  ↓
private GitHub Issue
```

Issue commentをpollしてCodexを呼ぶ。最初は、難しいのはこのtransportだと思っていました。

ところが開発中の最初のsmoke testで、**Issue queueではなく、Codex本体が応答する前に追加MCP/app層のOAuth要求で落ちました。**

transportが通ってもworkerが起動しない。さらに調べると、ChatGPT側のGitHub write可否、空repositoryのHEAD、local agentのfilesystem権限まで、それぞれ別の境界として扱わないといけませんでした。

ここで問いが変わりました。

**「Issueをどうqueueにするか」ではなく、「普段の対話型Codex環境から、自律workerに必要な能力だけをどこまで削れるか」。**

最終的に2026-08-12 16:54 JSTのE2Eでは、private queueを通したworkerが `exit_code: 0` と `BRIDGE_OK` を返しました。ただし、そこへ到達するまでに壊れた場所を順に追うと、bridgeの本体がpollingではなく境界設計だったことが分かります。

公開実装:
https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge

検証記録:
https://github.com/KAFKA2306/KAFKA2306/blob/9f9c05d10ae2c10109ba4ad1d460057a85779a80/scripts/codex-chatgpt-bridge/VERIFICATION.md

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
https://github.com/KAFKA2306/KAFKA2306/blob/7405e79a2f15d38c455d652e3f91f2b04269b42a/scripts/install-codex-chatgpt-bridge.ps1

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
https://github.com/KAFKA2306/KAFKA2306/blob/864774f15d7fc6522572a8e326dfa78573b0df74/scripts/codex-chatgpt-bridge/bridge-daemon.ps1

開発中の最初のsmokeでは、Codex本体の応答以前に、追加MCP/app層のOAuth要求で失敗しました。

ここで考え方を変えました。

自律daemonに必要なのは、普段の対話型Codex環境を完全再現することではありません。むしろ、普段利用している追加appやpluginの認証・初期化に引きずられると、bridgeのsmoke testまで失敗要因が増えます。

そこで autonomous run だけを user config / app / plugin discovery から分離し、interactive Codex の設定そのものは変更しない構成にしました。

この失敗と修正の時系列は公開verification recordにも残しています。

https://github.com/KAFKA2306/KAFKA2306/blob/9f9c05d10ae2c10109ba4ad1d460057a85779a80/scripts/codex-chatgpt-bridge/VERIFICATION.md

## 3つ目の問題：smoke用repositoryにもHEADが必要だった

次に出た失敗は、もっと地味でした。

installer は smoke test 用に空の Git repository を `git init` していました。しかし空repositoryにはまだ有効な `HEAD` commit がありません。

bridgeはworker resultへHEAD SHAも添えるため、smoke repository自身にもbaseline commitを作るよう変更しました。

現在のinstallerでは、temporary repositoryを初期化したあと、global Git configを変更せずに空commitを1つ作ります。

```powershell
& git -C $smokeRepo `
  -c 'user.name=Codex Bridge Smoke' `
  -c 'user.email=codex-bridge-smoke@localhost' `
  commit --allow-empty -m 'smoke baseline'
```

修正commit:
https://github.com/KAFKA2306/KAFKA2306/commit/23640ccec32355cad91bb7cfeed34845db54824c

「Git repositoryがある」と「参照できるHEADがある」も別の状態でした。

## 4つ目の問題：private queueでも、任意コマンド実行器にしてはいけない

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

「daemonを配置できた」と「Codexの結果をqueueまで戻せる」は別の状態だからです。

実際のE2E記録でも、この2条件を満たした時点だけを成功として残しています。

https://github.com/KAFKA2306/KAFKA2306/blob/9f9c05d10ae2c10109ba4ad1d460057a85779a80/scripts/codex-chatgpt-bridge/VERIFICATION.md

## 1コマンドでどこまで作るか

公開bootstrapは、秘密のrepositoryをcloneしません。

公開bundleをcommit hash固定で取得し、その後の installer が利用者自身のGitHub accountに private queue repository を作ります。

```powershell
$bootstrap = Join-Path $env:TEMP 'install-codex-chatgpt-bridge.ps1'
Invoke-WebRequest -UseBasicParsing `
  -Uri 'https://raw.githubusercontent.com/KAFKA2306/KAFKA2306/7405e79a2f15d38c455d652e3f91f2b04269b42a/scripts/install-codex-chatgpt-bridge.ps1' `
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
https://github.com/KAFKA2306/KAFKA2306/blob/c1ea710695ab71647b9e2d2f9d07caf6ec84bfce/scripts/codex-chatgpt-bridge/README.md

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

今回、最初に作ろうとしたのは「IssueをpollしてCodexを呼ぶ小さなdaemon」でした。

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

そして、private GitHub Issue は、その境界を人間にも読める形で残せる、小さなtransportになりました。

## 一次情報・実装証拠

- OpenAI Codex: https://github.com/openai/codex
- OpenAI Help — Connecting GitHub to ChatGPT: https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt
- OpenAI Help — Scheduled Tasks: https://help.openai.com/en/articles/10291617-tasks-inchatgpt
- GitHub CLI — `gh auth login`: https://cli.github.com/manual/gh_auth_login
- 公開bootstrap: https://github.com/KAFKA2306/KAFKA2306/blob/7405e79a2f15d38c455d652e3f91f2b04269b42a/scripts/install-codex-chatgpt-bridge.ps1
- 公開daemon: https://github.com/KAFKA2306/KAFKA2306/blob/864774f15d7fc6522572a8e326dfa78573b0df74/scripts/codex-chatgpt-bridge/bridge-daemon.ps1
- 公開guide: https://github.com/KAFKA2306/KAFKA2306/blob/c1ea710695ab71647b9e2d2f9d07caf6ec84bfce/scripts/codex-chatgpt-bridge/README.md
- E2E verification: https://github.com/KAFKA2306/KAFKA2306/blob/9f9c05d10ae2c10109ba4ad1d460057a85779a80/scripts/codex-chatgpt-bridge/VERIFICATION.md
