# Zenn publication

公開経路は3段階だけにする。

```text
main
  ↓  published: true を人が確定
Zenn Manual Release
  ↓  対象1記事だけコピー
zenn-release
  ↓  Zenn Connect
zenn.dev
```

## 1. main

`main` は執筆とレビューの正準。

公開する記事だけFront Matterを次の状態にする。

```yaml
published: true
published_at: YYYY-MM-DD HH:MM
```

`published_at` は公開retryのために変更しない。

## 2. Zenn Manual Release

`.github/workflows/zenn-manual-release.yml` を手動実行し、slugを1件指定する。

workflowが行うことは次だけ。

1. slugと記事を検証する
2. `published: true` と `published_at` を確認する
3. `articles/<slug>.md` を `zenn-release` へコピーする
4. `images/<slug>/` があれば同時にコピーする
5. `zenn-release` をpushする
6. Zenn公開状態を確認する

workflowはmainの記事本文、`published`、`published_at` を書き換えない。

同じ内容を再送する場合は、記事を改変せず `zenn-release` に空のdeploy commitを1件だけ作る。

## 3. zenn-release

`zenn-release` はZenn Connectが監視するデプロイ専用branch。

通常作業は行わない。

Zenn公式では、登録したbranchに変更があると同期が開始され、変更されたMarkdownファイルがzenn.devへ同期される。

- https://zenn.dev/zenn/articles/connect-to-github
- https://zenn.dev/zenn/articles/zenn-cli-guide

## 公開完了

GitHubへのpushだけでは完了にしない。

`pipeline.zenn_production` がZenn公式ユーザーRSSでslugとtitleを確認できた時だけ公開済みとする。

```bash
python -m pipeline.zenn_production --root <zenn-release checkout>
```

定期確認は `.github/workflows/zenn-production-verify.yml` が `zenn-release` を基準に行う。

## 画像

記事固有画像は次に置く。

```text
images/<slug>/
```

これ以外の画像配置を増やさない。

## 禁止

- retry用の本文コメント追加
- retry用のtimestamp変更
- `published_at` の書き換え
- `zenn-release` での通常開発
- `main` をproduction snapshotとして検証すること
- 複数記事を1回のmanual releaseで公開すること

## Zenn側設定

Zenn Connectの同期branchは `zenn-release` にする。

Zenn公式では同期branchをダッシュボードから指定できる。

- https://zenn.dev/zenn/articles/connect-to-github
