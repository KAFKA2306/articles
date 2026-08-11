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
source gate + internal proxy review
        ↓
revision / best-version retention
        ↓
weekly candidate accumulation
        ↓
month-end: re-verify all candidates
        ↓
3-review median + deterministic ranking
        ↓
highest passing candidate only
        ↓
articles/*.md
```

Graphitiは**アイデア源のみ**です。private diary本文、個人情報、税務、資産、健康、旅行、私生活、勤務先内部情報、未公開情報をpublic repoへ保存しません。

## Directory contract

```text
.github/workflows/
  article-pipeline.yml       # weekly candidate / actual month-end publish
  article-pipeline-ci.yml    # compile + tests + repository audit

pipeline/
  cli.py                     # candidate / publish entry point
  core.py                    # collection, drafting, source gate, proxy review, selection, publish
  graphiti.py                # private weekly → readable in-memory context → public-safe topic
  audit.py                   # fail-close repository/privacy audit
  config.json                # quality and path contract
  contracts/article.md       # writing/review/selection contract
docs/
  ARCHITECTURE.md
  GRAPHITI_WEEKLY.md

artifacts/
  candidates/YYYY-MM/        # unpublished, public-safe candidates only
  reports/YYYY-MM/           # review/source/selection/runtime evidence

articles/                    # Zenn-compatible published articles only
tests/
```

`articles/` だけが公開記事の正準出力です。候補と査読証跡は `artifacts/` に隔離し、実装コードは `pipeline/` に集約します。

## Automation

毎週月曜 09:00 JST:
- GitHub Models inferenceをpreflightする
- inferenceがHTTP 410なら生成をfail-closeし、`artifacts/reports/YYYY-MM/runtime-status.json` にblockerを保存する
- Graphiti weeklyをread-onlyで読む（`GRAPHITI_READ_TOKEN` がある場合のみ）
- weeklyを読みやすい作業用contextへ圧縮
- private内容を根拠にせず、公開GitHub evidence 2件以上へ再接地
- Graphiti由来候補 + public GitHub由来候補を生成
- source gateと内部proxy査読を実施
- target 4.1に届かなければ最大 `revision_limit` 回改稿
- 改稿で悪化した場合は評価済み版の最良版を候補として保持

毎月28〜31日 23:30 JST:
- workflowはfinalization windowとして起動
- 実際の暦上の月末日だけpublish処理を続行
- 当月の全候補から `pipeline_meta` を除いた公開本文だけを再検証
- 全候補を5軸×3回独立査読し、各軸中央値で判定
- `overall >= 3.8`、全軸 `>= 3.5`、source gate PASSのみを公開可能集合にする
- `overall` → 最低軸 → 自GitHub証拠数 → 有効一次情報数で決定的に順位付け
- 最高品質の1本だけを `articles/` へ公開
- 合格候補がなければ0本で終了
- 同月に1本公開済みなら追加公開しない

`workflow_dispatch` の `publish` は明示的な手動実行として月末日前でも許可します。ローカルで早期公開判定を試す場合は `ARTICLE_ALLOW_EARLY_PUBLISH=1` を明示します。

## Quality gate

内部評価は **LAPRAS AI Reviewで公開されている5軸を参考にしたproxy** です。LAPRAS上の実測AI Review値ではありません。

- evaluation kind: `internal_lapras_rubric_proxy`
- target overall: 4.1
- minimum overall: 3.8
- minimum each axis: 3.5
- primary-source URLs: 3件以上
- KAFKA2306 GitHub evidence: 2件以上
- external official primary source: 1件以上
- URLは実HTTP取得で検証
- gate失敗時は公開しない
- monthly publication limit: 1

## GitHub-side prerequisites

GitHub ActionsからGitHub Modelsを使うには、workflowの `models: read` だけでなく、repository自体でGitHub Modelsが有効になっている必要があります。

- GitHub公式: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-github-models-in-your-repository
- `KAFKA2306/articles` では **Settings → Models → Models in this repository → Enabled** が必要
- inferenceが利用不可の間は、記事を捏造・代替公開せずruntime blockerを記録して正常終了する
- 利用可能になった次回runではblocker reportを削除して通常生成へ復帰する

Graphiti入力には別途、private `KAFKA2306/graphiti` だけをread-onlyで読める `GRAPHITI_READ_TOKEN` が必要です。未設定時はGraphiti入力のみskipし、GitHub Modelsが利用可能ならpublic GitHub由来候補は継続します。

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

詳細は [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) と [`docs/GRAPHITI_WEEKLY.md`](docs/GRAPHITI_WEEKLY.md) を参照してください。
