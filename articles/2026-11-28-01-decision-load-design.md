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

この記事では、AIエージェントを設計・運用するときに区別すべき三つの問題を、査読済み研究から整理する。

## 1. 依存関係を減らすことと、情報を要約することを区別する

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

本稿では、情報処理能力の増強と処理需要の削減を区別する論点を「組織エントロピーの反転」として扱う。

## 2. 実行時の成果と、その後に必要な仕事を別々に測る

### AIに任せる仕事によって、正答率も変わる

Dell’Acquaら (2026) はBCGの知識労働者758人を対象に、GPT-4の利用による業務成績の変化を調べた [7]。

| 課題 | AI利用群の成績 |
| --- | --- |
| GPT-4の能力範囲内として選定した18課題 | 完了課題数12.2%増、完了速度25.1%向上 |
| 能力範囲外として選定した1課題 | 正答率が平均19パーセントポイント低下 |

後者の課題では、AIなしの正答率は84.5%だった。AIのみの群と、利用方法の説明を受けたAI利用群では、それぞれ70.6%と60%だった。

AIの利用効果は仕事によって異なる。この実験はGPT-4を対象としており、他のモデルやエージェントに数値をそのまま適用することはできない。

### 作ったコードを別の開発者が変更できるか

Borgら (2026) は151人（約95%が職業開発者）が完了した二段階の実験で、AI支援を受けて作ったコードの保守性を調べた [8]。

前半で参加者がJavaのWebアプリケーションに機能を追加し、後半では別の参加者がAIを使わずにそのコードを変更した。後半の無作為化実験の参加者は75人で、前半のAI利用の有無による変更時間やコード品質の有意差は検出されなかった。

ただし、後半の標本数では小〜中程度の差を検出する力が不足している。保守性が完全に同等だと証明したわけではない。また、この実験は仕事全体を完全自律エージェントへ委任する方式を比較していない。

実行時の生産性 [1, 7]、人間の監督負荷 [5]、後続担当者による変更時間・コード品質 [8] は、それぞれ異なる評価項目である。本稿では、実行後に必要になる判断や維持の負担に関する論点を「判断箇所負債」として扱う。

## 3. 追加する改善と、不要な仕組みを廃止する改善を比較する

### 削除案を検討するよう促すと、候補が増えた

Adamsら (2021) は8実験で、人が改善案を考えるときに有益な削除案を見落としやすいことを示した [9]。

第4実験の改善条件では、少なくとも一つの削除案を挙げた参加者の割合は、削除を考えるよう促さない群で21%、促した群で48%だった。

この結果が支持するのは、改善案の探索に削除を含めることである。削除した後の性能が常に向上することまでは示していない。

### 廃止する仕事によって、必要な調整は変わる

Matsuo (2026) は日本企業の知的財産部門の管理者385人の自由記述を分析し、既存の手順や知識を手放す取り組みを、効率改善、ネットワークの再構成、戦略の変更に分類した [10]。

上層部や他部門との連絡の関連は、取り組みの種類によって異なっていた。この調査は、連絡を減らすことで効率が上がるという因果関係を示していない。

人間の改善活動に関する研究 [9, 10] では、追加だけでなく削除を探索することや、不要な業務手順を手放す際の調整が扱われている。本稿ではこの論点を「自己減算型知能機関」と呼ぶ。自律エージェント自身の廃止による運用負荷の変化は、これらの論文では測定されていない。

## AIエージェントを増やす前に区別すること

| 設計時の問い | 研究が扱った比較 | 根拠 |
| --- | --- | --- |
| 依存関係を変えるのか、情報の見せ方を変えるのか | 依存の有無・情報の抽象度・監督負荷 | [5] |
| 処理能力を増やすのか、処理の必要性を減らすのか | 情報処理能力と情報処理需要 | [4] |
| 仕事は速くなるのか、正確になるのか | 完了件数・速度・正答率 | [1, 7] |
| 後から変更する担当者の負担はどうか | 変更時間・コード品質 | [8] |
| 追加以外の改善案は検討されたか | 削除を促す場合と促さない場合 | [9] |

この表は各研究で実際に扱われた比較を整理したものであり、新しい評価尺度や検証済みの導入手順ではない。三つの論点を統合した設計によって、規模の拡大と総判断負荷の削減を同時に達成できることも、引用した研究では実証されていない。

## 参考文献

2026年の正式掲載論文7本を中心に、組織設計・モジュール設計・削除行動の基礎研究3本を残した。2026年論文は研究対象との関連性、比較方法、掲載誌を重視して選んだ。被引用数による網羅的な順位ではない。

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
