<!-- pipeline_meta: {"idea_source": "public-github-bootstrap", "idea_only": true, "raw_private_content_persisted": false, "topic": {"title": "「取得できた」を成功条件にしない：fail-closeなデータパイプラインで取得・検証・配布を分離する", "audience": "外部APIを扱うデータエンジニア", "public_evidence": ["https://github.com/KAFKA2306/semiconductor-earnings-model/commit/8cf66c2196fda9da060768e67de0893a9584cb22", "https://github.com/KAFKA2306/investor2/commit/0e87aaf3ff1b8f73db970765ff337c964f30c56f"]}} -->

# 「取得できた」を成功条件にしない：fail-closeなデータパイプラインで取得・検証・配布を分離する

外部APIからデータを集めるパイプラインを運用しているデータエンジニア向けの記事です。問題は、HTTP 200やCSV生成を「成功」とみなすと、古い・欠損した・根拠の弱いデータまで下流へ流れてしまうことです。ここでは、実際に複数の公開実装で採用した **取得・検証・正本化・配布を別の状態として扱う fail-close 設計**を、最小実装と検証手順まで落として説明します。

## 1. 失敗は「APIが落ちた」だけではない

データ取得処理で最も分かりやすい失敗は、タイムアウトや5xxです。しかし運用上より厄介なのは、取得自体は成功しているのに、データとして採用してはいけないケースです。

例えば次の状態は、ネットワーク的には成功でもデータ品質としては失敗です。

- 必須列が欠けている
- 主キー候補が重複している
- 最新日付だと思ったレコードが実は古い
- sourceや会計basisを特定できない
- 欠損値を0で埋めると意味が変わる
- 取得元の利用条件上、外部配布してはいけない
- 検証後に正本が更新され、lineage hashが一致しなくなった

私が `KAFKA2306/semiconductor-earnings-model` で実装した Data Platform Standard v1 では、`data/earnings_ledger/` を正本に固定し、source不明・basis不明・矛盾・必須artifact欠落を fail-close で扱うようにしています。REST・CLI・MCPは同じ read-only `DataPlatformService` を共有し、adapter側で値を再計算しません。

実装証拠:
https://github.com/KAFKA2306/semiconductor-earnings-model/commit/8cf66c2196fda9da060768e67de0893a9584cb22

この設計で重要なのは、**「取得成功」と「採用成功」を別の状態にすること**です。

## 2. 状態を4段階に分ける

最小限、私は次の4段階を分けます。

```text
ACQUIRED
  ↓
VALIDATED
  ↓
CANONICAL
  ↓
PUBLISHABLE
```

### ACQUIRED

APIやファイルからpayloadを受信できた状態です。ここでは内容の正しさを保証しません。

### VALIDATED

schema、必須列、主キー、期間、鮮度、source、basisなど、対象ドメインの契約を満たした状態です。

### CANONICAL

検証済みデータが正本へ昇格し、再現可能なID・source hash・provenanceを持つ状態です。

### PUBLISHABLE

配布条件、鮮度、監査、権利境界まで通過した状態です。

この4段階を1つの `success=True` に潰すと、「取れたから公開する」という危険な短絡が起きます。

## 3. 検証はデータを書き出す前に落とす

`KAFKA2306/investor2` の J-Quants パイプラインでは、取得データを一時領域に置き、必須列・null・一意性を検証してから次へ進めています。外部配布は別フラグで既定 `false` にし、許可されていなければ検証済みでも配布しません。

実装証拠:
https://github.com/KAFKA2306/investor2/commit/0e87aaf3ff1b8f73db970765ff337c964f30c56f

J-Quantsの公式Python clientも公開されているため、API wrapperの実体は一次情報から追えます。

公式client:
https://github.com/J-Quants/jquants-api-client-python

検証関数は複雑である必要はありません。重要なのは「違反を見つけたら、その場で止める」ことです。

```python
def require_columns(df, required):
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")

    null_columns = [
        column for column in required
        if df[column].isna().any()
    ]
    if null_columns:
        raise ValueError(f"null in required columns: {sorted(null_columns)}")


def require_unique(df, key):
    if df.duplicated(key).any():
        raise ValueError(f"duplicate key: {key}")
```

ここで `drop_duplicates()` や `fillna(0)` を自動的に行わないのがポイントです。重複や欠損が「修復可能」かどうかは、データ取得層には判断できません。

## 4. nullを0に変えない

データ基盤では「値がない」と「値が0」は別の事実です。

例えば財務データで、

```json
{
  "operating_income": null,
  "null_reason": "source_not_disclosed"
}
```

と、

```json
{
  "operating_income": 0
}
```

は意味が違います。

前者は「開示から確認できない」、後者は「0という値が確認できた」です。ここを混ぜると、API、ダッシュボード、機械学習、LLMのすべてが誤った前提を共有します。

そのため正本側では、値だけでなく少なくとも次を保持します。

```text
canonical_id
source_url
source_hash
source_observed_at
freshness
null_reason
derivation_method
basis
provenance
```

Data Platform Standard v1では、このようなprovenance fieldを機械契約としてCIで検証しています。

https://github.com/KAFKA2306/semiconductor-earnings-model/commit/8cf66c2196fda9da060768e67de0893a9584cb22

## 5. REST・CLI・MCPごとに計算ロジックを持たせない

データ提供面が増えると、次のような分岐が起きがちです。

```text
REST → REST用の集計
CLI  → CLI用の集計
MCP  → MCP用の集計
```

これでは同じ会社・同じ期間を問い合わせても、adapterごとに値が変わる余地があります。

そこで、提供面は薄くします。

```text
                    ┌─ REST
canonical ledger → DataPlatformService ─ CLI
                    └─ MCP
```

MCPについても、公開実装ではread-only projectionだけを呼び、MCP側で財務値やfreshnessを再計算しないようにしました。公式Python SDKの実装・仕様は次のrepositoryから確認できます。

https://github.com/modelcontextprotocol/python-sdk

重要なのは「MCPを使うこと」ではなく、**MCPも他のadapterと同じ正本に従属させること**です。

## 6. 配布は検証とは別ゲートにする

検証を通ったデータでも、外部へ出してよいとは限りません。

J-Quantsのパイプラインでは、取得・validationの後に配布可否を別条件として評価し、明示的に許可されない限り外部配布しないようにしました。また、一時データはGitHubへcommitせず、runner上のstaging directoryを最後に削除します。

```yaml
env:
  EXTERNAL_DISTRIBUTION_ALLOWED: "false"

steps:
  - name: Fetch and validate
    run: python pipeline.py --output-dir .staging

  - name: Publish
    if: env.EXTERNAL_DISTRIBUTION_ALLOWED == 'true'
    run: ./publish.sh .staging

  - name: Cleanup
    if: always()
    run: rm -rf .staging
```

外部サービスへの認証には、可能なら長期tokenを保存するよりOIDCのような短命credentialを使う方が境界を狭くできます。GitHub ActionsのOIDCでは、workflowに `id-token: write` を与えてJWTを取得し、外部サービス側で短命access tokenへ交換する構成が公式に説明されています。

https://docs.github.com/en/actions/reference/security/oidc

## 7. 「取得成功」と「公開可能」を別KPIにする

運用メトリクスも分けます。

悪い例:

```text
pipeline_success_rate = 99.9%
```

これだけでは、何が成功したのか分かりません。

私は少なくとも次のように分ける方がよいと考えています。

```text
acquisition_success_total
eligible_events_total
rejected_events_total
stale_events_skipped_total
verified_metrics_total
publishable_snapshot_total
```

例えば `acquisition_success_total` が増えている一方、`eligible_events_total == 0` なら、「取得系は正常だが採用できる新規データがない」と読めます。

これを単一のsuccessへまとめると、収集器の正常性とデータの有効性を切り分けられません。

## 8. 最小のfail-close実装

Pythonなら、状態を明示したresult objectにすると扱いやすくなります。

```python
from dataclasses import dataclass
from typing import Literal

State = Literal[
    "acquired",
    "validated",
    "canonical",
    "publishable",
    "rejected",
]

@dataclass(frozen=True)
class PipelineResult:
    state: State
    reason: str | None
    source_hash: str | None


def promote(record) -> PipelineResult:
    if not record.source_url:
        return PipelineResult(
            state="rejected",
            reason="missing_source",
            source_hash=None,
        )

    if record.is_stale:
        return PipelineResult(
            state="rejected",
            reason="stale",
            source_hash=record.source_hash,
        )

    if not record.validation_passed:
        return PipelineResult(
            state="rejected",
            reason="validation_failed",
            source_hash=record.source_hash,
        )

    return PipelineResult(
        state="canonical",
        reason=None,
        source_hash=record.source_hash,
    )
```

例外で落とすべき契約違反と、`rejected` として監査記録に残すべき不採用を分けると、再実行時の判断がしやすくなります。

## 9. CIで検証する項目

実装後は、少なくとも次をCIへ入れます。

- 必須provenance fieldが欠けたら失敗
- source hashと正本artifactのhashが一致しなければ失敗
- nullを0/falseへ暗黙変換していない
- 同一入力から同一projectionを再生成できる
- REST / CLI / MCPが同じdomain serviceを読む
- staleなデータがpublishableへ昇格しない
- 配布許可がfalseならpublish stepが走らない
- 一時データが成功・失敗にかかわらず削除される

ローカルでも、正本serviceとadapter parityを直接テストします。

```bash
python -m pytest tests/test_data_platform_standard.py -q
```

実際の公開実装では、この種のdeterministic service testとMCP contract testをCIへ組み込んでいます。

https://github.com/KAFKA2306/semiconductor-earnings-model/commit/8cf66c2196fda9da060768e67de0893a9584cb22

## 10. 導入チェックリスト

既存パイプラインをfail-closeへ寄せるなら、次の順番が小さく始めやすいです。

1. `取得成功` と `採用成功` のフラグを分ける
2. rejected recordを捨てず、reason付きで別保存する
3. `null != 0` をschema contractにする
4. source URL/hash/観測時刻を正本recordへ持たせる
5. canonical serviceを1つ作り、REST/CLI/MCPを薄いadapterにする
6. freshness gateを公開直前に置く
7. distribution permissionをvalidationとは別にする
8. staging dataを永続化しない
9. parityとdeterministic replayをCIへ追加する
10. 「何件取れたか」ではなく「何件採用・棄却・公開可能だったか」を監視する

## 適用範囲と限界

この設計は、金融データ、企業開示、製造データ、外部SaaS APIのように「取れたこと」と「使ってよいこと」が一致しないパイプラインに向いています。

一方、fail-closeを厳しくしすぎると、source側の軽微なschema変更でも全停止します。そのため、停止条件を減らすのではなく、**rejected理由・source state・監査結果を観測可能にすること**が必要です。

また、この記事で示したfieldや状態名は万能な標準ではありません。ドメインごとに、何を「採用可能」とするかの契約は変わります。固定すべきなのは名前ではなく、取得・検証・正本・配布を一つの成功判定に潰さないという境界です。

## 次に検証すべきこと

次の課題は、fail-closeで止まった理由を人間向けの監査画面とAgent/MCPの両方から同じ意味で取得できるようにすることです。その際も、adapterが理由を再解釈せず、canonical serviceが返す `reason` とprovenanceをそのまま利用する設計を維持します。

## 一次情報・再現証拠

- https://github.com/KAFKA2306/semiconductor-earnings-model/commit/8cf66c2196fda9da060768e67de0893a9584cb22
- https://github.com/KAFKA2306/investor2/commit/0e87aaf3ff1b8f73db970765ff337c964f30c56f
- https://github.com/J-Quants/jquants-api-client-python
- https://github.com/modelcontextprotocol/python-sdk
- https://docs.github.com/en/actions/reference/security/oidc
