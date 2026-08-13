# KAFKA2306/articles

技術記事の**発見・生成・検証・編集査読・選抜・公開を行う正準repository**です。

このrepoの目的は、一般知識をまとめた記事を量産することではありません。
公開GitHub活動とprivacy-safeなGraphiti seedから、**一つの検証可能で意外な発見**を見つけ、その発見を追う記事だけを公開します。

## Canonical loop

```text
Graphiti weekly (private) ─┐
                          ├─> evidence-backed idea discovery
Public GitHub evidence ───┘
        ↓
find one anomaly / contradiction / failure /
unexpected connection / counterintuitive result / magnitude
        ↓
central question + initial hypothesis
        ↓
draft as discovery story
        ↓
source gate
        ↓
technical review + editorial review
        ↓
revision by cutting weak sections
        ↓
best-of-month selection by story quality first
        ↓
articles/*.md
```

Graphitiは**アイデア源のみ**です。private diary本文、個人情報、税務、資産、健康、旅行、私生活、勤務先内部情報、未公開情報をpublic repoへ保存しません。

## Editorial principle

記事は技術名から始めません。
タイトルと導入では、実装やデータから見つかった具体的な現象を主役にします。

候補ごとに以下を必須化しています。

- `central_question`
- `surprising_finding`
- `initial_hypothesis`
- `hypothesis_update`
- `stakes`
- `story_type`
- `evidence_urls`
- `why_interesting`

これらを公開証拠から作れない候補は記事化しません。
単なる生成ミス、URL間違い、設定漏れだけで終わる題材も、そこから別の検証可能な発見へ進めない限り棄却します。

設計根拠とZennの観察結果は [`docs/EDITORIAL_DESIGN.md`](docs/EDITORIAL_DESIGN.md) に固定しています。

## Interactive examples

`articles/*.md` は Zenn-compatible な公開物です。記事本文へ任意の JavaScript / Web Worker を注入できることを前提にしません。

Pyodide 等の interactive demo は、次の条件をすべて満たす場合だけ別の静的Web成果物として採用します。

- 入力を変えて再計算することが、静的なコード例より明確に理解を改善する
- Python source を JavaScript へ再実装しない
- 共通 runtime / worker を1実装だけ共有する
- runtime と追加 package は読者が実行を選ぶまで読み込まない
- package は demo ごとに明示し、共通 bundle を肥大化させない
- demo が停止・未配信でも記事本文だけで主張・失敗例・改善例・再現方法を理解できる
- 公開URLを実際に取得して E2E を確認できるまで、記事から「実行できる」とは書かない

Zenn 側で任意の custom interactive embed が公式にサポートされていると確認できない限り、記事への独自 component 埋め込みは行いません。対応済み外部サービスの埋め込み記法と、通常のリンクカードを区別します。

したがって Pyodide は標準機能ではなく、**有用性が上がり、かつ全体の複雑性を下げられる場合だけ採用する optional progressive enhancement** です。

一次仕様:

- https://zenn.dev/zenn/articles/markdown-guide
- https://pyodide.org/en/stable/usage/webworker.html
- https://pyodide.org/en/stable/usage/packages-in-pyodide.html
- https://pyodide.org/en/stable/usage/wasm-constraints.html

## Directory contract

```text
.github/workflows/
  article-pipeline.yml       # weekly candidate / monthly publish
  article-pipeline-ci.yml    # compile + tests + repository audit
  branch-hygiene.yml         # merged/redundant work branch cleanup

pipeline/
  cli.py                     # candidate / publish entry point
  core.py                    # collection, source verification, persistence
  editorial.py               # story shaping, drafting, dual review, revision
  runtime.py                 # Copilot CLI response normalization / fail-close JSON adapter
  graphiti.py                # private weekly → readable in-memory context → public-safe topic
  selection.py               # candidate maturation + story-first month-end selection
  audit.py                   # fail-close repository/privacy/editorial audit
  config.json                # quality and path contract
  contracts/article.md       # writing/review contract
docs/
  ARCHITECTURE.md
  EDITORIAL_DESIGN.md
  GRAPHITI_WEEKLY.md

artifacts/
  candidates/YYYY-MM/        # unpublished, public-safe candidates only
  reports/YYYY-MM/           # source + technical + editorial review evidence

articles/                    # Zenn-compatible published articles only
tests/
```

`articles/` だけが公開記事の正準出力です。候補と査読証跡は `artifacts/` に隔離し、実装コードは `pipeline/` に集約します。

## Branch lifecycle

**`main` だけを長寿命branchとします。branchを履歴・成果物・記事置き場として残しません。**

- canonical article pipeline の生成物は `main` に直接commitする
- 通常の記事追加・画像追加も、独立したレビューが不要なら `main` に直接commitする
- pipeline / CI / contract の変更などレビュー価値がある変更だけ短命branch + PRを使う
- same-repository PRをmergeしたらhead branchを即時削除する
- open PRがなく、`main` に対するunique patchもないbranchは `branch-hygiene.yml` が削除する
- unique patchが残るbranchは自動削除せず、PR化・`main`への取り込み・明示的な破棄のいずれかを行う

branch数を進捗指標にしません。正準状態は常に `main` と、その時点で本当にレビュー中のopen PRだけです。

## Automation

毎週月曜 09:00 JST:
- Graphiti weeklyをread-onlyで読む（`GRAPHITI_READ_TOKEN` がある場合のみ）
- weeklyを読みやすい作業用contextへ圧縮
- private内容を根拠にせず、公開GitHub evidenceへ再接地
- public GitHub候補を含め複数候補を探索
- 一つの問い・発見・仮説更新へ絞れないテーマを棄却
- source gateと2系統の査読を実行
- 不合格なら最大3回、論点を増やさず改稿

毎月の実月末 23:30 JST:
- 当月候補を全件、同一条件で再評価
- source gateを再実行
- 技術5軸 + 編集4軸を3回独立査読して中央値で判定
- `story_overall` → `interest` → `discovery` → technical `overall` の順で比較
- 合格した最高品質1本だけを `articles/` へ公開（合格0本なら公開0本）

## Quality gate

### Technical

- target overall: 4.1
- minimum overall: 3.8
- minimum each technical axis: 3.5

対象軸:
- logic
- utility
- readability
- originality
- clarity

### Editorial

- target story overall: 4.3
- minimum story overall: 4.0
- minimum each editorial axis: 3.8
- minimum interest: 4.1

対象軸:
- interest
- discovery
- narrative
- context

技術品質だけが高い記事は公開できません。
編集品質だけが高く、証拠が弱い記事も公開できません。

### Evidence

- primary-source URLs: 3件以上
- KAFKA2306 GitHub evidence: 2件以上
- external official primary source: 1件以上
- URLは実HTTP取得で検証
- gate失敗時は公開しない

## Editorial references

生成契約の設計はZenn公式の現行方針と公開事例を参照しています。

- https://info.zenn.dev/2026-02-03-community-guidelines-update
- https://zenn.dev/guideline
- https://info.zenn.dev/2026-07-02-publication-quarterly-award-2026q2
- https://info.zenn.dev/2026-07-24-zennfes-spring-2026-result

## Local verification

```bash
python -m compileall pipeline
python -m unittest discover -s tests -v
python -m pipeline.audit
```

## Runtime

候補生成:

```bash
python -m pipeline.cli candidate
```

公開選抜:

```bash
python -m pipeline.cli publish
```

GitHub Actionsの生成バックエンドは **GitHub Copilot CLI** です。`copilot-requests: write` と組み込み `GITHUB_TOKEN` で認証し、CLIには read/write/shell/url/memory tool を許可せず、純粋なテキスト生成器として使います。`runtime.py` はJSON契約がMarkdown fenceや短い前置きで装飾された場合でも最初の正当なJSON objectだけを正規化し、objectが無い場合はfail-closeします。private Graphiti readは別のread-only credential `GRAPHITI_READ_TOKEN` を使い、未設定時はGraphiti入力のみskipします。
