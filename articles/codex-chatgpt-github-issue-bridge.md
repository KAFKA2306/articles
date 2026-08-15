---
title: "GitHub IssueをAIの伝言板にしたら、伝言板に全部やらせてはいけないと分かった"
emoji: "📬"
type: "tech"
topics: ["codex", "github", "tailscale", "mcp", "automation"]
published: true
published_at: 2026-08-15 12:53
---

ChatGPTに相談する。

「このリポジトリ、どこがおかしい？」

次にローカルのCodex CLIへ移動して、同じ説明をする。

Codexが調べ終わったら、結果をコピーしてChatGPTへ戻す。

修正方針が決まったら、またCodexへ貼る。

数回なら平気です。でも、調査 → 判断 → 修正 → テストを繰り返すと、**自分がAI同士の伝書鳩になっている**ことに気づきます。

そこで私は、private GitHub Issueを2つのAIの間に置きました。

```text
ChatGPT / 人間
  ↓ 依頼を書く
private GitHub Issue
  ↓
local daemon
  ↓
Codex CLI
  ↓ 結果を書く
private GitHub Issue
  ↓
ChatGPT / 人間
```

感覚としては、会社の受付に置く伝言ノートです。

「この資料を確認してください」と書いておけば、担当者が見つけて仕事をする。終わったら同じノートに「確認しました」と残す。

最初は、これで十分だと思いました。

**GitHub IssueをAI同士のmessage queueにすればいい。**

ところがGitHub Actions、Tailscale、OpenAI Secure MCP Tunnel、本物のmessage queueと比べてみると、少し変なことをしていると分かりました。

会社で言えば、受付の伝言ノートに、

- 誰を社内に入れてよいか
- どの部屋まで行ってよいか
- 誰が実作業するか
- 荷物を何百件どう配送するか
- 本当に仕事が終わったか

まで全部任せようとしていたのです。

伝言ノートが悪いのではありません。

**伝言ノートは、伝言ノートとして使えばかなり便利です。**

この記事では、自作bridgeを「これが正解です」と紹介するのではなく、身近な仕事の流れに置き換えながら、GitHub Issue、Actions、Tailscale、MCP Tunnel、専用queueをどう使い分ければよいかを整理します。

公開実装: [KAFKA2306/KAFKA2306 — codex-chatgpt-bridge](https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge)

> この記事の実装説明は公開コードの仕様を確認して書いています。この記事の公開時点で、最新bundleをWindows実機へ再installしてE2E smoke testを再実行した、という主張はしていません。

## まず「小さな会社」だと思うと分かりやすい

AI agentの構成図を見ると、急に難しくなります。

`control plane`、`network plane`、`execution plane`。

言葉は正しいのですが、最初からこれを読むと「結局どれが何をしているの？」となりがちです。

なので、いったん5人くらいの小さな会社を想像します。

朝、あなたが会社に着いて、こんな仕事を頼みたいとします。

> 昨日から落ちているテストの原因を調べて。勝手に修正はしないで。

この一言だけでも、実際には5つの仕事があります。

| 日常の仕事 | 技術的な役割 | 代表例 |
|---|---|---|
| 受付に依頼を置く | Control | GitHub Issue、PR、workflow input |
| 担当者が作業場所まで行く | Network | Tailscale、Secure MCP Tunnel |
| 実際にPCを触って調べる | Execution | Codex CLI、GitHub Actions |
| 大量の依頼を順番に配る | Delivery | SQS、Pub/Subなど |
| 「終わった」を確認する | Evidence | test、exit code、HEAD SHA、artifact |

私が最初に作ったbridgeは、このうち何個かをGitHub Issueへ詰め込もうとしていました。

ここを分けるだけで、かなり見通しがよくなりました。

**受付、通路、作業場、配送センター、検収。全部を同じ仕組みにする必要はありません。**

## 先に結論：身近な例ならこう選ぶ

### READMEの誤字を直したい

GitHub上のファイルだけ見れば終わる仕事です。

```text
GitHub
  ↓
GitHub Actions
  ↓
Codex
  ↓
PR / artifact / comment
```

この場合、わざわざ自宅PCへ仕事を運ぶ理由は薄いです。

### GitHub Actionsから社内DBを使ってテストしたい

GitHubのrunnerから、インターネットには公開していないDBへ行く「道」が必要です。

```text
GitHub Actions
  ↓
Tailscale
  ↓
private DB
```

Tailscaleはこの「道」を担当します。

### ChatGPTから自分のPC上のツールを直接使いたい

その機能をMCP serverとして出せるなら、OpenAIのSecure MCP Tunnelが候補です。

```text
ChatGPT / Codex
  ↓
Secure MCP Tunnel
  ↓
private MCP server
```

### AIに調べてもらったあと、一度自分で読んでから修正させたい

ここではGitHub Issueが使いやすいです。

```text
調査依頼
  ↓
Issue
  ↓
Codexがread-onlyで調査
  ↓
Issueに結果
  ↓
人間が読む
  ↓
修正を許可
```

### 毎晩1万件の仕事を複数workerへ配りたい

これはもう「伝言板」の仕事ではありません。

配送センターが必要です。

SQSやPub/Subのような専用message queueを検討する領域です。

## 1. GitHub Actionsは「会社の作業場」

たとえば、PRが作られたら毎回Codexにレビューしてもらいたいとします。

人間の会社なら、受付に毎回メモを置くより、

> 新しい申請書が来たら、この手順で自動的に検査する

という作業手順を決めた方が自然です。

GitHub Actionsはまさにこの役割です。

GitHubには`workflow_dispatch`があり、UI、CLI、APIからworkflowを手動実行できます。また`repository_dispatch`は、GitHub外の出来事をきっかけにworkflowを起動するために使えます。

- [GitHub Docs — Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- [OpenAI — Codex GitHub Action](https://developers.openai.com/codex/github-action)

だから、

> GitHubに置いてあるコードを取ってきて、調べて、テストして、結果をPRへ返す

だけなら、まずActions側で完結できないか考える方が素直です。

自宅PCで30秒ごとにIssueを見張る必要はありません。

### ではlocal Codexは要らない？

ここで話が変わるのが、**そのPCにしかないものを使いたいとき**です。

例えば、

- 数百GBのローカルデータ
- GPU環境
- USBでつながった実機
- 社内VPN内のシステム
- 認証済みのデスクトップアプリ
- commit前の作業中workspace

です。

GitHubのcheckoutを取ってくるだけでは、その状態は再現できません。

このとき初めて「仕事をローカルへ届ける方法」が重要になります。

## 2. Tailscaleは「社員証が必要な専用通路」

Tailscaleを初めて比較したとき、Issue bridgeの代わりになるのではと思いました。

でも役割が違いました。

Tailscaleは「仕事を何件処理したか」を管理するものではなく、**そもそもその場所へ安全に行けるようにするもの**です。

たとえば会社の奥に、一般のお客さんは入れない検査室があるとします。

GitHub Actionsのrunnerは会社の外にいます。

Tailscaleを使うと、そのrunnerに一時的な社員証を渡して、許可された検査室まで通れるようにするイメージです。

Tailscaleの公式GitHub Actionは、GitHub Actionsのrunnerをtailnetへ参加させ、private deviceや内部サービスへ到達できるようにします。公式文書ではworkload identity federationを推奨しており、GitHubのOIDC tokenを使ってephemeral nodeを作る構成も説明されています。

- [Tailscale Docs — GitHub Action](https://tailscale.com/docs/integrations/github/github-action)

```text
GitHub Actions runner
  ↓ 一時的にtailnetへ参加
Tailscale
  ↓
社内API / DB / workstation
```

仕事が終われば、その一時的なnodeは片付けられます。

ここで大事なのは、Tailscaleが教えてくれるのは主に、

> このrunnerは、あのprivate serverまで行ける

ということです。

> この依頼はまだ未処理か

> 3回失敗したら隔離するか

> 人間の承認待ちか

まではTailscaleの仕事ではありません。

**Tailscaleは道路。Issueは伝言板。競合というより別の仕事です。**

Tailscale Serveも、tailnet内の他deviceからlocal serviceへ到達させる機能です。

- [Tailscale Docs — Serve](https://tailscale.com/docs/features/tailscale-serve)

## 3. Secure MCP Tunnelは「AI専用の通用口」

もっと直接的な選択肢もありました。

OpenAIはSecure MCP Tunnelを提供しています。

これは、private network、on-premises環境、developer machineなどにあるMCP serverをpublic internetへ公開せず、対応するOpenAI製品から利用するための仕組みです。

- [OpenAI — Secure MCP Tunnels](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)

会社の比喩でいえば、受付に伝言を置くのではなく、**AI専用の通用口を作る**感じです。

private側で`tunnel-client`を動かします。外から会社のドアを開けるのではなく、中からOpenAI側へoutbound HTTPS接続を張ります。

公式文書では、`tunnel-client`がqueued MCP workをlong-pollし、local MCP serverへJSON-RPC requestを転送し、responseを同じtunnelで返す構造が説明されています。

```text
ChatGPT
  ↓
OpenAI-hosted tunnel endpoint
  ↑ outbound HTTPS
local tunnel-client
  ↓
private MCP server
```

目的が、

> ChatGPTから自宅PCの検索ツールを呼びたい

> Codexから社内の検査APIを使いたい

のような「tool call」なら、この経路はかなり自然です。

ではIssue bridgeは不要でしょうか。

そうとも限りません。

MCPのrequest/responseより、

> まず調査して

> 結果を人間が読む

> よければ次の修正を許可する

という**仕事の受け渡しそのものを履歴として残したい**場合があります。

その場合、Issueという「目で読める伝言板」には別の価値があります。

## 4. GitHub Issueは「受付の伝言板」

ここで最初のbridgeへ戻ります。

GitHub Issueの良いところは、エンジニアなら追加の管理画面を覚えなくても読めることです。

朝PCを開いて、Issueを見る。

```text
依頼
「このテストが落ちる理由だけ調べて。修正はしないで」

結果
「原因はAです。exit_codeは0、HEADはabc123、変更ファイルはありません」
```

これなら人間も読めます。

次のAIも読めます。

何日か後に「なぜこの修正をしたんだっけ」と振り返ることもできます。

私のbridgeでは、controller commentとworker resultを同じprivate Issueへ残します。

さらに結果は「直しました」だけにしません。

```json
{
  "task_id": "task-...",
  "exit_code": 0,
  "sandbox": "read-only",
  "cwd": "D:\\dev\\example",
  "git": {
    "head": "<実行時のHEAD>",
    "status": []
  }
}
```

これは宅配で言えば、

> 届けました

だけではなく、

> どの荷物を、どこへ、いつ届け、受領状態はどうだったか

まで納品書に残す感覚です。

## 5. SQSは「伝言板」ではなく「配送センター」

ここは名前を混ぜると危険です。

私のbridgeは当初、GitHub Issueをmessage queueと呼んでいました。

でも本物のqueueと比べると、かなり違います。

Amazon SQSにはvisibility timeoutがあります。あるconsumerがmessageを処理している間、そのmessageを一時的に他consumerから見えなくできます。処理されず削除されなければ再び可視になります。standard queueはat-least-once deliveryなので、重複処理を考える必要もあります。

- [AWS Docs — Amazon SQS visibility timeout](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html)

身近に言えば、巨大な宅配センターです。

荷物が1000個来ても、

- 誰が今持っているか
- 配達に失敗したらどうするか
- 同じ荷物が来ても壊れないか
- 何度も失敗する荷物をどう隔離するか

を考える世界です。

一方GitHub Issueは、オフィスのホワイトボードに近い。

10件の仕事を人間とAIで相談しながら進めるなら、ホワイトボードの方が見やすいことがあります。

1万件の仕事を20 workerへ配るなら、ホワイトボードに付箋を1万枚貼るのはやめた方がいい。

この違いです。

なので今は、GitHub Issue bridgeを**human-readable control mailbox**と捉えています。

## 6. Webhookは「受付ベル」。でもベルを置く場所が要る

現在のbridgeはIssueを一定間隔で見に行きます。

```text
30秒ごとに受付を見る
「新しい依頼ある？」
```

少し間抜けに見えます。

Webhookなら、依頼が来た瞬間にベルを鳴らせます。

```text
Issueに新しい依頼
  ↓
Webhook
  ↓
worker起動
```

GitHubはWebhookについて、secretによる検証、HTTPS、必要なeventだけの購読、`X-GitHub-Delivery`による識別などを推奨しています。またreceiverは配信から10秒以内に2XXを返す必要があります。

- [GitHub Docs — Best practices for using webhooks](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks)

ただし、自宅PCにベルを鳴らすには、GitHubからそのPCへ届く経路が必要です。

つまり、

> pollingをなくしたら、今度はprivate PCへどう到達するか

という問題が戻ってきます。

ここでも、受付と道路は別問題です。

pollingは遅い。

でも、外から自宅PCへ入る入口を用意しなくても成立します。

小さな個人用途では、この単純さが価値になることがあります。

## 7. 安全性も「家の鍵」に置き換えると分かりやすい

private Issueだから安全、とは言えません。

もしIssueへ書ける人が、

> `C:\Windows`を消して

と書いたら、そのままlocal agentが実行する設計では困ります。

これは「家族だけが使う伝言板だから、書いてあることは何でも実行する」と言っているのと同じです。

そこでbridgeでは、仕事を受け取る前にいくつかの鍵を確認します。

```text
queue repository must be PRIVATE
controller author == configured GitHub login
cwd ∈ AllowedRoot
sandbox ∈ {read-only, workspace-write}
default sandbox = read-only
danger-full-access = rejected
```

公開daemon: [bridge-daemon.ps1](https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/bridge-daemon.ps1)

例えば`AllowedRoot = D:\dev`なら、`C:\Windows`や別の場所へ勝手に移動するtaskは拒否します。

そして、最初の調査はread-onlyです。

これは同僚に、

> まず棚を見て原因だけ教えて。物の場所は変えないで。

と頼むのに近いです。

調査結果を見てから、必要なときだけ、

> では、この棚だけ直していいよ。

とworkspace-writeへ上げます。

OpenAIのCodex文書でも、non-interactive executionとsandbox permissionを明示的に扱う仕組みが説明されています。

- [OpenAI — Codex non-interactive mode](https://developers.openai.com/codex/non-interactive-mode)
- [OpenAI — Codex sandboxing](https://developers.openai.com/codex/sandboxing)

## 8. 「終わりました」を信用しない。レシートを見る

AIに仕事を頼むと、最後にこう返ってくることがあります。

> 修正しました。テストも通っています。

人間同士でも、この一言だけでは少し不安です。

宅配なら受領印を見る。

会計ならレシートを見る。

ソフトウェアなら、機械的な証拠を見る方がよい。

私のbridgeでは、worker resultに少なくとも次を残します。

- exit code
- sandbox
- absolute cwd
- Git repository root
- HEAD SHA
- bounded `git status --porcelain=v1`

さらにinstallerは、daemonを起動できただけでは成功にしていません。

temporary Git repositoryを作り、Issue経由で実際にCodexへ仕事を送り、

```text
BRIDGE_OK
exit_code == 0
```

まで戻ってきた場合だけ成功扱いにする実装です。

公開installer: [install.ps1](https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/install.ps1)

「店員を雇えた」ではなく、**実際に注文して、商品が届き、レシートまで返ってきた**ところまで確認するsmoke testです。

## 9. 私なら今、こう使い分ける

### GitHubにあるコードだけを触る

**GitHub Actions + Codex**を先に検討します。

### GitHub Actionsから社内・自宅のprivate serviceへ行く

**Tailscale**を「道路」として使います。

### ChatGPT/Codexからprivate MCP toolを直接呼ぶ

**Secure MCP Tunnel**を先に検討します。

### 人間が途中で読んで、次へ進むか決めたい

**GitHub Issue**を「伝言板」として使います。

### 大量のtaskを複数workerへ確実に配りたい

**専用message queue**へ移ります。

こうすると、「TailscaleとGitHub Issueのどっちが強い？」という比較自体が少し変だと分かります。

**道路と受付を比べても仕方がありません。**

## まとめ：AIが増えても、仕事の基本は意外と普通だった

AI agentという言葉を使うと、急に未来のシステムを設計している気分になります。

でも、実際に困ったことを並べると、昔からある仕事の流れとかなり似ています。

```text
受付
  誰が何を頼んだか

通路
  その人はどこまで入ってよいか

作業場
  誰が実際に手を動かすか

配送
  大量の仕事をどう配るか

検収
  本当に終わったと何で確認するか
```

GitHub Issueは受付として便利でした。

Tailscaleは通路を作る。

GitHub ActionsやCodexは作業する。

Secure MCP Tunnelはprivate toolへのAI専用通路を作る。

SQSのようなqueueは大量配送を扱う。

test、exit code、HEAD SHAは検収に使える。

最初の私は、GitHub Issueという一枚の伝言板に、これらを全部やらせようとしていました。

比較して得た一番大きな学びは、特定の新しいツールではありません。

**AIに仕事を任せるときも、「誰が頼む」「どこまで入れる」「誰が作業する」「どう届ける」「何をもって完了とする」を分ければよい。**

そう考えると、agent architectureは少し身近になります。

そしてGitHub Issue bridgeも、万能なAI基盤ではなく、

> 人間とAIが同じ伝言板を見ながら、小さな仕事を安全に受け渡す

ための道具として、ちょうどよい位置に落ち着きました。

## 一次情報・実装証拠

- [OpenAI Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)
- [OpenAI Codex GitHub Action](https://developers.openai.com/codex/github-action)
- [OpenAI Codex non-interactive mode](https://developers.openai.com/codex/non-interactive-mode)
- [OpenAI Codex sandboxing](https://developers.openai.com/codex/sandboxing)
- [OpenAI Help — Connecting GitHub to ChatGPT](https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt)
- [GitHub Actions events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- [GitHub webhook best practices](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks)
- [Tailscale GitHub Action](https://tailscale.com/docs/integrations/github/github-action)
- [Tailscale Serve](https://tailscale.com/docs/features/tailscale-serve)
- [Amazon SQS visibility timeout](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html)
- [公開bridge](https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge)
