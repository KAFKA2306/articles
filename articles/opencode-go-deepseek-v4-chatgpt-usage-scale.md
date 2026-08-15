---
title: "月10ドルのOpenCode Goは安いのか？ Copilot・Cursor・Claude Code・Codexと比べる"
emoji: "♾️"
type: "tech"
topics: ["opencode", "ai", "coding", "cost", "capacity"]
published: false
published_at: 2026-08-13 12:09
---

OpenCode Goは月$10。

DeepSeek V4 Flashには、公式表で **月158,150 requests相当** とある。

では、他のAI codingサービスと比べても安いのか。

## 私はいま、ChatGPTをかなり重く使っている

私にとってChatGPTは、もう「たまに質問するチャット」ではない。

GitHubの複数repoを横断して状態を確認し、IssueやPR、CIを追う。記事を調査して書き直す。金融データを読む。画像を作る。scheduled taskの設計や運用も任せる。

同じ日に、これらを何本も並行して進めることも普通になった。

使っていて感じるのは、**「何回質問したか」では負荷を表せない**ということだ。

短い確認を1回するのと、大きなrepoを読み、検索し、修正し、CIまで追う1回では重さがまるで違う。

だからOpenCode Goの「158,150 requests」を見たときも、単純に「ChatGPTより何倍使える」とは思わなかった。

むしろ気になったのは、**この価格で、どれだけ重い仕事を継続して回せるのか**だった。

## 先に比較する

2026年8月15日時点の公式情報を並べるとこうなる。

| Service | 月額 | 含まれる利用量の見え方 | 向いている使い方 |
|---|---:|---|---|
| **OpenCode Go** | **$10** | DeepSeek V4 Flashは月$60 usage、約158,150 requests相当 | とにかく安く大量に回す |
| **GitHub Copilot Pro** | **$10** | 1,500 AI Credits = $15相当。code completionは無制限 | GitHub中心の開発 |
| **Cursor Pro** | **$20** | $20のAPI Agent usage + bonus usage | IDEとAgentを一体で使う |
| **Claude Pro + Claude Code** | **$20** | 固定request数ではなく5時間・週単位のusage limit | Claudeを開発と日常利用で共用 |
| **ChatGPT Plus + Codex** | **$20** | 固定request数ではなく、Codexはtoken-based credit pricing | Codex以外のChatGPT機能も使う |

## OpenCode Goの数字だけは読み方に注意

158,150回はhard quotaではない。

OpenCode Goの上限はドル換算で、

```text
5時間  $12
1週間  $30
1か月  $60
```

と定義されている。

DeepSeek V4 Flashを公式が観測した典型的なtoken / cache patternで使うと、その月$60が**約158,150 requests相当**になる、という意味だ。

さらに全modelが月$60ではない。DeepSeek V4 Proは月$15相当である。

## では、どれを選ぶか

私のようにAIを常時作業レイヤーとして使うなら、かなり単純である。

**安い計算資源を大量に欲しいならOpenCode Go。**

同じ$10でも、GitHubとの統合や無制限code completionまで欲しいならCopilot Pro。

IDE、Cloud Agent、MCPまで一体化した製品が欲しいならCursor。

ClaudeやChatGPTをコーディング以外にも使うなら、Claude ProやChatGPT Plusの方が契約をまとめやすい。

私はChatGPTを開発だけでなく、調査、記事、金融、画像、タスク運用まで横断して使っているので、単純な「推論単価」だけでは置き換えられない。

その一方で、GitHub作業を大量に回す部分だけ切り出すと、OpenCode Goの安さはかなり魅力的に見える。

つまりOpenCode Goの強みは、AI coding全部入りではない。

**月$10で、対応modelの推論容量をかなり安く買えること。**

ヘビーユースしているからこそ、158,150という派手な数字そのものより、こちらの方が重要だと感じる。

## 公式情報

- OpenCode Go: https://opencode.ai/docs/go/
- GitHub Copilot individual plans: https://docs.github.com/en/copilot/concepts/billing/individual-plans
- GitHub Copilot billing: https://docs.github.com/en/billing/concepts/product-billing/github-copilot-billing
- Cursor pricing: https://cursor.com/pricing
- Cursor models & pricing: https://docs.cursor.com/account/pricing
- Claude Pro: https://support.claude.com/en/articles/8325606-what-is-the-pro-plan
- ChatGPT Plus: https://help.openai.com/en/articles/6950777-what-is-chatgpt-plus
- Codex usage limits: https://help.openai.com/en/articles/11369540-codex-and-chatgpt-plan-usage-limits
- Codex rate card: https://help.openai.com/en/articles/20001106-codex-rate-card

各社の料金・利用上限は変更される。契約時には現行の公式情報を再確認する。