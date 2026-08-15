# Publication contract

## Invariant

このrepositoryで「公開済み」と呼べる状態は次だけとする。

```text
published: true in canonical Zenn release snapshot
+
Zenn公式ユーザーRSSにcanonical slugが存在
+
RSS上のtitleがrelease snapshotのtitleと一致
=
PUBLISHED_VERIFIED
```

公開カタログのauthorityはZenn公式ユーザーRSS `https://zenn.dev/kafka2306/feed?all=1` とする。GitHub上の `published: true`、commit成功、Actions green、deploy trigger成功だけでは公開完了と呼ばない。

## Deployment topology

通常作業とZenn production deployをbranchで分離する。

```text
main
  = drafting / review / CI / publication intent
              │
              │ explicit one-article release
              ▼
zenn-release
  = deployed production snapshot
    + approved target article
    + that article's referenced images
              │
              │ Zenn GitHub integration watches this branch
              ▼
zenn.dev
              │
              ▼
feed?all=1 verification
```

- `main` は正準作業branch。
- `zenn-release` はZenn deploy専用snapshot branch。
- `zenn-release` をmainへ丸ごと追従させない。
- `.github/workflows/zenn-manual-release.yml` だけが承認済みarticleと必要画像をrelease snapshotへ反映する。
- main上の別article、draft、実験、docsをrelease snapshotへ混入させない。
- force pushは禁止する。

## State machine

```text
DRAFT
  published:false on main
    │ explicit approval
    ▼
PUBLICATION_INTENT
  published:true on main
    │ Zenn Manual Release
    ▼
RELEASE_SNAPSHOT
  zenn-release contains approved target version
    │ Zenn GitHub sync
    ▼
PRODUCTION_VERIFICATION
    ├─ RSS slug + title一致 -> PUBLISHED_VERIFIED
    └─ missing / mismatch / fetch failure -> DEPLOY_PENDING
```

verification failureで `published:false` へ自動rollbackしない。公開意思はmain上で保持し、必要なら同じarticleをreconcileする。

## Zenn slug contract

Zennでは `articles/<slug>.md` のファイル名が記事slugになる。slugは12〜50文字、`a-z`、`0-9`、`-`、`_` のみ。

canonical validatorは `pipeline.zenn_slug` とする。

```bash
python -m pipeline.zenn_slug
python -m pipeline.zenn_slug --slug my-valid-article-slug
```

記事生成時に最終slugをfilesystem mutation前に検証し、repository-wide CIでも全articleを再検証する。公開済みslugはrenameしない。

## Main-side publication intent

Manual Releaseは入力された任意のvalid slugを1本だけ扱う。

- `published:false` なら対象articleだけを `true` にしてmainへcommitする。
- 既に `published:true` ならmainを変更せずreconcileする。
- `published_at` は既存値を保持する。
- mainへの変更がある場合、rebase後のexact commitへ `pipeline.zenn_slug`、`pipeline.publication_diff`、`pipeline.audit` を実行する。
- mainへのpushはnormal fast-forwardのみとし、force pushしない。

公開retryのためにarticle本文へmarker、timestamp、no-op commentを埋め込まない。

## Release snapshot construction

release snapshotへcopyしてよいものは原則として次だけ。

```text
articles/<approved-slug>.md
images/...   # approved articleが実際に参照するものだけ
```

workflowはrelease worktreeのchanged/untracked pathsを検査し、上記以外が混入したらfailする。

## Pre-deploy gates

`zenn-release` へpushする前にrelease snapshotそのものへ次を実行する。

1. `pipeline.zenn_slug --root <release>`
2. `collect_published_articles(<release>)` のcontract errors = 0
3. release diffがtarget article + referenced imagesだけ
4. Zenn CLI `preview --no-watch` で全article render
5. render結果に `data-body-error` がない
6. `git diff --check`

対象内容が前回releaseと同一のreconcileでは、articleを改変せず `zenn-release` に明示的なempty deploy commitを1件だけ作る。deploy trigger目的のdocs変更、本文marker、rollback commitは作らない。

## Production verification

`pipeline.zenn_production` は `--root` で指定したrelease snapshotの `published:true` をproduction expectationとして扱う。

```bash
python -m pipeline.zenn_production \
  --root _zenn_release \
  --wait-seconds 900 \
  --interval-seconds 15
```

- canonical slug missing -> FAIL
- title mismatch -> FAIL
- RSS fetch / parse failure -> FAIL
- 全件一致 -> PASS

定期 `.github/workflows/zenn-production-verify.yml` も `zenn-release` をexpectation sourceとして使う。

## Immutable `published_at`

既存 `published_at` はrelease/reconcile時に変更しない。誤変更の修復時のみ、Git履歴上でそのarticleに最初にcommitされた非null valueをcanonical originとして復元する。

禁止:
- retry時刻への更新
- 現在時刻への置換
- 推測値への置換
- 任意の過去値への変更

## Branch hygiene

- `main` と `zenn-release` は恒久branchとして保持する。
- merged / patch-equivalentでopen PRのない作業branchは `.github/workflows/branch-hygiene.yml` が削除する。
- unique patchまたはopen PRを持つbranchは自動削除しない。

## Canonical implementation

- work branch: `main`
- deploy branch: `zenn-release`
- slug validator: `pipeline/zenn_slug.py`
- transition guard: `pipeline/publication_diff.py`
- repository CI: `.github/workflows/article-pipeline-ci.yml`
- one-article release: `.github/workflows/zenn-manual-release.yml`
- production verifier: `pipeline/zenn_production.py`
- production observer: `.github/workflows/zenn-production-verify.yml`
- branch cleanup: `.github/workflows/branch-hygiene.yml`
- regression tests: `tests/test_zenn_slug.py`, `tests/test_publication_diff.py`, `tests/test_zenn_production.py`

## External authority

- Zenn GitHub integration / sync branch: https://zenn.dev/zenn/articles/connect-to-github
- Zenn CLI: https://zenn.dev/zenn/articles/zenn-cli-guide
- Zenn slug: https://zenn.dev/zenn/articles/what-is-slug
- Zenn RSS: https://zenn.dev/zenn/articles/zenn-feed-rss
