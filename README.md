# KAFKA2306/articles

**広い読者が自分事にできる問題を入口に、実体験・実測・失敗から、読後の判断や行動を一段よくする技術記事を作るrepository。**

このrepoの目的は「正しい技術情報を増やすこと」でも「監査可能な記事を増やすこと」でもありません。

最終的な価値は、読者が

- 時間を無駄にしない
- 同じ失敗を避ける
- 採用・導入・委任・停止を判断できる
- それまで見えていなかった問題に気づく
- 自分の仕事へ持ち帰れる考え方を得る

ことです。

> **Broad door. Original insight. Concrete proof. Useful exit.**

証拠・一次情報・監査は重要ですが、主役ではありません。これらは**読者価値を壊さないためのquality infrastructure**です。

## What we want to publish

強い記事は次の流れを持ちます。

```text
広く認識できるproblem / desire / friction
        ↓
具体的なscene / number / failure / comparison
        ↓
「普通はこう思う」という自然な予想
        ↓
自分たちの実体験・実測・公開artifact
        ↓
予想外だった発見 / 見方の更新
        ↓
読者が自分の仕事で使える判断・行動
```

### 入口は広く、証拠は狭く深く

記事タイトルや冒頭は、技術名を知っている人だけに通じる入口にしません。

```text
狭い入口:
Unity MCPのEDITOR_VALIDATED境界

広い入口:
AIに作らせたものを、誰が「完成」と判定するのか？
```

本文では必要なところまで専門的に掘ります。間口を広げることは内容を薄めることではありません。

### 顧客価値から逆算する

ここでいう「顧客」は、記事を読む人です。候補を作る前に、読者の利益を具体化します。

- 何分・何時間の調査を減らせるか
- どんな失敗や手戻りを避けられるか
- 何を安心して試せるようになるか
- 何をやめる判断ができるか
- どんな新しい能力・選択肢を得るか
- どの不確実性が減るか

`理解できる`、`勉強になる` だけでは弱いと扱います。

## Google / Zennから採用する編集原則

Google Search Centralはpeople-first contentの自己評価として、次を問いかけています。

- 想定読者が直接訪れても有用か
- first-hand expertise / depth of knowledgeがあるか
- 読後に目的達成に十分な情報を得られるか
- 他の検索結果より実質的な価値があるか
- original information / research / analysisがあるか
- タイトルが内容を正確かつ有用に要約しているか

一次情報:

- https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- https://developers.google.com/search/docs/fundamentals/creating-helpful-content?hl=ja

Zennも、生成AIで一般知識を得やすくなった現在、具体的な試行錯誤と書き手固有の視点、実体験に基づく知見を重視しています。

- https://zenn.dev/guideline
- https://info.zenn.dev/2026-02-03-community-guidelines-update
- https://info.zenn.dev/2026-03-10-ai-contents-guideline

このrepoではSEOを目的にこれらを使いません。**「読者にとって本当に読む理由があるか」の編集基準**として使います。

## Article value model

記事候補は次の7点でレビューします。

### 1. Reach — 間口

- intended audienceがタイトルだけで自分事にできるか
- 技術名を知らなくてもproblem / desireを理解できるか
- nicheな題材なら、そのnicheの外へ持ち帰れる意味があるか

### 2. Customer value — 読者の得

- 読後に時間・失敗・リスク・不確実性のどれかが減るか
- 新しい判断・行動・能力が増えるか
- 「知った」で終わらず仕事が変わるか

### 3. Originality — この記事でしか得にくいもの

- 自分たちの実測、失敗、比較、運用、artifactがあるか
- 公式docsや一般的AI要約で代替できないか
- obviousな結論を言い直しているだけではないか

### 4. Experience — 書き手固有の経験

- 実際に使った・作った・壊した・直した・運用した経験があるか
- 成功だけでなく摩擦や予想外が残っているか

### 5. Utility — Useful exit

- checklist / decision rule / design pattern / adoption rule / stop conditionなどへ変換できるか
- 読者が次に何をするか明確か

### 6. Trust — 信頼

- material claimは一次情報または公開証拠へ接地しているか
- observation / inference / speculationを混ぜていないか
- 証拠以上の断定をしていないか
- 未実証範囲を隠していないか

### 7. Portfolio value — 残す意味

- 既存記事とreader jobが重複していないか
- 半年後も読む理由があるか、または再検証コストに見合うか
- この1本が著者の専門性・視点を強めるか、薄めるか

## Article signature

公開候補は最低限次を一文で答えられる必要があります。

- `intended_audience`: 誰のための記事か
- `broad_entry`: 技術名を知らなくても分かる入口は何か
- `reader_job`: 読者は何を達成・判断したいか
- `reader_before`: 今どんな摩擦・損失・不確実性があるか
- `customer_value`: 何が減り、何が増えるか
- `original_observation`: 自分たちしか持っていない観測は何か
- `surprising_finding`: 読む前と後で何が変わるか
- `proof_of_value`: その発見を支える実測・実装・一次情報は何か
- `useful_exit`: 読者が持ち帰る判断・行動は何か
- `non_goal`: 何は証明していないか
- `half_life`: 何をいつ再検証するか
- `portfolio_overlap`: 既存記事で代替できない理由

`authority / verification boundary` は必要な場合だけ使います。**境界を見つけること自体を記事化理由にはしません。**

## What we do not publish

次は、正しくても原則として公開しません。

- 公式docsの要約
- install / setup手順だけ
- リンク集・サービス一覧
- tool名を並べただけの比較
- 「2026年の最強stack」のような根拠の弱いランキング
- repo changelog
- 二次情報を集めただけのAI report
- 実体験・実測のない独自framework
- 「Aを使ってBを作った」で読者価値がない成功談
- intended audienceが不明な記事
- titleが技術用語だけで閉じている記事
- 読後の利益を説明できない記事
- 既存記事の弱い焼き直し
- 根拠のない数値・閾値・成功率
- 読む前から結論が分かる記事

## Portfolio lifecycle

記事数はKPIではありません。

| State | 意味 |
|---|---|
| `KEEP` | Reach / customer value / originality / trustが現在も強い |
| `REVALIDATE` | 核は強いが価格・仕様・市場などvolatile factを再確認する |
| `REWRITE` | 独自価値はあるが入口・顧客価値・構成が弱い |
| `MERGE` | より強い記事へ価値とproofを集約する |
| `RETIRE` | 読む理由が薄い、重複、陳腐化、弱いproof、portfolio dilution |

公開済みだから永久保存、とは扱いません。

現行監査:
[`docs/zenn-portfolio-audit-2026-08-15.md`](docs/zenn-portfolio-audit-2026-08-15.md)

## Evidence is a quality gate, not the product

一次情報と監査は次のために使います。

```text
reader value
  ↓
original claim
  ↓
proof / calibration
  ↓
trust
```

順序を逆にしません。

「この証拠は何を許可するか？」は重要ですが、読者がその判断を必要としていなければ記事になりません。

最低原則:

- material external claimはcurrent primary sourceで確認する
- 自分たちの成果はpublic commit / PR / Issue / Actions / artifactへ接地する
- 数字にはtarget / period / unit / scopeを残す
- observation / inference / speculationを分離する
- 未確認を成功へ昇格しない
- sourceが弱ければclaimを削る

## Title and opening rule

タイトルは検索語ではなく、まず人間の問題を表します。

```text
problem / desire
  +
具体的な異常・数字・失敗・結果
  +
必要なら技術名
```

最低3案:

1. `broad_problem`
2. `concrete_result`
3. `searchable`

冒頭では500文字以内を目安に、

- 誰の何が困っているか
- 何が起きたか
- なぜ続きを読む価値があるか

が分かるようにします。

## Publication is human-controlled

Zennの公開は別side effectです。

```text
scheduled automation
  = discover / research / draft / review / compare

manual selection
  = published:false draftへ昇格

explicit human approval
  = published:true
```

schedule、score、CI green、mergeはpublication authorizationではありません。

## Repository structure

```text
articles/                    # Zenn-compatible sources
artifacts/candidates/        # unpublished candidates
artifacts/reports/           # evidence / review / selection reports
pipeline/                    # generation / review / audit implementation
pipeline/contracts/article.md
AGENTS.md                    # autonomous-agent operating rules
```

## Quick verification

```bash
python -m compileall pipeline demos/python-syntax-gate/syntax_gate.py
python -m unittest discover -s tests -v
node --check demos/_shared/pyodide-worker.mjs
node --check demos/python-syntax-gate/app.mjs
python -m pipeline.audit
```

Candidate generation:

```bash
python -m pipeline.cli candidate
```

Human-triggered selection to an unpublished Zenn draft:

```bash
ARTICLE_MANUAL=1 python -m pipeline.cli publish
```

---

**残したいのは「監査の厳しい記事」ではありません。**

**広く意味のある問題に、書き手固有の観測で新しい見方を与え、読者の次の行動を良くする記事です。**
