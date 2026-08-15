<!-- pipeline_meta: {"idea_source":"public-github-engineering","idea_only":true,"raw_private_content_persisted":false,"topic":{"title":"AIエージェント連携の本質はキューではない――GitHub Actions、Tailscale、MCP Tunnelと比較して分かった境界設計","audience":"ChatGPT、Codex、GitHub、ローカル実行環境を組み合わせて自動化したいエンジニア","central_question":"AIエージェント同士・クラウドとローカルを安全につなぐとき、GitHub Issue、Actions、Tailscale、MCP Tunnel、message queueをどう使い分けるべきか","surprising_finding":"GitHub Issue bridgeは一般解ではなく、人間可読な低頻度control planeとしては有効だが、到達性はTailscaleやSecure MCP Tunnel、GitHub-native実行はActions、厳密な配送は専用queueに任せる方が責務分離として自然だった","initial_hypothesis":"private GitHub IssueをqueueにすればChatGPTとlocal Codexの連携問題をまとめて解ける","hypothesis_update":"問題はqueueではなくcontrol plane・network plane・execution plane・permission boundary・completion evidenceの分離であり、用途ごとに既存の公式機構を組み合わせるべき","stakes":"ローカルagentの自律性を上げながら、credential、private infrastructure、任意ディレクトリ実行、誤った再実行を不用意に公開しない","story_type":"architecture-reassessment","public_evidence":["https://developers.openai.com/api/docs/guides/secure-mcp-tunnels","https://developers.openai.com/codex/github-action","https://developers.openai.com/codex/non-interactive-mode","https://developers.openai.com/codex/sandboxing","https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt","https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows","https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks","https://tailscale.com/docs/integrations/github/github-action","https://tailscale.com/docs/features/tailscale-serve","https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html","https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge"]}} -->

# AIエージェント連携の本質はキューではない――GitHub Actions、Tailscale、MCP Tunnelと比較して分かった境界設計

ローカルの Codex CLI に調査や修正を任せ、その最終出力を ChatGPT に貼り直す。

この往復を消すため、私は **private GitHub Issue を ChatGPT と local Codex の受け渡し場所にする bridge** を作りました。

最初はこれを「AI間のmessage queue」と考えていました。

しかし2026年の公式機構と横に並べてみると、この理解は狭すぎました。

GitHub Actions は外部イベントからworkflowを起動できる。TailscaleはGitHub-hosted runnerをprivate networkへ一時参加させられる。OpenAIには、private MCP serverをpublic internetへ出さずChatGPTやCodexから呼ぶための Secure MCP Tunnel がある。そして本物のmessage queueには、visibility timeout、acknowledgement、retry、dead-letter queueのような配送セマンティクスがある。

ここまで並べると、GitHub Issue は「queueの簡易版」ではありません。

**人間にも読める、低頻度のcontrol planeとして使うなら強い。だが、network、execution、deliveryまでIssueに背負わせると設計が崩れる。**

この記事では、自作bridgeを成功談として紹介するのではなく、一般的な選択肢と比較しながら「どこに何の責務を置くべきか」を考えます。

公開実装:
https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge

> **公開昇格条件**
> この原稿は記事候補です。最新公開bundleを実機で再installし、installer末尾の `BRIDGE_OK` と worker payload の `exit_code: 0` を確認するまで、`articles/` へは昇格しません。

## まず分けるべきは「5つのplane」だった

AI agent連携を一枚の矢印で描くと、異なる問題が同じ箱に見えます。

```text
ChatGPT → GitHub → local PC → Codex → GitHub → ChatGPT
```

実際には、少なくとも次の5つを分けた方が整理できます。

| plane | 問い | 代表的な仕組み |
|---|---|---|
| Control | 誰が、何を、いつ実行してよいか | Issue、PR、approval、workflow input |
| Network | private resourceへどう到達するか | Tailscale、Secure MCP Tunnel、VPN |
| Execution | agentをどこで動かすか | Codex CLI、GitHub Actions、self-hosted runner |
| Delivery | taskの重複、再試行、ackをどう扱うか | SQS、Pub/Sub、専用queue |
| Evidence | 何をもって成功とするか | exit code、HEAD SHA、patch、artifact、test result |

私の最初の設計は、GitHub Issueにこの5つのうち3つほどをまとめて背負わせようとしていました。

比較して分かったのは、**良いagent architectureは「全部を一つのtransportで解く」より、planeごとにauthorityを分ける**ということです。

## 結論を先に：2026年なら用途ごとに選ぶ

| 欲しいもの | 第一候補 | 理由 |
|---|---|---|
| GitHub上のイベントから再現可能なCodex処理 | GitHub Actions + `openai/codex-action` | repo-native、権限をjob単位で分離できる |
| GitHub-hosted runnerからprivate PC/APIへ到達 | Tailscale GitHub Action | ephemeral nodeでtailnetへ参加できる |
| ChatGPT/Codexからprivate MCP serverを直接呼ぶ | OpenAI Secure MCP Tunnel | public inboundを開けずoutbound-onlyで接続できる |
| 人間がブラウザで読める低頻度の非同期handoff | private GitHub Issue bridge | task/resultを同じ場所で観測しやすい |
| 高頻度・複数consumer・厳密なretry/ack | SQS / Pub/Sub等 | queue専用の配送セマンティクスがある |

重要なのは「どれが最強か」ではありません。

**何を解きたいのかを、transport名より先に決めること**です。

## 1. GitHub-nativeな自動化なら、まずActionsを疑う

GitHub Actionsには `workflow_dispatch` と `repository_dispatch` があります。

`workflow_dispatch` はUI、CLI、APIからmanual workflowを起動でき、`repository_dispatch` はGitHub外で起きたイベントからworkflowを起動するための公式機構です。

公式:
https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows

さらにOpenAIは `openai/codex-action@v1` を公式に提供しており、PR review、release preparation、migrationなどのrepeatable taskをGitHub Actions内でCodexに実行させる用途を説明しています。

公式:
https://developers.openai.com/codex/github-action

OpenAIのnon-interactive mode文書でも、GitHub ActionsではCLIを自前installして認証するよりCodex GitHub Actionを使うよう案内されています。

公式:
https://developers.openai.com/codex/non-interactive-mode

つまり、処理対象がGitHub repositoryのcheckoutだけで完結するなら、

```text
Issueをpoll
  → local daemon
  → Codex
```

よりも、

```text
GitHub event / dispatch
  → GitHub Actions
  → Codex GitHub Action
  → artifact / PR / comment
```

の方が一般的です。

workflow run、job、artifact、権限、再実行というGitHub側の既存control planeをそのまま使えるからです。

### ではlocal daemonは不要か

そうではありません。

**処理したいstateが「GitHub上のcheckout」ではなく、「自分のPCにしかない環境・デバイス・巨大データ・認証済みアプリ・作業中workspace」なら、executionをlocalに残す理由があります。**

ここで次の論点がnetworkです。

## 2. Tailscaleは「queue」ではなく「private reachability」を解く

Tailscaleを比較対象に入れると、Issue bridgeの役割が明確になります。

Tailscale Serveはtailnet内の他deviceからlocal serviceへ到達させる機構です。公開internetから到達させるFunnelとは役割が分かれています。

公式:
https://tailscale.com/docs/features/tailscale-serve
https://tailscale.com/docs/features/tailscale-funnel

さらにTailscaleはGitHub Actions向け公式Actionを提供しています。GitHub-hosted runnerをtailnetにephemeral nodeとして参加させ、private deviceやinternal APIへアクセスできます。

公式:
https://tailscale.com/docs/integrations/github/github-action

同文書では、workload identity federationを推奨し、GitHubのOIDC tokenから一時的なnodeを作り、workflow終了後にそのnodeを削除する構成を説明しています。

これはかなり強い選択肢です。

```text
GitHub event
  ↓
GitHub-hosted Actions runner
  ↓  Tailscale ephemeral node
private workstation / API / DB
```

この場合、private infrastructureをpublic internetへ出す必要がありません。

ただしTailscaleは、taskのack、retry、idempotency、human approvalを提供するmessage queueではありません。

**Tailscaleが解くのは「届くか」であり、「何を実行してよいか」「一度だけ処理したか」は別問題です。**

したがって、TailscaleとGitHub Issueは競合というより、異なるplaneを担当します。

## 3. さらに強い比較対象がOpenAI Secure MCP Tunnelだった

今回もっとも大きな再評価点です。

OpenAIは Secure MCP Tunnel を提供しており、private network、on-premises、developer machine上のMCP serverをpublic internetへ公開せず、ChatGPT、Codex、Responses APIなど対応OpenAI製品から呼び出せると説明しています。

公式:
https://developers.openai.com/api/docs/guides/secure-mcp-tunnels

仕組みはoutbound-onlyです。

private側で `tunnel-client` を動かし、OpenAI-hosted endpointへHTTPS接続します。clientがqueued MCP workをlong-pollし、private MCP serverへJSON-RPCをforwardし、responseを同じtunnel経由で返します。

これは、私がGitHub Issueで作った構造とかなり似ています。

```text
Issue bridge
local daemon --poll--> GitHub --task/result--> ChatGPT

Secure MCP Tunnel
local tunnel-client --long-poll--> OpenAI --MCP request/response--> ChatGPT/Codex
```

違いは、後者が **OpenAI製品からprivate toolを呼ぶための公式RPC path** であることです。

したがって、目的が

> ChatGPTからlocal toolを直接呼びたい

であり、そのlocal capabilityをMCP serverとして表現できるなら、2026年時点ではまずSecure MCP Tunnelを検討すべきです。

Issue bridgeが勝つのは、MCP RPCそのものよりも、**人間がGitHub上でtaskとresultを読めること、Issue/PRという既存の意思決定履歴に寄せたいこと、非同期の作業依頼として扱いたいこと**を重視する場合です。

## 4. 「Issueをqueueにする」は、専用queueと何が違うのか

ここは名前を正確にした方がよいです。

Amazon SQSのような専用queueには、messageをconsumerが処理中に他consumerから一時的に見えなくするvisibility timeoutがあります。処理失敗時には再び可視化でき、繰り返し失敗するmessageをdead-letter queueへ送る設計もあります。standard queueはat-least-once deliveryです。

公式:
https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html

GitHub Issue commentには、これらがqueue primitiveとして備わっているわけではありません。

私のbridgeではtask IDを付け、daemon側で処理済みIDを避けています。しかしこれは自前protocolです。

したがって、GitHub Issueを説明するときは、

**「message queue」より「durable, human-readable control mailbox」**

くらいに位置づける方が正確です。

低頻度なら、この弱さは逆に利点になります。

- browserだけでtask/resultを確認できる
- repositoryと同じidentity/permission体系を使える
- controller messageとworker resultを同じthreadに置ける
- 専用brokerを追加しなくてよい

一方、workerが増える、taskが大量になる、orderingやretryが重要になるなら、専用queueへ移るべきです。

## 5. Webhookならpollingを消せる。しかしprivate endpoint問題が戻る

GitHub webhookを使えば、Issueを30秒ごとにpollする必要はありません。

GitHubの公式best practiceは、webhook secretによるsignature verification、HTTPS、必要最小限のevent subscription、`X-GitHub-Delivery`によるdelivery識別などを推奨しています。またreceiverは10秒以内に2XXを返し、重い処理は非同期queueへ渡す構成を勧めています。

公式:
https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks
https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries

しかしlocal PCでwebhookを受けるには、外部から到達可能なendpointが必要になります。

そこで再び、

- public HTTPS endpointを持つ
- reverse tunnelを使う
- Tailscale等のprivate networkと別のtrusted runnerを組み合わせる
- OpenAI用途ならSecure MCP Tunnelへ寄せる

というnetwork designが必要です。

**pollingは遅いが、inbound portを開けなくてよい。**

このtrade-offを隠さない方が、記事としては価値があります。

## 6. それでもprivate GitHub Issue bridgeを残す理由

ここまで比較すると、自作bridgeを捨てるべきようにも見えます。

しかし、今回の制約ではまだ合理性があります。

### 理由1：ChatGPTの標準GitHub appはread-only

OpenAIのHelp Centerは、ChatGPTの標準GitHub appはrepositoryを分析・検索するためのread-only接続であり、code/update/PRをpushする用途はCodex側で提供すると説明しています。

公式:
https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt

したがって「GitHubがChatGPTから見える」だけでは、双方向controllerになれるとは限りません。

一方、write-capableなGitHub App、plugin、Codex、Enterprise向け構成などを使える環境では事情が変わります。ここを固定仕様として扱わないことが重要です。

### 理由2：local stateをそのまま使いたい

GitHub Actionsのcheckoutではなく、local PCのworkspaceやlocal-only dependencyを使いたい場合があります。

その場合、executionをlocalに残し、GitHubをcontrol mailboxとして使うのは単純です。

### 理由3：人間のレビュー地点を残したい

完全なRPCより、

```text
read-only調査
  ↓
result + evidence
  ↓
human / ChatGPT review
  ↓
workspace-write
```

の方が適する作業があります。

Issue threadはこの「一度止まって読む」境界を自然に作れます。

## 7. 自作bridgeも、一般的ベストプラクティス側へ寄せる

比較して終わりではなく、自作側も改善できます。

### 原則1：Issueをqueueではなくcontrol planeとして扱う

Issueに置くのは、prompt本文だけではなく、少なくとも次です。

```json
{
  "task_id": "...",
  "cwd": "...",
  "sandbox": "read-only",
  "requested_action": "review",
  "expected_evidence": ["exit_code", "git_head", "git_status"]
}
```

worker resultも自然言語だけにしません。

```json
{
  "task_id": "...",
  "exit_code": 0,
  "sandbox": "read-only",
  "cwd": "...",
  "git": {
    "head": "...",
    "status": []
  }
}
```

OpenAIの`codex exec`はJSONL出力に加え、JSON Schemaでfinal outputを拘束する `--output-schema` も公式にサポートしています。

公式:
https://developers.openai.com/codex/non-interactive-mode

今後は自前のMarkdown parsingを増やすより、machine-readable outputをCodex側でも強制する方が堅牢です。

### 原則2：readとwriteを別jobにする

OpenAIのnon-interactive modeは、`codex exec`の既定sandboxをread-onlyとし、automationでは必要最小限のpermissionを使うよう明記しています。編集時は `--sandbox workspace-write` を明示し、`danger-full-access` はcontrolled environmentに限定するよう案内しています。

公式:
https://developers.openai.com/codex/non-interactive-mode
https://developers.openai.com/codex/sandboxing

自作bridgeもこの思想に合わせ、

```text
observe / diagnose
  = read-only

modify
  = workspace-write
```

を別taskにしています。

### 原則3：network accessとfilesystem accessを別authorityにする

`workspace-write`だからnetworkも許す、とは限りません。

filesystem boundary、network boundary、GitHub write permissionは別々に制御するべきです。

Tailscaleのtag、GitHub Actionsの`permissions:`、Codex sandbox、AllowedRootは、それぞれ異なるauthorityです。

一つの「agentに任せる」フラグへ潰さない方が安全です。

### 原則4：completionは「返事が来た」ではなくevidenceで定義する

今回のinstallerは、daemonが起動しただけでは成功にしません。

一時Git repositoryからIssue経由でCodexを実行し、

```text
final message contains BRIDGE_OK
exit_code == 0
```

まで確認します。

これは比較後も残す価値があります。

transport、execution、return pathをE2Eで通すsmoke testだからです。

## 8. 実装例：現在のbridge

公開版は次の構成です。

```text
local send-task.ps1
  ↓
private GitHub Issue
  ↓ polling
Windows daemon
  ↓
codex exec
  ↓
private GitHub Issue
  ↓
ChatGPT / human reads result
```

公開sender:
https://github.com/KAFKA2306/KAFKA2306/blob/23640ccec32355cad91bb7cfeed34845db54824c/scripts/codex-chatgpt-bridge/send-task.ps1

公開daemon:
https://github.com/KAFKA2306/KAFKA2306/blob/23640ccec32355cad91bb7cfeed34845db54824c/scripts/codex-chatgpt-bridge/bridge-daemon.ps1

公開installer:
https://github.com/KAFKA2306/KAFKA2306/blob/23640ccec32355cad91bb7cfeed34845db54824c/scripts/codex-chatgpt-bridge/install.ps1

現在の主な境界は次です。

```text
queue repository must be PRIVATE
controller author == configured GitHub login
cwd ∈ AllowedRoot
sandbox ∈ {read-only, workspace-write}
default sandbox = read-only
danger-full-access = rejected
```

daemonはcontroller marker、author、task ID、AllowedRoot、sandboxを確認してから`codex exec`を実行します。

またautonomous runはuser config / app / plugin discoveryから分離し、普段のinteractive環境に依存しすぎないようにしています。

この設計の価値は「GitHub Issueでagentを動かせること」そのものではありません。

**identity、filesystem、execution、completionの境界を明示し、それを人間が読めるcontrol planeに残したこと**です。

## 9. 私なら今、こう選ぶ

### ケースA：repositoryだけ触ればよい

```text
GitHub event
  → GitHub Actions
  → openai/codex-action
  → artifact / PR / comment
```

これを第一候補にします。

### ケースB：GitHub Actionsからprivate PC/APIへ届きたい

```text
GitHub Actions
  → Tailscale GitHub Action
  → private service
```

Tailscaleをnetwork planeに使います。

### ケースC：ChatGPT/Codexからprivate local toolを直接呼びたい

```text
ChatGPT / Codex
  → Secure MCP Tunnel
  → private MCP server
```

MCPとして表現できるなら、公式pathを優先します。

### ケースD：人間が途中で読み、低頻度のtask/resultを残したい

```text
GitHub Issue
  → local worker
  → evidence
  → human / agent review
```

ここで初めてIssue bridgeが第一候補になります。

### ケースE：大量task、複数worker、厳密なretryが必要

GitHub Issueから離れ、専用message queueを使います。

## まとめ：「何でつなぐか」より「何を分離するか」

最初に作ろうとしたのは、private GitHub Issueを30秒ごとにpollしてCodexを呼ぶ小さなdaemonでした。

比較後の結論は、もっと一般的です。

```text
Control plane
  誰が何を実行してよいか

Network plane
  private resourceへどう到達するか

Execution plane
  どこでagentを動かすか

Delivery plane
  retry / duplicate / ackをどう扱うか

Evidence plane
  何をもって成功とするか
```

Tailscaleはnetworkを強くする。
GitHub Actionsはexecutionとworkflow controlを強くする。
Secure MCP TunnelはOpenAI製品からprivate MCPへの公式到達経路を作る。
SQSやPub/Subはdelivery semanticsを提供する。
GitHub Issueは、人間可読なcontrol mailboxとして使える。

この役割を混ぜない方がよい。

私のbridgeも、「Issueが最良のqueueだった」という話ではありません。

**小さな自律化を作るとき、transportを発明する前にauthorityとfailure semanticsを分解した方が、後から別の技術へ置き換えやすい。**

それが、GitHub Issue、Actions、Tailscale、MCP Tunnelを横に並べて初めて見えた結論です。

## 一次情報・実装証拠

- OpenAI Secure MCP Tunnel: https://developers.openai.com/api/docs/guides/secure-mcp-tunnels
- OpenAI Codex GitHub Action: https://developers.openai.com/codex/github-action
- OpenAI Codex non-interactive mode: https://developers.openai.com/codex/non-interactive-mode
- OpenAI Codex sandboxing: https://developers.openai.com/codex/sandboxing
- OpenAI Help — Connecting GitHub to ChatGPT: https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt
- GitHub Actions events (`workflow_dispatch`, `repository_dispatch`): https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- GitHub webhook best practices: https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks
- GitHub webhook signature validation: https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries
- Tailscale GitHub Action: https://tailscale.com/docs/integrations/github/github-action
- Tailscale Serve: https://tailscale.com/docs/features/tailscale-serve
- Tailscale Funnel: https://tailscale.com/docs/features/tailscale-funnel
- Amazon SQS visibility timeout / retry / DLQ: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html
- 公開bridge: https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge
