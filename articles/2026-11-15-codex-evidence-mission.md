---
title: "AIが「完了しました」と言ったら、どこを見れば確かめられるか"
emoji: "🔎"
type: "tech"
topics: ["codex", "aiagents", "evals", "github", "automation"]
published: false
---

記事の公開フラグを変えると、CIと同じ検査が通りました。でも、公開用ブランチを調べると、その記事はまだ入っていませんでした。「公開できる差分か」と「読者が読めるか」では、見る場所が違います。

開発・研究・音声制作を支える `.codex` を見直すときは、まず依頼者が受け取る結果を一つ書きます。不具合修正なら、利用者の操作で症状が消えたか。調査なら、その日に入手できた資料で数字を再計算できるか。音声なら、納品ファイルを再生したときに台詞がそろい、狙った間で聞こえるか。そこから、Codexに任せる作業と、完了を確かめる方法を決めます。 [複数リポジトリの運用記録](https://github.com/KAFKA2306/articles/blob/e3001144bb04ba2b80233ccb96c5576483588cce/articles/chatgpt-multiproject-autonomy.md)

## 公開フラグを変えて、公開用ブランチを調べた

手元の作業ツリーで下書きの `published` を `false` から `true` に変え、CIと同じ差分検査にかけました。結果は `PUBLICATION_DIFF_PASS: promotions=1 repairs=0`。11月9日に追加された下書きは、比較に使った9月2日の `zenn-release` には入っていませんでした。実験はローカルで行い、公開ページの検証は実際の公開時に行います。 [対象の下書き](https://github.com/KAFKA2306/articles/blob/e3001144bb04ba2b80233ccb96c5576483588cce/articles/2026-11-09-portable-agent-contracts.md) · [比較した公開用ブランチの版](https://github.com/KAFKA2306/articles/tree/1c541d5d538b67e31d83fa115e98a8bfda0dfb02)

「原稿をGitHubに収録する」依頼なら、`main` の対象コミットから原稿を読み戻せば確認できます。「読者が読めるようにする」依頼なら、公開URLで読めることまで確認します。同じMarkdownを直す仕事でも、依頼が変わると完了の証拠も変わります。

再現するには、GitとPythonが使える環境で、このリポジトリの履歴と公開用ブランチを取得しておきます。リポジトリ内で次を実行すると、差分検査の合格行が出たあと、固定した公開用コミットに原稿が存在しないこともコマンドの終了コードで確認できます。

~~~sh
(
  set -eu
  base=e3001144bb04ba2b80233ccb96c5576483588cce
  release=1c541d5d538b67e31d83fa115e98a8bfda0dfb02
  file=articles/2026-11-09-portable-agent-contracts.md
  repo=$(git rev-parse --show-toplevel)
  scratch=$(mktemp -d)
  tree="$scratch/fixture"
  trap 'git -C "$repo" worktree remove --force "$tree" 2>/dev/null || true; rmdir "$scratch"' EXIT
  git worktree add --detach "$tree" "$base"
  cd "$tree"
  python - "$file" <<'PYCODE'
import sys
from pathlib import Path

path = Path(sys.argv[1])
draft = path.read_text(encoding="utf-8")
flag = "published"
assert f"{flag}: false\n" in draft
path.write_text(draft.replace(f"{flag}: false\n", f"{flag}: true\n", 1), encoding="utf-8")
PYCODE
  git add "$file"
  git -c user.name=Fixture -c user.email=fixture@example.invalid commit -m 'Test a publication flag locally'
  python -m pipeline.publication_diff --base "$base" --head HEAD
  test -z "$(git ls-tree "$release" -- "$file")"
)
~~~

OpenAIのCodex運用事例では、エージェントがアプリを操作し、修正前後の挙動を確かめています。Anthropicの事例では、単体テストやHTTPの応答を確認しても、利用者の操作では機能の欠落が見つかりました。評価の手順を書くときは、仕事が終わったあとに利用者が実際に触る場所から考えます。 [OpenAIのCodex運用事例](https://openai.com/index/harness-engineering/) · [Anthropicの長時間実行エージェント事例](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents)

## 何を頼んだかで、確かめ方を変える

Evals Agentは、Codexが単独セッションの中で担う評価の役割です。依頼に付けた「分野と目的」から基準の版を選び、既存のテストや計測器を呼びます。資料が主張を支えるか、台詞の間が演出に合うかなど、意味の確認が必要なときだけ、同じセッションに判定例と該当箇所を渡します。必須項目ごとに合格・不合格・未確認を返し、根拠を添えます。未確認が残った案件は保留です。 [Anthropicの評価設計](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) · [OpenAIの評価設計](https://developers.openai.com/api/docs/guides/evaluation-best-practices)

| 依頼 | 確かめること | 見落としやすいこと |
| --- | --- | --- |
| ソフトウェアの不具合を直す | 普段の操作で修正前に症状が出て、修正後に消えるか。デプロイまで頼まれたら対象環境に入った版も確かめる | テストは通っているのに、利用者の操作ではまだ壊れる |
| 研究の数値を再現する | 根拠の原文、利用できた日付、入力値・単位・式をそろえ、決めた許容差に収まるか | 後日公開された値を使って、当時の結果を再現したことにする |
| 音声の完成ミックスを確認する | 再生できるか、台詞の欠落や音割れがないか。演技、間、聞き取りやすさは台本の行と再生時刻を添えて確認する | 音量は基準内でも台詞が一つ抜けている |

研究では、資料の公開時点を確認する試験を作れます。音声では、作品ごとの演出指示から試聴箇所を決めます。作品群を通じた声質や作風、画風の偏りは、夜話アーカイブで別に観測します。作品ごとの合否は、その作品の意図と納品物から判断します。 [finBIの時点整合性の事例](https://github.com/KAFKA2306/finBI/issues/10) · [夜話アーカイブの監査要件](https://github.com/KAFKA2306/yt3/issues/504) · [Anthropicの評価基準と作風の事例](https://www.anthropic.com/research/harness-design-long-running-apps) · [OpenAIの対話音声評価例](https://developers.openai.com/cookbook/examples/audio/voice_agent_evaluation)

## 既存のコマンドをつなぐ

`AGENTS.md`、Skills、Agents、MCP、自動化を見直し、実際に読み込まれた指示と実行履歴を探します。`AGENTS.md` には作業方針と基準の場所を置き、繰り返す手順は既存のSkillsから呼びます。Agentsに書かれた評価基準は、後から同じ版で採点できるようMasterに移します。MCPの既存接続は一次資料や実行結果の取得に使います。人間が先に目的と権限を決め、例外や公開などの重要な判断を引き受けます。 [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) · [Skills](https://learn.chatgpt.com/docs/build-skills) · [MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)

定時ジョブは、現在の状態を取る、目的別の検査を走らせる、書き込み先で結果を確かめる、台帳へ追記する、の順でコマンドを呼びます。応答が途切れたときは、同じ案件IDで書き込み先を調べてから再開します。定型判定と再集計のモデル呼び出しは0回。モデルには依頼、変更箇所、基準の該当項目、必要な証拠だけを渡します。 [Codexの非対話実行](https://learn.chatgpt.com/docs/non-interactive-mode) · [OpenAIのSkillsとプロンプトの実測](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)

コマンドは案件ID、成果物と基準の版、判定、観測値、証拠への参照をJSON Linesで出し、診断を標準エラーへ送ります。終了コードは合格が `0`、不合格が `1`、未確認が `2` です。新しい直接依存には2026年公開版を使い、版・公開日・使用箇所・一次URLを記録します。

| 作業 | 使う外部ツール |
| --- | --- |
| 制作と意味の確認 | Codex CLI 0.164.0の `codex exec --json` でGPT-6 Astraを実行し、使用量をJSONLから読む。 [CLIリリース](https://github.com/openai/codex/releases/tag/rust-v0.164.0) |
| ブラウザ操作 | リポジトリの既存テストを使う。新設する場合はPlaywright 1.61.0で `playwright test --reporter=json` を実行する。 [リリース](https://github.com/microsoft/playwright/releases/tag/v1.61.0) · [JSONレポーター](https://playwright.dev/docs/test-reporters) |
| 数値の再計算と台帳の集計 | DuckDB CLI 1.5.4で、取得済みの表を揃えて再計算し、同じCLIで台帳を集計する。 [新CLIの発表](https://duckdb.org/2026/03/09/announcing-duckdb-150) · [1.5.4リリース](https://duckdb.org/2026/06/17/announcing-duckdb-154) |
| 音声ファイル | FFmpeg 8.1.3の `ffprobe` でストリームと長さを調べ、`ffmpeg` でデコード、ラウドネス、ピークを測る。 [リリース](https://ffmpeg.org/download.html#release_8.1) · [ffprobe](https://ffmpeg.org/ffprobe.html) · [音声フィルター](https://ffmpeg.org/ffmpeg-filters.html) |

自作するのは、コマンド間で値を渡す短いスクリプトと、案件ごとの合格条件です。候補が複数あるときは、必須条件に通ったものを、先に決めた指標で比較します。同点なら現行版を採用します。試作を片付けたあとも、採用理由と判定をやり直せる証拠は残します。

## 100トークンを200と数えない

どの結果をどの基準で合格にしたか、あとから確かめられるようにします。判定と根拠はLedger、判定に使う条件とその版はMasterに置きます。訂正や再評価は、元の記録を参照する新しい行で残します。公開リポジトリへ載せる証拠は公開できるものに限り、元資料や音源は元のアクセス権で管理します。

分野をまたいで比較するときは、案件・目的・基準版・日付を共通にするStar Schemaを使います。判定は「評価1回の1条件」、利用量と介入は「実行1回」、復旧は「障害1件」を1行として記録します。

合成データで、100トークン使った実行に2つの判定を結びつけました。判定と結合した表でそのまま足すと、100が2行に現れて200になります。実行表で足すと100です。

~~~sh
duckdb -csv -c "
WITH runs(id, tokens) AS (VALUES ('run-1', 100)),
     checks(run_id, criterion) AS (VALUES ('run-1', 'action'), ('run-1', 'readback'))
SELECT (SELECT sum(tokens) FROM runs JOIN checks ON id = run_id) AS joined_total,
       (SELECT sum(tokens) FROM runs) AS run_total;"
~~~

DuckDB CLI 1.5.4での出力は `joined_total=200`、`run_total=100` でした。実案件では失敗した実行も記録し、`input_tokens` と `output_tokens` を足します。キャッシュ済み入力と推論出力は内訳として持ち、取得できなかった実行は未計測として数えます。 [Codexの使用量イベント](https://learn.chatgpt.com/docs/non-interactive-mode)

## 実案件で「任せてよい」を確かめる

最初は同じ成果物に従来の判定と新しい判定をかけます。品質基準と対象の選び方を先に決め、正常例、完了に見える不合格例、証拠が足りない例を混ぜます。書き込みが済んだ直後に応答が途切れた場合も、隔離した環境で再現します。基準を調整した案件とは別の案件で、以下を測ります。

| 見たいこと | 数え方 |
| --- | --- |
| 成果の品質 | 目的ごとに、対象件数、合格件数、未確認件数を出す |
| 人間の介入 | 権限内で処理できた確認と、人の判断が必要だった確認の件数・所要時間を記録する |
| 誤った完了判定 | 既知の不合格を正しく落とした数、誤合格、保留を数える。既知の合格についても誤却下と保留を数える |
| 失敗からの復旧 | 復旧可能な障害を分母に、二重書き込みを起こさず完了条件を再確認できた件数と、復旧時間を出す |
| トークン | 失敗分を含む入力・出力の総量と取得率を出し、合格を確認した案件1件あたりで比べる。合格0件なら総量と件数を示す |

今回再現したのは、公開の差分検査と公開先の状態が別々に観測できること、利用量は実行単位で集計する必要があることです。品質、介入、誤判定、復旧は各分野の実案件で測ります。

自分の案件で始めるなら、完了と判定する工程を一つ選びます。そこで検査に通るのに利用者が目的を果たせない例を作り、どこを見れば見落としを拾えるか考えます。記事なら公開ページ、不具合修正なら普段の操作、音声なら台詞が抜けた再生位置。その一つを、いつもの検証コマンドに加えます。
