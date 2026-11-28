---
title: "人間の判断負荷を増やさないAIエージェント設計"
emoji: "🧭"
type: "tech"
topics: ["ai", "aiagent", "architecture", "design", "management"]
published: false
created_at: "2026-11-28"
updated_at: "2026-11-28"
---

AIエージェント開発の目的は、AIに仕事をさせることではない。人間が引き受ける仕事を減らし、利用者が使える成果を増やすことである。

2026年、Narayanan & Feighは80人を対象とした実験で、AIエージェント間に依存関係がある条件では人間の監督負荷が増えることを報告した [5]。同年、Cuiらは3社の開発者4,867人を対象とする無作為化実験の統合分析で、AIコーディング支援によって完了タスク数が26.08%増えたと報告している（標準誤差10.3%）[1]。

仕事の処理能力と、それを監督する負担は別の指標である。

私が開発する[Kafstyler](https://github.com/KAFKA2306/kafstyler/blob/007137cb1ba50aa1c1d5409b935a8e7616c252f6/MISSION.md)では、案件や知識が増えても、読む量と重複運用を増やさないことを成功条件にしている。エージェント数、生成コード量、報告件数ではなく、利用者に届く成果と人間に残る仕事を重視する。

この方針を三つの観点に分ける。

- 目的：組織エントロピーの反転
- 評価：判断箇所負債
- 実践：自己減算型知能機関

三つの名称はKafstylerの開発思想を整理するためのもので、査読済みの学術用語や確立された評価尺度ではない。以下では、採用する開発原則と、それに関係する査読研究の結果を区別する。

## 1. 組織エントロピーの反転：規模と判断負荷を比例させない

### エージェントを増やす前に、一つで実行できないか考える

Kimら (2026) は *Nature Machine Intelligence* で、3系統のLLM、6種類のベンチマーク、単一エージェントと4種類の複数エージェント構成を比較した。プロンプト、ツール、計算予算をそろえた260構成の分析では、単一エージェントの基礎性能が、協調による性能改善の有無を説明する重要な要因だった [11]。

単一エージェントの性能が高い条件では、複数エージェントによる協調の利点が小さくなる場合がある。著者らの予測モデルは、評価対象と同じ領域の未使用構成で最適な構成を87%選択できた。この結果を未知の業務にそのまま適用できるわけではない。

Kafstylerの採用原則は、**必要な能力を満たす既存の構成を優先し、役割やエージェントの追加を目的にしないこと**である。複数構成を選ぶ場合も、同じ目的、ツール、計算予算の単一構成を比較対象に含める。

### 調整を速くする前に、調整が必要な依存関係を見直す

Narayanan & Feigh (2026) の監督実験では、エージェント間の依存がある条件で作業負荷が増え、軽度のエラーが見過ごされやすかった。情報の抽象度を変えても、依存による負荷の増加は解消されなかった [5]。

情報を要約して見せることと、調整を必要とする構造を変更することは別である。

Galbraith (1974) の組織情報処理論は、情報処理能力を増やす方法と、情報処理の必要性を減らす方法を区別した。自己完結的な仕事単位や余裕資源は後者に当たるが、資源の重複や費用との比較が必要になる [4]。

Parnas (1972) の情報隠蔽も、設計上の決定をモジュール内に置き、変更の影響範囲を限定する原理である。実装方法によっては実行効率が低下することも論じている [6]。

人間の組織に関しては、Dell’Acquaら (2026) のP&Gの専門職791人を対象とする実験で、AIを使う個人がAIを使わない2人チームに匹敵する商品開発課題の成果を出した [2]。Josephら (2026) の医療組織の研究では、電子カルテ導入後の意思決定の分散は、構成員の役割や業務手順に関する共通理解と関連した [3]。これらは人間の協業の研究であり、自律エージェント組織の調整負荷を直接測ってはいない。

### 開発原則：目的、仕事、実行を分離する

Kafstylerの[共通規約](https://github.com/KAFKA2306/kafstyler/blob/007137cb1ba50aa1c1d5409b935a8e7616c252f6/AGENTS.md)では、次のように役割を分ける。

| 管理するもの | 正本・担当 |
| --- | --- |
| 何を実現するか | MISSION |
| 次に何を解決するか | Issue |
| 共通の制約 | AGENTS.md |
| 専門的な判断と手順 | 必要なSkill |
| 確定した処理 | OS・標準CLI・mise |
| 実装の変更 | Git |
| 利用者に届いた成果 | 公開先・実機 |

同じ目的、仕様、進捗を会話や複数の台帳へ転記しない。役割の分離は、役割ごとに別のエージェントを起動することを意味しない。

この設計方針の目的は、案件の増加に合わせて共通規約や人間の調整業務を増やさないことにある。Kafstylerでは成果を利用者の入口で定義し、調査やPR、報告だけを完成扱いしない。

## 2. 判断箇所負債：判断を速くする前に、不要な判断をなくす

### AIの実行性能と維持の負担を区別する

Dell’Acquaら (2026) はBCGの知識労働者758人を対象に、GPT-4の利用による業務成績の変化を調べた [7]。

| 課題 | AI利用群の成績 |
| --- | --- |
| 能力範囲内として選定した18課題 | 完了課題数12.2%増、完了速度25.1%向上 |
| 能力範囲外として選定した1課題 | 正答率が平均19パーセントポイント低下 |

後者の正答率はAIなしで84.5%、AIのみで70.6%、AIの利用方法の説明を受けた群で60%だった。

AIの効果は課題によって異なる。この数値はGPT-4を対象とする実験の結果であり、別のモデルや自律エージェントの成績ではない。

Borgら (2026) は二段階の実験で、AI支援を受けて作ったJavaのWebアプリケーションを、別の開発者がAIなしで変更する際の保守性を調べた [8]。両段階で計151人が課題を完了し、後半の実験には75人が参加した。前半のAI利用の有無による変更時間やコード品質の有意差は検出されなかった。ただし、小〜中程度の差を検出するには標本数が不足している。

AIが生成したコードの保守性が常に悪化するという結果ではない。

実行件数、正答率、監督負荷、後続担当者の変更時間は、それぞれ分けて評価する。本稿で「判断箇所負債」と呼ぶのは、開発時だけでなく、その後の運用で判断を要求する構造に着目する考え方である。

### 開発原則：確定した処理にLLMを使わない

Kafstylerは、OSやCLIで結果が確定する処理を、LLMの自由な判断から分離する。[計算資源の3層配分](https://github.com/KAFKA2306/kafstyler/blob/007137cb1ba50aa1c1d5409b935a8e7616c252f6/AGENTS.md#計算資源の3層配分と停止契約)では、確定処理をOS・CLI、定型作業を低コストモデル、難しい判断を高知能モデルに割り当てる。

- 定期起動、差分取得、同期は既存の実行基盤を使う。
- 差分のない日常保守ではLLMを起動しない。
- 意味の判断が必要な箇所だけをLLMへ渡す。
- 既知の操作は既存CLIを実行し、未知の操作だけ必要な契約を読む。

これはKafstylerが採用している実行設計である。特定の配分が他の方式より高い性能を示したという比較実験ではない。

### 開発原則：仕事の状態を会話に閉じ込めず、失敗を隠さない

担当エージェントを固定する代わりに、後続担当が参照できる正本を定める。[Issue駆動開発](https://zenn.dev/kafka2306/articles/issue-driven-development)と[canonicalize](https://github.com/KAFKA2306/kafstyler/blob/007137cb1ba50aa1c1d5409b935a8e7616c252f6/skills/canonicalize/SKILL.md)では、仕事の状態を会話から切り離し、対象、意味、更新先を統一する。

Cemriら (2025) はNeurIPSの査読論文で、7種類の複数エージェント基盤の1,600件以上の実行履歴から、14種類の失敗をシステム設計、エージェント間の不整合、タスクの結果確認に関する三領域に分類した [12]。失敗の分析対象は、モデルの能力だけではない。

Kafstylerの[Crash-Driven Development](https://zenn.dev/kafka2306/articles/11cd731eebded1)では、失敗した処理を成功扱いせず、失敗した処理とその結果に依存する処理の停止範囲を明示する。

例えば、データの取得失敗と、正常に取得した結果が無変更だった状態は区別する。権限不足と競合も区別する。実行に不可欠な入力、依存、認可、安全、データ保全は実行時の契約として扱う。

これらは失敗の扱いに関する開発方針であり、Cemriらの分類によって特定の実装方式の優位性が証明されたわけではない。

## 3. 自己減算型知能機関：改善する仕組み自身も廃止の対象にする

### 追加より先に、削除・統合・現状維持を比較する

Adamsら (2021) は8実験で、人が改善案を考えるときに有益な削除案を見落としやすいことを示した [9]。第4実験の改善条件では、少なくとも一つの削除案を挙げた割合は、削除を考えるよう促さない群で21%、促した群で48%だった。

これは削除案の探索を支持する結果である。削除そのものが常に改善になるという結果ではない。

Matsuo (2026) は日本企業の知的財産部門の管理者385人の自由記述から、既存の手順や知識を手放す取り組みを、効率改善、ネットワークの再構成、戦略の変更に分類した [10]。上層部や他部門との連絡との関連は、取り組みの種類によって異なった。観察研究なので、連絡を減らす介入が効率を改善することを示すものではない。

### 開発原則：不要な仕事を正式に廃止する

KISSやYAGNIは、必要以上の複雑さや先回りした機能追加を避ける考え方である。Kafstylerでは、これを既に存在する仕組みと、改善活動そのものに適用する。

[decommission](https://github.com/KAFKA2306/kafstyler/blob/007137cb1ba50aa1c1d5409b935a8e7616c252f6/skills/decommission/SKILL.md)に定めた廃止対象は、コードだけではない。規約、文書、ジョブ、重複機能、旧方式も含む。

| 現行の開発方針 | 比較・保持する条件 |
| --- | --- |
| 新しい仕組みを作る前に削除・統合を検討 | 必要な成果と現在の依存関係 |
| 標準ツールが担える機能を移管 | 後継の能力と利用経路 |
| 新方式へ切り替えた後に旧方式を廃止 | 旧方式にしかない情報、識別子、利用者データ |
| 改善や保守のジョブも廃止対象にする | 起動する目的と残る必要性 |
| 変更する価値がなければ現状維持 | 正常な無変更と実行失敗の区別 |

改善担当のAIも例外にしない。不要な仕組みを維持するために、新しい仕事を探すことを成功条件にしない。

Kafstylerでは、削除件数や文書の短さも成果指標にしない。必要な判断基準、実行手順、出典、利用者データを残す。これは既存の廃止規約であり、自律エージェントの自己廃止による総運用費用の削減を実証した査読研究ではない。

## 結論：エージェントが増えたかではなく、人間に何が残ったか

三つの思想を、開発時の問いに置き換える。

| 思想 | 開発時の問い | 関連する査読研究 |
| --- | --- | --- |
| 組織エントロピーの反転 | 単一構成で足りないか。調整の必要性そのものを減らせないか | [4, 5, 6, 11] |
| 判断箇所負債 | 実行性能だけでなく、監督・引き継ぎ・保守の負担を比較しているか | [1, 5, 7, 8, 12] |
| 自己減算型知能機関 | 追加以外に削除・統合・置換・現状維持を比較したか | [9, 10, 11] |

三つを統合した開発方法の効果は、引用研究では実証されていない。表は新しい定量尺度ではなく、既存の開発方針と研究の対応を整理したものである。

私がKafstylerで目指すのは、特定のAIやセッションに依存せず、知識と成果を引き継ぎ、不要になった仕組みを退役させられる組織である。

**人間の判断負荷を増やさないことを、AIエージェント開発の制約にする。** その上で、必要な能力を増やし、利用者が使える成果を届ける。

## 参考文献

2026年の正式掲載論文8本と、組織設計・モジュール設計・削除行動の基礎研究3本、2025年のエージェント失敗分析1本を参照した。研究対象との関連性、比較方法、掲載誌・会議を重視しており、被引用数による網羅的な順位ではない。Kafstylerの規約は著者の開発方針の一次資料であり、以下の査読文献とは区別する。

1. Cui, K. Z., Demirer, M., Jaffe, S., Musolff, L., Peng, S., & Salz, T. (2026). The Effects of Generative AI on High-Skilled Work: Evidence from Three Field Experiments with Software Developers. *Management Science*, 72(11), 9408–9420. https://doi.org/10.1287/mnsc.2025.00535
2. Dell’Acqua, F., et al. (2026). The Cybernetic Teammate: A Field Experiment on Generative AI and Teamwork. *Organization Science*, 37(4), 1217–1242. https://doi.org/10.1287/orsc.2025.20702
3. Joseph, J., Wilson, A. J., Park, J., & Chow, D. (2026). Information processing, mutual understanding, and organization design in healthcare. *Strategic Management Journal*. Published online 20 August 2026. https://doi.org/10.1002/smj.70116
4. Galbraith, J. R. (1974). Organization Design: An Information Processing View. *Interfaces*, 4(3), 28–36. https://doi.org/10.1287/inte.4.3.28
5. Narayanan, R., & Feigh, K. M. (2026). Designing for Oversight: An Empirical Investigation of the Dual Impact of AI Dependency and Information Abstraction on Human Supervision in Decision-Making Teams. *International Journal of Human–Computer Interaction*, 42(18), 15444–15473. https://doi.org/10.1080/10447318.2026.2618568
6. Parnas, D. L. (1972). On the criteria to be used in decomposing systems into modules. *Communications of the ACM*, 15(12), 1053–1058. https://doi.org/10.1145/361598.361623
7. Dell’Acqua, F., et al. (2026). Navigating the Jagged Technological Frontier: Field Experimental Evidence of the Effects of Artificial Intelligence on Knowledge Worker Productivity and Quality. *Organization Science*, 37(2), 403–423. https://doi.org/10.1287/orsc.2025.21838
8. Borg, M., et al. (2026). Echoes of AI: Investigating the downstream effects of AI assistants on software maintainability. *Empirical Software Engineering*, 31(6), 161. https://doi.org/10.1007/s10664-026-10889-1
9. Adams, G. S., Converse, B. A., Hales, A. H., & Klotz, L. E. (2021). People systematically overlook subtractive changes. *Nature*, 592, 258–261. https://doi.org/10.1038/s41586-021-03380-y
10. Matsuo, M. (2026). Manager-initiated unlearning: A study of intellectual property departments in Japanese firms. *European Management Review*. Published online 1 March 2026. https://doi.org/10.1111/emre.70058
11. Kim, Y., et al. (2026). Capable language models can outgrow the benefits of collaboration. *Nature Machine Intelligence*, 8, 1157–1172. https://doi.org/10.1038/s42256-026-01268-y
12. Cemri, M., et al. (2025). Why Do Multi-Agent LLM Systems Fail? *Advances in Neural Information Processing Systems*, 38, Datasets and Benchmarks Track. https://doi.org/10.52202/085713-4082
