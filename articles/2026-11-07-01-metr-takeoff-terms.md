---
title: "AI開発が2倍速でも、超知能の到来日は分からない"
emoji: "📈"
type: "tech"
topics: ["ai", "anthropic", "metr", "agi", "research"]
published: false
---

「AIの進歩が約2倍に加速した」。この数字から「超知能が2027年に来る」「知能爆発は不可避だ」と結論づけてよいのだろうか。

2026年11月5日、METRはAnthropicの内部データを使った独立評価を公開した。能力を測る指標の伸び率は従来の**1.9倍**。ただし、測ったのは主に採点しやすい課題でのモデル能力の伸びであって、AGIや超知能の到来日ではない。[METRの評価](https://metr.org/blog/2026-11-05-anthropic-ai-rd-acceleration-assessment/)

私はMETRの評価、Anthropicの安全方針、AI 2027の予測本文を突き合わせた。その結果、同じ「2倍」「加速」という言葉でも、**観測値、原因の推定、安全上の警戒線、未来のシナリオ**で意味が異なることが分かった。混ぜると、正確な数字から不正確な未来予測を作れてしまう。

## 「加速」には、まず4つの別の問いがある

| 問い | 資料が答えていること | そこからは言えないこと |
| --- | --- | --- |
| 能力は速く伸びているか | METRのAECIは2025年10月以降、従来比1.9倍の伸び率と推定 | 全ての仕事が1.9倍速くなった |
| AIが加速させたか | METRは現在の加速の大半がAI利用による可能性を重視する | 因果寄与の割合が実験で確定した |
| 安全上の警戒線を越えたか | AnthropicとMETRの評価には不一致と不確実性がある | 1.9倍という観測だけで閾値越えが確定した |
| 超知能はいつ来るか | AI 2027は複数の条件に基づくシナリオと予測を示す | METRの測定から2027年到来が証明された |

出典：[METRの総合評価](https://metr.org/blog/2026-11-05-anthropic-ai-rd-acceleration-assessment/)、[METRによるRisk Reportレビュー](https://metr.org/blog/2026-11-05-rd-section-anthropic-risk-report-august-2026-review/)、[AI 2027 Takeoff Forecast](https://ai-2027.com/research/takeoff-forecast)

## 1. 赤の女王仮説と知能爆発は、「止まれない」と「必ず到達する」の違い

**赤の女王仮説**は、Leigh Van Valenが1973年に提唱した進化生物学の仮説だ。相互に適応する相手がいる環境では、相対的な適応度を保つために変化を続けなければならない。AI開発競争に当てはめれば、競争相手が改良し続けるので自分も改良を止めにくい、という比喩になる。しかし、元の仮説は「全員が必ず超知能へ到達する」という法則ではない。[Van Valen, *A New Evolutionary Law*（1973）](https://cir.nii.ac.jp/crid/1572543024839183232)

**知能爆発（intelligence explosion）**は、I. J. Goodが1960年代に論じた、機械が自分より優れた機械の設計を助け、改良が繰り返し増幅されるという構想だ。これは自己改良の連鎖についての仮説であって、現時点でその連鎖の無制限な持続が観測されたという報告ではない。なおこの論考は「Good 1965」と引用されることが多いが、出版社の書誌ページでは1966年刊と記載されている。[Good, *Speculations Concerning the First Ultraintelligent Machine*](https://www.sciencedirect.com/science/article/pii/S0065245808604180)

**ソフトウェア駆動の知能爆発**は、その中でも計算資源の増加より、アルゴリズムや計算効率の改善が連鎖を動かす構想を指す。AI 2027のTakeoff Forecastが中心的に扱うのはこちらだ。[AI 2027の方法論](https://ai-2027.com/research/takeoff-forecast)

競争が続くことと、改良が自己増幅することと、ある到達点が保証されることは、それぞれ別の命題である。

## 2. テイクオフは「速さ」の議論であって、日付の確定ではない

**テイクオフ**は、人間水準の能力から大幅に超人的な能力へ移る過程を指す。AI 2027では、特に超人的コーダー（SC）から人工超知能（ASI）までの期間を予測している。

**ファスト／ハードテイクオフ**は、その移行が日〜月単位など短期間に集中する筋書き、**スロー／ソフトテイクオフ**は、年単位など比較的長期間にわたり社会が変化を観測できる筋書きとして使われることがある。単一主体が先行するか、複数主体が並走するかも議論されるが、これらの名称に普遍的な日数や主体数の定義があるわけではない。これは移行経路の分類であり、METRの1.9倍という成長率からどちらかを直接判定できない。[AI 2027 Takeoff Forecast](https://ai-2027.com/research/takeoff-forecast)

**AGI（汎用人工知能）**には統一された到達基準がない。そこでAI 2027は、能力を段階で記述する。[AI 2027の能力定義](https://ai-2027.com/research/takeoff-forecast)

| 段階 | 意味 | AI 2027競争分岐の作中日付 |
| --- | --- | --- |
| SC（超人的コーダー） | トップ級エンジニアのAI研究関連コーディングをより速く安く実行 | 2027年3月 |
| SAR（超人的AI研究者） | トップ級の人間AI研究者の仕事をより速く安く実行 | 2027年8月 |
| SIAR（超知能的AI研究者） | AI研究において最良の人間を桁違いに上回る | 2027年11月 |
| ASI（人工超知能） | ほぼ全ての認知的作業で最良の人間を大幅に上回る | 2027年12月 |

**ここに重要な落とし穴がある。**この表は2025年4月公開の「競争分岐」というシナリオ内の到達日だ。一方、SCが2027年3月に実現するという条件の下でのTakeoff Forecastの**中央値**は、SARが2027年7月、SIARが2027年11月、ASIが**2028年4月**である。シナリオ上の日付と条件付きモデルの中央値を同じ数字として扱ってはいけない。[AI 2027 Takeoff Forecastの比較表](https://ai-2027.com/research/takeoff-forecast)

さらに**モーダル年**は単一年として最も確率の高い年、**中央値**は累積確率が50%に達する時点だ。著者らは2025年11月22日、「2027」は当時のモーダル年で、中央値はもっと後だったと明記した。2025年12月には予測が直観的判断に大きく依存すると追記し、予測モデルもその後更新している。「AI 2027より速い／遅い」と論じる際は、**シナリオの日付、モデルの条件付き中央値、著者のその時点の予測**のどれとの比較かを指定する必要がある。[AI 2027本編](https://ai-2027.com/)、[2025年12月追記](https://ai-2027.com/research/takeoff-forecast)、[著者側の更新モデル](https://www.aifuturesmodel.com/)

## 3. METRが測った「1.9倍」の中身

**AECI**は複数のベンチマークを統合した能力指数で、METRはAnthropic独自版を使った。2025年10月以降の伸び率は、それ以前の**1.9倍（95%信頼区間1.5〜2.8倍）**。これは「約2年分の過去のベンチマーク上の進歩を約1年で達成した」という意味だ。METRの本文に登場する「年間15点から30点なら2倍」は計算方法の**例示**であり、それをそのまま実測値として引用してはいけない。[METR：指標と定義](https://metr.org/blog/2026-11-05-anthropic-ai-rd-acceleration-assessment/)

**リンク関数**は、課題の難しさの分布を仮定して、ベンチマーク得点と潜在的な能力を結ぶ関数だ。この仮定を変えると加速の推定は**1.1〜2.9倍**まで動く。95%信頼区間1.5〜2.8倍は標準的なリンク関数を採用したモデル内の統計的不確実性であり、1.1〜2.9倍は分析上の仮定を変更した幅だ。同じ種類の区間ではない。[METR：頑健性検証](https://metr.org/blog/2026-11-05-anthropic-ai-rd-acceleration-assessment/)

**ブレークポイント（変化点）**は2025年10月7日。METRが初めからその日を指定したのではなく、単一の変化点があると仮定したモデルで、データへの当てはまりから推定した日付だ。変化点がちょうど一つという前提自体は分析者が置いている。[METR：Methodology](https://metr.org/blog/2026-11-05-anthropic-ai-rd-acceleration-assessment/)

METRは学習用計算資源の増加ペースの変化だけではこの加速を説明できないとし、AI利用が現在の加速の大半を担うという見方を示した。ただし、**AIの寄与は直接観測できない反実仮想を含む推定**であり、約80%という数字もMETR自身が大きな不確実性を伴う主観的判断と位置付けている。[METR：Attribution to AI](https://metr.org/blog/2026-11-05-anthropic-ai-rd-acceleration-assessment/)

## 4. 「2倍になったら危険確定」ではない

Anthropicの**Responsible Scaling Policy（RSP）v3.4**は、重要領域の研究開発自動化に関する警戒線を定めている。そのうちMETRが説明用に**2x Acceleration Threshold**と呼んだ基準は、AI能力全体の進歩が過去の非AI支援期の水準などに比べて倍速になり、かつその倍速化にAIによる研究・開発の自動化が大きく寄与していると考えられることを求める。単一のAECI推計値が2を超えたかどうかだけの条件ではない。別に、研究者・エンジニア全員を競争力ある費用で代替できるという基準もある。[RSP v3.4原文](https://www.anthropic.com/responsible-scaling-policy)、[METRの閾値解説](https://metr.org/blog/2026-11-05-rd-section-anthropic-risk-report-august-2026-review/)

Anthropicの**2026年8月Risk Report**は、2026年7月15日時点では倍速化の警戒線に未達だと判断した。METRは11月5日のレビューで、未達との公表は自信が強すぎると批判し、**当時すでに越えていた可能性**を認めた。ただし、METRとAnthropicの担当者の多数は未達寄りであり、**7月15日のモデルによる直接的な破局リスクが低かった**というAnthropicの結論にはMETRも概ね同意している。[Anthropic 2026年8月Risk Report](https://anthropic.com/aug-2026-risk-report)、[METRによるレビュー](https://metr.org/blog/2026-11-05-rd-section-anthropic-risk-report-august-2026-review/)

警戒線を越えた可能性と、すでに破局が差し迫っていることは違う。RSP自体も企業の計画と業界全体への勧告を区別するため、「越えれば追加要件が機械的に全て発動する」と要約するのも正確ではない。[Anthropic RSP v3.4](https://www.anthropic.com/responsible-scaling-policy)

## 5. 絶滅リスクと制御問題を、加速率と混ぜない

**絶滅リスク／実存的リスク（x-risk）**は、人類の絶滅や人間が未来を方向付ける力を恒久的に失うような結果を問題にする言葉だ。**制御問題**は、高度なAIの行動や目標を人間の意図と整合させ続けられるかという問いである。AnthropicのRisk Reportが挙げる脅威の一つにも、人間が文明への制御を失う可能性が含まれる。[Anthropic Risk Report](https://anthropic.com/aug-2026-risk-report)、[METRのRisk Reportレビュー](https://metr.org/blog/2026-11-05-rd-section-anthropic-risk-report-august-2026-review/)

「敵対した高度AIに人間は勝てるのか」は**敵対が起きた場合の被害規模**に関する問いだ。「どの確率で敵対するのか」は**発生可能性**に関する別の問いだ。METRのAECIの傾きは、どちらの確率も測っていない。[METRの測定範囲・制約](https://metr.org/blog/2026-11-05-anthropic-ai-rd-acceleration-assessment/)

さらにMETRは、結論を左右する重要な内部証拠の相当部分がAnthropicによって非公開化されたことを明記している。公開報告から独立に全てを再現できる状態ではない。[METRの開示制約](https://metr.org/blog/2026-11-05-anthropic-ai-rd-acceleration-assessment/)

## 次にAIの「加速」を見たとき、私はこの順で読む

1. **何が伸びたか**：ベンチマーク能力、研究者の自己申告、生産量、実際の研究成果のどれか。
2. **何と比較したか**：過去の伸び率か、AIを使わなかった世界の推定か。後者なら原因の推定が入る。
3. **区間は何を表すか**：統計上の信頼区間か、分析前提を変えた幅か。
4. **閾値は何のためか**：能力測定か、安全上の早期警戒か。越えたら何を判断できるか。
5. **未来の日付は何か**：作中シナリオか、条件付き中央値か、著者の現在の予測か。

この5つを分ければ、加速を過小評価せず、同時に観測から「2027年の超知能」や「人類絶滅は不可避」まで飛躍することも避けられる。

今回の観測から言えるのは、**Anthropicの採点可能なモデル能力の伸びは大きく加速しており、その要因としてAI利用が有力視されている**ということまでだ。知能爆発の開始時点、テイクオフの種類、ASI到達日、敵対確率は、なお別途検証すべき問いとして残る。[METR](https://metr.org/blog/2026-11-05-anthropic-ai-rd-acceleration-assessment/)、[AI 2027](https://ai-2027.com/research/takeoff-forecast)

---

**調査基準日：2026年11月7日。** 日付と政策基準は改定され得る。再検証時は[METR評価](https://metr.org/blog/2026-11-05-anthropic-ai-rd-acceleration-assessment/)、[METRの別レビュー](https://metr.org/blog/2026-11-05-rd-section-anthropic-risk-report-august-2026-review/)、[Anthropic RSP](https://www.anthropic.com/responsible-scaling-policy)、[AI 2027](https://ai-2027.com/)、[AI Futures Model](https://www.aifuturesmodel.com/)の最新版をそれぞれ確認する。
