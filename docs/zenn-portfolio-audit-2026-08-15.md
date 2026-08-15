# Zenn Portfolio Audit — 2026-08-15 v2

## Purpose

Zenn公開記事を、単なる正確性や「証拠境界」の厳密さではなく、**読者にとって読む理由があるか**で再監査する。

今回の基準は次の7軸。

1. **Reach** — intended audienceがproblemを自分事にできる入口か
2. **Customer value** — 時間・失敗・risk・uncertaintyを減らすか、capabilityを増やすか
3. **Originality** — docs / generic AI summaryで代替しにくいか
4. **Experience** — 実体験・実測・失敗・運用が見えるか
5. **Utility** — 読後に持ち帰れるdecision / checklist / patternがあるか
6. **Trust** — 一次情報・公開artifact・claim calibrationが十分か
7. **Portfolio value** — 残すことで著者のsignalが強くなるか

編集原則はGoogle Search Centralのpeople-first content自己評価とZennの現行ガイドラインを参照する。

- https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- https://developers.google.com/search/docs/fundamentals/creating-helpful-content?hl=ja
- https://zenn.dev/guideline
- https://info.zenn.dev/2026-02-03-community-guidelines-update
- https://info.zenn.dev/2026-03-10-ai-contents-guideline

Googleはintended audience、first-hand expertise、original information/research/analysis、読後のgoal completion、他ページより実質的な価値を自己評価項目としている。Zennは具体的な試行錯誤・書き手固有の視点・実体験を重視している。

## Portfolio thesis

今回の再読で、現在出したい記事を次のように定義し直す。

> **広い読者が自分事にできる問題を入口に、書き手固有の実体験・実測・失敗から、AI要約や公式docsだけでは得にくい見方を渡し、読後の判断や行動を一段よくする記事。**

短縮すると:

```text
Broad door
  -> Original insight
  -> Concrete proof
  -> Useful exit
```

`authority / verification / decision boundary` は重要なproof techniqueであるが、portfolioの主題そのものではない。

## Lifecycle

- `KEEP` — Reach / customer value / originality / utility / trustが強い
- `REVALIDATE` — core valueは強いがvolatile factを再確認
- `REWRITE` — core experience/insightは残すが入口・価値・構成を再設計
- `MERGE` — stronger articleへ統合
- `RETIRE_PENDING_ZENN_DASHBOARD` — public portfolioから外す。Zenn dashboard deletion待ち

## Current repo-managed public articles — 9

| Article | URL | Decision | Reader-value review |
|---|---|---|---|
| 人は他人を「何を任せられるか」で圧縮する——成果物が仕事の証拠になるまで | https://zenn.dev/kafka2306/articles/2026-08-13-02-how-people-compress-a-person | `KEEP` | 技術者以外にも通じる「能力をどう伝えるか」が入口。複数domainの公開成果をwork sampleへ変換する独自性があり、career/portfolio設計へ持ち帰れる。 |
| Claude Codeにテストを全部任せるなら、先に「合格条件」を固定する | https://zenn.dev/kafka2306/articles/2026-08-15-hook-runner-is-not-policy | `KEEP` | 「AIに全部任せたい」という広い欲求から入り、agent利用者のfalse confidenceを減らす。Claude Code固有記事に見えて、automation全般へ移植可能。 |
| 個人開発が123個になって分かった。ChatGPTに任せるべきはコードより「次の1件」だった | https://zenn.dev/kafka2306/articles/chatgpt-multiproject-autonomy | `KEEP` | 123 repo / 813 PRという具体性が強く、AI codingの速度論を「次を決める仕事」へreframeする。独自運用データと広いproblemが接続している。 |
| AIの文章に「透かし」があると言われたら、誰がそれを証明できるのか | https://zenn.dev/kafka2306/articles/claude-watermark-secret-key-detection | `KEEP` | AI生成判定という一般的な関心から入り、公開仕様の不確実性を含めて検証可能性へ整理する。技術・採用・教育・mediaに横展開できる。 |
| GitHub IssueからAIにローカルPCを任せてよいのか？ Unity・Blender・動画生成で考える安全な橋 | https://zenn.dev/kafka2306/articles/codex-chatgpt-github-issue-bridge | `KEEP` | titleはやや技術寄りだが「AIに自分のPCをどこまで任せるか」というproblemは広い。Unity/Blender/GPU実運用が固有proof。次回はさらにproblem-first titleを優先。 |
| ChatGPTを使い倒している私に、月10ドルのOpenCode Goが刺さった理由 | https://zenn.dev/kafka2306/articles/opencode-go-deepseek-v4-chatgpt-usage-scale | `REWRITE + REVALIDATE` | reasoning/controlとlocal executionを分ける発見は価値がある。一方、商品名・価格・request estimateが入口を支配しhalf-lifeも短い。「AI作業で最後までPCに残る仕事をどう渡すか」へ再設計した方がdurable valueが高い。 |
| 2026年、Unity MCPはどこまで実用か――14件で見えた「作れるが、見た目と挙動を監査し切れない」壁 | https://zenn.dev/kafka2306/articles/unity-mcp-editor-boundary | `KEEP` | nicheだがAI game/3D developerにはstakesが明確。14外部事例＋自前repoというfirst-hand/field-review価値が高く、setup記事では得られない判断材料を渡す。 |
| 速く出すために、勝手に出さない。GitHubとShopifyに学ぶRelease Engineering | https://zenn.dev/kafka2306/articles/validate-before-pages-deploy | `KEEP` | 「速く出したい」という普遍的欲求から入り、安全確認を減らさず待ちを減らすreframeがある。Google/GitHub/Shopify一次情報＋自前追試でuseful exitが強い。 |
| 第二の脳の次に必要なのは「意思決定のGit」だ——投資判断を後知恵バイアスから守る | https://zenn.dev/kafka2306/articles/why-i-could-buy-the-crash | `KEEP` | Obsidian/Notionという広い入口から、knowledge managementではなくdecision-time uncertainty保存へreframe。個人の実判断ログと研究を接続し、独自性・顧客価値とも強い。 |

### Current set conclusion

- `KEEP`: 8
- `REWRITE + REVALIDATE`: 1

現行群の強い記事は、**技術名より先に人間のproblem / desireがあり、その後に固有proofへ降りている**。

## Legacy public articles — 10

legacy 10本は前回auditの`RETIRE_PENDING_ZENN_DASHBOARD`を維持する。新しいreader-value基準で見ても、残す理由は強くならない。

| URL | Decision | Reader-value reason |
|---|---|---|
| https://zenn.dev/kafka2306/articles/9f9997babac335 | `RETIRE_PENDING_ZENN_DASHBOARD` | title/body promise mismatch。Reach以前にreader expectationを壊す。 |
| https://zenn.dev/kafka2306/articles/1436dad81ab3ac | `RETIRE_PENDING_ZENN_DASHBOARD` | link collection中心。generic AI/searchで代替しやすくoriginal valueが弱い。 |
| https://zenn.dev/kafka2306/articles/6dd453d941b99f | `RETIRE_PENDING_ZENN_DASHBOARD` | generic GEO/AEO checklist。first-hand evidenceとunsupported-number riskの問題。 |
| https://zenn.dev/kafka2306/articles/2005501fe91754 | `RETIRE_PENDING_ZENN_DASHBOARD` | toolchain自体が主役。読者problemよりstack名が入口で、現在のcontrolled experiment型記事に劣る。 |
| https://zenn.dev/kafka2306/articles/c599b0556555a7 | `RETIRE_PENDING_ZENN_DASHBOARD` | large framework proposalが先行し、読者の具体的job・first-hand proofが薄い。 |
| https://zenn.dev/kafka2306/articles/cd6f21d4a26bdd | `RETIRE_PENDING_ZENN_DASHBOARD` | install/how-to中心でhalf-lifeが短く、commodity化しやすい。 |
| https://zenn.dev/kafka2306/articles/5c21f4d010baeb | `RETIRE_PENDING_ZENN_DASHBOARD` | generic guideline。具体的failureとcustomer outcomeが弱い。 |
| https://zenn.dev/kafka2306/articles/5c3c93f798da3f | `RETIRE_PENDING_ZENN_DASHBOARD` | framework-first。読者problemより独自概念が前面に出る。 |
| https://zenn.dev/kafka2306/articles/11cd731eebded1 | `RETIRE_PENDING_ZENN_DASHBOARD` / `MERGE concept` | fail-loudの核は有用だがdoctrine-first。具体problem+experimentに分解して再利用する方が強い。 |
| https://zenn.dev/kafka2306/articles/77e6af7be1d527 | `RETIRE_PENDING_ZENN_DASHBOARD` / `MERGE concept` | zero-trust completionの核は有用だが抽象principleが先行。現在のClaude Code/Release Engineering記事が同じreader jobをより具体的に満たす。 |

## Retirement order

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

Complete deletion must not be reported until the public Zenn URL is actually absent. The GitHub connector cannot perform Zenn dashboard deletion.

## New portfolio rules

### We optimize for

```text
Reach
+ customer value
+ first-hand originality
+ useful exit
+ trust
```

### We do not optimize for

```text
article count
citation count
tool coverage
framework naming
AI-generated volume
SEO traffic by itself
```

### The crucial distinction

Old framing:

> ある証拠がどの判断までを許可するかを明らかにする。

New framing:

> 読者にとって意味のあるproblemを、書き手固有の観測で新しく見せ、読後の行動を良くする。証拠はその価値を信頼できるものにする。

この順序をREADME / AGENTS / article contractの正準とする。
