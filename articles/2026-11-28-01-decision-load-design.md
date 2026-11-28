---
title: "人間の判断負荷を増やさないAIエージェント設計"
emoji: "🧭"
type: "tech"
topics: ["ai", "aiagent", "architecture", "design", "management"]
published: false
created_at: "2026-11-28"
updated_at: "2026-11-28"
---

AIエージェントを増やすとき、実行できる仕事の量だけでなく、人間の監督負荷も評価する。

2026年のNarayanan & Feighの実験では、複数のAIエージェントの間に依存関係がある条件で、人間の監督負荷が増えた。表示する情報の抽象度を変えても、この負荷の増加は解消されなかった [5]。

一方、同年のCuiらの研究では、3社の開発者4,867人を対象とした無作為化実験の統合分析で、AIコーディング支援によって完了タスク数が26.08%増えた（標準誤差10.3%）[1]。

二つの研究が測ったのは別の指標である。仕事を多く処理できることは、人間の監督負荷が減ったことを意味しない。

この記事では、AIエージェントの開発を、従来のソフトウェア設計原則と接続して考える。責務の分離と疎結合、性能と保守性の区別、不要な構造の削減という三つの論点を、査読済み研究から整理する。開発上の採用方針は研究結果そのものとは区別して記す。

## 1. 疎結合：エージェント間の依存関係を減らす

### 単一エージェントを比較の基準にする

Kimら (2026) は *Nature Machine Intelligence* で、プロンプト、ツール、システム全体の計算予算をそろえ、単一エージェントと4種類の複数エージェント構成を比較した [11]。3系統のLLM、6種類のベンチマークにまたがる260構成の分析では、単一エージェントの基礎性能が、協調による性能改善の有無を最も安定して説明した。

単一エージェントの性能が十分高い条件では、エージェントを追加しても性能向上を期待しにくい。著者らは、観測範囲内で構成を選択するための経験的な基準を示しているが、すべての仕事に共通する法則とはしていない。未使用の同領域構成に対する最適構成の選択率は87%だった。

したがって複数エージェントを採用する際の比較対象には、同じ仕事・ツール・計算予算を与えた単一エージェントを含める。エージェント数自体を性能指標としない。

Narayanan & Feigh (2026) は80人を対象に、AIエージェント間の依存関係と情報の抽象度を変え、人間が複数のエージェントを監督する際の負荷を調べた [5]。

| 比較した条件 | 観測結果 |
| --- | --- |
| エージェント間の依存あり・なし | 依存がある条件では監督負荷が増加 |
| 情報の抽象度 | 抽象度を変えても依存による負荷増加は解消されない |
| エラーの認識 | 依存がある条件では軽度のエラーを見過ごしやすい |

この実験で区別されたのは、エージェント同士が依存する構造と、人間に情報を提示する方法である。後者だけを変更しても、前者による負荷の増加は解消されなかった。

ソフトウェア工学にも、依存関係に着目する設計原理がある。Parnas (1972) は、変更の影響を限定するために、設計上の決定をモジュール内部に隠す方法を論じた。一方、実装によっては実行効率が低下することも指摘している [6]。

### 情報処理能力を増やす方法と、処理の必要性を減らす方法

Galbraith (1974) は組織設計を次の二方向に分けた [4]。

| 目的 | 論文で論じた方法 |
| --- | --- |
| 処理の必要性を減らす | 余裕資源の確保、仕事単位の自己完結化 |
| 処理能力を増やす | 情報システムへの投資、部門間の関係形成 |

自己完結化や余裕資源にも費用がある。情報処理需要を減らす方法が常に優れるという理論ではない。

### 人間の協業では、AIや情報システムに何ができたか

Dell’Acquaら (2026) はP&Gの専門職791人を、個人または2人チーム、AIありまたはなしの4条件に割り当て、実際の商品開発課題に取り組ませた [2]。AI支援を受けた個人は、AIを使わない2人チームに匹敵する成果を出した。専門分野による提案の偏りも小さくなった。

Josephら (2026) は病院の電子カルテ導入を調べた。意思決定は分散する方向へ変化し、その変化はチーム内での役割、手順、臨床状況に関する共通理解に関連していた [3]。

これらは人間の協業に関する研究であり、自律エージェント間の依存を減らしたときの効果を測ったものではない。

### 開発原則との接続：関心の分離と情報隠蔽

Parnasの情報隠蔽 [6] は、実装上の判断をモジュールの内部に置く考え方である。AIエージェント開発でも、責務を分けることと、担当エージェントを増やすことは別の選択である。依存による監督負荷 [5] と、複数構成の計算予算をそろえた比較 [11] を、構成選択の根拠として扱う。

Kafstylerでは、目的をMISSION、共通の作業規約をAGENTS.md、専門手順をSkill、実行を既存CLIに置く。[共通規約](https://github.com/KAFKA2306/kafstyler/blob/007137cb1ba50aa1c1d5409b935a8e7616c252f6/AGENTS.md#文書の役割と構成) に明記された役割分担であり、その削減効果を測定した研究ではない。

情報処理能力の増強と処理需要の削減を区別するこの論点を、本稿では「組織エントロピーの反転」と呼ぶ。

## 2. 保守性：生成時の性能と、将来の判断負荷を分ける

### AIに任せる仕事によって、正答率も変わる

Dell’Acquaら (2026) はBCGの知識労働者758人を対象に、GPT-4の利用による業務成績の変化を調べた [7]。

| 課題 | AI利用群の成績 |
| --- | --- |
| GPT-4の能力範囲内として選定した18課題 | 完了課題数12.2%増、完了速度25.1%向上 |
| 能力範囲外として選定した1課題 | 正答率が平均19パーセントポイント低下 |

後者の課題では、AIなしの正答率は84.5%だった。AIのみの群と、利用方法の説明を受けたAI利用群では、それぞれ70.6%と60%だった。

AIの利用効果は仕事によって異なる。この実験はGPT-4を対象としており、他のモデルやエージェントに数値をそのまま適用することはできない。

### 作ったコードを別の開発者が変更できるか

Borgら (2026) は二段階の実験で、AI支援を受けて作ったコードの保守性を調べた [8]。有効な提出物は合計151件で、その95.4%は職業開発者によるものだった。

前半で参加者がJavaのWebアプリケーションに機能を追加し、後半では別の参加者がAIを使わずにそのコードを変更した。後半の無作為化実験の参加者は75人で、前半のAI利用の有無による変更時間やコード品質の有意差は検出されなかった。

ただし、後半の標本数では小〜中程度の差を検出する力が不足している。保守性が完全に同等だと証明したわけではない。また、この実験は仕事全体を完全自律エージェントへ委任する方式を比較していない。

### 開発原則との接続：正本の分離と失敗の明示

Cemriら (2025) はNeurIPSの査読済み論文で、7種類の複数エージェント基盤から収集した1,600件以上の実行履歴を分析した [12]。14種類の失敗を、システム設計、エージェント間の不整合、タスクの結果確認に関する三領域に分類している。この分類は、失敗の分析対象をモデルの能力だけに限定していない。

実行時の生産性 [1, 7]、人間の監督負荷 [5]、後続担当者の変更時間・コード品質 [8]、実行失敗の種類 [12] は別の評価項目である。

開発上の方針として、Kafstylerでは次のように役割を定めている。

- [正本の統一](https://github.com/KAFKA2306/kafstyler/blob/007137cb1ba50aa1c1d5409b935a8e7616c252f6/skills/canonicalize/SKILL.md)：同じ対象の状態・意味・更新先を分けて保持しない。
- [Issue駆動開発](https://zenn.dev/kafka2306/articles/issue-driven-development)：仕事の状態を会話から分離し、後続担当が再開する入口を定める。
- [Crash-Driven Development](https://zenn.dev/kafka2306/articles/11cd731eebded1)：必須入力・依存・権限・実行の失敗を隠さず、失敗した処理とその結果に依存する処理の停止範囲を明確にする。

これらは著者の開発方針であり、上記研究によってKafstylerの効果が実証されたという意味ではない。本稿では実行後に必要になる判断や維持負担に関する論点を「判断箇所負債」として扱う。

## 3. 単純化：追加・統合・廃止を比較する

### 削除案を検討するよう促すと、候補が増えた

Adamsら (2021) は8実験で、人が改善案を考えるときに有益な削除案を見落としやすいことを示した [9]。

第4実験の改善条件では、少なくとも一つの削除案を挙げた参加者の割合は、削除を考えるよう促さない群で21%、促した群で48%だった。

この結果が支持するのは、改善案の探索に削除を含めることである。削除した後の性能が常に向上することまでは示していない。

### 廃止する仕事によって、必要な調整は変わる

Matsuo (2026) は日本企業の知的財産部門の管理者385人の自由記述を分析し、既存の手順や知識を手放す取り組みを、効率改善、ネットワークの再構成、戦略の変更に分類した [10]。

上層部や他部門との連絡の関連は、取り組みの種類によって異なっていた。この調査は、連絡を減らすことで効率が上がるという因果関係を示していない。

### 開発原則との接続：KISS・YAGNI・廃止

KISSは必要以上に複雑な設計を避ける考え方、YAGNIは現在必要でない機能を先回りして実装しない考え方である。削除案を探索しない偏りに関する研究 [9] は、追加だけを候補とする改善活動を見直す根拠になる。単一・複数エージェントの比較 [11] は、役割やエージェントを追加する場合にも、より単純な構成を比較対象とする理由になる。

Kafstylerの[廃止と統合の手順](https://github.com/KAFKA2306/kafstyler/blob/007137cb1ba50aa1c1d5409b935a8e7616c252f6/skills/decommission/SKILL.md) では、現状維持、統合、外部実装への移管、廃止を比較し、必要な機能、利用経路、依存、保持情報を考慮する。改善対象には、規約・ジョブ・重複機能・旧方式も含める。

この論点を本稿では「自己減算型知能機関」と呼ぶ。これは著者の開発方針を表す名称である。自律エージェントが自らの改善機構を廃止する効果は、引用した研究では直接測定されていない。

## AIエージェントを開発するときに比較すること

| 開発原則 | 比較する設計・評価項目 | 査読研究 |
| --- | --- | --- |
| 疎結合・情報隠蔽 | 依存の有無、情報の抽象度、監督負荷 | [5, 6] |
| 単純な構成の優先 | 同一計算予算の単一・複数エージェント | [11] |
| 情報処理需要の削減 | 処理能力と処理の必要性 | [4] |
| 保守性の評価 | 完了件数、正答率、後続の変更時間・コード品質 | [1, 7, 8] |
| 失敗原因の分離 | 設計、不整合、結果確認に関する失敗 | [12] |
| 減算と廃止 | 追加・削除の探索、業務手順の変更 | [9, 10] |

開発原則は、研究で扱われた選択肢や評価項目を設計時に参照するためのものだ。特定の正本管理方式、CLI、Skill構成の優位性や、三つの思想を統合した設計による総判断負荷の減少まで、これらの研究が実証したわけではない。

## 参考文献

2026年の正式掲載論文8本と、組織設計・モジュール設計・削除行動の基礎研究3本、2025年のエージェント失敗分析1本を参照した。研究対象との関連性、比較方法、掲載誌・会議を重視しており、被引用数による網羅的な順位ではない。著者の開発規約へのリンクは査読論文とは区別して本文に置いた。

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
