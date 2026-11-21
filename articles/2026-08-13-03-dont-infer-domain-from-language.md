---
title: "GitHubのリポジトリ一覧で、用途が分からないものを未分類にする"
emoji: "🗂️"
type: "tech"
topics: ["github", "metadata", "python", "architecture"]
published: false
published_at: 2026-08-13 20:01
---

**分からないものを、もっともらしい分類で埋めるな。**

GitHub一覧で「PythonだからAI」「TypeScriptだからWeb」と推測すれば空欄は減る。しかし言語は実装の一部であって、リポジトリの用途を証明しない。根拠のない推測を事実として表示するほど、一覧はきれいになっても判断の質は下がる。

[agent-resourcesのcollector](https://github.com/KAFKA2306/agent-resources/blob/main/dashboard/collectors/repositories.py)では、明示的な`agent-zone-*`のtopicがある場合に用途を取り、それ以外は`unclassified`とした。[テスト](https://github.com/KAFKA2306/agent-resources/blob/main/dashboard/tests/test_repository_collector.py)と[PR #60](https://github.com/KAFKA2306/agent-resources/pull/60)に変更の証拠がある。

汎用規律は **「確認できない推定を事実欄へ入れるな。未知を独立の状態として残せ」**。分類率の高さは正答率の高さではない。

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

## 2個の明示タグがある入力はどうなるか

本文の`classify`は`agent-zone-*`タグをソートして**最初の一つ**を採る。例えば次の入力では`investing`が返る。

```python
repo = {
    "name": "mixed-purpose",
    "topics": ["agent-zone-web", "agent-zone-investing"],
    "language": "Python"
}
# 本文のclassify(repo)は "investing" を返す
```

これは**文字列の順で一つ選んだだけ**で、用途が投資に確定した根拠ではない。現行の[collector](https://github.com/KAFKA2306/agent-resources/blob/main/dashboard/collectors/repositories.py)が複数タグをどう扱うかは別途確認が必要。この簡易例だけで本番の曖昧さを解消したことにはならない。

「用途は一つ」の製品なら、タグ0件は`unclassified`、1件はその用途、2件以上は`review_required`とする合格条件を検討する。複数用途が許される製品なら、一覧へ両方を表示する。どちらを採るにせよ**複数タグの例をテストに入れ、黙って一つに確定しない**。

## まず1つ見直すなら

リポジトリ一覧から、用途を示すトピックがあるものと、言語しか分からないものを一つずつ選ぶ。両方の `topics` と `language` を手元に置いて、分類ロジックが何を根拠にしているか見る。

例えば、

```text
値がなければA
languageがPythonならB
名前にdataがあればC
```

のようなruleが、意味を本当に保証しているか確認する。

保証できないなら、いったん `unclassified` へ戻す。

同じ一覧で「明示トピックがある件数 ÷ 全件数」を記録する。トピック付きの例は指定の用途に分類され、言語しか分からない例は未分類になればよい。未分類の一覧から、次にトピックを補う対象を選べる。

それだけで、**綺麗だが嘘を含む一覧**から、**不足も含めて信頼できる一覧**へ近づける。

分からないときに、賢そうな答えを作らない。

それがこの分類UIで一番守りたかったことだった。


## この規律を採るときと撤回するとき

顧客情報、文書カテゴリ、障害原因の分類でも、表示した用途に正確さが必要なら未知を示す方法を試せる。ただし、これらは**応用仮説**であって利用者の誤判断が減ったという実測ではない。

推定分類が明示的に許され、誤判定率と損失を評価して十分低いと確認できたら「推定」と表示して使う余地はある。それでも確認済みと同じ欄へ混ぜてはいけない。さらに明示topicが複数ある入力では現在の簡易実装が一つを選ぶ境界が残る。**不明を埋める前に、確からしさを確かめる。**
