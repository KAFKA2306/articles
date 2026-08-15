# Zenn Portfolio Audit — 2026-08-15

## Purpose

Zennで公開されている記事を「昔書いたものだから残す」のではなく、**現在の読者へどんな判断能力を渡すか**で再評価する。

今回の監査は、次の2集合を突き合わせた。

1. Zenn上で個別公開URLを確認できたlegacy記事 10本
2. current `KAFKA2306/articles` で `published: true` のZenn同期記事 9本

合計 **19 public records** をportfolio review対象とした。

Zenn profileの集計表示はcache/取得時点で差が出る可能性があるため、本監査ではprofile上の総数ではなく、**個別URLとcurrent repository stateを正準**にした。

## External publication policy

Zenn公式の2026-03-10 AIコンテンツ方針は、AI利用自体ではなく、著者が主体となって正確性を検証し、経験・洞察を含めることを求めている。また、著者の確認が追いつかない速度の投稿や機械生成spamを問題視している。

- https://info.zenn.dev/2026-03-10-ai-contents-guideline
- https://zenn.dev/guideline

ZennのGitHub連携では、repository側の変更は同期される一方、記事の完全削除はZenn dashboard側の削除も必要と公式手順にある。

- https://zenn.dev/zenn/articles/connect-to-github

したがって本監査では、agentがdashboardを操作できないlegacy記事は `RETIRE_PENDING_ZENN_DASHBOARD` とする。public URLが消えるまで「削除済み」とは扱わない。

## What the portfolio is actually about

強い記事から抽出されるsignatureは、AI、GitHub、Unity、投資、CI/CDそのものではない。

**「ある証拠が、どの判断までを許可するか」を分離する記事**である。

反復している境界:

```text
implementation != validation
capability != authority
runner != policy / oracle
build != release != production verification
detection != independent verification
value != provenance
agent ability != delegated permission
artifact exists != visual/runtime completion
latest knowledge != decision-time evidence
```

強い記事は、toolを説明するのではなく、次の順で読者の判断を変える。

```text
失敗 / 異常 / 数字
  -> もっともらしい誤解
  -> 一次情報 / public artifact
  -> 証明できる範囲の境界
  -> 仮説更新
  -> decision rule
```

## Lifecycle rubric

- `KEEP`: 現在のportfolio signatureに強く一致し、証拠・reader job・decision ruleが十分。
- `REVALIDATE`: 核は残すが、価格・quota・product stateなど短いhalf-lifeを持つ。
- `REWRITE`: 核は価値があるが、現在の証拠/編集基準に不足。
- `MERGE`: reader jobが別記事に上位互換されている。
- `RETIRE_PENDING_ZENN_DASHBOARD`: current portfolioから外す。dashboard削除待ち。

## Current repo-managed public articles — 9

| Article | Public URL | Decision | Why |
|---|---|---|---|
| 人は他人を「何を任せられるか」で圧縮する——成果物が仕事の証拠になるまで | https://zenn.dev/kafka2306/articles/2026-08-13-02-how-people-compress-a-person | `KEEP` | skill列挙よりwork sample / verification / reuseで委任可能性を示す。career論ではなく「何を任せられるか」を証拠へ変換するdecision modelになっている。 |
| Claude Codeにテストを全部任せるなら、先に「合格条件」を固定する | https://zenn.dev/kafka2306/articles/2026-08-15-hook-runner-is-not-policy | `KEEP` | runnerとpolicy/oracleを分離し、agent実行能力と合格条件を別authorityとして扱う。current signatureの中心。 |
| 個人開発が123個になって分かった。ChatGPTに任せるべきはコードより「次の1件」だった | https://zenn.dev/kafka2306/articles/chatgpt-multiproject-autonomy | `KEEP` | PR数を自慢で終わらせず、state / contract / evidenceを外部化して「次を選ぶ」制御loopへ抽象化している。 |
| AIの文章に「透かし」があると言われたら、誰がそれを証明できるのか | https://zenn.dev/kafka2306/articles/claude-watermark-secret-key-detection | `KEEP` | vendor未公開仕様を推測せず、embedding / secret / detection / verification interfaceを分離。未確認を正しいstateとして残す。 |
| GitHub IssueからAIにローカルPCを任せてよいのか？ Unity・Blender・動画生成で考える安全な橋 | https://zenn.dev/kafka2306/articles/codex-chatgpt-github-issue-bridge | `KEEP` | coding-agent紹介ではなくlocal state / binary asset / GPUへ責務が広がるときの権限・証拠・completion boundaryを扱う。 |
| ChatGPTを使い倒している私に、月10ドルのOpenCode Goが刺さった理由 | https://zenn.dev/kafka2306/articles/opencode-go-deepseek-v4-chatgpt-usage-scale | `REVALIDATE` | 「reasoning/control planeとlocal executionを分ける」という核は再利用可能。ただしprice / request estimate / provider planは短いhalf-lifeを持つため定期再検証が必要。 |
| 2026年、Unity MCPはどこまで実用か――14件で見えた「作れるが、見た目と挙動を監査し切れない」壁 | https://zenn.dev/kafka2306/articles/unity-mcp-editor-boundary | `KEEP` | 複数の実運用例と自前repoを比較し、CAN_GENERATE != CAN_AUDIT_THE_RESULTを示す。authoringとvisual/gameplay/runtime auditを分離。 |
| 速く出すために、勝手に出さない。GitHubとShopifyに学ぶRelease Engineering | https://zenn.dev/kafka2306/articles/validate-before-pages-deploy | `KEEP` | GitHub/Google/Shopifyの一次情報と自前追試を接続し、build / validate / release / verifyを分離。一般CI/CD解説よりdecision ruleが強い。 |
| 第二の脳の次に必要なのは「意思決定のGit」だ——投資判断を後知恵バイアスから守る | https://zenn.dev/kafka2306/articles/why-i-could-buy-the-crash | `KEEP` | 知識保存ではなくdecision-time uncertaintyを固定するという別reader jobを持ち、結果を知った後の物語と当時の判断をdiff可能にする。 |

### Current-public conclusion

現行9本は、8本を`KEEP`、1本を`REVALIDATE`とする。

削除対象を作るために基準を厳しくするのではない。現行群は2026-08の刷新を繰り返した結果、旧群より明確に現在のsignatureへ収束している。

## Legacy public articles — 10

### 1. Crash-Driven Development

- URL: https://zenn.dev/kafka2306/articles/11cd731eebded1
- Published: 2026-01-30
- Decision: `RETIRE_PENDING_ZENN_DASHBOARD`

価値の核は「失敗を隠さずstack traceを観測可能にする」にある。しかし記事全体は独自doctrineとして強く一般化され、現在の基準で必要なclaim calibration / public experiment / non-goalが弱い。

**Reuse:** fail-loud / observable failureの核だけを、将来の検証可能な記事へ統合する。旧page自体は残さない。

### 2. Astral Toolchain / Modern Python Zero-Fat

- URL: https://zenn.dev/kafka2306/articles/2005501fe91754
- Published: 2026-02-22
- Decision: `RETIRE_PENDING_ZENN_DASHBOARD`

Ruff/uv等のtoolchain紹介と独自「Zero-Fat」frameworkが中心。現在の基準では、どのfaultをどのauthorityが検出したかというcontrolled evidenceが不足し、tool stack自体が価値になっている。

**Superseded by:** verification-stack系のcontrolled experimentsと、個別authorityを測る現在の方針。

### 3. AAARTS autonomous alpha system

- URL: https://zenn.dev/kafka2306/articles/c599b0556555a7
- Published: 2026-03-01
- Decision: `RETIRE_PENDING_ZENN_DASHBOARD`

複数概念を束ねた大きなarchitecture提案だが、記事の中心価値に対して実運用・失敗fixture・再現証拠が薄い。現在なら「frameworkを提案した」では公開しない。

**Reuse:** 個別componentが公開実験で反証可能になった場合のみ、別記事として再発見する。

### 4. agent-resources article with biographical/AI policy report body

- URL: https://zenn.dev/kafka2306/articles/9f9997babac335
- Published: 2026-03-08
- Decision: `RETIRE_PENDING_ZENN_DASHBOARD` — highest priority

タイトルがagent-resourcesのdeveloper hubを約束する一方、本文は別人物の経歴・AI方針等を扱う長いreportへ逸脱しており、**title/body promise mismatch**が大きい。現在のportfolioに残す合理性がない。

### 5. Windows Docker × Gemini CLI × everything-claude-code install commands

- URL: https://zenn.dev/kafka2306/articles/cd6f21d4a26bdd
- Published: 2026-03-19
- Decision: `RETIRE_PENDING_ZENN_DASHBOARD`

導入command中心で、version / provider / package stateに強く依存する短寿命how-to。固有experimentやportable decision ruleが弱い。

### 6. AI agent directory-management guidelines

- URL: https://zenn.dev/kafka2306/articles/5c21f4d010baeb
- Published: 2026-03-27
- Decision: `RETIRE_PENDING_ZENN_DASHBOARD`

一般的best practiceと推奨値の組み合わせが中心。どのdirectory failureを何件観測し、どのruleで改善したかというground truthが不足する。

**Reuse:** 実repoでcontext rot / file discovery / residueのfaultを測った記事へ統合可能。

### 7. Zero-trust contract

- URL: https://zenn.dev/kafka2306/articles/77e6af7be1d527
- Published: 2026-05-13
- Decision: `RETIRE_PENDING_ZENN_DASHBOARD` / `MERGE concept`

「LLMの自己申告を受け入れずartifact / test / proofで完了判定する」という核は現在のsignatureそのもの。一方、旧稿は絶対表現・独自principle命名が強く、現在の `hook-runner-is-not-policy` 等が、より狭く・証拠付きで同じreader jobを上位互換している。

**Superseded by:** https://zenn.dev/kafka2306/articles/2026-08-15-hook-runner-is-not-policy

### 8. Adaptive Survivable Verification System (ASVS)

- URL: https://zenn.dev/kafka2306/articles/5c3c93f798da3f
- Published: 2026-05-17
- Decision: `RETIRE_PENDING_ZENN_DASHBOARD`

大きな独自verification frameworkを先に提示する構成で、現在の「failure first / boundary first / controlled evidence」方針と逆。frameworkそのものをauthorityにしてしまうリスクがある。

### 9. AI活用してそうな情報サイトのクオリティがすごい

- URL: https://zenn.dev/kafka2306/articles/1436dad81ab3ac
- Published: 2026-06-11
- Decision: `RETIRE_PENDING_ZENN_DASHBOARD` — highest priority

実体は外部websiteのcategory別link list。固有の観測、比較protocol、検証、decision ruleがなく、現在のarticle contractではcandidate段階で不採用になる。

### 10. GEO / AEO operations guideline

- URL: https://zenn.dev/kafka2306/articles/6dd453d941b99f
- Published: 2026-06-13
- Decision: `RETIRE_PENDING_ZENN_DASHBOARD` — highest priority

generic SEO/GEO checklistと多数の数値的推奨が中心。現在の基準では、各数値のprimary evidence / scope / reproductionを確認できない限り公開claimにしない。

## Retirement order

Zenn dashboardで削除する順序:

1. https://zenn.dev/kafka2306/articles/9f9997babac335
2. https://zenn.dev/kafka2306/articles/1436dad81ab3ac
3. https://zenn.dev/kafka2306/articles/6dd453d941b99f
4. https://zenn.dev/kafka2306/articles/2005501fe91754
5. https://zenn.dev/kafka2306/articles/c599b0556555a7
6. https://zenn.dev/kafka2306/articles/cd6f21d4a26bdd
7. https://zenn.dev/kafka2306/articles/5c21f4d010baeb
8. https://zenn.dev/kafka2306/articles/5c3c93f798da3f
9. https://zenn.dev/kafka2306/articles/11cd731eebded1
10. https://zenn.dev/kafka2306/articles/77e6af7be1d527

最初の3本は、title/body mismatch、純link集、unsupported-number-heavy guidelineという理由で、現在のportfolio signalを最も強く薄める。

## Exact human action for legacy deletion

旧10本はcurrent `articles/` に対応sourceが存在しないweb-created legacy postsとして扱うため、available GitHub toolsだけではpublic deletionを完了できない。

Zenn公式手順に従い、人間が各記事についてdashboardで削除を実行する。

```text
Zenn dashboard
  -> 記事の管理
  -> 対象article
  -> 削除
```

削除後はpublic URLを再取得し、404/非公開を確認して初めてretirementを完了とする。

**この監査documentを作っただけでは削除完了ではない。**

## New portfolio rule

今後、公開前に次の問いへ全部答える。

```text
Reader job:
Observed anomaly:
Initial hypothesis:
Strongest public evidence:
What the evidence proves:
What it does NOT prove:
Hypothesis update:
Decision rule:
Non-goal:
Why this deserves a separate article:
Half-life / revalidation trigger:
```

公開後も同じ問いで再監査する。

**公開記事を増やすことより、弱い記事を退役させ、1本あたりの信頼密度を上げることを優先する。**
