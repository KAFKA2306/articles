---
title: "CSV一括登録でデータを壊さない。追加・重複・エラーを実行前に全部確認する"
emoji: "🧪"
type: "tech"
topics: ["javascript", "dataengineering", "testing", "privacy"]
published: false
published_at: 2026-08-12 12:30
---

CSVから何百件もデータを登録するとき、本当に怖いのは「CSVを読めないこと」ではない。

**間違ったデータを、正常に一括登録できてしまうこと**だ。

既存データとの重複、表記揺れ、不正なID、情報不足。これらを含むCSVをそのまま本番データへ書き込むと、あとで人間が重複削除や修正をすることになる。

そこで、本棚データベース `KAFKA2306/books` では、CSVを選んでもすぐには登録しない。

まず全行を既存データと照合し、

- すでに登録済み
- 新規追加できる
- 既存作品の別Editionとして追加できる
- 同じCSV内で重複している
- ISBNが不正
- 情報不足
- 類似タイトルがあり人間確認が必要

のように、**実行前に1行ずつ判定結果を見せる**ようにした。

しかも、この確認中は正準catalogを書き換えない。

この記事では、CSV parserの作り方ではなく、**一括登録を「押してから祈る処理」にしないための設計**を、実装とテストを根拠に整理する。

実装の一次情報はこちら。

- 診断core: https://github.com/KAFKA2306/books/blob/main/src/migration-diagnosis.mjs
- 非破壊性を含むテスト: https://github.com/KAFKA2306/books/blob/main/tests/migration-diagnosis.test.mjs
- Browser UI: https://github.com/KAFKA2306/books/blob/main/migration.js
- 初期実装commit: https://github.com/KAFKA2306/books/commit/e9dbe8c968f17dd3626d9488a3fcb269fdbaaecc
- Browser版PR: https://github.com/KAFKA2306/books/pull/43

## 「CSVを読み込めた」は成功条件ではない

例えば、手元にこんな記録があるとする。

```text
1984 / Kindle
1984 新訳版 / 購入済み
一九八四年 / 紙
サンプル: 1984
```

人間なら、4行をそのまま4冊の新規データとは考えない。

同じ作品かもしれない。別の版かもしれない。単なるメモが混ざっているかもしれない。

一方、単純なCSV importerの成功条件を「構文エラーなく読み込めた」にすると、4行を4件として登録することもできてしまう。

だから必要なのは、importの成否だけではない。

**その行を登録したら、既存データに対して何が起きるのか。**

これを登録前に説明できることが重要になる。

## importボタンより先に「登録予定表」を作る

典型的なimport処理は、次の責務を一つの流れに詰め込みやすい。

```text
parse
→ normalize
→ validate
→ existing dataを検索
→ actionを決める
→ canonical dataへ書き込む
→ 結果を返す
```

この構造では、判定と書き込みが近い。

途中で「既存データだった」「同じCSV内で重複していた」と判明した時点で、すでに副作用をどう扱うか考えなければならない。

そこで最初の実装では、書き込み自体を外した。

```text
parse
→ normalize
→ precheck
→ diagnose
→ report

# canonical dataへの書き込みなし
```

Browser版でユーザーが行うことも単純だ。

1. CSVを選ぶ
2. 「診断する」を押す
3. 行ごとの結果を確認する
4. 必要ならJSON / HTML reportを保存する

この段階には「全部適用する」ボタンを置いていない。

機能を減らしたのではなく、**正しい判定を確認する工程と、本番データを書き換える工程を分離した**。

Browser実装では `migration.js` がCSVを読み、公開catalogを取得し、`diagnoseMigration()` を呼び出している。

https://github.com/KAFKA2306/books/blob/main/migration.js

## 成功・失敗ではなく「なぜそう判断したか」を返す

一括登録では、`success: true` だけ返されても判断材料にならない。

必要なのは理由である。

現在の診断coreでは、例えば次のreason codeを返す。

```text
invalid_isbn
existing_holding
duplicate_in_batch
insufficient_metadata
existing_work_without_isbn
review_similar_title
safe_new_work
safe_new_edition
```

実装:
https://github.com/KAFKA2306/books/blob/main/src/migration-diagnosis.mjs

これにより、同じ「登録しない」という結果でも意味を分けられる。

| 判定 | 意味 | 次の行動 |
|---|---|---|
| `existing_holding` | すでに登録済み | 変更しない |
| `safe_new_work` | 新しい作品として追加候補 | 自動処理候補 |
| `safe_new_edition` | 既存作品の別版として追加候補 | 自動処理候補 |
| `duplicate_in_batch` | 同じ入力内で重複 | 入力を確認 |
| `invalid_isbn` | ISBNが不正 | 修正 |
| `review_similar_title` | 類似作品候補あり | 人間確認 |

人間向けUIの文言は後から変えられる。

一方、自動処理や集計に使うreason codeは固定できる。

つまり、**利用者への説明とシステムの判断契約を分離できる**。

## 通常登録とCSV登録で「正解」を分けない

移行機能を別実装にすると、別の事故が起こる。

通常登録では重複扱いなのに、CSV登録では新規扱いになる。

CLIでは要確認なのに、Browserでは自動追加扱いになる。

入力経路ごとに判定ロジックを持つと、「どれが本当の判定か」が分からなくなる。

そこでmigration側は、既存catalogの `precheckCandidates` を再利用している。

```text
CLI / Browser
      ↓
diagnoseMigration()
      ↓
precheckCandidates()
```

`src/migration-diagnosis.mjs` の先頭でも `precheckCandidates` をimportしており、診断結果をその共通判定から組み立てている。

https://github.com/KAFKA2306/books/blob/main/src/migration-diagnosis.mjs

**入力方法は違っても、「このデータをどう扱うか」のauthorityは1か所にする。**

これが、CSV機能そのものより重要だった。

## CSVはBrowserの外へ送らない

本棚データには、書名、ISBN、購入経路、購入履歴などが含まれうる。

診断だけなら、それをサーバへアップロードする必要はない。

Browser版では、選択されたCSVを `File.text()` で読み、公開されている `api/v1/catalog.json` を取得して、ブラウザ内で診断する。

```js
const [text, response] = await Promise.all([
  fileInput.files[0].text(),
  fetch('./api/v1/catalog.json', { cache: 'no-store' }),
]);

const rows = parseCsv(text);
const catalog = await response.json();
currentReport = diagnoseMigration(rows, catalog);
```

現在のBrowser実装:
https://github.com/KAFKA2306/books/blob/main/migration.js

PR #43にも、選択したCSVはbrowser memory内で処理し、ユーザーファイルをuploadしないことが設計境界として記録されている。

https://github.com/KAFKA2306/books/pull/43

これは「アップロード後に安全に保管する」設計ではない。

**そもそも診断に不要なデータを送らない**設計である。

## 「書き換えません」という表示だけでは証拠にならない

診断reportは次の情報を持つ。

```json
{
  "mode": "dry-run",
  "catalog_mutated": false
}
```

しかし、このフラグだけなら自己申告でしかない。

内部でcatalogを変更してしまったあとに `false` を返すバグも作れる。

そこでテストでは、診断前後のcatalogを比較している。

```js
const before = JSON.stringify(catalog);
const report = diagnoseMigration(rows, catalog);

assert.equal(report.mode, 'dry-run');
assert.equal(report.catalog_mutated, false);
assert.equal(JSON.stringify(catalog), before);
```

現在のテスト:
https://github.com/KAFKA2306/books/blob/main/tests/migration-diagnosis.test.mjs

「壊しません」と説明するだけでなく、**本当に入力catalogが変化していないことを回帰テストにする**。

ここまでやって初めて、dry-runが仕様ではなく検証対象になる。

## JSONとHTMLを同じ判定結果から作る

一括登録の確認結果は、開発者だけが読むとは限らない。

そのため、同じ診断結果から機械向けJSONと人間向けHTMLを作る。

```text
同じ diagnosis report
       ├─ JSON → CI / 集計 / 後続処理
       └─ HTML → 人間レビュー
```

重要なのは、JSON用とHTML用で再判定しないことだ。

判定は一度だけ行い、表示形式だけを変える。

`renderDiagnosisHtml(report)` も同じreport objectを入力にしている。

https://github.com/KAFKA2306/books/blob/main/src/migration-diagnosis.mjs

## ユーザーが本当に見たいのは件数ではなく「自分の1行」

「100件中95件成功」というsummaryは便利だ。

しかし、既存データへ一括登録する場面では、それだけでは安心できない。

残り5件が何なのか分からないからだ。

ユーザーが確認したいのは、例えばこういう表である。

| 入力行 | 予定action | 理由 |
|---|---|---|
| ISBN既存 | 変更なし | `existing_holding` |
| 新規ISBN + 既存Work | Edition追加候補 | `safe_new_edition` |
| 新規title | Work追加候補 | `safe_new_work` |
| 類似title | 保留 | `review_similar_title` |
| ISBN不正 | 拒否 | `invalid_isbn` |

つまり、重要なのは「何件通ったか」より、**この1行をシステムがどう理解したのか**である。

## この設計を他のシステムへ移すなら

本棚に限った話ではない。

顧客台帳、商品マスタ、設備台帳、会員データなど、既存データへ外部ファイルを一括登録する処理なら同じ構造を使える。

最低限、次の5点を分ける。

### 1. 本番判定を副作用のない関数へ切り出す

```js
function precheckCandidates(candidates, canonical) {
  // normalize / validate / lookup / decide
  // canonicalは変更しない
}
```

### 2. 書き込み前に予定actionを返す

```js
function diagnoseMigration(rows, canonical) {
  const precheck = precheckCandidates(normalize(rows), canonical);
  return {
    mode: 'dry-run',
    catalog_mutated: false,
    results: precheck.results.map(toDiagnosticResult),
  };
}
```

### 3. 理由をmachine-readableなcodeにする

UI文言と自動処理の契約を分ける。

### 4. 非破壊性をbefore / afterでテストする

「変更しない予定」ではなく、実際に変更されていないことを検証する。

### 5. CLIとUIで同じ判定coreを使う

入力・表示をadapterにし、意味判定を複製しない。

## dry-runだけでは、本番適用の安全性は完成しない

ここは重要な制約である。

dry-runで「今なら安全」と判定しても、その後に正準データが更新されれば結果は変わりうる。

実際のapply処理まで作るなら、さらに考える必要がある。

- 診断後にcanonicalが更新されるTOCTOU
- transaction競合
- 外部APIへの副作用
- 大規模入力のmemory制約
- server-side secretが必要な照合

したがって、dry-runは「安全なmigrationが完成した」という意味ではない。

価値は、**本番書き込みを作る前に、判定規則を独立して見せ、テストできること**にある。

## import機能ではなく「実行前に説明できる機能」を作る

最初の要求を「CSVを取り込めるようにする」と置くと、最短経路はimportボタンになる。

しかしユーザー側から要求を置き直すと違う。

> 自分のデータを壊さず、外へ送らず、書き込む前に、各行がどう扱われるか確認したい。

この要求なら、最初に作るべきものはimporterではない。

**登録予定を説明する診断画面**である。

一括登録を安心して使えるかどうかは、「成功しました」と表示できるかでは決まらない。

**実行前に、何をする予定なのかを説明できるか。**

そこから設計した方が、結果として壊れにくい。