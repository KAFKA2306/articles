# Zenn publication

Zenn本番への変更は、`zenn-release` が動いたときだけ発生させる。

```text
main
  ↓  人が published 状態を確定
Zenn Manual Release
  ↓  一時 zenn-sync/* branch + PRを作るだけ
human merge
  ↓  zenn-release が1回だけ更新
Zenn Connect
  ↓
zenn.dev
```

Zenn公式では、登録したブランチへのpushまたはPR mergeでデプロイが開始される。したがって、監視branchである `zenn-release` を通常のautomationから直接更新しない。

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

`.github/workflows/zenn-manual-release.yml` は `zenn-release` へ直接pushしない。

手動実行時に次を指定する。

- `slug`: 対象1記事
- `action`: `publish` または `unpublish`
- `confirm`: pending production changeを1件作る意思確認

workflowは次をfail-closedで実行する。

1. slugを検証する
2. `main` の `published` が要求状態と一致することを確認する
3. `zenn-release` 向けのopen PRが既に1件でもあれば停止する
4. 対象記事と `images/<slug>/` だけを `zenn-release` snapshotへ適用する
5. staged diffが対象slug以外を含めば停止する
6. `zenn-release` が同一内容ならbranchもPRも作らない
7. 差分がある場合だけ `zenn-sync/<run>` branchへcommitする
8. `zenn-release` 宛てPRを1件作る
9. auto-mergeしない

この時点では `zenn-release` は動かないため、Zenn本番デプロイは発生しない。

## 3. 人によるmerge

Zenn本番へ反映したい場合だけ、`zenn-release` 宛てのPRを人が確認してmergeする。

merge前に最低限確認する。

- 対象slugが1件だけ
- `action` が意図どおり
- unrelated fileがない
- 同じ目的の別PRがない

mergeにより `zenn-release` が1回だけ更新され、その1回がZenn Connectの本番同期要求になる。

## 4. zenn-release

`zenn-release` はZenn Connectが監視する本番snapshot branch。

**直接編集・直接push・通常automationからの更新は禁止。**

公開・非公開・記事更新・画像更新を含め、Zennへ反映したい変更は必ず `Zenn Manual Release` が作る単一PRを経由する。

`zenn-release` へのpush後は `.github/workflows/zenn-production-verify.yml` がZenn公開状態を検証する。このverificationはread-onlyで、release branchへcommitしない。

## デプロイ回数の不変条件

1回の明示操作について次だけを許可する。

```text
requested snapshot == zenn-release
→ 0 release branch
→ 0 PR
→ 0 zenn-release update
→ 0 Zenn deploy

requested snapshot != zenn-release
→ 1 temporary branch
→ 1 pending PR
→ human mergeまで 0 Zenn deploy
→ merge時に zenn-release 1 update
→ 1 Zenn deploy
```

同一slug・同一内容の再実行で追加のproduction commitを作らない。

固定の「1日N回」制限はrepository側に実装しない。Zenn公式はユーザーごとに期間あたりの投稿上限があると説明しているが、具体的な件数や期間は公開していないため、未公開値を推測しない。

- https://info.zenn.dev/2026-03-10-ai-contents-guideline

## 公開完了

GitHubへのmergeだけでは公開完了にしない。

publishは `pipeline.zenn_production` がZenn公式ユーザーRSSでslugとtitleを確認できた場合のみ完了とする。

```bash
python -m pipeline.zenn_production --root <zenn-release checkout>
```

非公開化はZenn公開RSSから対象slugが消えたことを確認して完了とする。

## 画像

記事固有画像は次だけを使う。

```text
images/<slug>/
```

release workflowは対象slugの画像ディレクトリだけを同期する。

## 禁止

- `zenn-release` への直接push
- `zenn-release` を通常の作業branchとして使うこと
- release PRのauto-merge
- 同時に複数の `zenn-release` PRを開くこと
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

Zenn公式では同期branchをダッシュボードから指定できる。

- https://zenn.dev/zenn/articles/connect-to-github

さらにGitHub側では `zenn-release` に branch protection / ruleset を設定し、直接pushを禁止してPR経由を強制するのがサーバー側の最終防御になる。GitHub公式は protected branch / ruleset でpull request要件、force push禁止、bypass禁止などを設定できるとしている。

- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches

このGitHub設定とZennダッシュボードの同期branch設定はrepository内コードだけでは変更できないため、外部設定として維持する。
