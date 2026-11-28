---
title: "選ばれた一覧からは、選定の正しさを証明できない"
emoji: "📏"
type: "tech"
topics: ["python", "dataengineering", "testing", "api"]
published: false
created_at: "2026-08-14"
updated_at: "2026-11-28"
---

検索結果、営業候補、投資対象の上位50件を受け取ったとする。50件が順番に並んでいれば、選定は成功したように見える。ところが取得処理が途中で止まっていても、同じ形式の一覧は作れる。

選ばれた一覧から分かるのは、何が選ばれたかである。何と比較して選ばれたかは分からない。ランキングを意思決定に使うなら、**取得の境界と選抜の境界を分けて記録する**必要がある。

## 一覧が完成していても、候補集合は完成していない

典型的な実装は次のようになる。

2026年8月14日の実例では、候補51社から50社を選んだ。上限で外れたQDレーザの企業コードと売上を出力へ残し、取得件数と採用件数を分けている。

GitHub REST APIなどでは、検索結果は複数ページに分割される。[公式のページネーション仕様](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api)が示すように、一回の応答は全体の一部分であり得る。最初のページだけを取得しても、50件以上あれば上のコードは50件を返す。

取得件数と採用件数は別の数である。完全に取得した候補へ条件を適用し、その集合を並べ替えてから採用件数を制限する。この順序が逆なら「上位50件」は「たまたま取得できた範囲の上位50件」になる。

## 最初に落ちた一件を保存する

[2026年8月14日の半導体企業の抽出](https://github.com/KAFKA2306/semiconductor-earnings-model/commit/45ccb7dad68c46a3e488b122205b6af2bf27f5e6)では、候補51社から50社を選んだ。[固定された出力](https://github.com/KAFKA2306/semiconductor-earnings-model/blob/45ccb7dad68c46a3e488b122205b6af2bf27f5e6/data/financial_analysis/sandisk-investor-day-2026-edinet-semiconductor-50.json)には、採用外となった企業も一件残っている。

```json
{
  "candidate_count": 51,
  "record_count": 50,
  "first_excluded_by_limit": {
    "name": "株式会社ＱＤレーザ",
    "edinet_code": "E35542",
    "revenue": 1372801000.0,
    "currency": "JPY"
  }
}
```

この記録があれば、翌回にQDレーザが採用されたとき、前回から境界直下にいたことを説明できる。[当時の報告](https://github.com/KAFKA2306/semiconductor-earnings-model/blob/45ccb7dad68c46a3e488b122205b6af2bf27f5e6/docs/reports/semiconductor/2026-08-14-sandisk-investor-day-edinet50.md)とともに比較の根拠を追える。

全候補を保存できるなら、それがより強い再現材料になる。保存費用やライセンス、個人情報の制約がある場合は、必要な範囲で境界情報を残す。ただし一件の除外記録は全候補の正当性を証明しない。取得完了と順位の妥当性には、それぞれ独立した根拠が要る。

## 同点で壊れる順位を、先に直す

仮に50位と51位の売上が等しかったら、売上降順だけでは採否を再現できない。これは実際の50位の売上を示したものではなく、順位規則の欠陥を考える反例だ。

企業コード昇順など、同点を処理する規則を事前に決める。次は取得済みの企業一覧に適用する最小実装例である。企業コードは一意、売上は同じ単位と期間の数値であることを前提とする。

```python
def select(rows, n):
    if n < 1:
        raise ValueError("n must be positive")
    ranked = sorted(rows, key=lambda r: (-r["revenue"], r["code"]))
    return {
        "candidate_count": len(ranked),
        "record_count": min(n, len(ranked)),
        "records": ranked[:n],
        "first_excluded_by_limit": ranked[n] if len(ranked) > n else None,
    }

rows = [
    {"code": "B", "revenue": 100},
    {"code": "A", "revenue": 100},
    {"code": "C", "revenue": 90},
]
print(select(rows, 1))
```

この入力ではAが採用され、Bが最初の除外対象になる。入力順を逆転させても結果は同じになる設計だ。実際の取得処理と結合するときは、次の情報も出力に添える。

| 記録 | 判断できること |
| --- | --- |
| 取得元・時点・完了状態 | 候補集合がどこまで含まれるか |
| 対象条件・欠損処理 | 誰が順位付けの対象になるか |
| 候補数・採用数・上限 | 件数制限による除外の有無 |
| 順位基準・同点規則 | 同じ入力で採否を再現できるか |
| 最初の除外対象 | 採否の境目に誰がいたか |

取得途中の失敗を空配列や正常完了に置き換えてはならない。境界が存在しない場合のnullと、取得失敗で境界が分からない状態は異なる。

推薦や優先キューにも同じ設計を移せるが、上の企業抽出以外で効果を測ったわけではない。また、順位基準そのものが目的に適切かどうかは別の判断である。全件取得済みで候補数が上限以下なら、除外対象は存在しない。そこで架空のN+1件目を作る必要はない。

次に上位一覧を受け取ったら、最下位の採用対象と最初の除外対象を並べ、両者を分けた規則と候補の取得範囲を確認する。順位表の見た目ではなく、採否を説明できる情報を要求する。
