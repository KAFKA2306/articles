---
title: "第二の脳の次に必要なのは「意思決定のGit」だ——投資判断を後知恵バイアスから守る"
emoji: "📉"
type: "idea"
topics: ["意思決定", "LLM", "GitHub", "投資", "知識管理"]
published: true
published_at: 2026-08-13 12:33
---

NotionやObsidianは、知識を残し、探し、つなぐための道具を大きく前進させた。

Obsidianは、ローカルファイルを基盤にし、Gitを同期・版管理の手段として使う方法まで公式ヘルプで案内している。NotionにもページのVersion historyがあり、過去版を確認・復元できる。

- Obsidian Manifesto: https://obsidian.md/about
- Obsidian, Sync your notes across devices: https://obsidian.md/help/Getting%2Bstarted/Sync%2Byour%2Bnotes%2Bacross%2Bdevices
- Notion, Version history: https://www.notion.com/help/duplicate-delete-and-restore-content

だから、この記事は「NotionやObsidianには履歴がない」という話ではない。

問題は、**何を保存するか**である。

私が投資で困っていたのは、知識を思い出せないことではなかった。

結果が出たあとに、

- 当時どこまで事実を確認していたのか
- どこからが自分の推論だったのか
- 何を不確実だと思っていたのか
- 何が起きれば仮説を捨てるつもりだったのか

を、結果に汚染されず再現できないことだった。

投資で守るべきなのは、記憶そのものではない。

**結果を見る前に、自分がどこまで知り、どこから先を推論し、何をまだ知らなかったかという「当時の不確実性」である。**

ノートは過去を読みやすくする。

私が必要だったのは、**過去の判断を、結果に合わせて都合よく書き換えにくくする仕組み**だった。

> **第二の脳が知識を保存するなら、意思決定のGitは「結果を知る前の自分」を保存する。**

この記事は、AIに銘柄選択を委ねる方法ではない。

**曖昧な人間の判断を、あとから検証・反証・再利用できる対象へ変える方法**について書く。

> これは私自身の売買判断の記録であり、特定銘柄の売買を勧めるものではありません。

## 「知識管理」と「意思決定管理」は、最適化対象が違う

NotionやObsidianとGitを、単純な機能比較にしても意味はない。

ObsidianでもGitは使えるし、NotionにもVersion historyがある。したがって差はアプリそのものではなく、**保存対象のデータモデルと運用規則**にある。

私が欲しかったのは、テーマごとに整理された最新ノートではなく、判断ごとに固定された履歴だった。

| 知識管理で価値になりやすいもの | 意思決定管理で価値になるもの |
|---|---|
| 知識を保存する | 判断時点の情報集合を固定する |
| 情報をリンクする | 事実・推論・未確認を分離する |
| 最新版へ更新する | 過去版を残したまま新しい判断を追加する |
| 後から検索する | 当時何を知り得たかを再現する |
| AIで要約する | AIで観測と推論の混線を検出する |
| 「何を知っているか」を増やす | 「なぜ決めたか」を監査可能にする |

平時には、この違いは小さく見える。

暴落では大きい。

## 投資家は市場だけでなく、自分の記憶にも負ける

2026年、手元の口座明細で確認できる範囲では、NF日経半導体株（200A）を3回買っている。

| 日付 | 買付単価 |
|---|---:|
| 4月1日 | 2,992円 |
| 4月6日 | 3,080円 |
| 7月29日 | 3,601円 |

数量は公開しない。

後からチャートだけを見れば、「暴落でうまく買えた」という成功談にできる。

しかし、それでは判断から学べない。

後知恵バイアスが厄介なのは、過去の予測を過大評価するだけではない。**当時そこにあった不確実性そのものを、結果が出た後に小さく見せる**からだ。

「あの時点で分かっていた」

「最初からこのシナリオだった」

「この材料を見て判断した」

結果が確定したあとなら、過去はいくらでも整った物語に編集できる。

これは心理学でいう**後知恵バイアス（hindsight bias）**の問題に近い。

Baruch Fischhoffの1975年の実験では、結果を知らされた参加者は、その結果を事前にも予測できたはずだと過大評価し、しかも結果を知ったことが自分の判断を変えた影響に十分気づかなかった。

https://doi.org/10.1037/0096-1523.1.3.288

投資の文脈では、Bruno BiaisとMartin Weberが2009年に、より直接的な検証をしている。66人の学生を対象にした実験では、後知恵バイアスが強いほどボラティリティを低く見積もった。さらにロンドンとフランクフルトの投資銀行家85人を対象にした実験では、**後知恵バイアスが強い参加者ほど投資課題の成績が低かった**。

https://doi.org/10.1287/mnsc.1090.1000

同論文の要旨は、後知恵バイアスを短くこう表現している。

> **“they knew it all along.”**

「最初から分かっていた」。

投資結果を見た後の自分が、最も作りやすい物語である。

Fischhoffは2025年、50年分の研究を振り返り、後知恵バイアスは多様な実験・実務場面で確認されてきたと整理している。そのうえで、単に「バイアスに注意しよう」と警告するだけでは明確な効果が見られず、**過去の視点を再構成すること**の方が有望かもしれないと述べている。

https://doi.org/10.1037/xhp0001232

ここが、意思決定ログの設計とつながる。

必要なのは、結果を知った後にうまく反省する能力だけではない。

**結果を知る前の不確実性を、外部に保存しておくこと**である。

そこで私は、判断時点で最低限次の5項目を分けて残すようにした。

1. 観測できた事実
2. 自分が置いた仮説
3. 仮説を棄却する条件
4. 実際に選んだ行動
5. 後日の答え合わせ

そして、結果を見る前の版をGitで固定する。

この設計の目的は、後知恵バイアスを「克服する」ことではない。

**バイアスが働いた後でも、判断前の状態と、結果を知った後に作った物語をdiffできるようにすること**である。

## 4月：価格が織り込む「悪い未来」に必要な条件を、現実側で探した

4月の判断は、4月1日に突然始まったものではない。

`yt3` のGit履歴には、3月17日付の分析が遅くとも3月27日時点で保存されている。

- 固定スナップショット: https://github.com/KAFKA2306/yt3/blob/b5cecf13efd4b40cb53a97b4950db5dc353ba5ba/data/memory/essences.json
- commit: https://github.com/KAFKA2306/yt3/commit/b5cecf13efd4b40cb53a97b4950db5dc353ba5ba

このmemoryに含まれる個々の数値を、現在の事実として使うつもりはない。

証拠として重要なのは、**4月の買付より前から、地政学をニュースの見出しではなく、物流・供給・価格を制約する現実として考えていた版が残っている**ことだ。

米中央軍はOperation Epic Furyを公式ページで記録している。

https://www.centcom.mil/OPERATIONS-AND-EXERCISES/EPIC-FURY/

私は軍事リスクが存在しないと思って買ったわけではない。

疑ったのは、価格がさらに先の悪化まで織り込んでいるのではないか、という点だった。

当時の短いログには、次の記録がある。

> 3月31日 「ホルムズ海峡を諦めたんじゃないの」
>
> 4月1日 9:22 「アメリカ陸軍なにしに派遣したんだ」

言葉は雑だが、問いは明確だった。

**さらに大きな戦争を継続・拡大するなら、それを成立させる兵力、配置、補給、政治的意思が現実側にも現れるはずだ。**

価格が暗黙に置いている「悪い未来」から逆算し、その未来に必要な条件を現実側で探した。

必要条件が十分に確認できないなら、「現実が安全だ」と断定するのではなく、**価格が悪い未来を過大に織り込んでいる可能性**を検討できる。

4月1日に買った。

### 買った直後に、自分の因果モデルが外れた

同じ4月1日のログには、次の記録も残っている。

> 「ホルムズ海峡締まったままでも終戦したら日経上がるんだ。分からんかった。」

成功談を作るだけなら、この一文は削った方がきれいだ。

意思決定を検証するなら逆である。

**外れた部分こそ残す。**

私は当初、ホルムズ海峡の閉鎖そのものをかなり重く見ていた。ところが市場の反応を見て、海峡の正常化そのものより、長期戦や追加軍事作戦の確率低下を価格が先に評価し得ることを学んだ。

4月1日のホワイトハウス発表では、軍事目標が完了に近づいているという説明と同時に、今後2〜3週間は強い攻撃を続けるとの発言も記録されている。

https://www.whitehouse.gov/releases/2026/04/president-trump-delivers-powerful-primetime-address-on-operation-epic-fury/

自分に都合のよい材料だけが出ていたわけではない。

反対材料も含めて仮説を更新し、4月6日にもう一度買った。

4月8日、ホワイトハウスは停戦について発表した。

https://www.whitehouse.gov/releases/2026/04/peace-through-strength-operation-epic-fury-crushes-iranian-threat-as-ceasefire-takes-hold/

結果は自分に有利だった。

ただし、結果が良かったことから「4月1日時点で停戦を予見していた」と逆算してはいけない。

再利用したいのは予言ではなく、次の手順である。

> **価格が悪い未来を強く織り込んでいるなら、その未来を成立させる条件を現実側で探す。条件が不足していれば価格を疑う。反対材料が出れば仮説を更新する。**

## 7月：企業が悪いのか、売り手が苦しいのかを分けた

7月は、同じ考え方を企業価値へ使った。

分析の中心に置いていたのはキオクシアだった。一方、手元の口座明細で今回確認できる7月29日の執行は、NF日経半導体株（200A）の3,601円での買付である。

ここでは、**分析対象と執行対象を混同しない**ことも重要になる。

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

このような生ログは、当時の思考を残す証拠にはなる。

しかし、そのまま外部事実にはならない。

JPXの公開データから信用残の変化は確認できても、追証や強制決済が実際に何株発生したかまでは直接分からない。

- https://www.jpx.co.jp/markets/statistics-equities/margin/05.html
- https://www.jpx.co.jp/markets/statistics-equities/margin/index.html

したがって、「信用買いの強制整理が下落を増幅した」は**需給仮説**として扱う。

同様に「予想PER三倍台？」も、当時置いた私的な利益シナリオからの概算であり、会社予想でもETFの公表PERでもない。

この日の判断を分解すると、3つの問いになった。

1. **実体** — 利益は本当に崩れるのか
2. **売り手** — 下落は企業価値の悪化だけで説明できるのか
3. **価格** — 自分の利益予想を弱くしてもなお安いのか

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

に分け、さらに結果を見る前に、継続強気・WATCH・仮説棄却の条件を書いた。

たとえば、ASPと利益率が同時に悪化する、データセンター向け出荷が計画未達になる、在庫増加とフリーキャッシュフロー悪化が同時に起こる、といった条件なら仮説を弱める、または捨てる設計だった。

ここでGitが効く。

**結果を見る前の仮説と、結果を見た後の評価を別の版にできる。**

決算資料の参照先も、後から差し替えず残す。

- キオクシアホールディングス IR: https://www.kioxia-holdings.com/ja-jp/ir.html
- 当時参照した決算資料: https://ssl4.eir-parts.net/doc/285A/tdnet/2859908/00.pdf

重要なのは、決算が良かったか悪かったかだけではない。

**決算前に、自分が何を確認条件・棄却条件として置いていたかが残っていること**だ。

## 2つの局面で残ったのは、同じ3ゲートだった

4月は地政学、7月は半導体だった。

対象は違うが、判断は同じ3問に圧縮できた。

### Gate 1: 実体は壊れたか

まず現実を見る。

実体が壊れているなら買わない。

### Gate 2: 売りは実体悪化だけで説明できるか

恐怖、レバレッジ解消、信用整理、イベント前後のポジション調整など、企業価値とは別の事情が売りを増幅していないかを見る。

それでも実体悪化だけで十分説明できるなら、買わない。

### Gate 3: 自分が間違う弱気ケースでも安いか

強気シナリオがほぼ全部当たらないと成立しない投資なら、買わない。

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

見たいのは、**価格が暗黙に仮定している悪い世界と、現実の制約とのずれ**である。

## LLMは「答えを出す人」ではなく、判断のlintに使う

LLMへ大量のノートを読ませれば、過去の知識を検索・要約できる。

それは便利だが、判断で危険なのは検索漏れだけではない。

人間の短いメモには、観測、推測、願望、断定が混ざる。

たとえば「信用が焼けている」という一言には、観測事実と需給仮説が混在している。

そこで判断前のメモをLLMへ渡すなら、結論を出させるより、次のように分解させる。

```text
この時点で利用可能な情報だけを使って整理して。

1. 観測できた事実
2. 私が置いている仮説
3. 推論にすぎない部分
4. この仮説を棄却する条件
5. まだ確認できていない情報

観測と推論を混ぜず、結論の確度を上げすぎないこと。
```

欲しいのは「買いです」という答えではない。

**自分の思考に混入した型エラーを見つけること**だ。

LLMをアルファ生成器ではなく、思考のlintとして使う。

## Backlinkだけでは足りない。判断時点を固定する

知識管理では、リンクを増やすほど文脈が豊かになる。

意思決定では、それだけでは足りない。

結果を知った後に元ノートを最新知識へ更新してしまえば、「当時の判断」は新しい情報に汚染される。

そこで判断時点では、最低限これだけを独立したDecision Logとして残す。

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

答え合わせは別commit、または後続の記録として追加する。

GitHubで参照するときも、`main` のURLだけでなくcommit SHAを含む固定URLを使う。GitHub公式ドキュメントも、ブランチ名ではなくcommit IDを使えば、そのcommit内の正確なファイル版へ恒久的にリンクできると説明している。

https://docs.github.com/ja/repositories/working-with-files/using-files/getting-permanent-links-to-files

Git自体も、commit・tree・blobなどを内容に基づくオブジェクトIDで管理する。Gitの公式データモデルでは、Git objectは作成後に変更されないと説明されている。

https://git-scm.com/docs/gitdatamodel.html

もちろん、Gitは判断の正しさを保証しない。ブランチ履歴をrewritingする操作もできる。

それでも、**結果を見る前の版を明示的なcommitとして残し、そのSHAを外部から参照する**ことで、過去の判断を無言で最新版へ溶かすことは難しくなる。

ここで重要なのは「Gitだから正しい」ではない。

**判断前と判断後を、同じ文書の上書きではなく、比較可能な別状態として保存すること**である。

## 「ノートを増やす」から「判断能力を複利化する」へ

`KAFKA2306/investor` では、投資研究の情報を、公式fact、派生値、推定・予測、解釈、執行証拠へ分けている。

https://github.com/KAFKA2306/investor

`KAFKA2306/investor2` でも、仮説を登録し、その時点で利用可能だったデータを固定し、バックテスト、OOS検証、採択・棄却・保留まで証拠を残す。

- https://github.com/KAFKA2306/investor2
- https://github.com/KAFKA2306/investor2/blob/main/docs/architecture/canonical-investment-flow.md
- https://github.com/KAFKA2306/investor2/blob/main/docs/specs/time_tested_alpha_policy.md
- https://github.com/KAFKA2306/investor2/blob/main/docs/research/multi_paper_oos_summary.md

そこで気づいた。

> **定量研究ではモデルをGit管理して反証していた。裁量判断では、自分の思考も同じように反証可能な形で残せばいい。**

もちろん、裁量判断とOOS検証は同じではない。

共通しているのは、**結果を見る前に条件を固定し、外れた結果も消さない**ことだ。

これを続けると、蓄積されるのは「読んだ情報」だけではなくなる。

- どの観測を重視したか
- どこで推論を飛躍させたか
- 何を反証条件に置いたか
- どの失敗パターンを繰り返したか
- 次回どの情報を先に取りに行くべきか

つまり、次の判断を安くするためのデータが残る。

**知識の複利ではなく、判断能力の複利**である。

## ObsidianでもNotionでも実装できる。重要なのは「ノート」から「Decision Object」へ変えること

ここまで読むと、「それならObsidianにGitを入れればいい」「NotionのVersion historyでも残せる」と思うかもしれない。

その通りだ。

この記事はアプリの乗り換え記事ではない。

重要なのは、アプリより**データモデルと運用規則**である。

ページの正準単位を「テーマ」や「資料」だけにせず、ひとつの意思決定を独立したobjectとして持つ。

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

結果を見る前に、このobjectを固定する。

結果が出た後は、元の観測や仮説を「正しかった形」に修正せず、`outcome` と `lessons` を後続情報として追加する。

これだけで、ノートは単なる知識の置き場ではなく、**意思決定の検証データ**になる。

## 正解率より、学習可能性を守る

この方法を導入しても、判断は外れる。

実体悪化を一時的な売りと誤認することもある。売り手の事情を観測できていないのに、強制売却だと決めつけることもある。自分に都合のよい利益予想を「弱気ケース」と呼んでしまうこともある。

LLMも間違う。Gitも、間違った仮説を正しくしてくれない。

それでも、この仕組みには価値がある。

**失敗したとき、「何を見て、どこを推論し、どの条件を見落としたか」を次の判断へ持ち越せるからだ。**

行動ファイナンスでは、後知恵バイアス以外にも、利益銘柄を早く売り損失銘柄を長く持ちやすいdisposition effectや、overconfidenceと過剰売買の関係が研究されてきた。

- Shefrin & Statman, 1985: https://doi.org/10.1111/j.1540-6261.1985.tb05002.x
- Barber & Odean, 2001: https://doi.org/10.1162/003355301556400

ただし、この記事で後知恵バイアスを特に重視する理由は、**判断時の失敗だけでなく、失敗から学ぶ過程そのものを壊すから**である。

結果を知った後に、「自分は最初から分かっていた」と過去を再構成してしまえば、成功からも失敗からも正しいフィードバックを取れない。

必要なのは、もっと多くのノートではない。

**結果を知る前の判断を固定し、結果とdiffし、次の判断へ再利用すること**だ。

第二の脳が「忘れないためのシステム」だとすれば、私が次に欲しかったのは、

> **後知恵で自分を騙さないためのシステム**

だった。

私にとってLLMとGitは、そのための道具になった。

## 出典・検証用リンク

知識管理・Git:

- Obsidian Manifesto  
  https://obsidian.md/about
- Obsidian, Sync your notes across devices  
  https://obsidian.md/help/Getting%2Bstarted/Sync%2Byour%2Bnotes%2Bacross%2Bdevices
- Notion, Version history  
  https://www.notion.com/help/duplicate-delete-and-restore-content
- GitHub Docs, ファイルへのパーマリンクを取得する  
  https://docs.github.com/ja/repositories/working-with-files/using-files/getting-permanent-links-to-files
- Git, core data model  
  https://git-scm.com/docs/gitdatamodel.html

行動ファイナンス・認知バイアス:

- Baruch Fischhoff, *Hindsight is not equal to foresight: The effect of outcome knowledge on judgment under uncertainty*, 1975  
  https://doi.org/10.1037/0096-1523.1.3.288
- Bruno Biais & Martin Weber, *Hindsight Bias, Risk Perception, and Investment Performance*, Management Science, 2009  
  https://doi.org/10.1287/mnsc.1090.1000
- Baruch Fischhoff, *Fifty years of hindsight bias research—Reflection on Fischhoff (1975)*, 2025  
  https://doi.org/10.1037/xhp0001232
- Hersh Shefrin & Meir Statman, *The Disposition to Sell Winners Too Early and Ride Losers Too Long*, The Journal of Finance, 1985  
  https://doi.org/10.1111/j.1540-6261.1985.tb05002.x
- Brad M. Barber & Terrance Odean, *Boys Will Be Boys: Gender, Overconfidence, and Common Stock Investment*, The Quarterly Journal of Economics, 2001  
  https://doi.org/10.1162/003355301556400

一次資料:

- U.S. Central Command, Operation Epic Fury  
  https://www.centcom.mil/OPERATIONS-AND-EXERCISES/EPIC-FURY/
- The White House, Operation Epic Fury address, April 1, 2026  
  https://www.whitehouse.gov/releases/2026/04/president-trump-delivers-powerful-primetime-address-on-operation-epic-fury/
- The White House, ceasefire announcement, April 8, 2026  
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