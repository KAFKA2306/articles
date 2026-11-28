---
title: "判断負荷を増やさない組織設計"
emoji: "🧭"
type: "tech"
topics: ["architecture", "design", "ai", "organization", "management"]
published: false
created_at: "2026-11-28"
updated_at: "2026-11-28"
---

組織の判断負荷を減らすには、情報処理を速くする方法と、処理すべき情報そのものを減らす方法を区別したい。組織設計論では、この区別は1974年から論じられている [3]。

生成AIによる作業時間の短縮は、前者に関係する研究成果である。Noy & Zhang (2023) の無作為化実験では、大卒の専門職453人が文章作成課題に取り組み、ChatGPTを使った群では平均所要時間が40%減り、品質評価が18%上がった [1]。Brynjolfsson et al. (2025) の顧客対応業務の研究では、AI支援によって時間当たりの解決件数が平均15%増えた [2]。

ただし、両研究の生産性指標は個別業務を対象としており、組織全体の判断負荷を測ったものではない。

組織設計、技術的負債、組織学習の研究から、判断負荷を考えるための三つの論点を整理する。「組織エントロピーの反転」「判断箇所負債」「自己減算型知能機関」は、これらを整理するための本稿の名称である。

## 処理する情報を減らす（組織エントロピーの反転）

Galbraith (1974) は、仕事の不確実性に対応する組織設計を二つに分けた [3]。

| 方法 | 具体的な設計 |
| --- | --- |
| 情報処理の必要性を減らす | 時間や資源に余裕を持たせる。仕事を一つの組織単位で完結できるようにする |
| 情報処理能力を増やす | 階層間で情報を伝えるシステムを整える。部門を横断して調整できる関係を作る |

余裕資源を持つには費用がかかり、仕事を自己完結させると資源の専門化による利点を失うことがある。Galbraithはこうした費用も含めて設計方法を比較している [3]。

調整がどこで必要になるかを考えるには、Malone & Crowston (1994) の調整理論が参考になる。調整を、複数の活動の間にある依存関係を管理する過程として扱う [4]。

実際に、Sablis et al. (2021) は2社の2プロジェクトに属する9つのソフトウェア開発チームを調査した。49人への質問紙調査などから、チーム外の連絡先を二種類に分けている [5]。

- 専門知識を得るための連絡先：チーム当たり4〜20
- 仕事を調整するための連絡先：チーム当たり2〜30

同じプロジェクトに属していても、必要な調整はチームごとに異なった。調整の必要性が満たされることと業績との関係について、研究は明確な結論を得ていない [5]。

## 維持にかかる負担を測る（判断箇所負債）

### 技術的負債による追加作業

Besker et al. (2019) は開発者43人への継続調査と16件のインタビューを行い、別のデータでも結果を調べた [6]。

開発者が技術的負債によって浪費したと報告した時間は、平均で作業時間の23%だった。追加作業の中で最も一般的だったのは、追加のテストである。

### 変更時に他の部分を理解する必要を減らす

Parnas (1972) は、処理順に従ってプログラムを分割する方法と、設計上の決定を各モジュールの内部に隠す方法を比較した [7]。

後者は「情報隠蔽」と呼ばれる。あるモジュールを変更するときに、他のモジュールまで変更したり理解したりする必要を減らすための設計原理である。論文は開発の独立性、変更の柔軟性、理解のしやすさを論じる一方、実装方法によっては実行効率が低下することも指摘している。

### 自動化は故障時の性能まで比較する

Onnasch et al. (2014) は18実験のメタ分析で、自動化の程度と人間の作業成績、作業負荷、状況認識との関係を調べた [8]。

| 測定項目 | 自動化の程度を高めた場合 |
| --- | --- |
| 平常時の作業成績 | 改善 |
| 正常動作時の作業負荷 | 軽減する傾向 |
| 故障時の作業成績 | 悪化 |
| 状況認識 | 悪化 |

特に情報分析の支援から行動選択の支援へ移る段階で、故障時の作業成績や状況認識への悪影響が生じやすかった [8]。

自動化の評価では、正常に動作している間の作業負荷だけでなく、故障時の対応能力も考慮する必要がある。

## 不要になった仕組みを手放す（自己減算型知能機関）

### 削除も改善案に含める

Adams et al. (2021) は8実験を通じ、人は問題を解決する際に有益な削除案を見落としやすいことを示した [10]。

削除案を検討するよう促された場合や、改善案を考える機会が複数あった場合は、見落としが少なかった。認知的負荷が高い条件では、削除案が見落とされやすかった。

この研究が示したのは削除を探索する必要性であり、削除の方が常に優れているということではない。

### 残す知識と手放す知識を区別する

Levitt & March (1988) は、組織が経験から得た知識を日常の手順や行動様式（ルーチン）に残す過程を論じている [9]。組織の記憶は個人の記憶に限らず、こうしたルーチンにも保持される。

一方、既存の知識やルーチンを意図的に使わなくする過程は、組織的アンラーニングと意図的忘却の研究対象となっている。

Kluge (2023) のレビューでは、環境の変化への適応、リーダーの行動、変更するルーチンの特性、個人の認知制御などが、この過程に関係する要因として整理されている [11]。

Klammer et al. (2025) は、アンラーニングを不要な知識を手放していく時間的な過程として捉え直した。組織ごとの状況によって進み方が異なり、その過程を捉えるために長期的な研究が必要だと指摘している [12]。

## 組織設計で区別すべき三つのこと

| 比較する対象 | 根拠 |
| --- | --- |
| 情報処理能力を増やすことと、処理の必要性を減らすこと | 組織情報処理論・調整理論 [3, 4, 5] |
| 日常業務の速さと、維持や故障への対応にかかる負担 | 技術的負債・モジュール設計・自動化の研究 [6, 7, 8] |
| 必要な知識を保持することと、不要になった知識やルーチンを手放すこと | 減算の実験・組織学習の研究 [9, 10, 11, 12] |

これらの研究は、対象や評価指標が異なる。三つを統合した組織設計によって、成長と総判断負荷の削減を同時に達成できることまで実証したものではない。

## 参考文献（査読済み学術誌）

1. Noy, S., & Zhang, W. (2023). Experimental evidence on the productivity effects of generative artificial intelligence. *Science*, 381, 187–192. https://doi.org/10.1126/science.adh2586
2. Brynjolfsson, E., Li, D., & Raymond, L. (2025). Generative AI at Work. *The Quarterly Journal of Economics*, 140, 889–942. https://doi.org/10.1093/qje/qjae044
3. Galbraith, J. R. (1974). Organization Design: An Information Processing View. *Interfaces*, 4(3), 28–36. https://doi.org/10.1287/inte.4.3.28
4. Malone, T. W., & Crowston, K. (1994). The interdisciplinary study of coordination. *ACM Computing Surveys*, 26(1), 87–119. https://doi.org/10.1145/174666.174668
5. Sablis, A., Smite, D., & Moe, N. B. (2021). Team-external coordination in large-scale software development projects. *Journal of Software: Evolution and Process*, 33(3), e2297. https://doi.org/10.1002/smr.2297
6. Besker, T., Martini, A., & Bosch, J. (2019). Software developer productivity loss due to technical debt—A replication and extension study examining developers' development work. *Journal of Systems and Software*, 156, 41–61. https://doi.org/10.1016/j.jss.2019.06.004
7. Parnas, D. L. (1972). On the criteria to be used in decomposing systems into modules. *Communications of the ACM*, 15(12), 1053–1058. https://doi.org/10.1145/361598.361623
8. Onnasch, L., Wickens, C. D., Li, H., & Manzey, D. (2014). Human performance consequences of stages and levels of automation: An integrated meta-analysis. *Human Factors*, 56, 476–488. https://doi.org/10.1177/0018720813501549
9. Levitt, B., & March, J. G. (1988). Organizational Learning. *Annual Review of Sociology*, 14, 319–338. https://doi.org/10.1146/annurev.so.14.080188.001535
10. Adams, G. S., Converse, B. A., Hales, A. H., & Klotz, L. E. (2021). People systematically overlook subtractive changes. *Nature*, 592, 258–261. https://doi.org/10.1038/s41586-021-03380-y
11. Kluge, A. (2023). Recent findings on organizational unlearning and intentional forgetting research (2019–2022). *Frontiers in Psychology*, 14, 1160173. https://doi.org/10.3389/fpsyg.2023.1160173
12. Klammer, A., Grisold, T., Nguyen, N., & Hsu, S.-W. (2025; online 2024). Organizational unlearning as a process: What we know, what we don’t know, what we should know. *Management Review Quarterly*, 75, 2147–2171. https://doi.org/10.1007/s11301-024-00430-3
