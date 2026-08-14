---
title: "50件だけ保存すると、51件目が消える。Top-Nの境界を残す"
emoji: "📏"
type: "tech"
topics: ["python", "dataengineering", "testing", "api"]
published: false
---

「売上上位50社」のような一覧を作るとき、上位50件だけ保存して終わっていないだろうか。

それだと、翌日の結果が1社だけ入れ替わったときに、**本当に順位が動いたのか、取得件数の上限やページネーションで候補を落としたのか**を後から区別しにくい。

今回 `KAFKA2306/semiconductor-earnings-model` で半導体企業を売上降順に抽出した公開データでは、`limit: 50` に対して候補は51社だった。そこで上位50社だけでなく、最初に上限外となった51位の企業も `first_excluded_by_limit` として保存した。

- `candidate_count`: 51
- `record_count`: 50
- `first_excluded_by_limit`: QDレーザ（EDINET code `E35542`）
- 51位の売上: 1,372,801,000 JPY

一次証拠:

- https://github.com/KAFKA2306/semiconductor-earnings-model/commit/45ccb7dad68c46a3e488b122205b6af2bf27f5e6
- https://github.com/KAFKA2306/semiconductor-earnings-model/blob/45ccb7dad68c46a3e488b122205b6af2bf27f5e6/data/financial_analysis/sandisk-investor-day-2026-edinet-semiconductor-50.json
- https://github.com/KAFKA2306/semiconductor-earnings-model/blob/45ccb7dad68c46a3e488b122205b6af2bf27f5e6/docs/reports/semiconductor/2026-08-14-sandisk-investor-day-edinet50.md
- https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api
- https://docs.python.org/3/library/heapq.html

この記事で扱うのは金融データそのものではない。**Top-Nを生成するデータパイプラインで、採用されたN件だけでなく「境界」を証拠として残す設計**である。

## 1. 問題: Top 50だけでは「なぜ50件なのか」が消える

典型的な実装は単純だ。

```python
rows = fetch_rows()
rows = sorted(rows, key=lambda row: row["revenue"], reverse=True)
top50 = rows[:50]
write_json(top50)
```

出力を見る限り、50件のランキングとしては正しい。

しかし、このJSONだけを翌月に見ても次は分からない。

- 候補は50社しかなかったのか
- 51社以上あったが上限で切ったのか
- APIの1ページ目しか取得できなかったのか
- filter条件で51位以下を除いたのか
- 50位と51位の差は大きかったのか小さかったのか

特に「50件返った」は危険な観測だ。GitHub REST APIの公式ドキュメントでも、大量の結果はページ分割され、1回のレスポンスは全件ではなく一部だけになる。`per_page` は1ページで返す件数を変えるだけで、候補集合全体の件数を意味しない。

つまり、**取得上限とランキング上限は別の境界**である。

## 2. 原因: 配列のsliceが境界情報を捨てる

Pythonの `heapq.nlargest(n, iterable)` は、公式ドキュメント上 `sorted(iterable, key=key, reverse=True)[:n]` と同等の結果を返す。

これはTop-N計算として正しい。一方で `[:n]` の結果だけを永続化すると、`n` の直後に何があったかは消える。

壊れた例を小さくすると分かりやすい。

```python
rows = [
    {"name": "A", "score": 100},
    {"name": "B", "score": 90},
    {"name": "C", "score": 89},
]

result = sorted(rows, key=lambda x: x["score"], reverse=True)[:2]
```

保存されるのは次だけだ。

```json
[
  {"name": "A", "score": 100},
  {"name": "B", "score": 90}
]
```

ここからは、Cが89点で境界のすぐ下にいたことを復元できない。

翌日Bが88点になりCが89点のままなら、Top 2はA/Cへ入れ替わる。しかし前日の出力しかなければ、「Cが突然現れた」ように見える。

## 3. 設計判断: N件ではなくN+1件目まで観測する

今回採った形は、Top-N本体とは別に次の3種類を保存することだった。

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

この形の利点は、ランキング本体を肥大化させずに境界だけ監査できることだ。

### 代替案A: 全候補を保存する

最も強い。完全な再計算ができる。

ただし候補集合が数百万件なら、スナップショットの容量や個人情報・ライセンス・取得コストまで抱える。Top-Nの監査だけが目的なら過剰な場合がある。

### 代替案B: candidate_countだけ保存する

「候補がN件を超えていた」は分かる。

しかし50位と51位の距離が分からない。境界付近の入れ替わりを説明する証拠としては弱い。

### 代替案C: cutoff値だけ保存する

`50位のscore = 90` のような閾値を残す方法もある。

これも有用だが、同点やtie-breakerがあると「誰が落ちたか」を説明できない。そこで、少なくとも最初の除外レコードの安定IDとsort keyを残す方が診断しやすい。

## 4. 実装: 境界をデータ構造にする

最小実装は次のように書ける。

```python
from collections.abc import Callable, Iterable
from typing import Any


def top_n_with_boundary(
    rows: Iterable[dict[str, Any]],
    *,
    n: int,
    key: Callable[[dict[str, Any]], Any],
) -> dict[str, Any]:
    if n < 1:
        raise ValueError("n must be >= 1")

    ranked = sorted(rows, key=key, reverse=True)

    return {
        "candidate_count": len(ranked),
        "record_count": min(n, len(ranked)),
        "records": ranked[:n],
        "first_excluded_by_limit": ranked[n] if len(ranked) > n else None,
    }
```

利用例:

```python
rows = [
    {"id": "A", "score": 100},
    {"id": "B", "score": 90},
    {"id": "C", "score": 89},
]

snapshot = top_n_with_boundary(
    rows,
    n=2,
    key=lambda row: row["score"],
)
```

改善後の出力はこうなる。

```json
{
  "candidate_count": 3,
  "record_count": 2,
  "records": [
    {"id": "A", "score": 100},
    {"id": "B", "score": 90}
  ],
  "first_excluded_by_limit": {"id": "C", "score": 89}
}
```

これなら翌日CがBを抜いたとき、前日から境界直下にいたことを機械的に説明できる。

## 5. ただし、N+1件目を保存するだけでは不十分

この設計には重要な前提がある。

**ランキング対象の候補集合を最後まで取得できていること**だ。

例えばAPIが30件ずつページネーションするのに1ページ目だけ取得し、その30件からTop 20を作った場合、21位を保存しても全体の21位とは限らない。

GitHub REST APIの公式ドキュメントは、ページ分割されたレスポンスでは `link` ヘッダーから追加ページを取得する方法を示している。したがって一般化すると、処理順は次になる。

1. 上流APIのページネーションを完走する
2. filter条件を適用する
3. `candidate_count` を確定する
4. sort keyとtie-breakerで順序を確定する
5. Top-Nを採用する
6. N+1件目を `first_excluded_by_limit` として保存する

ここを逆にすると、「ページ上限」と「ランキング上限」を混同する。

## 6. 検証: 4ケースだけでも壊れ方をかなり防げる

読者がそのまま試せる `unittest` は次の形になる。

```python
import unittest


class TopNBoundaryTest(unittest.TestCase):
    def test_records_first_excluded_item(self):
        rows = [
            {"id": "A", "score": 100},
            {"id": "B", "score": 90},
            {"id": "C", "score": 89},
        ]
        result = top_n_with_boundary(rows, n=2, key=lambda x: x["score"])
        self.assertEqual(result["candidate_count"], 3)
        self.assertEqual(result["record_count"], 2)
        self.assertEqual(result["first_excluded_by_limit"]["id"], "C")

    def test_boundary_is_null_when_not_truncated(self):
        rows = [{"id": "A", "score": 1}]
        result = top_n_with_boundary(rows, n=2, key=lambda x: x["score"])
        self.assertIsNone(result["first_excluded_by_limit"])

    def test_rejects_zero_limit(self):
        with self.assertRaises(ValueError):
            top_n_with_boundary([], n=0, key=lambda x: x["score"])

    def test_boundary_moves_when_rank_changes(self):
        before = [
            {"id": "A", "score": 100},
            {"id": "B", "score": 90},
            {"id": "C", "score": 89},
        ]
        after = [
            {"id": "A", "score": 100},
            {"id": "B", "score": 88},
            {"id": "C", "score": 89},
        ]
        b = top_n_with_boundary(before, n=2, key=lambda x: x["score"])
        a = top_n_with_boundary(after, n=2, key=lambda x: x["score"])
        self.assertEqual(b["first_excluded_by_limit"]["id"], "C")
        self.assertEqual(a["first_excluded_by_limit"]["id"], "B")
```

本番ではさらに、同点時のtie-breakerを固定する。例えば `(-revenue, edinet_code)` のように安定IDを第2キーへ入れれば、同値の並びが実行ごとに揺れる問題を避けやすい。

## 7. 実データで何が分かったか

公開スナップショットでは、条件は次のように記録されている。

- business tag: `semiconductor`
- `revenue > 0`
- delistedを除外
- revenue降順
- limit 50

その結果、2026-08-14の候補は51社、採用は50社、最初の上限外はQDレーザだった。

重要なのはQDレーザという企業名ではない。**「50社」という出力に対して、51社目が存在したことを出力自身が説明できる**点である。

さらに同じスナップショットでは欠損値を0へ変換せず `null` のまま保持している。これは境界証拠と同じ思想で、表示を簡単にするために観測事実を潰さない設計になっている。

## 8. 失敗と学び

最初にTop-Nを実装するとき、`sorted(... )[:n]` はあまりに自然なので、その直後の要素を保存する発想は抜けやすい。

しかし、ランキングの運用で問題になるのは上位1位より、しばしば**採用・不採用が切り替わる境界**である。

- feature selectionの上位K個
- 検索結果の上位N件
- 推薦候補の上位N件
- 異常検知スコア上位N件
- バッチ処理の優先キュー
- 採用候補や審査対象の上限

どれも同じ構造を持つ。

ここでの学びは、「全部保存しよう」ではない。

**Top-Nを公開・永続化するなら、少なくとも候補総数と最初の除外対象を同じsnapshotへ束ねる。**

これだけで、後から境界の変化を説明できる範囲が大きく増える。

## 9. 再現方法

自分のパイプラインへ導入するときは、次の順で十分だ。

1. 現在 `rows[:n]` や `LIMIT n` を使っている箇所を探す
2. その直前の候補集合が完全取得済みか確認する
3. `candidate_count` を保存する
4. 採用件数を `record_count` として保存する
5. `n+1` 件目の安定IDとsort keyを保存する
6. 候補数が `n` 以下なら境界を `null` にする
7. 翌runで境界対象が入れ替わるテストを1本追加する

SQLなら、上位N件を返すクエリとは別にN+1件目を取得してもよいし、window functionでrankを付けて `rank <= n + 1` まで取得してから分けてもよい。

## まとめ

Top-Nは、N件のリストではなく**境界を持つ選択結果**として保存した方が監査しやすい。

上位50件だけを保存すると、51件目は消える。候補総数と最初の除外対象を残しておけば、「なぜこの50件なのか」を後からデータ自身で説明できる。

ただし、その前提として上流のページネーションを完走し、候補集合そのものが完全であることを先に確認する。

一文で持ち帰るなら、**Top-Nを保存するときはN+1件目も証拠として残す**、である。
