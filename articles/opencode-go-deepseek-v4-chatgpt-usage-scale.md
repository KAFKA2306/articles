---
title: "ChatGPTを使い倒している私に、月10ドルのOpenCode Goが刺さった理由"
emoji: "♾️"
type: "tech"
topics: ["opencode", "chatgpt", "coding", "mcp", "local"]
published: false
published_at: 2026-08-13 12:09
---

OpenCode Goは最初の月$5、その後$10/月。

DeepSeek V4 Flashは、公式が観測した典型的な利用パターンなら **月158,150 requests相当** とされている。

最初は「安いな」で終わっていた。

でも、自分が最近書いた記事を読み返すと、私にとっての価値は別のところにあった。

**私はすでに、AIにローカルPCでやらせたい仕事を大量に持っていた。**

## ChatGPTはもう「司令塔」になっている

私はChatGPTで、GitHubの複数repoを横断し、Issue、PR、CI、記事、調査、金融、画像、scheduled taskまで扱っている。

別の記事では、123個の個人開発を横断すると、重要なのはコード生成より「次にどの仕事を進めるか」だと書いた。

- [個人開発が123個になって分かった。ChatGPTに任せるべきはコードより「次の1件」だった](https://zenn.dev/kafka2306/articles/chatgpt-multiproject-autonomy)

この役割はChatGPTから動かしたくない。

一方で、ChatGPTやGitHub上のagentだけでは扱いにくい仕事が残る。

## 私が「localでやりたい」と書いていたもの

Codexとのbridgeを作った記事で、私はローカル実行が必要になる例をすでに列挙していた。

- 数百GBのローカルデータ
- GPU環境
- USBでつながった実機
- 社内VPN内のシステム
- 認証済みのデスクトップアプリ
- commit前の作業中workspace

- [GitHub IssueをAIの伝言板にしたら、伝言板に全部やらせてはいけないと分かった](https://zenn.dev/kafka2306/articles/codex-chatgpt-github-issue-bridge)

Unityでも同じだった。

PrefabのAnimator、PhysBone、Contact、Transform階層、Play Modeでの実挙動は、GitHubのコードだけ読んでも確定できない。実際のUnity Editorとprojectを観測する必要がある。

つまり私に足りなかったのは、もう1つの汎用チャットではない。

**自分のPC上で、file、shell、test、local toolを触り続けられる実行側だった。**

## そこでOpenCode Goが刺さる

OpenCodeには、project内でshell commandを実行する`bash`、fileを読む・編集するtoolがあり、local MCP serverも接続できる。

だから私の使い分けはこうなる。

```text
ChatGPT
= control plane
= 調査 / 判断 / repo横断 / 次の仕事を決める

OpenCode Go
= local execution plane
= file / shell / test / local MCP / 作業中workspace
```

これはChatGPTをOpenCodeへ乗り換える話ではない。

**ChatGPTでは届きにくいローカル実行面を、月$10の推論容量で埋める話**である。

## 他サービスと比べても、私には役割が違う

| Service | 月額 | 私にとっての役割 |
|---|---:|---|
| **OpenCode Go** | **$10** | local repo・shell・test・MCPを大量に回すworker |
| **GitHub Copilot Pro** | **$10** | GitHub/IDE中心のcompletionとCopilot workflow |
| **Cursor Pro** | **$20** | EditorとAgentを一体で使う |
| **Claude Pro + Claude Code** | **$20** | Claudeとterminal codingを同じ契約で使う |
| **ChatGPT Plus + Codex** | **$20** | 私の横断的な調査・判断・agent運用の中心 |

OpenCode Goの158,150回はhard quotaではない。DeepSeek V4 Flashの月$60 usageを、公式の典型的なtoken/cache patternからrequest数へ換算した推定値である。

私にとって重要なのは、その数字自体ではなくなった。

**すでに「この仕事はlocalでやりたい」と感じていた領域へ、安価なagent capacityを置ける。**

それなら月$10を払う理由がある。

逆に、実際のrepoやUnity/MCP作業で完了率が低いなら、158,150回使えても意味はない。

私が見るべきKPIはrequest数ではなく、**localで完了できた仕事の数**だ。

## 注意：local実行とlocal推論は別

OpenCode GoはローカルLLMを買うサービスではない。GoのmodelはOpenCode Go provider経由で利用する。

つまりここで言うlocalは、**実行場所とtool accessが自分のPCにある**という意味で、推論まで完全offlineという意味ではない。

外部送信できないデータを扱う場合は、権限・redaction・tool boundaryやlocal modelを別に設計する必要がある。

## 公式情報

- OpenCode Go: https://opencode.ai/docs/go/
- OpenCode Tools: https://opencode.ai/docs/ja/tools/
- OpenCode MCP servers: https://opencode.ai/v2/docs/mcp-servers
- GitHub Copilot plans: https://docs.github.com/en/copilot/concepts/billing/individual-plans
- Cursor pricing: https://cursor.com/pricing
- Claude Pro: https://support.claude.com/en/articles/8325606-what-is-the-pro-plan
- Codex usage: https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan/

料金・model・利用上限は変更される。契約時には現行の公式情報を再確認する。