---
title: "GitHub IssueをAIの実行キューにしてよいのか？ Codex・Copilot・Actionsと比べて分かった境界"
emoji: "🔁"
type: "tech"
topics: ["codex", "github", "copilot", "security", "automation"]
published: false
published_at: 2026-08-12 17:02
---

# GitHub IssueをAIの実行キューにしてよいのか？ Codex・Copilot・Actionsと比べて分かった境界

GitHub Issueに仕事を書き、AI coding agentへ渡す。

2026年現在、この発想自体はもう珍しくありません。

GitHub Copilot cloud agentはIssueを割り当てると作業を行い、Pull Requestを作成して人間へレビューを依頼します。GitHubはOpenAI Codexを含むthird-party coding agentsについても、Issueやpromptから非同期に作業を委譲し、PRでレビューする流れを公式に提供しています。

- GitHub Docs — Kick off a task with Copilot agents:
  https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/kick-off-a-task
- GitHub Docs — About third-party coding agents:
  https://docs.github.com/en/copilot/concepts/agents/about-third-party-coding-agents

OpenAI側も、Codexをrepositoryに接続し、コードの理解・修正・テスト・レビューを行うcoding agentとして提供しています。

- OpenAI Developers:
  https://developers.openai.com/
- OpenAI — Running Codex safely at OpenAI:
  https://openai.com/index/running-codex-safely/

では、なぜ私はわざわざ

```text
GitHub Issue
  ↓
Windowsの常駐daemon
  ↓
ローカルCodex CLI
```

というbridgeを作ったのでしょうか。

結論から言うと、この仕組みの価値は**「IssueからAIを起動できたこと」ではありません**。

本当に考える価値があったのは、

> cloud上のcoding agentではなく、自分のローカルPCまでAIの実行経路を伸ばすなら、どんな安全境界を追加しなければならないか

という問題でした。

この記事では、自作bridgeを単独の成功談として扱いません。

GitHub Issues、Copilot/Codexのagent workflow、GitHub Actionsのself-hosted runner、OpenAIが公開しているCodexの安全設計と比較しながら、**AIへ仕事を委譲するシステムの一般的な設計原則**としてレビューします。

公開実装:
https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge

---

## 先に結論：repositoryだけで完結するなら、自作bridgeは第一選択ではない

2026年時点の選択肢を大きく分けると、次のようになります。

| 方法 | 実行場所 | 向いている仕事 | 主な境界 |
|---|---|---|---|
| GitHub Copilot / third-party coding agent | cloud | repositoryの調査・修正・テスト・PR | branch / PR / review / agent policy |
| Codexのrepository workflow | cloud中心 | repositoryを使ったcoding task | environment / sandbox / review |
| GitHub Actions GitHub-hosted runner | ephemeral VM | 再現可能なCI・build・test | workflow permissions / secrets |
| GitHub Actions self-hosted runner | 自分のmachine | 特殊hardwareや社内networkが必要なCI | runner access / workflow trust |
| 自作local bridge | 自分のPC | local file、GUI、device、既存認証などが必要 | controller / path / sandbox / tool / output |

GitHubは、Issueをcoding agentへ割り当て、agentがPRを作り、人間がその差分をレビューする流れを正式なworkflowとして提供しています。

さらにGitHubは、Copilotが生成したPRについても「通常のcontributionと同じように十分レビューする」よう明記しています。required reviewが設定されているrepositoryでは、Copilot PRに対する本人のapprovalだけではrequired approvalとして数えない仕組みもあります。

GitHub Docs:
https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/review-copilot-output

したがって、一般的なrepository修正だけが目的なら、

```text
Issue
  ↓
agent
  ↓
branch
  ↓
Pull Request
  ↓
CI + human review
```

という既存の経路を優先する方が自然です。

**local PCを直接実行環境にする理由がないなら、local PCを実行環境にしない。**

これが最初のレビュー結論です。

---

## 一般原則1：Issueは「仕事の記録」であって「実行権限」ではない

GitHubはIssuesを、ideas、feedback、tasks、bugsなどを計画・追跡するための仕組みとして説明しています。

GitHub Docs:
https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues

Projectsのbest practicesでも、IssuesとPull Requestsを作業のsingle source of truthとして使い、仕事を分解し、状態や依存関係を追跡することが推奨されています。

GitHub Docs:
https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects

ここで重要なのは、

```text
Issueに書かれている
```

ことと、

```text
その内容をmachine上で実行してよい
```

ことは別だという点です。

Issueはcontrol planeとしては優秀です。

- 誰が依頼したか残る
- 何を依頼したか残る
- commentで状態を追える
- PRやcommitと関連づけられる
- 人間が後から監査できる

一方で、Issue本文やcommentをそのままshell command相当の権限へ変換すれば、Issueは事実上remote execution interfaceになります。

その瞬間から必要なのは「Issueの使い方」ではなく、**実行系のsecurity design**です。

この区別は、自作bridgeだけの話ではありません。

GitHubのcoding agentsも、Issueを受け取った後はagent sessionとbranch/PRへ作業場所を移します。Issueをそのままproduction変更権限として扱っているわけではありません。

---

## 一般原則2：agentの能力より先に、実行環境を狭くする

OpenAIが2026年に公開したCodexの安全運用では、中心となる考え方として

- managed configuration
- constrained execution
- network policies
- agent-native logs
- sandboxing
- approvals

が挙げられています。

OpenAI:
https://openai.com/index/running-codex-safely/

特にOpenAIは、sandboxを

- どこへwriteできるか
- networkへ到達できるか
- どのpathを保護するか

といった**technical execution boundary**として説明し、approval policyとは分離しています。

これは重要です。

AIへのpromptに

```text
危ないことはしないで
他のfolderは見ないで
```

と書くことは、境界ではありません。

境界とは、agentがその指示を無視しても突破できない仕組みです。

```text
prompt rule     = AIへの依頼
sandbox rule    = 実行系による強制
```

この2つを混同しないことが、agentic systemの基本になります。

---

## 一般原則3：「自分のPCで動かす」はcloudより強い理由が必要

local executionには大きな利点があります。

例えば、

- cloudへ置けないlocal dataを読む
- 自宅や社内network上のserviceへ接続する
- local GPUを使う
- Windows専用toolやGUI applicationを操作する
- local deviceやhardwareを扱う
- 既にlocal machine上にある認証済みserviceを使う

といった用途です。

しかし、その代わりに実行環境が**長寿命の実machine**になります。

ここはGitHub Actionsのself-hosted runnerに非常に近い問題です。

GitHubはself-hosted runnerについて、ephemeralでcleanなVMである保証がなく、untrusted codeによって継続的にcompromiseされる可能性があると警告しています。public repositoryではself-hosted runnerをほぼ使うべきではなく、private/internal repositoryでもforkやPRを作れる利用者を信頼できるか注意するよう明記しています。

GitHub Docs — Secure use reference:
https://docs.github.com/en/actions/reference/security/secure-use

GitHub Docs — Adding self-hosted runners:
https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners

自作bridgeも本質的には同じです。

```text
cloud agent
  = disposableな作業環境へ仕事を持っていく

local bridge
  = 普段使っているmachineへ仕事を持ってくる
```

後者の方が、漏洩・誤操作・永続化のblast radiusは大きくなりやすい。

したがって、local bridgeは便利だから使うのではなく、**localでなければ達成できない仕事があるときだけ使う**のが妥当です。

---

## 一般原則4：最小権限は「アカウント」だけでなく5層に分ける

least privilegeという言葉はよく使われますが、coding agentでは「token権限を小さくする」だけでは足りません。

少なくとも次の5層があります。

```text
1. Identity
   誰がtaskを発行できるか

2. Filesystem
   どこをread/writeできるか

3. Process
   どのcommand・programを起動できるか

4. Network / Tool
   どのservice、MCP、APIへ接続できるか

5. Output
   実行結果をどこへ返してよいか
```

GitHub Copilot cloud agentでもinternet accessはfirewallで制限でき、GitHubはその目的をdata exfiltration riskの管理だと説明しています。

GitHub Docs:
https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-the-firewall

つまり、agent securityは「入力を守る」だけではありません。

**出ていく通信と出力も境界です。**

---

## 一般原則5：仕事の完了点は「agentが止まった」ではなくreviewable artifactにする

AI automationで最も危険な曖昧さの1つが、成功条件です。

```text
processが起動した
agentが返事をした
fileが変わった
```

これらは、仕事が正しく完了した証拠ではありません。

GitHubのcoding agent workflowがPR中心になっているのは、この点でも合理的です。

PRなら、

- diff
- commit
- CI
- review comments
- approvals
- merge status

を1つのreviewable artifactに集約できます。

GitHubはCopilotの出力について、人間が通常のPRと同様にreviewすることを明示しています。またCopilot code reviewについても、すべての問題を発見できる保証はなく、人間のreviewで補完するよう案内しています。

GitHub Docs:
https://docs.github.com/en/copilot/concepts/agents/code-review

この考え方を一般化すると、agent taskのcompletion contractは次のようになります。

```text
execution success
  + expected behavior
  + machine-verifiable checks
  + reviewable diff/artifact
  + human acceptance when required
```

単なる`exit_code = 0`より一段強い契約です。

---

# では、自作bridgeは何をしているのか

ここまでの一般原則を踏まえて、実際のbridgeをレビューします。

構成は次の通りです。

```text
ChatGPT / sender
        │
        │ controller task
        ▼
private GitHub Issue
        │
        │ GitHub CLI polling
        ▼
Windows bridge daemon
        │
        │ codex exec
        ▼
local Codex CLI
        │
        │ final response + exit code + git evidence
        ▼
private GitHub Issue
```

実装:
https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/bridge-daemon.ps1

この設計を、先ほどの5層で見ます。

---

## 1. Identity：誰のtaskを実行するか固定する

bridge daemonはIssue commentを順番に読みますが、すべてのcommentを実行するわけではありません。

実装では、comment authorのGitHub loginがinstallerで設定した`ControllerLogin`と一致する場合だけ処理対象にします。

さらに、commentには

```text
codex-bridge:v1
role=controller
task=...
```

というmarkerとJSON blockが必要です。

つまり、概ね

```text
正しい形式
AND
正しいmarker
AND
comment author == ControllerLogin
```

で初めてtaskになります。

これは一般原則として、

> collaboration権限とexecution authorityを分離する

という意味があります。

private repositoryに入れることと、local PCへ命令できることを同一視していません。

---

## 2. Filesystem：`AllowedRoot`から外へ出さない

taskは`cwd`を指定できます。

しかしdaemonは、指定されたpathを正規化した上で、install時に設定した`AllowedRoot`配下かを検査します。

例えば、

```text
AllowedRoot = D:\dev
```

なら、

```text
OK
D:\dev\project-a
D:\dev\project-b

REJECT
C:\Users\...
D:\private-data
```

となります。

この制限はpromptではなくPowerShell側で実行されます。

ここはOpenAIが説明するsandboxの考え方と同じ方向です。

**自然言語で「見ないで」と頼むのではなく、path boundaryをprogramで強制する。**

---

## 3. Process / Filesystem：既定を`read-only`にする

bridgeのsandbox既定値は`read-only`です。

許可されている値も、

```text
read-only
workspace-write
```

だけです。

それ以外はdaemonが拒否します。

つまり、

```text
調査
→ read-only

変更が必要
→ workspace-writeを明示
```

という昇格方式です。

これは「agentに何でもできる状態を与え、promptで抑制する」より安全です。

一方で注意も必要です。

`workspace-write`を許可した時点で、AllowedRoot内の対象workspaceに対する変更能力は生まれます。したがって重要なrepositoryでは、最終的な保護をagent sandboxだけに依存せず、Git branch、PR、CI、review rulesで二重化する方がよいでしょう。

---

## 4. Tool：interactive環境をそのままautonomous runへ持ち込まない

このbridgeで実際に起きた失敗の1つが、普段使いのCodex環境にある追加MCP/app層がOAuth認証を要求し、自動実行が停止したことでした。

検証記録:
https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/VERIFICATION.md

その後、autonomous runでは

```text
--ignore-user-config
--disable apps
--disable plugins
```

を指定し、interactive Codexの設定・apps・pluginsから分離しました。

local MCPもdeny-by-defaultで、daemonにhard-codeしたallowlistとtask側の明示opt-inの両方が必要です。

現在の公開実装で許可されているlocal MCPは`youtube_music`だけです。

実装:
https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/bridge-daemon.ps1

この失敗から得られる一般知見は、

> 人間向けの便利なinteractive environmentと、無人実行用のruntime profileを分離する

ことです。

便利機能を全部載せるほどagentが賢くなるとは限りません。

無人実行では、tool surfaceが増えるほど

- credential
- network destination
- failure mode
- side effect

も増えます。

---

## 5. Output：結果も機密情報になり得る

bridgeはCodexのfinal messageだけでなく、

- task ID
- exit code
- sandbox
- MCP names
- cwd
- Git HEAD
- Git status

などのevidenceをworker resultとして返します。

一方、raw JSONL event logはlocal runtimeにだけ保持します。

公開されているE2E verificationも、raw queueそのものではなく、必要最小限の結果だけです。

理由は、task outputに

- local path
- repository state
- private task内容

などが含まれる可能性があるためです。

検証記録:
https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/VERIFICATION.md

これはGitHub Copilotがagent firewallをdata exfiltration対策として扱っていることとも整合します。

AI systemでは、

```text
何を読ませるか
```

だけでなく、

```text
何を外へ送れるか
```

を同じ重要度で考える必要があります。

---

# 実際のE2Eで分かったこと

2026-08-12の公開verificationでは、bridgeの成功条件を

```text
worker exit_code = 0
final Codex message = BRIDGE_OK
```

の両方にしました。

検証記録:
https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/VERIFICATION.md

ここでは、

```text
Scheduled Taskを登録できた

daemonが起動した

Issue commentを読めた
```

だけでは成功にしていません。

bring-up中には、

1. unrelated MCP/app layerのOAuth要求
2. smoke用Git repositoryにvalid HEADがない

という2つのfailure classも記録されています。

それぞれ、

- autonomous runからuser config/apps/pluginsを分離
- smoke repositoryへbaseline commitを作る

という形で修正されました。

この部分は単なる実装メモ以上の意味があります。

**agentic workflowは、happy pathのdemoよりfailure boundaryの方が設計情報として価値が高い**からです。

---

# ただし、このbridgeにも残る弱点がある

自作したからといって、これを「安全」と言い切るべきではありません。

一般的なagent architectureと比べると、まだ重要な差があります。

## 1. 長寿命のlocal machineである

GitHub-hosted runnerやcloud agentのようなdisposable environmentではありません。

local machineがcompromiseされた場合、影響が次のtaskにも残る可能性があります。

この点はGitHubがself-hosted runnerについて警告している問題と同型です。

## 2. network policyをbridge独自に細かく定義していない

現在の公開daemonはfilesystem root、sandbox、MCP allowlistを明示していますが、bridge側でdomain単位のnetwork allowlistを構築しているわけではありません。

OpenAIがCodex安全運用でnetwork policyを独立した境界として扱い、GitHubもCopilot cloud agentにfirewallを設けていることを考えると、これは追加hardening候補です。

## 3. `workspace-write`は最終承認ではない

agentがworkspaceを書き換えられることと、その変更を採用してよいことは別です。

重要なcode changeでは、

```text
workspace-write
  ↓
git diff
  ↓
commit / branch
  ↓
PR
  ↓
CI
  ↓
human review
```

まで持っていく方が、現在のcoding agentの標準的な安全モデルに近づきます。

## 4. GitHub account自体がcontrol credentialになる

`ControllerLogin`を確認しているため、controller accountの認証状態は非常に重要です。

Issue commentを実行指示として使う以上、GitHub account、GitHub CLI authentication、repository accessが事実上control planeのcredentialになります。

したがって「private repositoryだから安心」という理解では不十分です。

---

# 2026年時点での選び方

最終的には、次の順番で選ぶのが合理的です。

## A. repositoryだけで完結する

**まずGitHub上のcoding agentを使う。**

```text
Issue / prompt
  ↓
cloud agent
  ↓
branch / PR
  ↓
CI + review
```

この用途のために、自宅PCへremote execution pathを追加する必要はありません。

## B. build/testだけlocal resourceが必要

**GitHub Actionsのrunner設計を検討する。**

ただしself-hosted runnerにはGitHub自身が強いsecurity warningを出しているため、repository trust、workflow trust、runner isolationを先に設計します。

## C. local file・device・GUI・既存認証など、localでしかできない

**そのとき初めてlocal bridgeを検討する。**

最低限、

```text
identity allowlist
filesystem allowlist
read-only default
explicit write elevation
tool / MCP allowlist
network boundary
bounded output
machine-verifiable completion
PR / human review for important changes
```

を設計対象にします。

---

# 私たちが作ったのは「AIへの橋」ではなく、小さなcontrol planeだった

最初は、GitHub Issueを使えばChatGPTとlocal Codexをつなげられる、という発想でした。

しかし、2026年のGitHub/Codex ecosystemと比較すると、Issueからagentへ仕事を渡すこと自体はすでに一般化しています。

差が出るのは、その先です。

```text
誰が発行できるか
どこで実行するか
何を触れるか
どのtoolを使えるか
どこへ通信できるか
何を成果物と呼ぶか
誰が最後に承認するか
```

この7つを明示した瞬間、単なるbridgeではなく**control plane**になります。

そして、一般知見として最も重要なのは次の1行です。

> AI coding agentを安全にするのは、賢いpromptではなく、agentの外側に置いた強制可能な境界とreviewableな成果物である。

GitHub Issueはそのcontrol planeの入口として使えます。

しかし、Issueそのものはsandboxでもapprovalでもありません。

repositoryだけで仕事が完結するなら、既存のcloud agent + PR workflowを使う。

local PCへ到達する必要があるときだけbridgeを足し、その分だけ境界も増やす。

これが、自作実装と2026年の公式agent workflowを比較して得た結論です。

---

## 一次情報・実装証拠

### GitHub

- About issues
  https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues
- Planning and tracking work
  https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/planning-and-tracking-work-for-your-team-or-project
- Best practices for Projects
  https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects
- Kick off a task with Copilot agents
  https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/kick-off-a-task
- About third-party coding agents
  https://docs.github.com/en/copilot/concepts/agents/about-third-party-coding-agents
- Review output from Copilot
  https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/review-copilot-output
- About GitHub Copilot code review
  https://docs.github.com/en/copilot/concepts/agents/code-review
- Customize Copilot firewall
  https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-the-firewall
- Secure use reference for GitHub Actions
  https://docs.github.com/en/actions/reference/security/secure-use
- Adding self-hosted runners
  https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners

### OpenAI

- OpenAI Developers — Codex
  https://developers.openai.com/
- Running Codex safely at OpenAI
  https://openai.com/index/running-codex-safely/
- Enterprise admin getting started guide for Codex
  https://help.openai.com/en/articles/11390924

### このbridgeの実装証拠

- Bridge implementation
  https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge
- Bridge daemon
  https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/bridge-daemon.ps1
- E2E verification
  https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/VERIFICATION.md
- Hardened autonomous-run commit
  https://github.com/KAFKA2306/KAFKA2306/commit/864774f15d7fc6522572a8e326dfa78573b0df74
