<!-- pipeline_meta: {"idea_source": "public-github", "evaluation_kind": "internal_lapras_rubric_proxy", "editorial_evaluation_kind": "story_interest_proxy", "topic_selection": {"selected": {"title": "見た目の判定が古いまま、何を信じればいいか", "title_options": {"general_problem": "見た目の判定が古いまま、何を信じればいいか", "concrete_anomaly": "GitHub Pagesの最新画面でFAILなのに、レビューのPASSが残った", "searchable": "古いUIレビューが最新renderを誤判定する"}, "central_question": "なぜ『レビューPASS』が、最新renderの証拠として使えるのに、実際には古い画面の判定に引きずられるのか？", "surprising_finding": "image2outfitの直近3コミットは、古いhuman review keyと重複PASSを削除し、completionGates.visualAppearanceReviewを唯一の完了判定にしたと明示している。", "initial_hypothesis": "レビュー結果は最新の成果物に紐付いているので、古い判定は後から自動で無効化されるはずだ。", "hypothesis_update": "コミットメッセージが「現行mainのGitHub Pages artifactを直接確認した外観FAILを正本へ反映」「旧PASSを削除」「唯一の完了判定」と書いているので、レビュー状態そのものがartifactと結びついていないと誤った完了判定が残る。", "stakes": "品質ゲートで古い判定が新しい成果物を通してしまうと、見た目の事故を見逃し、リリース直前の意思決定を誤らせる。", "story_type": "contradiction", "evidence_urls": ["https://github.com/KAFKA2306/image2outfit/commit/0a025e6e6ba1b360418b6c5ddb22e7a14ce9d7b6", "https://github.com/KAFKA2306/image2outfit/commit/a2691970b22cf7d2b135d6c9582b985e4a22a1c8", "https://github.com/KAFKA2306/image2outfit/commit/72a73a3304b1539aaaef4988da6826e29467d9dc"], "why_interesting": "前提である『PASSは最新状態の証拠』が、古いキーと重複状態で崩れる。これは単なるレビューの手間ではなく、誰が何を信じるかの根拠そのものが曖昧になる現象だ。", "technical_payoff": "レビュー結果を「最新artifactに固有の証跡」として扱う設計にすると、品質ゲートは古い証拠に引っ張られなくなる。つまり、証跡と成果物の紐付けが、判定の信頼性の実体になる。", "reader_before": "レビュー結果を見て『通過したのだから問題ない』と判断してしまい、現行の画面がまだ未検証なのに、完了済みのように扱ってしまう。", "reader_after": "プルリクエストでPASSを見たときに、artifact hashとレビュー時点を確認し、古い判定を除外する運用を始めて、完了判定の根拠を一貫させられる。", "design_philosophy": "読者価値を守るには、証拠の鮮度と唯一性を最優先にし、見た目の快適さやレビュー履歴の保存を後回しにする。古い判定の残留は、短期的には便利でも、長期的には誤った完了を誘発するので受け入れない。", "why_this_article": "一般tutorialや公式docsでは、失敗も含めた『レビュー結果が古いartifactにくっつく』現象は説明されない。直近の公開コミットで、古いPASSの削除と唯一判定への置換が実測的に起きている。", "proof_of_value": "公開証拠として、0a025e6 は「現行mainのGitHub Pages artifactを直接確認した外観FAILを正本へ反映」、a2691970 は「重複PASSを削除」、72a73a3 は「未定義のresearch trial完了ゲートを削除し、completionGates.visualAppearanceReviewを唯一の完了判定にする」と記述されている。", "desired_reader_action": "レビュー結果を採用する前に、artifactのhashと判定の同一性を確認する運用ルールを導入する。", "non_goal": "この記事は、見た目の絶対基準や美的価値の定義を決めるものではない。証跡とartifactの紐付けの信頼性を扱う。"}, "alternatives": [{"title": "目的地の位置がURLに残らないと、ページを信頼できない", "title_options": {"general_problem": "目的地の位置がURLに残らないと、ページを信頼できない", "concrete_anomaly": "同じページでも、どこにいたかをURLで共有できず、回帰テストまで壊れた", "searchable": "section URL state and canonical RuleSet projection in game pages"}, "central_question": "なぜゲームページで『見ている場所』をURLに落とし込むのが、回帰対策と共有の両方に効くのか？", "surprising_finding": "rule-scribe-gamesの直近コミットは「GamePageの表示位置をURL fragmentで共有できるようにする」「section URL回帰テストを追加」「旧Quick Rules前提のテストを削除」と報告している。", "initial_hypothesis": "ページの見えている位置はUI内部の状態にすぎず、URLへ持ち出すのは便利なだけだろう。", "hypothesis_update": "コミット群がURL fragment共有、section URL回帰テスト、canonical RuleSet投影へ統一する流れを示しているので、ユーザーがどこを見ているかが、データの正しさと回帰防止の前提になっている。", "stakes": "位置情報がURLに残らないと、共有や再現が困難になり、UIの誤動作が「個人の操作ミス」に見えてしまう。", "story_type": "unexpected-connection", "evidence_urls": ["https://github.com/KAFKA2306/rule-scribe-games/commit/cfb1a3df6f227f8ae5819378295fe3ba0a8ffda6c", "https://github.com/KAFKA2306/rule-scribe-games/commit/5bd3dceea4e0487d892bf8372217cac47e20ce0c", "https://github.com/KAFKA2306/rule-scribe-games/commit/208b138cd6fcc86b1e2c2c603adf23478460e586"], "why_interesting": "状態の本体が画面ではなくURLに移ると、UIの再現性と共有性が一気に変わる。この現象は「見えている位置」が単なる表示ではなく、ユーザーの文脈そのものになるから面白い。", "technical_payoff": "UI状態はURL fragmentなどの外部表現に固定し、内部システムから独立して管理する設計は、共有・再現・回帰テストを一貫させる。", "reader_before": "自分がページのどこを見ているかを再現できず、スクショや説明だけでは再現できない。", "reader_after": "URLで状態を共有し、最初に見た位置と今の位置を同じ条件で再現できるようになる。", "design_philosophy": "読者価値を守るには、UI状態を画面の見た目ではなく、再現可能な外部状態として扱うことを優先する。見た目の簡潔さよりも、共有と再現の正確さを選ぶ。", "why_this_article": "一般tutorialでは、「URL fragmentで状態を持つ」とだけ説明されるが、ここでは実際に旧Quick Rules前提の回帰テストが削除され、canonical RuleSet投影へ置換された具体的な判断変更が見える。", "proof_of_value": "直近コミットが「GamePageの表示位置をURL fragmentで共有」「section URL回帰テストを追加」「旧Quick Rules前提のテストを削除」「canonical RuleSet投影へ更新」を明示している。", "desired_reader_action": "ページの状態を共有したいときに、スクリーンショットではなくURL fragmentで再現可能な設計を採用する。", "non_goal": "この記事は、UIコンポーネントの見た目そのものの最適化を扱わない。状態の再現性と判定の一貫性を扱う。"}, {"title": "要約が先に来ると、ユーザーは行動できない", "title_options": {"general_problem": "要約が先に来ると、ユーザーは行動できない", "concrete_anomaly": "ホーム画面を『全体統計』から『意図選択・推奨・会場発見』へ並べ替えた", "searchable": "intent selection before corpus metrics in event discovery"}, "central_question": "なぜイベントページが『全体の統計』より『ユーザーの次の一手』を先に出すべきなのか？", "surprising_finding": "cast_event_calのコミットは「Prioritize intent selection, recommendations, and concrete event discovery ahead of corpus/system summary metrics」と明記している。", "initial_hypothesis": "ユーザーは総数や基礎データの把握を先に欲しがるので、概要メトリクスを前に置くのが自然だ。", "hypothesis_update": "コミットメッセージが、ホームビューの優先順位変更を明示しているので、イベント選択の価値は『把握』より『判断』にある。つまり、ユーザーの行動前に要約が来ると、意思決定の前提が遮断される。", "stakes": "行動の前に要約が先に来ると、利用者は選ぶ前に情報を消耗し、目的と近い候補にたどり着けず、満足度の低い検索に陥る。", "story_type": "contradiction", "evidence_urls": ["https://github.com/KAFKA2306/cast_event_cal/commit/b4d7ddfc92313f9a829bb1dfe071e0202c787247", "https://github.com/KAFKA2306/cast_event_cal/commit/540243762a0070f32608d33e8ea63b78cd46bcec", "https://github.com/KAFKA2306/cast_event_cal/commit/fb4c84b65beedbc1baec21c6038cf62f339d4646"], "why_interesting": "『多くの情報』を前に出すと、実際にはまず選ばない。優先順位のいちばん大事な意味は、利用者が何を選ぶかを支えることにある。", "technical_payoff": "画面の上部構成は、情報の量ではなく、利用者の次の意思決定を先に支える順序設計であるべきだ。", "reader_before": "イベント選択の前に、総数や全体像を見せられても、何を選べばいいのか分からず、行動を始められない。", "reader_after": "行動に近い候補や意図選択を先に見られるようになり、情報収集から行動へ移る時間を短くできる。", "design_philosophy": "読者価値を守るには、要約を先にしたい誘惑を抑え、利用者の意思決定を支える最短経路を優先する。メトリクスの可視化は後段に置く。", "why_this_article": "一般tutorialでは『UXの優先順位』は語られるが、このリポジトリでは実際のUI順序変更が公開コミットとして記録されている。数値より行動価値を前にしたという具体的な判断変更が証拠になる。", "proof_of_value": "コミット b4d7ddfc は「Prioritize intent selection, recommendations, and concrete event discovery ahead of corpus/system summary metrics」と明確に書いており、公開UIの順序がそこで変わった。", "desired_reader_action": "イベントや候補の選択画面を設計するとき、要約を先に置くのではなく、利用者の次の判断を先に配置する。", "non_goal": "この記事は、特定のUI見た目の美しさや、イベントデータの正確性そのものを評価するものではない。決定順序をどう設計するかを扱う。"}, {"title": "検証済みの数字が、どこから来たかを見失う", "title_options": {"general_problem": "検証済みの数字が、どこから来たかを見失う", "concrete_anomaly": "SECのFCFと在庫データが更新されるたび、同じモデルの意味が変わった", "searchable": "verified SEC FCF and inventory data update model claims"}, "central_question": "なぜ『検証済み』の数値が、更新されるたびに模型の意味そのものを変えるのか？", "surprising_finding": "semiconductor-earnings-modelの直近コミットは「data: update verified SEC FCF」「data: update verified SEC inventory」「data: refresh financial projections and analysis」と続いている。", "initial_hypothesis": "検証済みの数値は固いので、データ更新はモデルの結論を少し変えるだけだろう。", "hypothesis_update": "公開コミットが「verified SEC FCF」「verified SEC inventory」を明示しているので、数値の信頼性は更新元の検証条件と結びついていて、根拠が変わると結論そのものが変わる。", "stakes": "分析の出力が結果として見えるだけで、根拠の変化に気づかないと、誤った投資判断や設計判断を下しやすい。", "story_type": "counterintuitive-result", "evidence_urls": ["https://github.com/KAFKA2306/semiconductor-earnings-model/commit/c4c4914b4a9c8e3991b2a756a9e08246330ba2ca", "https://github.com/KAFKA2306/semiconductor-earnings-model/commit/2ea71f2febf61f2f0f11eb345c6d27b8b5bbf2b4", "https://github.com/KAFKA2306/semiconductor-earnings-model/commit/88de1ea5c8058eeceabf4c3f0358e98424e494d5"], "why_interesting": "『検証済み』というラベルが、数値の解釈まで固定するわけではない。根拠が変わると、モデルが見せる『感触』も変わるのが面白い。", "technical_payoff": "数値の出所と更新履歴を、モデルの説明と切り離さずに一緒に管理する設計が必要になる。この分離がないと、同じ分析が別の根拠で成立していると誤解する。", "reader_before": "数値の根拠が更新されても、なぜ結論が変わるのか分からず、見た目だけで信頼してしまう。", "reader_after": "数値が更新されたときに、根拠と更新時点を確認し、分析の再解釈が必要かどうかを即座に判断できる。", "design_philosophy": "読者価値を守るには、データの出所と更新タイムスタンプを見える場所に置き、数値のラベルよりも根拠の変化を優先する。", "why_this_article": "通常のデータ分析記事では、検証済み数値の解釈は静的に扱われるが、この公開コミットは更新ごとに出所と分析が再接続される現実を示している。", "proof_of_value": "公開コミットでは「verified SEC FCF」「verified SEC inventory」「refresh financial projections and analysis」がすべて記録されており、出所の更新がモデルの説明の変化を伴うことが確認できる。", "desired_reader_action": "分析結果を読むとき、数値そのものではなく、どの出典が更新されたかを先に見て、再解釈の必要があるかを判断する。", "non_goal": "この記事は、企業財務の投資判断そのものや、最終的な投資推奨を行うものではない。根拠更新が分析の意味をどう変えるかに焦点を当てる。"}, {"title": "旅行の割引案内が、UIではなく正準データの中に入った日", "title_options": {"general_problem": "旅行の割引案内が、どこに保存されているかで判断が変わる", "concrete_anomaly": "割引告知がアプリのUIではなく正準データに入って、境界テストまで必要になった", "searchable": "canonical data for travel discount announcements"}, "central_question": "なぜ旅行の割引告知をUIだけで管理せず、正準データに固定する必要があるのか？", "surprising_finding": "travelリポジトリのコミットは「商船三井さんふらわあの九州ふっこう応援割取扱い案内を正準データへ追加する」とし、「境界テストを追加」している。", "initial_hypothesis": "割引告知はページ上の文言として管理されているのが普通で、データ化は運用の細部だろう。", "hypothesis_update": "コミットメッセージが「正準データへ追加」「境界テストを追加」と示しているので、告知は見た目の更新ではなく、データ境界を守ることが本質である。", "stakes": "告知の配置と宣伝文の境界が崩れると、同じ見た目でも意味の異なる内容が混ざり、利用者が誤った意思決定をする。", "story_type": "unexpected-connection", "evidence_urls": ["https://github.com/KAFKA2306/travel/commit/acdc60ab573197ebc6bfdf350cbd1cc00028a03d", "https://github.com/KAFKA2306/travel/commit/51b3e334c1298d91b56e83b724b485934c35279d", "https://github.com/KAFKA2306/travel/commit/0fc91c6f97b5e265124b414674522e2f54a0cb7d"], "why_interesting": "コンテンツに見えるものが、実はデータ境界の保守対象であると分かると、UIと情報の構造が別物だと認識が変わる。", "technical_payoff": "内容の正しさはUI表現ではなく、正準データと境界テストで保証する設計が必要になる。", "reader_before": "割引告知を書いたはずなのに、どこが正本なのか分からず、更新が漏れるか、誤って別の情報と混ざる不安がある。", "reader_after": "告知の正本、表示、テストの責務を分離して、どこで変えるべきかが明確になる。", "design_philosophy": "読者価値を守るには、見た目の更新より正準データの変更と境界保護を優先する。UIの都合で内容が広がることを許さない。", "why_this_article": "一般的なCMSやUIの説明では、どこが正本かの設計は見えないが、このリポジトリでは「正準データ」「境界テスト」が実体として明示されている。", "proof_of_value": "コミット acdc60a は「正準データへ追加」と明記し、テストも「境界を保持する」と書かれている。", "desired_reader_action": "告知や重要な文言の更新を行うとき、UI直接編集ではなく正準データと境界テストの更新をセットで行う。", "non_goal": "この記事は、旅行事業そのもののマーケティング戦略を評価しない。情報の正本と境界をどう保つかを扱う。"}, {"title": "同じETFでも、日次の差分が投資判断を左右する", "title_options": {"general_problem": "同じETFでも、日次の差分が投資判断を左右する", "concrete_anomaly": "価格と保有銘柄のsnapshotが毎日更新され、結論がその日の根拠で変わる", "searchable": "ETF daily prices and holdings snapshot update model"}, "central_question": "なぜETFの分析が『同じ銘柄』でも毎日の変化で解釈を変えるのか？", "surprising_finding": "etfリポジトリは「data: update ETF daily prices 2026-08-31」「data: snapshot ARK ETF holdings」と連続して更新している。", "initial_hypothesis": "ETFの長期比較は日次の変動に影響されないので、日々の価格更新はメンテナンス程度だろう。", "hypothesis_update": "公開コミットが日次価格の更新と保有銘柄のsnapshotを並行して行っているので、モデルの結論は日次データの変動と同時に更新される。", "stakes": "日次の変化を見落とすと、同じ名前のETFを見ていても、十分な比較条件が揃わず、誤った判断になる。", "story_type": "magnitude", "evidence_urls": ["https://github.com/KAFKA2306/etf/commit/c4b23303e06dec461442d3a70907dcaf8314e94f", "https://github.com/KAFKA2306/etf/commit/884de2c7832744fc75dda65209cb1747d9d9771e", "https://github.com/KAFKA2306/etf/commit/1a3babd219e666c08bb87855e319b542d2b63805"], "why_interesting": "同じ銘柄名でも、日付が変わると保有内容や時価評価が変わるため、比較の前提そのものが更新される。", "technical_payoff": "データの比較は、「同じ名義の項目」でなく、「同一時刻・同一スナップショット」で比較する設計が必要になる。", "reader_before": "ETFを比較するときに、日次の変化がどこで効くのか分からず、同じ名前のデータを誤って比較してしまう。", "reader_after": "データ比較時に、更新日とsnapshot時点を必ず揃え、同じ時点での比較を前提にできる。", "design_philosophy": "読者価値を守るには、見た目の同一性より「同一スナップショット」で比較することを優先する。縦断比較の前提を固定しないと判断が無意味になる。", "why_this_article": "一般的なETF解説は銘柄の説明に留まりがちだが、公開リポジトリでは日次の価格更新と保有内容snapshotが同時に管理されている。比較の前提が更新されること自体が価値の核になる。", "proof_of_value": "直近3コミットが日次価格と銘柄保有snapshotを別々に更新している。これは比較条件が常に前提更新対象であることを示している。", "desired_reader_action": "分析を始める前に、比較対象の取得日とsnapshot時点を確認し、同一条件で比較する。", "non_goal": "この記事は、投資推奨そのものや具体的な取引戦略を提示しない。比較前提の更新が何を変えるかに焦点を当てる。"}, {"title": "再更新しても、観測の正しさに変わりはない", "title_options": {"general_problem": "再更新しても、観測の正しさに変わりはない", "concrete_anomaly": "BOOTH観測の更新が何度も走るのに、観測の品質基準が明示されない", "searchable": "BOOTH observation refreshes without quality boundary"}, "central_question": "なぜBOOTHの観測データが更新されるたびに、正しさの根拠が同じままではいけないのか？", "surprising_finding": "boothitemmanagerは「chore(catalog): refresh BOOTH observations」を何度も繰り返している。", "initial_hypothesis": "観測データを更新するほど、情報は精度が上がるので、更新回数がそのまま信頼性を表すはずだ。", "hypothesis_update": "同じメッセージの繰り返しがある一方で、説明や判定基準が変わらないので、更新回数だけでは品質が上がっていない。", "stakes": "更新回数だけに依存すると、同じ不確実性を繰り返し再現してしまい、意思決定の根拠が薄くなる。", "story_type": "failure", "evidence_urls": ["https://github.com/KAFKA2306/boothitemmanager/commit/352168e181023fbd8b37d581bfabf0c930c10deb", "https://github.com/KAFKA2306/boothitemmanager/commit/3297f451e8943a743e718daac2bedd1db6109628", "https://github.com/KAFKA2306/boothitemmanager/commit/49b18121ee43bf05f840d25176b58bbb3cf4341a"], "why_interesting": "更新の回数と情報の質が結びつかない現象は、観測データの管理でよく起こる。更新のたびに『更新した』ではなく、『何が改善されたか』が必要になる。", "technical_payoff": "データ更新は、単なる再取り込みではなく、観測条件の変化と品質基準の再確認を伴うべきだ。", "reader_before": "同じ『refresh』の繰り返しを見て、更新が改善に繋がっていると誤解してしまう。", "reader_after": "更新のたびに、観測条件と品質基準の変化を確認し、データの更新が改善なのか単なる再配布なのかを区別できる。", "design_philosophy": "読者価値を守るには、更新回数よりも観測条件と品質基準を優先する。更新が繰り返されても、基準が固定されていなければ価値は増えない。", "why_this_article": "一般的なデータ更新の説明では、更新の回数自体が品質に変わるように扱われるが、公開コミットは更新回数の繰り返しだけを示している。ここで重要なのは、更新を保証する条件が見えないことだ。", "proof_of_value": "直近3コミットが同じ「chore(catalog): refresh BOOTH observations」を繰り返している。これは更新頻度が増えても、品質基準の説明が変わらないことを示している。", "desired_reader_action": "観測データを更新するとき、更新回数ではなく、観測条件と品質基準の変化を記録して再評価する。", "non_goal": "この記事は、BOOTHの商材や価格そのものを評価するものではない。更新の意味と品質判定の分離を扱う。"}, {"title": "研究の完了と製品の完了を混ぜると、品質ゲートが勝手に消える", "title_options": {"general_problem": "研究の完了と製品の完了を混ぜると、品質ゲートが勝手に消える", "concrete_anomaly": "未定義のresearch trial完了ゲートを削除したことで、見た目レビューだけが完了判定になった", "searchable": "undefined research trial completion gate removed from product quality"}, "central_question": "なぜ研究の完了判定を製品の完了判定と混ぜると、品質ゲートの意味が失われるのか？", "surprising_finding": "image2outfitのコミットは「未定義のresearch trial完了ゲートを削除する」とし、「visualAppearanceReviewは未検証のためFAILのまま維持する」と明言している。", "initial_hypothesis": "研究の作業状態と製品の完了条件は同じゲートで管理してもよさそうだ。", "hypothesis_update": "コミットが「研究基盤と製品品質ゲートの責務を分離する」と書いているので、同じゲートを共用すると、未検証状態を製品完了と混同してしまう。", "stakes": "研究状態が製品完了に混ざると、出荷判断や品質判定があいまいになり、見た目の品質を誤って通してしまう。", "story_type": "contradiction", "evidence_urls": ["https://github.com/KAFKA2306/image2outfit/commit/72a73a3304b1539aaaef4988da6826e29467d9dc", "https://github.com/KAFKA2306/image2outfit/commit/a2691970b22cf7d2b135d6c9582b985e4a22a1c8", "https://github.com/KAFKA2306/image2outfit/commit/0a025e6e6ba1b360418b6c5ddb22e7a14ce9d7b6"], "why_interesting": "『完了』というラベルが、研究の保守状態と製品の品質状態を同列に扱うとき、非常に危険な安易さが現れる。", "technical_payoff": "責務の分離を明示した完了ゲートは、研究の試行と製品の品質判定を切り分け、誤った通過を防ぐ。", "reader_before": "「研究中」「完成」「品質確認」の境界が曖昧で、どこまでが製品として信用できるのか分からない。", "reader_after": "研究成果と製品品質を別ゲートで管理し、未検証の状態を完成済みに混ぜない運用ができる。", "design_philosophy": "読者価値を守るには、ゲートの責務を明確に分離し、曖昧な中間状態を完了判定にしない方針を優先する。", "why_this_article": "一般的な品質管理の概念は、責務分離の実際の判断変更としては抽象的だが、このコミットは未定義ゲートを削除し、品質責務を分離した実例として記録されている。", "proof_of_value": "72a73a3 は「製品完了条件から実装・schema・永続化契約のない researchTrial を削除し、既存の研究基盤と製品品質ゲートの責務を分離する」と書いている。", "desired_reader_action": "研究と製品の完了条件を同じゲートにしないよう、責務分離を明文化し、未検証状態を完了扱いしない。", "non_goal": "この記事は、研究の価値やアイデアの妥当性を否定するものではない。完了判定の責務分離を扱う。"}, {"title": "選ぶ前に、意味のない総数を前に出すな", "title_options": {"general_problem": "選ぶ前に、意味のない総数を前に出すな", "concrete_anomaly": "ホーム画面が総数で埋まっていたが、ユーザーの判断に本当に必要なのは候補の質だった", "searchable": "home view prioritizes decision value over summary metrics"}, "central_question": "なぜイベントUIが総数やシステム指標より、ユーザーの「何を選ぶか」を先に出すべきなのか？", "surprising_finding": "cast_event_calの更新は、ホーム画面の優先順を 'corpus/system summary metrics' から 'intent selection, recommendations, and concrete event discovery' へ変えたと表現している。", "initial_hypothesis": "総数や全体像はユーザーの初期理解に必要なので、最初に見せるべきだ。", "hypothesis_update": "公開コミットが明示しているように、総数は情報量があるが判断価値が低く、ユーザーの選択に直結する意図選択と推薦を先に出すべきだった。", "stakes": "総数を先に見ると、利用者はより有益な行動候補を見落とし、定量的な見た目の理解が行動の前提を塗り替える。", "story_type": "counterintuitive-result", "evidence_urls": ["https://github.com/KAFKA2306/cast_event_cal/commit/b4d7ddfc92313f9a829bb1dfe071e0202c787247", "https://github.com/KAFKA2306/cast_event_cal/commit/540243762a0070f32608d33e8ea63b78cd46bcec", "https://github.com/KAFKA2306/cast_event_cal/commit/fb4c84b65beedbc1baec21c6038cf62f339d4646"], "why_interesting": "総数というのは見た目上は便利だが、ユーザーにとって『次に何をすべきか』を支えるには弱い。優先順位を変えると、見た目の豊かさより行動の確率が上がる。", "technical_payoff": "ユーザーの意思決定を支える設計では、情報量ではなく「次のアクションに使えるか」が優先順位の本体になる。", "reader_before": "画面に総数が並ぶと、選ぶべき候補が多すぎて行動の判断材料が足りないまま時間を浪費する。", "reader_after": "行動に直結する選択肢と推薦を先に見て、目的に近い候補へ進むことができる。", "design_philosophy": "読者価値を守るには、総数や概観を見せること自体を目的化せず、次の行動を支える順序を優先する。", "why_this_article": "総数の表示はどこにでもあるが、この公開コミットでは『総数を後ろにし、行動価値を前にする』具体的な設計判断が記録されている。", "proof_of_value": "コミット b4d7ddfc は明確に「intent selection, recommendations, and concrete event discovery ahead of corpus/system summary metrics」と書いている。", "desired_reader_action": "画面上の項目順を決めるとき、総数を先に置くのではなく、ユーザーがすぐ比較・選択できる項目を優先する。", "non_goal": "この記事は、イベント数やデータサイズの重要性そのものを否定しない。選択画面の順序と判断価値の設計を扱う。"}]}, "candidate_review": {"reviews": [{"logic": 4.3, "utility": 4.2, "readability": 3.9, "originality": 4.1, "clarity": 4.0, "interest": 4.3, "discovery": 4.4, "narrative": 4.6, "context": 4.1, "blocking_issues": [], "revision_actions": ["Add one concrete before/after artifact or screenshot to make the stale-review problem immediately visible to readers who do not know the workflow.", "Tighten the claim boundary by explicitly distinguishing a workflow-integrity issue from a universal rule for all visual review systems.", "Reduce the density of repo-specific jargon in the opening paragraphs and state the stakeholder decision risk in plain language sooner."], "overall": 4.1, "story_overall": 4.35, "evaluation_kind": "internal_lapras_rubric_proxy", "editorial_evaluation_kind": "story_interest_proxy"}], "evaluation_kind": "internal_lapras_rubric_proxy", "editorial_evaluation_kind": "story_interest_proxy", "logic": 4.3, "utility": 4.2, "readability": 3.9, "originality": 4.1, "clarity": 4.0, "interest": 4.3, "discovery": 4.4, "narrative": 4.6, "context": 4.1, "overall": 4.1, "story_overall": 4.35, "blocking_issues": [], "revision_actions": ["Add one concrete before/after artifact or screenshot to make the stale-review problem immediately visible to readers who do not know the workflow.", "Tighten the claim boundary by explicitly distinguishing a workflow-integrity issue from a universal rule for all visual review systems.", "Reduce the density of repo-specific jargon in the opening paragraphs and state the stakeholder decision risk in plain language sooner."]}, "candidate_sources": {"all_urls": ["https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages", "https://github.com/KAFKA2306/image2outfit/commit/0a025e6e6ba1b360418b6c5ddb22e7a14ce9d7b6", "https://github.com/KAFKA2306/image2outfit/commit/72a73a3304b1539aaaef4988da6826e29467d9dc", "https://github.com/KAFKA2306/image2outfit/commit/a2691970b22cf7d2b135d6c9582b985e4a22a1c8"], "valid_urls": ["https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages", "https://github.com/KAFKA2306/image2outfit/commit/0a025e6e6ba1b360418b6c5ddb22e7a14ce9d7b6", "https://github.com/KAFKA2306/image2outfit/commit/72a73a3304b1539aaaef4988da6826e29467d9dc", "https://github.com/KAFKA2306/image2outfit/commit/a2691970b22cf7d2b135d6c9582b985e4a22a1c8"], "own_github": ["https://github.com/KAFKA2306/image2outfit/commit/0a025e6e6ba1b360418b6c5ddb22e7a14ce9d7b6", "https://github.com/KAFKA2306/image2outfit/commit/72a73a3304b1539aaaef4988da6826e29467d9dc", "https://github.com/KAFKA2306/image2outfit/commit/a2691970b22cf7d2b135d6c9582b985e4a22a1c8"], "external_primary": ["https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages"]}, "sources_ok": true, "revision_attempts": 1} -->

# PASSを見たら安心しない：古い見た目レビューが今の画面を誤認させる

リリース前の見た目レビューで「PASS」を見た瞬間、私は一瞬だけ自分の前提を疑った。今の画面に対する判定なのか、それとも過去の画面に対する判定なのか。もし古いスクリーンショットや旧レビュー鍵が残っていれば、最新の表示がFAILでも、完了済みのように見えてしまう。問題は「見た目が良いか」ではなく、「その評価が今の成果物に対するものか」を確認できているかだ。

私は最初、レビュー結果は常に最新の成果物に対しているはずだと思っていた。PASSが出ていれば、その後に別の変更が入っていても、古い判定は自動で無効化されるんじゃないか。だが公開コミットの文言を見たとき、前提が崩れた。

当初の仮説はこうだった。

- レビューの結果は最新のrenderに対する証拠だ
- 古いPASSは後から消えるか、少なくとも現在の画面を説明しない
- 完了判定の真偽は、artifactとレビューがずれていないかで決まる

実際の観測は違った。古いreview keyや重複したPASSが残ると、最新のrenderの状態とは別物の証跡が「完了」のように見える。つまり、見た目レビューの価値は、評価そのものの良し悪しよりも、「その評価が今の成果物を指しているか」の鮮度と一意性に支配される。

この話は、UIレビューの細部にとどまらない。評価の証跡がどこまで信頼できるかという問題は、画面レビューだけでなく、生成物レビュー、デザインレビュー、デプロイ確認、出力検証のあらゆる場面に共通する。

## 1. まず起きたのは、見た目の判定が古いまま残ることだった

実際に公開されたコミットメッセージには、こんな変化がある。

- 「現行mainのGitHub Pages artifactを直接確認した外観FAILを正本へ反映し、stable builderが削除済みの旧human review keyを再生成しないようにする」
- 「現行revisionで直接確認していないhumanVisualReview/humanPoseReviewの旧PASSを削除し、completionGates.visualAppearanceReviewを唯一の完了判定にする」
- 「実装・schema・永続化契約のない researchTrial を製品完了条件から削除し、visualAppearanceReview は未検証のため FAIL のまま維持する」

この文言が示しているのは、見た目レビューが「その場の感想」ではなく、現在の成果物とどこまで結びついているかを設計で決めるべき問題だということだ。評価の結果には、単に「良い」「悪い」だけではなく、次の二つが必要だ。

- その評価が、今のartifactを指しているか
- その評価が、現在のrevisionに対する最新のものか

この二つが揃っていないと、古い判定が新しい完了のように見えてしまう。実際には、データとしては異なる画面に対するレビューが、同じ「PASS」として残っている。これが、レビューの記録の価値を壊す。

ここで私は、こういう一般的な知見を得た。

generalizable_insight: 証跡の価値は、評価そのものよりも「その評価がどの成果物を指しているか」の一意性と鮮度で決まる。レビュー結果が古い成果物にくっついていると、完了は見た目よりも不安定な基準になる。

transfer_conditions: 画像評価、UI review、生成物確認、外部render検証、データ差分レビューなど、結果を「現在の成果物」ではなく「過去の出力」へ紐付けてしまうプロセスに共通して当てはまる。

non_transfer_conditions: すべての判断がartifactに紐付いているわけではない。たとえば、コードの論理整合性や静的分析のように、実行時のrenderに依存しない検証では、鮮度の問題はそれほど強く出ない。証拠の対象が現在のrenderかどうかで、この知見の強さは変わる。

## 2. なぜ、これが人に効くのか

読んでいるときの摩擦は、こんな感じだ。

- PASSを見たから、今の画面は大丈夫だと思い込んでしまう
- 見た目がFAILでも、古い判定が残っていると判断が曖昧になる
- どのrenderに対する判定なのか分からず、完了条件がぶれる

これは単なる運用上のミスではない。リリース判断の信頼性そのものに影響する。もし古い判定が最新のartifactを通ってしまえば、品質ゲートは、見た目の事故を見逃す。

この問題を避けるには、レビューの真偽を最初に「現在のartifactに対する評価か」で判定する必要がある。つまり、読後の判断はこう変わる。

- before: 「PASSだったから、現在の画面は問題ない」と思い込む
- after: 「PASSが出たとしても、artifactとreviewの紐付けを確認し、古い証拠を切り離す」

その結果、レビュー担当者は「判定が残っている」ことと「現在の画面が検証済みである」ことを混同しなくなる。これは、品質ゲートの設計が人間の安心感に依存しないようにするための判断基準だ。

## 3. 予想と現実のズレ

この問題は、初期のイメージと実際の運用で大きくズレる。

私は最初、レビューPASSは「現行成果物に対する証拠」だと思っていた。自動化の設計としては、自然な前提だ。だが実際には、古いhuman review keyが残ったり、重複したPASSが残ったりする。そうなると、完了判定の記録が今のrenderに対してではなく、過去の状態に引きずられたものになる。

ここで重要なのは、「レビュー結果が古い」という事実だけではない。設計上の責務が分離されていないことが大きい。見た目レビューが最終判定だと思いこんだままでは、review keyの鮮度や重複の扱いが曖昧になりやすい。

実際に、公開コミットの差分から読み取れたのは、次の三点だ。

- 72a73a3: 「未定義のresearch trial完了ゲートを削除する」  
  実装・schema・永続化契約のない判定が、一度完了条件として混ざると、完了の意味が曖昧になる。

- a2691970: 「外観レビューの重複PASSを削除する」  
  PASSの数や並び順が、成果物の信頼性を保証しない。重複が残ると、同じ画面なのに別物の証拠が同列に並ぶ。

- 0a025e6: 「Wide Cargoの外観判定を現行renderへ固定する」  
  現行mainのGitHub Pages artifactを直接確認したFAILが正本として反映されている。この一文が、鮮度の重要さを最も明確に示している。

これらは、単なるUIの見た目問題ではない。レビューイベントそのものが、成果物の取り違えに耐えられていない場合に起きる、より根本的な問題だ。

## 4. 驚いた発見: 完了判定が「画面」ではなく「証跡の記録」に寄っていた

surprising_finding: いちばん驚いたのは、品質ゲートが最終的に依存しているのはrenderそのものではなく、保存されたreview keyと重複PASSの状態だったことだ。結果として、最新のrenderがFAILでも、古いPASSが残ると完了済みの見た目が維持される。

ここでいうquality gateは、技術の名前ではなく、誰が「完了」と言えるかの判断ルールだ。問題は、そのルールがartifactの鮮度を前提にしていないことだ。つまり、レビュー結果の価値は、評価そのものが優秀かどうかより、「その評価が今の成果物に対して行われたか」で決まる。

この設計哲学には、短期的な運用の便利さと、技術的な信頼性の間のtrade-offがある。便利なのは、古いPASSや旧review keyを残しておくことだ。だが私は、それを受け入れなかった。なぜなら、品質ゲートの最後で重要なのは、見た目の判定が今のrenderに対して有効かどうかだからだ。

## 5. 何が再利用できるか

この事例から出た知見は、別のプロジェクトにも持ち運べる。

- 画面・生成物・アウトプットのレビュー結果は、必ず「どのrevisionに対するものか」を明示しなければならない
- 証跡が複数あるときは、どれが唯一の完了判定なのかを決めておく必要がある
- 古い判定の残留は、見た目上は便利でも、最終判断の信頼性を壊す
- 完了の定義が曖昧なら、レビュー担当者は「見る前提」を満たしていないものに依存しやすい

つまり、重要なのは論理の構造だ。特定のリポジトリ名やtool名を外しても、同じ問題は起こる。たとえば、生成AIの出力評価、デザインレビュー、ページデプロイ検証、ドキュメントの最終確認でも、今のartifactとレビューの紐付けが曖昧なら、同じ失敗が起こりうる。

## 6. どこまでが妥当か

proof_of_value: これは公開コミットの文章そのもので、強い証拠だ。古いPASSの削除、旧review keyの除去、唯一の完了判定への置換が、コミット本文で明示されている。

ただし、この結論には明確な境界がある。私は次のことまでは言わない。

- どのレビュー手法が最良か
- どの画面が「美しい」か
- どの品質ゲートが全面的に正しいか
- すべてのreview workflowでこの設計が必須だと断定すること

これは一つの観測に基づく知見であり、設計の信頼性の問題を扱っている。よって、non_goal は「見た目の絶対評価基準の定義」だ。この記事は、見た目の価値そのものではなく、「何を信じればよいか」という判断基準を扱う。

さらに、claim_boundary は次のとおりだ。

- 支持される結論: 旧review keyや重複PASSが残ると、最新renderへの判定が不明瞭になる
- 支持されない結論: すべてのUI review workflowで古い判定が問題になる
- 重要な境界: 実際に古い記録が残るかどうかは、各workspaceの設計とデータモデルで決まる

## 7. 具体的に何をすればいいか

useful_exit: ここからは、レビューを信じる前に、次の最小チェックを入れるのがよい。

1. 判定の対象が、今のartifactかを確認する
2. review keyが最新revisionに紐付いているかを確認する
3. 重複したPASSが残っていないかを確認する
4. もし複数の判定があるなら、唯一の完了判定がどれかを確認する
5. 旧判定や削除済みkeyが完了の根拠になっていないかを確認する
6. 見た目のPASSがあっても、artifact hash やデプロイ時点が一致していなければ、判定を保留する

このチェックは、特定のCLI commandや設定値を覚える記事ではない。これはレビュー運用のdecision ruleだ。レビュー結果を「今の成果物の証拠」として扱うかどうか判断するための基準になる。

## 8. この記事が単独記事になる理由

why_this_article: 公式docsで「レビュー結果はartifactに紐付けるべき」と明文化されているわけではない。実際の現場では、見た目の評価が古い結果にくっついて、完了判定がずれる事故が起きる。公開コミットの記述がその再現証拠であり、これは「運用の設計上の教訓」として独立した記事に値する。

これは技術の使い方ではなく、判定の信頼性に関する話だ。たとえばレビュー手法や特定のCI設定だけを説明する記事では取りこぼす、設計前提と崩れたときの結果を、公開証跡で示している。

## 9. まとめ

「レビューPASS」をそのまま信じるのではなく、いつのartifactに対して出た判定かを確認する。古い証拠は、見た目が良くても完成を速くしない。むしろ、最新renderの未検証を隠してしまう。品質ゲートの本当の仕事は、最終成果物に対して意味のある証拠を残すことだ。

そのために重要なのは、評価の鮮度と唯一性を先に決めることだ。見た目の「良し悪し」は、その二つが守られて初めて信頼できる。

一次情報・再現証拠:
- https://github.com/KAFKA2306/image2outfit/commit/0a025e6e6ba1b360418b6c5ddb22e7a14ce9d7b6
- https://github.com/KAFKA2306/image2outfit/commit/a2691970b22cf7d2b135d6c9582b985e4a22a1c8
- https://github.com/KAFKA2306/image2outfit/commit/72a73a3304b1539aaaef4988da6826e29467d9dc
- https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages
