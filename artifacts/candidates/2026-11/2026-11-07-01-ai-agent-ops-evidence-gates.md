# AIを毎時動かしても、開発が進んだ証拠はどこにある？

> 状態: 未公開の記事候補。調査基準日: 2026-11-07。変更前後の自プロジェクト実測と本番反映の独立証拠は未収集。公開判定: 保留。
>
> 対象読者: 自律コーディング、AIエージェント、定期実行による開発改善を運用する人。
>
> 記事の中心的な提案は設計仮説であり、効果の実証ではない。提案の根拠は本文の一次資料URLに示す。

## タイトル候補

1. 広い入口: **AIを毎時動かしても、開発が進んだ証拠はどこにある？**（採用）
2. 具体的な問題: **「実行成功」と「修正完了」を取り違えない、AI自律開発の作り方**
3. 検索可能: **AIエージェントの自律改善ループ設計：Harness、Evals、GitHub Actionsをつなぐ**

## 動いたことと、直ったことは違う

エージェントが「修正しました」と返答しても、利用者が期待する状態に変わったとは限らない。Anthropicはエージェント評価を説明する際、会話上の完了宣言（transcript）と、実際に環境に残った結果（outcome）を区別している。たとえば予約したという回答だけでは、予約データが存在する証拠にならない。出典：[Anthropic, *Demystifying evals for AI agents*, 2026-01-09](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)。

これをGitHub上の自律開発に移すなら、成功条件を「調べた」「提案した」「コミットした」「テストが通った」「マージされた」「利用可能になった」に分解する必要がある。これは本稿の設計提案であり、根拠はGitHubのリポジトリ操作とワークフロー権限の公式仕様、およびAnthropicのoutcome評価である。出典：[GitHub Contents API](https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28)、[GitHub Actions workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)、[Anthropic Agent Evals](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)。

## 2026年までに公開されたトップ事例から、何を学べるか

### 1. モデルより先に、仕事ができる環境を設計する

OpenAIは2026年2月11日、Codexがコードを書く内部製品開発の事例を報告した。同社によると、約5か月で約1,500件のPRを少人数で作成・マージし、人間が手書きしたコードをゼロにする制約で実験した。著者は、初期の進みが予想より遅かった理由として、エージェントの実行環境や抽象化の不足を挙げている。**これはOpenAIの特定事例の自己報告であり、他の環境でも同じ生産性になることを証明しない。** 出典：[OpenAI, *Harness engineering*, 2026-02-11](https://openai.com/index/harness-engineering/)。

同記事では、リポジトリ内の知識を参照可能な正本にし、AGENTS.mdを巨大な手順書ではなく入口として使い、ログやメトリクスをエージェント自身が調査できるようにした。ここからの設計提案は、指示文を長くする前に「変更対象・テスト方法・失敗の証拠に実際にアクセスできるか」を点検することだ。出典：[OpenAI, *Harness engineering*](https://openai.com/index/harness-engineering/)。

### 2. 経験は会話ではなく、再実行できる評価へ残す

OpenAIは2026年5月12日のCookbookで、実行トレース、レビュー、評価ケース、改善案、実装引き継ぎをつなぐループを公開した。サンプルが示すのは、改善候補を作る仕組みであり、すべての候補が自動でマージされ、実環境で有効になるという証明ではない。出典：[OpenAI, *Build an Agent Improvement Loop with Traces, Evals, and Codex*, 2026-05-12](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop)。

Anthropicは2026年1月9日、現実の業務を模した評価で失敗を回帰テストへ変え、振る舞いの悪化を検出する方法を解説した。同じ不具合を再発させないため、本稿では**毎時実行で見つかった失敗を、翌時間にも走る評価ケースにする**ことを提案する。出典：[Anthropic, *Demystifying evals for AI agents*, 2026-01-09](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)。

### 3. 長時間の自律実行には、引き継ぎ可能な状態が要る

Anthropicは2025年11月26日、初回に環境を準備する役割と、各実行で小さく前進して進捗・Git履歴を残す役割を分ける実験を紹介した。実験では、未完了を完了と誤認したり、次回実行が前回の作業を推測し直したりする問題も報告された。ただし実証対象は主に同社の長時間コーディング実験であり、あらゆる自律業務への有効性は未確定である。出典：[Anthropic, *Effective harnesses for long-running agents*, 2025-11-26](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents)。

本稿で提案する引き継ぎ記録は、自然文の「完了」ではなく、対象Issue、基準コミット、変更ファイル、試験結果、残存障害、次の一手を保持すること。これはAnthropicの進捗ファイルとGit履歴による引き継ぎを、定期実行の監査に応用した設計案である。出典：[Anthropic長時間実行の原文](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents)、[GitHub Contents API](https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28)。

### 4. 最先端の加速報告を、そのまま自分たちの成果にしない

METRは2026年11月5日、Anthropicの内部モデルのAECIベンチマーク上の進歩率が2025年10月以降に**1.9倍（95%信頼区間1.5〜2.8倍）**となったと報告した。METRは同時に、この測定がベンチマークへの適合や手法の影響を受け得ること、重要な内部証拠の多くが非公開化されたことも説明している。これは**モデル能力の伸びに関する評価**であり、自分たちのGitHub自律改善の成功率、変更品質、工数削減率を測った数字ではない。出典：[METR, *Independent Assessment of AI R&D Acceleration at Anthropic in October 2026*, 2026-11-05](https://metr.org/blog/2026-11-05-anthropic-ai-rd-acceleration-assessment/)。

## 提案: 毎時実行を「成果物の状態」で管理する

本節は**提案する運用設計**であり、効果の実測ではない。評価では返答より最終状態を見るというAnthropicの方法と、GitHubの書き込み・CIの公式仕様を組み合わせる。出典：[Anthropic Agent Evals](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)、[GitHub Contents API](https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28)、[GitHub Actions workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)。

| 状態 | 必要な証拠 | 次へ進んでよい条件 |
| --- | --- | --- |
| DISCOVERED | 一次資料URL、公開日、適用対象 | 検証可能な変更仮説がある |
| IMPLEMENTED | 差分、commit SHA、対象ブランチ | 実際に変更ファイルが存在する |
| TESTED | テスト条件、結果、対象SHA | 想定失敗が再現し修正後に通る |
| REVIEWED | 評価記録、退行・費用の確認 | 採用根拠と未解決事項が見える |
| MERGED | PR URL、merge commit SHA | 対象ブランチへの反映が検証できる |
| RELEASED | 本番での確認結果または配布物の識別子 | 利用者が期待する状態が確かめられた |

表の各状態名と判定条件は、本稿が提案する規約であり、GitHubやAnthropicが標準化した状態名ではない。出典（設計上の根拠）：[GitHub Contents API](https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28)、[GitHub Actions workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)、[Anthropic Agent Evals](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)。

特に注意したいのは権限である。GitHub Actionsの`GITHUB_TOKEN`にはリポジトリやジョブの設定によって異なる権限があり、`contents: write`の設定文言だけで実際の書き込み成功を確約できない。書き込みが拒否された場合、許可の迂回ではなく、拒否理由の記録と正規の許可経路の確認へ進む。出典：[GitHub Actions workflow syntax, permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)、[GitHub REST Contents API](https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28)。

## 実測するなら、何を比較するか

以下は**未実施の実験計画**である。評価の設計根拠は実業務を再現し最終状態を測るAnthropicの方針と、トレースから評価を生成するOpenAIの例にある。サンプル数や合格基準は研究成果ではなく、この環境向けの事前登録案である。出典：[Anthropic Agent Evals](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)、[OpenAI Agent Improvement Loop](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop)。

1. 過去の再現可能な作業20件を固定し、優先度・難易度ごとに層化する。新方式と旧方式に同じ課題を割り当て、実行順を入れ替える（計画値20件は暫定、統計的妥当性は未検証）。
2. 結果は「コメントの成功宣言」ではなく、commit、対象SHAでのCI、必要ならmergeと利用者視点の確認で判定する。
3. 主要指標は**証拠付き完了率**。副指標は1件当たりの人手介入、再作業回数、試験の退行、所要時間、API・実行コスト。
4. 失敗例を固定の回帰テストへ追加し、旧方式の再現結果と新方式の結果を同時保存する。
5. 変更が性能を改善しない、重要な回帰を起こす、証拠が欠ける場合は**採用保留または棄却**とし、次回実行へ未完了状態を正確に引き継ぐ。

重要なのは、初回20件の比率を普遍的な成功率と解釈しないこと。差が小さければ実行数を増やし、信頼区間やタスク難度の偏りを報告する。これは本稿の測定上の注意であり、特定の改善量を予測する主張ではない。根拠：[Anthropic Agent Evals](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)、[METRの不確実性の開示](https://metr.org/blog/2026-11-05-anthropic-ai-rd-acceleration-assessment/)。

## 今回の公開可能性

この記事用の既存レポジトリは、READMEと編集契約で、著者固有の実測、他のプロジェクトにも持ち帰れる知見、一次資料への接地を求めている。品質設定には一次資料の最低件数や自分のGitHub証拠の最低件数もある。出典：[KAFKA2306/articles README](https://github.com/KAFKA2306/articles/blob/main/README.md)、[編集契約](https://github.com/KAFKA2306/articles/blob/main/pipeline/contracts/article.md)、[pipeline/config.json](https://github.com/KAFKA2306/articles/blob/main/pipeline/config.json)。

現段階で本稿が提示するのは、**外部事例と公開仕様に基づく実験可能な提案**までである。変更前後の自プロジェクトの同条件計測、失敗から再現テストを作った履歴、GitHubへの実反映、対象SHAでのCI、利用結果は本稿に添付していない。したがって効果実証済みの記事としては公開しない。必要な追加証拠は、対象Issue、before/after評価ログ、PR、commit SHA、CI実行URL、完成状態の観測記録である。公開保留の判断基準は：[AGENTS.md](https://github.com/KAFKA2306/articles/blob/main/AGENTS.md)、[article contract](https://github.com/KAFKA2306/articles/blob/main/pipeline/contracts/article.md)。

## 重要主張と一次資料の照合台帳

確認日はすべて**2026-11-07**。日付は資料の公開日。資料が証明しない範囲を右列に書いた。

| 重要主張 | 一次資料・公開日 | 証明していないこと |
| --- | --- | --- |
| エージェントの会話と最終状態は区別する | [Anthropic Agent Evals](https://www.anthropic.com/research/demystifying-evals-for-ai-agents), 2026-01-09 | 特定システムの完了率 |
| OpenAIのCodex中心の製品開発事例 | [OpenAI Harness engineering](https://openai.com/index/harness-engineering/), 2026-02-11 | 他社・他repoでの速度向上 |
| traces→feedback→evals→実装handoffを示す例 | [OpenAI Cookbook](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop), 2026-05-12 | 自動PRマージや本番改善の保証 |
| 長期実行はGit履歴・進捗記録で引き継ぐ | [Anthropic long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents), 2025-11-26 | 定期実行全般への普遍的な効果 |
| AECI上の加速1.9倍、95%区間1.5〜2.8倍 | [METR報告](https://metr.org/blog/2026-11-05-anthropic-ai-rd-acceleration-assessment/), 2026-11-05 | 自社開発自動化の速度・生産性 |
| GitHubの書き込みはAPIと権限で管理される | [GitHub Contents API](https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28)、[Actions syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), 更新日個別不明 | 今回の接続の書き込み権限があること |
| このレポジトリでは実体験と独自の証拠が公開条件 | [README](https://github.com/KAFKA2306/articles/blob/main/README.md)、[編集契約](https://github.com/KAFKA2306/articles/blob/main/pipeline/contracts/article.md)、[設定](https://github.com/KAFKA2306/articles/blob/main/pipeline/config.json), 現行版確認2026-11-07 | 本稿が公開品質に到達したこと |

**事実分類:** 一次資料に明示された内容は「外部公開証拠」。運用状態の表と実験設計は「筆者の提案」。自社の改善実績と稼働成否は「未検証」。提案と未検証を、実績や測定値として扱わない。この区分はレポジトリのclaim provenance規則に準拠する。出典：[AGENTS.md](https://github.com/KAFKA2306/articles/blob/main/AGENTS.md)。

## 結論

**次の一時間にすることは、さらに大きな調査ではなく、ひとつの変更に対応する証拠の鎖を最後までつなぐこと。** これはAnthropicの最終状態評価、OpenAIの改善ループ、GitHubの実際の書き込み・CIの仕組みを組み合わせた**検証待ちの提案**である。出典：[Anthropic Agent Evals](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)、[OpenAI improvement loop](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop)、[GitHub Contents API](https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28)。

