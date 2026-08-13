---
title: "60件引数を残しても、公開一覧は60件で切らない"
emoji: "📚"
type: "tech"
topics: ["api", "pagination", "typescript", "architecture"]
published: false
published_at: 2026-08-13 23:03
---

APIの互換性を守るために古い `limit=60` 引数を残したまま、公開アーカイブ全件取得へ移行したい。ここで素直に `slice(0, 60)` を残すと、呼び出し元は壊れなくてもデータ契約だけが古いまま残る。

`KAFKA2306/vlog` のReader実装では、この問題を「引数の互換性」と「productionで保証する取得範囲」を分離して解いている。PR #54で全件paginationと欠落検知を共通化し、PR #55で既存の `60` 引数を互換面として残しながら、production/default pathでは公開アーカイブを切り詰めない実装へ変更した。

一次情報:

- https://github.com/KAFKA2306/vlog/pull/54
- https://github.com/KAFKA2306/vlog/pull/55
- https://github.com/KAFKA2306/vlog/blob/4bec2f9d04fa12b0b469cc0a3dc68ec6593d58b8/apps/reader/lib/public-archive.ts
- https://github.com/KAFKA2306/vlog/blob/4bec2f9d04fa12b0b469cc0a3dc68ec6593d58b8/apps/reader/lib/novels-complete.ts
- https://github.com/KAFKA2306/vlog/blob/5897543bc432c59e440d09c1a3f8712663419422/apps/reader/tests/public-archive.test.ts
- https://github.com/PostgREST/postgrest/blob/main/docs/references/api/pagination_count.rst

## 1. 問題

実際の状況は次のようなものだった。

```ts
const items = await getPublicNovels(60)
```

この呼び出しは既存コードやテストから見れば安定している。しかし、公開Readerの要件が「最新60件」から「公開対象をすべて列挙する」に変わったあとも `60` をそのまま取得上限として使うと、61件目以降は静かに消える。

壊れた例は、互換性のために残した引数をそのまま新しい意味契約にも適用する実装である。

```ts
export async function getPublicNovels(limit = 60) {
  const rows = await fetchRows({ limit })
  return rows
}
```

このコードは例外を出さない。60件以下の環境ではテストも通りやすい。そのため、データ件数が閾値を超えた瞬間に初めて欠落が見える。

## 2. 原因

原因は、**呼び出しシグネチャの互換性**と**取得結果の意味契約**を同じものとして扱ったことにある。

`limit` 引数には少なくとも2つの役割があり得る。

1. 呼び出し元を壊さないための互換面
2. 実際に返すデータ量を決める業務仕様

仕様変更後もこの2つを結び付けたままだと、古い既定値が新しいproduction semanticsへ侵入する。

`vlog` PR #54では先に共通の全件取得contractを作り、`Prefer: count=exact` と `Content-Range` の総件数を使ってpagination完了条件を検証するようにした。さらにprivate row、公開開始日前、重複ID、総件数drift、missing pageを失敗扱いにしている。PostgREST公式ドキュメントも、paginationとcountを組み合わせて全rowを辿れること、`Prefer: count=exact` でtotal countを `Content-Range` に含められることを明記している。

## 3. 設計判断と代替案

代替案は3つある。

### 案A: `limit=60` を削除する

最もきれいだが、既存呼び出し元とテストを一斉に直す必要がある。変更範囲が大きく、機能変更とAPI破壊が同時に起こる。

### 案B: `limit=60` を残し、そのまま切り詰める

互換性は高いが、新しい「完全な公開アーカイブ」という要件を満たさない。最も危険なのは、失敗ではなく部分成功になる点である。

### 案C: 引数は残すがproduction pathでは意味を切り離す

`vlog` PR #55はこの形を採用している。Diary側は `_legacyLimit?: number` として受け取るが、remote public archiveが取れた場合は全件を返す。Novel側も、既存のinjected fetchテストではlegacy limitを維持しつつ、default production fetchでは共通のcomplete archive readerへ流す。

この設計の利点は、**互換性移行と意味契約移行を別々に進められること**である。

## 4. 実装

最小形にすると、境界は次のようになる。

```ts
type FetchLike = typeof fetch

async function fetchAllPublicRows(): Promise<Row[]> {
  const out: Row[] = []
  let expectedTotal: number | null = null
  let offset = 0
  const pageSize = 250

  while (expectedTotal === null || out.length < expectedTotal) {
    const response = await fetch(
      `/rest/v1/items?order=date.desc,id.asc&limit=${pageSize}&offset=${offset}`,
      { headers: { Prefer: 'count=exact' } },
    )
    if (!response.ok) throw new Error(`request failed: ${response.status}`)

    const total = parseExactCount(response.headers.get('content-range'))
    if (expectedTotal === null) expectedTotal = total
    else if (total !== expectedTotal) throw new Error('count drift')

    const rows = await response.json() as Row[]
    if (rows.length === 0) break
    out.push(...rows)
    offset += rows.length
  }

  if (expectedTotal === null || out.length !== expectedTotal) {
    throw new Error(`incomplete archive: expected ${expectedTotal}, got ${out.length}`)
  }
  return out
}

export async function getItems(
  legacyLimit = 60,
  fetchImpl: FetchLike = fetch,
) {
  if (fetchImpl !== fetch) return fetchLegacyRows(legacyLimit, fetchImpl)
  return fetchAllPublicRows()
}
```

重要なのは `_legacyLimit` という名前そのものではない。**production pathがその値を取得上限として解釈しない**ことがcontractである。

### 改善後の例

公開対象が83件あり、既存callerが `getItems(60)` を呼んでいても、production/default pathでは83件を返す。一方、既存unit testがinjected fetchで60件上限を前提としているなら、そのテスト用互換経路だけは段階的に維持できる。

## 5. 検証

「60件を超えても返る」だけでは不十分である。完全取得contractなら、欠落を成功として返さないことまで検証する。

`vlog` PR #54のtestではDiary/Novelの両方について、件数0〜17、page size 1〜5を組み合わせて全IDが1回ずつ返ることを確認している。さらに次のnegative caseを独立fixtureにしている。

- private rowが混じったらreject
- 公開開始日前のrowが混じったらreject
- page間でduplicate IDが出たらreject
- missing pageならpartial resultを返さずreject
- countがpagination途中で変わったらreject

読者向けの最小テストなら、少なくとも境界値を3つ置く。

```ts
for (const count of [59, 60, 61]) {
  const rows = makeRows(count)
  const result = await fetchAll(rows, { pageSize: 20 })
  expect(result).toHaveLength(count)
}
```

61件で初めて失敗する実装を、この1行追加で捕まえられる。

## 6. 失敗と学び

最初にpaginationを正しく作っても、上位callerが最後に `slice(0, 60)` していれば完全取得にはならない。

実際、PR #54では共通archive readerが全件取得を実装した一方、Diary callerには引数によるsliceが残り、Novelには独立した `limit=60` pathが残っていた。PR #55の目的は、その残存truncate pointをproduction/default pathから外すことだった。

ここから得られる学びは、**下位層のpagination correctnessだけをテストしても、product contractは保証できない**ということだ。取得層、adapter層、UI loader層のどこか1か所に固定上限が残れば、ユーザーから見える結果は欠ける。

また `count=exact` 自体にもコストがある。PostgREST公式ドキュメントは大きなtableではexact countが遅くなり得ると説明している。そのため、これは常に最適なpagination方式という主張ではない。今回の設計判断は「公開アーカイブを完全列挙し、欠落をfail-closeしたい」という要件に対するものだ。

## 7. 再現方法

手元で再現するなら、DBやSupabaseは不要である。fake fetchだけで確認できる。

1. 61件の配列を用意する。
2. `limit=20&offset=N` を解釈して20件ずつ返すfake fetchを作る。
3. response headerへ `Content-Range: start-end/61` を付ける。
4. 旧実装として `getItems(60)` の最後に `slice(0, 60)` を置き、60件になることを確認する。
5. 改善実装ではlegacy引数をproduction pathの取得上限に使わず、61件になることを確認する。
6. 2page目を空配列へ差し替え、61件未満のpartial resultではなく例外になることを確認する。

確認したいのは「pagination関数が動く」ことではなく、**古い互換引数が新しい完全取得contractを再び狭めていないこと**である。

## まとめ

後方互換のために古い引数を残すことと、その引数の古い意味をproductionに残すことは別問題である。

完全取得へ移行するときは、次の順序が安全だった。

1. 下位層にcomplete pagination contractを作る
2. count drift・duplicate・missing pageをfail-closeする
3. 上位callerに残るtruncate pointを洗い出す
4. legacy引数は互換面として残しても、production semanticsから切り離す
5. 59/60/61のような境界値で回帰を固定する

「APIは壊していないのにデータだけ欠ける」という不具合は、型や例外では見つけにくい。互換性と意味契約を別々に設計すると、この種の静かな欠落をかなり早い段階で止められる。
