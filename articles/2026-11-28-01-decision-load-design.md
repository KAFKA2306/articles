---
title: "人間の判断負荷を増やさないAIエージェント設計"
emoji: "🧭"
type: "tech"
topics: ["ai", "aiagent", "architecture", "design", "management"]
published: false
created_at: "2026-11-28"
updated_at: "2026-11-28"
---

AIエージェントを増やすとき、実行できる仕事の量と、人間が引き受ける調整・監督・保守の負担を別々に評価したい。

Narayanan & Feigh (2026) は複数のAIエージェントを人間が監督する実験で、エージェント間の依存関係が監督負荷を増やすことを報告した [5]。一方、Cuiら (2026) は3社の開発者4,867人を対象とした無作為化実験の統合分析で、AIコーディング支援によって完了タスク数が26.08%増えたと報告している（標準誤差10.3%） [1]。

前者は監督負荷、後者は作業の生産性を測った別々の研究である。生産性の向上だけから監督負荷の削減は判断できない。

AIエージェントの設計・運用に関係する査読研究を、依存関係、監督・維持、仕組みの廃止という三つの観点で整理する。エージェントを直接対象にした実験と、一般のAI支援や人間の組織を対象にした研究は区別する。各章の括弧内は本稿の整理軸であり、確立された学術用語ではない。

## 1. エージェント間の依存と人間の調整を減らす（組織エントロピーの反転）

### AI支援で人間同士の協業はどう変わるか

Dell’Acquaら (2026) はP&Gの専門職791人を対象に、実際の商品開発課題を使った事前登録済みの企業内実験を行った [2]。

| 実験条件 | 人数とAIの有無 |
| --- | --- |
| 個人 | 1人・AIなし |
| チーム | 2人・AIなし |
| AI支援個人 | 1人・AIあり |
| AI支援チーム | 2人・AIあり |

AIを使う個人は、AIを使わない2人チームに匹敵する成果を出した。また、AIなしでは研究開発職と営業・事業系の専門職で提案の方向が異なったが、AI利用群では専門分野による偏りが小さくなった。

これは特定の商品開発課題における比較であり、企業全体で調整業務や人員を削減できることを示す結果ではない。

### 情報共有と意思決定の分散

Josephら (2026) は米国の大規模病院で、電子カルテの段階的導入を利用した準自然実験を行った [3]。

電子カルテの導入後、意思決定は分散する方向に変化した。その効果は、医療チームの構成員が互いの役割、業務手順、臨床上の状況を共通して理解している場合に強かった。

Galbraith (1974) は組織設計の選択肢を、処理すべき情報を減らす方法と、情報処理能力を高める方法に分けている [4]。前者には余裕資源の確保や仕事単位の自己完結化が含まれ、後者には情報システムへの投資や部門間の関係形成が含まれる。余裕資源や自己完結化にも費用がある。

## 2. エージェントの実行性能と人間の監督負荷を分けて評価する（判断箇所負債）

### 依存関係と監督負荷を測った実験

Narayanan & Feigh (2026) は80人を対象に、複数のAIエージェントを監督する人間の作業負荷を調べた [5]。

| 調べた設計条件 | 観測結果 |
| --- | --- |
| エージェント間の依存関係 | 依存がある条件では負荷が増えた |
| 情報の抽象化 | 依存による負荷の増加は解消されなかった |
| エラーの認識 | 依存条件では軽度のエラーが見過ごされやすかった |

エージェントの出力を要約して見せることと、エージェント同士の依存関係を減らすことは、別の設計変更である。この実験では後者に関係する負荷の差が観測された。

ソフトウェアの設計でも、Parnas (1972) は設計上の決定をモジュール内に隠し、変更の影響が他の部分へ広がらない構造を論じている [6]。ただし、実装方法によっては実行効率が低下することも指摘した。

### AIに任せる仕事の適性を区別する

Dell’Acquaら (2026) はBCGの知識労働者758人を対象に、GPT-4を利用できる場合と利用できない場合の仕事の成果を比較した [7]。

| 課題 | AI利用群の結果 |
| --- | --- |
| GPT-4が対応可能とされた18課題 | 完了した課題数が12.2%増加、平均で25.1%速く完了 |
| GPT-4の能力範囲外として選定した複雑な課題 | 正答する確率が19%低下 |

研究は、同じ知識労働の中でも、AIが役立つ課題とそうでない課題が混在することを示している。現在のすべてのモデルに同じ数値を適用できるわけではない。

### AIが生成した成果物の保守性を評価する

Borgら (2026) は151人（95%が職業開発者）を対象とする二段階の事前登録実験を行った [8]。

最初に参加者がJavaのWebアプリケーションへ機能を追加し、次に別の参加者がAIを使わずにそのコードを変更した。後半の無作為化実験では、前半でAIを使用したかどうかによる変更時間・コード品質の有意差は検出されなかった。

少なくともこの実験条件では、AIによるコード生成が後続の保守性を一律に悪化させるという証拠は得られていない。

## 3. エージェント運用の改善で廃止も検討する（自己減算型知能機関）

### 追加に偏る改善案の探索

Adamsら (2021) は *Nature* に掲載された8実験で、参加者が改善の際に有益な削除案を見落としやすいことを示した [9]。

実験4の改善条件では、削除案を少なくとも一つ挙げた参加者の割合が、削除を考えるよう促さない場合の21%から、促した場合の48%に増えた。

この研究は削除案を候補に含めることを支持するが、すべての削除が改善になることを示してはいない。

### 業務手順の廃止と部門間の調整

Matsuo (2026) は日本企業の知的財産部門の管理者385人を対象に、不要な業務手順を手放す取り組みを研究した [10]。

自由記述の分析から、部門のアンラーニング（既存の知識や手順を意図的に手放すこと）を、効率改善、ネットワークの再構成、戦略の変更に分類した。

部門内の効率改善では、上層部や他部門への連絡が少ない管理者の回答の方が、効率改善に関する記述が多かった。一方、戦略やネットワークを変える取り組みでは、部門を越える連絡が関係していた。

これは自由記述を分類した観察研究であり、連絡を減らす介入によって効率が上がると証明したものではない。業務の変更内容に応じて必要な調整が異なるという知見である。

## AIエージェント設計で区別する三つの判断

| 設計上の論点 | 根拠 |
| --- | --- |
| 処理能力の増強と調整需要の削減 | 企業内実験、医療組織の準自然実験、組織設計論 [2, 3, 4] |
| 実行時の成果と監督・保守の負荷 | 開発者の企業内実験、エージェント監督実験、保守性実験 [1, 5, 6, 7, 8] |
| 追加する改善と、不要な業務を廃止する改善 | 削除案の実験、知的財産部門のアンラーニング研究 [9, 10] |

各研究の対象と指標は異なる。人間の組織に関する研究結果を、自律エージェントの運用にそのまま一般化することはできない。三つの観点を統合したエージェント設計によって、規模の拡大と総判断負荷の減少を同時に達成できることまで、これらの研究は実証していない。

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
