# KAFKA2306/articles

技術記事の**生成・検証・選抜・公開を行う正準repository**です。

このrepoは投資ガイドや単発HTMLの保管場所ではありません。private `KAFKA2306/graphiti` の週間記録と公開GitHub活動から技術テーマを発見し、公開一次証拠へ再接地できた候補だけを記事化します。

## Canonical loop

```text
Graphiti weekly (private) ─┐
                          ├─> topic discovery
Public GitHub evidence ───┘
        ↓
public evidence grounding
        ↓
draft
        ↓
source gate
        ↓
multi-review
        ↓
revision
        ↓
best-of-month selection
        ↓
articles/*.md
```

Graphitiは**アイデア源のみ**です。private diary本文、個人情報、税務、資産、健康、旅行、私生活、勤務先内部情報、未公開情報をpublic repoへ保存しません。

## Directory contract

```text
.github/workflows/
  article-pipeline.yml       # weekly candidate / monthly publish
  article-pipeline-ci.yml    # compile + tests + repository audit

pipeline/
  cli.py                     # candidate / publish entry point
  core.py                    # collection, drafting, source gate, review, publish
  graphiti.py                # private weekly → readable in-memory context → public-safe topic
  selection.py               # candidate maturation + month-end review-all selection
  audit.py                   # fail-close repository/privacy audit
  config.json                # quality and path contract
  contracts/article.md       # writing/review contract

docs/
  ARCHITECTURE.md
  GRAPHITI_WEEKLY.md

artifacts/
  candidates/YYYY-MM/        # unpublished, public-safe candidates only
  reports/YYYY-MM/           # review/source evidence

articles/                    # Zenn-compatible published articles only
tests/
```

`articles/` だけが公開記事の正準出力です。候補と査読証跡は `artifacts/` に隔離し、実装コードは `pipeline/` に集約します。

## Automation

毎週月曜 09:00 JST:
- Graphiti weeklyをread-onlyで読む（`GRAPHITI_READ_TOKEN` がある場合のみ）
- weeklyを読みやすい作業用contextへ圧縮
- private内容を根拠にせず、公開GitHub evidence 2件以上へ再接地
- Graphiti由来候補 + public GitHub由来候補を生成

毎月の実月末 23:30 JST:
- 当月候補を全件、同一条件で再評価
- source gateを再実行
- 内部LAPRAS-rubric proxyの5軸を3回独立査読して中央値で判定
- 最大3回改稿
- 合格した最高品質1本だけを `articles/` へ公開（合格0本なら公開0本）

## Quality gate

- target overall: 4.1
- minimum overall: 3.8
- minimum each axis: 3.5
- primary-source URLs: 3件以上
- KAFKA2306 GitHub evidence: 2件以上
- external official primary source: 1件以上
- URLは実HTTP取得で検証
- gate失敗時は公開しない

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

GitHub Actionsの生成バックエンドは **GitHub Copilot CLI** です。`copilot-requests: write` と組み込み `GITHUB_TOKEN` で認証し、CLIには read/write/shell/url/memory tool を許可せず、純粋なテキスト生成器として使います。GitHub Modelsは2026-07-30に終了したため使用しません。private Graphiti readは別のread-only credential `GRAPHITI_READ_TOKEN` を使い、未設定時はGraphiti入力のみskipします。

詳細は [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) と [`docs/GRAPHITI_WEEKLY.md`](docs/GRAPHITI_WEEKLY.md) を参照してください。
