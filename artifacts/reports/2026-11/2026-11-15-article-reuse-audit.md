# 記事本文の再利用性監査 2026-11-15

52本の本文から、使う場面、用意するもの、手順や判断、結果の確かめ方を読者がたどれるか確認した。49本に不足を補い、手順と判定が記載済みの3本は維持した。
技術記事は実行例と期待値、調査や論考は照合に使う資料と判断を保留する条件を重視した。Agent Skillsの本文指針を、読者が使う記事向けに応用した。 [Agent Skills仕様](https://agentskills.io/specification#body-content)

| 記事 | 判定 | 補った手順・維持の理由 |
| --- | --- | --- |
| [UI改修で読み上げ通知や動きの軽減に必要な記述が消えたら、CIで止める](../../../articles/2026-08-13-01-accessibility-contract.md) | 更新 | 変更前のHTMLと記述を欠いたコピーで、CIが欠落を拾うか確認する |
| [何を任せられる人かが伝わるポートフォリオの作り方](../../../articles/2026-08-13-02-how-people-compress-a-person.md) | 更新 | 成果物と検証記録を開き、何を任せられるかを一例で説明する |
| [GitHubのリポジトリ一覧で、用途が分からないものを未分類にする](../../../articles/2026-08-13-03-dont-infer-domain-from-language.md) | 更新 | 用途トピックがある例と、言語しか分からない例を対照にする |
| [記事の年代別比較で、効果量と年代判定の可否を別々に記録する](../../../articles/2026-08-13-04-effect-size-is-not-a-conclusion.md) | 更新 | 比較集団と許可した用途を記録し、年代判定に渡した場合の停止を確かめる |
| [公開一覧から消えた61件目を、古いAPIの呼び出しを保ったまま表示する](../../../articles/2026-08-13-04-legacy-limit-complete-archive.md) | 更新 | 旧上限の前後3件数を、取得処理から実際の一覧まで流す |
| [共有画像をコミットで固定し、公開後もSHA-256で照合する](../../../articles/2026-08-13-05-pin-assets-commit-sha256.md) | 更新 | 元のコミットとSHA-256を記録し、公開URLから取り直して照合する |
| [ブラウザとテストで、同じPythonの計算ルールを使う](../../../articles/2026-08-13-06-python-one-source-browser.md) | 更新 | 同じ金利スナップショットで平常値とデータがない場合の画面を確認する |
| [AIで作った図の数値やCI結果を、公開前に元の記録と照合する](../../../articles/2026-08-14-01-audit-generated-image-claims.md) | 更新 | 図にある数字やCI結果を、対応する計測や実行記録と照合する |
| [YouTubeの自動投稿先を、投稿直前に3点で照合する](../../../articles/2026-08-14-02-publish-destination-guard.md) | 更新 | 投稿を呼ばず、実行の用途と設定・認証先の一致、拒否を試す |
| [CIでマニフェストを再生成し、差分が出たら失敗させる](../../../articles/2026-08-14-03-manifest-drift-gate.md) | 更新 | 二つの版と差分を使い、一覧の更新忘れを検出する例を動かす |
| [AIに独自用語と略語を増やさせない。294候補から1語だけ用語集に追加した](../../../articles/2026-08-14-04-controlled-vocabulary-promotion-gate.md) | 更新 | 読者が略語の説明を省いても同じ対象を指せるか、既存の例で確かめる |
| [AI生成文の検出ツールは、日本語で動けば結果を使えるか](../../../articles/2026-08-14-05-compatibility-is-not-validation.md) | 更新 | 対照入力を使い、対象言語と実際に担う処理を順に判定する |
| [売上上位50社の集計で、51位も記録する理由](../../../articles/2026-08-14-06-top-n-boundary-evidence.md) | 更新 | 50件と51件を入力し、採用数と順位外の境界情報を読む |
| [公開カタログに個人予定を混ぜない](../../../articles/2026-08-14-07-public-catalog-boundary.md) | 更新 | 架空の内部項目を加え、公開用の出力に含まれないことを確認する |
| [自動生成物の品質検査で、警告と公開を止める欠陥を分ける](../../../articles/2026-08-14-08-severity-aware-quality-gate.md) | 更新 | Node.jsの例で警告時の通過と重複時の停止を確認する |
| [実行IDに用途を入れて、設定と保存先の取り違えを防ぐ](../../../articles/2026-08-14-09-domain-prefixed-run-id.md) | 更新 | 実行IDと設定を照合し、別の保存先へ届く前に止まるかを試す |
| [CIを速くする前に、変更ごとに必要なテストを決める](../../../articles/2026-08-15-affected-set-is-a-contract.md) | 更新 | 比較対象のコミットを固定し、CIが必要な検査の欠落と余分を見分ける |
| [AIキャラの魅力は賢さで決まる？ VRChatのペット「ムチォ」から考える](../../../articles/2026-08-15-ai-character-intelligence-muchio.md) | 更新 | ペットの機能を一つ変え、遊んだときに起きた出来事を比べる |
| [Claude Codeに実装を任せるとき、合格条件を別に管理する](../../../articles/2026-08-15-hook-runner-is-not-policy.md) | 更新 | Issueと現在の合格条件を開き、実装の差分より先に判定ルールの差分を見る |
| [型チェックを通っても、APIから届くJSONは実行時に検証する](../../../articles/2026-08-15-runtime-validation-boundary.md) | 更新 | 正常な値と範囲外の値を、同じJSON入力口に渡す |
| [Oxlintでtscを置き換える前に、実際のリポジトリで型チェックを試す](../../../articles/2026-08-15-two-of-two-is-not-compiler-authority.md) | 更新 | 実際のCIと同じコマンド、設定、通過・失敗の対照ケースで型検査を比べる |
| [Pyreflyの設定を変えたら、型チェックで検出できた不具合が2件から5件に増えた](../../../articles/2026-08-15-type-checker-config-is-authority.md) | 更新 | 共通のサンプルを使い、型検査の違いが設定由来か確かめる |
| [AIが付けた開発用語を、一次資料で確かめて既存の言葉に戻す](../../../articles/2026-08-16-01-standard-terms-not-rigid-workflows.md) | 更新 | 呼び方と実際の操作を組にし、一次資料の用語と照合する |
| [AIに書かせた開発文書から、独自用語と略語を減らす](../../../articles/2026-08-16-ai-added-decision-cost-audit.md) | 更新 | 独自語の定義と使用箇所を集め、言い換えると消える意味を確認する |
| [AIの能力向上ペースと超知能の到来予測を分けて読む](../../../articles/2026-11-07-01-metr-takeoff-terms.md) | 更新 | 見出しと原典を開き、AIの能力指数の伸びと予測の日付を区別する |
| [AIの監視はどこで途切れたか。Anthropicの事故報告を読む](../../../articles/2026-11-07-02-ai-agent-safety-blind-spots.md) | 更新 | 定時処理を一つ選び、起動設定・依頼・ログ・成果を照合する |
| [Unityの作業を別のAIに引き継ぐためのファイル設計](../../../articles/2026-11-09-01-portable-agent-contracts.md) | 更新 | Unityのパス・GUID・合格条件から、操作結果と検証結果を照合する |
| [AIを替えるとき、作業手順と合格条件をGitで引き継ぐ設計](../../../articles/2026-11-09-portable-agent-contracts.md) | 更新 | 記事のJSONとスキーマを用意し、正しい結果と必須項目の欠落を試す |
| [キオクシアのPER2.5倍に必要な純利益と、好況後のキャッシュフロー](../../../articles/2026-11-15-01-kioxia-per-cashflow.md) | 更新 | 決算の元データと表計算の式から、現在の倍率が前提とする利益を逆算する |
| [AIが「完了しました」と言ったら、どこを見れば確かめられるか](../../../articles/2026-11-15-codex-evidence-mission.md) | 更新 | GitとPythonで公開状態の差分を再現し、判定の終了状態を読む |
| [ドラムの3Dアニメで、叩く時刻が合っても打面がずれる](../../../articles/3d-animation-contact-timing.md) | 維持 | ドラムの打点を変える入力、実行コマンド、ズレごとの出力が既にそろう |
| [METRが測ったAnthropicのAI能力指数、伸び率は従来の約2倍](../../../articles/ai-research-acceleration-metr-2026.md) | 更新 | 課題一つと既存の出力を用意し、合格条件と時間・費用をそろえて再試行する |
| [123の個人開発リポジトリで、ChatGPTに次の作業を選ばせる方法](../../../articles/chatgpt-multiproject-autonomy.md) | 更新 | Issue、PR、CI、利用時の成果を開き、次に一件だけ何を確認するか決める |
| [AI生成文の透かしを、第三者はどこまで検証できるか](../../../articles/claude-watermark-secret-key-detection.md) | 更新 | 公式文書の対象と検証手段を確認し、提供元による検証と独立検証を分ける |
| [GitHub IssueからUnityやBlenderを動かすAIに、どこまで権限を渡すか](../../../articles/codex-chatgpt-github-issue-bridge.md) | 更新 | 普段のIssueを一件選び、入力・実行範囲・成果物の一致を確認する |
| [ComfyUIのワークフロー22,213件を集め、8用途で試す候補を絞った](../../../articles/comfyui-8-missions-selection-20261107.md) | 更新 | 同じ画像で候補と既存ワークフローを動かし、生成物と時間を比べる |
| [AIで整えた書誌データを登録前に照合したら、OCRの60件中24件が重複だった](../../../articles/csv-migration-dry-run-before-write.md) | 更新 | 台帳のコピーで、追加・重複・保留の候補を本番書き込み前に照合する |
| [Nebiusの顧客前払いは、どの設備投資の100％超をカバーしたのか](../../../articles/financial-ratio-denominator-check.md) | 更新 | 決算原典と集計表を並べ、分母などを差し替えた行が落ちるか確かめる |
| [「何の差？」と聞かれる見出しをAIと直す](../../../articles/headline-reader-check.md) | 更新 | jqの検査結果を、比較対象・時系列・根拠の修正につなげる |
| [AIに同じ指示を繰り返すのをやめた。Issue駆動開発という最小運用](../../../articles/issue-driven-development.md) | 更新 | 既存不具合を一件選び、Issueに残した再現手順で修正後を確かめる |
| [VRChatのペット「ムチォ」に別のモデルを組み込む前に、何を確かめるか](../../../articles/muchio-shiroinu-body-adapter.md) | 更新 | モデルのPrefabとテスト用シーンで、接続前後の動きを比べる |
| [ChatGPTで方針を決めたあと、OpenCode Goにどの作業を任せるか](../../../articles/opencode-go-deepseek-v4-chatgpt-usage-scale.md) | 更新 | 小さな修正といつものテストを引き継ぎ、差分と失敗時の説明を読む |
| [資料の集計が856行と7,699行。比較の前に対象範囲と出所を確かめる](../../../articles/primary-source-derived-data-provenance.md) | 更新 | 旧集計と新集計の資料一覧を比較し、対象差と集計方法の差を分ける |
| [品質チェックの合否が二重になる。工程を止める条件を一か所で管理する](../../../articles/stage-specific-quality-gates.md) | 更新 | 同じ工程で二つの判定が出るか、点数や成果物を変えて確認する |
| [攻撃か、防御か。敵のHPを1だけ変えて確かめる](../../../articles/sts2-one-hp-choice-test.md) | 維持 | 同じ盤面から4分岐を再現する方法と、採点結果の読み方が既にそろう |
| [Unity MCPで作ったものの見た目と動作を、どこまで確かめられるか](../../../articles/unity-mcp-editor-boundary.md) | 更新 | 通れるべき扉を例に、画面・通常操作・対象クライアントで証拠を集める |
| [検証を通った変更だけをGitHub Pagesで公開する仕組み](../../../articles/validate-before-pages-deploy.md) | 更新 | ワークフロー定義と一回のログから、検証結果と公開後の応答をたどる |
| [動画生成AIのAPI変更に備え、絵コンテとリクエストを分ける](../../../articles/video-storyboard-ir-provider-compile.md) | 更新 | 代表カットと公式仕様を用意し、送信前にフレームや参照が残るか確かめる |
| [2024年衆院選で自公が過半数を割った後、469日で予算と法律はどう変わったか](../../../articles/vote-leverage-audit-2021-2026.md) | 更新 | 気になる政策を一つ選び、選挙結果から政府案・修正・成立・施行まで追う |
| [VRChatのペットが拾った会話と、確認済みの事実を分けて記録する](../../../articles/vrcpet-observation-source.md) | 更新 | 3行の架空ログを使い、正常2行と異常1行の検査を実行する |
| [AIが作った確認画面をEscで閉じたら、次の入力は元のボタンに届くか](../../../articles/web-dialog-keyboard-eval.md) | 維持 | Playwrightの入力・キー操作・期待するフォーカス・故障時の動作が既にそろう |
| [投資の結果を知る前に、判断の根拠と撤回条件をGitに残す](../../../articles/why-i-could-buy-the-crash.md) | 更新 | 結果前の根拠と撤回条件をコミットし、結果後に固定した版と照合する |
