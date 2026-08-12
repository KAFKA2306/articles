---
title: "CSV importerを作る前にdry-runしか作らなかったら、CLIとブラウザの判定が1本になった"
emoji: "🧪"
type: "tech"
topics: ["javascript", "dataengineering", "testing", "privacy"]
published: true
published_at: 2026-08-12 12:30
---

CSVの1行が、構文上は正常だとします。

ISBNは新しい。しかし正規化した書名は既存Workに近い。

これは「成功」でしょうか。それとも「失敗」でしょうか。

今回 `KAFKA2306/books` で移行機能を作っていて、この2値では足りませんでした。`safe_new_work`、`safe_new_edition`、`existing_holding`、`review_similar_title` は、どれも単純なparse errorではないからです。

そこで最初に作ったのはimporterではなく、**正準データを一切変更せず、本番と同じ判定理由だけを返すdry-run診断**でした。

その後にCLIとブラウザUIを増やしたところ、両方を別々に実装する必要はありませんでした。どちらも同じ `diagnoseMigration()` へ合流できたからです。

なぜ「書き込む機能を作らない」というMVPが、後続のUIまで単純化したのか。そこを実装順に追います。

## 1. 問題：importは成功/失敗だけでは足りない

移行対象のCSVには、少なくとも次のようなケースが混ざります。

- 既に登録済みのISBN
- ISBNは新しいが既存Workへ追加すべきEdition
- 完全に新規のWork
- ISBNのチェックディジット不正
- 同じCSV内の重複
- ISBNが無く、正規化書名だけが既存Workと一致
- 類似タイトルがあり、人間確認が必要

直接importする設計では、これらを「成功した行」「失敗した行」の2値に押し込みがちです。しかし実際には、`safe_new_work` と `review_similar_title` はどちらも構文エラーではありません。必要なのは**行ごとの意味的な判定理由**です。

この図で見るべき点は、CSVと正準catalogの間に「診断」という読み取り専用段階を置いていることです。書き込みより前に、何が安全で何が要確認かを分離します。

![移行診断の全体像](/images/csv-migration-dry-run-before-write/01-overview.png)

## 2. 原因：判定と副作用が同じ関数に入ると境界が消える

典型的なimporterは次のような責務を一度に持ちます。

```text
parse
→ normalize
→ validate
→ lookup existing data
→ decide action
→ mutate canonical data
→ report result
```

ここで問題なのは、`decide action` と `mutate canonical data` が連続していることです。途中で例外が起きればロールバックが必要になり、部分成功を許せば再実行時の冪等性まで考える必要があります。

今回のMVPではここを切り離しました。

```text
parse
→ normalize
→ precheck
→ diagnose
→ report

# canonical mutation は存在しない
```

この図では、直接importが「判定」と「書き込み」を同時に抱えることで、ISBN不正やbatch重複を見つけるタイミングと副作用の順序が絡む点を見ます。

![直接importのリスク](/images/csv-migration-dry-run-before-write/02-direct-import-risk.png)

実装では `diagnoseMigration(rows, catalog)` が既存の `precheckCandidates` を再利用し、結果に `mode: 'dry-run'` と `catalog_mutated: false` を含めます。

```js
export function diagnoseMigration(rows, catalog) {
  const candidates = normalizeMigrationRows(rows);
  const precheck = precheckCandidates(candidates, catalog);

  return {
    schema_version: 1,
    mode: 'dry-run',
    catalog_mutated: false,
    summary: { ...precheck.summary, reason_counts: counts },
    results,
  };
}
```

実装根拠:
https://github.com/KAFKA2306/books/commit/e9dbe8c968f17dd3626d9488a3fcb269fdbaaecc

## 3. 設計判断：既存precheckを「唯一の判定コア」にする

別のmigration専用validatorを新設する案もありました。しかし、それを採ると通常登録と移行でルールがずれます。

たとえば通常登録では「既存Holding」と判定されるISBNが、migration validatorでは「新規Edition」になるような差分が生じると、ユーザーは入力経路によって異なる結果を受け取ります。

そこでmigrationは既存の `precheckCandidates` を呼ぶadapterにしました。

この図で見るべき点は、CLIとBrowserが互いを再実装せず、中央の `diagnoseMigration()` に合流していることです。UIが増えても判定規則は一か所です。

![共有判定コア](/images/csv-migration-dry-run-before-write/03-shared-core.png)

### 代替案との比較

| 案 | 利点 | 欠点 | 採否 |
|---|---|---|---|
| migration専用validator | 独立して作りやすい | 本番判定とdriftする | 不採用 |
| importしてrollback | 本番コードを直接使える | rollback・部分成功・再実行が複雑 | MVPでは不採用 |
| 既存precheckを再利用するdry-run | 判定差分が生まれにくい | precheckを副作用なしに保つ必要 | 採用 |

## 4. ブラウザUI：CSVをアップロードしない

CLIの次にブラウザUIを追加した実装では、選択したCSVをサーバへ送信せず、ブラウザ内で診断する境界を採用しています。PR #43 は、選択したCSVをブラウザメモリ内だけで処理し、ユーザーファイルをアップロードしないことを明記しています。

ブラウザ版は次の2つだけを読みます。

1. ユーザーが選択したCSVを `File.text()` でブラウザ内メモリへ読む
2. 公開済みの `api/v1/catalog.json` を `fetch()` する

W3C File APIは、Webアプリがユーザーのファイルを表現・選択・読み取りできるAPIを定義しています。
https://www.w3.org/TR/FileAPI/

MDNの `Blob.text()` ドキュメントでも、Blobの内容をUTF-8文字列として非同期に取得することが説明されています。
https://developer.mozilla.org/en-US/docs/Web/API/Blob/text

実装では選択CSVを送信する `fetch` はありません。

```js
const [text, response] = await Promise.all([
  fileInput.files[0].text(),
  fetch('./api/v1/catalog.json', { cache: 'no-store' }),
]);

const rows = parseCsv(text);
const catalog = await response.json();
currentReport = diagnoseMigration(rows, catalog);
```

この図では、ネットワーク境界を見ます。外から取得するのは公開catalogだけで、Local CSVからUpload APIへ向かう経路はありません。

![ローカル処理のプライバシー境界](/images/csv-migration-dry-run-before-write/04-local-privacy-boundary.png)

PR #43でも「selected CSV in browser memory only」「user file is never uploaded」を設計境界として明記しています。
https://github.com/KAFKA2306/books/pull/43

## 5. 実装：エラーメッセージではなくreason codeを出す

人間向けのエラーメッセージだけを返すと、後から集計しにくくなります。文言変更がAPI変更になってしまうからです。

そこで診断結果にはmachine-readableな `reason_codes` を入れました。

実装されたコードには、少なくとも次が存在します。

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

この図で見るべき点は、「何が起きたか」を文言ではなく安定したコードとして残すことです。UI表示と自動処理を分離できます。

![reason code](/images/csv-migration-dry-run-before-write/05-reason-codes.png)

たとえばJSON reportはCIや後段処理で `reason_counts` を集計できます。一方HTML reportは人間が表として読みます。どちらも同じ `report` から生成されます。

## 6. 検証：dry-runを宣言ではなくテストで固定する

`catalog_mutated: false` と返すだけでは、非破壊性の証明にはなりません。内部でcatalogを書き換えてからfalseを返すバグも作れてしまいます。

テストでは診断前にcatalogを直列化し、診断後と一致することを確認しています。

```js
const before = JSON.stringify(catalog);
const report = diagnoseMigration(rows, catalog);

assert.equal(report.mode, 'dry-run');
assert.equal(report.catalog_mutated, false);
assert.equal(JSON.stringify(catalog), before);
```

この図では、`catalog_mutated: false` という自己申告と、before/after同一性検証を分けて見るべきです。重要なのは後者です。

![非破壊性テスト](/images/csv-migration-dry-run-before-write/06-non-mutation-test.png)

同じテストで、既存Holding、新規Work、ISBN不正、batch重複のreason codeも確認しています。

実装根拠:
https://github.com/KAFKA2306/books/commit/e9dbe8c968f17dd3626d9488a3fcb269fdbaaecc

## 7. UIは「選ぶ→診断→保存」の3段階だけにした

ブラウザ版の操作は次の3段階です。

1. CSVを選ぶ
2. 「診断する」を押す
3. JSONまたはHTMLを保存する

正準catalogへ「適用する」ボタンはありません。MVPの目的を診断に限定したためです。

この図で見るべき点は、ユーザーフローの中に書き込み操作が存在しないことです。誤クリックで正準データが変わる経路自体を作っていません。

![3段階の操作](/images/csv-migration-dry-run-before-write/07-three-step-flow.png)

この制約にはトレードオフがあります。診断後に安全な行だけ自動適用するところまでは一度に完了できません。しかし、「診断結果が正しいか」と「適用が安全か」を別リリースで検証できます。

## 8. JSONとHTMLを同じreportから生成する

診断結果をCLIログだけにすると、人間には読めても再利用しにくい。JSONだけにすると、非エンジニアが確認しにくい。そこで二つを同じreport objectから作りました。

```js
await fs.writeFile(
  path.join(outputDir, 'report.json'),
  `${JSON.stringify(report, null, 2)}\n`,
  'utf8',
);

await fs.writeFile(
  path.join(outputDir, 'report.html'),
  renderDiagnosisHtml(report),
  'utf8',
);
```

ブラウザ版でも同じ `renderDiagnosisHtml(report)` を使ってダウンロードできます。Blob URLの作成・解放には `URL.createObjectURL()` と `URL.revokeObjectURL()` を使っています。MDNは前者がBlob等を指すobject URLを生成し、不要になったURLはrevokeすることを説明しています。
https://developer.mozilla.org/en-US/docs/Web/API/URL/createObjectURL_static

この図で見るべき点は、JSONとHTMLが別々の判定処理ではなく、一つのreportの投影であることです。

![JSONとHTML](/images/csv-migration-dry-run-before-write/08-json-html-output.png)

## 9. 失敗しやすいケースを回帰テストへ入れる

正常系だけをテストすると、「新規Workが作れそう」という確認しかできません。移行で本当に怖いのは衝突系です。

今回のテストでは少なくとも次を一つのfixtureで確認しています。

- 既存ISBN → `existing_holding`
- 新しい書名 → `safe_new_work`
- 不正ISBN + 書名なし → `invalid_isbn` + `insufficient_metadata`
- 同一入力内重複 → `duplicate_in_batch`

この図では、成功ケースよりBLOCKケースの方が多い点を見ます。migration diagnosisは「通す機能」ではなく「止める理由を説明する機能」だからです。

![テストマトリクス](/images/csv-migration-dry-run-before-write/09-test-matrix.png)

## 10. 失敗：ブラウザUIだけ別実装にすると何が起きるか

ブラウザUI追加時に最も避けたかったのは、CLIの判定結果を画面側で再現することでした。

たとえばUI側に次のようなコードを書けば、一見動きます。

```js
if (!isbn) {
  // 新規本として扱う
}
```

しかし本番側では「ISBNなし + 正規化書名が既存Workと一致」を別判定にしている可能性があります。UI独自ロジックは、その瞬間から二つ目の仕様になります。

今回の実装では、`migration.js` が `parseCsv`, `diagnoseMigration`, `renderDiagnosisHtml` をimportしています。これにより、UIは入力・表示・downloadに集中し、意味判定を持ちません。

ブラウザ版実装:
https://github.com/KAFKA2306/books/commit/9f83eb07b126d2236e79246b92cc27df1417e2e2

## 11. 再現方法

同じパターンを別システムへ移す場合、最小構成は次の通りです。

### Step 1: 本番書き込み前のprecheckを関数化する

```js
function precheckCandidates(candidates, canonical) {
  // normalize / validate / lookup / decide
  // ここでは canonical を変更しない
}
```

### Step 2: migration adapterでreason codeへ写像する

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

### Step 3: 非破壊性をテストする

```js
const before = JSON.stringify(canonical);
diagnoseMigration(rows, canonical);
assert.equal(JSON.stringify(canonical), before);
```

### Step 4: CLIとBrowserから同じ関数を呼ぶ

CLIはファイルI/O、Browserは `File.text()` とDOM描画だけを担当させます。

### Step 5: report schemaを固定する

最低限、次を機械可読にします。

```json
{
  "schema_version": 1,
  "mode": "dry-run",
  "catalog_mutated": false,
  "summary": {},
  "results": []
}
```

この図で見るべき点は、個別ライブラリ固有の実装より、別システムへ持ち出せる4つの境界です。

![再利用できる設計原則](/images/csv-migration-dry-run-before-write/10-takeaways.png)

## 12. この設計が向く場面と向かない場面

向いているのは、既存データとの照合が必要で、入力行ごとに「自動適用可能 / 要確認 / 拒否」の意味判定がある移行です。

例:

- CRMの顧客CSV取り込み
- 書誌・商品マスタ統合
- 旧システムからのアカウント移行
- 設備台帳・資産台帳の初期投入
- 設定ファイルのschema migration

一方で、dry-runだけでは解決しない問題もあります。

- 書き込み時のtransaction競合
- 診断後から適用前までにcanonicalが変化するTOCTOU
- 数百万行規模でブラウザメモリに収まらない入力
- server-side secretが必要な照合
- 実際の副作用まで含めないと検証できない外部API migration

この場合は、diagnosis reportにcanonical revision/hashを持たせ、apply時に同じrevisionであることを確認する、あるいはstaging transactionへ進める設計が必要です。

## 13. まとめ

最初は「CSVをimportできるようにする」が課題に見えました。しかし実装を分解すると、先に必要だったのはimporterではなく、**同じ本番ルールを使って、書き込まずに判断理由を返す仕組み**でした。

この設計から持ち帰れる原則は4つです。

1. 判定と副作用を分離する
2. CLI・UIで判定コアを共有する
3. 人間向け文言ではなくreason codeを契約にする
4. 非破壊性はフラグではなくbefore/afterテストで固定する

移行処理を安全にする最短手は、rollbackを豪華にすることではありません。**適用前に「何をする予定か」を本番と同じ規則で説明できる段階を作ること**です。
