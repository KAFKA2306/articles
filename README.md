# KAFKA2306/articles

[![Article Pipeline CI](https://github.com/KAFKA2306/articles/actions/workflows/article-pipeline-ci.yml/badge.svg)](https://github.com/KAFKA2306/articles/actions/workflows/article-pipeline-ci.yml)
[![Canonical Article Pipeline](https://github.com/KAFKA2306/articles/actions/workflows/article-pipeline.yml/badge.svg)](https://github.com/KAFKA2306/articles/actions/workflows/article-pipeline.yml)
[![Zenn Production Verification](https://github.com/KAFKA2306/articles/actions/workflows/zenn-production-verify.yml/badge.svg)](https://github.com/KAFKA2306/articles/actions/workflows/zenn-production-verify.yml)

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

### まず、読者の判断規則を変える

記事の第一目的は「このリポジトリで何を直したか」ではありません。**強い汎用規律を打ち出し、失敗の仕組みと具体的な証拠で支持し、反例で試すこと**です。

[Crash-Driven Development](https://zenn.dev/kafka2306/articles/11cd731eebded1)の「失敗を正常値で隠すな」のように、読者が次の日から**何か一つをやめ、代わりに別の判断を始める**原則を求めます。語気の強さや新語ではなく、行動を変える力を評価します。

例として、[AIの合格条件](articles/2026-08-15-hook-runner-is-not-policy.md)は「テストが大事」ではなく **「合格の決定権を実装者の自己採点に委ねるな」**、[上位50社の選定](articles/2026-08-14-06-top-n-boundary-evidence.md)は「一覧を正しく」ではなく **「上位N件だけで選定を正当化するな。N+1件目を保存せよ」**、[財務比率](articles/financial-ratio-denominator-check.md)は「数値に注意」ではなく **「比率を使う前に分母と期間を固定せよ」**まで踏み込みます。

そして毎回、元の常識、規律が必要な理由、実際に観測された数値・変更・結果、別の分野への応用条件、規律を撤回すべき反例を示します。**他分野へ移せるのは判断規則。実証済みなのは、観測した範囲だけ。** [編集契約](pipeline/contracts/article.md#編集の第一原理強い汎用原則を実例で証明し反例で試す)

### 具体性の最低ライン

「改善した」「検証した」「運用可能になった」で説明を終えません。読者が同じ対象を開いて判断できるよう、**対象のURL・ファイルやデータ版、入力、実際の操作・計算、前後の結果、失敗例、根拠**を残します。コードがない考察記事でも、実在する比較対象と判断の分岐を示します。未実施の操作は実績と区別します。

例：「決算データの出典が開きやすくなった」ではなく、「[半導体決算一覧](https://kafka2306.github.io/semiconductor-earnings-model/earnings/)のNVIDIA行から、対象期末のSEC提出書類を2クリックから1クリックで開けるようにし、対象11社の直接リンクを0社から11社にした。別の四半期への誤リンクは検査で失敗する」まで書きます。実測条件と[検証記録](articles/kafstyler-agent-quality-loop.md#1タップの改修で出典がずれる条件を試した)を併記します。

執筆・改稿・査読では[超具体性の必須条件](pipeline/contracts/article.md#超具体性の必須条件初稿改稿査読の共通ゲート)を使います。「どこを開く？ 何を入力する？ どう変わる？ 失敗したら？ 根拠は？」の一つが欠けて読者が先へ進めなければ差し戻します。**具体例を増やしただけではなく、読者が自分で使えるか**を合格条件にします。
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
- どんな新しい能力・選択肢を得られるか
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

誰が読み、読後に何を判断できるか、どの実体験や実測が根拠になるかを、執筆前に一文ずつ書きます。必要な項目は[記事候補の必須項目](pipeline/contracts/article.md#required-candidate-fields)で確認できます。

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

## 記事ファイル名と日付

新規記事は `articles/YYYY-MM-DD-NN-topic.md` とする。`YYYY-MM-DD` は作成日の日本時間、`NN` は当日の2桁連番、`topic` は短い英数字の説明。Zennの12〜50文字のslug制約を守る。

全記事のfrontmatterに `created_at: "YYYY-MM-DD"`（作成日）と `updated_at: "YYYY-MM-DD"`（改定日）を明記する。新規作成時は両者を同日とし、本文を改定した日は `updated_at` を更新する。`published_at` はZennの公開日時であり、両者と混同しない。

既存記事の初期値にはGitで確認できる初回記録日・最終変更日（JST）を用いた。原稿の執筆開始日そのものを証明するものではない。既存の非日付slugは参照先や公開URLの互換性を保つため維持し、新規作成には使わない。[編集契約](pipeline/contracts/article.md#記事ファイル名と作成改定日) · [Zennのslug仕様](https://zenn.dev/zenn/articles/what-is-slug)

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

**強い汎用規律を具体的な観測と反例で試し、読者が別の仕事でも判断を変えられる記事です。**