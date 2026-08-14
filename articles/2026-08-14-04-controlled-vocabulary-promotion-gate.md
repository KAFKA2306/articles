---
title: "候補語をそのまま正規語にしない。用語集をpromotion gateで育てる"
emoji: "📚"
type: "tech"
topics: ["dataengineering", "knowledgegraph", "documentation", "testing", "ai"]
published: false
---

AIやデータ基盤を運用していると、新しい用語が次々に増えます。

`LLM`、`RAG`、`MCP`のような語を見つけたたびに用語集へ即追加すると、短期的には便利です。しかし、別名・表記揺れ・定義の出典・採用理由が曖昧なまま正規語へ昇格すると、検索、UI、ドキュメント、集計で同じ概念が別物として扱われます。

この記事では、公開GitHubの実装を題材に、**候補語の収集と正規語への昇格を分離する promotion gate** を整理します。

結論は単純です。

> **「見つけた語」と「正規語」を同じ集合にしない。候補はqueueに置き、一次情報で識別子・preferred term・定義を確認できたものだけをcanonical glossaryへ昇格する。**

## 問題：候補語を即登録するとcanonical vocabularyが壊れる

たとえば入力に次の3表記が現れたとします。

```text
LLM
Large Language Model
Large Language Models
```

文字列としては別ですが、同じ概念を指している可能性があります。

ここで入力をそのまま正規語テーブルへ追加すると、壊れた状態はこうなります。

```yaml
terms:
  - term: LLM
  - term: Large Language Model
  - term: Large Language Models
```

検索側はalias展開が必要になり、集計側はどの表記を代表値にするか決められません。さらに、後から公式定義を追加すると、3レコードのどれへ付与すべきかという移行問題まで発生します。

## 原因：discoveryとverificationを同じ状態遷移にしている

用語集には少なくとも2種類の状態があります。

1. **見つかったが、まだ正規化していない候補**
2. **外部の一次情報と照合し、canonical termとして採用できる語**

この2つを同じテーブルへ無条件に書き込むと、「観測した」という事実がそのまま「正しい定義を持つ」という意味に変換されます。

公開実装 `KAFKA2306/nlm` では、この2段階を分離しています。2026-08-14のcommit `24f96d325facbad0857cdcb26d168619b20b7ee6` では、inventory全294件のうちverifiedを32→33、needs_reviewを262→261へ更新し、`Large Language Model (LLM)` を review queue から verified set へ1件だけ昇格しました。

一次情報:

- https://github.com/KAFKA2306/nlm/commit/24f96d325facbad0857cdcb26d168619b20b7ee6

この更新は単なる表記変更ではありません。canonical側には次の要素が追加されています。

- stable id: `large-language-model`
- preferred term: `Large Language Model`
- aliases: `LLM`, `Large Language Models`
- domain: `ai`
- 日本語定義
- related terms
- source URL
- source type
- verified date
- status

つまり、**候補文字列をcanonical entityへpromotionする時点で、識別・表記・出典・状態をまとめて固定する**設計です。

## 一次情報で何を確認するか

この例では、NLMのMeSH Browserがcontrolled vocabularyとして使われています。

2026年版のMeSH Browserで `Large Language Models` は次の情報を持っています。

- MeSH Heading: `Large Language Models`
- Unique ID: `D000098342`
- Entry Term: `Large Language Model`
- Date Introduced: `2025/01/01`
- Last Updated: `2026/01/01`
- Deep Learning配下のtree numberを含む

公式一次情報:

- https://meshb.nlm.nih.gov/record/ui?ui=D000098342
- https://id.nlm.nih.gov/mesh/D000098342.html

ここで重要なのは、単に「説明文がそれっぽい」ことではありません。**外部controlled vocabularyがstable identifierとpreferred conceptを持っている**ため、自前の用語集もそこへ対応付けできます。

## 設計判断：inventoryとcanonical glossaryを分ける

最小構成は2層です。

```text
観測された語
    ↓
review inventory
    ↓ verification gate
canonical glossary
```

inventoryには未確認語を残します。

```yaml
needs_review_by_domain:
  ai:
    - Retrieval-Augmented Generation (RAG)
    - Read-only MCP
    - Remote MCP
```

canonical glossaryには、確認できた語だけを置きます。

```yaml
terms:
  - id: large-language-model
    term: Large Language Model
    aliases:
      - LLM
      - Large Language Models
    domain: ai
    sources:
      - title: Large Language Models MeSH Descriptor Data 2026
        url: https://meshb.nlm.nih.gov/record/ui?ui=D000098342
        source_type: controlled_vocabulary
    verified_at: "2026-08-14"
    status: verified
```

この分離により、「候補を捨てない」と「未確認語を正規語として公開しない」を両立できます。

## 代替案1：文字列正規化だけで吸収する

小文字化、空白除去、単複変換などで `LLM` と `Large Language Models` を寄せる方法です。

これは重複候補の発見には使えますが、canonical entityの確定には不十分です。

理由は、文字列が近いことと、同一概念であることは別だからです。略語は特に衝突しやすく、domainが変われば同じ文字列が別概念を指す場合があります。

したがって文字列正規化は **candidate generation** に使い、promotionの根拠にはしない方が安全です。

## 代替案2：LLMで定義を生成して即採用する

生成AIに「この語を定義して」と依頼すれば、見た目のよい用語集はすぐ作れます。

しかし、生成された定義だけではstable identifierもrevision dateも保証できません。さらに、後から一次情報と食い違ったときに、どの時点の定義が正しかったのか追跡しにくくなります。

LLMは候補整理や検索query生成には使えても、**canonical promotionの最終根拠は公開一次情報へ戻す**方が監査可能です。

## 実装：promotionを1件のtransactionとして扱う

promotion時に複数ファイルを別々に手修正すると、inventoryだけ減ってcanonical側へ追加されない、といった片側更新が起きます。

そこで1件のpromotionを次のtransactionとして扱います。

```text
1. review queueから候補を選ぶ
2. 一次情報でidentifier / preferred term / aliasesを確認
3. canonical termsへ追加
4. verified setへ追加
5. needs_reviewから削除
6. verified / needs_review件数を更新
7. 公開用projectionを再生成または同期
8. testsで整合性を確認
```

`KAFKA2306/nlm` の該当commitでは、実際にinventoryの件数、verified set、review queue、canonical terms、公開用 `docs/glossary.md` が同じ変更で更新されています。

これは用語集を単なるMarkdownではなく、**状態遷移を持つ小さなデータプロダクト**として扱う考え方です。

## 壊れた失敗例：queueだけ減らす

たとえば次の変更は危険です。

```diff
 needs_review:
- 262
+ 261

 needs_review_by_domain:
-  - Large Language Model (LLM)
```

canonical側へ追加がなければ、候補が消えただけです。

逆にcanonical側だけ追加してqueueから削除しなければ、同じ語が未確認と確認済みの両方に残ります。

そのため、CIでは最低でも次を検査できます。

```python
assert verified + needs_review == total
assert candidate not in needs_review_terms
assert canonical_id in canonical_terms
assert source_url.startswith("https://")
assert status == "verified"
```

## 改善後：identityとstateを同時に固定する

改善後のpromotionでは、1つの概念に対して次を同時に確定します。

```text
identity  : stable id
label     : preferred term
aliases   : observed variants
evidence  : primary source URL
state     : verified
history   : verified_at
```

この形なら、UIはpreferred termだけ表示しつつ、検索はaliasesでもhitさせられます。集計キーはstable idへ寄せられるため、表記変更があっても同一entityとして扱えます。

## 検証：件数だけでなく集合差分を見る

`verified=33`、`needs_review=261`、`total=294` なら算術上は整合しています。

しかし、件数だけでは同じ候補を2回登録したり、別候補を誤って削除したりしても検出できません。

実務では次の集合条件も持つと安全です。

```text
verified_terms ∩ needs_review_terms = ∅
canonical IDs are unique
aliases do not create ambiguous canonical ownership
all verified terms have at least one source
all source-backed promotions carry verification date
```

つまり、**count invariant + set invariant + provenance invariant** の3種類を分けて検証します。

## 再現方法：小さなpromotion gateを作る

次の3ファイルだけで再現できます。

```text
inventory.yaml
terms.yaml
validate.py
```

`inventory.yaml`:

```yaml
total: 3
verified: 1
needs_review: 2
verified_terms:
  - HTTP
needs_review_terms:
  - Large Language Model (LLM)
  - Retrieval-Augmented Generation (RAG)
```

`terms.yaml`:

```yaml
terms:
  - id: http
    term: HTTP
    sources:
      - https://www.rfc-editor.org/rfc/rfc9110
    status: verified
```

ここへ `Large Language Model (LLM)` をpromotionするときは、MeSHの `D000098342` を確認し、stable id・preferred term・alias・sourceを `terms.yaml` に追加してからinventoryを更新します。

最後にvalidatorで、件数、重複、source有無、verified/reviewの排他性を検査します。

## 失敗と学び

用語集で最も危険なのは、誤字よりも**未確認の候補が正規語へ静かに混ざること**です。

候補収集を厳しくしすぎると新語を取りこぼします。一方、正規語への追加を緩くするとcanonical vocabularyが汚れます。

この2つは同じgateで解決しようとせず、

- discoveryは広く
- promotionは狭く
- canonical側は一次情報付き

と分離した方が運用しやすくなります。

## まとめ

再利用しやすい用語集は、単なる「言葉と説明の表」ではありません。

```text
candidate discovery
  → review inventory
  → primary-source verification
  → canonical promotion
  → projection
```

という状態遷移を持つデータです。

`KAFKA2306/nlm` の公開実装では、`Large Language Model (LLM)` を1件だけreview queueからverifiedへ移し、同時にcanonical term・alias・source・verified date・公開projectionを更新しています。

**候補は保存する。しかし、一次情報でidentityを確定できるまではcanonicalにしない。**

このpromotion gateは、技術用語集だけでなく、製品マスタ、タグ辞書、業界分類、人物名寄せ、データカタログにもそのまま応用できます。
