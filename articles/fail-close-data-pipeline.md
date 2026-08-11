---
title: "「取得できた」を成功条件にしない：fail-closeなデータパイプライン設計"
emoji: "🧭"
type: "tech"
topics: ["python", "github", "dataengineering", "mcp"]
published: true
published_at: 2026-08-11 19:48
---

外部APIからデータを集める処理では、HTTP 200やCSV生成をそのまま「成功」と扱うと、取得できたデータと採用してよいデータを混同します。実装上は、**取得・検証・正本化・配布を別の状態として扱う**方が安全です。

この記事では、公開済みの2つの実装を根拠に、fail-closeなデータパイプラインをどう分解したかを整理します。

## 取得成功と採用成功を分ける

最低限、状態を次のように分けます。

```text
ACQUIRED
  ↓
VALIDATED
  ↓
CANONICAL
  ↓
PUBLISHABLE
```

- `ACQUIRED`: APIやファイルからpayloadを受信できた
- `VALIDATED`: schema、必須項目、一意性、freshnessなどの契約を通過した
- `CANONICAL`: 正本へ昇格し、source URL/hashやprovenanceを持つ
- `PUBLISHABLE`: 配布条件や監査条件まで通過した

この区別を入れる理由は単純です。ネットワーク上の成功と、データ品質上の成功は同じではありません。

## 実装1: 正本serviceを1つに固定する

`KAFKA2306/semiconductor-earnings-model` の Data Platform Standard v1 では、`data/earnings_ledger/` を正本とし、REST・CLI・MCPが同じread-only `DataPlatformService` を利用する構成を実装しました。commitには、adapter側で財務値・freshness・quality statusを再計算しないこと、provenance、null semantics、deterministic replay、fail-close quality gateを導入したことが記録されています。

実装証拠:
https://github.com/KAFKA2306/semiconductor-earnings-model/commit/8cf66c2196fda9da060768e67de0893a9584cb22

提供面ごとに計算ロジックを持たせると、同じ入力でもREST・CLI・MCPで値がずれる余地が生まれます。そこで境界を次のようにします。

```text
                    ┌─ REST
canonical ledger → DataPlatformService ─ CLI
                    └─ MCP
```

重要なのはMCPそのものではなく、**MCPも他のadapterと同じ正本に従属させる**ことです。

Model Context ProtocolのPython SDKは公開リポジトリで確認できます。

https://github.com/modelcontextprotocol/python-sdk

## nullを0に変えない

データ基盤では「値がない」と「値が0」は別の事実です。

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

は意味が異なります。

そのため、正本側では値だけでなく、例えば次のようなlineage情報を保持します。

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

前述のData Platform Standard v1のcommitでも、主要recordへsource URL/hash、freshness、null reason、derivation、basis、provenanceを持たせ、欠損を0/falseへ補完しない方針が明示されています。

## 実装2: 検証と外部配布を別ゲートにする

`KAFKA2306/investor2` では、J-Quants取得データをrunner上の一時領域へ置き、検証と外部配布を分離するworkflowを追加しました。

実装証拠:
https://github.com/KAFKA2306/investor2/commit/0e87aaf3ff1b8f73db970765ff337c964f30c56f

このcommitには、外部配布フラグが明示的に許可された場合だけpublish stepへ進み、そうでなければ検証済みでも配布しない境界が含まれています。また、staging dataは成功・失敗にかかわらず削除するstepを持っています。

J-Quants側のPython clientは、J-Quants Organizationの公開repositoryで確認できます。

https://github.com/J-Quants/jquants-api-client-python

## credentialも配布境界に含める

外部サービスへ配布するworkflowでは、長期tokenを固定保存する方法だけでなくOIDCを使う設計も取れます。

GitHub公式ドキュメントでは、ActionsでOIDC tokenを要求するには `id-token: write` が必要で、この権限自体は外部resourceへのwrite権限を与えるものではなく、OIDC tokenの取得を許可するものだと説明されています。

https://docs.github.com/en/actions/reference/security/oidc

`investor2` の対象commitでも、publish jobに `id-token: write` を付与し、外部配布許可とcredential取得を分けています。

## 最小のfail-close実装

Pythonなら状態を明示したresult objectにすると、取得成功と採用成功を潰さずに扱えます。

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
        return PipelineResult("rejected", "missing_source", None)

    if record.is_stale:
        return PipelineResult("rejected", "stale", record.source_hash)

    if not record.validation_passed:
        return PipelineResult(
            "rejected",
            "validation_failed",
            record.source_hash,
        )

    return PipelineResult("canonical", None, record.source_hash)
```

ここで、欠損や重複を取得層が勝手に `fillna(0)` や `drop_duplicates()` で修復しないことが重要です。修復できるかどうかはドメイン契約側で判断し、判断できなければ止めます。

## CIで見る項目

実装後は、少なくとも次をCIで確認します。

- 必須provenance fieldが欠けたら失敗する
- source hashと正本artifactのhashが一致しなければ失敗する
- nullを0/falseへ暗黙変換しない
- 同一入力から同一projectionを再生成できる
- REST / CLI / MCPが同じdomain serviceを読む
- staleなデータがpublishableへ昇格しない
- 配布許可がfalseならpublish stepが走らない
- 一時データが成功・失敗にかかわらず削除される

## 運用KPIも分ける

単一の `pipeline_success_rate` だけでは、何が成功したのか分かりません。

例えば次のように分けます。

```text
acquisition_success_total
eligible_events_total
rejected_events_total
stale_events_skipped_total
verified_metrics_total
publishable_snapshot_total
```

`acquisition_success_total` が増えていても `eligible_events_total == 0` なら、「取得系は正常だが採用できる新規データがない」と読めます。

## まとめ

fail-closeなデータパイプラインで固定したいのは、個々のfield名ではありません。

**取得できたこと、検証を通ったこと、正本へ昇格できたこと、外部へ配布してよいことを、それぞれ別の状態として扱うこと**です。

この境界を持たせると、外部APIのschema変更や欠損、stale data、配布条件の未設定があった場合に、根拠の弱いデータを静かに下流へ流すより先に止められます。

## 一次情報・再現証拠

- https://github.com/KAFKA2306/semiconductor-earnings-model/commit/8cf66c2196fda9da060768e67de0893a9584cb22
- https://github.com/KAFKA2306/investor2/commit/0e87aaf3ff1b8f73db970765ff337c964f30c56f
- https://github.com/J-Quants/jquants-api-client-python
- https://github.com/modelcontextprotocol/python-sdk
- https://docs.github.com/en/actions/reference/security/oidc
