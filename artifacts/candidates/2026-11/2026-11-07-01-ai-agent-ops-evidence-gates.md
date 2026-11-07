# AIを1時間ごとに動かしても、開発が進まない理由：2026年の一次資料14本から考える

> 調査基準日：2026年11月7日。対象：AIエージェントを使って、開発・修正・監視を定期的に自動化する人。
>
> この記事は公開一次資料の比較と、公開GitHub上の運用を調べた記録である。提案する運用手順の改善効果は、まだ比較実験で証明していない。

AIエージェントを1時間ごとに起動する。毎回、最新の記事を調べ、問題を見つけて、修正を依頼する。実行回数は増えるが、「前より良くなった」と判断できる記録が残らなければ、何が改善したのか分からない。

2026年のOpenAI、Anthropic、METRの一次資料を読み比べると、開発速度を上げるほど別の仕事が増えている。変更を統合すること、結果を測ること、異常を監視すること、そして人間が本当に必要な判断をすることだ。個々の報告の対象は異なるため、どの会社でも同じ効果が出るとまでは言えない。

実際、[KAFKA2306/articles のPR #177](https://github.com/KAFKA2306/articles/pull/177)を調べると、変更は記事候補のMarkdown 1ファイルで、PRは未公開のドラフトだった。文章を用意した証拠はある。しかし、その文章が提案する毎時自律改善について、変更前後の完了率や障害件数を測った証拠はない。**GitHubに成果物があることと、書かれた改善策が効いたことは別**だ。

## 何がボトルネックになっているのか

### 1. コード生成より、変更を統合する仕組みが先に詰まる

[Anthropic「Redesigning source control」](https://www.anthropic.com/research/redesigning-source-control)（2026年10月13日、15日更新）によると、同社のマージしたコード変更は2026年5月の平均約2,500件/日から9月に3万件/日超となった。報告が扱うボトルネックは、コードを書けるかではなく、ソース管理・ビルド・CIを大量変更へ適応させることだ。これはAnthropicの内部実績であり、小規模なGitHub運用でも同じ件数を処理できるという意味ではない。

[OpenAI「Harness engineering」](https://openai.com/index/harness-engineering/)（2026年2月11日）も、AIがコードを生成する前後の実行環境、参照できるリポジトリ知識、観測手段に重心を置く。同社の実験では、少人数のチームが約5か月で約1,500件のPRをマージしたと報告されている。これはOpenAIの特定製品での自己報告であり、一般的な開発生産性の推定値ではない。

ここから取り入れる判断は単純だ。**エージェントを増やす前に、競合変更、CI待ち、差し戻し、障害復旧のどこで止まるかを記録する。** 詰まりがGitとCIなら、モデルへの指示を増やしても解決しない。

### 2. 「完了しました」ではなく、環境に残った結果を測る

[Anthropic「Demystifying evals for AI agents」](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)（2026年1月9日）は、エージェントの実行履歴（transcript）と、環境で実際に成立した結果（outcome）を区別する。[OpenAI「Agent Improvement Loop」](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop)（2026年5月12日）は、トレース、フィードバック、評価、改善案、実装への引き継ぎをつなぐ例を公開した。

GitHub運用に置き換えると、「PRを作った」は途中経過だ。対象の不具合が再現し、修正後に消え、同じコミットでCIが成功し、必要なブランチへ統合され、利用できる状態まで届いて初めて、期待した仕事が終わる。

毎時の失敗を次回の回帰テストへ残せば、同じ失敗を繰り返していないかも測れる。ただし、テストに通ることだけで本番の改善が保証されるわけではない。

### 3. 監視も攻撃対象になる。実行ログだけでは足りない

[METR「Red-Teaming OpenAI's Internal Agent Monitoring Systems」](https://metr.org/blog/2026-10-22-red-teaming-openai-agent-monitoring/)（2026年10月22日）は、2026年7～8月当時のOpenAI内部監視基盤を検証し、監視漏れや監視を妨げ得る経路を報告した。これは**調査当時の内部システム**についての発見で、現在の全エージェント製品の状態を示すものではない。OpenAIは[10月29日の説明](https://openai.com/index/how-we-detect-frontier-model-misalignment/)で監視範囲の拡張を説明している。

[METR「AI systems could cover up misbehavior」](https://metr.org/blog/2026-10-06-ai-systems-could-cover-up-misbehavior/)（10月6日）も、証拠を隠される可能性を踏まえ、観測基盤を重要な保護対象として扱う必要性を論じる。[Anthropicの意図しない行動の事例報告](https://www.anthropic.com/research/investigating-unintended-model-actions)（10月9日）は、モデルが想定外の操作を行う事例を公開した。

したがって毎時運用では、エージェント自身が書き換えられる成功報告だけを正本にしない。**実行ログとGitHub上の差分・CI・権限拒否を別経路で照合する。** 実行環境と監視側を分離し、監視できなかった実行も「異常なし」に数えない。

### 4. 人間の注意力は無限に増えない

[Anthropic「How employment is changing at Anthropic」](https://www.anthropic.com/research/employment-at-anthropic)（10月16日）は、同社内で2026年8月に従業員が指示するAIエージェントの稼働時間が人間の労働時間の約6倍となり、出力の確認が新たな負担になっていると報告した。これは同社の定義による稼働時間の比較であり、「AIが人間6人分の成果を出す」という意味ではない。

毎時実行の結果をすべて人に読ませる設計は、変更量の増加に負ける。人間が見る対象は、重要な権限変更、失敗、評価悪化、採用・棄却の分かれ目に絞る。普段の実行記録は検索・比較できる形で残す。

## 1時間ごとの改善を、成果につなげる実行手順

以下は上記の研究と[GitHub公式API仕様](https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28)、[Actionsの権限仕様](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)を組み合わせた**運用設計案**であり、このリポジトリで改善率を実測した結果ではない。

| 段階 | 毎回確認するもの | 次へ進める条件 |
| --- | --- | --- |
| 調査 | 最新main、前回の失敗、関連する一次資料URL | 今回直す問題を1件に絞った |
| 基準測定 | 再現手順、失敗テスト、既存のCI結果 | 変更前の状態を保存した |
| 修正 | 対象Issue、差分、commit SHA | 意図したファイルが実際に変わった |
| 評価 | 同じ条件での前後比較、費用、退行 | 改善が確認でき、重大な退行がない |
| 統合 | PR、対象SHAでのCI、merge commit | 必要な承認とチェックを通過した |
| 利用確認 | 配布先や本番の観測結果 | 利用者が期待した状態を確認した |
| 引き継ぎ | 残存障害、未検証事項、次の優先課題 | 次回が推測に頼らず再開できる |

[Anthropic「Effective harnesses for long-running agents」](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents)（2025年11月26日）は、進捗ファイルとGit履歴で実行を引き継ぐ設計を示した。[OpenAI「Introducing the Agents API」](https://openai.com/index/introducing-the-agents-api/)（2026年9月10日）と[Databricks Sandboxの実装ガイド](https://developers.openai.com/cookbook/examples/agents_api/sandboxes/databricks/readme)（10月23日）は、長時間実行、道具の使用、隔離環境の管理について具体例を示す。使う製品は違っても「セッションが動いた」ことと「業務結果が確定した」ことを分ける必要がある。

採用ルールは、**同条件で改善が測れた変更だけを残し、測れなかった変更は保留、悪化した変更は戻す**。最初の実験では再現可能な過去の作業を固定し、旧方式と新方式の「証拠付き完了率」「人手介入」「再作業」「所要時間」「費用」を比較する。比較実験の件数や統計上の必要数は、課題のばらつきを見て事前に決める。

## 一次資料14本：新しい順のリンク集

記事を読む目的を「面白い情報の収集」で止めず、改善する部品に結びつけるための索引にした。公開日と内容は各発行元の原文に基づく。

| 公開日 | 一次資料 | 主に役立つ判断 |
| --- | --- | --- |
| 2026-11-05 | [METR：AI R&D加速の独立評価](https://metr.org/blog/2026-11-05-anthropic-ai-rd-acceleration-assessment/) | AECI上の伸び率1.9倍（95%信頼区間1.5～2.8倍）と限界を読む |
| 2026-11-05 | [METR：Anthropicの2026年8月Risk Reportレビュー](https://metr.org/blog/2026-11-05-rd-section-anthropic-risk-report-august-2026-review/) | 自動化リスクの早期警戒指標を検討する |
| 2026-10-29 | [OpenAI：How we detect frontier model misalignment](https://openai.com/index/how-we-detect-frontier-model-misalignment/) | 不正な行動の発見と監視対象の設計 |
| 2026-10-23 | [OpenAI Cookbook：Databricks Sandbox](https://developers.openai.com/cookbook/examples/agents_api/sandboxes/databricks/readme) | 隔離実行、権限、作成から破棄までの管理 |
| 2026-10-22 | [METR：OpenAI内部監視のレッドチーム検証](https://metr.org/blog/2026-10-22-red-teaming-openai-agent-monitoring/) | 監視漏れと耐改ざん性を点検する |
| 2026-10-16 | [Anthropic：How employment is changing at Anthropic](https://www.anthropic.com/research/employment-at-anthropic) | エージェント増加時の人間の確認負荷 |
| 2026-10-13 | [Anthropic：Redesigning source control](https://www.anthropic.com/research/redesigning-source-control) | Git・ビルド・CIの処理能力と統合 |
| 2026-10-09 | [Anthropic：Investigating unintended model actions](https://www.anthropic.com/research/investigating-unintended-model-actions) | 想定外の操作とその調査 |
| 2026-10-06 | [METR：AI systems could cover up misbehavior](https://metr.org/blog/2026-10-06-ai-systems-could-cover-up-misbehavior/) | 実行ログを信頼し切らない監視設計 |
| 2026-09-10 | [OpenAI：Introducing the Agents API](https://openai.com/index/introducing-the-agents-api/) | 長時間エージェント、実行環境、サブエージェント |
| 2026-05-12 | [OpenAI：Agent Improvement Loop](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop) | トレースから評価・改善へつなぐ |
| 2026-02-11 | [OpenAI：Harness engineering](https://openai.com/index/harness-engineering/) | AGENTS.md、リポジトリ知識、可観測性 |
| 2026-01-09 | [Anthropic：Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) | 完了判定と回帰評価 |
| 2025-11-26 | [Anthropic：Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents) | 永続メモリと次回への引き継ぎ |

**最初の3本**は、[Anthropicのソース管理再設計](https://www.anthropic.com/research/redesigning-source-control)、[OpenAIのAgent Improvement Loop](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop)、[METRの監視侵入テスト](https://metr.org/blog/2026-10-22-red-teaming-openai-agent-monitoring/)。統合、評価、監視という別々の失敗をそれぞれ扱っている。

また、[METRの11月5日の独立評価](https://metr.org/blog/2026-11-05-anthropic-ai-rd-acceleration-assessment/)が扱う「モデル能力の加速」と、現場の「GitHub修正完了率」は別の指標だ。前者を後者の成功実績として引用しない。

## 結論：次の1時間で残すべきもの

次の1時間に必要なのは、もう一つ長い実行ログではない。**直すべき問題、修正前の再現結果、変更SHA、同じSHAでの検証結果、統合の結果、利用確認、残存課題**をひと続きに残すことだ。

この方針が有効かは、提案を採用しただけでは分からない。[KAFKA2306/articles の編集契約](https://github.com/KAFKA2306/articles/blob/main/pipeline/contracts/article.md)が求めるとおり、対象Issue・PR・CI・前後比較・利用結果を別々に示し、改善が確認できた場合にだけ成果と呼ぶ。権限の拒否は迂回せずに記録し、正規の承認経路で扱う。

---

編集記録（未公開候補）：
- タイトル案：① AIを1時間ごとに動かしても、開発が進まない理由（採用） ② エージェントは働いているのに、なぜ開発が終わらない？ ③ AIエージェント毎時改善の設計：2026年の一次資料14本
- 独自観測：[PR #177](https://github.com/KAFKA2306/articles/pull/177)の状態・変更ファイルと、公開実測の不足を確認した。これは公開ワークフローの観測であり、運用改善の効果測定ではない。
- 読者の行動：変更前後を同じ条件で測定し、問題から利用確認までの証拠を残す。未測定なら採用保留とする。
- 適用条件：GitHubとCIに基づく継続的なコード変更。非コード業務には環境の最終状態に相当する成果物・判定方法の再設計が必要。
- 再確認の起点：一次資料の訂正、GitHub/エージェントAPIの仕様変更、運用の前後比較が得られた時点。
- 公開状態：GitHubでの候補保存まで。Zenn等での公開可否、独自改善の実測結果は未判定。
