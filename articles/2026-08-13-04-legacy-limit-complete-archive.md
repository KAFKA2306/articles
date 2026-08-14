---
title: "APIは壊れていないのに、61件目が消える。互換性を守りながら「全部見える」を取り戻す"
emoji: "📚"
type: "tech"
topics: ["api", "pagination", "typescript", "architecture"]
published: false
published_at: 2026-08-13 23:03
---

公開一覧が60件までは正常に見える。

61件目が増えた瞬間、何もエラーを出さずに消える。

APIも落ちない。既存callerも壊れない。テストも60件以下ならgreenのまま。

利用者から見ると、**「全部見える」と思っていた一覧が静かに欠ける。**

`KAFKA2306/vlog` では、以前から残っていた `limit=60` という互換引数と、新しい「公開対象をすべて列挙する」というproduct contractを分離した。

- PR #54: https://github.com/KAFKA2306/vlog/pull/54
- PR #55: https://github.com/KAFKA2306/vlog/pull/55
- archive reader: https://github.com/KAFKA2306/vlog/blob/4bec2f9d04fa12b0b469cc0a3dc68ec6593d58b8/apps/reader/lib/public-archive.ts
- complete reader: https://github.com/KAFKA2306/vlog/blob/4bec2f9d04fa12b0b469cc0a3dc68ec6593d58b8/apps/reader/lib/novels-complete.ts

この記事で扱うのはpaginationの実装方法ではない。

**古い呼び出し元を壊さず、利用者へは現在のproduct promiseどおりの完全な結果を返す移行方法**について書く。

## 古い引数が、新しいUXを縛っていた

既存コードには、次のような呼び出しがあった。

```ts
const items = await getPublicNovels(60)
```

以前の要件が「最新60件」なら正しい。

しかし要件が、

```text
公開対象をすべて一覧する
```

へ変わったあとも、`60` をそのまま取得上限として使えば61件目以降は消える。

ここで厄介なのは、**後方互換を守った結果としてproduct semanticsだけが古いまま残る**ことだ。

## signature compatibilityとproduct semanticsを分ける

`limit` には2つの意味が混ざっていた。

1. 既存callerを壊さないためのAPI surface
2. 実際に返す件数を制限する業務仕様

要件変更後は、この2つを切り離した。

```text
legacy argument
  └─ caller compatibilityのため残す

production semantics
  └─ complete public archiveを返す
```

PR #55では、legacy引数を受け取る面を残しつつ、default production pathではその値を最終truncateへ使わない形へ移行している。

**引数を残すことと、その古い意味を残すことは同じではない。**

## complete fetchは「複数page取れた」だけでは足りない

PR #54では、まず下位層へcomplete archive contractを作った。

`Prefer: count=exact` と `Content-Range` のtotalを使い、期待件数までpageを辿る。

しかし本当に守りたいのは、loopが回ったことではない。

```text
期待total = 83
取得total = 83
duplicate = 0
missing page = 0
invalid/private row = 0
```

まで確認して初めてcompleteと扱う。

途中pageが空なら、取れた分だけを返さない。

countが途中で変われば止める。

duplicate IDがあれば止める。

**部分成功を「全件取得成功」にしない。**

## 下位paginationが正しくても、最後のsliceで全部壊れる

ここが実装上の重要な学びだった。

下位のarchive readerが83件を正しく返しても、上位callerが最後に、

```ts
return rows.slice(0, 60)
```

としていれば、利用者には60件しか見えない。

PR #54でcomplete paginationを作ったあとも、上位のlegacy truncate pointが残っていたため、PR #55でproduction pathから外した。

つまり完全取得は、

```text
fetch layer
adapter layer
reader layer
UI loader
```

のどこか1つだけ見ても証明できない。

**最終的に利用者へ返る配列までcontractを追う必要がある。**

## 59 / 60 / 61をtestするだけで、静かな欠落を捕まえやすい

境界値testは単純だ。

```ts
for (const count of [59, 60, 61]) {
  const rows = makeRows(count)
  const result = await fetchAll(rows, { pageSize: 20 })
  expect(result).toHaveLength(count)
}
```

60までしかtestしなければ、旧仕様の上限とtest datasetが偶然一致してしまう。

61を1件足すだけで、古いtruncateが見える。

この種のcontractでは、通常ケースを増やすより**境界の外へ1歩出るfixture**が効く。

## 利用者が欲しいのは「API互換」ではなく「欠けていない」こと

開発者には、

```text
breaking changeを避けた
```

ことが重要に見える。

利用者には、

```text
公開されているものが全部見える
```

ことの方が重要である。

だからmigrationの成功条件を、

```text
古いcallerがまだ動く
```

だけにしない。

```text
古いcallerも動く
AND
新しいproduct promiseも満たす
```

へする。

この2軸で見れば、互換性維持がUX退行を隠すことを防ぎやすい。

## 既存APIを見直すときのチェックリスト

古いdefaultやlimitが残るAPIでは、次を確認する。

1. この引数は今も業務仕様なのか、単なる互換面なのか
2. 下位層はcompleteでも上位でtruncateしていないか
3. 0件と取得失敗を分けているか
4. pagination途中のcount driftを検出しているか
5. duplicate/missing pageをpartial successにしていないか
6. 旧上限の直前・同値・直後をtestしているか

特に6は安い。

`59 / 60 / 61` のような3点だけでも、古い制約がproductionへ漏れているか見つけやすい。

## exact countにもコストがある

今回の方式が常に最適という話ではない。

PostgRESTの公式documentationでも、exact countは大きなtableでコストが上がり得る。

https://github.com/PostgREST/postgrest/blob/main/docs/references/api/pagination_count.rst

今回それを使ったのは、**公開アーカイブを完全列挙し、欠落をfail-closeしたい**という要件があったからだ。

性能が主目的なら、別のpagination contractを選ぶこともある。

設計手段よりproduct promiseを先に置く。

## この変更で守ったのはコードではなく、一覧への信頼だった

古い `limit=60` を削除してbreaking changeにする必要はなかった。

同時に、60件という古い意味まで残す必要もなかった。

- caller compatibilityは残す
- complete archive semanticsへ移す
- partial resultは返さない
- boundary testで61件目を守る

この分離で、**APIを壊さずに「全部見える」体験を更新できた。**

後方互換を守るとき、本当に守るべきなのは古いコードの形だけではない。

現在の利用者に何を約束しているかも、同じくらい重要だった。
