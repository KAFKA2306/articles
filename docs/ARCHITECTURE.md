# Architecture

## Responsibility

`KAFKA2306/articles` は記事生成の唯一の正準repoです。

- `graphiti`: private memory / weekly source of ideas
- `articles`: public evidence grounding / story shaping / drafting / dual review / publication
- `Zenn`: published delivery surface

責務を混ぜません。private memoryの保存やGraphiti本体の運用はこのrepoでは行いません。

## State model

生成物は3段階です。

1. `artifacts/candidates/YYYY-MM/*.md`
   - public-safeな未公開候補
   - Graphiti raw textは禁止
2. `artifacts/reports/YYYY-MM/*.json`
   - source gate、technical review、editorial reviewの証跡
3. `articles/*.md`
   - Zenn front matterを持つ公開記事

## Autonomous state machine

```text
DISCOVER
  ↓
FIND_ONE_DISCOVERY
  ↓
SHAPE_QUESTION_AND_HYPOTHESIS
  ↓
GROUND
  ↓
DRAFT
  ↓
VERIFY_SOURCES ─────────fail─────────┐
  ↓ pass                              │
TECHNICAL_REVIEW ────────fail────────┤
  ↓ pass                              │
EDITORIAL_REVIEW ────────fail────────┤
  ↓ pass                              │
          REVISE_BY_CUTTING_WEAKNESS ┘
  ↓
MONTH_END_REVIEW_ALL
  ↓
RANK_STORY_FIRST
  ↓
SELECT
  ↓
PUBLISH
```

公開本数を満たすためにgateを緩めません。

## Discovery contract

記事候補は、実装やデータから次のいずれかを見つけた場合だけstory-readyになります。

- `anomaly`
- `contradiction`
- `failure`
- `unexpected-connection`
- `counterintuitive-result`
- `magnitude`

さらに、次をすべて持つ必要があります。

```text
central_question
surprising_finding
initial_hypothesis
hypothesis_update
stakes
story_type
evidence_urls
why_interesting
```

この形にできない場合は記事生成へ進まず、候補探索へ戻します。

## Editorial runtime

`pipeline/editorial.py` は既存の `core.py` に対してruntime overrideを導入します。
これにより、収集・URL検証・保存など既存の安定した処理を変更せず、次の編集判断だけを差し替えます。

- topic selection
- topic enrichment
- drafting
- technical + editorial evaluation
- pass/fail decision
- revision

`pipeline/cli.py` は `install_robust_model_call()` の後に `install_editorial_pipeline()` を呼びます。
そのため、Graphiti候補とpublic GitHub候補の両方が同じ編集品質ゲートを通ります。

Graphiti側で旧形式のtopic metadataが返った場合も、`draft_article()` の前に `enrich_topic()` がstory-ready形式へ変換します。公開証拠から十分な発見を構成できない場合はfail-closeします。

## Dual review

### Technical axes

```text
logic
utility
readability
originality
clarity
```

`overall` はこの5軸の算術平均です。
これはLAPRAS AI Reviewの実測値ではなく、内部proxyです。

### Editorial axes

```text
interest
discovery
narrative
context
```

`story_overall` はこの4軸の算術平均です。

技術品質が高くても、編集品質の最低値を満たさない候補は公開不可です。
月末の順位付けは次の順です。

```text
story_overall
interest
discovery
overall
minimum editorial axis
minimum technical axis
own GitHub evidence count
valid source count
```

これにより、「正確だが弱い記事」が「少し技術スコアは低いが、発見が明確で読み進めやすい記事」を押しのけることを防ぎます。

## Revision policy

改稿は加筆競争にしません。

- `interest` が弱い → 抽象的な導入を切り、具体的な現象から開始
- `discovery` が弱い → 主役以外の論点を切る
- `narrative` が弱い → 問い→仮説→観測→更新→結論へ再配置
- `context` が弱い → 必要な固有名詞だけ、その場で一文説明
- source gateが弱い → 未確認の断定を削る

改稿で前版より悪化した場合、`selection.py` は評価済み版のうち最良のものを保持します。

## Graphiti boundary

Graphiti adapterは次の順序で処理します。

1. private weeklyをread-only取得
2. `summary / highlights / decisions / next / timeline` をin-memoryで圧縮
3. private内容から技術テーマを発見
4. public GitHub signalsへ再接地
5. KAFKA2306 GitHub evidence 2件以上を返せないテーマを棄却
6. raw private contentを破棄
7. public-safe topic metadataだけcandidateへ残す
8. editorial layerで一つの発見へ再整形

public repoへ残せるGraphiti由来metadataは、抽象化済みtopic、record count、復元不能digest、公開証拠だけです。

## Failure policy

- Graphiti credentialなし: Graphiti候補のみskip
- Graphiti privacy gate fail: Graphiti候補を作らない
- story-ready変換失敗: candidateを作らない
- primary-source不足: publishしない
- HTTP検証失敗: publishしない
- technical review最低値未達: revise、上限到達後はpublishしない
- editorial review最低値未達: revise、上限到達後はpublishしない
- 同月に公開済み: no-op

## Model backend

生成・査読はGitHub Copilot CLIを非対話モードで使用します。Actionsでは組み込み `GITHUB_TOKEN` と `copilot-requests: write` を使います。Copilot CLIへはGraphitiの圧縮contextをstdinで渡し、process argumentやartifactへprivate本文を残しません。`shell / write / read / url / memory` toolは明示denyし、記事生成器からrepository mutationや外部参照を分離します。
