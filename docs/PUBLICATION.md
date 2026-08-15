# Publication contract

## Invariant

このrepositoryでは、次を公開済みの唯一の意味とする。

```text
published: true in canonical Zenn release snapshot
+
Zennの公開ユーザーRSSにcanonical slugが存在
+
RSS上のtitleがrelease snapshotのtitleと一致
=
PUBLISHED_VERIFIED
```

公開カタログのauthorityはZenn公式のユーザーRSS `https://zenn.dev/kafka2306/feed?all=1` とする。GitHub上の `published: true`、commit成功、Actions greenだけでは公開完了と呼ばない。

## Deployment topology

Zenn deployと通常の執筆を同じbranchに載せない。

```text
main
  = drafting / review / CI / publication intent
              │
              │ explicit one-article release
              ▼
zenn-release
  = last deployed snapshot
    + approved target article
    + that article's referenced images
              │
              │ Zenn GitHub integration watches this branch only
              ▼
zenn.dev
              │
              ▼
feed?all=1 verification
```

- `main` はrepositoryの正準作業branch。
- `zenn-release` はZenn deploy専用snapshot branch。
- `zenn-release` をmainへ丸ごと追従させない。
- `.github/workflows/zenn-manual-release.yml` だけが、承認済みの対象articleと必要画像をrelease snapshotへcopyしてcommitする。
- main上で並行して変更された別article、draft、実験、docsは、そのreleaseへ混入させない。
- release branchへforce pushしない。

Zenn公式は「登録した同期branchに変更があると自動deploy」としている。mainに多数のagent/editorial commitが入る運用では、mainを直接同期branchにすると非公開作業までdeploy queueを消費するため、専用branchへ分離する。

### One-time Zenn setting

Zenn DashboardのGitHubデプロイ設定で同期branchを **`zenn-release`** にする。GitHub側branchは作成済みで、release workflowもこのbranchをdeploy targetとして使う。

Zenn側branch変更が確認できるまでは、mainへのpushでも旧設定によるdeployが発生し得る。移行完了後はZenn Dashboardのdeploy historyで対象branchが `zenn-release` になっていることを確認する。

## State machine

```text
DRAFT
  published:false on main
    │ explicit human approval
    ▼
PENDING_RELEASE
  published:false on main
    │ Zenn Manual Release: exactly one article
    ▼
PUBLICATION_REQUESTED
  published:true on main
    │ copy approved article only
    ▼
RELEASE_SNAPSHOT
  zenn-release contains approved target version
    │ Zenn GitHub sync
    ▼
PRODUCTION_VERIFICATION
  pipeline.zenn_production --root release_snapshot
    ├─ RSS slug + title一致 -> PUBLISHED_VERIFIED
    └─ missing / mismatch / fetch failure -> DEPLOY_PENDING
```

**verification failureで `published:false` へrollbackしない。** rollback pushは新しいZenn deployを発生させ、非同期queueで古いsnapshotが後から反映される振動を作るためである。公開意思はmain上で `published:true` のまま保持し、必要なら同じ対象articleをreconcileして新しいrelease commitを作る。

## Zenn slug contract

Zennでは `articles/<slug>.md` のファイル名（拡張子を除く）が記事slugになる。slugは12〜50文字、`a-z`、`0-9`、`-`、`_` のみ。

このrepositoryでは `pipeline.zenn_slug` をcanonical validatorとする。

```bash
python -m pipeline.zenn_slug
python -m pipeline.zenn_slug --slug my-valid-article-slug
```

記事生成時は最終slugを先に検証し、不正slugならfilesystem mutation前に失敗する。CIのrepository-wide検査は第二防衛線である。

公開済みslugはファイル名変更で修正しない。公開前の不正slugだけをrenameする。

## Main-side publication intent

Manual Releaseはmain上で対象articleだけを変更する。

- `published:false` なら `true` にする。
- 既に `true` ならreconcileとして扱う。
- `published_at` は既存値を保持する。
- 非表示 `zenn-deploy-sync` markerだけを更新し、同じarticleの再deployを一意のcommitにする。
- mainへのrelease commitは最新mainへrebase後、normal fast-forward pushする。
- force pushは禁止。
- rebase後のexact commitに `pipeline.zenn_slug`、`pipeline.publication_diff`、`pipeline.audit` を実行する。

mainへのpublication-intent commitは、Zenn deployそのものではない。Zenn側が `zenn-release` を同期branchとしていることが前提である。

## Release snapshot construction

main commit後、workflowは `zenn-release` を別worktreeへcheckoutする。

release snapshotへcopyしてよいものは原則として次だけ。

```text
articles/<approved-slug>.md
images/...   # approved articleが実際に参照するものだけ
```

workflowはrelease worktreeのchanged/untracked pathsを列挙し、上記以外が混入したらfailする。

これにより、main上の別article編集、未承認draft、docs、実験コード、agentの並行作業はrelease snapshotへ入らない。

## Pre-deploy release gates

`zenn-release` へcommitする前に、release snapshotそのものへ次を実行する。

1. `pipeline.zenn_slug --root <release>`
2. `collect_published_articles(<release>)` のcontract errors = 0
3. release diffがtarget article + referenced imagesだけ
4. Zenn CLI `preview --no-watch` で全article render
5. render結果に `data-body-error` がない
6. `git diff --check`

このgateを通過したsnapshotだけを `zenn-release` へnormal pushする。

## Production verification

`pipeline.zenn_production` は `--root` を受け取り、**指定snapshotの `published:true`** をproduction expectationとして扱う。

Manual Releaseではdeploy直後に、

```bash
python -m pipeline.zenn_production \
  --root _zenn_release \
  --wait-seconds 900 \
  --interval-seconds 15
```

を実行する。

定期 `.github/workflows/zenn-production-verify.yml` はmain上の最新verifier implementationを使いつつ、別checkoutした `zenn-release` を `--root` に指定する。mainの作業中stateをproduction expectationには使わない。

- canonical slug missing -> FAIL
- title mismatch -> FAIL
- RSS fetch / parse failure -> FAIL
- 全件一致 -> PASS

## Draft/editorial commits

Zenn deploy branch分離後は、通常のmain commitでZenn queueを消費しない。そのためZenn回避だけを目的に `[skip ci]` を常用する必要はない。GitHub CIをskipする副作用があるため、branch移行完了後は通常のCIを維持する。

移行前の旧main監視期間だけは、不要deployを抑えるため既存automationが `[skip ci]` を使う場合がある。

## Immutable `published_at` recovery

既存articleの `published_at` を誤変更した場合、現在時刻や任意の過去値へ変更しない。Git履歴上、そのarticleで最初にcommitされた非null valueだけをcanonical originとして復元する。

`pipeline.publication_diff` は通常の日時変更をFAILにし、first valueへのrecoveryだけをrepairとして許可する。

## Posting-limit boundary

Zenn側の投稿上限・アカウント固有拒否理由はZenn Dashboardのdeploy historyをauthorityとする。未知のquotaを推測して複数articleを連打しない。

## Canonical implementation

- canonical work branch: `main`
- canonical deploy snapshot branch: `zenn-release`
- slug validator: `pipeline/zenn_slug.py`
- transition guard: `pipeline/publication_diff.py`
- renderer / repository CI: `.github/workflows/article-pipeline-ci.yml`
- one-at-a-time release: `.github/workflows/zenn-manual-release.yml`
- production verifier: `pipeline/zenn_production.py`
- scheduled production observer: `.github/workflows/zenn-production-verify.yml`
- regression tests: `tests/test_zenn_slug.py`, `tests/test_publication_diff.py`, `tests/test_zenn_production.py`

## External authority

- Zenn GitHub integration / sync branch: https://zenn.dev/zenn/articles/connect-to-github
- Zenn CLI / publish / deploy history: https://zenn.dev/zenn/articles/zenn-cli-guide
- Zenn slug: https://zenn.dev/zenn/articles/what-is-slug
- Zenn RSS: https://zenn.dev/zenn/articles/zenn-feed-rss
