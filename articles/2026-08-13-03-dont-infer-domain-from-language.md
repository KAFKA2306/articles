---
title: "PythonだからAI、TypeScriptだからWeb、をやめる。分類不能をunclassifiedで残す"
emoji: "🗂️"
type: "tech"
topics: ["github", "metadata", "python", "architecture"]
published: false
published_at: 2026-08-13 20:01
---

GitHub上のリポジトリを自動分類するとき、情報不足を「PythonだからAI系」「TypeScriptだからWeb系」のような推測で埋めると、UIは整っても分類へ根拠のない意味が混ざる。

`KAFKA2306/agent-resources` の現在の `main` では、project zone は明示的な `agent-zone-*` topic がある場合だけ採用し、それ以外は `unclassified` に送る。GitHub公式でもtopicsはprojectの目的やsubject areaなどを表すmetadataとして説明され、repository languagesはfiles/directoriesからGitHub Linguistが算出する言語統計として説明されている。

一次情報:

- https://github.com/KAFKA2306/agent-resources/blob/main/dashboard/collectors/repositories.py
- https://github.com/KAFKA2306/agent-resources/blob/main/dashboard/tests/test_repository_collector.py
- https://github.com/KAFKA2306/agent-resources/pull/60
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-repository-languages

## 1. 問題

実際の入力を2件考える。

```json
{"name":"market-research","topics":["agent-zone-investing","python"],"language":"Python"}
{"name":"photo-indexer","topics":[],"language":"Python"}
```

前者には `agent-zone-investing` という明示的な意味metadataがある。後者から確定できるのは主言語がPythonであることだけで、投資、画像、科学計算、CLIなどのdomainは確定しない。

壊れた例は、明示topicがないとき `language-python` のようなgroupを作るfallbackである。欠損は消えるが、domain taxonomyとimplementation taxonomyが混ざる。

## 2. 原因

原因は「欠損値を埋めること」と「意味を推論すること」を同一視したことにある。

GitHub topicsとlanguagesは同じrepository metadataに見えるが役割が違う。topicsは目的・subject areaなどを明示できる。一方languagesはrepositoryのコード構成から算出される。Pythonで書かれたprojectが何を目的にしているかは、languageだけでは決まらない。

## 3. 設計判断と代替案

代替案は3つある。

1. primary languageをfallbackにする。ほぼ全repoへラベルを付けられるが、domainとしての意味は弱い。
2. READMEやrepo名からLLMで推論する。自然な分類を作れる可能性はあるが、model・prompt・文章変更で結果が揺れ、GitHub metadataだけでは説明できなくなる。
3. explicit semantic metadataだけを採用し、不明は `unclassified` にする。

`agent-resources` は3を採用している。PR #60でもlanguage fallbackを外し、LLM/domain inferenceをnon-goalとしている。現在の `main` の `infer_group()` も `agent-zone-*` topicがなければ `UNCLASSIFIED_GROUP` を返す。

## 4. 実装

改善後の核は小さい。

```python
ZONE_PREFIX = "agent-zone-"
UNCLASSIFIED = "unclassified"

def classify(repo):
    topics = repo.get("topics") or []
    zones = sorted(
        t[len(ZONE_PREFIX):]
        for t in topics
        if isinstance(t, str) and t.startswith(ZONE_PREFIX)
        and t[len(ZONE_PREFIX):]
    )
    return zones[0] if zones else UNCLASSIFIED
```

`language` を削除する必要はない。別軸のmetadataとして保存してよい。ただしdomain分類関数のfallbackには使わない。

改善後の例では、`agent-zone-investing` があれば `investing`、topicsが空でlanguageだけPythonなら `unclassified` になる。

## 5. 検証

守りたいcontractは「正しいzoneが付く」だけではなく「根拠なしにzoneを作らない」ことなので、negative testを置く。

```python
assert classify({"topics":["agent-zone-investing"],"language":"Python"}) == "investing"
assert classify({"topics":[],"language":"Python"}) == "unclassified"
assert classify({"topics":[],"language":"JavaScript"}) == "unclassified"
```

`agent-resources/main` の回帰testにも、PythonとJavaScriptのどちらでも明示zoneがなければ `unclassified` になる検証がある。

## 6. 失敗と学び

`unclassified` が増えるとdashboardが未完成に見える。しかし推測で埋めると、本当に不足しているsemantic metadataの量が見えなくなる。

例えば100 repo中40 repoが `unclassified` なら、「semantic metadata coverageが60%」という改善対象を観測できる。これをlanguage由来のgroupで埋めると、見かけ上は100%にできてもdomain metadataが不足している事実は消える。

学びは、unknown stateを有効な状態として残すこと、そしてdomain・language・runtimeなど別taxonomyを1つのgroupへ押し込まないことである。

## 7. 再現方法

読者は上の `classify()` と3つのassertだけで再現できる。

まずassertが通ることを確認する。次に、topicsが空の場合に `language-python` を返すfallbackを追加する。するとPython/JavaScriptの2つのassertが失敗する。

これで「分類できること」ではなく、**根拠なしに分類しないこと**をtestで固定できる。

さらに実務では `unclassified` の比率をcoverageとして別に計測する。coverageが低ければtopicなど正準metadataを改善し、classifierへ推測規則を足して数字だけ改善しない。

## まとめ

自動分類では、空欄を埋めることより、出力した意味を説明できることの方が重要である。

GitHub topicsは目的やsubject areaを表す明示metadataとして使える。repository languageはコードから算出された別軸の情報で、それだけではproject domainを確定できない。

だから意味カテゴリの根拠がなければ `unclassified` にする。unknownを残すことで誤分類を避け、metadata不足そのものを観測できる。

**分からないときに、賢そうな分類を作らない。** これが再利用しやすいtaxonomyの最小契約になる。