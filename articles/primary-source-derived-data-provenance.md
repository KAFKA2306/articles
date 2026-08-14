---
title: "856件が7,699件になっても、分析の信頼を失わないために残したもの"
emoji: "🔎"
type: "tech"
topics: ["dataengineering", "provenance", "python", "github"]
published: false
published_at: 2026-08-12 11:21
---

最初の集計は **856行** だった。

同じテーマを後から取り直すと、今度は **7,699行**。内訳は **5,026 purchases + 2,673 sales** だった。

数字だけ見れば、かなり危ない。

「前の集計が間違っていたのでは？」

「どちらを信じればいい？」

「また数字が変わるのでは？」

分析を使う側から見れば、こう感じて当然だと思う。

しかし調べると、856と7,699は同じ母集団を数えた結果ではなかった。

856は部分集合、7,699は対象文書集合を広げた派生集計だった。しかも7,699も、U.S. Office of Government Ethics（OGE）が公表した単一の「公式合計」ではない。

壊れていたのは足し算ではない。

**数字だけを保存し、「その数字が何を代表しているか」を十分に残していなかったこと**だった。

そこで、公開データ分析の成果物を次のように分けることにした。

```text
一次資料
  ↓
観測できた値
  ↓
派生集計
  ↓
外部実装とのcross-check
  ↓
公開してよい値
```

この分離を入れると、数字が更新されても「前が間違いだった」の一言で終わらない。

**何が変わったのかを説明できる。**

この記事で扱うのは、provenanceという用語そのものではない。

**数字が変わっても、利用者が分析を信頼し続けられる状態をどう作るか**である。

- 実装commit: https://github.com/KAFKA2306/investor2/commit/c8a3ab271b58396c2aa3b38d9ba7a8f4244a3210
- 正準snapshot: https://github.com/KAFKA2306/investor2/blob/main/docs/research/data/us_oge_trump_278t_trade_count_2026-08-11.json

## 856と7,699は、同じ「件数」ではなかった

OGE Form 278-T は Periodic Transaction Report である。

OGE公式資料では、一定条件の報告対象取引について提出要件が定められている。

- OGE公式ガイド: https://www.oge.gov/web/278eGuide.nsf/Form_278-T
- OGE公式PTR Job Aid: https://www.oge.gov/Web/OGE.nsf/0/882742627808D2F9852589AC0059DF74/$FILE/508%20Finished%20PTR%20Job%20Aid%20All.pdf

ここで大事なのは、PDFに並ぶ行を「本人が直接発注したトレード回数」と読み替えないことだ。

今回の実装では17件のOGE Form 278-T文書を公式URL付きで索引化した。

そのうえで、7,699という値を次のように扱った。

- purchases: 5,026
- sales: 2,673
- total: 7,699
- status: `derived_external_parser_crosscheck`

5,026 + 2,673 = 7,699 というreconciliationは保存する。

しかし、**これを「OGE公式集計」とは呼ばない。**

このラベルがあることで、856→7,699という変化を「訂正」ではなく「scopeの更新」と説明できた。

## 一番危険なのは、数字だけがきれいに残ること

次のJSONは簡潔で扱いやすい。

```json
{
  "source": "OGE",
  "transactions": 7699
}
```

しかし、利用者が知りたい重要な情報が消えている。

- 7,699はOGEが明示した値なのか
- 自前parserで数えたのか
- 第三者parserの集計なのか
- 何文書を対象にしたのか
- 取得に失敗した文書はなかったのか
- 以前の856と何が違うのか

この状態でダッシュボードへ「7,699件」とだけ表示すると、見た目は整っていても説明責任がない。

そこで、値の周囲に最低限の意味を持たせる。

```json
{
  "scope": {
    "oge_278t_document_count": 17
  },
  "aggregate": {
    "transaction_rows": 7699,
    "purchases": 5026,
    "sales": 2673,
    "status": "derived_external_parser_crosscheck"
  },
  "official_definition": {
    "guide_url": "https://www.oge.gov/web/278eGuide.nsf/Form_278-T"
  }
}
```

重要なのはfield名ではない。

**利用者が「どこまでが一次資料で、どこからが計算か」を後から辿れること**だ。

## 私が分けた4つの状態

このケースでは、値を少なくとも4種類へ分けた。

### observed

一次資料そのものから確認したもの。

例:

- 公式PDF URL
- filing date
- 文書内の観測可能なrow

### derived

observedを入力に計算したもの。

例:

- 複数文書の行数合計
- purchase / sale集計
- 日別・期間別集計

### cross-check

正準値を検証する補助情報。

外部parserと一致しても、その外部実装を一次資料へ昇格させない。

### unavailable / partial

取得できなかった、または母集団が確定できない状態。

ここを `0` や `complete` に変換しない。

この4状態を分けるだけで、「数字があるか」ではなく「その数字をどこまで使ってよいか」を判断しやすくなる。

## 「取れた」と「全部取れた」は別の体験にする

公開データの収集では、HTTP 200が返ると成功した気になる。

しかし17文書のうち3文書を取得できず、14文書だけ集計できた場合、その値を全期間合計として出すと利用者は誤解する。

そこで `investor2` のsource contractでは、次を要求している。

- `query_or_scope`
- `retrieved_at`
- `source_urls`
- normalized filing index
- derived counts
- artifact hash
- partial / unavailableをcompleteへ昇格しないこと

つまり、成功条件を「処理が落ちなかった」から、**利用者へ意味を誤らず渡せる状態になった**へ変えた。

```text
取得できた
  ↓
母集団を確定できた
  ↓
派生処理を再現できた
  ↓
一次資料とのspot checkを通った
  ↓
公開可能
```

どこかで条件を満たさなければ、数字は作れても公開しない。

## SHA-256は「正しさ」ではなく「同じものを見ている」を固定する

snapshot catalogにはartifactのSHA-256も残している。

hashがあるから数字が正しい、という意味ではない。

目的は、**どのbyte列を検証し、どのartifactを採用したかを後から同定できること**である。

GitHubのArtifact Attestationsも、artifactのprovenanceを検証可能にする一方、それ自体がartifactの安全性を保証するわけではないと説明している。

https://docs.github.com/en/actions/concepts/security/artifact-attestations

データでも同じで、

- hashは同一性
- source URLは出所
- scopeは対象範囲
- parser/methodは計算方法
- spot checkは意味の検証

という別の役割を持つ。

一つの「verified: true」に全部押し込まない方がよい。

## 旧値を消さなかった理由

今回のsnapshotには、次のようなverification情報を残した。

```json
{
  "verification": {
    "primary_source_indexed": true,
    "primary_pdf_last_row_spot_checks": 5,
    "aggregate_is_not_labeled_as_an_oge_published_total": true,
    "previous_partial_count_856_superseded": true
  }
}
```

856は正準値からsupersedeした。

しかし削除して「最初から存在しなかった」ことにはしなかった。

なぜなら、856は単なる計算ミスではなく、**狭いscopeで得られた過去の観測結果**だったからだ。

ここを残すと、将来また数字が変わっても、変更履歴を説明できる。

```text
856
└─ 部分集合

7699
└─ 17文書を対象にしたcross-check集計
```

「数字が変わった」ではなく、「数字が代表する範囲が変わった」と言える。

この違いは、分析を継続利用する人にとって大きい。

## UIで数字を出すなら、値より先にラベルを設計する

データモデルを丁寧にしても、UIで全部「件数」と表示すれば意味はまた消える。

例えば次のように分けたい。

```text
7,699 rows
Derived cross-check
Scope: 17 OGE Form 278-T documents
Source: official OGE document index + external parser cross-check
```

少なくとも、利用者が

- 公式値
- 自前集計
- 外部cross-check
- partial / unavailable

を見分けられるようにする。

**Provenanceは裏側のデータ品質機能ではなく、数字を安心して使うためのUI情報でもある。**

## 別の分析へ持ち出すなら、5項目から始めればいい

すべての分析基盤へ大きなprovenance frameworkを入れる必要はない。

重要なKPIや派生値について、まず次の5つを残すだけでも違う。

```yaml
value: 7699
source: official OGE documents
scope: 17 Form 278-T documents
method: external parser cross-check + reconciliation
observed_at: 2026-08-11
```

さらに派生値なら、

```yaml
derived_from:
  - document index
  - parser output
```

を持たせる。

これだけで、次回値が変わったときに「何が変わったか」を比較できる。

## この設計で減らしたいのは、計算ミスだけではない

もちろん計算ミスは減らしたい。

しかし、それ以上に減らしたいのは、**正しい数字を間違った意味で使うこと**だ。

- 部分集合を全件だと思う
- 派生値を公式値だと思う
- 取得失敗を0件だと思う
- 外部cross-checkを一次資料だと思う
- scope更新をデータ急増だと思う

こうした事故は、計算式が正しくても起こる。

だから値と一緒に、出所・範囲・方法・状態を残す。

今回856が7,699へ変わったことで、その必要性がはっきりした。

**数字が変わらない分析を作ることはできない。**

でも、数字が変わったときに「なぜ」を答えられる分析は作れる。

利用者が長く使えるのは、その方だと思う。
