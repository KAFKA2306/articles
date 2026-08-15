---
title: "ChatGPTとOpenCode Goを競合させない。local実行だけを分離する"
emoji: "♾️"
type: "tech"
topics: ["opencode", "chatgpt", "coding", "mcp", "local"]
published: false
published_at: 2026-08-13 12:09
---

OpenCode Goを見て、最初は単純に安いと思った。

初月$5、その後$10/月。DeepSeek V4 Flashは、公式が観測した典型的な利用パターンなら月158,150 requests相当とされている。

でも、いまの自分には「ChatGPTの代わり」が欲しいわけではない。

**ChatGPTはそのまま使って、local実行だけ別に任せたい。**

これが一番しっくりきた。

## ChatGPTで考えて、localで実行する

いまはChatGPTで、GitHubを横断して次に触るrepoを決めたり、IssueやPRを見たり、記事や調査を進めたりしている。

以前の記事でも、123個の個人開発を横断すると、コードを書くこと以上に「次に何を進めるか」を決める仕事が重くなると書いた。

- [個人開発が123個になって分かった。ChatGPTに任せるべきはコードより「次の1件」だった](https://zenn.dev/kafka2306/articles/chatgpt-multiproject-autonomy)

この部分はChatGPTでかなり満足している。

困るのは、その先だ。

自分のPCにしかないものを触りたい。

- commit前のworkspace
- 大きなローカルデータ
- GPU環境
- 認証済みのデスクトップアプリ
- Unity EditorやPrefabの実状態
- local MCPでつないだtool

これはGitHub上の状態だけでは完結しない。

以前local Codexとのbridgeを作ったときも、結局ここが残った。

- [GitHub IssueをAIの伝言板にしたら、伝言板に全部やらせてはいけないと分かった](https://zenn.dev/kafka2306/articles/codex-chatgpt-github-issue-bridge)

## OpenCode Goには、その役だけを期待する

OpenCodeには、project環境でshell commandを実行する`bash`、fileのread/edit/write、MCP serverとの接続がある。

なので使い分けはかなり単純にできる。

```text
ChatGPT
考える / 調べる / 横断する / 次を決める

OpenCode Go
local repoを読む / 直す / testする / shellを回す / local MCPを触る
```

OpenCode Goに記事を書かせたいわけでも、金融を調べさせたいわけでもない。

**local executionだけを担う契約として使う。**

そう考えると、自分の中ではかなり整理された。

## 158,150回より、localで何回やり直せるか

OpenCode Goの利用制限はrequest数ではなくドル換算で、公式docsでは5時間$12、週間$30、月間$60のusageとされている。

DeepSeek V4 Flashの月158,150 requestsは、そのusageを典型的なtoken/cache patternから換算した推定値で、hard quotaではない。

でも自分にとって重要なのは、もう158,150という数字ではない。

```text
直す
↓
testする
↓
失敗する
↓
また直す
```

このlocal loopを、料金をあまり気にせず何度も回せるか。

そこに月$10を払う価値を感じている。

ChatGPTとの役割も競合しない。

**考える場所は変えない。実行する場所だけ増やす。**

今のところ、この使い方が一番試してみたい。

## 注意：local実行とlocal推論は別

OpenCode Goはlocal LLMの契約ではない。GoのmodelはOpenCode Go provider経由で利用する。

ここでいうlocalは、実行場所とtool accessが自分のPCにあるという意味で、推論まで完全offlineという意味ではない。

## 公式情報

- OpenCode Go: https://opencode.ai/docs/go/
- OpenCode Tools: https://opencode.ai/docs/ja/tools/
- OpenCode MCP: https://opencode.ai/docs/mcp-servers/

料金・model・利用上限は変更されるため、契約時には現行docsを再確認する。