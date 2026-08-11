# Autonomous Monthly Article Factory

## Objective

毎月1本以上、LAPRAS AI Reviewで3.5以上を狙える最高品質の技術記事を公開する。

量産ではなく、週次で候補を作り、月次で最良候補だけを公開する。

## Pipeline

1. 毎週月曜 09:00 JST に公開GitHub活動を収集する。
2. 直近のrepo、commit、設計テーマから5候補を作る。
3. 既存記事との重複を避け、実装証拠が最も強いテーマを1件選ぶ。
4. 記事を生成し `candidates/` に保存する。
5. 毎月25日・27日・29日に候補を比較し、最良1件を選ぶ。
6. LAPRAS公式の5軸（論理性・実用性・読みやすさ・独自性・明確性）を3回独立査読し、中央値で判定する。
7. 一次情報URLを実HTTP取得し、KAFKA2306 GitHub一次証拠2件以上、外部公式一次情報1件以上を必須にする。
8. 目標4.1、最低overall 3.8、各軸3.5以上を満たさなければ最大3回自動改稿する。
9. 合格した1本だけ `articles/*.md` にZenn front matter付きで書き出し、`published: true` にする。
10. 査読値と一次情報検証結果を `reports/*.json` に保存する。

## Why the gate is stricter than 3.5

LAPRASの実AI Reviewは公開後のクロールで初めて確定するため、GitHub Actions内では同一値を事前取得できない。そのため内部評価を安全側に寄せ、3.5を直接目標にせず4.1を目標、3.8を最低公開基準とする。

## GitHub Models

GitHub Actionsでは `GITHUB_TOKEN` と `permissions: models: read` を使い、GitHub Modelsの推論APIを利用する。追加APIキーを必須にしない。

既定モデルは `openai/gpt-4.1`。変更する場合はworkflowの `ARTICLE_MODEL` を更新する。

## Zenn connection

Zennへの自動公開には、Zenn側でこのGitHub repositoryをアカウント連携repoとして一度だけ接続し、同期ブランチを `main` に設定する必要がある。

Zenn公式仕様では、連携済みrepoの同期対象branchにpushすると自動デプロイされ、`articles/*.md` の `published: true` が公開対象になる。

この外部OAuth/GitHub App承認だけはGitHub repository内のコードから代行できない。接続後は月次候補生成・選抜・改稿・公開まで自動化される。

## Repository outputs

- `article_factory/config.json` — 品質ゲートとモデル設定
- `article_factory/prompt.md` — 執筆・査読契約
- `article_factory/run.py` — 生成・査読・一次情報検証・公開処理
- `candidates/` — 非公開候補
- `articles/` — Zenn同期対象の公開記事
- `reports/` — 月次品質証跡
- `.github/workflows/monthly-article.yml` — 定期実行
- `.github/workflows/article-factory-ci.yml` — 構文・設定CI

## Failure policy

- 一次情報URLが不足・404・許可外host → 公開しない
- KAFKA2306 GitHub一次証拠が2件未満 → 公開しない
- overall 3.8未満 → 改稿、最終的に失敗なら公開しない
- いずれかの評価軸が3.5未満 → 改稿、最終的に失敗なら公開しない
- 同月に既に1本公開済み → 重複公開しない

「月1本」を守るため25日だけでなく27日・29日にも再試行するが、品質ゲートを下げて本数だけ満たすことはしない。
