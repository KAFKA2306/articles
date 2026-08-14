---
title: "生成画像を証拠にしない：図の主張を公開前に監査する"
emoji: "🔎"
type: "tech"
topics: ["chatgpt", "imagegeneration", "testing", "automation", "zenn"]
published: false
---

生成画像を技術記事へ入れるとき、最初に壊れやすいのは「画像ファイルがあるか」ではありません。**画像の中に書かれた数値・URL・CI状態・PR番号を、いつの間にか事実として扱ってしまうこと**です。

画像ファイルの存在確認と、画像内の主張の検証は別問題です。Zenn公式はGitHub連携で扱う画像について、リポジトリ直下の `/images`、対応拡張子、1ファイル3MB以内、`/images/` から始まる絶対パスという配置条件を定めています。しかし、これは画像を配信できる条件であって、画像内に描かれた技術的主張の正しさを保証する条件ではありません。

この記事の結論は一つです。

> **生成図は公開成果物になる前に、もう一度「未検証の入力」として扱う。ファイル検証と factual claim 検証を分離する。**

この考え方は、生成画像を禁止するためではありません。OpenAIはChatGPTおよびAPIで画像生成機能を提供しています。生成能力が高いからこそ、「見栄えが良い」と「検証済み」を同じゲートにしない設計が必要です。

## 問題：画像リンクが正しくても、画像内の主張は正しいとは限らない

たとえば技術記事に次のようなダッシュボード風の図を置いたとします。

```text
CI: SUCCESS
P99: 42 ms
改善率: 37%
PR: #123 merged
commit: abcdef1
```

Markdownとして画像が正しく参照され、Zennへ配信できても、この5項目が実測・実状態と一致することは別途確認が必要です。

ここで混同しやすいのが、次の2種類のゲートです。

```text
artifact gate
  - ファイルが存在する
  - 拡張子が許可されている
  - サイズ制限内である
  - Markdown参照先が正しい

evidence gate
  - 数値の元データがある
  - URLが実在する一次情報である
  - CI状態をGitHubからread-backした
  - PR/commitをGitHubからread-backした
  - 因果表現に仕様・コード・実験の根拠がある
```

前者だけ通すと、「表示できるが根拠のない図」を公開できます。

`KAFKA2306/articles` の現行設定でも、画像方針は `objective: reader_comprehension`、`fixed_count: null`、`require_explanatory_value: true` です。つまり画像枚数を成果指標にせず、理解に寄与する場合だけ使う契約です。

- https://github.com/KAFKA2306/articles/blob/93059cc44225a253d3275d57f92149a8ea949145/pipeline/config.json
- https://github.com/KAFKA2306/articles/blob/93059cc44225a253d3275d57f92149a8ea949145/pipeline/audit.py

## 原因：生成処理の後に「再入力」の工程がない

壊れた工程は単純です。

```text
検証済み本文
  ↓
画像生成
  ↓
PNG / WebP
  ↓
そのまま公開
```

この流れでは、本文の事実確認が画像生成の前で終わっています。しかし生成処理は、本文をそのままビットマップへ転写するだけではありません。レイアウト、短縮表現、ラベル、数値、UI風要素などを含む新しい成果物を作ります。

したがって、公開フローは次のように扱う方が安全です。

```text
検証済み本文
  ↓
画像生成
  ↓
未検証の生成物
  ↓
画像内claimの棚卸し
  ↓
一次情報との照合
  ↓
verified / illustrative / reject
  ↓
公開
```

重要なのは、生成画像を「出力だから信頼できる」と分類しないことです。**生成後の画像は、公開判定に対しては新しい入力です。**

## 具体例：CI成功画面を描くなら、CIを別途確認する

説明用の図にGitHub Actions風の緑チェックを描くと、読者は自然に「実際にCIが成功した」と解釈しやすくなります。

そこで、画像内の表示を3種類に分けます。

```yaml
claims:
  - text: "CI SUCCESS"
    kind: runtime_state
    mode: verified
    evidence_url: "https://github.com/.../actions/runs/..."

  - text: "worker"
    kind: structural_label
    mode: illustrative

  - text: "P99 42 ms"
    kind: benchmark
    mode: reject
    reason: "計測artifactがない"
```

`verified` は一次情報URLを必須にします。`illustrative` は構造理解だけに使い、実測値や現在状態を持たせません。`reject` は画像を直すか使わないという意味です。

この分離をすると、「図として分かりやすいから」という理由で未検証の数値を残す余地が減ります。

## 壊れた失敗例：改善率だけが画像に残る

次のbefore/after図を考えます。

```text
Before: 18.7%
After:   0.6%
95% improved
```

元ログ、母数、集計期間、実行条件がないなら、この図は結果図として使えません。数字が具体的であるほど、それらしく見えるだけです。

改善後は、証拠がない数値を消して構造図に落とします。

```text
flaky test
  ↓
固定時刻
固定seed
外部依存の分離
  ↓
再現性を検証する
```

「測っていない数値をN/Aにする」「結果図ではなく設計図にする」は、情報量を減らす行為ではありますが、検証可能性は上がります。

## 設計判断：画像の外にfigure manifestを置く

画像そのものを正準データにすると、人間が目視で全claimを覚えておく必要があります。そこで、画像の横に機械可読なmanifestを置きます。

```json
{
  "figures": [
    {
      "id": "architecture-01",
      "mode": "illustrative",
      "claims": [],
      "evidence_urls": []
    },
    {
      "id": "ci-result-01",
      "mode": "verified",
      "claims": ["CI success"],
      "evidence_urls": [
        "https://github.com/OWNER/REPO/actions/runs/RUN_ID"
      ]
    }
  ]
}
```

最低限のルールはこれだけです。

```python
def validate_figure(item):
    if item["mode"] == "verified" and not item["evidence_urls"]:
        raise ValueError("verified figure requires evidence")
    if item["mode"] == "illustrative" and item["claims"]:
        raise ValueError("illustrative figure must not carry factual claims")
```

実務では `claims` を文字列だけでなく `kind`、`value`、`source` に分けても構いません。ただし、最初から複雑なschemaを作る必要はありません。**verifiedなのにevidenceが空、という事故をfail-closeできること**が先です。

## URLは画像の中ではなく本文・manifestで検証する

URLらしい文字列が画像に描かれていても、その場ではクリックできず、HTTP到達性や発行主体も確認できません。

外部仕様を根拠にする場合は、画像内の文字列ではなく本文側に実URLを残します。今回使っている一次情報は次の3つです。

- OpenAI公式: 画像生成をChatGPTおよびAPIへ提供していること
  - https://openai.com/index/image-generation-api/
- Zenn公式: GitHub管理画像の配置・拡張子・3MB制限・参照パス
  - https://zenn.dev/zenn/articles/deploy-github-images
- GitHub Docs: branch URLは後で内容が変わり得るため、特定versionの証拠にはcommit IDを使ったpermalinkを利用できること
  - https://docs.github.com/en/repositories/working-with-files/using-files/getting-permanent-links-to-files

特に再現記事では、`blob/main/...` よりcommit SHAを含むURLの方が「当時何を見たか」を固定しやすくなります。

## 実装：公開前チェックを5段階にする

CIへ組み込むなら、次の順序にします。

### 1. 画像が本当に必要か

文章・コード・表だけで理解できるなら作りません。画像枚数をKPIにしないためです。

### 2. 画像の役割を1つ決める

`structure`、`flow`、`comparison`、`result` のように役割を一つに絞ります。結果図は最も厳しく検証します。

### 3. claim inventoryを作る

数値、状態、URL、固有名詞、バージョン、因果を列挙します。

### 4. evidenceを固定する

GitHub上のコードを根拠にするなら、GitHub Docsのpermalink方針に従いcommit SHAを含むURLへ固定します。外部仕様なら公式一次情報URLを残します。

### 5. fail-closeする

検証できないclaimは、削除、一般化、または画像そのものを不採用にします。根拠がない状態を「あとで確認」にして公開へ流さないことが重要です。

## 検証：レビュー時に答える質問を固定する

公開レビューでは、画像ごとに次だけ確認すれば十分です。

```text
[ ] この図は本当に必要か
[ ] 図の役割は一つか
[ ] 数値はあるか → 元データはあるか
[ ] 状態表示はあるか → read-backしたか
[ ] URLはあるか → 本文側で一次情報を開いたか
[ ] 因果表現はあるか → 根拠があるか
[ ] GitHub証拠はcommit permalinkで固定できているか
[ ] 根拠なしclaimが残っていないか
```

これはOCRで完全自動化しなくても有効です。自動化の目的は「画像の意味をAIに判定させる」ことではなく、**verifiedというラベルを付けるための証拠欠落を機械的に拒否すること**だからです。

## 再現方法：1枚だけで試す

手元の記事で次を試せます。

1. 既存の図を1枚選ぶ。
2. 図に書かれた数値・状態・URL・固有名詞を列挙する。
3. 各項目へ一次情報URLを付ける。
4. URLを付けられない項目を削除するか `illustrative` に変える。
5. GitHubのコードを根拠にした箇所はcommit permalinkへ固定する。
6. 画像ファイル側はZennの配置条件も別途確認する。

この作業をすると、「画像が存在する」と「画像が証拠として使える」が別の品質属性だと分かります。

## 失敗からの学び

生成画像の品質問題を、プロンプト改善だけで解こうとすると限界があります。プロンプトを丁寧にしても、最終成果物を一次情報と照合する工程がなければ、公開側の保証は増えません。

改善の中心は画像モデルではなく、**公開パイプラインのtrust boundary**です。

- 生成前: 本文の事実を検証する
- 生成後: 画像を未検証入力へ戻す
- 公開前: claimとevidenceを照合する
- 公開時: artifact gateとevidence gateの両方を通す

画像がきれいかどうかは、その後の問題です。

## まとめ

生成画像を技術記事で安全に使うとき、覚えることは一つです。

**画像ファイルの存在確認はartifact gate、画像内の主張確認はevidence gate。両者を分ける。**

図を作る必要がない記事では作らない。作るなら、生成後に未検証入力として再評価する。数値・状態・URL・因果を持つなら一次情報へ結び、結べないclaimは公開しない。

この設計なら、画像生成の能力が変わっても、公開記事の検証可能性は同じルールで守れます。
