---
title: "第二の脳の次に必要なのは「意思決定のGit」だ——暴落で買えた理由を後から捏造しないために"
emoji: "📉"
type: "idea"
topics: ["意思決定", "LLM", "GitHub", "投資", "知識管理"]
published: false
published_at: 2026-08-13 12:33
---

NotionやObsidianのようなツールは、知識を残し、探し、つなぐことを大きく前進させた。

Obsidianは公式にMarkdown editor / knowledge base appと説明し、リンクされた知識ベースを強みとしている。Notion AIは、ワークスペース内の知識を検索し、文章を書き、タスクまで進める統合AIとして位置づけられている。

- Obsidian: https://obsidian.md/help/obsidian
- Obsidian Manifesto: https://obsidian.md/about
- Notion AI: https://www.notion.com/help/notion-ai-faqs

どちらも有用だ。

しかし、2026年に自分の投資判断を振り返って、別の欠落に気づいた。

**私が困っていたのは、知識を思い出せないことではなかった。結果を知った後に、「当時の自分が何を知り、何を推測し、何を理由に賭けたのか」を改変せず再現できないことだった。**

ノートは過去を読みやすくする。

私が必要だったのは、**過去の判断を書き換えにくくする仕組み**だった。

だから、投資判断をソフトウェアの変更履歴のように扱うことにした。

> **第二の脳が知識を保存するなら、意思決定のGitは「結果を知る前の自分」を保存する。**

この記事は「AIに銘柄を選ばせる方法」ではない。

**曖昧な人間の判断を、あとから反証・diff・再利用できる資産へ変える方法**について書く。

> これは私自身の売買判断の記録であり、特定銘柄の売買を勧めるものではありません。

## 「知識管理」と「意思決定管理」は、似ているようで目的が違う

ここでNotionやObsidianの機能比較をしたいわけではない。

Obsidian自身がGitによるversion controlを同期方法の一つとして案内しているし、Notionにもページのversion historyがある。

- ObsidianのGit利用: https://obsidian.md/help/sync-notes
- Notionのversion history: https://www.notion.com/help/duplicate-delete-and-restore-content

違いはツールではなく、**何を正準データとして残すか**だ。

私が欲しかったのは、きれいなノートではなく次の5点だった。

| 第二の脳で価値になりやすいもの | 意思決定ログで価値になるもの |
|---|---|
| 知識を保存する | 判断前の情報集合を固定する |
| 情報をリンクする | 証拠と仮説を分離して結ぶ |
| 後から検索する | 当時何を知り得たか再現する |
| 最新版へ更新する | 古い判断を消さず新しい版を追加する |
| AIで要約する | AIで観測・推論・願望の混線を検出する |
| 「何を知っているか」を増やす | 「なぜ決めたか」を監査可能にする |

この違いは、平時には小さく見える。

暴落では大きい。

## 暴落で試されたのは、知識量ではなく「判断を固定する能力」だった

2026年、手元の口座明細で確認できる範囲では、NF日経半導体株（200A）を3回買っている。

| 日付 | 買付単価 |
|---|---:|
| 4月1日 | 2,992円 |
| 4月6日 | 3,080円 |
| 7月29日 | 3,601円 |

数量は公開しない。

後からチャートを見れば、「暴落でうまく買えた」という成功談にできる。

でも、それでは何も学べない。

人間は結果を知ると、過去の思考まで少しずつ書き換える。

「あの時点で分かっていた」

「最初からこのシナリオだった」

「この材料を見て判断した」

後からなら、いくらでも整った物語を作れる。

### 投資家は市場だけでなく、自分の記憶にも負ける

これは心理学でいう**後知恵バイアス（hindsight bias）**にかなり近い。

Baruch Fischhoffの1975年の実験では、結果を知らされた人は、その結果の事後的な起こりやすさを高く評価し、しかも結果を知ったことが自分の判断へ与えた影響にほとんど気づかなかった。

https://doi.org/10.1037/0096-1523.1.3.288

投資の文脈では、Bruno BiaisとMartin Weberが2009年にさらに直接的な検証をしている。学生を対象にした実験では後知恵バイアスがボラティリティ推定を低下させ、ロンドンとフランクフルトの投資銀行家85人を対象にした実験では、**後知恵バイアスが強い参加者ほど投資課題のperformanceが低かった**。

https://doi.org/10.1287/mnsc.1090.1000

彼らは後知恵バイアスの状態を、短くこう表現している。

> **“they knew it all along.”**

「最初から分かっていた」。

まさに、投資結果を見た後の自分が作りやすい物語である。

行動ファイナンスには、ほかにも再現されてきた失敗パターンがある。ShefrinとStatmanは、利益銘柄を早く売り、損失銘柄を長く保有しやすい**disposition effect**を理論化・検証した。BarberとOdeanは35,000超の家計口座を分析し、overconfidenceの予測と整合的な過剰売買とperformance低下を報告している。

- Disposition effect: https://doi.org/10.1111/j.1540-6261.1985.tb05002.x
- Overconfidence and trading: https://doi.org/10.1162/003355301556400

ただし、この文章で後知恵バイアスを特に重視する理由は、**失敗する瞬間だけでなく、失敗から学ぶ瞬間まで壊すからだ。**

結果を知った後で「自分は最初から分かっていた」と記憶を書き換えれば、成功からも失敗からも正しいfeedbackを取れない。

だから必要なのは、もっと精密な回顧録ではない。

**結果を知る前のignoranceまで保存しておくことだ。**

そこで判断時に、最低限これだけを分離した。

1. その時点で観測できた事実
2. 自分が置いた仮説
3. 反証条件
4. 実際に選んだ行動
5. 後日の答え合わせ

さらに、結果を見る前の版をGitで固定した。

## 4月：価格が織り込む「悪い未来」に必要な条件を、現実側で探した

4月の判断は、4月1日に突然始まったものではない。

`yt3` のGit履歴には、3月17日付の分析が遅くとも3月27日時点で保存されている。

- 固定スナップショット: https://github.com/KAFKA2306/yt3/blob/b5cecf13efd4b40cb53a97b4950db5dc353ba5ba/data/memory/essences.json
- commit: https://github.com/KAFKA2306/yt3/commit/b5cecf13efd4b40cb53a97b4950db5dc353ba5ba

このmemoryに書かれた個々の数値を、今の事実として使うつもりはない。

証拠として重要なのは、**4月の買付より前から、地政学をニュースの見出しではなく、物流・供給・価格を制約する現実として考えていた版が残っている**ことだ。

米中央軍はOperation Epic Furyを公式に記録している。

https://www.centcom.mil/OPERATIONS-AND-EXERCISES/EPIC-FURY/

私は軍事リスクが存在しないと思って買ったわけではない。

疑ったのは、価格がさらに先の悪化まで織り込んでいるのではないか、という点だった。

当時の短いログには、次の記録がある。

> 3月31日 「ホルムズ海峡を諦めたんじゃないの」
>
> 4月1日 9:22 「アメリカ陸軍なにしに派遣したんだ」

言葉は雑だが、問いは明確だった。

**さらに大きな戦争をするなら、それを実現する兵力・配置・補給・政治的意思が現実に現れるはずだ。**

つまり、価格が暗黙に置いている「悪い未来」から逆算して、その未来に必要な条件を現実側で探した。

必要条件が十分に見えないなら、現実ではなく価格の方を疑う余地がある。

4月1日に買った。

### 買った直後に、自分の因果モデルが外れた

同じ4月1日のログには、次も残っている。

> 「ホルムズ海峡締まったままでも終戦したら日経上がるんだ。分からんかった。」

成功談だけ作るなら、この一文は消した方がきれいだ。

意思決定ログでは逆である。

**外れた部分こそ残す。**

私は当初、ホルムズ海峡の閉鎖そのものをかなり重く見ていた。ところが市場の反応を見て、長期戦や追加軍事作戦の確率低下を価格が先に評価し得ることを学んだ。

4月1日のホワイトハウス記録では、軍事目標が完了へ近づいているという説明と同時に、今後2〜3週間は強い攻撃を続けるとの発言も記録されている。

https://www.whitehouse.gov/releases/2026/04/president-trump-delivers-powerful-primetime-address-on-operation-epic-fury/

自分に都合のいい材料だけではなかった。

反対材料が出れば仮説を更新し、4月6日にもう一度買った。

4月8日、ホワイトハウスは停戦について発表した。

https://www.whitehouse.gov/releases/2026/04/peace-through-strength-operation-epic-fury-crushes-iranian-threat-as-ceasefire-takes-hold/

結果は自分に有利だった。

ただし、ここから「4月1日時点で停戦を予言していた」とは言えない。

再利用したいのは予言ではなく、次の判断手順だ。

> **価格が悪い未来を強く織り込んでいるなら、その未来に必要な条件を現実側で探す。条件が不足していれば価格を疑う。反対材料が出れば仮説を更新する。**

## 7月：企業が悪いのか、売り手が苦しいのかを分けた

7月は、同じ考え方を企業価値へ使った。

分析の中心に置いていたのはキオクシアだった。一方、手元の口座明細で今回確認できる7月29日の執行は、NF日経半導体株（200A）の3,601円での買付である。

**分析対象と執行対象を混ぜない。**

7月29日のログには、数時間のうちに次の記録がある。

> 12:25 「営業利益でるはず」
>
> 12:40 「信用買いの強制整理が進んでいるが、まだ整理完了とはいえない」
>
> 18:09 「やっす」
>
> 18:09 「予想PER三倍台？」
>
> 18:09 「信用　焼けてきた」

このような生ログを、そのまま「事実」に昇格させると危険だ。

JPXの公開データから信用残の変化は確認できても、追証や強制決済が実際に何株発生したかまでは直接分からない。

- https://www.jpx.co.jp/markets/statistics-equities/margin/05.html
- https://www.jpx.co.jp/markets/statistics-equities/margin/index.html

したがって、「信用買いの強制整理が下落を増幅した」は**需給仮説**として残す。

同様に「予想PER三倍台？」も、当時置いた私的な利益シナリオからの概算であり、会社予想でもETFのPERでもない。

この日の判断を3つへ分けた。

1. **実体** — 利益は本当に崩れるのか
2. **売り手** — 下落は企業価値悪化だけで説明できるのか
3. **価格** — 自分の利益予想を弱くしてもまだ安いのか

株価が下がったから安い、ではない。

### 結果を見る前に、棄却条件をGitへ置いた

翌7月30日、決算前の分析をGitHubへ残した。

- 固定スナップショット: https://github.com/KAFKA2306/semiconductor-earnings-model/blob/04590b68e6f4ec6e5ff0a41af50ddd363a57f074/docs/reports/semiconductor/2026-07-30-kioxia-nand-sector-capex.md
- commit: https://github.com/KAFKA2306/semiconductor-earnings-model/commit/04590b68e6f4ec6e5ff0a41af50ddd363a57f074

この版では情報を、

- 会社開示
- 作業仮定
- 推論
- 未確認

へ分け、さらに結果を見る前に、継続強気 / WATCH / 仮説棄却の条件を書いた。

たとえば、ASPと利益率が同時に悪化する、データセンター向け出荷が計画未達になる、在庫増加とフリーキャッシュフロー悪化が同時に起こる、といった条件なら仮説を捨てる設計だった。

ここでGitが効く。

**結果を見る前の仮説と、結果を見た後の評価を別の版にできる。**

決算資料の確認先も、後から差し替えずURLとして残す。

- キオクシアホールディングス IR: https://www.kioxia-holdings.com/ja-jp/ir.html
- 当時参照した決算資料: https://ssl4.eir-parts.net/doc/285A/tdnet/2859908/00.pdf

重要なのは、決算が良かったか悪かったかだけではない。

**決算前に自分が何を条件として置いていたかが残っていること**だ。

## 2つの局面で残ったのは、同じ3ゲートだった

4月は地政学、7月は半導体だった。

対象は違うが、判断は同じ3問へ圧縮できた。

### Gate 1: 実体は壊れたか

まず現実を見る。

実体が壊れているなら買わない。

### Gate 2: 売りは実体悪化だけで説明できるか

恐怖、レバレッジ解消、信用整理、イベント前後のポジション整理など、価値とは別の事情が売りを増幅していないかを見る。

それでも実体悪化だけで十分説明できるなら買わない。

### Gate 3: 自分が間違う弱気ケースでも安いか

強気シナリオが全部当たらないと成立しないなら買わない。

短くすると、

> **実体を見る。売り手を見る。弱気でも安いときだけ候補にする。**

```python
if fundamentals_broken:
    return "PASS"

if selling_is_explained_by_fundamentals:
    return "PASS"

if not cheap_even_in_bear_case:
    return "PASS"

return "BUY_CANDIDATE"
```

暴落そのものは買い理由ではない。

良い決算そのものも買い理由ではない。

見たいのは、**価格が暗黙に仮定している悪い世界と、現実の制約のずれ**だ。

## LLMは「第二の脳」を賢くするより、判断のlintに使う

LLMへ大量のノートを読ませれば、過去の知識を検索・要約できる。

それも便利だ。

しかし判断で一番危険なのは、検索漏れだけではない。

人間の短いメモには、観測、推測、願望、断定が混ざる。

例えば「信用が焼けている」という一言を、そのまま強い事実にすると危険だ。

そこで判断前のメモをLLMへ渡すなら、私は次のように分解させる。

```text
この時点で利用可能な情報だけを使って整理して。

1. 観測できた事実
2. 私が置いている仮説
3. 事実ではなく推論に過ぎない部分
4. この仮説を棄却する条件
5. まだ確認できていない情報

結論を強くしすぎず、観測と推論を混ぜないこと。
```

欲しいのは「買いです」という答えではない。

**自分の思考の型エラーを見つけること**だ。

LLMをアルファ生成器ではなく、思考のlintとして使う。

## Backlinkより先に、commit SHAが必要な場面がある

知識管理では、リンクを増やすほど文脈が豊かになる。

意思決定では、それだけでは足りない。

結果を知った後に元ノートを更新してしまえば、「当時の判断」は最新知識に汚染される。

だから判断時点では、最低限これだけ残す。

```markdown
# Decision Log

observed_at: 2026-07-30 12:00 JST
status: WATCH

## 観測
- ...

## 仮説
- ...

## 価格が暗黙に置いている悪いシナリオ
- ...

## 反証条件
- ...

## 未確認
- ...

## 判断
- BUY / WATCH / PASS
```

結果が出ても、この版を「正しかった形」に書き換えない。

答え合わせは別commit、または別セクションとして追加する。

記事やレビューから参照するときも、`main` だけでなくcommit SHAを含む固定URLを使う。

Gitは正解を保証しない。

しかし、**いつ何を考えていたかを、後から都合よく別物にしにくくできる。**

## 「ノートを増やす」から「判断能力を複利化する」へ

`KAFKA2306/investor` では、投資研究の情報を、公式fact、派生値、推定・予測、解釈、執行証拠へ分けている。

https://github.com/KAFKA2306/investor

`KAFKA2306/investor2` でも、仮説を登録し、その時点で利用可能だったデータを固定し、バックテスト、OOS検証、採択・棄却・保留まで証拠を残す。

- https://github.com/KAFKA2306/investor2
- https://github.com/KAFKA2306/investor2/blob/main/docs/architecture/canonical-investment-flow.md
- https://github.com/KAFKA2306/investor2/blob/main/docs/specs/time_tested_alpha_policy.md
- https://github.com/KAFKA2306/investor2/blob/main/docs/research/multi_paper_oos_summary.md

ここで気づいた。

> **定量研究ではモデルをGit管理して反証していた。裁量判断では、自分の思考をGit管理して反証すればいい。**

もちろん裁量判断とOOS検証は同じではない。

共通しているのは、**結果を見る前に条件を固定し、悪い結果も消さない**ことだ。

これを続けると、蓄積されるのは「読んだ情報」だけではなくなる。

- どの観測を重視したか
- どこで推論を飛躍させたか
- 何を反証条件に置いたか
- どの失敗パターンを繰り返したか
- 次回どの情報を先に取りに行くべきか

つまり、次の判断を安くするためのデータが残る。

**知識の複利ではなく、判断能力の複利**である。

## ObsidianでもNotionでも実装できる。重要なのは「ノート」から「Decision Object」へ変えること

ここまで読むと、「それならObsidianにGitを入れればいい」「Notionのversion historyでも残せる」と思うかもしれない。

その通りだ。

この記事はアプリの乗り換え記事ではない。

Obsidianは公式にもローカルファイルとGitを組み合わせられる。Notionにもversion historyがある。

重要なのは、アプリではなく**データモデル**だ。

ページの正準単位を「テーマ」や「資料」だけにせず、ひとつの意思決定を次のobjectとして持つ。

```yaml
decision_id: 2026-07-30-kioxia
observed_at: 2026-07-30T12:00:00+09:00
observations: []
hypotheses: []
falsifiers: []
unknowns: []
action: WATCH
evidence_urls: []
resolved_at: null
outcome: null
lessons: []
```

このobjectを結果前に固定する。

結果後は上書きせず、outcomeとlessonsを追加する。

それだけで「ノート」はかなり違うものになる。

## この仕組みで得たいのは「正解率」だけではない

この方法を導入しても、判断は外れる。

特に危ないのは、

- 実体悪化を「一時的な売り」と誤認する
- 売り手の事情を観測できないのに、強制売却だと決めつける
- 自分の強気な利益予想を「弱気ケース」と呼ぶ

といったケースだ。

LLMも間違うし、Gitも間違った仮説を正しくしてくれない。

それでも、この仕組みには価値がある。

**失敗したとき、「何を見て、どこを推論し、どの条件を見落としたか」を次の判断へ持ち越せるからだ。**

成功した判断も、失敗した判断も、再利用可能な学習データになる。

これは投資だけの話ではない。

研究なら「この実験結果が出なければ仮説を捨てる」。

障害対応なら「このログが出れば原因A、出なければAを捨てる」。

企画なら「このKPIが動かなければ仮説を見直す」。

採用なら「この証拠が取れなければ候補者評価を更新する」。

必要なのは、もっと多くのノートではない。

**結果を知る前の判断を固定し、結果とdiffし、次の判断へ再利用することだ。**

第二の脳が「忘れないためのシステム」だとすれば、私が次に欲しかったのは、

> **後知恵で自分を騙さないためのシステム**

だった。

私にとってLLMとGitは、そのための道具になった。

## 出典・検証用リンク

知識管理ツールの公式情報:

- Obsidian, What is Obsidian  
  https://obsidian.md/help/obsidian
- Obsidian Manifesto  
  https://obsidian.md/about
- Obsidian, Sync your notes across devices（Gitを含む同期方法）  
  https://obsidian.md/help/sync-notes
- Notion, What is Notion AI?  
  https://www.notion.com/help/notion-ai-faqs
- Notion, Version history  
  https://www.notion.com/help/duplicate-delete-and-restore-content

行動ファイナンス・認知バイアスの一次研究:

- Baruch Fischhoff, Hindsight is not equal to foresight: The effect of outcome knowledge on judgment under uncertainty, 1975  
  https://doi.org/10.1037/0096-1523.1.3.288
- Bruno Biais & Martin Weber, Hindsight Bias, Risk Perception, and Investment Performance, Management Science, 2009  
  https://doi.org/10.1287/mnsc.1090.1000
- Hersh Shefrin & Meir Statman, The Disposition to Sell Winners Too Early and Ride Losers Too Long, The Journal of Finance, 1985  
  https://doi.org/10.1111/j.1540-6261.1985.tb05002.x
- Brad M. Barber & Terrance Odean, Boys Will Be Boys: Gender, Overconfidence, and Common Stock Investment, The Quarterly Journal of Economics, 2001  
  https://doi.org/10.1162/003355301556400

一次資料:

- U.S. Central Command, Operation Epic Fury  
  https://www.centcom.mil/OPERATIONS-AND-EXERCISES/EPIC-FURY/
- The White House, Operation Epic Fury address  
  https://www.whitehouse.gov/releases/2026/04/president-trump-delivers-powerful-primetime-address-on-operation-epic-fury/
- The White House, ceasefire announcement  
  https://www.whitehouse.gov/releases/2026/04/peace-through-strength-operation-epic-fury-crushes-iranian-threat-as-ceasefire-takes-hold/
- KIOXIA Holdings, Investor Relations  
  https://www.kioxia-holdings.com/ja-jp/ir.html
- Japan Exchange Group, 銘柄別信用取引週末残高  
  https://www.jpx.co.jp/markets/statistics-equities/margin/05.html
- Japan Exchange Group, 個別銘柄信用取引残高表  
  https://www.jpx.co.jp/markets/statistics-equities/margin/index.html

当時の公開履歴:

- 2026-03-27時点の `yt3` memory  
  https://github.com/KAFKA2306/yt3/blob/b5cecf13efd4b40cb53a97b4950db5dc353ba5ba/data/memory/essences.json
- 上記memoryを含むcommit  
  https://github.com/KAFKA2306/yt3/commit/b5cecf13efd4b40cb53a97b4950db5dc353ba5ba
- 2026-07-30 キオクシア／NANDセクター設備投資監査  
  https://github.com/KAFKA2306/semiconductor-earnings-model/blob/04590b68e6f4ec6e5ff0a41af50ddd363a57f074/docs/reports/semiconductor/2026-07-30-kioxia-nand-sector-capex.md
- 同ファイルを追加した決算前commit  
  https://github.com/KAFKA2306/semiconductor-earnings-model/commit/04590b68e6f4ec6e5ff0a41af50ddd363a57f074

買付日・買付単価は手元の口座明細で確認した。数量は公開していない。

日々の短い引用は当時の自分自身の記録から抜粋した。公開にあたり、第三者の氏名・ハンドル・発言・会話上の個人情報は使用していない。