# Publication contract

## Invariant

このrepositoryでは、次を常に同値にする。

```text
published: true
=
Zenn production URL が HTTP 200
+
URL が https://zenn.dev/kafka2306/articles/<slug> のまま
+
Zenn上のtitleがrepositoryのtitleと一致
```

`published: true` は「公開を依頼した」だけではない。上のproduction verificationまで通った状態だけを公開済みと呼ぶ。

## State machine

```text
DRAFT
  published:false
    │ explicit human approval
    ▼
PUBLICATION_REQUESTED
  published:true を main へ反映
    │ Zenn GitHub sync
    ▼
PRODUCTION_VERIFICATION
  pipeline.zenn_production
    ├─ 200 + canonical URL + title match -> PUBLISHED_VERIFIED
    └─ 404 / redirect / title mismatch / network failure -> FAILED
```

GitHub push直後はZenn同期に時間差があるため、push runだけ最大10分retryする。定期reconciliationは毎時1回、即時判定する。

## Fail-closed rules

- `published:true` なのに `published_at` がない記事は不合格。
- `published:true` で未来の `published_at` を持つ記事は不合格。予約公開が必要なら公開時刻までは `published:false` を維持する。
- 404、Zenn以外へのredirect、slug不一致、title mismatchはすべて不合格。
- GitHub Actions green、commit成功、`published:true` の存在だけでは公開成功と報告しない。
- 完了報告は `Zenn Production Verification` が対象commitでPASSした後だけ許可する。

## Canonical implementation

- verifier: `pipeline/zenn_production.py`
- production observer: `.github/workflows/zenn-production-verify.yml`
- regression tests: `tests/test_zenn_production.py`

同じ判定ロジックを別workflowへ複製しない。production truthはverifierへ集約する。

## External authority

Zenn公式では、`published: true` の記事を連携GitHub repositoryの登録branchへpushすると同期が開始される。一方、デプロイエラーはZenn dashboardのデプロイ履歴で確認する必要があり、反映には時間がかかる場合がある。

- https://zenn.dev/zenn/articles/zenn-cli-guide
