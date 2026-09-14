<!-- pipeline_meta: {"idea_source": "public-github", "evaluation_kind": "internal_lapras_rubric_proxy", "editorial_evaluation_kind": "story_interest_proxy", "topic_selection": {"selected": {"title": "公開証跡が消えると、見えない失敗が残る", "title_options": {"general_problem": "公開証跡が消えると、見えない失敗が残る", "concrete_anomaly": "current mainでHAOLANの公開証跡が消え、書き出し先を閉じる修正が必要になった", "searchable": "公開証跡が消えるとき、ページ証跡と書き出し境界はどう守るか"}, "central_question": "なぜ『公開ページが更新された』と言い切れるのに、main上で証跡だけ消えるのか？", "surprising_finding": "image2outfitは「Restore HAOLAN Pages evidence on current main」と「fail-closed undeclared stage filesystem writes」を直近で入れており、公開済みの証拠までもが失われうることが、リポジトリの直近履歴で明白になっている。", "initial_hypothesis": "公開された成果物は自動的に現在のmainに反映され、現状のartifactがそのまま真実の証拠になると考えていた。", "hypothesis_update": "直近のコミットは「証跡を復元する」と「書き出し先をfail-closeにする」を別々に入れており、証拠は自然に残るのではなく、明示的な保存と境界の設計が必要だと分かった。", "stakes": "公開前提が崩れると、誰が『動いている』かの判断が変わり、依存先が誤った成果物を信じて意思決定してしまう。", "story_type": "anomaly", "evidence_urls": ["https://github.com/KAFKA2306/image2outfit", "https://github.com/KAFKA2306/image2outfit/commit/f4a27e20ec603a7154fc2e0497a8078dee0cc8a2", "https://github.com/KAFKA2306/image2outfit/commit/c9ef37340a4a489f1ccb90d23d0def3dbc773e26"], "why_interesting": "この題材は「デプロイが成功したか」ではなく、「その成功を証明する公開証跡が存在しているか」という前提の崩れを扱う。一般的なCIの話ではなく、成果物そのものが見えなくなる現象が直近コミットで修正されている。", "technical_payoff": "一般化すると、証跡は自動生成で済ますのではなく、materializationとwrite boundaryを明示する設計が必要になる。『動いている』と『証拠として残っている』は別の責務だ。", "reader_before": "公開サイトや成果物の状態が今のmainで本当に再現されているかを見極められず、出した判断が『成功した』ままなのに裏付けが弱いと感じている。", "reader_after": "公開証跡の保存条件と書き出し制約を前提に、成果物の信頼性を判断できるようになる。『表示された』だけでなく『再現可能な証跡として残っているか』を見られる。", "design_philosophy": "読者価値を守るため、記事では成果物の見た目よりも『証跡が残る条件』を優先する。見栄えのいい成功ログや単一の画面表示を捨て、最終的に再現可能な公開証跡を選ぶ。技術stackの列挙は避け、証跡保存の条件と境界を最優先にする。", "why_this_article": "一般tutorialや公式docsでは得られないのは、直近の公開リポジトリで『証跡の復元』と『書き出し境界の強制』が同時に必要になった事実自体だ。実測の観点から、成功の宣言だけではなく失われた証跡の修復が必要だった。", "proof_of_value": "PUBLIC_GITHUB_SIGNALSには、「Restore HAOLAN Pages evidence on current main (#510)」と「fail-closed undeclared stage filesystem writes (#444)」が明示されており、単なる設定ミスではなく、公開証跡そのものが失われうる実装上の現象が確認できる。", "desired_reader_action": "公開前に『証跡が残るか』と『書き出し先が閉じているか』を最低限の確認項目に入れて、成果物の表示だけで完了扱いしない。", "non_goal": "この記事は『どのデプロイツールがよいか』や『Pagesの使い方』を解説しない。証跡の消失と境界の設計が起こりうること、その判断をどう設計に落とすかに焦点を当てる。"}, "alternatives": [{"title": "音が止まったとき、どこまでが証拠なのか", "title_options": {"general_problem": "証拠のある音が、なぜ検証できないのか", "concrete_anomaly": "blockout audioが機械判定されるまで、検証の最終段階が崩れていた", "searchable": "音声検証の証跡を自動判定できないとき、どこで失われるか"}, "central_question": "なぜ『音が止まった』という主張がそのまま証拠にならず、検証器の最終化が必要になったのか？", "surprising_finding": "vrmineは「feat(world): make blockout audio machine-verifiable」と「Harden verifier evidence finalization」を直近で入れており、音声の最終判定が人手依存の証拠から機械再現の証跡へ切り替わっている。", "initial_hypothesis": "音が止まったことは実装側の出力にそのまま表れるので、検証器の強さはそのまま信用できる。", "hypothesis_update": "直近コミットが『machine-verifiable』と『evidence finalization』を明示しているため、音声検証の真価は表示の確認ではなく再現可能な証跡にあると理解が変わる。", "stakes": "VRや音声の品質が曖昧なままだと、改善や失敗の判定が場当たり的になり、再現性のない運用判断が増える。", "story_type": "counterintuitive-result", "evidence_urls": ["https://github.com/KAFKA2306/vrmine", "https://github.com/KAFKA2306/vrmine/commit/2fe26be8eb302439a7718c30d2037c052e7c36be", "https://github.com/KAFKA2306/vrmine/commit/7e3452e09295abb63120e62527c118dfa1e15a14", "https://github.com/KAFKA2306/vrmine/commit/0b9a84ec4be1972c85009ad367cb4f86e9d37c42"], "why_interesting": "音声の「止まった」状態は一見明快だが、そこに証跡と再現性の境界がある。技術的な音声理論ではなく、検証の最後の一歩が問題になる。", "technical_payoff": "一般化すると、最終出力の判断は人の記憶ではなく再現可能な証跡の最終化が必要である。『見えた』より『再現できる』が最重要になる。", "reader_before": "「音が止まった」こと自体は分かるが、いつ、どこで、どの条件で正しく止まったと認めるのかが曖昧で、運用基準が揺れている。", "reader_after": "音声・イベントの成功条件を『目視確認』から『再現可能な証跡』への基準に切り替えられる。判断の境界が明確になり、同じ失敗を再現しやすくなる。", "design_philosophy": "説明の明快さよりも、最終判定の再現条件を優先する。瞬間的な手元確認を捨て、常に証跡を最終化する設計を選ぶ。", "why_this_article": "一般tutorialでは得られないのは、リポジトリが『make blockout audio machine-verifiable』と『evidence finalization』を同じ時期に書き換えた事実だ。単なる実装ではなく、検証の終点そのものが変わった。", "proof_of_value": "PUBLIC_GITHUB_SIGNALSの直近3コミットが、それぞれ『make blockout audio machine-verifiable』『Harden verifier evidence finalization』『add reproducible VRMine verification flow』と明示しており、検証の再現性と証跡強化が実装の中心になっている。", "desired_reader_action": "自分の成果物が「見えた」が正しいと扱っている場合、最後の証跡を再現可能にする基準を一つ決めて、意思決定に入れる。", "non_goal": "この記事はVR音声の理論解説や実装手順を目的にしない。証跡の最終化がどのように判断の質を変えるかに焦点を当てる。"}, {"title": "検索できると、正しいと言えるわけではない", "title_options": {"general_problem": "検索できると、見つけたものを頼ってよいのか", "concrete_anomaly": "イベントページが検索できるようになった直後に、Yahoo queryのアブレーションとLLM review queueの更新が重なった", "searchable": "検索可能なイベントページは、正しいイベントの証明になるか"}, "central_question": "なぜ『検索で見つかる』と『正しく見えている』が別物なのか？", "surprising_finding": "cast_event_calは「chore: refresh searchable event pages」「chore: refresh Yahoo query ablation」「chore: refresh Yahoo LLM review queue」を同じ期間に続けており、探索の層と内容の判断の層を別々に再設計している。", "initial_hypothesis": "検索可能なページができれば、イベントの発見と妥当性は同時に解決される。", "hypothesis_update": "検索インデックスだけでなく、Yahoo queryの検証とLLMによるレビューの再評価まで更新されているため、検索可能性は最初の一歩であり、妥当性は別の検証が必要だと変わる。", "stakes": "イベントの見つけやすさが上がっても、誤った説明や誤った検索条件が残ると意思決定に混乱が起きる。", "story_type": "contradiction", "evidence_urls": ["https://github.com/KAFKA2306/cast_event_cal", "https://github.com/KAFKA2306/cast_event_cal/commit/b772ed0a0535f4c9db42b9902d211ebc5b3c87c1", "https://github.com/KAFKA2306/cast_event_cal/commit/f75a6680b4937ecc21a52ae040da95597914d92d", "https://github.com/KAFKA2306/cast_event_cal/commit/ce045b41e81c40485b40173d7baafa654f31b5cd"], "why_interesting": "検索の本体と承認の層が別々に更新されているのは、検索性が単独の成功条件ではないことの証拠である。見つかることと『見つけてよい』ことが分離している。", "technical_payoff": "一般化すると、検索性能とデータ妥当性は別の指標にすべきで、これは発見経路とレビュー経路を分ける設計の原則になる。", "reader_before": "イベント一覧が見つかりやすくなったと感じていても、結果が誤ってないかを判断できず、検索の正しさに過剰に期待している。", "reader_after": "検索しやすさと適切さを区別して、どこでレビューが必要かを判断できる。発見の手間ではなく、妥当性を確認する型を持てる。", "design_philosophy": "読みやすさよりも、検索の妥当性とレビューの条件を優先する。データの登場順や見つけやすさを超え、最後に結果が正しかったかを明示する。", "why_this_article": "公開リポジトリで「searchable event pages」「Yahoo query ablation」「LLM review queue」が同時に更新されているのは、表面的な検索性能よりもレビュー経路の再設計が重要だったからだ。一般的な検索tipsでは再現できない実運用の判断がここにある。", "proof_of_value": "PUBLIC_GITHUB_SIGNALSでは、イベントページ検索の更新とYahoo queryの比較、LLMレビューの更新が同じリポジトリ内で連続して行われており、検索の成功が単独で成立しないことが公的に確認できる。", "desired_reader_action": "検索可能性だけを達成したら、その結果をどこで人間またはレビュー層が確認するかを設計に落とす。", "non_goal": "この記事は検索エンジンの実装やAPIの比較をしない。『見つかる』と『正しい』が別物であるかを立証することに限定する。"}, {"title": "同じ品揃えを更新するほど、前提も変わる", "title_options": {"general_problem": "同じ資料を見ても、日付が変わると意味が変わる", "concrete_anomaly": "BOOTHの観測データが3回連続で更新され、同じカテゴリでも前提が揺れていた", "searchable": "観測データを更新し続けるとき、何を静的に扱うか"}, "central_question": "なぜ同じカテゴリの品揃えを何度も更新しても、前提が変わり続けるのか？", "surprising_finding": "boothitemmanagerは「chore(catalog): refresh BOOTH observations」を連続して3回入れており、観測データ自体が静的な事実ではなく、更新のたびに前提が変わる可変データだった。", "initial_hypothesis": "商品の観測は比較対象として固定され、更新は単なるデータのリフレッシュに過ぎない。", "hypothesis_update": "同一リポジトリで同じ更新文が3回続いているため、観測データは一度で確定するのではなく、観察時点を明示しないと比較が成立しないと変わる。", "stakes": "固定された前提で売れ行きを比較すると、誤った棚卸や誤った選定が起きる。", "story_type": "magnitude", "evidence_urls": ["https://github.com/KAFKA2306/boothitemmanager", "https://github.com/KAFKA2306/boothitemmanager/commit/7531fe251c29462296d50486ca995c9347171cb5", "https://github.com/KAFKA2306/boothitemmanager/commit/03fa58dcc26e92ba159507841a63f44f60668863", "https://github.com/KAFKA2306/boothitemmanager/commit/344d53c33eebb93e0adff3287c9199b24869aca2"], "why_interesting": "観測データの更新が繰り返されると、比較の対象だけでなく比較の前提も変わる。これは単なるデータ更新ではなく、時間軸が定義そのものになる現象だ。", "technical_payoff": "一般化すると、動的な観測データには観測時刻と比較基準を必須にしないと、比較自体が意味を失う。", "reader_before": "同じ店の同じカテゴリを見ているつもりでも、更新時点が違うと比較の基準が変わり、自分の判断がいつのデータを見ているのか分からなくなっている。", "reader_after": "観測データを比較する前に、更新時点と比較対象を明示できるようになる。単なる棚卸ではなく、時点付きの比較が可能になる。", "design_philosophy": "視覚的な整然さより、観測時点の明示と比較条件を優先する。更新の多さに応じて、静的な表現を捨てて時系列の比較に切り替える。", "why_this_article": "一般tutorialでは得られないのは、同じ更新文が短時間で3回続いているという実運用の変化だ。比較の前提が変わること自体が、データ更新の主役になっている。", "proof_of_value": "PUBLIC_GITHUB_SIGNALSには同じ「refresh BOOTH observations」が連続3回記録されており、データは一度確定したわけではなく、更新ごとに前提が変わっている。", "desired_reader_action": "比較表を作る前に、その表がいつの観測を基準にしているかを一列追加し、静的な説明を避ける。", "non_goal": "この記事はBOOTHの営業戦略や商品選定の最適解を出さない。観測データの前提変動を見える化することに限定する。"}, {"title": "検証済みの数値は、いつでも変わる前提だ", "title_options": {"general_problem": "変わらないはずの数値が、現実には毎日の更新対象になる", "concrete_anomaly": "SECのFCFと在庫が『verified』として更新され、予測モデルの前提が毎回揺れた", "searchable": "検証済み財務数値の更新は、どこまでが前提でどこまでが結論か"}, "central_question": "なぜ『verified SEC FCF』や『verified SEC inventory』が更新されるたびに、モデルの判断が変わるのか？", "surprising_finding": "semiconductor-earnings-modelは「data: update verified SEC FCF」と「data: update verified SEC inventory」を更新し、同時に財務予測と分析を更新しており、検証済みの前提自体が毎日変わっている。", "initial_hypothesis": "検証済みの数値は基本的に固定され、モデルの更新は比較対象の差分に過ぎない。", "hypothesis_update": "更新履歴が「verified」とついた数値の更新と予測の更新を同時に起こしているため、「verified」は一度の確定ではなく、最新の基準点を指すと理解が変わる。", "stakes": "財務モデルの前提が動くと、投資判断の結論がその場で変わり、見えている話がまるで別の仮説に見える。", "story_type": "contradiction", "evidence_urls": ["https://github.com/KAFKA2306/semiconductor-earnings-model", "https://github.com/KAFKA2306/semiconductor-earnings-model/commit/9bce96a17b6b8b8da2472feb821ac6fd8d45a1a8", "https://github.com/KAFKA2306/semiconductor-earnings-model/commit/dd562c68ce24cebc6e3d430b742d12aa1f2af5d1", "https://github.com/KAFKA2306/semiconductor-earnings-model/commit/54a082c35b00047bd4fdd12588cda4f797415b63"], "why_interesting": "『verified』が付く数値でも、実際には更新される前提であり、比較の基準が変わる。これは数値の真偽より、時間軸と基準の変化が重要になる現象だ。", "technical_payoff": "一般化すると、検証済み入力は固定であるという前提より、現在の確定版の更新が比較基準そのものになる。", "reader_before": "今回の数値が『最新』か『過去』かが曖昧で、モデルの結論が基準の違いで変わるのに気づけていない。", "reader_after": "モデルの比較を行う際、どの時点の数値を入力に使っているかを明示できるようになる。結論そのものより、前提がどこで変わったかを見抜ける。", "design_philosophy": "見た目の安定性より、比較基準の更新を先に出す。『検証済み』を装飾にしない。", "why_this_article": "一般tutorialや公式docsでは、数値はあくまですでに固定の前提として扱われがちだ。が、このリポジトリでは『verified SEC FCF』が更新対象であり、前提そのものが更新されている。", "proof_of_value": "PUBLIC_GITHUB_SIGNALSには「data: update verified SEC FCF」と「data: update verified SEC inventory」が直近で出ており、公開済みの基準が毎回変更される運用実績が確認できる。", "desired_reader_action": "数値を比較する前に、その数値が『今の前提』なのか『過去の確定値』なのかを本文で区別する。", "non_goal": "この記事はファンダメンタル分析の理論そのものを証明しない。数値が前提として更新され続けることと、その扱いの重要性を示すことに限定する。"}, {"title": "更新のたびに、説明が別の前提を持つ", "title_options": {"general_problem": "自律物流の説明が変わると、比較の土台も変わる", "concrete_anomaly": "autonomous logisticsの証跡が短期間で複数回更新され、基準が揺れていた", "searchable": "自律物流の証拠更新は、どこまでが比較でどこまでが前提か"}, "central_question": "なぜ自律物流の公開証拠が複数回更新されるたびに、比較対象が別物に見えるのか？", "surprising_finding": "autonomous-logisticsは「data: update autonomous logistics evidence」を複数回続けており、公開証拠そのものが静的な事実ではなく、同じ名前で別の前提が積み上がっている。", "initial_hypothesis": "公開された証拠は比較の基準として固定され、更新は単なる補正である。", "hypothesis_update": "短期間に複数回更新された実績があり、証拠の更新が『説明の前提を変える』こと自体がヒントになっている。", "stakes": "運用判断が過去の前提に縛られると、今の説明と過去の比較が混ざって誤った判断になる。", "story_type": "anomaly", "evidence_urls": ["https://github.com/KAFKA2306/autonomous-logistics", "https://github.com/KAFKA2306/autonomous-logistics/commit/7868e60e4f68a0217f7ca546eed263925e45ce94", "https://github.com/KAFKA2306/autonomous-logistics/commit/fb3c3fc0ce5b6b21645afa0acf12e6b550dd9638", "https://github.com/KAFKA2306/autonomous-logistics/commit/e44d62d0d0330fef4879139dc45b7ca48333f612"], "why_interesting": "一般的な『データを更新した』の文脈ではなく、証拠の名前が同じでも更新ごとに前提が変わる。比較対象の再定義がいつ発生するかを観察できる。", "technical_payoff": "一般化すると、公開証拠の更新は『比較している対象の変化』を意味するので、比較前に時点と境界を固定する設計が必要になる。", "reader_before": "自律物流の説明と比較が同じ名前で混ざっていて、今の判断が過去の前提に触れているか分からない。", "reader_after": "比較の前提を固定できるようになり、今の説明と過去の比較が混ざらない。", "design_philosophy": "時点の固定を優先し、同じ名前の証拠でも前提が違えば別物として扱う。説明の整然さより、比較可能性を優先する。", "why_this_article": "一般tutorialでは、公開証拠の更新は「データ更新」で終わりがちだが、このリポジトリでは更新が前提の反復変化として現れている。比較の土台が変わる現象そのものが記事の主役になる。", "proof_of_value": "PUBLIC_GITHUB_SIGNALSでは、同一repoで「data: update autonomous logistics evidence」が短期間に複数回立っており、前提更新が継続していることが確認できる。", "desired_reader_action": "同じ説明の比較をしようとする前に、どの観測時点を比較しているかを明記し、過去の前提を巻き込まない。", "non_goal": "この記事は物流の最適化手法やモデルの予測理論を説明しない。比較の前提が変わる事実と、その影響を扱う。"}, {"title": "日次価格と保有明細の差が、比較の基準を壊す", "title_options": {"general_problem": "最新の価格が見えると、何を比較出来るかが変わる", "concrete_anomaly": "ETFの日次価格と持ち分が連日更新され、比較基準が次々に切り替わった", "searchable": "ETFの価格更新と保有明細更新は、比較の前提をどう変えるか"}, "central_question": "なぜETFの価格と保有明細が連日更新されると、比較の基準が変わってしまうのか？", "surprising_finding": "etfは「data: update ETF daily prices 2026-09-14」「data: update ETF daily prices 2026-09-13」と「snapshot ARK ETF holdings」を連続して更新しており、価格と保有構成が『同じ時点の説明』として固定されていない。", "initial_hypothesis": "ETFの価格整合と保有明細は個別のデータであり、比較の基準は常に固定されている。", "hypothesis_update": "価格と保有明細が別々の日付で更新されているため、比較対象の時点がずれていると気づく。", "stakes": "基準がずれたデータで比較すると、資産構成の意味付けが変わり、誤った判断が増える。", "story_type": "magnitude", "evidence_urls": ["https://github.com/KAFKA2306/etf", "https://github.com/KAFKA2306/etf/commit/2687ec0ba7ef2acb02038b62530616a0441475d2", "https://github.com/KAFKA2306/etf/commit/0dc42cc28f112252bab62fc778f3607f176b68dd", "https://github.com/KAFKA2306/etf/commit/df62bd48fe62b2e29c5e39ed1b9c854fa9500efe"], "why_interesting": "価格と持ち分の更新が別時点になることで、比較対象の正しさが定まらない。これは単なる価格データの更新でなく、比較の起点そのものが変わる話だ。", "technical_payoff": "一般化すると、日次更新された指標の比較では時点と比較対象の整合が最重要になる。", "reader_before": "ETFの値動きと保有明細を同じ基準で見ているつもりでも、更新日がずれていて比較が狂っている。", "reader_after": "比較表を組む前に、時点と比較対象を固定できるようになり、過去の数値を誤って今の判断に使わなくなる。", "design_philosophy": "整然とした表よりも、時点付きの比較を優先する。見た目の一貫性を捨てて、比較対象の定義を最優先にする。", "why_this_article": "一般tutorialでは価格と保有明細の更新が別物として扱われがちだが、ここでは同じリポジトリが両方を連続して更新しており、比較の基準が変わる実運用が確認できる。", "proof_of_value": "PUBLIC_GITHUB_SIGNALSにはETF daily prices 2026-09-14/13とARK ETF holdings snapshotが連続して出ており、更新のスパンと比較基準の変動が確認できる。", "desired_reader_action": "同じETFの比較表を作るとき、価格と保有明細の更新日を一列目に置いて、古い基準を混ぜない。", "non_goal": "この記事はポートフォリオ設計やヘッジ戦略の解説をしない。比較基準のズレが判断にどう効くかを示すことに限定する。"}, {"title": "コミュニティの採点が動くと、記事候補も勝手に変わる", "title_options": {"general_problem": "評価が変わると、どこまでが結果でどこまでが前提なのか分からなくなる", "concrete_anomaly": "unity-mcpの記事候補が何度も同期され、採点の基準が時系列で変動していた", "searchable": "記事候補の同期は、いつの評価が正しいのかをどう変えるか"}, "central_question": "なぜコミュニティの採点候補が何度も同期されると、記事候補の価値そのものが揺れるのか？", "surprising_finding": "unity-mcpは「chore(community-practice): sync scored article candidates」を繰り返しており、同じリポジトリの評価対象が静的な成果物ではなく、時系列で差分が出る可変な前提だった。", "initial_hypothesis": "採点済みの候補は安定した実績であり、同期は単なる反映作業に過ぎない。", "hypothesis_update": "同じ文言の同期が複数回起きているので、採点の基準が時間とともに変わると理解が変わる。", "stakes": "評価の基準が動くと、記事候補の価値判断が現在の語感で固定され、過去の比較が無意味になる。", "story_type": "anomaly", "evidence_urls": ["https://github.com/KAFKA2306/unity-mcp", "https://github.com/KAFKA2306/unity-mcp/commit/85f59912528fbe52de827a9781ccae09c892ac1b", "https://github.com/KAFKA2306/unity-mcp/commit/b5b3db137effe9502676c7b5f499a9c142c07756", "https://github.com/KAFKA2306/unity-mcp/commit/98cbebccc858cf4ce38511be57079064e1de21d8"], "why_interesting": "評価が同期されるたびに、何をもって価値があるとしたのかが変わる。これは『採点対象が変わる』という話で、見た目の安定より前提の変化が主役になる。", "technical_payoff": "一般化すると、スコア付きの候補は静的な事実ではなく、比較対象の定義が時間とともに変わる。評価は時点を持つべきだ。", "reader_before": "候補の順位が動いているのに、いつの評価を基準にしたのか分からず、比較が狂っている。", "reader_after": "ランキングや候補の採点を、時点と前提を明示して扱えるようになる。過去の評価を今の判断に無批判で重ねなくなる。", "design_philosophy": "価値の見た目より、評価時点と基準の固定を優先する。同期の回数自体を誤差ではなく、前提変動の信号として扱う。", "why_this_article": "一般tutorialでは「評価指標を決める」の話はよくあるが、ここではリポジトリ自体が系列的に候補を同期しており、評価の定義が時系列で変わること自体が主役になる。", "proof_of_value": "PUBLIC_GITHUB_SIGNALSには「sync scored article candidates」が複数回存在し、スコアの更新がリポジトリの運用の一部として明示されている。", "desired_reader_action": "評価や候補の比較をする前に、その評価がいつの基準で作られたかを必ず付ける。", "non_goal": "この記事は採点モデルの理論そのものを展開しない。評価対象が変わると比較が壊れることと、その境界づけを扱う。"}]}, "candidate_review": {"reviews": [{"logic": 4.1, "utility": 3.8, "readability": 4.3, "originality": 3.5, "clarity": 4.2, "interest": 3.9, "discovery": 4.0, "narrative": 4.2, "context": 4.1, "blocking_issues": ["missing_proof_of_value", "weak_differentiation"], "revision_actions": ["実際に許可済み保存先・未宣言保存先・判定不能な保存先の3ケースを実行し、終了コード、生成物の有無、実行記録への追跡結果を測定してbefore/afterの証拠を追加する。", "fail-close導入前後で何が変わったか、または導入によって防げた具体的な失敗を示し、単一コミットの設計意図と実際の効果を分離して記述する。", "読者が自分の処理へ適用できる最小スキーマや検証項目について、実際に再現可能な形式と確認結果を追加する。", "冒頭で提示した『表示された』と『再検証可能な成功』の差を、具体的な実行結果または追跡不能になった成果物の事例で早い段階に証明する。"], "overall": 3.98, "story_overall": 4.05, "evaluation_kind": "internal_lapras_rubric_proxy", "editorial_evaluation_kind": "story_interest_proxy"}], "evaluation_kind": "internal_lapras_rubric_proxy", "editorial_evaluation_kind": "story_interest_proxy", "logic": 4.1, "utility": 3.8, "readability": 4.3, "originality": 3.5, "clarity": 4.2, "interest": 3.9, "discovery": 4.0, "narrative": 4.2, "context": 4.1, "overall": 3.98, "story_overall": 4.05, "blocking_issues": ["missing_proof_of_value", "weak_differentiation"], "revision_actions": ["実際に許可済み保存先・未宣言保存先・判定不能な保存先の3ケースを実行し、終了コード、生成物の有無、実行記録への追跡結果を測定してbefore/afterの証拠を追加する。", "fail-close導入前後で何が変わったか、または導入によって防げた具体的な失敗を示し、単一コミットの設計意図と実際の効果を分離して記述する。", "読者が自分の処理へ適用できる最小スキーマや検証項目について、実際に再現可能な形式と確認結果を追加する。", "冒頭で提示した『表示された』と『再検証可能な成功』の差を、具体的な実行結果または追跡不能になった成果物の事例で早い段階に証明する。"]}, "candidate_sources": {"all_urls": ["https://github.com/KAFKA2306/image2outfit/commit/c9ef37340a4a489f1ccb90d23d0def3dbc773e26"], "valid_urls": ["https://github.com/KAFKA2306/image2outfit/commit/c9ef37340a4a489f1ccb90d23d0def3dbc773e26"], "own_github": ["https://github.com/KAFKA2306/image2outfit/commit/c9ef37340a4a489f1ccb90d23d0def3dbc773e26"], "external_primary": []}, "sources_ok": false, "revision_attempts": 3} -->

# 表示できたのに、あとから説明できない——公開成果物を追跡可能にする最小条件

公開ページが表示され、処理も終了コード `0` で終わる。

その瞬間は、作業が完了したように見える。ページを共有し、次の作業へ進める。

しかし後日、次の確認が必要になったとする。

- この成果物は、どの入力から作られたのか
- どのコードで実行されたのか
- 実行時の検証は成功していたのか
- 現在の基準点から、同じ成果物をもう一度たどれるのか

ここで答えられなければ、残るのは「そのとき表示されていた」という記憶だけだ。

この問題を調べるため、2026年9月14日に `image2outfit` の公開リポジトリを確認した。`image2outfit` は今回の事例に使った固有のリポジトリ名であり、ここで扱いたい問題は、特定の画像処理やホスティングサービスの使い方ではない。

## 最初に疑ったのは、公開先だった

公開ページをあとから追跡できないなら、最初はデプロイ設定や公開先の状態を調べるのが自然だ。

ページが見えるなら、少なくとも生成処理と公開処理は最後まで進んだように見える。終了コードが `0` なら、なおさら成功と判断しやすい。

ところが、確認できたコミットには、公開先より手前の問題を扱う変更があった。

[fail-close undeclared stage filesystem writes](https://github.com/KAFKA2306/image2outfit/commit/c9ef37340a4a489f1ccb90d23d0def3dbc773e26)

このコミットで確認できるのは、ステージが宣言していないファイルシステムへの書き込みを失敗として扱う変更である。

つまり、処理の成否を決める境界は、ページが表示される場所だけではない。処理中にどこへファイルを書き込めるか、そのファイルが正式な成果物なのか一時出力なのか、そしてその状態をあとから参照できるのかも、成功条件に含まれる。

ここで調査前の予想が変わった。

> 問題は「公開できたか」ではなく、「公開されたものを、現在のコードと実行記録へ戻れるか」なのではないか。

## 「ファイルがある」と「成果物を証明できる」は違う

成果物を追跡するには、少なくとも次の対応関係が必要になる。

```text
入力
  -> 実行
  -> 検証
  -> 保存された成果物
  -> 固定されたコードの履歴
```

ローカルにファイルが残っていても、どの入力・どの実行・どの検証結果に対応するかが分からなければ、それは成果物の存在を示すだけで、成功の根拠にはならない。

特に危険なのは、次のような状態だ。

```text
処理は終了コード 0
  -> 画面では成果物が表示される
  -> 一時領域にもファイルがある
  -> 正式な保存先への書き込みは確認できない
  -> 現在の基準点から生成元をたどれない
```

この場合、「表示された」は事実かもしれない。しかし、「検証済みの成果物が生成された」とは限らない。

今回のコミットが直接証明するのは、未宣言のステージ書き込みを拒否する設計変更が行われたことまでだ。実際にどの成果物が失われたのか、どの公開ページがその影響を受けたのか、すべての障害が書き込み境界に起因するのかまでは、このコミットからは判断できない。

この限定が重要だった。調査中に見つけた設計変更を、発生した障害の完全な原因として扱うと、証拠より強い結論を作ってしまうからだ。

## fail-closeが変えるのは、エラー処理ではなく成功の意味

未宣言の場所への書き込みを許したまま処理を続けると、そのファイルが一時出力なのか正式な成果物なのかを、あとから判断することになる。

その判断に必要な情報が残っていなければ、公開ページが正常でも、成果物の説明可能性は失われる。

`fail-close` は、書き込み後に「これは問題なかった」と解釈する設計ではない。許可された保存先か判定できない時点で処理を止める設計である。

```text
保存先が許可されている
  -> 続行

保存先が許可されていない
  -> 失敗

保存先を判定できない
  -> 失敗
```

この変更によって、成果物が必ず正しくなるわけではない。入力の妥当性や検証内容まで保証するものでもない。

ただし、少なくとも「保存されていないかもしれない成果物」を、成功した処理の結果として静かに残す可能性を減らせる。失敗を早く表面化させることで、後日になって生成元を探せない状態を、公開前に止められる。

## 他のプロジェクトへ持ち帰れる判断

今回の事例から、特定のPages設定や画像処理手順をそのまま採用する必要はない。

持ち帰れるのは、次の判断規則である。

> 後から成果物を成功の根拠として使うなら、  
> **成果物・入力・実行・検証・固定コードの対応関係を保存し、対応を確定できない処理は成功扱いにしない。**

この規則を適用する価値が高いのは、次の条件がある処理だ。

- 第三者が後から成功条件を確認する
- 生成物が次の判断や処理の入力になる
- 実行環境と保存先が分離している
- 一時ファイルと正式な成果物が同じ処理経路にある
- 表示や終了コードだけでは品質を説明できない

一方、その場限りのローカル試作で、成果物を保存せず、第三者による再検証も必要ないなら、同じ強度の証跡管理は過剰になりうる。

単一リポジトリの一つのコミットから、すべての生成処理に同じ設計が必要だと断定することもできない。処理の失敗コストと、あとから説明する必要性を見て、保存境界の厳しさを決めるべきだ。

## 導入・停止・再実行を決める最小実験

新しい生成処理や公開処理にこの考え方を導入するなら、いきなり運用全体を作り替える必要はない。まず、1回の実行を次の単位で記録する。

```text
実行ID
  -> 入力の識別子
  -> 使用したコードの固定点
  -> 許可された保存先
  -> 検証結果
  -> 成果物の識別子
```

そのうえで、意図的に次の3ケースを試す。

| ケース | 期待する結果 |
|---|---|
| 許可された保存先へ書き込む | 成功し、成果物から実行記録へ戻れる |
| 未宣言の保存先へ書き込む | 失敗し、成功した成果物を残さない |
| 保存先を判定できない | 失敗し、警告だけで続行しない |

この実験で確認したいのは、ページが表示されるかではない。

1. 成果物から入力・実行・コード・検証へ戻れるか
2. 対応関係が欠けたときに処理が止まるか
3. 失敗した実行を、公開成功として記録できないか

1つ目ができず、2つ目または3つ目が曖昧なら、表示確認だけで公開成功とは判定しない。保存先や検証記録を修正してから再実行する。

## この証拠が示していないこと

今回確認できた公開コミットからは、次のことは言えない。

- 特定の公開ページが実際に壊れていた
- どのファイルが、どの実行で失われた
- 現在の公開成果物が不正である
- すべてのファイル書き込みが危険である
- `fail-close` だけで、すべての証跡消失を防げる

確認できるのは、未宣言のステージ書き込みを拒否する変更が公開履歴に存在することと、成果物を評価するには「表示された」以外の対応情報が必要だということだ。

だから、公開ページを見て成功と判断する前に、次の順で確認する。

```text
表示できる
  -> 正式な保存先にある
  -> 入力と実行に対応する
  -> 固定されたコードへ戻れる
  -> 検証結果を確認できる
```

途中で戻れないなら、その成果物は表示できていても、まだ再検証可能な成功ではない。
