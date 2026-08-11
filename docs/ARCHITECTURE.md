# Architecture

## Responsibility

`KAFKA2306/articles` は記事生成の唯一の正準repoです。

- `graphiti`: private memory / weekly source of ideas
- `articles`: public evidence grounding / drafting / review / publication
- `Zenn`: published delivery surface

責務を混ぜません。private memoryの保存やGraphiti本体の運用はこのrepoでは行いません。

## State model

生成物は3段階です。

1. `artifacts/candidates/YYYY-MM/*.md`
   - public-safeな未公開候補
   - Graphiti raw textは禁止
2. `artifacts/reports/YYYY-MM/*.json`
   - source gateと査読の証跡
3. `articles/*.md`
   - Zenn front matterを持つ公開記事

## Autonomous state machine

```text
DISCOVER
  ↓
GROUND
  ↓
DRAFT
  ↓
VERIFY_SOURCES ──fail──> REVISE
  ↓ pass                  ↑
REVIEW ─────────fail──────┘
  ↓ pass
SELECT
  ↓
PUBLISH
```

`VERIFY_SOURCES` と `REVIEW` はfail-closeです。公開本数を満たすためにgateを緩めません。

## Graphiti boundary

Graphiti adapterは次の順序で処理します。

1. private weeklyをread-only取得
2. `summary / highlights / decisions / next / timeline` をin-memoryで圧縮
3. private内容から技術テーマを発見
4. public GitHub signalsへ再接地
5. KAFKA2306 GitHub evidence 2件以上を返せないテーマを棄却
6. raw private contentを破棄
7. public-safe topic metadataだけcandidateへ残す

public repoへ残せるGraphiti由来metadataは、抽象化済みtopic、record count、復元不能digest、公開証拠だけです。

## Failure policy

- Graphiti credentialなし: Graphiti候補のみskip
- Graphiti privacy gate fail: Graphiti候補を作らない
- primary-source不足: publishしない
- HTTP検証失敗: publishしない
- review最低値未達: revise、上限到達後はpublishしない
- 同月に公開済み: no-op
