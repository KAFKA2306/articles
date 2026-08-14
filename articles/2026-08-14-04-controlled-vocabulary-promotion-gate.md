---
title: "用語を増やすほど検索が壊れる。294候補から1語だけ正規語へ昇格した理由"
emoji: "📚"
type: "tech"
topics: ["dataengineering", "knowledgegraph", "documentation", "testing", "ai"]
published: false
---

用語集は、語を追加するほど便利になると思っていた。

しかし実際には、追加を急ぐほど検索や集計が壊れやすい。

例えば、

```text
LLM
Large Language Model
Large Language Models
```

を見つけた順に3件登録すると、人間には同じ概念に見えてもsystemには別entityとして残る。

`KAFKA2306/nlm` では、inventory 294件のうちverifiedを32→33、needs_reviewを262→261へ更新し、`Large Language Model (LLM)` を**1件だけ**canonical glossaryへ昇格した。

- commit: https://github.com/KAFKA2306/nlm/commit/24f96d325facbad0857cdcb26d168619b20b7ee6

増やしたのは1語だけ。

しかし、その1語には、

- stable id
- preferred term
- aliases
- domain
- definition
- source URL
- verified date
- status

をまとめて持たせた。

この記事で扱うのは用語集の書き方ではない。

**人もAIも同じ概念を同じentityとして探せる状態を、候補収集の速度を落とさず維持する方法**について書く。

## 「見つけた」と「正規語にした」を同じstateにしない

新しい語を見つけること自体は簡単である。

README、論文、issue、会話、AI出力から候補は大量に集められる。

問題は、その観測をそのままcanonicalへ書くことだ。

```text
observed term
   ≠
canonical concept
```

そこで2層にする。

```text
review inventory
   ↓ verification
canonical glossary
```

candidateは広く集める。

canonicalへのpromotionだけを狭くする。

これにより、**新語を取りこぼさないことと、正規データを汚さないことを両立**できる。

## 294件中1件だけ進めても、遅いとは限らない

`nlm` のcommitでは、

```text
total        = 294
verified     = 32 → 33
needs_review = 262 → 261
```

だった。

件数だけ見ると進捗は1件である。

しかし、canonical vocabularyでは「何件増やしたか」より、**あとから同じconceptを再利用できるか**の方が重要だった。

`Large Language Model` にはaliasとして `LLM` と複数形表記を紐づけ、stable idへ寄せる。

検索はaliasでもhitできる。

集計はstable idで行える。

UIはpreferred termだけ表示できる。

1件のpromotionで、複数の利用面を同じidentityへ揃えられる。

## 一次情報は「説明文」よりidentityを固定するために使う

この例ではNLM MeSHのcontrolled vocabularyを参照した。

- https://meshb.nlm.nih.gov/record/ui?ui=D000098342
- https://id.nlm.nih.gov/mesh/D000098342.html

重要なのは、もっともらしい説明文を得ることではない。

**stable identifierとpreferred conceptを外部の正準体系へ接続できること**である。

LLMに定義を書かせることはできる。

しかし生成文だけでは、同一entityか、revisionがいつか、別名をどう扱うかまで固定できない。

AIは候補整理に使う。

promotionの根拠は検証可能なsourceへ戻す。

## promotionをtransactionとして扱う

候補をverifiedへ移すとき、複数箇所を別々に手修正するとstateが壊れる。

```text
queueから消えたがcanonicalへ入っていない
canonicalへ入ったがqueueにも残っている
verified countだけ変わった
```

そこで1件のpromotionを、

```text
candidateを選ぶ
→ sourceでidentity確認
→ canonicalへ追加
→ aliasesを固定
→ verified setへ追加
→ review queueから削除
→ count更新
→ public projection更新
→ tests
```

という1つのstate transitionとして扱う。

**用語集をMarkdownではなく、小さなdata productとして扱う。**

## countだけ合っていても壊れる

`33 + 261 = 294` なら算術上は正しい。

しかし同じ語がverifiedとreviewの両方に残っていても、件数だけでは見つけられない。

だから、

```text
count invariant
set invariant
provenance invariant
```

を分ける。

例えば、

```python
assert verified + needs_review == total
assert verified_terms.isdisjoint(needs_review_terms)
assert canonical_ids_are_unique()
assert every_verified_term_has_source()
```

のように検証する。

## UIでは「未確認」を隠さない

候補queueが大きいと、未完成に見える。

しかし全部をverifiedへ押し込むより、

```text
Verified: 33
Needs review: 261
```

と見せた方が、利用者はどこまで信頼してよいか分かる。

さらに、candidateを検索結果へ出す場合も、

```text
verified
candidate / unverified
```

を表示で分けられる。

**検索できることと、canonicalとして信頼できることを同じにしない。**

## discoveryを広くできるのは、promotionが狭いから

この設計の意外な利点は、AIによる候補収集を大胆にできることだった。

candidateが即canonicalにならないなら、多少ノイズがあってもqueueへ置ける。

```text
AI / crawler / user input
      ↓
wide discovery
      ↓
review queue
      ↓
strict promotion
```

入口は広く、出口は狭くする。

これなら知識の増加速度とcanonical品質を同時に上げやすい。

## 他のmaster dataでも同じ

このpatternは用語集だけではない。

- 製品マスタ
- 企業名寄せ
- 工場taxonomy
- タグ辞書
- 人物entity
- 業界分類

でも使える。

観測した値を即正規データにせず、candidate stateを持つ。

そしてpromotion時に、

```text
identity
preferred label
aliases
source
status
verified_at
```

を固定する。

## まず1語だけ試すなら

既存用語集から、表記揺れが多い語を1つ選ぶ。

1. observed variantsを集める
2. stable identityを確認する
3. preferred termを決める
4. aliasesを紐づける
5. sourceを残す
6. verifiedへpromotionする
7. queueから消えたことをtestする

大量一括更新より、この1件のstate transitionを正しく作る方が先でよい。

用語集の価値は、何語あるかだけではない。

**同じものを同じものとして、人もAIも迷わず使えること。**

そのために、294候補から1語だけ進めるpromotion gateが必要だった。
