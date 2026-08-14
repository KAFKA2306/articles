---
title: "暴落で買えた理由より、「当時なぜ買ったか」を後から証明できる方が大事だった"
emoji: "📉"
type: "idea"
topics: ["意思決定", "LLM", "GitHub", "投資", "クオンツ"]
published: false
published_at: 2026-08-13 12:33
---

2026年、手元の口座明細で確認できる範囲では、NF日経半導体株（200A）を3回買っている。

| 日付 | 買付単価 |
|---|---:|
| 4月1日 | 2,992円 |
| 4月6日 | 3,080円 |
| 7月29日 | 3,601円 |

数量は公開しない。

後からチャートを見れば、「暴落でうまく買えた」という成功談にできる。

でも、私が残したかったのは成功談ではなかった。

**本当に価値があるのは、結果を知った今でも「当時なぜその判断をしたか」を検証できることではないか。**

人間は結果を知ると、過去の思考まで少しずつ書き換える。

「あの時点で分かっていた」

「最初からこのシナリオだった」

「この材料を見て判断した」

後からなら、いくらでもきれいに言える。

そこで、投資判断をソフトウェアの変更履歴のように扱うことにした。

- その時点で見えていた情報を分ける
- 自分の仮説を明示する
- 間違いだと認める条件を先に書く
- LLMで観測と推論の混線を洗う
- Gitで結果を見る前の版を固定する
- 後日、結果とdiffする

この記事は「AIに銘柄を選ばせる方法」ではない。

**曖昧な人間の判断を、あとから反証・再利用できる資産へ変える方法**について書く。

> これは私自身の売買判断の記録であり、特定銘柄の売買を勧めるものではありません。

## 4月：悪い未来を実現する条件を、価格ではなく現実側で探した

4月の判断は、4月1日に突然始まったものではない。

`yt3` のGit履歴には、3月17日付の分析が遅くとも3月27日時点で保存されている。

- 固定スナップショット: https://github.com/KAFKA2306/yt3/blob/b5cecf13efd4b40cb53a97b4950db5dc353ba5ba/data/memory/essences.json
- commit: https://github.com/KAFKA2306/yt3/commit/b5cecf13efd4b40cb53a97b4950db5dc353ba5ba

このmemoryに書かれた個々の数値を、今の事実として使うつもりはない。

証拠として重要なのは、**4月の買付より前から、地政学をニュースではなく物流・供給・価格を制約する現実として考えていた版が残っている**ことだ。

米中央軍はOperation Epic Furyを公式に記録している。

https://www.centcom.mil/OPERATIONS-AND-EXERCISES/EPIC-FURY/

私は軍事リスクが存在しないと思って買ったわけではない。

疑ったのは、価格がさらに先の悪化まで織り込んでいるのではないか、という点だった。

当時の短いログには、次のような記録がある。

> 3月31日 「ホルムズ海峡を諦めたんじゃないの」
>
> 4月1日 9:22 「アメリカ陸軍なにしに派遣したんだ」

言葉は雑だが、考えていたことはかなり明確だった。

**さらに大きな戦争をするなら、それを実現する兵力・配置・補給・政治的意思が現実に現れるはずだ。**

つまり、価格が暗黙に置いている「悪い未来」から逆算して、その未来に必要な条件を現実側で探した。

必要条件が十分に見えないなら、価格の方が悪い未来を強く織り込みすぎている可能性がある。

4月1日に買った。

### 買った直後に、自分の因果モデルが外れた

同じ4月1日のログには、次も残っている。

> 「ホルムズ海峡締まったままでも終戦したら日経上がるんだ。分からんかった。」

成功談だけ作るなら、この一文は消した方がきれいだ。

しかし、意思決定を検証するなら逆である。

私は当初、ホルムズ海峡の閉鎖そのものをかなり重く見ていた。ところが市場は、海峡が直ちに正常化しなくても、長期戦や追加軍事作戦の確率が下がることを先に評価した。

**価格を観測して、自分の因果も修正した。**

4月2日のホワイトハウス記録には、軍事目標の達成見通しと同時に、今後2〜3週間は強い攻撃を続けるという発言も含まれている。

https://www.whitehouse.gov/releases/2026/04/president-trump-delivers-powerful-primetime-address-on-operation-epic-fury/

自分に都合のいい材料だけではなかった。

反対材料が出れば仮説を更新し、4月6日にもう一度買った。

4月8日、ホワイトハウスは停戦とホルムズ海峡再開への合意を発表した。

https://www.whitehouse.gov/releases/2026/04/peace-through-strength-operation-epic-fury-crushes-iranian-threat-as-ceasefire-takes-hold/

結果は自分に有利だった。

ただし、ここから「4月1日時点で停戦を予言していた」とは言えない。

再現したいのは予言ではなく、次の判断手順だ。

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

ここでも、生ログをそのまま事実へ昇格させないことが重要だった。

JPXの公開データから信用残の変化は確認できても、追証や強制決済が実際に何株発生したかまでは直接分からない。

- https://www.jpx.co.jp/markets/statistics-equities/margin/05.html
- https://www.jpx.co.jp/markets/statistics-equities/margin/index.html

したがって、「信用買いの強制整理が下落を増幅した」は**需給仮説**として残す。

同様に「予想PER三倍台？」も、当時置いた私的な利益シナリオからの概算であり、会社予想でもETFのPERでもない。

この日の判断を分けると、3つだった。

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

7月31日の会社発表では、2027年3月期第1四半期の売上収益は約1兆7,671億円、営業利益は約1兆2,700億円、親会社株主に帰属する利益は約8,422億円だった。

https://ssl4.eir-parts.net/doc/285A/tdnet/2859908/00.pdf

これは「利益は本当に崩れるのか」という実体側の問いには強い答えだった。

一方で、この決算は「信用買いの強制整理が下落の主因だった」という需給仮説を証明しない。

そこは仮説のまま残す。

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

擬似コードならこれだけだ。

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

## LLMは「答えを出す人」ではなく、思考のlintとして使う

この判断手順自体は、LLMなしでもできる。

LLMを使う理由は別にある。

人間の短いメモには、観測、推測、希望、断定が混ざる。

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

**自分の思考の混線を見つけること**だ。

LLMをアルファ生成器ではなく、思考のlintとして使う。

## Gitはコードではなく「当時の自分」をversioningする

判断時点では、最低限これだけ残せばよい。

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

記事やレビューから参照するときも、`main` ではなくcommit SHAを含む固定URLを使う。

Gitは正解を保証しない。

しかし、**いつ何を考えていたかを、後から都合よく別物にしにくくできる。**

## 定量研究でやっていたことを、人間の判断にも持ち込んだ

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

判断を記録するとき、最低限残すのは5つでよい。

1. **観測** — その時点で確認できた事実
2. **仮説** — 何が起きていると思ったか
3. **反証条件** — 何が起きたら見方を捨てるか
4. **判断** — BUY / WATCH / PASS など実際の選択
5. **答え合わせ** — 後日、何が当たり何が外れたか

再現したいのは底値ではない。

**結果を知る前の自分を残し、その判断プロセスを次にも使える状態にすること**だ。

私にとってLLMとGitは、そのための道具になった。

## 出典・検証用リンク

一次資料:

- U.S. Central Command, Operation Epic Fury  
  https://www.centcom.mil/OPERATIONS-AND-EXERCISES/EPIC-FURY/
- The White House, Operation Epic Fury address  
  https://www.whitehouse.gov/releases/2026/04/president-trump-delivers-powerful-primetime-address-on-operation-epic-fury/
- The White House, ceasefire announcement  
  https://www.whitehouse.gov/releases/2026/04/peace-through-strength-operation-epic-fury-crushes-iranian-threat-as-ceasefire-takes-hold/
- KIOXIA Holdings, FY2026 Q1 consolidated financial results  
  https://ssl4.eir-parts.net/doc/285A/tdnet/2859908/00.pdf
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
