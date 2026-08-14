---
title: "CSVを入れる前に「この1行が何になるか」を全部見せる。壊さない移行UXを作った"
emoji: "🧪"
type: "tech"
topics: ["javascript", "dataengineering", "testing", "privacy"]
published: false
published_at: 2026-08-12 12:30
---

同じ本について、手元の記録にこんな4行があったとする。

```text
1984 / Kindle
1984 新訳版 / 購入済み
一九八四年 / 紙
サンプル: 1984
```

人間なら、全部を別の本だとは思わない。

「同じ作品かもしれない」

「版が違うかもしれない」

「実際に持っているものと、単なるメモが混ざっているかもしれない」

と読む。

しかしCSV importerは、そこまで気を利かせてくれない。

読み込める4行なら、そのまま4件として登録できてしまう。

私が欲しかったのは、importボタンではなかった。

**書き込む前に、この1行が既存データへどう扱われる予定なのかを全部見せる画面**だった。

今回のケーススタディは `KAFKA2306/books` という本棚データベースである。

このDBでは、

- Work = 作品
- Edition = 版・形式
- Holding = 実際の所蔵

を分けている。

だから同じCSVでも、行ごとに意味が違う。

```text
既に持っている
新しい版として追加できる
完全に新しい作品
情報不足
ISBN不正
同じCSV内で重複
似たタイトルがあり人間確認が必要
```

これを成功 / 失敗の2値へ潰したくなかった。

そこで最初に作ったのはimporterではなく、**正準catalogを一切変更せず、「この行なら何をする予定か」と理由だけを返すdry-run診断**だった。

- 実装・テスト: https://github.com/KAFKA2306/books/commit/e9dbe8c968f17dd3626d9488a3fcb269fdbaaecc
- Browser版: https://github.com/KAFKA2306/books/pull/43

この記事で扱うのはCSV parsingの方法ではない。

**大切なデータへ書き込む前に、利用者が変更予定を理解し、危ない行だけ止められる移行体験をどう作るか**である。

## importerより先に「予定表」を作った

典型的なimporterは、次の責務を一度に持ちやすい。

```text
parse
→ normalize
→ validate
→ existing dataを検索
→ actionを決める
→ canonical dataへ書き込む
→ 結果を返す
```

問題は、`actionを決める` と `書き込む` が近すぎることだ。

途中で「このISBNは既存Holdingだった」「タイトルが既存Workに似ている」と分かっても、その時点ではもう副作用と向き合う必要がある。

- rollbackするのか
- 部分成功を許すのか
- 再実行したら重複しないか
- 人間確認が必要な行だけどう戻すのか

そこでMVPでは、書き込みを消した。

```text
parse
→ normalize
→ precheck
→ diagnose
→ report

# canonical mutationなし
```

この時点で、利用者ができることは3つだけである。

1. CSVを選ぶ
2. 診断する
3. JSON / HTML reportを保存する

**「適用する」ボタンは作らなかった。**

機能不足ではある。

しかし最初のリリースで守りたかったのは、ワンクリックで全部終わることではなく、**何が起きるか分からないまま正準データが変わらないこと**だった。

## 同じ4行でも、返すべきなのは4つの理由

回帰テストでは、同じ診断関数へ次の入力を渡している。

```js
[
  { title: '赤毛のアン', isbn: '9784102113417' },
  { title: '新しい本', isbn: '' },
  { title: '', isbn: '1234' },
  { title: '新しい本', isbn: '' },
]
```

期待する結果は単なる `success: true/false` ではない。

例えば、

```text
existing_holding
safe_new_work
invalid_isbn
insufficient_metadata
duplicate_in_batch
```

のようなreason codeを返す。

実装には少なくとも次がある。

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

ここで重要なのは、人間向けのエラーメッセージを契約にしないことだ。

UIには、

> この本はすでに所蔵済みです

と表示してもいい。

しかしmachine-readableな結果は `existing_holding` に固定する。

そうすると、

- HTMLでは人間に分かりやすく見せる
- JSONでは件数を集計する
- 後でsafeだけapplyする
- reviewだけ人間へ回す

といった用途へ分岐できる。

**利用者への説明と、システムの判断契約を分けられる。**

## 一番重要だったのは、migration専用ロジックを作らなかったこと

移行機能だから、migration専用validatorを作る案は自然だった。

しかし、それを採ると別の問題が始まる。

通常登録では「既存Holding」なのに、CSV移行では「新規Edition」と判定する。

CLIではreviewなのに、browserではsafeになる。

入力経路によって正解が変わる。

これが一番避けたかった。

そこでmigration側は、既存の `precheckCandidates` を再利用するadapterにした。

```text
CLI ───────┐
           ├─> diagnoseMigration()
Browser ───┘
                 ↓
          precheckCandidates()
```

CLIもBrowserも、意味判定を持たない。

入力方法と表示方法だけが違い、**「このデータをどう扱うか」の正解は1か所だけ**に置く。

これはdry-runを作った副産物ではなく、むしろ大きな価値だった。

importerを急いで作らなかったから、後からUIを増やしても判定ロジックを複製せずに済んだ。

## ブラウザ版では、CSVをアップロードしない

CSVには購入履歴や管理情報が含まれることがある。

診断するだけなのに、いったんサーバへアップロードする必要はなかった。

Browser版では、

1. ユーザーが選んだCSVを `File.text()` でbrowser memoryへ読む
2. 公開済みの `api/v1/catalog.json` だけを取得する
3. browser内で `diagnoseMigration()` を実行する

という境界にした。

```js
const [text, response] = await Promise.all([
  fileInput.files[0].text(),
  fetch('./api/v1/catalog.json', { cache: 'no-store' }),
]);

const rows = parseCsv(text);
const catalog = await response.json();
currentReport = diagnoseMigration(rows, catalog);
```

選択CSVを送信するupload APIはない。

PR #43でも、`selected CSV in browser memory only`、`user file is never uploaded` を設計境界としている。

https://github.com/KAFKA2306/books/pull/43

これはセキュリティ機能を増やしたというより、**そもそも送らなくてよいデータを送らない**というUX判断である。

利用者は「診断するために、自分のCSVをどこかへ預ける」必要がない。

## `catalog_mutated: false` と書くだけでは信用しない

reportには、

```json
{
  "mode": "dry-run",
  "catalog_mutated": false
}
```

を含めている。

しかし、このフラグは自己申告でしかない。

内部でcatalogを書き換えてから `false` を返すバグも作れる。

そこでテストはbefore/afterを比較する。

```js
const before = JSON.stringify(catalog);
const report = diagnoseMigration(rows, catalog);

assert.equal(report.mode, 'dry-run');
assert.equal(report.catalog_mutated, false);
assert.equal(JSON.stringify(catalog), before);
```

重要なのは、**「壊しません」と書くことではなく、本当に同じデータが残ったことを検証すること**だ。

この違いは、移行機能を人に使ってもらうときの信頼に直結する。

## 診断reportは、人と機械の両方が使える形にする

CLIログだけなら開発者は読める。

JSONだけなら後段処理はしやすい。

しかし実際の移行では、エンジニア以外が内容を確認することもある。

そこで一つのreport objectから、

- JSON
- HTML

を生成する。

```text
同じ診断結果
   ├─ JSON → CI / 集計 / 自動処理
   └─ HTML → 人間レビュー
```

判定は一度だけ行う。

表示形式ごとに再判定しない。

これも「正解を1つにする」ための設計である。

## この移行UXで、利用者が先に知りたいこと

importerの内部実装より、利用者が知りたいのは次の方だと思う。

| 入力行 | 予定action | 理由 | 自動適用 |
|---|---|---|---|
| ISBN既存 | 変更なし | `existing_holding` | no-op |
| 新規ISBN + 既存Work | Edition追加候補 | `safe_new_edition` | 候補 |
| 新規title | Work追加候補 | `safe_new_work` | 候補 |
| 類似title | 保留 | `review_similar_title` | 人間確認 |
| ISBN不正 | 拒否 | `invalid_isbn` | 不可 |

**「何件成功したか」より、「この行に何が起きるか」が分かる方が重要**である。

特に既存データへ追加するmigrationでは、件数だけのsummaryは安心材料になりにくい。

## dry-runだけでは解決しないこともある

この設計は、書き込み前の意味判定を安全にする。

しかし、実際にapplyするときには別の問題が残る。

- 診断後にcanonicalが更新されるTOCTOU
- transaction競合
- 外部APIへの副作用
- 大規模CSVのmemory制約
- server-side secretが必要な照合

したがって次の段階では、diagnosis reportへcanonical revision/hashを持たせ、apply時に同じrevisionであることを確認する、といった設計が必要になる。

**dry-runは完成したmigrationではない。**

その代わり、applyを作る前に「判断ルールが正しいか」を独立して検証できる。

## 別システムへ持ち出すなら、5つだけ真似すればいい

CRM、設備台帳、商品マスタ、アカウント移行などでも、同じ考え方は使える。

最初から大きなmigration frameworkを作る必要はない。

### 1. 本番判定を副作用なしの関数へ切る

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

### 3. reason codeを固定する

人向け文言とmachine contractを分ける。

### 4. before/afterで非破壊性をテストする

自己申告ではなく状態で検証する。

### 5. CLIとUIで同じ診断coreを使う

入力・表示だけをadapterにする。

この5つがあれば、少なくとも「書き込むまで何が起きるか分からない」状態からは抜けられる。

## importerを作る前に、利用者へ約束するものを変えた

最初の課題は「CSVを取り込めるようにする」だった。

しかし実際に欲しかった体験を言い直すと、違った。

> **自分のデータを壊さず、送らず、書き込む前に、どの行がどう扱われるか分かる。**

この約束を先に置くと、実装順も変わった。

importerではなくdiagnosis。

applyではなくreport。

UI独自判定ではなくshared core。

「成功しました」ではなくreason code。

rollbackを豪華にするより先に、**適用前に何をする予定かを本番と同じ規則で説明できること**を作った。

移行処理を安心して使えるようにするには、その順番の方が効いた。
