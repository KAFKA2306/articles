# KAFKA2306/articles

**証拠から「なぜこうなった？」を見つけ、読者が追体験できる一つの発見へ変える技術記事repository。**

一般知識をAIで量産するためのrepoではありません。
公開GitHub活動とprivacy-safeなprivate seedから問いを見つけ、一次情報へ再接地し、仮説更新・reader value・proofまで揃った記事だけを公開候補にします。

> **Discover one surprising fact. Prove it. Turn it into something the reader can use.**

## Vision

記事を読んだ人が得るのは、技術名の知識ではなく、**「自分なら次にどう判断・実装・運用するか」を決められる状態**です。

このrepoでは、1本の記事を次の変化として設計します。

```text
読む前
  └─ 何が起きているか分からない / 失敗理由が曖昧 / どこまで信じてよいか分からない
        ↓
具体的なscene・数字・失敗
        ↓
自然な予想
        ↓
公開証拠で検証
        ↓
仮説更新
        ↓
読む後
  └─ 判断できる / 試せる / 止められる / 説明できる / 運用へ持ち込める
```

「正しく説明した」で終わらず、reader before → after を本文で成立させます。

## Design philosophy

### 1. 技術名より現象を先にする

`MCP`、`Provenance`、`Pyodide`、`GitHub Actions` から記事を始めません。

先に、

- 61件目だけが消えた
- 856件が7,699件になった
- CIが自分でmanifestを直してからgreenになった
- AI生成図に実行していない `CI SUCCESS` が描かれた

のような、読者が意味を理解できる現象を置きます。

技術は、その謎を解くために必要になった位置でだけ登場させます。

### 2. 一記事一発見

候補は次のいずれかへ収束させます。

- anomaly
- contradiction
- failure
- unexpected connection
- counterintuitive result
- magnitude

複数の正しい論点を詰め込むより、中心の問いを前進させない節を削ります。

### 3. private contextはidea seed、public evidenceはclaim source

private Graphiti weeklyは、題材候補を見つけるためのread-only seedです。

```text
private seed
   ↓ idea only
public GitHub / official primary source
   ↓ re-ground
public claim
```

private diary本文、個人情報、税務、資産、健康、旅行、私生活、勤務先内部情報、未公開情報をpublic evidenceへ昇格させません。

### 4. 「動いた」を完成にしない

必要に応じて、

```text
tool success
runtime compatibility
validation
allowed use
production / public verification
```

を別stateとして扱います。

未実証範囲を明示できない記事は、強い営業資産にはなりません。

### 5. 弱い記事を長文化して救わない

問い・reader value・proofが弱ければ、文章を足して合格にしません。

- rewrite
- merge
- keep private
- archive / delete

を正規のlifecycleとして扱います。

**記事数はKPIではありません。**

## Why / 差別化

このrepoの差別化は、LLM、Graphiti、Copilot CLI、Pyodide、GitHub Actionsそのものではありません。

一般的なAI記事生成と違い、公開前に次を要求します。

1. **何が意外だったか** — `central_question` / `surprising_finding`
2. **何を最初に予想したか** — `initial_hypothesis`
3. **何を見て考えが変わったか** — `hypothesis_update`
4. **読者の何が変わるか** — `reader_before` / `reader_after`
5. **なぜこの記事なのか** — `why_this_article`
6. **本当に使える根拠は何か** — `proof_of_value`
7. **何を証明しないか** — `non_goal`
8. **読者が次に何を試せるか** — `desired_reader_action`

これらを公開証拠から作れない候補は記事化しません。

営業価値もCTAでは作りません。
「お問い合わせください」を足す代わりに、本文から自然に使えるchecklist、template、decision table、最小導入手順へ変換します。

正準contract:
[`pipeline/contracts/article.md`](pipeline/contracts/article.md)

編集設計:
[`docs/EDITORIAL_DESIGN.md`](docs/EDITORIAL_DESIGN.md)

現行portfolio監査:
[`docs/article-portfolio-audit-2026-08-14.md`](docs/article-portfolio-audit-2026-08-14.md)

## Discovery journey

```text
Graphiti weekly (private, optional) ─┐
                                    ├─> candidate discovery
Public GitHub evidence ─────────────┘
        ↓
find one anomaly / contradiction / failure /
unexpected connection / counterintuitive result / magnitude
        ↓
central question + initial hypothesis
        ↓
reader before / after + differentiation + proof
        ↓
draft as discovery story
        ↓
source gate
        ↓
technical review + editorial review + reader-value blocking gate
        ↓
revision by cutting weak sections
        ↓
best-of-month selection by story quality first
        ↓
articles/*.md
```

候補生成時点で価値を定義するため、「書き終わってから営業っぽい一文を足す」という順序にはしません。

## Evidence / privacy boundary

### Public claimに使えるもの

- KAFKA2306 public GitHub code / commit / PR / issue / artifact
- vendor / standards body / official documentation
- 公開データの一次資料
- 本文で再現できるfixture・test・measurement

### Idea seedに留めるもの

- private Graphiti weekly
- private diary
- 個人情報を含むconversation
- 未公開業務情報
- private financial / health / travel context

private seedで気づいたテーマでも、公開記事のclaimはpublic evidenceへ再接地します。

### Evidence gate

最低条件:

- primary-source URLs: 3件以上
- KAFKA2306 GitHub evidence: 2件以上
- external official primary source: 1件以上
- URLは実HTTP取得で検証
- 未確認を0件・成功・completeへ変換しない

## Editorial contract

### Story fields

- `central_question`
- `surprising_finding`
- `initial_hypothesis`
- `hypothesis_update`
- `stakes`
- `story_type`
- `evidence_urls`
- `why_interesting`

### Reader-value fields

- `reader_before`
- `reader_after`
- `design_philosophy`
- `why_this_article`
- `proof_of_value`
- `desired_reader_action`
- `non_goal`

次はcandidate段階で不合格です。

- `reader_after` が「理解する」「学ぶ」だけ
- `why_this_article` が「詳しく説明する」「分かりやすく解説する」だけ
- `proof_of_value` が空
- 技術名・repository名・CI追加を価値そのものにしている

本文査読では次をblocking issueとして扱います。

- `weak_reader_value`
- `weak_differentiation`
- `missing_proof_of_value`
- `forced_commercial_cta`
- `technical_value_as_product`
- `premature_conclusion_in_opening`
- `narrow_technical_title_entry`

technical / story scoreが高くても、blocking issueが残れば公開できません。

## Quality gate

### Technical floor

| Axis | Minimum |
|---|---:|
| overall | 3.8 |
| logic | 3.5 |
| utility | 3.5 |
| readability | 3.5 |
| originality | 3.5 |
| clarity | 3.5 |

Target overall: **4.1**

### Editorial floor

| Axis | Minimum |
|---|---:|
| story overall | 4.0 |
| interest | 4.1 |
| discovery | 3.8 |
| narrative | 3.8 |
| context | 3.8 |

Target story overall: **4.3**

月末比較では、technical scoreより先に、

```text
story_overall
→ interest
→ discovery
→ technical overall
```

を見ます。

「他のエンジニアに役立つ」は品質床であり、「読みたい」の代用にはしません。

## Candidate → review → publish

### Weekly candidate

**毎週月曜 09:00 JST** にcandidate modeを起動します。

現行workflow:
[`.github/workflows/article-pipeline.yml`](.github/workflows/article-pipeline.yml)

処理:

1. private Graphiti weeklyをread-onlyで取得できる場合だけ読む
2. public GitHub evidenceを探索
3. story + reader-value contractを満たす候補だけ残す
4. source gateを実行
5. technical / editorial / reader-value review
6. 不合格なら最大3回、論点を増やさず改稿
7. `artifacts/candidates/YYYY-MM/` と `artifacts/reports/YYYY-MM/` に保存

### Month-end selection

**実月末 23:30 JST** のwindowでpublish modeを起動します。
`28–31日`にscheduleし、実際の月末かどうかは`pipeline.selection.is_month_end()`でfail-close判定します。

1. 当月候補を全件再検証
2. 査読を3回独立実行し中央値で判定
3. source / technical / editorial / reader-value gateを全通過した集合だけ残す
4. 最高品質1本だけ選ぶ
5. 合格0本なら公開0本

月1本は上限でありノルマではありません。

## Zenn publication boundary

`articles/*.md` は **Zenn-compatibleな正準article source** です。
`published: false` のdraftもここに存在します。

候補・査読証跡は `artifacts/` に隔離します。

Zenn公式では、GitHub連携時のarticle slugは `articles/[slug].md` のファイル名で決まり、slugは半角英小文字・数字・ハイフン・アンダースコアの **12〜50文字**です。一度Zenn上で作成したslugは変更できないため、公開済みarticleを管理目的だけでrenameしません。

一次仕様:

- https://zenn.dev/zenn/articles/what-is-slug
- https://zenn.dev/zenn/articles/markdown-guide

### Filename policy

新規公開article:

```text
YYYY-MM-DD-NN-title.md
```

例:

```text
2026-08-13-01-codex-chatgpt-github-issue-bridge.md
```

- `YYYY-MM-DD`: 公開処理を行うJST日付
- `NN`: 同日内 `01`, `02`, ...
- `title`: 短いASCII kebab-case
- config上のtitle部分最大: 36文字
- 既存公開slugはrenameしない

## Interactive examples are optional

Zenn本文が成立するためにinteractive demoを必須にしません。

Zenn公式Markdown guideはリンクカードや対応済み外部サービスのembedを定義していますが、このrepoは**任意custom JavaScript / 独自Web Workerを記事本文へ注入できることを前提にしません**。

Pyodide等を使う場合も別の静的Web成果物として扱い、次を要求します。

- static本文だけで主張・再現方法が完結する
- Python sourceをJavaScriptへ再実装しない
- runtime / packageは実行操作までlazy load
- demoごとのpackageを明示
- 公開URLのE2E前に「実行できる」と記事へ書かない

つまりinteractive demoは、**理解を明確に改善し、全体complexityを下げる場合だけのprogressive enhancement**です。

関連Issue: #31

## Repository structure

```text
.github/workflows/
  article-pipeline.yml       # weekly candidate / month-end selection
  article-pipeline-ci.yml    # compile + tests + repository/privacy audit
  branch-hygiene.yml         # merged/redundant work branch cleanup

pipeline/
  cli.py                     # candidate / publish entry point
  core.py                    # collection, source verification, persistence
  editorial.py               # story/value shaping, drafting, review, revision
  filenames.py               # Zenn-compatible publication filename contract
  runtime.py                 # Copilot CLI fail-close response adapter
  graphiti.py                # private weekly → in-memory seed
  selection.py               # candidate maturation + month-end selection
  audit.py                   # repository/privacy/editorial audit
  config.json                # quality / value / path contract
  contracts/article.md       # canonical article contract

artifacts/
  candidates/YYYY-MM/        # unpublished public-safe candidates
  reports/YYYY-MM/           # source + review evidence
  archive/                   # retired reusable notes, not article candidates

articles/                    # Zenn-compatible canonical article sources

docs/
  ARCHITECTURE.md
  EDITORIAL_DESIGN.md
  article-portfolio-audit-2026-08-14.md

tests/
```

## Quick verification

```bash
python -m compileall pipeline
python -m unittest discover -s tests -v
python -m pipeline.audit
```

Candidate generation:

```bash
python -m pipeline.cli candidate
```

Month-end selection:

```bash
python -m pipeline.cli publish
```

## Automation / runtime

GitHub Actionsの生成backendは **GitHub Copilot CLI** です。

- `copilot-requests: write`
- built-in `GITHUB_TOKEN`
- CLIのread/write/shell/url/memory toolsは許可せず、text generation boundaryとして使う
- `runtime.py` はJSON contractをfail-closeで正規化
- private Graphiti readは別のread-only `GRAPHITI_READ_TOKEN`
- token未設定時はGraphiti入力だけskip

モデルやtoolが価値なのではなく、**同じeditorial contractを再現可能に実行するためのruntime**として扱います。

## Branch lifecycle

`main` だけを長寿命branchにします。

- content pipelineの正準outputは`main`
- pipeline / CI / contractのレビュー価値がある変更だけ短命branch + PR
- merged branchはcleanup対象
- open PRなし・unique patchなしのbranchは`branch-hygiene.yml`で整理
- unique patchがあるbranchは自動で捨てない

branch数を進捗指標にしません。

## Issue workflow

Issueは「記事を増やす依頼」ではなく、editorial contractとして扱います。

最低限、

```text
reader problem
→ value
→ proof
→ differentiation
→ lifecycle decision / acceptance criteria
```

を持たせます。

記事化できない場合も、`KEEP_PRIVATE / MERGE / DELETE-ARCHIVE` を正常な完了として扱います。

## Editorial references

- Zenn community guideline update 2026-02-03  
  https://info.zenn.dev/2026-02-03-community-guidelines-update
- Zenn guideline  
  https://zenn.dev/guideline
- Zenn AI content policy 2026-03-10  
  https://info.zenn.dev/2026-03-10-ai-contents-guideline
- Zenn Publication 2026/Q2  
  https://info.zenn.dev/2026-07-02-publication-quarterly-award-2026q2
- Zennfes Spring 2026 results  
  https://info.zenn.dev/2026-07-24-zennfes-spring-2026-result

---

**このrepoで最終的に残したいのは、記事数ではありません。**

読者が「なぜそうなった？」を追い、公開証拠で確かめ、最後に自分の仕事へ持ち帰れる一つの発見です。
