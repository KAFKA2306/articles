---
title: "AIの「完了しました」を、仕事ごとの証拠で確かめる"
emoji: "🔎"
type: "tech"
topics: ["codex", "aiagents", "evals", "github", "automation"]
published: false
---

AIに仕事を任せても、毎回「動いた？」「出典は合っている？」「音源は最後まで聴いた？」と聞き直すなら、確認の仕事が人間に残ります。だからといって、テストが通っただけで「完了」にすると、実際に使える状態かどうかを見落とします。

私たちは、開発・研究・制作を支える `.codex` を刷新します。人間が目的と権限を定め、Codexがその範囲で作業します。各プロジェクトの既存ツールが成果物を読み戻し、依頼の目的に合った証拠で完了を判定します。同じ成果物でも目的が違えば証拠は変わります。この違いを評価基準に残し、品質と人の介入を比較します。 [複数リポジトリの運用記録](https://github.com/KAFKA2306/articles/blob/e3001144bb04ba2b80233ccb96c5576483588cce/articles/chatgpt-multiproject-autonomy.md)

## 公開フラグを変えて検査に通してみた

このリポジトリの既存の下書きで、公開フラグを `false` から `true` に変えました。ネットワークへ送らないローカル作業ツリーで変更をコミットし、CIと同じ `python -m pipeline.publication_diff` を変更前後のコミットに対して実行すると、`PUBLICATION_DIFF_PASS: promotions=1 repairs=0` が返りました。当該の下書きは11月9日に `main` に追加されたものです。比較対象の公開用ブランチ `zenn-release` は9月2日のコミットで止まっており、下書きを含みません。公開操作は試さず、同じ記事で差分検査の結果と公開用ブランチを読み比べました。

検査が確認したのは、公開状態への変更がリポジトリの差分ルールを満たすことです。公開を確かめるには、対象ページを取得する必要があります。同じMarkdownを扱っていても、下書きを収録する仕事では収録先のコミットが証拠になり、読者が読める状態にする仕事では公開先が証拠になります。評価を分ける単位は、ファイルの種類でも「開発」という分類でもなく、依頼した目的です。

再現には [実験時の main](https://github.com/KAFKA2306/articles/tree/e3001144bb04ba2b80233ccb96c5576483588cce) と [公開用ブランチの観測時点](https://github.com/KAFKA2306/articles/tree/1c541d5d538b67e31d83fa115e98a8bfda0dfb02) を使えます。対象は [作業契約の記事の下書き](https://github.com/KAFKA2306/articles/blob/e3001144bb04ba2b80233ccb96c5576483588cce/articles/2026-11-09-portable-agent-contracts.md) です。

~~~sh
base=e3001144bb04ba2b80233ccb96c5576483588cce
release=1c541d5d538b67e31d83fa115e98a8bfda0dfb02
file=articles/2026-11-09-portable-agent-contracts.md
set -e
git worktree add --detach ../codex-eval-fixture "$base"
cd ../codex-eval-fixture
python - "$file" <<'PYCODE'
import sys
from pathlib import Path

path = Path(sys.argv[1])
draft = path.read_text(encoding="utf-8")
flag = "published"
path.write_text(draft.replace(f"{flag}: false\n", f"{flag}: true\n", 1), encoding="utf-8")
PYCODE
git add "$file"
git commit -m 'Local fixture: single publication flag transition'
python -m pipeline.publication_diff --base "$base" --head HEAD
git ls-tree "$release" -- "$file"  # この版では出力が空
cd -
git worktree remove ../codex-eval-fixture
~~~

OpenAIのCodex運用事例でも、エージェントがアプリを操作して修正前後を確認できるようにしています。Anthropicは、単体テストやHTTPリクエストを試しても利用者の操作経路では機能が欠けていた事例を報告しています。どちらも、まず仕事が終わったときの状態を決め、その状態を利用者が触る場所で観測する設計の参考になります。 [OpenAIのCodex運用事例](https://openai.com/index/harness-engineering/) ／ [Anthropicの長時間実行エージェント事例](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents)

## Evals Agentは「ドメイン × 目的」で基準を選ぶ

Evals Agentは、依頼に付けた「ドメイン × 目的」と基準の版を読み、成果物と実行結果を照合する役割です。実行主体はCodexの単独セッションです。決まった採点は既存のテストや計測器を呼ぶスクリプトが行います。一次資料が主張を支えるか、音声の間が演出意図に沿うかなどは、同じセッションに典型例と該当箇所を渡します。評価側は版を固定した基準と証拠を読み、セッションからは所見だけを受け取ります。根拠が不足した項目は未確認で返します。 [Anthropicの評価設計](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) ／ [OpenAIの評価設計](https://developers.openai.com/api/docs/guides/evaluation-best-practices)

| ドメイン × 目的 | 確認する証拠 | 誤って「完了」としやすい例 |
| --- | --- | --- |
| ソフトウェア × 不具合修正 | 通常の利用経路での修正前後の挙動、対象リビジョンの回帰検査。デプロイまで依頼された場合は、対象環境でその版が動くこと | テストは成功したが、利用者の経路で症状が再現する |
| 研究 × 定量結果の再現 | 主張に対応する一次資料の箇所、利用可能だった時点、入力値・単位・計算方法、許容差を含む再計算結果 | 数字は合うが、対象時点より後に公開された値が混じる |
| 音声制作 × 完成ミックスの確認 | 再生、欠落、クリッピングなどの技術検査と、作品指示に沿う演技・間・聞き取りやすさを確認した試聴箇所 | 音量は仕様内だが、台詞が抜けているか、演技が作品の狙いを外す |

研究の時点整合性には既出の [finBIの事例](https://github.com/KAFKA2306/finBI/issues/10) を使えます。音声では [夜話アーカイブの監査要件](https://github.com/KAFKA2306/yt3/issues/504) に沿い、作品群の声質・作風・画風の偏りは制作・公開を止めない独立の観測として扱います。Anthropicはアプリの評価基準の書き方が作風の収束に影響した事例を報告しています。音声でも表現を固定しやすい共通点数の採用は避け、作品ごとの意図と試聴結果を記録する方針です。 [Anthropicの制作・評価分離の事例](https://www.anthropic.com/research/harness-design-long-running-apps) ／ [OpenAIの対話音声評価の例](https://developers.openai.com/cookbook/examples/audio/voice_agent_evaluation)

各必須条件は「合格」「不合格」「未確認」で返し、証拠と理由を添えます。必須条件に未確認が残れば、完了判定は保留します。作品全体を平均点で合格させると、台詞の欠落のような必須条件が埋もれるためです。合否への効き方も基準に書きます。

## いま使っている仕組みから始める

最初に `AGENTS.md`、Skills、Agents、MCP、自動化を棚卸しし、実際に読み込まれた指示、使えるツール、定時実行が残した証拠、重複した判定を確かめます。既存の自動化に評価の呼び出しを足し、同じ仕事を回すスケジュールの重複を避けます。

- `AGENTS.md` には共通の作業方針と、各プロジェクトの契約を探す場所を置きます。繰り返す手順は既存のSkillsに寄せ、Codexが探索する `.agents/skills` など、実際に読み込まれる場所で維持します。 [OpenAIのAGENTS.mdガイド](https://learn.chatgpt.com/docs/agent-configuration/agents-md) ／ [Skillsガイド](https://learn.chatgpt.com/docs/build-skills)
- 既存のAgentsに書かれた観測点をMasterへ移し、評価の実行はプロジェクトの標準コマンドへ集約します。MCPは一次資料と現在状態を取得する既存接続を使います。外部書き込みの権限、例外、公開の判断は人間が先に定め、運用中の処理は定時ジョブとスクリプトで進めます。 [OpenAIの実装事例](https://openai.com/index/harness-engineering/) ／ [OpenAIのMCPガイド](https://learn.chatgpt.com/docs/extend/mcp?surface=cli) ／ [Anthropicの制作・評価の実装事例](https://www.anthropic.com/research/harness-design-long-running-apps)

## 判定をUNIXコマンドでつなぐ

既存ジョブは「現状を取得 → 目的別の検査を実行 → 書き込み先で読み戻す → 台帳に追記 → 集計」の順に呼びます。終了コードは `0` が合格、`1` が不合格、`2` が未確認。標準出力には案件ID、成果物の版、基準版、項目、判定、証拠への参照、観測値をJSON Linesで出し、診断は標準エラーへ送ります。応答が途切れたら同じ案件IDで書き込み先を照会し、済んだ操作は確認結果を再利用します。

| 受け持つ仕事 | 2026年公開の版と既存の入口 |
| --- | --- |
| 作業と意味の確認 | Codex CLI 0.164.0の `codex exec --json`。GPT-6 Astraに渡すのは目的、基準の該当項目、差分、証拠の該当箇所。判定と再集計の定型処理ではモデル呼び出し0回。使用量はCLIのJSONLから拾う。 [CLIリリース](https://github.com/openai/codex/releases/tag/rust-v0.164.0) ／ [非対話実行](https://learn.chatgpt.com/docs/non-interactive-mode) ／ [Skillsとプロンプトの実測](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) |
| ブラウザの操作確認 | リポジトリの利用経路テストを優先し、新規のブラウザテストはPlaywright 1.61.0の `playwright test --reporter=json` で記録する。 [リリース](https://github.com/microsoft/playwright/releases/tag/v1.61.0) ／ [JSONレポーター](https://playwright.dev/docs/test-reporters) |
| 研究の再計算と横断集計 | DuckDB CLI 1.5.4で、取得済みの表の単位・時点をそろえて再計算し、同じ実行ファイルでLedgerを集計する。一次資料の取得は各案件の正規経路を使う。 [CLI初出](https://duckdb.org/2026/03/09/announcing-duckdb-150) ／ [1.5.4リリース](https://duckdb.org/2026/06/17/announcing-duckdb-154) |
| 音声ファイルの検査 | FFmpeg 8.1.3の `ffprobe` でストリームと長さを取り、`ffmpeg` でデコードとラウドネス・ピークを確認する。演技や間の所見には台本の行と再生時刻を添える。 [リリース](https://ffmpeg.org/download.html#release_8.1) ／ [ffprobe](https://ffmpeg.org/ffprobe.html) ／ [音声フィルター](https://ffmpeg.org/ffmpeg-filters.html) |

新しく加える直接依存は、公開日・採用版・使う機能・一次URLをプロジェクトに記録します。自作は、既存コマンドの入出力をつなぐ短いスクリプトと、案件でしか決められない評価基準に絞ります。同じ目的の候補は必須条件で絞り、Masterで先に決めた優先指標で比較します。同点は現行版を採用し、試作は破棄します。判定を再現する証拠と採用理由を残します。

## 評価を後から再現できるようにする

Ledger、Master、Star Schemaは今回の運用設計です。既存のGit、実行ログ、証拠台帳を参照し、同じデータの書き写しを減らします。非公開の資料・音声・実行ログは元のアクセス制御下に置き、台帳には権限を維持した参照と判定に必要な情報を記録します。公開リポジトリに出すのは公開できる証拠です。

| 役割 | 記録する内容 |
| --- | --- |
| Ledger | 案件と評価のID、成果物の版、基準の版、条件ごとの判定と根拠、例外や介入、失敗と復旧結果。再評価と訂正は元の記録を参照する新しい行にする |
| Master | ドメインと目的ごとの必須条件、使う証拠、判定方法、許容差、判断を人に戻す条件の版。変更理由と適用開始を残す |
| Star Schema | 案件、ドメイン、目的、基準版、日付を共有する。条件判定は「評価 × 条件」に1行。利用量と介入は「実行」に1行。復旧は「障害」に1行。各粒度で先に集計してから比較する |

例えば、1回の実行に100トークン、必須条件が2件あるとします。条件行と結合した後に利用量を足すと200になり、実行単位で先に足すと100になります。次の合成データをDuckDB CLI 1.5.4で実行して両方の出力を確認しました。

~~~sh
duckdb -csv -c "
WITH runs(id, tokens) AS (VALUES ('run-1', 100)),
     checks(run_id, criterion) AS (VALUES ('run-1', 'action'), ('run-1', 'readback'))
SELECT (SELECT sum(tokens) FROM runs JOIN checks ON id = run_id) AS joined_total,
       (SELECT sum(tokens) FROM runs) AS run_total;"
~~~

出力は `joined_total=200`、`run_total=100`。再試行の負担を評価するには、失敗した実行の利用量も実行表へ入れます。`input_tokens` と `output_tokens` を合計し、キャッシュ済み入力と推論出力は内訳として保持します。記録が欠けた実行は未計測件数として出します。 [Codexの利用量イベント](https://learn.chatgpt.com/docs/non-interactive-mode)

## 実案件で任せられる範囲を広げる

まず各ドメインの代表案件で、従来の完了判定と新しい判定を並行して記録します。同じ成果物に対する判定の比較と、同程度の案件に対する作業全体の比較を行います。比較前に案件の選び方と品質基準を固定し、新しい評価はまず閲覧用に動かします。正しい成果物、完了に見える不合格、証拠が不足した成果物を混ぜ、評価担当自身の誤判定も測ります。

| 比較するもの | 数え方 |
| --- | --- |
| 成果の品質 | 同じ基準での合格件数と対象件数を目的ごとに記録する。未確認件数も示す |
| 不要な人間の介入 | 権限内で証拠から処理できた確認の件数と所要時間を、対象案件数とともに記録する。人間の判断が必要だった介入も件数を残す |
| 誤った完了判定 | 既知の不合格のうち、検出・誤合格・保留の件数を記録する。既知の合格についても、誤却下と保留を数える |
| 失敗からの復旧 | 復旧可能な失敗を分母に、完了条件を再確認でき、外部への二重書き込みが生じなかった件数と復旧時間を記録する |
| トークン | 成功・失敗を含む総入力・出力と使用量の取得率を出す。完了を証拠で確認できた案件数を分母に比較し、合格0件のときは総量と件数を出す |

「作業は続けられるが証拠が消えた」「外部操作は成功したが応答が途切れた」ケースも、隔離した環境で試します。試験の期待結果は先に固定し、採点基準を調整する案件と導入判断に使う案件を分けます。品質と誤判定を維持または改善し、通常の手動確認が減り、復旧できた目的から適用を広げます。

全プロジェクトでの品質、介入削減、誤判定検出、復旧率はこれから測ります。自分の案件で試すなら、いま「完了」を決めている工程を一つ選び、手前の検査を通っても目的を達成していない成果物を用意してください。それを完了と判定するなら、依頼の成功を直接確認できる証拠を一つ加えます。
