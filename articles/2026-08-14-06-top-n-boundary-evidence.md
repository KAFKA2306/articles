---
title: "上位N件だけで選定を正当化するな。N+1件目を残せ"
emoji: "📏"
type: "tech"
topics: ["python", "dataengineering", "testing", "api"]
published: false
---

「上位50社」が50件返ってきた。それだけでは**なぜその50社が選ばれたか**を説明できない。途中でデータ取得が打ち切られても、50件の一覧は見栄えよく完成する。

[2026年8月14日の半導体企業の抽出](https://github.com/KAFKA2306/semiconductor-earnings-model/commit/45ccb7dad68c46a3e488b122205b6af2bf27f5e6)では、候補51社から50社を採り、最初に外れたQDレーザ（E35542、売上1,372,801,000円）を`first_excluded_by_limit`へ保存した。[固定snapshot](https://github.com/KAFKA2306/semiconductor-earnings-model/blob/45ccb7dad68c46a3e488b122205b6af2bf27f5e6/data/financial_analysis/sandisk-investor-day-2026-edinet-semiconductor-50.json)と[報告](https://github.com/KAFKA2306/semiconductor-earnings-model/blob/45ccb7dad68c46a3e488b122205b6af2bf27f5e6/docs/reports/semiconductor/2026-08-14-sandisk-investor-day-edinet50.md)に残る。

汎用規律は **「上位N件の採否を語るなら、N+1件目と取得範囲を残せ」**。選抜の正当性は選ばれた対象だけからは検証できない。

## 50件返ってきた、は完全性の証拠にならない

典型的なTop-Nは簡単に書ける。

```python
rows = fetch_rows()
rows = sorted(rows, key=lambda row: row["revenue"], reverse=True)
top50 = rows[:50]
write_json(top50)
```

この出力には50件並ぶ。

しかし翌月そのJSONだけを見ても、候補集合の外側は消えている。

```text
Top 50
├─ 1位
├─ ...
└─ 50位

51位以下: 不明
```

さらに上流がAPIなら、別の境界もある。

GitHub REST APIの現行公式ドキュメントでも、結果が多い場合はresponseがpaginationされ、1回のresponseには全件ではなくsubsetが返る。`per_page` は1ページの件数を変えるもので、候補集合全体を保証するものではない。

- https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api

つまり、少なくとも次の2つを分けないといけない。

```text
upstream retrieval boundary
  APIから候補を最後まで取得できたか

ranking boundary
  完全な候補集合から何件を採用したか
```

この2つを同じ `limit=50` で表現すると、**「上位50社」なのか「最初に取れた50社」なのかが分からなくなる。**

## 私が残したのは、ランキングの外側にある最小証拠だった

全部の候補を保存するのが最も強い場合もある。

ただし、候補集合が大きければstorage、license、privacy、取得コストまで増える。

Top-Nの説明責任だけが目的なら、少なくとも次を残すとかなり違う。

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

これで翌日51位だった企業が50位へ上がっても、

> 突然現れた

ではなく、

> 前日から境界直下にいて、順位が入れ替わった

と説明できる。

**採用されたレコードだけでなく、最初に採用されなかったレコードも証拠にする。**

これが今回の設計判断だった。

## Top-Nを「一覧」ではなく「判断可能なsnapshot」にする

ランキングを業務で使うなら、私は最低でも次をセットで残したい。

| Evidence | 何が分かるか |
|---|---|
| `candidate_count` | 候補集合がNを超えていたか |
| `record_count` | 実際に何件採用したか |
| sort key | 何を基準に順位を付けたか |
| tie-breaker | 同値の並びがなぜその順か |
| first excluded record | 境界直下に何がいたか |
| source / retrieved_at | どのデータをいつ見たか |
| filter conditions | 何を候補から除外したか |

金融screeningなら、これだけで「上位50」の意味がかなり具体的になる。

検索、推薦、feature selection、異常検知、審査、優先キューでも構造は同じだ。

## 実装は小さい

候補集合を完全に取得できた後なら、境界保存自体は小さく書ける。

```python
def top_n_with_boundary(rows, *, n, key):
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

重要なのはこの関数より処理順である。

```text
全ページを取得
  ↓
対象filterを適用
  ↓
candidate_countを確定
  ↓
安定したsort / tie-breaker
  ↓
Top-Nを採用
  ↓
N+1件目を保存
```

上流取得を完走する前にTop-Nを作ると、N+1件目を保存しても「全体のN+1位」にはならない。

## どこまで自動化できるか

この設計をranking pipelineへ入れると、次の監査を機械化できる。

- `record_count <= candidate_count` か
- `record_count == min(limit, candidate_count)` か
- `candidate_count > limit` のとき boundary record が存在するか
- `candidate_count <= limit` のとき boundary が `null` か
- boundaryのsort keyが採用最下位を超えていないか
- 前回snapshotから境界付近がどう動いたか
- sourceと取得時刻が欠けていないか

手元で試すなら、全件取得したデータと、順位を決める列を用意し、候補が50件の例と51件の例を一度ずつ集計する。どちらも採用は50件。候補が50件なら境界直下の記録は `null`、51件なら51位が1件入ることを確かめる。

つまり人が毎回「このランキング、本当に50位まで正しい？」と手で確認するのではなく、**ランキング自身に説明責任を持たせられる。**

## これは金融だけの話ではない

同じ問題は、Top-Nを意思決定へ渡すところなら起きる。

```text
検索結果の上位20件
推薦候補の上位10件
異常検知score上位100件
feature importance上位30個
採用候補の上位50人
営業優先リスト上位100社
```

一覧だけ渡せば「採用されたもの」は見える。

境界証拠まで渡せば、**採用されなかったものとの距離**も見える。

この差は、ランキングが単なる表示なのか、後から説明できる意思決定材料なのかの違いになる。

## 50位と51位が同額なら、別の並び順が必要

[2026年8月14日のsnapshot](https://github.com/KAFKA2306/semiconductor-earnings-model/blob/45ccb7dad68c46a3e488b122205b6af2bf27f5e6/data/financial_analysis/sandisk-investor-day-2026-edinet-semiconductor-50.json)は候補51社、採用50社で、上限外となったQDレーザ（E35542）の売上1,372,801,000円まで残した。

ただし、**仮に50位と51位の売上が同額**だったら、売上降順だけでは入れ替わりを説明できない。この同額は反例であり実際の50位の値ではない。運用するときは次を残す。

```text
input:   取得した候補全件、決算期、通貨と単位
sort:    売上の降順。同額は企業コード昇順（規則の例）
output:  1〜50位、51位、候補件数、取得時点
reject:  取得途中の失敗、決算期の混在、同点処理が未定
```

企業コード昇順は**再現性のための設計案**で、元コードの既存仕様を示すものではない。さらに、候補取得がAPIの最初の51件で打ち切られていたら、51位を記録しても全体の完全性は証明できない。

## 境界

N+1件目を保存すればランキング全体が正しい、とまでは言えない。

次は別途必要になる。

- 上流データの完全取得
- sourceそのものの妥当性
- 欠損値の扱い
- sort keyの意味妥当性
- tie-breakerの固定
- 同じ条件で再計算できるsnapshot

今回の実装が保証するのは、**Top-Nで切った瞬間に境界情報を自分で捨てないこと**である。

## まとめ

2026年8月14日の半導体screeningでは、候補51社に対して上位50社を採用した。

普通なら50社を保存して終わるところを、51位のQDレーザまでsnapshotへ残した。

その結果、成果物は単なる「50社一覧」ではなく、

```text
なぜ50件なのか
その外側に何がいたのか
翌回の入れ替わりをどう説明するか
```

まで追える形になった。

私が再利用したいのはN+1件目という小技ではない。

**ランキング・screening・推薦を、利用者が後から疑っても検証できる成果物にすること。**

データを集めて並べるだけでなく、その判断境界まで証拠として設計する。


## この規律の適用・撤回条件

採用候補、推薦商品、補助金の選抜でも境界近くの採否理由を求められるなら、最初の除外対象と同点処理を保存する判断を試せる。ただし、これらは**応用仮説**であって、この金融snapshot以外で実証したわけではない。

候補が最初からN件以下で、全件取得が別の方法で保証されるならN+1件目は存在せず、必要なのは取得完了の証拠になる。逆にN+1件目があってもAPIが51件で打ち切られていたら網羅性は証明できない。**境界一件を完全性の代わりにしない。**
