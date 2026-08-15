# Article Contract

## Goal

公開するのは、**一次情報と公開実装を追った結果、読者の判断を更新する一つの発見が残った記事だけ**とする。

このrepoは記事数、更新頻度、tool coverage、word countを最適化しない。

正確さは必要条件であって十分条件ではない。良い記事は、読者に新しい知識を渡すだけでなく、

```text
何を信じてよいか
何をまだ信じてはいけないか
どこまで機械へ任せてよいか
何を満たしたら次へ進んでよいか
```

を判断できる状態へ変える。

## Canonical article shape

```text
1. observed scene / failure / number
2. natural initial interpretation
3. current primary evidence + public artifact
4. falsification / boundary
5. hypothesis update
6. portable decision rule
7. non-goal / unproven area
```

技術名、framework名、製品名は入口ではなく、この問いを解くために必要な位置で登場させる。

## Required candidate fields

執筆前に最低限次を定義する。

- `reader_job`: 読者が実際に決めたいこと・進めたいこと。
- `reader_before`: 読む前の摩擦・損失・不確実性・false confidence。
- `observed_anomaly`: 実測された異常、失敗、矛盾、数字、反例。
- `central_question`: 1本で答える問い。
- `initial_hypothesis`: 調査前にもっともらしかった解釈。
- `surprising_finding`: 証拠で更新された発見。
- `hypothesis_update`: 何を見て考えが変わったか。
- `proof_of_value`: この文章固有の公開証拠・実測・失敗・比較。
- `boundary`: 証拠が許可する結論と、許可しない結論。
- `decision_rule`: 別の現場へ持ち帰れる判定規則。
- `reader_after`: 読後に可能になる具体的な判断・行動。
- `desired_reader_action`: 読後に自然に試せる次action。
- `non_goal`: 証明しないこと、未実証範囲。
- `half_life`: 価格・quota・仕様など再検証が必要な事実。
- `portfolio_overlap`: 既存記事で代替できない理由。

既存pipeline互換のため、`design_philosophy` / `why_this_article` / `why_interesting` / `stakes` / `story_type` / `evidence_urls` も保持する。

## Question gate

文章を書く前に、問い自体を査読する。

次の最低1つが必要。

- 読者の自然な予想と観測結果がずれた。
- 一次情報によって当初前提を撤回した。
- 実測値に無視できない桁差・変化量がある。
- 簡単だと思った場所とは別の場所が本当の難所だった。
- successに見えた結果が、別のverification layerでは未完だった。
- 同じ言葉で潰れていた2つ以上のauthority / stateを分離した。
- failureから一般化可能なdecision ruleが更新された。

次は原則不採用。

- 公式docsの要約。
- setup / install手順だけ。
- link集。
- tool比較表だけ。
- 「Aを使ってBを作った」だけ。
- repository changelog。
- generic best practice。
- secondary-source collage。
- 実装・測定・反証のない独自framework。
- magic number / arbitrary thresholdを中心にした記事。
- 読む前から結論が常識的に予想できる記事。

**弱い問いを長文・図・引用・文体で救済しない。topic selectionへ戻す。**

## Authority / boundary gate

material claimごとに次を確認する。

```text
この証拠は何を証明する？
この証拠では何を証明できない？
この結果を根拠に、読者はどのactionまで進めてよい？
```

記事は、通常ひとつ以上の境界を明示する。

- capability != authority
- implementation != validation
- runner != policy / oracle
- build != release != production verification
- test pass != user-visible correctness
- tool success != runtime completion
- detection != independent verification
- current value != provenance
- agent ability != delegated permission
- generated artifact != visually/runtime accepted artifact

境界がない記事は、単なる説明記事になっていないか再検討する。

## Evidence gate

原則として公開時点のprimary / official sourceを使う。

最低source countは `pipeline/config.json` を正準とする。

必須原則:

1. material external claimは実HTTP取得で検証する。
2. vendor仕様はvendor公式、標準はstandards body、製品価格・quotaは現行公式pageを優先する。
3. KAFKA2306固有の成果はpublic commit / PR / Issue / Actions / artifactで検証する。
4. historical stateが重要ならmutable branchよりfixed commit/runを使う。
5. 数字にはtarget / period / unit / scope / comparison basisを付ける。
6. observation / inference / speculationを分離する。
7. sourceが取得不能・矛盾・古い場合はclaimを弱めるか削除する。
8. 未実行をPASS、unknownを0、candidateをproductionへ昇格させない。
9. 別providerの実装を使って未公開vendor内部を推測しない。
10. citation countは品質の代理にならない。

## Reader value gate

`reader_after` は次のようなactionable stateを要求する。

- 採否を決められる
- 止める条件を決められる
- 委任範囲を決められる
- 何を追加検証すべきか決められる
- failure stateを分類できる
- 変更前後を説明できる
- 同じmistakeを別domainで避けられる

`理解できる` / `学べる` だけでは不合格。

`why_this_article` は一般tutorial / docs / AI要約で代替できない、実測・失敗・比較・反証・判断変更の最低1つへ接地する。

`proof_of_value` が空ならpublish不可。

## Portability and durability

一回の特殊事例を記事化する場合、少なくとも一つのportable abstractionを抽出する。

良い抽象化:

```text
GitHub Pagesが無効だった
  -> deploy availabilityとartifact validityを分ける

Unity MCPがsuccessを返した
  -> authoring successとvisual/runtime auditを分ける
```

悪い抽象化:

```text
このrepositoryではこのfileをこのように直した
```

さらに`half_life`を持たせる。

- price / quota / provider lineup: short
- current product behavior / API: medium, version-sensitive
- immutable experiment at fixed commit: long
- stable principle supported by multiple primary sources: long

volatile factが記事の価値の中心なら `REVALIDATE` を前提にする。

## Portfolio novelty / overlap

公開前に既存記事を比較する。

次の場合は新規公開より `MERGE` を優先する。

- 同じreader jobを扱う。
- 同じdecision ruleへ収束する。
- 新記事のproofが既存記事の補強にすぎない。
- 新しいtool名だけが違う。

**記事数を増やすことは価値ではない。proofを集約してsignalを強くする。**

## Title contract

タイトルは技術名より、読者が認識できるproblem / anomalyから始める。

候補は最低3案作る。

1. `general_problem`
2. `concrete_anomaly`
3. `searchable`

選択titleはこの候補内から選ぶ。

原則:

```text
plain-language problem
  -> concrete proofable anomaly
  -> technical search term only when useful
```

`MCP`, `Pyrefly`, `Pydantic`, `Zod`, `GitHub Actions` 等を知らないと意味が分からないtitleは、技術名を知らない読者が問題を認識できる入口へ戻す。

本文で証明できない数字・強い断定をtitleへ置かない。

## Story contract

本文は説明順ではなく発見順を優先する。

```text
scene
  -> unresolved question
  -> initial hypothesis
  -> evidence / experiment
  -> failure or contradiction
  -> updated model
  -> decision rule
```

記事冒頭で結論を全部説明して発見を消さない。ただし、意図的に情報を隠してsuspenseを作らない。

中心の問いを前進させない節は削る。

## Technical quality floor

LAPRAS AI Reviewで公開されている5軸を参考にした**内部proxy**を使用する。LAPRAS上の実測値ではない。

- `logic`
- `utility`
- `readability`
- `originality`
- `clarity`

`overall` は5軸の算術平均。

現行minimum/targetは `pipeline/config.json` を正準とする。

このscoreは品質床であり、公開価値の目的関数ではない。

## Editorial quality floor

既存pipeline互換の4軸を維持する。

- `interest`
- `discovery`
- `narrative`
- `context`

`story_overall` は4軸の算術平均。

さらにblocking reviewでは最低限次を確認する。

- `weak_reader_value`
- `weak_differentiation`
- `missing_proof_of_value`
- `forced_commercial_cta`
- `technical_value_as_product`
- `premature_conclusion_in_opening`
- `narrow_technical_title_entry`
- `uncalibrated_claim`
- `missing_decision_rule`
- `portfolio_redundancy`

既存実装がまだ新blocking codeを機械判定しない場合も、人間/agent auditではblockingとして扱う。

## Images

画像はsupporting evidence / explanationでありquotaではない。

追加するのは、次のどれかを満たす場合だけ。

- causal / state flowを短くする
- measured comparisonを理解しやすくする
- boundaryを可視化する
- actual artifactを示す

生成画像に存在しないCI結果、数字、URL、screenshot-like evidenceを描かせない。

articleは画像なしでも成立させる。

## Publication boundary

Zenn公式方針:

- https://info.zenn.dev/2026-03-10-ai-contents-guideline
- https://zenn.dev/guideline

このrepoではautomationとpublicationを分離する。

```text
schedule
  -> candidate discovery / drafting / review only

manual pipeline selection
  -> selected candidateをarticles/へ published:false でmaterialize

explicit human approval
  -> published:true
```

schedule、月末、score、CI green、mergeはpublication authorizationではない。

内部function/CLI名が`publish`でも、`published:false`を作るだけならpublic publicationとは呼ばない。

## Lifecycle after publication

公開後も次のstateを持つ。

- `KEEP`
- `REVALIDATE`
- `REWRITE`
- `MERGE`
- `RETIRE`

`RETIRE` 判定:

- central claimが現在検証できない
- evidenceより強い結論を誘発する
- title/body promise mismatch
- newer articleにreader jobを完全に上位互換された
- generic summary / link list / setup guideでunique proofがない
- unsupported magic numberが主張の中核
- maintenance costがdurable valueを上回る
- portfolio signatureを薄める

Zenn上の削除はZenn公式GitHub連携手順に従い、repo-managed articleではdashboardとrepoの両方を扱う。

- https://zenn.dev/zenn/articles/connect-to-github

agentがdashboard操作できない場合は、public deletionを完了したと報告してはいけない。

## Publication portfolio review cadence

候補生成とは別に、公開記事を定期的に再監査する。

最低確認項目:

1. public URLが存在する。
2. titleとbodyの約束が一致する。
3. material sourceが現在もclaimを支持する。
4. volatile factsを再検証した。
5. newer articleとのoverlapを確認した。
6. decision ruleが今も再利用可能。
7. overclaim / hindsight rewriteがない。
8. lifecycle stateを更新した。

公開記事数を増やすより、弱い記事をretireしてportfolio signalを強くすることを優先する。

## Final publication test

公開を承認する前に、次を一文ずつ答えられること。

```text
Reader job:
Observed anomaly:
Initial hypothesis:
Strongest public evidence:
What that evidence proves:
What it does NOT prove:
Hypothesis update:
Decision rule:
Non-goal:
Why this deserves a separate article:
Half-life / revalidation trigger:
```

一つでも曖昧なら `published:false` を維持する。
