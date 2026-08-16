---
title: "中国AIはNVIDIAに勝つ必要がない――安いTokenを大量生産できる国は、もう負けているのか？"
emoji: "📊"
type: "tech"
topics: ["ai", "china", "semiconductor", "cloud", "data"]
published: false
---

「中国AIはNVIDIAに勝てるのか？」

この問いは分かりやすい。でも、中国のAI産業が成立する条件を考えるには、少し狭すぎる。

NVIDIAの最上位GPUに性能で勝てなくても、**十分な算力を確保し、安いTokenを大量かつ継続的に供給し、それが実際に使われ、売上になる**なら、AI産業としては成立しうる。

問題は、それが本当に起きているのかである。

そこで私は、中国AIを「強い／弱い」で採点するのをやめた。代わりに、同じ公開一次資料から同じ数量を継続取得する **China AI Quantitative Monitor** を作った。

- Monitor: https://kafka2306.github.io/semiconductor-earnings-model/china-ai/
- Raw JSON: https://kafka2306.github.io/semiconductor-earnings-model/api/v3/china-ai/index.json

この記事も結論を先に置かない。2026年8月16日時点で公開されている数量を、`算力 → Token使用量 → 価格 → 国産accelerator → deployment → AI売上` の順に見る。

## まず、1日120兆Tokenという実使用量が出ている

火山引擎はFORCE 2026で、豆包大模型の日平均使用量を **120兆Token/日** と掲載している。同じページには、100万input tokensあたり **0.15元から**、初期限流 **500万TPM** というサービス側の数量もある。

https://www.volcengine.com/event/force-2606

重要なのは、モデルのベンチマーク順位ではない。

```text
価格が安い
  ↓
APIとして供給される
  ↓
実際に大量のTokenが消費される
```

この3つを別々に確認できることだ。

もちろん120兆Token/日だけでは、中国全体のToken消費量も、採算も、NVIDIA依存度も分からない。だからMonitorでは、その値を勝手に補完しない。

## 中国全体の智能算力は2185 EFLOPS

工業和信息化部は、2026年6月末の中国の智能算力を **2185 EFLOPS（FP16）** と公表している。地域構成は東部55.9%、中部10.6%、西部32.6%、東北0.9%。全国算力施設の上架率は71.4%だった。

https://cqca.miit.gov.cn/xwdt/bsxx/art/2026/art_056ab89b9bea45d1a4161e2c56293896.html

さらに工信部は2026年のAPEC関連会見で、2025年の中国AI核心産業規模が **1.2兆元を突破**し、AI企業が **6200社超**、中国企業のopen-source model累計downloadが **100億回超**と説明している。

https://www.miit.gov.cn/xwfb/bldhd/art/2026/art_d109e2b6dc4844cc902a1f6f49712f67.html

ここで見たいのは「国家がAIを推している」という一般論ではない。供給側の母数を同じ単位で残せるかである。

## 国産acceleratorは「性能」だけでなく「何台使われたか」を見る

Huaweiは2026年7月17日、Ascend 384 SuperPoDについて **750セット超**が商用導入され、**20超の業界**で使われていると公表した。

同じ発表ではAtlas 950 SuperPoDの公開実機として、1024 cards、FP8 1 EFLOPS、FP4 2 EFLOPS、global unified memory 256 TBという数量も示している。

https://www.huawei.com/cn/news/2026/7/atlas-950-superpod

Alibabaも自社accelerator Zhenwuについて、累計 **56万個超**を出荷し、外部顧客 **400社超**、導入 **20業界超**と公表している。

https://www.alibabagroup.com/en-US/document-1994119844504535040

ここでも「H100やBlackwellより速いか」を最初の判定軸にはしない。

見るべきなのは、

- 何個出荷されたか
- 何system導入されたか
- 何社・何業界が使ったか
- software ecosystemが増えているか

である。

性能差が存在しても、供給量・cluster設計・software・価格で実用的な推論基盤が成立する可能性は残る。逆に、benchmarkだけ高くてもdeploymentが増えなければ産業供給能力の証拠にはならない。

## そして、Tokenは売上になっているのか

Baiduは2026年第1四半期に、Core AI-powered Business売上 **136億元**、AI Cloud Infrastructure売上 **88億元**を開示した。AI Cloud Infrastructureは前年同期比 **79%増**、GPU Cloudは **184%増**だった。

https://ir.baidu.com/news-releases/news-release-details/baidu-announces-first-quarter-2026-results/

Kuaishouは同じ四半期に、Kling AI売上 **6.5億元超**、前年同期比 **300%超**、2026年3月のARRを約 **5億ドル**と公表した。

https://ir.kuaishou.com/news-releases/news-release-details/kuaishou-technology-announces-first-quarter-2026-unaudited

Alibabaの2026年3月四半期ではCloud Intelligence Group売上が **416.26億元**、AI関連製品売上が **89.71億元**。AI関連製品は11四半期連続で前年同期比3桁成長と開示されている。

https://www.alibabagroup.com/zh-HK/document-1991237455038119936

モデル性能の比較だけでは、この層が抜ける。

```text
compute
  ↓
API supply
  ↓
token consumption
  ↓
production deployment
  ↓
AI revenue
```

中国AIを産業として見るなら、この連鎖を追う必要がある。

## 「NVIDIAに勝つ必要がない」は結論ではなく、反証可能な仮説にする

ここまでの数字は、中国AIがNVIDIAから独立したことを証明しない。

特に現時点で、一次資料だけでは次の重要値を十分に埋められていない。

- 中国のAI workloadに占める国産accelerator比率
- AscendやZhenwuの製造歩留まり
- HBMの実調達量
- clusterの実消費電力と総保有cost
- subsidyを除いたToken供給のunit economics
- 120兆Token/日のうち、production workloadが占める比率

この空欄は欠点ではない。**分からない値を推定値で埋めないこと自体が、このMonitorの仕様**である。

では、何が起きれば「安いTokenを大量生産できればNVIDIAに勝たなくてもよい」という仮説は弱くなるのか。

例えば、次を継続観測すればよい。

1. Token/dayが伸びない、または大きく減る
2. API価格は安いがrate limitやavailabilityが改善しない
3. 国産acceleratorの出荷・deploymentが増えない
4. AI CloudやAI application売上が継続的な利用増へつながらない
5. compute capacityは増えるが利用率が上がらない
6. 国産compute/software ecosystemのdeveloper・downloadが停滞する

逆にこれらが伸び続けるなら、「最速GPUを持つ国だけがAI産業で勝てる」という前提は弱くなる。

## 既存の中国AI論説と違うのは、意見を更新するのではなく時系列を更新すること

中国AIを巡る議論では、DeepSeek、輸出規制、Huawei Ascend、米国のCapEx、電力、国家戦略などを組み合わせれば、かなり説得力のある論説を書ける。

ただし論説には弱点がある。半年後に前提が変わったとき、文章全体を読み直さないと何が変わったか分かりにくい。

今回の中心成果は文章ではなくMonitorにした。

同じschemaに、

- compute capacity
- token/day
- API price
- accelerator shipment
- production deployment
- developer/download
- AI revenue
- measured business outcome

を追加していく。

これなら「中国AIは脅威か」という大きな問いを、毎回ゼロから論じ直す必要がない。

**前回から何の数量が増え、何が止まり、何がまだ空欄なのかを見るだけでよい。**

## 私が今後更新するもの

記事本文の結論を毎月書き換えるのではなく、公開JSONを更新する。

https://kafka2306.github.io/semiconductor-earnings-model/api/v3/china-ai/index.json

採用ルールは単純にする。

- 一次資料で確認できた数量だけ追加する
- period / metric / value / unit / qualifier / sourceを残す
- 推論値は実測値と混ぜない
- 未確認値は空欄のままにする
- 新しい開示が出たら同じmetricへ時系列を追加する

この形なら、将来「中国AIは成功した／失敗した」と言いたくなったときにも、先に結論を置かずに済む。

**NVIDIAを倒したかではなく、安いTokenをどれだけ生産し、どれだけ使われ、どれだけ売上になったか。**

私は今後、中国AIをその数字で追う。