# Publication contract

## Invariant

このrepositoryでは、次を公開済みの唯一の意味とする。

```text
published: true
+
Zennの公開ユーザーRSSにcanonical slugが存在
+
RSS上のtitleがrepositoryのtitleと一致
=
PUBLISHED_VERIFIED
```

公開カタログのauthorityはZenn公式のユーザーRSS `https://zenn.dev/kafka2306/feed?all=1` とする。GitHub上の `published: true`、commit成功、Actions greenだけでは公開完了と呼ばない。

## Deployment topology

Zenn deployと通常の執筆を同じbranchに載せない。

```text
main
  ├─ drafting / review / experiments / CI
  ├─ published:false drafts
  └─ publication intent
          │
          │ Zenn Manual Release only
          ▼
zenn-release
  └─ exact release snapshot
          │
          │ Zenn GitHub integration watches this branch only
          ▼
zenn.dev
          │
          ▼
feed?all=1 verification
```

- `main` はrepositoryの正準作業branch。
- `zenn-release` はZenn deploy専用branch。
- `zenn-release` へ直接実装・記事編集をcommitしない。
- `.github/workflows/zenn-manual-release.yml` だけが `zenn-release` をfast-forwardする。
- force pushは禁止。`zenn-release` がrelease targetのancestorでない場合はfail closedする。
- 通常のmain commitはZenn deploy eventではない。

Zenn公式は「登録した同期branchに変更があると自動deploy」としているため、mainに多数のagent/editorial commitが入る運用では専用deploy branchへ分離する。

### One-time Zenn setting

Zenn DashboardのGitHubデプロイ設定で同期branchを **`zenn-release`** にする。GitHub側branchは作成済みで、release workflowとproduction verifierもこのbranchをcanonical deploy branchとして扱う。

branch変更がZenn側で確認できるまでは、mainへのpushでも旧設定によるdeployが発生し得る。移行完了後はZenn deploy履歴で対象branchが `zenn-release` になっていることを確認する。

## State machine

```text
DRAFT
  published:false
    │ explicit human approval
    ▼
PENDING_RELEASE
  published:false
    │ Zenn Manual Release: exactly one article
    ▼
PUBLICATION_REQUESTED
  published:true on main
    │ exact validated SHA
    ▼
DEPLOY_TRIGGERED
  zenn-release fast-forwarded to that SHA
    │ Zenn GitHub sync
    ▼
PRODUCTION_VERIFICATION
  pipeline.zenn_production
    ├─ RSS slug + title一致 -> PUBLISHED_VERIFIED
    └─ missing / mismatch / fetch failure -> DEPLOY_PENDING
```

**verification failureで `published:false` へrollbackしない。** rollback pushは新しいZenn deployを発生させ、非同期queueで古いsnapshotが後から反映される振動を作るためである。公開意思は `published:true` のまま保持し、必要なら同じ対象記事をreconcileして新しいrelease snapshotを作る。

## Zenn slug contract

Zennでは `articles/<slug>.md` のファイル名（拡張子を除く）が記事slugになる。slugは12〜50文字、`a-z`、`0-9`、`-`、`_` のみ。

このrepositoryでは `pipeline.zenn_slug` をcanonical validatorとする。

```bash
python -m pipeline.zenn_slug
python -m pipeline.zenn_slug --slug my-valid-article-slug
```

記事生成時は最終slugを先に検証し、不正slugならfilesystem mutation前に失敗する。CIのrepository-wide検査は第二防衛線である。

公開済みslugはファイル名変更で修正しない。公開前の不正slugだけをrenameする。

## Pre-deploy fail-closed rules

- 全article pathが `pipeline.zenn_slug` を通る。
- 1 releaseで対象記事は1本だけ。
- `published:false -> true` は明示的な現在の人間承認がある場合だけ。
- 既存 `published_at` は変更・削除しない。canonical recoveryはGit履歴上のfirst committed valueだけ。
- Zenn CLI renderを通す。
- release mutationは対象 `articles/<slug>.md` だけ。
- mainへのpublication commitはnormal fast-forward push。競合時は最新mainへrebaseし、force pushしない。
- `zenn-release` はrelease target SHAへfast-forwardできる場合だけ更新する。

## Manual release gate

`.github/workflows/zenn-manual-release.yml` は次を行う。

1. mainをcheckoutする。
2. repository全体と入力slugを検査する。
3. 対象が `published:false` なら1本だけ `true` にする。既に `true` ならreconcile modeにする。
4. 対象articleへ非表示の `zenn-deploy-sync` markerを更新し、release attemptを一意のcommitにする。
5. mutationが対象article 1ファイルだけであることを確認する。
6. 最新mainへrebaseしてnormal fast-forward pushする。
7. その**exact commit SHA**へ `zenn-release` をfast-forwardする。
8. Zenn RSSを最大15分pollする。
9. slug + normalized title一致なら `PUBLISHED_VERIFIED`。
10. 未収束なら `DEPLOY_PENDING`。rollback commitは作らない。

次の記事へ進めるのは、直前のreleaseが `PUBLISHED_VERIFIED` になった後とする。

## Production verification

`.github/workflows/zenn-production-verify.yml` は `zenn-release` pushをdeploy eventとして監視する。push時は最大15分pollし、schedule / manual dispatchでは現在のproduction stateを即時reconcileする。

verifier自身も `zenn-release` をcheckoutする。mainの作業中snapshotをproduction expectationとして比較しない。

検査対象は、release snapshotに存在する現在dueな `published:true` 全記事。

- canonical slug missing -> FAIL
- title mismatch -> FAIL
- RSS fetch / parse failure -> FAIL
- 全件一致 -> PASS

## Draft/editorial commits

Zenn deploy branch分離後は、通常のmain commitでZenn queueを消費しない。そのためZenn回避だけを目的に `[skip ci]` を常用する必要はない。GitHub CIをskipする副作用があるため、deploy branch移行完了後は通常のCIを維持する。

移行前の旧main監視期間だけは、不要なZenn deployを抑えるため既存automationが `[skip ci]` を使う場合がある。

## Immutable `published_at` recovery

既存記事の `published_at` を誤変更した場合、現在時刻や任意の過去値へ変更しない。Git履歴上、その記事で最初にcommitされた非null valueだけをcanonical originとして復元する。

`pipeline.publication_diff` は通常の日時変更をFAILにし、first valueへのrecoveryだけをrepairとして許可する。

## Posting-limit boundary

Zenn側の投稿上限・アカウント固有拒否理由はZenn Dashboardのdeploy historyをauthorityとする。未知のquotaを推測して複数記事を連打しない。

## Canonical implementation

- deploy branch: `zenn-release`
- slug validator: `pipeline/zenn_slug.py`
- transition guard: `pipeline/publication_diff.py`
- renderer / repository CI: `.github/workflows/article-pipeline-ci.yml`
- one-at-a-time release: `.github/workflows/zenn-manual-release.yml`
- production verifier: `pipeline/zenn_production.py`
- production observer: `.github/workflows/zenn-production-verify.yml`
- regression tests: `tests/test_zenn_slug.py`, `tests/test_publication_diff.py`, `tests/test_zenn_production.py`

## External authority

- Zenn GitHub integration / sync branch: https://zenn.dev/zenn/articles/connect-to-github
- Zenn CLI / publish / deploy history: https://zenn.dev/zenn/articles/zenn-cli-guide
- Zenn slug: https://zenn.dev/zenn/articles/what-is-slug
- Zenn RSS: https://zenn.dev/zenn/articles/zenn-feed-rss
