---
title: "同じ画像URLなのに中身が変わる。共有アセットを固定する"
emoji: "📌"
type: "tech"
topics: ["github", "ci", "frontend", "architecture"]
published: false
published_at: 2026-08-13 23:40
---

複数のGitHub Pagesで同じ画像やアイコンを使いたいとき、いちばん簡単なのは中央repoの `main` を直接参照することだ。しかし、`main` は更新される。URLが同じでも、その先のファイルは将来変わり得る。

GitHub公式ドキュメントも、branch名を含む通常のファイルURLはbranch headの更新に合わせて内容が変わり得るため、特定versionを共有したい場合はcommit IDを使ったpermalinkにするよう説明している。

この問題に対して `KAFKA2306/prompt-vault` と `KAFKA2306/travel` では、共有アセットを **asset IDで選ぶ → Prompt Vaultのcommitを固定する → SHA-256を照合する → consumer repoへvendorする → build後とdeploy後にも同じhashを再確認する** という境界を実装した。

一次情報:

- https://github.com/KAFKA2306/prompt-vault/commit/f96a2d6b5bb257080f235f04cdfb5745e8700ed3
- https://github.com/KAFKA2306/prompt-vault/commit/a6ef582f7112b0f504bea3d535b9c45437c107f9
- https://github.com/KAFKA2306/travel/commit/cbc7aeae37398a0f50b76c6de6e85319653dfbfe
- https://docs.github.com/en/repositories/working-with-files/using-files/getting-permanent-links-to-files?apiVersion=2022-11-28
- https://docs.github.com/en/rest/git/blobs

## 1. 問題

たとえば、複数siteから次のようなURLを参照するとする。

```text
https://raw.githubusercontent.com/example/assets/main/hero.webp
```

初日は正しい画像が出る。だが中央repoの `main` で `hero.webp` が差し替えられると、consumer側のcommitを1行も変更していないのに、表示結果だけが変わる。

ここで壊れているのはHTTPではない。404にもならず、buildも通り得る。**consumerが「どのbytesを採用したのか」を後から再現できない**ことが問題になる。

GitHub公式のpermalink説明では、branch head上のファイルは新しいcommitによって変わり得る一方、URL中のbranch名を特定commit IDへ置き換えると、そのcommit内の正確なversionへ固定できる。

### 実際の状況

`prompt-vault` の2026年8月13日の実装では、Pages共有アセットを `assets/registry.json` とcollection manifestで管理し、consumerはasset IDと配置先だけを宣言する構造を追加した。さらに `vendor_assets.py` はPrompt Vaultのcommitを引数で受け取り、canonical sourceのSHA-256を確認してからconsumerへコピーする。

同日の `travel` では `travel-basic` を実consumerとして導入し、lock fileへ次の4点を固定した。

```json
{
  "canonical_repository": "KAFKA2306/prompt-vault",
  "canonical_commit": "90111f8953dd2a45aca2da7053bfdeef57459b41",
  "consumer_repository": "KAFKA2306/travel",
  "source_sha256": "8c45dfb3c32aa5d2991b9d3b9d710b66722f0ef10fb62a0b5dea2582f36ea383"
}
```

commitだけでなく、採用したbytesのdigestまでconsumer側に残している。

## 2. 原因

原因は、**「どこにあるか」と「何を採用したか」を同じURLで表現しようとしたこと**にある。

branch URLは場所を示すには便利だが、branch headは動く。対してconsumerが必要なのは、レビュー時に確認したものとdeploy時に配信するものが同じだと検証できる識別子である。

ここでは識別子を2層に分ける。

1. **commit ID**: どのrepository snapshotを参照したか
2. **SHA-256**: そのsnapshotから取り出したasset bytesが期待値と一致するか

GitHubのGit blob APIも、repository内のファイル内容をGit blobとして扱い、blobにhash識別子を持つことを公式に説明している。今回のconsumer contractではそれとは別にSHA-256をmanifestへ記録し、vendored file・build artifact・deploy後のfileを同じdigestで照合している。

## 3. 設計判断と代替案

### 案A: `main` をruntime hotlinkする

実装は最小になる。しかしconsumer repoのcommitと実際に表示されるasset versionが分離する。

`prompt-vault` のAgent World asset manifestでも、default policyとして mutable `main` URLをruntime hotlinkしないことを明記している。

### 案B: commit permalinkだけを使う

GitHub上の参照先versionは固定できる。単一fileを読むだけなら有効である。

一方、consumer側にコピーしたfileやbuild後のfileまで同一bytesか確認したい場合、commit IDだけではconsumer filesystem上の実体を直接検査できない。そこで今回の実装ではSHA-256もlockへ残す。

### 案C: tagだけを固定する

release単位で扱いやすい。しかしconsumerが最終的にどのcommitを採ったかまでlockに残す設計のほうが、再現時の参照点が明示的になる。

### 案D: commit＋SHA-256＋vendor

今回の採用案である。

consumerは中央repoをruntime dependencyにせず、自分のbuild対象へassetを保持する。その代わり、コピー元commitとdigestをlockへ記録し、CIで一致を検証する。

重要なのは「中央管理だからconsumerはassetを持たない」ではない。**中央repoは正準sourceとdistribution metadataを持ち、consumerは採用versionを自分のrepositoryに固定する**という責務分離である。

## 4. 実装

最小構成は3ファイルで作れる。

### 4.1 中央manifest

```json
{
  "id": "travel-basic",
  "file": "travel-basic-illustration.webp",
  "sha256": "8c45dfb3c32aa5d2991b9d3b9d710b66722f0ef10fb62a0b5dea2582f36ea383"
}
```

`prompt-vault` のcollection manifestは実際にasset ID、file、size、SHA-256、生成由来、用途制約を記録している。

### 4.2 consumer manifest

```json
{
  "schema_version": "1.0.0",
  "repository": "KAFKA2306/travel",
  "assets": [
    {
      "collection": "site-basics",
      "id": "travel-basic",
      "destination": "public/assets/kafka-signal/travel-basic-illustration.webp"
    }
  ]
}
```

consumerはsource pathを自由記述せず、asset IDを選択する。配置先だけをconsumer責務として宣言する。

### 4.3 lock file

vendor後に、commitとsource/destination digestを保存する。

```json
{
  "canonical_commit": "90111f8953dd2a45aca2da7053bfdeef57459b41",
  "assets": [
    {
      "id": "travel-basic",
      "destination": "public/assets/kafka-signal/travel-basic-illustration.webp",
      "source_sha256": "8c45dfb3c32aa5d2991b9d3b9d710b66722f0ef10fb62a0b5dea2582f36ea383",
      "destination_sha256": "8c45dfb3c32aa5d2991b9d3b9d710b66722f0ef10fb62a0b5dea2582f36ea383"
    }
  ]
}
```

### 最小verification

Python標準libraryだけでも確認できる。

```python
from hashlib import sha256
from pathlib import Path

EXPECTED = "8c45dfb3c32aa5d2991b9d3b9d710b66722f0ef10fb62a0b5dea2582f36ea383"
path = Path("public/assets/kafka-signal/travel-basic-illustration.webp")

actual = sha256(path.read_bytes()).hexdigest()
if actual != EXPECTED:
    raise SystemExit(f"asset drift: {actual}")
```

`travel` のCIでは、source/destination digestのlock値だけでなく、vendored fileと `dist/` のbuild後fileを実際に読み直して同じSHA-256になることを確認している。

## 5. 検証

この設計で見るべき境界は4つある。

### 1. 正準source

registryに記録されたSHA-256と中央repoの実fileが一致するか。

`prompt-vault` のvendoring実装はcanonical source SHA-256を確認してからcopyする。さらに、既存destinationがlocalで変更済み、または未管理fileを別内容で上書きしようとする場合はsilent overwriteせず失敗する。

### 2. consumer checkout

lock fileの `canonical_commit` とasset digestが期待値どおりか。

### 3. build artifact

source treeで合っていてもbuild工程で別fileに置換される可能性があるので、`dist/` 側もhashを再計算する。

`travel` のworkflowは `public/assets/...` と `dist/assets/...` の両方を検証している。

### 4. deploy後

最後に公開URLからfileを再取得してSHA-256を確認する。

`travel` のworkflowはGitHub Pages deploy成功後、公開された `travel-basic-illustration.webp` を `curl` で取得し、同じ `8c45...ea383` と一致することを検証する。

つまり検証chainは次のようになる。

```text
canonical asset
  -> vendor後のconsumer file
  -> build artifact
  -> deployed file
```

各段階で同じdigestを要求する。

## 6. 失敗と学び

### 壊れた例: URLだけを信じる

```html
<img src="https://raw.githubusercontent.com/example/assets/main/hero.webp">
```

この方式では、consumerのPRで確認したあとに中央repoの `main` が進めば、consumerのcode review外で表示内容が変わる。

### 改善後: 採用versionをconsumerで固定する

```text
asset ID       = travel-basic
source repo    = KAFKA2306/prompt-vault
source commit  = 90111f8...
SHA-256        = 8c45dfb3...ea383
destination    = public/assets/kafka-signal/travel-basic-illustration.webp
```

これならasset更新は「中央repoの変更」だけでは完了しない。consumer側で新commit・新hashをlockへ反映する変更としてreviewできる。

もう1つ重要なのは、**hashをmanifestへ書くだけでは検証にならない**ことである。`travel` の実装が強いのは、PR buildとdeploy後の両方で実fileからdigestを再計算している点にある。

## 7. 再現方法

GitHub Pagesや画像生成環境がなくても、2つのdirectoryだけで再現できる。

1. `source/hero.txt` に `version-1` と書く。
2. SHA-256を計算して `manifest.json` に保存する。
3. `source/hero.txt` を `consumer/public/hero.txt` へcopyする。
4. `lock.json` へsource commit相当の識別子とSHA-256を書く。
5. consumer側でfileを読み直し、lockのSHA-256と一致することを確認する。
6. sourceだけ `version-2` に変更し、manifestのhashを更新せずvendorを試す。
7. source hash mismatchで停止することを確認する。
8. 次にconsumer側だけ手編集し、destination hash mismatchで停止することを確認する。

最小scriptは次の形でよい。

```python
from hashlib import sha256
from pathlib import Path

expected = Path("manifest.sha256").read_text().strip()
actual = sha256(Path("source/hero.txt").read_bytes()).hexdigest()
assert actual == expected, (expected, actual)
```

ここで確かめたいのはcopy処理そのものではない。**更新がreview可能なversion changeとして現れ、期待していないbytesが黙ってconsumerへ入らないこと**である。

## まとめ

共有アセットを中央管理するとき、`main` URLを共通化するだけではversion管理にならない。

今回の実装から再利用できる最小contractは次の4点だった。

1. consumerはpathではなくcanonical asset IDを選ぶ
2. source repositoryのcommit IDを固定する
3. sourceとdestinationのSHA-256をlockへ残す
4. PR buildとdeploy後に実bytesからdigestを再計算する

GitHubのcommit permalinkは「どのversionを指したか」を固定する。consumer lockのSHA-256は「実際に配ったbytesがそのversionの期待値と一致したか」を検証する。

この2つを分けると、共有assetを増やしても「中央repoの更新だけで全siteの見た目が暗黙に変わる」状態を避けながら、各consumerの変更を小さなreview可能単位にできる。
