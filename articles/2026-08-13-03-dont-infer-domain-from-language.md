---
title: "分類できないなら、無理に埋めない。unclassifiedを残した方がUIは信頼できた"
emoji: "🗂️"
type: "tech"
topics: ["github", "metadata", "python", "architecture"]
published: false
published_at: 2026-08-13 20:01
---

GitHubのrepository一覧を分類するとき、空欄は気になる。

PythonならAI。

TypeScriptならWeb。

そう埋めれば、一覧はすぐ整う。

しかし、その瞬間からUIは**分かっていないことまで分かった顔をする**。

`KAFKA2306/agent-resources` では、project zoneを明示的な `agent-zone-*` topicがある場合だけ採用し、それ以外は `unclassified` にするよう変更した。

- collector: https://github.com/KAFKA2306/agent-resources/blob/main/dashboard/collectors/repositories.py
- tests: https://github.com/KAFKA2306/agent-resources/blob/main/dashboard/tests/test_repository_collector.py
- PR #60: https://github.com/KAFKA2306/agent-resources/pull/60

この記事で扱うのはtaxonomyの作り方ではない。

**情報不足をそれらしい推測で埋めず、「まだ分からない」を利用者へ正しく見せる設計**について書く。

## languageは分かっても、domainは分からない

例えば次の2repoがある。

```json
{"name":"market-research","topics":["agent-zone-investing","python"],"language":"Python"}
{"name":"photo-indexer","topics":[],"language":"Python"}
```

1件目には `agent-zone-investing` という明示的な意味metadataがある。

2件目から分かるのは、主言語がPythonであることまでだ。

AI、画像、投資、科学計算、CLIのどれかは確定しない。

それでも `language-python → AI` のようなfallbackを置けば、UI上の空欄は消える。

代わりに、**根拠のない意味が増える。**

## `unclassified` は失敗ではなく、情報の状態にする

改善後の核は小さい。

```python
ZONE_PREFIX = "agent-zone-"
UNCLASSIFIED = "unclassified"

def classify(repo):
    topics = repo.get("topics") or []
    zones = sorted(
        t[len(ZONE_PREFIX):]
        for t in topics
        if isinstance(t, str)
        and t.startswith(ZONE_PREFIX)
        and t[len(ZONE_PREFIX):]
    )
    return zones[0] if zones else UNCLASSIFIED
```

ここで `language` を捨てる必要はない。

言語は言語として表示する。

ただしdomainの根拠には使わない。

```text
Domain: unclassified
Language: Python
```

この表示なら、利用者は何が分かっていて何が分かっていないかを区別できる。

## 見栄えの100%より、意味のcoverageを測る

unknownを許さない設計では、推測ruleを足すほど「分類済み率」を100%へ近づけられる。

しかし、それでは本当に足りないmetadataが見えなくなる。

例えば100repo中40repoに意味topicがなければ、

```text
semantic metadata coverage = 60%
```

と観測できる。

この40件をlanguage fallbackで埋めると、UI上は100%にできても、意味metadataが不足している事実は消える。

**unknownを残すと、改善対象が見える。**

これは欠点ではなく、運用上の価値である。

## classifierを賢くするより、昇格条件を明確にする

`unclassified` から正式なzoneへ移す条件を決める。

例えば、

```text
明示topicが付いた
→ canonical zoneへ昇格
```

とする。

READMEやrepo名からLLMで推論する案もあるが、それをcanonicalにするなら、少なくとも推論結果と明示metadataを同じstateにしない方がよい。

```text
explicit
inferred
unclassified
```

のようにprovenanceを分ける。

今回の `agent-resources` は、より単純にexplicitだけを採用した。

## negative testで「勝手に分類しない」を守る

守りたいのは正しい分類だけではない。

**根拠がないときに分類しないこと**もcontractである。

```python
assert classify({"topics":["agent-zone-investing"],"language":"Python"}) == "investing"
assert classify({"topics":[],"language":"Python"}) == "unclassified"
assert classify({"topics":[],"language":"JavaScript"}) == "unclassified"
```

このtestがあると、後から誰かが便利なfallbackを追加しても、意味境界を壊した時点で気づける。

## UIではunknownを隠さず、次のactionにつなげる

`unclassified` をただ灰色で並べるだけでは使いにくい。

そこでUI上は、

- unclassified件数
- explicit metadata coverage
- metadata追加が必要なrepo

を見えるようにする方がよい。

つまりunknownを、

```text
見せたくない欠損
```

ではなく、

```text
次に整備すべきqueue
```

として扱う。

これなら「未分類がある」ことが運用を前へ進める。

## この考え方はrepository分類以外でも使える

同じ問題は、

- 顧客segment
- 文書category
- 製品taxonomy
- 工場domain
- AI-generated label
- データ品質status

でも起きる。

根拠が弱いのに一番近そうなcategoryへ押し込むと、見た目は整う。

しかし利用者は、そのlabelを事実として使い始める。

だから、

```text
known
inferred
unknown
```

を必要に応じて分ける。

**分類精度だけでなく、分類根拠の透明性をUXにする。**

## まず1つ見直すなら

既存のclassifierでfallback ruleを探す。

例えば、

```text
値がなければA
languageがPythonならB
名前にdataがあればC
```

のようなruleが、意味を本当に保証しているか確認する。

保証できないなら、いったん `unclassified` へ戻す。

そしてcoverageを測る。

それだけで、**綺麗だが嘘を含む一覧**から、**不足も含めて信頼できる一覧**へ近づける。

分からないときに、賢そうな答えを作らない。

それがこの分類UIで一番守りたかったことだった。
