# Publication contract

## Invariant

このrepositoryでは、次を公開済みの唯一の意味とする。

```text
published: true
=
Zennの公開ユーザーRSSにcanonical slugが存在
+
RSS上のtitleがrepositoryのtitleと一致
```

公開カタログのauthorityはZenn公式のユーザーRSS `https://zenn.dev/kafka2306/feed?all=1` とする。個別HTMLはbot対策等で取得条件が変わり得るため、CIの全件reconciliationには使わない。

`published: true` は「公開を依頼した」の意味にはしない。production verificationを通過して初めて公開済みと呼ぶ。

## State machine

```text
DRAFT
  published:false
    │ explicit human approval
    ▼
PUBLICATION_REQUESTED
  1変更につき最大1記事だけ false -> true
    │ Zenn GitHub sync
    ▼
PRODUCTION_VERIFICATION
  pipeline.zenn_production
    ├─ public RSSにslug + title一致 -> PUBLISHED_VERIFIED
    └─ missing / title mismatch / catalog error -> FAILED
```

GitHub push直後はZenn同期に時間差があるため、記事変更を含むpush runだけ最大10分retryする。定期reconciliationは毎時1回、即時判定する。

## Pre-deploy fail-closed rules

- 新規の `published:false -> true` は1変更につき最大1記事。
- 既存記事で一度指定された `published_at` は変更・削除しない。Zenn公式の公開日時immutable契約に合わせる。
- Zenn公式CLIで全記事をrenderし、`data-body-error` を含む本文は公開不可。
- `published:true` にはtitleと`published_at`を要求する。このrepositoryでは `true` を「今すでに公開されるべき状態」に限定するため、未来日時の予約公開は使わず、公開時刻までは `published:false` を維持する。

最後のルールはZenn自体の制約ではなく、このrepository固有のより厳しいinvariantである。Zenn公式は未来の`published_at`による予約公開をサポートしているが、それを使うと `published:true = 現在public` が成立しなくなるため採用しない。

## Post-deploy fail-closed rules

- GitHub Actions green、commit成功、`published:true` の存在だけでは公開成功と報告しない。
- `pipeline.zenn_production` が全 `published:true` をZenn公開RSSで照合する。
- missing slug、title mismatch、RSS取得不能はすべてFAIL。
- 完了報告は `Zenn Production Verification` がPASSした後だけ許可する。
- hourly reconciliationで、公開後に発生したdriftも再検出する。

## Zenn posting-limit boundary

Zennはユーザーごとに期間あたりの投稿上限数を持ち、上限は複数指標で決まりユーザーごとに異なると公式に説明している。したがって、このrepositoryは未知のquotaを推測して複数記事を連打しない。

公開は1本ずつ行い、production verificationが完了する前に次の新規公開へ進まない。アカウント固有のdeploy拒否理由はZenn dashboardのデプロイ履歴をauthorityとする。

## Canonical implementation

- pre-deploy transition guard: `pipeline/publication_diff.py`
- official renderer check: `.github/workflows/article-pipeline-ci.yml`
- production verifier: `pipeline/zenn_production.py`
- production observer: `.github/workflows/zenn-production-verify.yml`
- regression tests: `tests/test_publication_diff.py`, `tests/test_zenn_production.py`

同じ判定ロジックを別workflowへ複製しない。

## External authority

- Zenn GitHub連携: https://zenn.dev/zenn/articles/connect-to-github
- Zenn CLI / publish / published_at: https://zenn.dev/zenn/articles/zenn-cli-guide
- Zenn RSS: https://zenn.dev/zenn/articles/zenn-feed
- Zenn AIコンテンツ方針・投稿上限: https://info.zenn.dev/2026-03-10-ai-contents-guideline
