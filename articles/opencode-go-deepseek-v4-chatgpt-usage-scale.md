---
title: "月10ドルのOpenCode Goは本当に安いのか？ Copilot・Cursor・Claude Code・Codex・Antigravityと「容量」で比べる"
emoji: "♾️"
type: "tech"
topics: ["opencode", "ai", "coding", "cost", "capacity"]
published: false
published_at: 2026-08-13 12:09
---

OpenCode GoのDeepSeek V4 Flashには、公式表で **月158,150 requests** という数字が出ている。

最初に見ると、

> これってほぼ無限では？

と思う。

しかし、2026年8月15日時点で他のAI coding subscriptionまで横に並べると、見るべき数字はrequest数ではなかった。

**OpenCode Go / GitHub Copilot / Cursor / Claude Code / OpenAI Codex / Google Antigravityは、そもそも「利用量」の売り方が違う。**

そして比較して初めて、OpenCode Goの強みも弱みも見える。

この記事の結論を先に書く。

- **raw compute capacityを安く買う**なら、OpenCode Goはかなり異質に強い
- **GitHubとの統合まで含める**なら、同じ月$10でもCopilot Proは別の商品になる
- **IDE・Cloud Agent込み**ならCursorはusageだけで比較できない
- Claude Code / Codex / Antigravityは、固定request数より**動的なrate limit / agentic usage**として売られている
- 最後に比較すべきKPIは `requests / month` ではなく、**`completed work / $`** である

## 2026年のAI codingは「何回使えるか」から離れつつある

少し前までAI coding subscriptionは、

```text
500 requests / month
1000 requests / day
```

のような数字で比較しやすかった。

しかし2026年8月時点では、大手の多くがそこから離れている。

GitHub Copilotは2026年6月1日にrequest-based billingから**token使用量に応じたAI Credits**へ移行した。

Cursorも第三者modelはAPI価格に連動するusage poolで管理している。

OpenAI Codexも2026年4月にmessage単位から**token-based credit pricing**へ変更した。

Claude CodeとAntigravityも、promptの重さによって消費量が変わるrate-limit型である。

つまり、比較軸はこう変わった。

```text
旧:
subscription price / request count

現在:
subscription price
× included compute
× model quality
× product integration
× task completion rate
```

ここを揃えないと、158,150 requestsと「Claude Codeを何時間使えるか」を同じ表に置いても意味がない。

## まず横に並べる

2026年8月15日時点の公式情報だけを使い、個人向けの入口を並べた。

| Service | 月額の代表プラン | 公開されている利用量の単位 | 固定的に読める容量 | 超過後 |
|---|---:|---|---|---|
| OpenCode Go | **$10** | dollar usage | 5h $12 / week $30 / month最大$60。DeepSeek V4 Flashは月$60、V4 Proは月$15のmodel usage | Zen balanceへfallback可 |
| GitHub Copilot Pro | **$10** | GitHub AI Credits | **1,500 credits/月 = $15相当**。paid planのcode completionはunlimited | 追加AI Creditsを購入可能 |
| Cursor Pro | **$20** | usage pool | third-party models **$20/月** + Cursor Modelsの別pool | 同API rateでon-demand usage |
| Claude Pro | **$20** | session / weekly usage | 固定ドル額は公開されていない。5時間session + weekly limit | usage credits / PAYGへ移行可能 |
| ChatGPT Plus + Codex | **$20** | agentic usage / token credits | 固定ドル額は公開されていない。taskの規模・contextで消費が変動 | creditsを追加購入可能 |
| Google Antigravity | **Free / Pro $20 / Ultra $100・$200** | baseline quota | paidは5時間refresh + weekly limit。絶対量は固定値として公開されていない | purchased AI creditsでoverage |

この表で一番重要なのは、数字の大小ではない。

**公開の仕方そのものが違う。**

OpenCode Go、Copilot、Cursorは比較的「computeの金額換算」が見える。

Claude、ChatGPT/Codex、Antigravityは、subscriptionに含まれるbaseline capacityを固定ドル額へ変換しにくい。

だから「どれが一番多く使えるか」を1つのrequest数へ無理やり変換するのはやめた方がいい。

## OpenCode Goは、$10で最大$60のmodel usageを買う設計

OpenCode Goは初月$5、その後$10/月。

利用制限はrequest数ではなく、公式docsで次のように定義されている。

```text
5時間  = $12 usage
1週間  = $30 usage
1か月  = $60 usage
```

ただし、**全modelが月$60ではない。**

公式のmodel別表では、月間usageはmodelによって$15または$60になっている。

DeepSeekでは、

| Model | 月間model usage | typical requests / month |
|---|---:|---:|
| DeepSeek V4 Pro | **$15** | 17,150 |
| DeepSeek V4 Flash | **$60** | 158,150 |

である。

ここは旧稿より重要なポイントだ。

DeepSeek V4 Flashなら、

```text
subscription: $10
included model usage: $60
nominal leverage: 6x
```

になる。

一方V4 Proなら、

```text
subscription: $10
included model usage: $15
nominal leverage: 1.5x
```

である。

**「OpenCode Goは全部6倍」ではない。modelによって経済性が違う。**

公式も「多くのmodelでは$10に対して6xのusageを目指すが、一部modelは仕入れ・hosting条件のため低い」と説明している。

さらにDeepSeek V4 Flashの158,150 requestsもhard quotaではない。

公式が観測したtypical pattern、

```text
790 input
68,000 cached
280 output tokens / request
```

から換算した推定値である。

したがって正しい読み方は、

> 月158,150回使える

ではなく、

> **DeepSeek V4 Flashを公式の典型的cache patternで使った場合、月$60のusageが約158,150 requestsに相当する**

である。

公式:
https://opencode.ai/docs/go/

## 同じ月$10のGitHub Copilot Proと比べると性格が分かる

月額だけなら、OpenCode GoとGitHub Copilot Proは同じ$10である。

しかし2026年6月以降、CopilotはAI Credits制になった。

Copilot Proは、

```text
price: $10 / month
base credits: 1,000
flex allotment: 500
total: 1,500 AI credits / month
```

である。

GitHubは **1 AI credit = $0.01** と定義しているので、名目上は$15相当のAI usageになる。

```text
Copilot Pro
$10 subscription
→ $15 AI credits
→ 1.5x
```

この数字だけなら、DeepSeek V4 Flashを使うOpenCode Goの$60に対して小さい。

しかしCopilot Proには別の価値がある。

paid planではcode completionsとnext edit suggestionsがAI Credits課金の対象外で、unlimitedである。さらにCopilot Chat、CLI、cloud agentなどGitHubのworkflowへ統合されている。

つまり、

```text
OpenCode Go
= 安価なmodel capacity + agent選択の自由

Copilot Pro
= GitHub-native workflow + completion + agent usage
```

であり、同じ$10でも購入しているものが違う。

公式:
https://docs.github.com/en/copilot/concepts/billing/individual-plans
https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-individuals
https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing

## Cursorは「model代」だけでなく、agent productを買う

Cursor Proは$20/月。

現行docsではusage poolが2つに分かれている。

```text
Cursor Models pool
Other Models pool
```

ProのOther Models poolには、第三者modelのAPI価格換算で**$20/月**が含まれる。

上位は、

| Plan | Price | Other Models usage |
|---|---:|---:|
| Pro | $20 | $20 |
| Pro Plus | $60 | $70 |
| Ultra | $200 | $400 |

である。

ただし、これだけを見てOpenCode Goより割高と結論づけるのも雑だ。

Cursorには別にCursor Models poolがあり、さらにEditor、Agent、Cloud Agents、Bugbot、MCP、skills、hooksなどがproductとして束ねられている。

Cursor自身も、usage dataから、

```text
limited Agent users: often within $20
daily Agent users: typically $60–$100/month
power users with multiple agents/automation: often $200+/month
```

と案内している。

この数字はかなり示唆的である。

**人間が時々Agentを使う世界と、複数agentを自動運転する世界では必要capacityが1桁違う。**

公式:
https://cursor.com/docs/models-and-pricing
https://cursor.com/pricing

## Claude Codeは「prompt数」ではなく共有usage budgetとして読む

Claude Proは$20/月、Maxは$100の5x tierと$200の20x tierがある。

2026年6月の現行Help Centerでは、Claude Codeの利用量を固定prompt数として保証していない。

Claude / Claude Code / Claude Desktopなどの利用は同じusage limitを共有し、消費は会話の長さ、model、project complexity、codebase sizeなどで変わる。

Proにはsession-based limitとweekly limitがあり、session limitは5時間でresetする。

Maxは、

```text
$100 → 5x Pro capacity per session
$200 → 20x Pro capacity per session
```

という設計である。

つまりClaude Codeを、

```text
$20 / N prompts
```

と固定換算するのは現在の公式説明に合わない。

また上限到達後はusage creditsを有効化し、標準API rateによる従量課金へ移行できる。

これはOpenCode Goとはかなり違う商品設計である。

OpenCode Goは「model usageの金額」が比較的明示的。

Claude Codeは「Claude ecosystem全体で共有する作業容量」を買う。

公式:
https://support.claude.com/en/articles/8325606-what-is-the-pro-plan
https://support.claude.com/en/articles/11049741-what-is-the-max-plan
https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan
https://support.claude.com/en/articles/12429409-manage-usage-credits-for-paid-claude-plans

## ChatGPT Plus / Codexもrequest数ではなくtoken-basedへ移った

ChatGPT Plusは$20/月。

Codexは対象planに含まれるが、OpenAIは「何messages使えるか」はtaskの大きさと複雑さで変わると説明している。

さらに2026年4月、Codexのflexible pricingはmessage単位からtoken-basedへ変更された。

つまり、

```text
small script
```

と、

```text
large repo
+ long-running task
+ large context
+ parallel agents
```

を同じ1 messageとして数える意味が薄くなった。

OpenAIのrate cardも、input / cached input / output tokenからcreditsを計算する方式になっている。

上限到達後はPlus / Proの対象ユーザーなら追加creditsを購入できる。

ここでも比較すべきは「何回会話したか」ではない。

```text
agentic usage consumed
completed tasks
human intervention
retry cost
```

である。

公式:
https://help.openai.com/en/articles/6950777-what-is-chatgpt-plus
https://help.openai.com/en/articles/11369540-codex-and-chatgpt-plan-usage-limits
https://help.openai.com/en/articles/20001106-codex-rate-card
https://help.openai.com/en/articles/12642688-using-credits-for-flexible-usage-in-chatgpt-free-go-plus-pro-sora

## GoogleはGemini CLIではなくAntigravityを見る

ここは2026年の記事で特に注意が必要だった。

古い比較記事には、Gemini CLIの「1日1000 requests」などを載せたくなる。

しかしGoogleは2026年6月18日、個人版Gemini Code Assist / Google AI Pro / Ultraによる従来のGemini CLI経路を終了し、consumer usersを**Antigravity**へ移行した。

したがって2026年8月時点で比較対象にするならAntigravityである。

現在は、

```text
Individual: $0
Google AI Pro: $20/month
Google AI Ultra: $100/month
Google AI Ultra: $200/month
```

という階層になっている。

Googleの2026年5月発表では、$100 Ultraは$20 Proの5x、$200 Ultraは20xのtoken capacityとされている。

ただしbaseline quotaの絶対token数は固定値として公開されていない。

Pro / Ultraでは5時間ごとにquotaがrefreshし、weekly limitもある。実際の消費はagentが行ったwork量で変わる。

つまりAntigravityも、固定request数より**work-correlated quota**として読むべきサービスである。

公式:
https://antigravity.google/pricing
https://antigravity.google/docs/plans
https://antigravity.google/blog/changes-to-antigravity-plans
https://developers.google.com/gemini-code-assist/docs/deprecations/code-assist-individuals

## こう並べると、OpenCode Goの異常値が見える

比較可能なところだけ、subscription priceに対する明示的なcompute poolを計算する。

| Plan | Subscription | 明示的なusage value | nominal ratio |
|---|---:|---:|---:|
| OpenCode Go + DeepSeek V4 Flash | $10 | $60 | **6.0x** |
| OpenCode Go + DeepSeek V4 Pro | $10 | $15 | **1.5x** |
| GitHub Copilot Pro | $10 | 1,500 credits = $15 | **1.5x** |
| Cursor Pro | $20 | third-party $20 + Cursor Models pool | **1.0x + first-party pool** |
| Cursor Pro Plus | $60 | third-party $70 + Cursor Models pool | **1.17x + first-party pool** |
| Cursor Ultra | $200 | third-party $400 + Cursor Models pool | **2.0x + first-party pool** |

Claude、Codex、Antigravityはbaseline allowanceを同じドル換算で公式公開していないため、この表から外した。

ここで無理に推定値を作らないことが重要である。

**確認できる数字だけで見ると、DeepSeek V4 Flashを使ったOpenCode Goの6xはかなり目立つ。**

しかし、まだ「最強」とは言えない。

なぜなら$1のcomputeが生む成果はmodelとagent harnessで違うからだ。

## 最後は「1件完了するのに何ドルか」で決める

例えば、安いmodelが1 issueを解くのにretryを繰り返すなら、raw computeが6倍あっても意味がない。

```text
Model A
$0.10 / attempt
10 retries
= $1.00 / completed task

Model B
$0.40 / attempt
1 attempt
= $0.40 / completed task
```

なら、request単価が4倍高いModel Bの方が安い。

AI coding subscriptionで本当に見るべきKPIは、

```yaml
completed_tasks: ...
usage_usd: ...
requests: ...
retries: ...
human_interventions: ...
wall_clock_minutes: ...
```

から作る。

```text
$ / completed task
requests / completed task
retry rate
human intervention rate
minutes / completed task
```

これならOpenCode Go、Copilot、Cursor、Claude Code、Codex、Antigravityを同じ成果軸へ戻せる。

## どれを選ぶか

2026年8月時点の公式仕様から、選択理由はかなり整理できる。

### raw capacityを最優先する

**OpenCode Go**。

特にDeepSeek V4 Flashのように月$60 usage対象の安価modelを高cache率で回す用途では、$10 subscriptionに対するcapacityが大きい。

さらにGoのmodelはAPI endpointでも提供され、OpenCode以外のagentからも利用できる。

### GitHubの中で完結したい

**GitHub Copilot**。

OpenCode Goよりraw computeだけを買う商品ではない。completion、CLI、cloud agent、GitHub workflowとの統合に価値がある。

### editorとagent platformを一体で買う

**Cursor**。

model usageだけでなく、Editor、Cloud Agents、Bugbot、first-party model poolまで含めて判断する。

### Claudeをcoding以外にも日常的に使う

**Claude Pro / Max**。

ClaudeとClaude Codeが同じsubscription / usage budgetに統合されていること自体が価値になる。

### coding以外のresearch・analysisも同じ契約で使う

**ChatGPT Plus / Pro + Codex**。

Codex単体のrequest単価ではなく、ChatGPT全体のtool bundleとして評価する。

### Google ecosystemでagent-first環境を使う

**Antigravity**。

無料tierから入り、必要に応じてPro / Ultraへ上げられる。ただし現在のbaseline quotaは固定request数ではなく動的なので、実測が必要である。

## 「月158,150回」に驚く記事ではなくなった

最初は、OpenCode GoのDeepSeek V4 Flashが月158,150 requests相当という数字を見て、

> 自分にはほぼ無限では？

という話だった。

他サービスまで並べると、もっと重要な構造が見えた。

**2026年のAI coding subscriptionは、request数ではなくcompute budgetをどう商品化するかの競争になっている。**

OpenCode Goは、安いopen modelを大量に回せるcapacity商品。

CopilotはGitHub-nativeなcoding platform。

Cursorはeditor + agent platform。

ClaudeとChatGPTはgeneral AI subscriptionの中にcoding agentを統合している。

Antigravityはagent-first environmentとしてquotaを売っている。

だから、最終的な質問は、

```text
何回使えるか？
```

ではない。

```text
月$10 / $20 / $100 / $200で、
自分の仕事を何件完了できるか？
```

である。

そこまで測れば、OpenCode Goの158,150という大きな数字も、ようやく意思決定に使える。

## 2026年8月15日時点の一次情報

- OpenCode Go: https://opencode.ai/docs/go/
- GitHub Copilot individual plans: https://docs.github.com/en/copilot/concepts/billing/individual-plans
- GitHub Copilot usage-based billing: https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-individuals
- GitHub Copilot model pricing: https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing
- Cursor Models & Pricing: https://cursor.com/docs/models-and-pricing
- Claude Pro: https://support.claude.com/en/articles/8325606-what-is-the-pro-plan
- Claude Max: https://support.claude.com/en/articles/11049741-what-is-the-max-plan
- Claude Code with Pro / Max: https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan
- ChatGPT Plus: https://help.openai.com/en/articles/6950777-what-is-chatgpt-plus
- Codex usage limits: https://help.openai.com/en/articles/11369540-codex-and-chatgpt-plan-usage-limits
- Codex rate card: https://help.openai.com/en/articles/20001106-codex-rate-card
- Google Antigravity pricing: https://antigravity.google/pricing
- Google Antigravity plans: https://antigravity.google/docs/plans
- Google Antigravity plan changes: https://antigravity.google/blog/changes-to-antigravity-plans
- Gemini Code Assist consumer deprecation: https://developers.google.com/gemini-code-assist/docs/deprecations/code-assist-individuals

各社とも利用上限・model・pricingは変更される。この記事の数値を将来読む場合は、必ず現行の公式docsを再確認する。
