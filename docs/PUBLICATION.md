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

## Zenn slug contract

Zennでは `articles/<slug>.md` のファイル名（拡張子を除く）がそのまま記事slugになる。slugは次をすべて満たす必要がある。

- 12〜50文字
- 半角英小文字 `a-z`
- 半角数字 `0-9`
- ハイフン `-`
- アンダースコア `_`

このrepositoryでは `pipeline.zenn_slug` をslugのcanonical validatorとする。

```bash
# repository内の全記事を検査
python -m pipeline.zenn_slug

# 新規slug候補を作成前に検査
python -m pipeline.zenn_slug --slug my-valid-article-slug
```

`Article Pipeline CI` はPR/pushの最初に全 `articles/**/*.md` を検査し、1件でも不正ならZenn CLIやpublication処理へ進まない。`pipeline.publication_diff` と `Zenn Manual Release` も同じvalidatorを再利用する。

公開済みslugはファイル名変更で修正しない。Zenn上では別記事扱いになるため、公開前の不正slugだけをリネームする。

## Pre-deploy fail-closed rules

- 全記事のfilename/slugが `pipeline.zenn_slug` を通過すること。
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

1. repository全体と入力slugを `pipeline.zenn_slug` で検査する。
2. 1記事だけ `published:false -> true` にする。
3. mainへpushする。
4. Zenn公開RSSで現在の全 `published:true` を最大10分照合する。
5. 全件PASSなら対象記事を `PUBLISHED_VERIFIED` とする。
6. FAILなら対象記事を `published:false` に自動rollbackし、`PENDING_RELEASE` を維持する。

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

- slug validator: `pipeline/zenn_slug.py`
- pre-deploy transition guard: `pipeline/publication_diff.py`
- official renderer check: `.github/workflows/article-pipeline-ci.yml`
- manual one-at-a-time release: `.github/workflows/zenn-manual-release.yml`
- production verifier: `pipeline/zenn_production.py`
- production observer: `.github/workflows/zenn-production-verify.yml`
- recovery tracker: GitHub Issue #140
- regression tests: `tests/test_zenn_slug.py`, `tests/test_publication_diff.py`, `tests/test_zenn_production.py`

slug判定ロジックは `pipeline.zenn_slug` に集約し、別workflowへregexを複製しない。

## External authority

- Zenn slug: https://zenn.dev/zenn/articles/what-is-slug
- Zenn GitHub連携: https://zenn.dev/zenn/articles/connect-to-github
- Zenn CLI / publish / published_at: https://zenn.dev/zenn/articles/zenn-cli-guide
- Zenn RSS: https://zenn.dev/zenn/articles/zenn-feed-rss
- Zenn AIコンテンツ方針・投稿上限: https://info.zenn.dev/2026-03-10-ai-contents-guideline
- Zenn問い合わせ: https://zenn.dev/inquiry
