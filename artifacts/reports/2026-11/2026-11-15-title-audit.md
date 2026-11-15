# 記事タイトル監査 2026-11-15

[監査時点の main](https://github.com/KAFKA2306/articles/tree/68aa6a6b58d111e7c5d96c2d9b71dacfb0193566/articles) にある記事 52 本を、本文と照合した。46 本を改稿し、6 本を維持した。

| 監査時点の設定 | 更新 | 維持 |
| --- | ---: | ---: |
| 公開設定あり | 7 | 1 |
| 下書き | 39 | 5 |

題だけで何についての話か分かるか、本文の中心に合っているか、結果の範囲や断定の強さを原稿が支えるかを、順に各0〜2点で評価した。2点はそのまま使える、1点は曖昧さや不足がある、0点は重要な対象の欠落または根拠との不一致を表す。点は原稿を照合した編集判断。読者実験による測定値ではない。

主題は、本文の導入に加え、再現例・結果・結論から判断した。数字を残す場合は対象と単位を添え、実証できていない成果は問いや設計として表現した。比較対象を明示するだけでは、根拠以上の断定を補えないと判断した。 [見出しの照合手順](../../../articles/headline-reader-check.md) · [Googleのタイトル指針](https://developers.google.com/search/docs/appearance/title-link)

| 記事 | 採否 | 元の題 | 採用した題 | 評価前→後（主題・焦点・根拠） | 判断理由 |
| --- | --- | --- | --- | --- | --- |
| [`2026-08-13-01-accessibility-contract`](../../../articles/2026-08-13-01-accessibility-contract.md) | 更新 | UIを速く作り直しても、利用者を置き去りにしない。アクセシビリティ退行をCIで止める | UI改修で読み上げ通知や動きの軽減に必要な記述が消えたら、CIで止める | 1 / 1 / 1 → 2 / 2 / 2 | grepで検査するのは読み上げ通知と動きの軽減に関する記述。利用体験全体の退行防止を約束しない。 |
| [`2026-08-13-02-how-people-compress-a-person`](../../../articles/2026-08-13-02-how-people-compress-a-person.md) | 更新・公開設定あり | 人は他人を『何を任せられるか』で圧縮する——成果物が仕事の証拠になるまで | 何を任せられる人かが伝わるポートフォリオの作り方 | 1 / 0 / 2 → 2 / 2 / 2 | 成果物から委任の可否を判断するための記載例が中心。「人を圧縮する」より対象と目的が伝わる。 |
| [`2026-08-13-03-dont-infer-domain-from-language`](../../../articles/2026-08-13-03-dont-infer-domain-from-language.md) | 更新 | 分類できないなら、無理に埋めない。unclassifiedを残した方がUIは信頼できた | GitHubのリポジトリ一覧で、用途が分からないものを未分類にする | 1 / 1 / 0 → 2 / 2 / 2 | 分類対象と選ぶ処置を明示。「信頼できた」は本文で測った結果ではない。 |
| [`2026-08-13-04-effect-size-is-not-a-conclusion`](../../../articles/2026-08-13-04-effect-size-is-not-a-conclusion.md) | 更新 | Cohen's dが0.76でも「判定できる」とは言わない。数字と利用許可を分ける | 記事の年代別比較で、効果量と年代判定の可否を別々に記録する | 1 / 1 / 1 → 2 / 2 / 2 | 2022年と2026年の探索比較。Cohen’s dの値を未知の記事の年代判定に使う根拠の強さと区別する。 |
| [`2026-08-13-04-legacy-limit-complete-archive`](../../../articles/2026-08-13-04-legacy-limit-complete-archive.md) | 更新 | APIは壊れていないのに、61件目が消える。互換性を守りながら「全部見える」を取り戻す | 公開一覧から消えた61件目を、古いAPIの呼び出しを保ったまま表示する | 2 / 1 / 2 → 2 / 2 / 2 | 61件目が見えない場所と、維持したAPIの互換性を明示。 |
| [`2026-08-13-05-pin-assets-commit-sha256`](../../../articles/2026-08-13-05-pin-assets-commit-sha256.md) | 更新 | 中央の画像を更新しても、公開サイトが勝手に変わらない。共有assetをcommitとhashで固定する | 共有画像をコミットで固定し、公開後もSHA-256で照合する | 2 / 1 / 2 → 2 / 2 / 2 | 固定する対象とデプロイ後の実ファイル照合まで読める。 |
| [`2026-08-13-06-python-one-source-browser`](../../../articles/2026-08-13-06-python-one-source-browser.md) | 更新 | 業務ロジックをUIにコピーするな。「正解」を1か所に置く設計 | ブラウザとテストで、同じPythonの計算ルールを使う | 1 / 1 / 2 → 2 / 2 / 2 | 「正解」が指すものを、両方で実行する計算処理まで具体化。 |
| [`2026-08-14-01-audit-generated-image-claims`](../../../articles/2026-08-14-01-audit-generated-image-claims.md) | 更新 | 生成AIの図に「CI成功」と書いてあった。見栄えより先に「信じてよい」を作る | AIで作った図の数値やCI結果を、公開前に元の記録と照合する | 2 / 1 / 2 → 2 / 2 / 2 | 読者の作業を数値・CI結果の原典照合として明示。 |
| [`2026-08-14-02-publish-destination-guard`](../../../articles/2026-08-14-02-publish-destination-guard.md) | 更新 | 全部成功したのに、違うチャンネルへ投稿される。その事故を3点照合で止める | YouTubeの自動投稿先を、投稿直前に3点で照合する | 1 / 1 / 1 → 2 / 2 / 2 | 実際に観測したのは設定のずれ。誤投稿が発生したように読める表現を修正。 |
| [`2026-08-14-03-manifest-drift-gate`](../../../articles/2026-08-14-03-manifest-drift-gate.md) | 更新 | CIが自分で直してからgreenになる。manifestの「更新忘れ」を差分で止める | CIでマニフェストを再生成し、差分が出たら失敗させる | 2 / 1 / 2 → 2 / 2 / 2 | 再生成後にコミットとの差分で止める手順を明示。 |
| [`2026-08-14-04-controlled-vocabulary-promotion-gate`](../../../articles/2026-08-14-04-controlled-vocabulary-promotion-gate.md) | 維持 | AIに独自用語と略語を増やさせない。294候補から1語だけ用語集に追加した | 現行題 | 2 / 2 / 2 → 2 / 2 / 2 | AI文書の独自用語と294候補から1語を選んだ事実の両方が伝わる。 |
| [`2026-08-14-05-compatibility-is-not-validation`](../../../articles/2026-08-14-05-compatibility-is-not-validation.md) | 更新・公開設定あり | OSSが動いた。でもその判定はまだ使えない。「動く」と「使ってよい」を4状態に分ける | AI生成文の検出ツールは、日本語で動けば結果を使えるか | 1 / 1 / 2 → 2 / 2 / 2 | OSSの種類と検査した言語を明示。動作確認を検出精度の確認と混同させない。 |
| [`2026-08-14-06-top-n-boundary-evidence`](../../../articles/2026-08-14-06-top-n-boundary-evidence.md) | 更新 | 『売上上位50社』を、そのまま信じなくていいようにする。51位まで証拠に残した | 売上上位50社の集計で、51位も記録する理由 | 2 / 1 / 2 → 2 / 2 / 2 | 51位を保存する工夫は具体的。ランキング全体の完全性まで約束しない。 |
| [`2026-08-14-07-public-catalog-boundary`](../../../articles/2026-08-14-07-public-catalog-boundary.md) | 維持 | 公開カタログに個人予定を混ぜない | 現行題 | 2 / 2 / 2 → 2 / 2 / 2 | 公開する場所と、混入を防ぐデータが題だけで分かる。 |
| [`2026-08-14-08-severity-aware-quality-gate`](../../../articles/2026-08-14-08-severity-aware-quality-gate.md) | 更新 | 全部をFAILにしない。品質ゲートにWARNとFAILを分ける | 自動生成物の品質検査で、警告と公開を止める欠陥を分ける | 1 / 1 / 2 → 2 / 2 / 2 | 検査対象とFAILの具体的な帰結を示す。 |
| [`2026-08-14-09-domain-prefixed-run-id`](../../../articles/2026-08-14-09-domain-prefixed-run-id.md) | 更新 | 同じ日付のrunが混ざる。run IDをdomainで区切る | 実行IDに用途を入れて、設定と保存先の取り違えを防ぐ | 1 / 1 / 1 → 2 / 2 / 2 | 日付の重複に限らない問題。何を間違って読むかを明示。 |
| [`2026-08-15-affected-set-is-a-contract`](../../../articles/2026-08-15-affected-set-is-a-contract.md) | 更新 | CIが速くなった。必要なテストを消しただけかもしれない | CIを速くする前に、変更ごとに必要なテストを決める | 2 / 1 / 2 → 2 / 2 / 2 | 本文の3ケースは検査対象の選定。速度の実測を期待させない。 |
| [`2026-08-15-ai-character-intelligence-muchio`](../../../articles/2026-08-15-ai-character-intelligence-muchio.md) | 更新・公開設定あり | AIキャラクターは、賢いほど面白いのか？――ムチォがひっくり返した「知能」の価値 | AIキャラの魅力は賢さで決まる？ VRChatのペット「ムチォ」から考える | 2 / 2 / 1 → 2 / 2 / 2 | 問いを残し、VRChatの事例の位置づけを示す。「ひっくり返した」という実証を要する表現を外す。 |
| [`2026-08-15-hook-runner-is-not-policy`](../../../articles/2026-08-15-hook-runner-is-not-policy.md) | 更新・公開設定あり | Claude Codeに全部任せるなら、合格条件だけはClaudeに任せない | Claude Codeに実装を任せるとき、合格条件を別に管理する | 2 / 2 / 1 → 2 / 2 / 2 | 「全部」を実装と検証基準の役割分担に戻す。 |
| [`2026-08-15-runtime-validation-boundary`](../../../articles/2026-08-15-runtime-validation-boundary.md) | 更新 | 型チェックはgreen。それでも壊れたJSONは通る | 型チェックを通っても、APIから届くJSONは実行時に検証する | 2 / 1 / 1 → 2 / 2 / 2 | 失敗はJSONの構文ではなく中身の型。どの境界で何を確かめるかが分かる。 |
| [`2026-08-15-two-of-two-is-not-compiler-authority`](../../../articles/2026-08-15-two-of-two-is-not-compiler-authority.md) | 更新 | Oxlintは2/2でtscと同点。それでもtscを消さなかった | Oxlintでtscを置き換える前に、実際のリポジトリで型チェックを試す | 1 / 1 / 2 → 2 / 2 / 2 | 2件の再現例しか通していないことより、次に確認すべき実リポジトリでの動作を伝える。 |
| [`2026-08-15-type-checker-config-is-authority`](../../../articles/2026-08-15-type-checker-config-is-authority.md) | 更新 | Pyreflyが2/5から5/5になった。変えたのは製品ではなく設定だけ | Pyreflyの設定を変えたら、型チェックで検出できた不具合が2件から5件に増えた | 2 / 1 / 2 → 2 / 2 / 2 | 設定変更と数字の意味を一文で明示。 |
| [`2026-08-16-01-standard-terms-not-rigid-workflows`](../../../articles/2026-08-16-01-standard-terms-not-rigid-workflows.md) | 更新 | AIの独自用語を増やさない。過去の説明ではなく、毎回一次資料を見る | AIが付けた開発用語を、一次資料で確かめて既存の言葉に戻す | 2 / 1 / 2 → 2 / 2 / 2 | 一次資料を見る目的を、GitやCIに付いた独自の別名の見直しとして示す。 |
| [`2026-08-16-ai-added-decision-cost-audit`](../../../articles/2026-08-16-ai-added-decision-cost-audit.md) | 更新・公開設定あり | AIが書いたrepositoryを読みにくくする独自用語と略語を減らす | AIに書かせた開発文書から、独自用語と略語を減らす | 1 / 1 / 2 → 2 / 2 / 2 | 監査対象をリポジトリ全体からREADME、Issueなどの開発文書へ絞る。 |
| [`2026-11-07-01-metr-takeoff-terms`](../../../articles/2026-11-07-01-metr-takeoff-terms.md) | 更新 | AI開発が2倍速でも、超知能の到来日は分からない | AIの能力向上ペースと超知能の到来予測を分けて読む | 2 / 1 / 0 → 2 / 2 / 2 | 能力指数の伸び率をAI開発全体の速度と読ませない。到来予測を読み解く記事。 |
| [`2026-11-07-02-ai-agent-safety-blind-spots`](../../../articles/2026-11-07-02-ai-agent-safety-blind-spots.md) | 更新 | AIを監視していたのに事故が起きた理由 | AIの監視はどこで途切れたか。Anthropicの事故報告を読む | 1 / 1 / 1 → 2 / 2 / 2 | 複数事例の出所と、適用漏れ・監視対象外という問題を示す。 |
| [`2026-11-09-01-portable-agent-contracts`](../../../articles/2026-11-09-01-portable-agent-contracts.md) | 更新 | AIエージェントを替えても作業を引き継げるか | Unityの作業を別のAIに引き継ぐためのファイル設計 | 1 / 1 / 2 → 2 / 2 / 2 | Unity事例に基づくファイル構成案。引き継ぎ成功の実証を約束しない。 |
| [`2026-11-09-portable-agent-contracts`](../../../articles/2026-11-09-portable-agent-contracts.md) | 更新 | AIを替えるたびに同じ指示を書かない。作業契約をGitで共有する設計 | AIを替えるとき、作業手順と合格条件をGitで引き継ぐ設計 | 2 / 1 / 2 → 2 / 2 / 2 | 作業契約の中身を明示し、Unityの具体設計を扱う記事と焦点を区別する。 |
| [`2026-11-15-01-kioxia-per-cashflow`](../../../articles/2026-11-15-01-kioxia-per-cashflow.md) | 更新 | キオクシアのPER2.5倍には、次の四半期にいくら必要か | キオクシアのPER2.5倍に必要な純利益と、好況後のキャッシュフロー | 1 / 1 / 2 → 2 / 2 / 2 | 「次の四半期にいくら」が指す純利益と、本文後半のキャッシュフローの試算を題に含める。 |
| [`2026-11-15-codex-evidence-mission`](../../../articles/2026-11-15-codex-evidence-mission.md) | 維持 | AIが「完了しました」と言ったら、どこを見れば確かめられるか | 現行題 | 2 / 2 / 2 → 2 / 2 / 2 | AIの完了報告をどこで確かめるかという問いが、公開用ブランチの例と仕事別の確認方法に合う。 |
| [`3d-animation-contact-timing`](../../../articles/3d-animation-contact-timing.md) | 更新 | ドラムの3Dアニメで、音は合うのに叩く場所が違う | ドラムの3Dアニメで、叩く時刻が合っても打面がずれる | 2 / 2 / 1 → 2 / 2 / 2 | 実験で比較したのはGLBの時刻と接触位置。音源そのものの比較と混同させない。 |
| [`ai-research-acceleration-metr-2026`](../../../articles/ai-research-acceleration-metr-2026.md) | 更新 | AI開発はもう人間だけの仕事ではない。Anthropicの進歩が約2倍に加速した | METRが測ったAnthropicのAI能力指数、伸び率は従来の約2倍 | 1 / 1 / 0 → 2 / 2 / 2 | 報告書で計測した指数の傾きに主張を絞る。個人の自己申告や因果寄与とは区別する。 |
| [`chatgpt-multiproject-autonomy`](../../../articles/chatgpt-multiproject-autonomy.md) | 更新・公開設定あり | 個人開発が123個になって分かった。ChatGPTに任せるべきはコードより「次の1件」だった | 123の個人開発リポジトリで、ChatGPTに次の作業を選ばせる方法 | 1 / 1 / 2 → 2 / 2 / 2 | 123の単位と、コードを書く前に任せた判断を特定。 |
| [`claude-watermark-secret-key-detection`](../../../articles/claude-watermark-secret-key-detection.md) | 更新・公開設定あり | AIの文章に「透かし」があると言われたら、誰がそれを証明できるのか | AI生成文の透かしを、第三者はどこまで検証できるか | 2 / 2 / 1 → 2 / 2 / 2 | 透かしの検出・検証と、著者や由来の断定を一つにまとめない。 |
| [`codex-chatgpt-github-issue-bridge`](../../../articles/codex-chatgpt-github-issue-bridge.md) | 更新 | GitHub IssueからAIにローカルPCを任せてよいのか？ Unity・Blender・動画生成で考える安全な橋 | GitHub IssueからUnityやBlenderを動かすAIに、どこまで権限を渡すか | 2 / 1 / 2 → 2 / 2 / 2 | 「安全な橋」が指す問題をローカル環境の実行権限に戻す。冒頭の題も同期。 |
| [`comfyui-8-missions-selection-20261107`](../../../articles/comfyui-8-missions-selection-20261107.md) | 更新 | 22,213件集めても「最良」とは言えなかった：ComfyUIの8用途別Workflow選定結果 | ComfyUIのワークフロー22,213件を集め、8用途で試す候補を絞った | 2 / 1 / 2 → 2 / 2 / 2 | 収集・選定の結果と書き、40枠の実機未検証の状態に合わせる。 |
| [`csv-migration-dry-run-before-write`](../../../articles/csv-migration-dry-run-before-write.md) | 更新 | LLMで雑データを整えると、なぜ壊れる？ 455件→414件、60件中24件を止めた実例 | AIで整えた書誌データを登録前に照合したら、OCRの60件中24件が重複だった | 1 / 1 / 1 → 2 / 2 / 2 | 対象が不明な二組の数字をやめ、検出対象と登録前の処置を明示。 |
| [`financial-ratio-denominator-check`](../../../articles/financial-ratio-denominator-check.md) | 更新 | 決算の「前払い100％」を、会社全体の数字と取り違えないために | Nebiusの顧客前払いは、どの設備投資の100％超をカバーしたのか | 2 / 1 / 1 → 2 / 2 / 2 | 100％超の分母は一定の新規契約に対応する設備投資。会社名と条件を題で復元できる。 |
| [`headline-reader-check`](../../../articles/headline-reader-check.md) | 維持 | 「何の差？」と聞かれる見出しをAIと直す | 現行題 | 2 / 2 / 2 → 2 / 2 / 2 | 曖昧な比較をAIと直す実例が導入にあり、題が編集作業を具体的に予告する。 |
| [`issue-driven-development`](../../../articles/issue-driven-development.md) | 維持・公開設定あり | AIに同じ指示を繰り返すのをやめた。Issue駆動開発という最小運用 | 現行題 | 2 / 2 / 2 → 2 / 2 / 2 | 同じ指示を繰り返す摩擦と、Issueを使う解決策が一読で分かる。 |
| [`muchio-shiroinu-body-adapter`](../../../articles/muchio-shiroinu-body-adapter.md) | 更新 | 「モデル差し替え」を作ろうとしたら、公式説明の1行で設計が変わった | VRChatのペット「ムチォ」に別のモデルを組み込む前に、何を確かめるか | 1 / 1 / 2 → 2 / 2 / 2 | 対象と作業を明示し、Prefabでの確認前の設計として示す。冒頭の題も同期。 |
| [`opencode-go-deepseek-v4-chatgpt-usage-scale`](../../../articles/opencode-go-deepseek-v4-chatgpt-usage-scale.md) | 更新 | ChatGPTを使い倒している私に、月10ドルのOpenCode Goが刺さった理由 | ChatGPTで方針を決めたあと、OpenCode Goにどの作業を任せるか | 2 / 1 / 1 → 2 / 2 / 2 | 記事はローカル作業の分担案。価格と主観的な評価を入口から外す。 |
| [`primary-source-derived-data-provenance`](../../../articles/primary-source-derived-data-provenance.md) | 更新 | 856件が7,699件になっても、分析の信頼を失わないために残したもの | 資料の集計が856行と7,699行。比較の前に対象範囲と出所を確かめる | 1 / 1 / 2 → 2 / 2 / 2 | 単位と何を保存するかを示す。2つの集計が同一母集団だったように読ませない。 |
| [`stage-specific-quality-gates`](../../../articles/stage-specific-quality-gates.md) | 更新 | 同じ品質条件を2回判定しない。AI時代の品質ゲートは「追加」より「一本化」する | 品質チェックの合否が二重になる。工程を止める条件を一か所で管理する | 2 / 1 / 1 → 2 / 2 / 2 | 一本化するのは停止条件の判断。工程別の検査をやめる話ではない。 |
| [`sts2-one-hp-choice-test`](../../../articles/sts2-one-hp-choice-test.md) | 維持 | 攻撃か、防御か。敵のHPを1だけ変えて確かめる | 現行題 | 2 / 2 / 2 → 2 / 2 / 2 | 攻撃と防御、敵のHPを1だけ変える検査方法が題だけで分かる。 |
| [`unity-mcp-editor-boundary`](../../../articles/unity-mcp-editor-boundary.md) | 更新 | 2026年、Unity MCPはどこまで実用か――14件で見えた『作れるが、見た目と挙動を監査し切れない』壁 | Unity MCPで作ったものの見た目と動作を、どこまで確かめられるか | 2 / 1 / 2 → 2 / 2 / 2 | 実用の意味を見た目・動作の検証へ。ゲーム以外の素材も射程に収める。冒頭の題も同期。 |
| [`validate-before-pages-deploy`](../../../articles/validate-before-pages-deploy.md) | 更新 | 速く出すために、勝手に出さない。GitHubとShopifyに学ぶRelease Engineering | 検証を通った変更だけをGitHub Pagesで公開する仕組み | 1 / 1 / 2 → 2 / 2 / 2 | 事例の実装と読者が持ち帰る公開設計を明示。 |
| [`video-storyboard-ir-provider-compile`](../../../articles/video-storyboard-ir-provider-compile.md) | 更新 | 生成AIのAPI仕様が変わっても、映像の意図まで書き直さない。Storyboardを正準にする | 動画生成AIのAPI変更に備え、絵コンテとリクエストを分ける | 2 / 1 / 2 → 2 / 2 / 2 | 映像の意図とAPI仕様を分ける設計を、絵コンテとリクエストという具体的な対象で伝える。 |
| [`vote-leverage-audit-2021-2026`](../../../articles/vote-leverage-audit-2021-2026.md) | 更新 | 自公を過半数割れにして、469日で何が変わった？――2024年衆院選を予算と法律で答え合わせする | 2024年衆院選で自公が過半数を割った後、469日で予算と法律はどう変わったか | 2 / 2 / 1 → 2 / 2 / 2 | 時系列の照合と投票の因果的な評価を混同させない。 |
| [`vrcpet-observation-source`](../../../articles/vrcpet-observation-source.md) | 更新 | ペットが聞いた会話を、そのまま『記憶』にしてはいけない：壊れた1行から観測と事実を分ける | VRChatのペットが拾った会話と、確認済みの事実を分けて記録する | 1 / 1 / 2 → 2 / 2 / 2 | ペットと記録の仕組みを明示。会話ログと確認済み事実で証拠の強さが異なる。 |
| [`web-dialog-keyboard-eval`](../../../articles/web-dialog-keyboard-eval.md) | 更新 | AIが作った確認画面、閉じたあとにどこへ戻る？ | AIが作った確認画面をEscで閉じたら、次の入力は元のボタンに届くか | 2 / 1 / 2 → 2 / 2 / 2 | 何を閉じ、何がどこへ戻るのかを題だけで特定。 |
| [`why-i-could-buy-the-crash`](../../../articles/why-i-could-buy-the-crash.md) | 更新 | 第二の脳の次に必要なのは「意思決定のGit」だ——投資判断を後知恵バイアスから守る | 投資の結果を知る前に、判断の根拠と撤回条件をGitに残す | 1 / 1 / 1 → 2 / 2 / 2 | 「第二の脳」の前提知識を省き、後から検証可能にする記録項目を示す。 |

作業範囲は main の記事タイトル。題を本文冒頭にも置く3本では、同じ題にそろえた。本文の主張と引用の更新、テーマが重なる記事の統合、Zenn本番への反映は別工程。
