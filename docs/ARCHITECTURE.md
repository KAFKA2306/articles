# Architecture

## Responsibility

`KAFKA2306/articles` は記事生成の唯一の正準repoです。

- `graphiti`: private memory / weekly source of ideas
- `articles`: public evidence grounding / drafting / review / selection / publication
- `Zenn`: published delivery surface

責務を混ぜません。private memoryの保存やGraphiti本体の運用はこのrepoでは行いません。

## State model

生成物は3段階です。

1. `artifacts/candidates/YYYY-MM/*.md`
   - public-safeな未公開候補
   - Graphiti raw textは禁止
   - `pipeline_meta` は候補運用metadataであり、公開本文・source gate・月末査読には含めない
2. `artifacts/reports/YYYY-MM/*.json`
   - source gate、内部proxy査読、月末selectionの証跡
3. `articles/*.md`
   - Zenn front matterを持つ公開記事
   - candidate metadataは含めない

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
PROXY_REVIEW ───below target┘
  ↓
KEEP_BEST_VERSION
  ↓
ACCUMULATE_WEEKLY
  ↓
MONTH_END_REVERIFY_ALL
  ↓
3x PROXY REVIEW / MEDIAN
  ↓
FILTER PASSING SET
  ↓
DETERMINISTIC RANK
  ↓
PUBLISH TOP 1 OR 0
```

`VERIFY_SOURCES` と公開quality gateはfail-closeです。公開本数を満たすためにgateを緩めません。品質ゲートを通る候補がなければその月は0本です。

## Internal review semantics

内部5軸はLAPRAS AI Reviewで公開されている軸を参考にした `internal_lapras_rubric_proxy` です。

- LAPRAS上の実測AI Review値ではない
- `overall` は内部proxyの5軸算術平均
- target overall 4.1
- minimum overall 3.8
- minimum each axis 3.5

外部のLAPRAS実測値を取得できる公式経路が確認できるまでは、proxyと実測を混同しません。

## Candidate maturation

weekly candidate生成時にsource gateと1回の内部proxy reviewを実行します。target 4.1未達なら `revision_limit` の範囲で改稿し、各版を比較します。

best-version retentionは次の順序です。

1. quality gate PASS
2. source gate PASS
3. overall
4. 最低軸
5. 自GitHub証拠数
6. 有効一次情報数

改稿によって品質が下がっても、より良かった前版を失いません。

## Month-end selection

workflowは28〜31日 23:30 JSTに起動しますが、通常のscheduled publishは暦上の最終日だけ続行します。

当月候補はすべて同一条件で処理します。

1. `pipeline_meta` を除去
2. source gate再実行
3. 3回独立proxy review
4. 各軸中央値を採用
5. overall 3.8以上、全軸3.5以上、source gate PASSのみ残す
6. `overall` → 最低軸 → 自GitHub証拠数 → 有効一次情報数で順位付け
7. 1位だけpublish
8. 合格候補0件ならpublish 0本
9. 同月公開済みならno-op

候補0件時に月末その場で新規記事を生成するfallbackは持ちません。月次選抜は、その月に育てた候補だけを対象にします。

## Graphiti boundary

Graphiti adapterは次の順序で処理します。

1. private weeklyをread-only取得
2. `summary / highlights / decisions / next / timeline` をin-memoryで圧縮
3. private内容から技術テーマを発見
4. public GitHub signalsへ再接地
5. KAFKA2306 GitHub evidence 2件以上を返せないテーマを棄却
6. raw private contentを破棄
7. public-safe topic metadataだけcandidateへ残す
8. public evidenceだけで記事本文を生成・改稿

public repoへ残せるGraphiti由来metadataは、抽象化済みtopic、record count、復元不能digest、公開証拠、public articleの査読結果だけです。

## Failure policy

- Graphiti credentialなし: Graphiti候補のみskip
- Graphiti privacy gate fail: Graphiti候補を作らない
- primary-source不足: candidateは改稿対象、month-endではpublish集合から除外
- HTTP検証失敗: publishしない
- proxy review最低値未達: publishしない
- 当月合格候補なし: 正常な0本としてselection reportを残す
- 同月に公開済み: no-op
- scheduled runが月末日前: no-op
