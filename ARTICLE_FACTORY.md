# Autonomous Monthly Article Factory

## Objective

毎月1本以上、LAPRAS AI Reviewで3.5以上を狙える最高品質の技術記事を公開する。

量産ではなく、週次で候補を作り、月次で最良候補だけを公開する。

## Pipeline

1. 毎週月曜 09:00 JST に公開GitHub活動を収集する。
2. `GRAPHITI_READ_TOKEN` が設定済みなら、private `KAFKA2306/graphiti` の直近weekly diaryも実行時だけ読み、技術テーマ発見の補助入力にする。
3. Graphiti由来テーマはprivate記録を根拠にせず、公開GitHub上で2件以上の実装証拠へ再接地できる場合だけ候補化する。
4. 直近のrepo、commit、設計テーマから候補を作る。
5. 既存記事との重複を避け、実装証拠が最も強いテーマを選び、`candidates/` に保存する。
6. 毎月25日・27日・29日に候補を比較し、最良1件を選ぶ。
7. LAPRAS公式の5軸（論理性・実用性・読みやすさ・独自性・明確性）を3回独立査読し、中央値で判定する。
8. 一次情報URLを実HTTP取得し、KAFKA2306 GitHub一次証拠2件以上、外部公式一次情報1件以上を必須にする。
9. 目標4.1、最低overall 3.8、各軸3.5以上を満たさなければ最大3回自動改稿する。
10. 合格した1本だけ `articles/*.md` にZenn front matter付きで書き出し、`published: true` にする。
11. 査読値と一次情報検証結果を `reports/*.json` に保存する。

## Autonomous-loop boundary

内側のループは自律化する。

`Graphiti / public GitHub → topic discovery → public evidence grounding → draft → source gate → multi-review → revision → best-of-month selection → publish`

LAPRASの実AI Review値は公開後にLAPRAS側で計算される外部評価であり、公式の取得APIが利用できることを前提にしない。このため、現行実装ではLAPRAS実測値そのものをGitHub Actionsへ自動帰還させるループは持たない。内部ゲートを4.1目標 / 3.8最低にして外部3.5割れを抑える。

将来、LAPRASが公式APIまたは安全な機械取得経路を提供した場合のみ、実測値をcalibration feedbackとして接続する。非公式スクレイピングや認証cookie保存は採用しない。

## Graphiti privacy boundary

Graphiti記録は**アイデア源だけ**に使う。

- private diary本文を記事へ引用しない。
- private diary本文を `candidates/`、`articles/`、`reports/` へ保存しない。
- 個人情報、税務、資産、健康、旅行、私生活、勤務先内部情報、未公開情報はテーマ化しない。
- 技術テーマは必ずpublic GitHub evidenceへ再接地する。
- Graphitiから取得した生テキストはworkflowプロセス内だけで使用し、Gitへstageしない。
- public repoに残すmetadataは抽象化済みテーマ、record count、内容を復元できないdigest、公開証拠だけとする。

`KAFKA2306/graphiti` は別repositoryなので、Actions標準の `GITHUB_TOKEN` ではなく、read-onlyのfine-grained credentialを `GRAPHITI_READ_TOKEN` secretとして一度だけ設定する。未設定時はGraphiti入力だけskipし、公開GitHub由来の通常候補生成は継続する。

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
- `article_factory/graphiti_seed.py` — private Graphiti記録を公開可能な技術テーマへ変換するideation adapter
- `candidates/` — Zenn未公開候補。repository自体はpublicなのでprivate情報を置かない
- `articles/` — Zenn同期対象の公開記事
- `reports/` — 月次品質証跡
- `.github/workflows/monthly-article.yml` — 定期実行
- `.github/workflows/article-factory-ci.yml` — 構文・設定・privacy境界CI

## Failure policy

- 一次情報URLが不足・404・許可外host → 公開しない
- KAFKA2306 GitHub一次証拠が2件未満 → 公開しない
- overall 3.8未満 → 改稿、最終的に失敗なら公開しない
- いずれかの評価軸が3.5未満 → 改稿、最終的に失敗なら公開しない
- Graphiti seedのprivacy check失敗 → Graphiti由来候補を作らない
- `GRAPHITI_READ_TOKEN` 未設定 → Graphiti入力のみskipし通常候補生成を継続
- 同月に既に1本公開済み → 重複公開しない

「月1本」を守るため25日だけでなく27日・29日にも再試行するが、品質ゲートを下げて本数だけ満たすことはしない。
