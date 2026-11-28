---
title: "判断負荷を増やさない組織設計"
emoji: "🧭"
type: "tech"
topics: ["architecture", "design", "ai", "organization", "management"]
published: false
created_at: "2026-11-28"
updated_at: "2026-11-28"
---

生成AIによる作業の高速化は、組織全体の判断負荷の削減と同じ指標ではない。

Noy & Zhang (2023) は453人の大卒専門職を対象とした無作為化実験で、生成AIを利用した文章作成の平均所要時間が40%減少し、品質評価が18%上昇したと報告した [1]。Brynjolfsson et al. (2025) は顧客支援業務のデータを分析し、AI支援によって時間当たり解決件数が平均15%増加したと報告している [2]。

これらの研究が測定したのは個別業務の生産性であり、組織全体の管理・調整・保守に必要な判断の総量ではない。

本稿は、組織の情報処理需要、技術的負債、不要な知識や構造の除去に関する査読済み研究を、目的・評価・実践の三つの観点で整理する。各節の名称は本稿の整理軸であり、確立された学術用語ではない。

## 目的：組織エントロピーの反転

### 情報処理能力を増やすだけでなく、情報処理の必要性を減らす

Galbraith (1974) は仕事の不確実性と組織構造の関係を情報処理の観点から論じた [3]。

その組織設計論では、情報処理の必要性を減らす戦略と、情報処理能力を増やす戦略を区別する。

| 戦略 | Galbraithが示した方法 |
| --- | --- |
| 情報処理の必要性を減らす | 余裕資源の確保、自己完結的な仕事単位の形成 |
| 情報処理能力を増やす | 垂直方向の情報システムへの投資、横断的な関係の形成 |

Malone & Crowston (1994) は、調整を活動間の依存関係を管理する過程として定義した [4]。

Sablis et al. (2021) は、2社の2プロジェクトに属する9チームを対象に、インタビュー19件、フォーカスグループ9件、49人への質問紙調査を行った [5]。同じプロジェクトのチーム間でも、専門知識を得るための調整と、仕事の依存関係を管理するための調整の必要性が異なっていた。

チーム当たりの外部連絡先は、専門知識に関する調整で4〜20、仕事に関する調整で2〜30だった。調整の必要性が満たされることとチームの業績との関係については、明確な結論を得ていない [5]。

**情報処理能力の増強と、情報処理需要の削減は区別して考える。** [3]

## 評価：判断箇所負債

### 技術的負債は将来の追加作業を発生させる

Besker et al. (2019) は開発者43人への継続調査と16件のインタビューを実施し、独立したデータによる追試を行った [6]。

開発者が報告した技術的負債による時間の浪費は平均23%だった。追加時間が費やされる最も一般的な活動は追加テストであった。

この23%は対象となった開発者の報告値であり、組織全般における判断負荷の割合ではない。

### 設計上の決定を他の部分から隠す

Parnas (1972) は、処理の順番に基づくモジュール分割と、設計上の決定を各モジュールの内部に隠す分割を比較した [7]。

後者は、他の部分を理解・変更せずに個別のモジュールを変更できるようにする設計原理である。論文では開発の独立性、変更の柔軟性、理解のしやすさをモジュール分割の目的として論じる一方、実装方法によっては実行効率が低下することも指摘している。

### 自動化の評価には障害時の性能も含める

Onnasch et al. (2014) は18実験のメタ分析で、自動化の程度と人間の作業成績・作業負荷・状況認識との関係を調べた [8]。

| 評価対象 | 自動化の程度を高めた場合の結果 |
| --- | --- |
| 平常時の作業成績 | 改善 |
| 正常動作時の作業負荷 | 軽減する傾向（作業成績ほど明確ではない） |
| 自動化の故障時の成績 | 悪化 |
| 状況認識 | 悪化 |

特に情報分析の支援から行動選択の支援へ移行する段階で、悪影響が生じやすいと報告された。

**自動化の評価では平常時の性能だけでなく、故障時の性能と状況認識も扱う。** [8]

## 実践：自己減算型知能機関

### 追加だけでなく削除を検討する

Adams et al. (2021) は8実験で、問題を解決する際に人が追加による変更を優先し、有益な削除案を見落としやすいことを報告した [10]。

削除という選択肢を明示的に提示することや、改善案を繰り返し考える機会を与えることで、削除案の見落としは減少した。一方、認知的負荷を高めると、削除案が見落とされやすくなった。

この結果は削除が常に追加より優れていることを示すものではない。

### 経験から得た判断基準を組織に残す

Levitt & March (1988) は組織学習の研究を整理し、過去の経験から得た解釈が行動を導くルーチンとして組織に保存される過程を論じた [9]。組織の記憶は構成員の記憶だけではなく、ルーチンや手続きにも保持される。

### 不要になったルーチンを意図的に手放す

組織的アンラーニングと意図的忘却は、従来の知識やルーチンの再利用を意図的に抑制する過程を扱う研究領域である。

Kluge (2023) の研究レビューは、組織の適応環境、リーダーの行動、変更するルーチンの特性、個人の認知制御など、複数の水準の要因とアンラーニングの過程との関連を整理した [11]。

Klammer et al. (2025) の統合的文献レビューは、アンラーニングを継続的な取り組みとして捉え、何を手放すべきかの特定、アンラーニングを促す仕組み、新たな学習内容の業務への統合という観点を整理している [12]。

**組織の学習では、経験をルーチンとして保持することと、不要になった知識やルーチンを手放すことの双方が研究されている。** [9, 11, 12]

## 結論：研究から区別できる三つの設計判断

| 観点 | 査読研究で論じられた内容 |
| --- | --- |
| 目的 | 情報処理能力の増強と情報処理需要の削減を区別する [3, 4, 5] |
| 評価 | 技術的負債による追加作業、設計上の依存関係、自動化の正常時・故障時の性能を扱う [6, 7, 8] |
| 実践 | 削除案も探索し、組織の知識の保持とアンラーニングを区別する [9, 10, 11, 12] |

これらの研究はそれぞれ異なる対象、方法、評価指標を持つ。三つの観点を統合した組織設計が、成長と総判断負荷の減少を同時に達成することを実証した研究ではない。

## 参考文献（査読済み学術誌）

1. Noy, S., & Zhang, W. (2023). Experimental evidence on the productivity effects of generative artificial intelligence. *Science*, 381, 187–192. https://doi.org/10.1126/science.adh2586
2. Brynjolfsson, E., Li, D., & Raymond, L. (2025). Generative AI at Work. *The Quarterly Journal of Economics*, 140, 889–942. https://doi.org/10.1093/qje/qjae044
3. Galbraith, J. R. (1974). Organization Design: An Information Processing View. *Interfaces*, 4(3), 28–36. https://doi.org/10.1287/inte.4.3.28
4. Malone, T. W., & Crowston, K. (1994). The interdisciplinary study of coordination. *ACM Computing Surveys*, 26(1), 87–119. https://doi.org/10.1145/174666.174668
5. Sablis, A., Smite, D., & Moe, N. (2021). Team-external coordination in large-scale software development projects. *Journal of Software: Evolution and Process*, 33(3), e2297. https://doi.org/10.1002/smr.2297
6. Besker, T., Martini, A., & Bosch, J. (2019). Software developer productivity loss due to technical debt—A replication and extension study examining developers' development work. *Journal of Systems and Software*, 156, 41–61. https://doi.org/10.1016/j.jss.2019.06.004
7. Parnas, D. L. (1972). On the criteria to be used in decomposing systems into modules. *Communications of the ACM*, 15(12), 1053–1058. https://doi.org/10.1145/361598.361623
8. Onnasch, L., Wickens, C. D., Li, H., & Manzey, D. (2014). Human performance consequences of stages and levels of automation: An integrated meta-analysis. *Human Factors*, 56, 476–488. https://doi.org/10.1177/0018720813501549
9. Levitt, B., & March, J. G. (1988). Organizational Learning. *Annual Review of Sociology*, 14, 319–338. https://doi.org/10.1146/annurev.so.14.080188.001535
10. Adams, G. S., Converse, B. A., Hales, A. H., & Klotz, L. E. (2021). People systematically overlook subtractive changes. *Nature*, 592, 258–261. https://doi.org/10.1038/s41586-021-03380-y
11. Kluge, A. (2023). Recent findings on organizational unlearning and intentional forgetting research (2019–2022). *Frontiers in Psychology*, 14, 1160173. https://doi.org/10.3389/fpsyg.2023.1160173
12. Klammer, A., Grisold, T., Nguyen, N., & Hsu, S.-W. (2025; online 2024). Organizational unlearning as a process: What we know, what we don’t know, what we should know. *Management Review Quarterly*, 75, 2147–2171. https://doi.org/10.1007/s11301-024-00430-3
