---
title: "AI組織は成長するほど管理が楽になるべきだ"
emoji: "🧭"
type: "tech"
topics: ["ai", "aiagent", "architecture", "design", "management"]
published: false
created_at: "2026-11-28"
updated_at: "2026-11-28"
---

エージェントを増やす前に、何を増やすのかを決める。利用者が使える成果か、それともAIの稼働件数か。人間の負担も独立して測る。

私が開発するKafstylerでは、案件と知識が増えても読む量と重複運用を増やさないことを成功条件にしている。本稿ではこの目標を「組織エントロピーの反転」と呼ぶ。設計上の定義と観測手順は著者の提案であり、既に査読で確立された理論・規格ではない。

## 1. 問題：仕事が増えることと、人間の負担が減ることは違う

Cuiら (2026) は3社の開発者4,867人を対象にした無作為化実験の統合分析で、AIコーディング支援によって完了タスク数が26.08%増えたと報告した（標準誤差10.3%）[1]。

一方、Narayanan & Feigh (2026) の80人を対象とする監督実験では、AIエージェント間に依存関係がある条件で人間の作業負荷が増えた。情報の抽象度を変えてもその増加は解消されなかった [2]。

異なる実験の結果である。実行時の生産性の上昇だけでは、管理負荷の減少は分からない。

## 2. 中心命題：成長の条件に総管理負荷を含める

[KafstylerのMISSION](https://github.com/KAFKA2306/kafstyler/blob/007137cb1ba50aa1c1d5409b935a8e7616c252f6/MISSION.md)では、利用者に成果を届けること、担当AIが変わっても再開できること、差分のない保守でLLMを起動しないことを成功条件に置く。

必要な成果・品質・安全性を維持した上で、成果と能力が増えても総管理負荷を増やさない。さらに減少させることを目標とする。これはKafstylerの価値判断であり、あらゆる組織で達成できるという経験則ではない。

## 3. 定義：何を成長と負荷として扱うか

| 項目 | 本稿の定義 |
| --- | --- |
| 成果 | 利用者の入口で利用できる仕事の結果 |
| 能力 | 必要な品質・安全性で実行可能な仕事の範囲 |
| 規模 | 案件数、利用者数、仕事量など、対象に応じて固定する指標 |
| 管理負荷 | 人間の探索・判断・調整・監督・引き継ぎ・維持に使う時間と関連費用 |

成果と能力の拡大に伴って総管理負荷が減る状態を反転とする。単位当たりの負荷だけが減る状態は効率化と区別する。熱力学のエントロピーを計測するという意味ではない。

## 4. 仕組み：処理能力より先に処理需要を見る

Galbraith (1974) は、情報処理能力を増やす方法と処理の必要性を減らす方法を区別した。自己完結的な仕事単位や余裕資源は後者に当たるが、資源の重複や費用との比較が必要になる [3]。

Kimら (2026) は3系統のLLM、6種類のベンチマークにまたがる260構成について、同じプロンプト・ツール・計算予算で単一エージェントと4種類の複数構成を比較した。単一エージェントの基礎性能は協調の利点を説明する重要な要因だった [4]。

処理能力を増やす設計と、調整の必要性を減らす設計を別の候補として比較する。複数構成が常に劣るという結論ではない。

## 5. 測定：総負荷と成果当たり負荷を併記する

次の観測項目は提案仕様である。

| 指標 | 単位・条件 |
| --- | --- |
| 利用可能な成果 | 同じ種類・受入条件の完了件数 |
| 能力 | 対応可能な業務の範囲と各受入条件 |
| 総管理時間 | 人時間／観測期間 |
| 成果当たり管理時間 | 人時間／完了件数 |
| 運用費用 | 円／観測期間 |
| 品質・安全 | 業務固有の既存基準、失敗・手戻り |

異質な成果を件数で合算せず、種類ごとに比較する。時間と金額も換算根拠なしに加算しない。成果件数がゼロなら成果当たり時間は定義しない。

## 6. 実践：比較対象と成功条件を先に決める

1. 成果、能力、必須条件、組織の範囲、観測期間を決める。
2. 既存の業務履歴と利用先から、変更前の成果と管理負荷を把握する。
3. エージェントを追加する案と、既存構成を活用する案を比較する。
4. 同じ仕事の種類・受入条件で変更前後を観測する。繁忙期や仕事の難易度が異なる場合は分けて扱う。
5. 第2部で負荷の発生源を特定し、第3部の介入後に同じ指標へ戻る。

観測できなかった値は未測定とする。既存の記録で足りるなら、新しい管理台帳を作らない。

## 7. 根拠：協業と意思決定に関する実測

Dell’Acquaら (2026) はP&Gの専門職791人を対象とする商品開発課題の実験で、AIを利用する個人がAIなしの2人チームに匹敵する成果を出したと報告した [5]。Josephら (2026) の病院の電子カルテ導入研究では、意思決定の分散とチーム内の共通理解との関連が報告された [6]。

いずれも人間の協業の研究であり、自律エージェント組織の総管理負荷を直接測った結果ではない。

参照実装として、Kafstylerの[作業規約](https://github.com/KAFKA2306/kafstyler/blob/007137cb1ba50aa1c1d5409b935a8e7616c252f6/AGENTS.md)は、目的をMISSION、仕事をIssue、実装をGit、成果を利用先に分離している。この分担は公開された設計上の事実であり、負荷反転の実測結果ではない。

## 8. 反証条件：仕事を減らしただけでは成功としない

成果や必要な能力が失われた、品質や安全性が低下した、別の担当者や利用者へ負担を移した場合は反転と判定しない。

成果が増えても総管理負荷が増えたなら、成果当たりの負荷が改善していても反転は未達である。比較条件がそろわない場合は判定を保留する。

## 9. 標準仕様案：同じ条件で結果を引き継ぐ

入力は対象範囲、成果の受入条件、観測期間、比較対象、必須の品質・安全条件。出力は成果量、能力、総管理時間、成果当たり時間、運用費用、品質・安全性、未測定項目とする。

この出力を第2部の原因分析、第3部の変更へ渡す。変更後は同じ観測条件に戻す。業務固有の成果単位は置き換えられるが、他分野での有効性は未実証である。


## 連載の位置づけ

本稿は成功条件を定義する。 三部作の出力は、目的→測定→介入→変更後の観測という順に接続する。

- 第1部：組織エントロピーの反転（本稿）
- 第2部：[判断箇所負債](https://github.com/KAFKA2306/articles/blob/main/articles/2026-11-28-02-decision-point-debt.md)
- 第3部：[自己減算型知能機関](https://github.com/KAFKA2306/articles/blob/main/articles/2026-11-28-03-self-subtracting-agents.md)

## 参考文献

1. Cui, K. Z., Demirer, M., Jaffe, S., Musolff, L., Peng, S., & Salz, T. (2026). The Effects of Generative AI on High-Skilled Work: Evidence from Three Field Experiments with Software Developers. *Management Science*, 72(11), 9408–9420. https://doi.org/10.1287/mnsc.2025.00535
2. Narayanan, R., & Feigh, K. M. (2026). Designing for Oversight: An Empirical Investigation of the Dual Impact of AI Dependency and Information Abstraction on Human Supervision in Decision-Making Teams. *International Journal of Human–Computer Interaction*, 42(18), 15444–15473. https://doi.org/10.1080/10447318.2026.2618568
3. Galbraith, J. R. (1974). Organization Design: An Information Processing View. *Interfaces*, 4(3), 28–36. https://doi.org/10.1287/inte.4.3.28
4. Kim, Y., et al. (2026). Capable language models can outgrow the benefits of collaboration. *Nature Machine Intelligence*, 8, 1157–1172. https://doi.org/10.1038/s42256-026-01268-y
5. Dell’Acqua, F., et al. (2026). The Cybernetic Teammate: A Field Experiment on Generative AI and Teamwork. *Organization Science*, 37(4), 1217–1242. https://doi.org/10.1287/orsc.2025.20702
6. Joseph, J., Wilson, A. J., Park, J., & Chow, D. (2026). Information processing, mutual understanding, and organization design in healthcare. *Strategic Management Journal*. Published online 20 August 2026. https://doi.org/10.1002/smj.70116
