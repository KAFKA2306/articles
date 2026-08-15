# Article Contract

## Goal

公開するのは、**広い読者が自分事にできる問題を入口に、書き手固有の実体験・実測・失敗から、読後の判断や行動を一段よくする一つの発見が残った記事だけ**とする。

このrepoは記事数、更新頻度、tool coverage、word count、SEO trafficを最適化しない。

正確さ・一次情報・監査可能性は必要条件だが、記事そのものの価値ではない。

Canonical shorthand:

```text
Broad door
  -> Original insight
  -> Concrete proof
  -> Useful exit
```

## People-first editorial principles

Google Search Centralのpeople-first content自己評価から、次を採用する。

- intended audienceが直接訪れても有用か
- first-hand expertise / depth of knowledgeが見えるか
- original information / research / analysisがあるか
- 他の検索結果より実質的な価値があるか
- 読後に目的達成に十分な情報を得られるか
- titleが内容を正確かつ有用に要約しているか

Primary:

- https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- https://developers.google.com/search/docs/fundamentals/creating-helpful-content?hl=ja

Zennの現行ガイドラインから、次を採用する。

- 具体的な試行錯誤
- 書き手ならではの視点
- 実体験に基づく知見
- 読者が理解しやすい構成
- 内容に合うtitle
- 未検証AI contentの乱造を避ける

Primary:

- https://zenn.dev/guideline
- https://info.zenn.dev/2026-02-03-community-guidelines-update
- https://info.zenn.dev/2026-03-10-ai-contents-guideline

これらはSEO攻略ではなく、**読者価値の自己監査**として使う。

## Canonical article shape

```text
1. broadly recognizable problem / desire / friction
2. concrete scene / number / failure / comparison
3. natural expectation
4. first-hand experience / measurement / public artifact
5. non-obvious finding / reframing
6. practical consequence
7. useful exit
8. proof limits / non-goal
```

技術名・framework名・製品名は、読者がproblemを理解した後に必要な位置で登場させる。

## Required candidate fields

執筆前に最低限次を定義する。

### Reach

- `intended_audience`: 誰が読むと得をするか。
- `broad_entry`: 技術名を知らなくても分かるproblem / desire。
- `stakes`: time / money / risk / effort / quality / capabilityの何が効くか。

### Customer value

- `reader_job`: 読者が達成・判断したいこと。
- `reader_before`: 読む前の摩擦・損失・不確実性・false confidence。
- `customer_value`: 何が安く、速く、安全に、明確に、新しく可能になるか。
- `reader_after`: 読後に可能になる具体的な判断・行動。
- `useful_exit`: checklist / decision rule / design pattern / stop condition / adoption rule / reproducible next step。

### Originality / experience

- `original_observation`: 実測・失敗・比較・運用・実装・artifactなど書き手固有の観測。
- `initial_hypothesis`: 調査前の自然な予想。
- `surprising_finding`: 一般docs / generic AI summaryでは得にくい発見。
- `hypothesis_update`: 実際の観測で何が変わったか。
- `why_this_article`: 単独記事にする理由。

### Proof / trust

- `proof_of_value`: public evidence / measurement / implementation / primary source。
- `claim_boundary`: 証拠がsupportする結論とsupportしない結論。
- `non_goal`: 証明しないこと。
- `half_life`: volatile factと再検証trigger。

### Portfolio

- `portfolio_overlap`: 既存記事で代替できない理由。
- `durable_value`: immediate product/news momentを越えて読む理由。

既存pipeline互換のため、`central_question` / `design_philosophy` / `why_interesting` / `story_type` / `evidence_urls` も保持してよい。

## Reach gate

「間口が広い」は万人向けという意味ではない。

合格条件:

- intended audienceがtitleだけでproblemを認識できる
- niche technologyを知らなくても、なぜ読む価値があるか分かる
- niche記事でも、そのaudienceにとってjob / stakesが明確

例:

```text
弱い:
Unity MCPのEDITOR_VALIDATED境界

強い:
AIに作らせたものを、誰が「完成」と判定するのか？
```

本文は専門的でよい。**入口だけを実装詳細で閉じない。**

## Customer-value gate

`reader_after` が `理解できる` / `学べる` / `知識が増える` だけなら不合格。

最低1つ必要:

- 調査時間を減らせる
- 手戻り・failureを避けられる
- risk / uncertaintyを減らせる
- 採用・導入・委任・停止を判断できる
- 再現できる
- 新しいcapabilityを使える
- 何をしないか決められる

記事のproofが強くても、customer valueを説明できなければpublishしない。

## Originality / experience gate

最低1つ必要:

- 自分で使った結果
- 自分で作ったartifact
- 自分で測った数字
- 自分で遭遇したfailure
- 自分で比較した条件
- 自分で長期運用して見えた変化
- 一次情報で当初前提を撤回した記録

公式docsの要約、二次情報の編集、AI要約だけでは通さない。

`why_this_article` は「分かりやすく説明する」では不合格。

## Question / discovery gate

次の最低1つが必要。

- 読者の自然な予想と観測結果がずれた
- 一次情報によって当初前提を撤回した
- 実測値に意味のある差がある
- 簡単だと思った場所とは別の場所が難所だった
- successに見えた結果に別のfailureが残った
- 一見無関係な事象が実測可能な構造でつながった
- failureからreaderの行動が変わる知見を得た
- product / toolの使い方より「何のために使うか」が変わった

弱い問いを長文・図・引用・文体で救済しない。

## Useful-exit gate

記事の最後に最低1つ、読者が自分の仕事へ持ち帰れるものを作る。

- decision rule
- checklist
- design principle
- experiment protocol
- adoption / rejection rule
- stop condition
- reproducible minimal procedure
- comparison lens
- mental model

CTAはuseful exitではない。

## Evidence / trust gate

Evidence is quality infrastructure, not the product.

material claimごとに次を確認する。

```text
What does this prove?
What does it NOT prove?
Why does the reader need this proof?
```

必須原則:

1. changeable external claimはcurrent primary / official sourceで確認する。
2. vendor仕様はvendor公式、標準はstandards bodyを優先する。
3. KAFKA2306固有の成果はpublic commit / PR / Issue / Actions / artifactで確認する。
4. historical stateが重要ならfixed commit/runを使う。
5. 数字にはtarget / period / unit / scope / comparison basisを付ける。
6. observation / inference / speculationを分離する。
7. inaccessible / contradictory / stale sourceならclaimを弱めるか削除する。
8. NOT_RUN / unknown / pendingをPASS / 0 / completeへ昇格しない。
9. citation countは品質の目的関数にしない。

`authority / verification boundary` は読者価値を生む場合だけ本文の中心に置く。

## Portfolio novelty / overlap

新規記事より `MERGE` を優先する条件:

- 同じreader job
- 同じuseful exit
- 新しいproofが既存記事の補強にすぎない
- tool名だけ違う
- 新記事のReach / customer value / originalityが既存記事以下

**記事数を増やすより、1本の価値密度を上げる。**

## Title contract

最低3案を作る。

1. `broad_problem`
2. `concrete_result`
3. `searchable`

原則:

```text
human problem / desire
  -> concrete proofable result / failure / anomaly
  -> technical search term when useful
```

タイトルは内容を正確に表す。誇張clickbaitは禁止。

冒頭500文字を目安に、

- 誰のproblemか
- 何が起きたか
- なぜ続きを読む価値があるか

が分かること。

## Story contract

説明順より発見順を優先する。

```text
friction / desire
  -> scene
  -> expectation
  -> experiment / experience
  -> contradiction / discovery
  -> updated model
  -> useful exit
```

結論を隠して人工的なsuspenseを作らない。一方、冒頭で全部説明して発見を消さない。

## Technical quality floor

LAPRAS AI Reviewで公開されている5軸を参考にした内部proxyを使用する。LAPRAS上の実測値ではない。

- `logic`
- `utility`
- `readability`
- `originality`
- `clarity`

`overall` は5軸の算術平均。

現行minimum/targetは `pipeline/config.json` を正準とする。

このscoreは品質床であり、公開価値の目的関数ではない。

## Editorial blocking issues

最低限次をblockingとして扱う。

- `unclear_intended_audience`
- `narrow_technical_title_entry`
- `weak_customer_value`
- `weak_reader_value`
- `commodity_information`
- `weak_first_hand_experience`
- `weak_differentiation`
- `missing_proof_of_value`
- `missing_useful_exit`
- `forced_commercial_cta`
- `technical_value_as_product`
- `premature_conclusion_in_opening`
- `uncalibrated_claim`
- `portfolio_redundancy`

既存実装が全codeを機械判定しなくても、人間/agent auditではblockingとして扱う。

## What we do not publish

- official docs summary
- install/setup only
- link collection
- tool/service directory
- generic best-practice article
- product roundup without reader decision
- unsupported "best stack" ranking
- repository changelog
- secondary-source AI report
- framework without first-hand implementation/measurement
- article whose intended audience is unclear
- technology-first title hiding the actual problem
- `Aを使ってBを作った` with no customer value
- obvious conclusion
- unsupported numeric guidance
- duplicate reader job with weaker proof

## Images

画像はreader comprehension / comparison / proofを改善する場合だけ使う。

- generated illustrationをscreenshot / measurement / historical evidenceとして扱わない
- articleは画像なしでも成立
- visual claimは元artifactへ接地
- decoration quotaは禁止

## Publication boundary

```text
schedule
  -> candidate discovery / research / drafting / review only

manual pipeline selection
  -> articles/へ published:false でmaterialize

explicit human approval
  -> published:true
```

schedule、月末、score、CI green、mergeはpublication authorizationではない。

## Lifecycle after publication

- `KEEP`: Reach / customer value / originality / experience / utility / trustが強い
- `REVALIDATE`: insightは強いがvolatile factあり
- `REWRITE`: core experienceは価値があるが入口・価値・構成が弱い
- `MERGE`: same reader jobをより強い記事へ集約
- `RETIRE`: 読む理由・独自性・信頼・durable valueが不足

`RETIRE` / `REWRITE` trigger:

- intended audienceが不明
- titleがimplementation-first
- commodity information化した
- first-hand proofが薄い
- useful exitがない
- central claimがstale / unverifiable
- newer articleに上位互換された
- title/body promise mismatch
- unsupported numberが中心
- maintenance cost > durable reader value
- portfolio signalを薄める

## Publication portfolio review cadence

公開記事を定期再監査する。

1. public URL
2. Reach
3. customer value
4. originality / first-hand experience
5. useful exit
6. source / trust
7. overlap
8. half-life
9. lifecycle state

公開記事数を増やすより、弱い記事をretireしてportfolio valueを上げる。

## Final publication test

公開承認前に一文ずつ答える。

```text
Intended audience:
Broad entry:
Reader job:
Reader before:
Customer value:
Original observation:
Natural expectation:
Surprising finding:
Strongest proof:
Useful exit:
What the proof does NOT establish:
Why this deserves a separate article:
Half-life / revalidation trigger:
```

一つでも曖昧なら `published:false` を維持する。
