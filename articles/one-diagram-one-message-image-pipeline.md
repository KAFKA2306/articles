---
title: "生成AIの図に『CI成功』と書いてあった。画像の中の嘘を公開前に落とす"
emoji: "🔎"
type: "tech"
topics: ["chatgpt", "imagegeneration", "zenn", "testing", "automation"]
published: false
published_at: 2026-08-13 09:21
---

# 生成AIの図に「CI成功」と書いてあった。画像の中の嘘を公開前に落とす

生成AIへ技術記事の図を頼むと、見栄えの良いUI、グラフ、URL、数値、CI結果まで描いてくれます。

問題は、その中に**実行していないCI、測っていない改善率、存在確認していないURL**まで混ざり得ることです。

Markdown側のリンクチェックは通ります。画像ファイルも存在します。それでも、画像内の主張は真実とは限りません。

そこで `KAFKA2306/articles` の画像生成フローでは、生成画像を最終成果物ではなく**untrusted input**としてもう一度監査する設計にしました。

この記事で扱うのは、代表的な5種類だけです。

## 1. 「CI成功」は画像に描かれただけでは証拠にならない

生成図には、GitHub風の緑のcheckや `CI SUCCESS` が自然に描かれることがあります。

しかし、実GitHub Actions runと照合していない表示は単なるpixelです。

```text
画像内
✓ lint
✓ test
✓ deploy

実GitHub
未確認
```

このとき画像はCI証拠ではありません。

CI状態を記事へ書くなら、GitHub上のrun / check / commitを本文側で確認し、画像は説明用に留めます。

**画像自身をevidence sourceにしない**ことが最初のルールです。

## 2. 「5.0/5.0」や「95%改善」は最も危険

生成AIは、比較図を分かりやすくするために数値を補ってしまうことがあります。

例えば、

```text
Before 18.7%
After   0.6%
95% improved
```

という図が出ても、計測ログがなければその値は採用しません。

必要なのは少なくとも、

```text
source data
command / script
execution environment
commit
result artifact
```

です。

どれも存在しない場合は、数値を消して構造図へ落とします。

```text
NG: 95% improved
OK: before / afterの設計差だけを示す
```

「N/A」の方が、もっともらしい架空値より有用です。

## 3. グラフは測定結果に見えやすい

軸、系列、legendが揃った瞬間、生成グラフは実測結果に見えます。

しかし、AIが描いた折れ線や棒の高さから実データを逆生成してはいけません。

結果グラフを公開できる条件を、次のように固定します。

```yaml
figure:
  type: result
  status: verified
  evidence:
    data: path/to/result.csv
    script: path/to/plot.py
    commit: <sha>
```

このevidence chainがない生成グラフは、`result`ではなく`illustrative`です。

## 4. URL・PR番号・commit SHAも画像から転記しない

生成図には、

```text
PR #42
abc1234
https://example.com/docs
```

のような文字列も描けます。

見た目がGitHub UIでも、実GitHubの状態とは無関係です。

公開記事へPR番号やcommit SHAを書く場合は、GitHubから取得した値を本文へ置きます。画像内文字列を逆にsourceへしてはいけません。

URLも同じです。

画像に描かれたURLではなく、ブラウザで確認できる一次情報URLを本文に保持します。

## 5. 条件表が細かいほど「本物らしく」見える

モデル名、token数、TTL、request count、hardwareなどが表になっていると、実験条件に見えます。

しかし条件表そのものも生成できます。

そこで、figureごとに画像の外へmanifestを持たせます。

```json
{
  "id": "figure-03",
  "mode": "illustrative",
  "factual_claims": [],
  "evidence_urls": []
}
```

実測結果なら、

```json
{
  "id": "figure-07",
  "mode": "verified",
  "factual_claims": [
    "test run succeeded"
  ],
  "evidence_urls": [
    "https://github.com/.../actions/runs/..."
  ]
}
```

とします。

## artifact gateとevidence gateを分ける

画像公開には2種類の成功条件があります。

```text
artifact gate
  ├─ file exists
  ├─ path is valid
  ├─ format is supported
  └─ size is acceptable

evidence gate
  ├─ number is verified
  ├─ CI state is verified
  ├─ URL exists
  ├─ PR / commit exists
  └─ causal statement has evidence
```

Zenn公式はGitHub連携時の画像配置やMarkdown記法を説明しています。

- https://zenn.dev/zenn/articles/deploy-github-images
- https://zenn.dev/zenn/articles/markdown-guide

これらはartifact gateの根拠になります。

一方、画像の中の数値やCI状態が正しいかは、別途こちらで検証する必要があります。

## 実装するevidence gate

最小実装は単純です。

```python
def validate_figure(item):
    if item["mode"] == "verified" and not item["evidence_urls"]:
        raise ValueError("verified figure requires evidence")

    if item["mode"] == "illustrative" and item["factual_claims"]:
        raise ValueError("illustrative figure must not assert facts")
```

重要なのはOCRを完璧にすることではありません。

**生成前に、その図が何を主張してよいかをcontractとして決めること**です。

結果図なら証拠が必要。概念図なら実測値を書かない。

## 画像生成モデルが高性能でも、evidence gateは消えない

OpenAIの現行APIでは、GPT Image 2が画像生成・編集用のモデルとして公開されています。

公式:
https://developers.openai.com/api/docs/models/gpt-image-2

画像内text renderingの性能が高くなるほど、逆に技術図では「文字として自然だから事実に見える」問題が強くなります。

これは画像モデルの欠陥というより、**生成された説明表現と一次証拠を同じものとして扱う工程の欠陥**です。

## 公開前チェック

生成図1枚ごとに、最低限これだけ確認します。

```text
[ ] 実測していない数値がない
[ ] 未確認のCI状態がない
[ ] 架空URLがない
[ ] 架空PR / commitがない
[ ] 因果を描くなら根拠がある
[ ] verified図にはevidence URLがある
[ ] illustrative図は事実主張を持たない
```

1つでも確認できなければ、画像を修正するか削除します。

## まとめ

生成画像は、説明力のあるfigureを高速に作れます。

しかし、

```text
画像が生成できた
!=
画像内の主張が検証できた
```

です。

だから生成後にもう一度、画像をuntrusted inputとして扱う。

架空CI、架空数値、架空グラフ、架空URL、架空PRを、**figure manifest + evidence gate**で公開前に落とす。

技術記事の画像品質を上げるときに必要なのは、「もっと綺麗な絵」だけではなく、**絵の中の主張までCI対象にすること**でした。

## 一次情報

- OpenAI GPT Image 2: https://developers.openai.com/api/docs/models/gpt-image-2
- Zenn — GitHub連携で画像を配置する: https://zenn.dev/zenn/articles/deploy-github-images
- Zenn — Markdown記法: https://zenn.dev/zenn/articles/markdown-guide
