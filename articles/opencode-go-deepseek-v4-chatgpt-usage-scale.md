---
title: "OpenCode Goを見て、月10ドルなら試したいと思った理由"
emoji: "♾️"
type: "tech"
topics: ["opencode", "chatgpt", "coding", "mcp", "local"]
published: false
published_at: 2026-08-13 12:09
---

OpenCode Goは最初の月$5、その後$10/月。

DeepSeek V4 Flashは、公式が観測した典型的な利用パターンなら **月158,150 requests相当** とされている。

数字だけ見たときは、正直「安いな」で終わった。

でも最近の自分の作業を思い返していたら、これ、かなり欲しかったものに近いかもしれないと思った。

## ChatGPTで決められる。でも、その先がローカルに残る

いまはChatGPTでかなりの仕事をしている。

GitHubを横断して次に触るrepoを決める。IssueやPRを見る。記事を直す。金融データを読む。画像を作る。scheduled taskも回す。

[個人開発が123個になって分かった。ChatGPTに任せるべきはコードより「次の1件」だった](https://zenn.dev/kafka2306/articles/chatgpt-multiproject-autonomy) でも書いたけれど、考えるところ、選ぶところはかなりChatGPTに寄せられるようになった。

一方で、最後まで寄せきれない仕事がずっと残っている。

以前、local Codexとのbridgeを作ったとき、自分でこう書いていた。

- 数百GBのローカルデータ
- GPU環境
- USBでつながった実機
- 社内VPN内のシステム
- 認証済みのデスクトップアプリ
- commit前の作業中workspace

[GitHub IssueをAIの伝言板にしたら、伝言板に全部やらせてはいけないと分かった](https://zenn.dev/kafka2306/articles/codex-chatgpt-github-issue-bridge)

読み返していて、「まさにここだ」と思った。

ChatGPTで方針を決めたあと、結局自分のPCへ戻って、localの状態を見ながら続きをやる。その部分をもっとAIに任せたかった。

Unityも同じで、PrefabのAnimatorやPhysBone、Contact、Transform階層、Play Modeでの実挙動は、GitHub上のコードだけでは決めきれない。実際のEditorを見ないと分からない。

## OpenCode Goなら、そこに置けそうだった

OpenCodeにはshellを実行する`bash`、fileのread/edit/write、local MCP serverとの接続がある。

つまり、自分のPC上のrepoを読み、testを回し、fileを直し、必要ならlocal MCP経由でUnityなどに触る、という使い方ができる。

そこでようやく、月158,150 requests相当という数字が自分に繋がった。

「そんなに会話できる」のではなく、

**localで何度も試して、直して、testして、また直す余裕があるかもしれない。**

こっちの方がずっと重要だった。

## ChatGPTを置き換えたいわけではない

ここも自分の中ではかなりはっきりしている。

ChatGPTは今のまま使いたい。

調査したり、複数repoを横断したり、次に何をやるか決めたりする場所として便利だからだ。

OpenCode Goに期待しているのは、その代わりではない。

**ChatGPTで決めたことを、自分のPC側で大量に実行する役。**

この役割なら、月$10はかなり納得しやすい。

## 他と比べるとこう見える

| Service | 月額 | 今の自分なら |
|---|---:|---|
| **OpenCode Go** | **$10** | local repo・shell・test・MCPを回す |
| **GitHub Copilot Pro** | **$10** | GitHub/IDE中心なら強い |
| **Cursor Pro** | **$20** | EditorごとAgent中心にするなら便利 |
| **Claude Pro + Claude Code** | **$20** | Claudeとterminal codingをまとめたいなら自然 |
| **ChatGPT Plus + Codex** | **$20** | 今の調査・判断・横断作業の中心 |

OpenCode Goの158,150回はhard quotaではない。DeepSeek V4 Flashの月$60 usageを、公式の典型的なtoken/cache patternからrequest数へ換算した推定値である。

でも、もうその数字そのものにはあまり惹かれていない。

**自分が何度も「ここはlocalでやりたい」と感じていた場所に、月$10でAIを置ける。**

それなら試したい。

あとは実際にrepoやUnity/MCP作業をやらせてみて、どれだけ仕事が終わるかを見るだけだと思っている。

## 注意：local実行とlocal推論は別

OpenCode GoはローカルLLMを買うサービスではない。GoのmodelはOpenCode Go provider経由で利用する。

ここで言うlocalは、**実行場所とtool accessが自分のPCにある**という意味で、推論まで完全offlineという意味ではない。

## 公式情報

- OpenCode Go: https://opencode.ai/docs/go/
- OpenCode Tools: https://opencode.ai/docs/ja/tools/
- OpenCode MCP servers: https://opencode.ai/v2/docs/mcp-servers
- GitHub Copilot plans: https://docs.github.com/en/copilot/concepts/billing/individual-plans
- Cursor pricing: https://cursor.com/pricing
- Claude Pro: https://support.claude.com/en/articles/8325606-what-is-the-pro-plan
- Codex usage: https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan/

料金・model・利用上限は変更される。契約時には現行の公式情報を再確認する。