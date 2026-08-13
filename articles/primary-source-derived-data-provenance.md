---
title: "856件が7,699件になった。でも計算ミスではなかった：「どこまで数えたか」を残す"
emoji: "🔎"
type: "tech"
topics: ["dataengineering", "provenance", "python", "github"]
published: false
published_at: 2026-08-12 11:21
---

最初の集計は **856行** でした。

同じテーマを後から取り直すと、今度は **7,699行**。内訳は **5,026 purchases + 2,673 sales** です。

では、856は計算ミスだったのでしょうか。

そうではありませんでした。856は部分集合を対象にした値で、7,699は対象文書集合を広げた派生集計でした。しかも7,699も、U.S. Office of Government Ethics（OGE）が公表した単一の「公式合計」ではありません。

ここで壊れていたのは足し算ではなく、**その数字が何を代表するのかというラベル**でした。

この問題をきっかけに、OGE Form 278-T の公開データでは、一次資料そのもの、一次資料から観測した値、外部パーサを使った派生集計を別レイヤーへ分けました。

- 実装commit: https://github.com/KAFKA2306/investor2/commit/c8a3ab271b58396c2aa3b38d9ba7a8f4244a3210
- 正準snapshot: https://github.com/KAFKA2306/investor2/blob/main/docs/research/data/us_oge_trump_278t_trade_count_2026-08-11.json

この記事の問いは一つです。

**数字が更新されたとき、「前の値が間違っていた」のか、「scopeが違った」のかを、後からどう判別できるようにするか。**

## 1. 856と7,699は、何を数えていたのか

OGE Form 278-T は Periodic Transaction Report です。OGE公式ガイドでは、対象者に報告対象取引がある場合に提出が必要で、取引通知を受けてから30日以内、かつ取引から45日以内という提出期限が示されています。

- OGE公式ガイド: https://www.oge.gov/web/278eGuide.nsf/Form_278-T
- OGE公式PTR Job Aid: https://www.oge.gov/Web/OGE.nsf/0/882742627808D2F9852589AC0059DF74/$FILE/508%20Finished%20PTR%20Job%20Aid%20All.pdf

Job Aid は、原則として1取引あたり1,000ドル超の株式・債券・先物・オプション等の purchase / sale / exchange を報告対象として説明しています。したがって、PDFに並ぶ行は「公開された報告取引」であり、そのまま「本人が直接発注したトレード回数」と読み替えることはできません。

実装では17件のOGE Form 278-T文書を公式URL付きで索引化する一方、7,699行という集計値を `derived_external_parser_crosscheck` として分離しています。5,026 purchases + 2,673 sales = 7,699 という reconciliation は保持しますが、これを「OGE公式集計」とは呼びません。

ここで初めて、856から7,699へ変わった理由を「値の訂正」ではなく「scopeの更新」として説明できます。

## 2. 失敗しやすいデータモデル

最初に避けるべき形は、次のような1レコードへの押し込みです。

```json
{
  "source": "OGE",
  "transactions": 7699
}
```

このJSONでは、少なくとも次の3点が判別できません。

1. 7,699はOGEが明示した値なのか
2. PDFを自前集計した値なのか
3. 第三者パーサを照合した値なのか

値だけが残り、**観測方法が消えています**。後からパーサの対象範囲が変わっても、利用側は差分理由を説明できません。

## 3. 改善した設計：source と derived を分離する

実装したsnapshotでは、公式定義、公式文書索引、派生集計を分けました。最小化すると次の構造です。

```json
{
  "scope": {
    "oge_278t_document_count": 17
  },
  "aggregate": {
    "transaction_rows": 7699,
    "purchases": 5026,
    "sales": 2673,
    "status": "derived_external_parser_crosscheck",
    "source_url": "<cross-check source>"
  },
  "official_definition": {
    "guide_url": "https://www.oge.gov/web/278eGuide.nsf/Form_278-T"
  },
  "records": [
    {
      "form": "OGE Form 278-T",
      "source_url": "<official OGE PDF>"
    }
  ]
}
```

重要なのは、`source` の名前ではなく **status と URL の粒度**です。

### observed

一次資料そのものから確認した値。例：PDFのURL、掲載された取引行、listed filing date。

### derived

observed を入力に計算した値。例：複数文書の行数合計、日別件数、purchase / sale 集計。

### cross-check

正準値を作るための補助検証。第三者実装との一致確認には使えても、それ自体を一次資料へ昇格させません。

### unavailable

取得できなかった、または母集団が確定できなかった状態。ここを `0` に変換しないことが重要です。

## 4. fail-close をデータ取得にも適用する

`investor2` のsource contractには、OGE取得について次のルールを置いています。

- provenance に `query_or_scope`, `retrieved_at`, `source_urls` を必須化
- normalized filing index と derived counts を SHA-256 で固定
- 公式OGE URLをすべて保持
- unavailable transaction を推測しない
- partial filing set を complete とみなさない
- failure mode を `fail-closed` にする

この設計の利点は、「取れなかった」と「0件だった」を分離できることです。

たとえば17文書のうち3文書の取得に失敗した場合、14文書だけの合計を全期間合計として公開してはいけません。処理自体は成功していても、**母集団の完全性が壊れた時点で公開ゲートを閉じる**べきです。

## 5. なぜ SHA-256 を保存するのか

snapshot catalog にはartifactのSHA-256を保存しています。目的は「暗号学的に安全だから数字も正しい」と主張することではありません。目的は、**どのバイト列を検証・採用したかを後から同定すること**です。

ここは supply-chain provenance と似ています。GitHubのArtifact Attestationsも、artifactがどのrepository・workflow・commitから生成されたかを検証可能にする仕組みであり、GitHub自身も「attestationはartifactが安全である保証ではない」と明記しています。

- GitHub Docs: https://docs.github.com/en/actions/concepts/security/artifact-attestations

データsnapshotでも同じで、hashは「正しさ」の証明ではなく**同一性**の固定です。正しさは別途、source URL、scope、parser、reconciliation、spot checkで検証します。

## 6. 実際に入れた検証

今回のsnapshotでは、次を機械可読な検証情報として残しています。

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

特に重要なのは最後の2つです。

以前の856行という値は部分集合を対象にした値だったため、正準値から supersede しました。しかし削除して「最初から存在しなかった」ことにはしません。**誤った値の履歴ではなく、誤ったscopeの履歴**として扱います。

この区別があると、数字が 856 → 7,699 に変わった理由を「データが急増した」と誤解せず、「対象文書集合を完全化した」と説明できます。

## 7. 再現するための最小チェックリスト

公開データを集計する場合、少なくとも次を満たすと provenance の混線を減らせます。

1. 一次資料のURLをレコード単位で保存する
2. `retrieved_at` と資料側の日付を分ける
3. 母集団のscopeを文章で保存する
4. observed / derived / cross-check / unavailable を区別する
5. derived値に計算元と計算式を持たせる
6. partial取得時はcomplete扱いしない
7. snapshotにcontent hashを持たせる
8. spot check件数と場所を残す
9. 旧値をsupersedeした理由を残す
10. UIでは「公式値」と「自前集計」をラベルで分ける

## 8. 数字をUIへ出す前の判定

実務では、次の順で判定すると事故を減らせます。

```text
公式資料を取得できたか
  └─ no  → unavailable
  └─ yes
      ↓
母集団を確定できたか
  └─ no  → partial / publishしない
  └─ yes
      ↓
派生処理を再現できるか
  └─ no  → derived値をpublishしない
  └─ yes
      ↓
一次資料とのspot checkを通ったか
  └─ no  → reject
  └─ yes → publish可能
```

「HTTP 200だったから成功」では不十分です。**取得成功・母集団確定・派生計算成功・意味の検証**は別々の状態です。

## 9. 適用範囲と限界

この設計は、政府開示、決算PDF、統計資料、スクレイピング結果など、一次資料から二次データセットを作る処理に適用できます。

一方、今回の7,699行という値はOGEが公表した単一集計値ではなく、snapshot内でも第三者パーサによるcross-checkとして明示しています。また、OGE Form 278-Tの行数は「本人が直接発注した注文回数」を意味しません。OGEの公式説明では、一定条件の報告対象取引を開示する制度だからです。

したがって、このsnapshotから言えるのは「指定scopeの公開Form 278-T群について、外部パーサ集計を7,699行として照合し、その帰属を分離して保存した」までです。それ以上の投資行動解釈には別の検証が必要です。

## 10. 次に検証すべきこと

次の改善は、各PDFを自前parserで正規化し、document-level count → aggregate の全計算経路をrepository内だけで再現可能にすることです。その段階では第三者cross-checkを正準集計から外し、公式PDF → parser version → normalized rows → aggregate → snapshot hash までを一本のprovenance chainとして固定できます。

データ基盤で重要なのは、数字を増やすことではありません。**その数字について「どこまでが観測で、どこからが計算か」を機械的に答えられること**です。
