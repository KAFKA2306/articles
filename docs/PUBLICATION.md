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
PENDING_RELEASE
  published:false
  approval / Issue queue preserved
    │ Zenn Manual Release: exactly one article
    ▼
PUBLICATION_REQUESTED
  published:true
    │ Zenn GitHub sync
    ▼
PRODUCTION_VERIFICATION
  pipeline.zenn_production
    ├─ public RSSにslug + title一致 -> PUBLISHED_VERIFIED
    └─ missing / title mismatch / catalog error -> rollback to PENDING_RELEASE
```

GitHub push直後はZenn同期に時間差があるため、production verificationは最大10分retryできる。定期reconciliationは毎時1回、現在 `published:true` の全記事を即時判定する。

## Pre-deploy fail-closed rules

- 新規の `published:false -> true` は1変更につき最大1記事。
- 既存記事で一度指定された `published_at` は変更・削除しない。Zenn公式の公開日時immutable契約に合わせる。
- Zenn公式CLIで全記事をrenderし、`data-body-error` を含む本文は公開不可。
- `published:true` にはtitleと`published_at`を要求する。このrepositoryでは `true` を「今すでに公開されるべき状態」に限定するため、未来日時の予約公開は使わず、公開時刻までは `published:false` を維持する。

最後のルールはZenn自体の制約ではなく、このrepository固有のより厳しいinvariantである。Zenn公式は未来の`published_at`による予約公開をサポートしているが、それを使うと `published:true = 現在public` が成立しなくなるため採用しない。

## Approved pending queue

公開承認済みだがZenn productionで確認できていない記事は、公開意思を失わず `published:false` に戻す。公開承認はIssue等のqueueで保持する。

2026-08-15のrecovery queueは Issue #140 をcanonical trackerとする。

- https://github.com/KAFKA2306/articles/issues/140

`published:false` はここでは「内容が未承認」を意味しない。`PENDING_RELEASE` の記事では「Zenn本番がまだ成功していない」を意味する。

## Manual release gate

投稿制限などZenn側stateが不明なとき、自動scheduleで新規投稿を連打しない。`.github/workflows/zenn-manual-release.yml` を明示的に起動し、approved pending articleを1本だけreleaseする。

workflowは次を行う。

1. 1記事だけ `published:false -> true` にする。
2. mainへpushする。
3. Zenn公開RSSで現在の全 `published:true` を最大10分照合する。
4. 全件PASSなら対象記事を `PUBLISHED_VERIFIED` とする。
5. FAILなら対象記事を `published:false` に自動rollbackし、`PENDING_RELEASE` を維持する。

次の記事へ進めるのは前の記事が `PUBLISHED_VERIFIED` になった後だけとする。

## Immutable `published_at` recovery

誤って既存記事の `published_at` を変更してしまった場合、新しい日時を再指定しない。Git履歴を先頭から走査し、その記事で最初にcommitされた非nullの `published_at` だけをcanonical originとして復元する。

```text
first committed published_at
        │
        ├─ current valueと同じ -> no-op
        └─ current valueと違う -> originへの復元のみ許可
```

`pipeline.publication_diff` は通常の日時変更をFAILにし、Git履歴上のfirst valueへの復元だけを `PUBLICATION_DIFF_REPAIR` として許可する。任意の過去値、現在時刻、推測した公開時刻への変更は許可しない。

このrecoveryはZenn側の既存metadataとの整合を戻すための修復であり、「公開日時を書き換える」機能ではない。

## Post-deploy fail-closed rules

- GitHub Actions green、commit成功、`published:true` の存在だけでは公開成功と報告しない。
- `pipeline.zenn_production` が全 `published:true` をZenn公開RSSで照合する。
- missing slug、title mismatch、RSS取得不能はすべてFAIL。
- 完了報告は `Zenn Production Verification` がPASSした後だけ許可する。
- hourly reconciliationで、公開後に発生したdriftも再検出する。

## Zenn posting-limit boundary

Zennはユーザーごとに期間あたりの投稿上限数を持ち、上限は複数指標で決まりユーザーごとに異なると公式に説明している。したがって、このrepositoryは未知のquotaを推測して複数記事を連打しない。

公開は1本ずつ行い、production verificationが完了する前に次の新規公開へ進まない。アカウント固有のdeploy拒否理由はZenn dashboardのデプロイ履歴をauthorityとする。上限に関する確認・緩和が必要な場合、Zenn公式問い合わせフォームの「投稿制限と上限緩和」を使う。

## Canonical implementation

- pre-deploy transition guard: `pipeline/publication_diff.py`
- official renderer check: `.github/workflows/article-pipeline-ci.yml`
- manual one-at-a-time release: `.github/workflows/zenn-manual-release.yml`
- production verifier: `pipeline/zenn_production.py`
- production observer: `.github/workflows/zenn-production-verify.yml`
- recovery tracker: GitHub Issue #140
- regression tests: `tests/test_publication_diff.py`, `tests/test_zenn_production.py`

同じ判定ロジックを別workflowへ複製しない。

## External authority

- Zenn GitHub連携: https://zenn.dev/zenn/articles/connect-to-github
- Zenn CLI / publish / published_at: https://zenn.dev/zenn/articles/zenn-cli-guide
- Zenn RSS: https://zenn.dev/zenn/articles/zenn-feed-rss
- Zenn AIコンテンツ方針・投稿上限: https://info.zenn.dev/2026-03-10-ai-contents-guideline
- Zenn問い合わせ: https://zenn.dev/inquiry
