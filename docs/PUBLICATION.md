# Zenn publication

Zennへの本番同期は、`zenn-release` の変更だけで発生させる。

```text
main
  ↓  人が published 状態を確定
Zenn Manual Release
  ↓  対象1記事だけを同期
zenn-release
  ↓  Zenn Connect
zenn.dev
```

Zenn公式では、登録したブランチに変更があると自動で同期（デプロイ）が開始される。したがって、`zenn-release` へのpush回数をそのまま本番デプロイ回数として扱う。

- https://zenn.dev/zenn/articles/connect-to-github
- https://zenn.dev/zenn/articles/zenn-cli-guide

## 1. main

`main` は執筆・レビュー・公開意思の正準。

公開する記事:

```yaml
published: true
published_at: YYYY-MM-DD HH:MM
```

非公開にする記事:

```yaml
published: false
```

`published_at` はretry目的では変更しない。

通常の生成・監査・CIは `main` だけを変更し、`zenn-release` には触れない。

## 2. Zenn Manual Release

`.github/workflows/zenn-manual-release.yml` だけが `zenn-release` を更新する正規経路。

手動実行時に次を指定する。

- `slug`: 対象1記事
- `action`: `publish` または `unpublish`
- `confirm`: Zenn本番デプロイを1回発生させる意思確認

workflowは次をfail-closedで実行する。

1. slugを検証する
2. `main` の `published` が要求状態と一致することを確認する
3. 対象記事と `images/<slug>/` だけを `zenn-release` worktreeへコピーする
4. staged diffが対象slug以外を含めば停止する
5. `zenn-release` が同一内容ならcommitもpushも行わない
6. 差分がある場合だけ1 commitをnormal fast-forward pushする
7. publishは公開RSS、unpublishは公開RSSからの消失で確認する

`zenn-release` が途中で他の更新を受けてpushが競合した場合は停止する。force push、空commit、retry用本文変更は行わない。

## 3. zenn-release

`zenn-release` はZenn Connectが監視する本番snapshot branch。

**直接編集・直接push・PR mergeによる通常作業は禁止。**

公開・非公開・記事更新・画像更新を含め、Zennへ反映したい変更は必ず `Zenn Manual Release` を通す。

通常のGitHub作業やagentは `zenn-release` を書き込み対象として扱わない。

## デプロイ回数の不変条件

1回の明示操作について、次のどちらかだけを許可する。

```text
requested snapshot == zenn-release
→ 0 commit
→ 0 Zenn deploy

requested snapshot != zenn-release
→ 1 commit
→ 1 Zenn deploy
```

同一slug・同一内容の再実行で追加commitを作らない。

固定の「1日N回」制限はrepository側に実装しない。Zenn公式はユーザーごとに期間あたりの投稿上限があると説明しているが、具体的な件数や期間は公開していないため、未公開値を推測しない。

- https://info.zenn.dev/2026-03-10-ai-contents-guideline

## 公開完了

GitHubへのpushだけでは完了にしない。

publishは `pipeline.zenn_production` がZenn公式ユーザーRSSでslugとtitleを確認できた場合のみ完了とする。

```bash
python -m pipeline.zenn_production --root <zenn-release checkout>
```

unpublishは同じ公開RSSから対象slugが消えた場合のみ完了とする。

定期確認は `.github/workflows/zenn-production-verify.yml` が `zenn-release` を基準に行う。

## 画像

記事固有画像は次だけを使う。

```text
images/<slug>/
```

release workflowは対象slugの画像ディレクトリだけを同期する。

## 禁止

- `zenn-release` への直接push
- `zenn-release` を通常の作業branchとして使うこと
- retry用の本文コメント追加
- retry用のtimestamp変更
- retry用の空commit
- `published_at` のretry目的変更
- force push
- 1回のreleaseで複数記事を変更すること
- 通常CIからZenn本番同期を起動すること
- Zennが公開していない投稿上限値を推測して固定すること

## Zenn側設定

Zenn Connectの同期branchは **`zenn-release`** に固定する。

Zenn公式では同期branchをダッシュボードから指定でき、登録したbranchへのpushまたはmergeでデプロイが始まる。

- https://zenn.dev/zenn/articles/connect-to-github

この外部設定はrepository内のコードだけでは強制できないため、Zennダッシュボード上でも `zenn-release` になっていることを変更時に確認する。
