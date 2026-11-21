---
title: "未実行を合格と呼ぶな。旧検査を消す前の条件"
emoji: "🧪"
type: "tech"
topics: ["typescript", "oxlint", "ci", "testing", "tooling"]
published: false
---

**新しい検査が2/2を出しても、古い検査を消す理由にはならない。**

OxlintのtypeCheckと`tsc`は、固定した二つの型エラーをどちらも検出した。誤検知は0。しかし実際のリポジトリで、置換に使うOxlint `--type-check`の実行状態は **NOT_RUN** だった。公式資料に置換例があっても、このrepoで旧検査と同じ範囲を守った証拠にはならない。

ここでの汎用規律は **「新方式が旧方式の重要な仕事を代替したと実証するまで、旧方式を削除するな」**。未実行をPASSに変えると、最も大切な失敗の検出を見逃したまま構成を軽量化できてしまう。

## controlled fixtureでは同点だった

| candidate | fixed type faults | detected | clean blocking FP |
|---|---:|---:|---:|
| `tsc` | 2 | 2/2 | 0 |
| Oxlint `typeCheck` | 2 | 2/2 | 0 |

controlled evidence:
https://github.com/KAFKA2306/articles/blob/81848adca34e077835735a1f8586c6e8cd8cd511/benchmarks/verification-stack-v2/results/controlled/summary.json

この2件については、Oxlint `typeCheck`を「検出できないから残せない」とは言えない。

一方で、2件はTypeScript全体のconformanceではない。correctness parityの小さな証拠を、そのままreplacement authorizationへ昇格させることもできない。

## 公式の「置換できる」と、自分のrepoで「消してよい」は別

Oxlint公式はtype checkingを提供し、独立した`tsc --noEmit`を置換できる例を示す。一方、CLI/config referenceでは`--type-check` / `options.typeCheck`を**experimental type checking**と明記している。

- https://oxc.rs/docs/guide/usage/linter/type-aware
- https://oxc.rs/docs/guide/usage/linter/cli.html
- https://oxc.rs/docs/guide/usage/linter/config-file-reference

TypeScript側では`noEmit`が、出力せずtype checkingする公式surfaceとして存在する。

https://www.typescriptlang.org/tsconfig/noEmit.html

つまりcapabilityは確認できても、自分のrepoのrequired surfaceまで同等かは別に確認する必要がある。

## 今回止めたのはreal-repoの空欄だった

frozen real-repository evidenceでは、`tsc`と通常のOxlintは観測済みだったが、replacementで使いたいOxlint `--type-check`自体は **NOT_RUN** だった。

https://github.com/KAFKA2306/articles/blob/81848adca34e077835735a1f8586c6e8cd8cd511/benchmarks/verification-stack-v2/results/external/summary.json

```text
controlled fixture
  tsc:              2/2
  Oxlint typeCheck: 2/2

real repo / same surface
  tsc:              observed
  Oxlint typeCheck: NOT_RUN
```

この状態で2→1へ削ると、「同等だから簡素化した」ではなく「未確認のsurfaceへauthorityを移した」になる。

## 削除条件を先に6つ書く

型チェックを一本化するときは、現行CIの `tsc --noEmit` の呼び出し、対象の `tsconfig`、正常なコミット、必ず拾いたい失敗を一件ずつ起こす変更を用意する。現行と候補を同じ入力にかけて、正常時の終了結果と、失敗時の診断を並べる。

1. **同じ責務** — 旧gateが担うfailure classを公式に持つ
2. **fixed correctness** — repoで重要なfaultをclean baseline付きで通す
3. **real-repo parity** — replacementに使う同じsurfaceを実repoで走らせる
4. **config coverage** — 必要なtsconfig / diagnostic surfaceの欠落がない
5. **stability acceptance** — feature statusをblocking authorityとして受け入れられる
6. **actual deletion** — 条件達成後は旧gateを消し、二重authorityを常設しない

候補を実リポジトリでまだ走らせていない、または必要な診断を取りこぼしたなら、現行コマンドを残す。条件を満たしたら、置換後のCIで正常・失敗の両方を確かめてから旧コマンドを外す。

## 実リポジトリで比べる4行の記録

`tsc --noEmit`を消す前に、同一コミットと同一`tsconfig`から次を実行する。表は**比較手順の例**であり、実測の追加ではない。

| 入力 | tsc | Oxlint `--type-aware --type-check` |
| --- | --- | --- |
| 正常なコード | 終了コード・診断を保存 | 終了コード・診断を保存 |
| 引数の型を一か所壊す | 非0終了と診断を確認 | 非0終了と診断を確認 |
| 戻り値の型を一か所壊す | 非0終了と診断を確認 | 非0終了と診断を確認 |
| 実repoで未実行 | 測定なしならNOT_RUN | 測定なしならNOT_RUN |

Oxlint側の対象ファイルとTypeScriptの`include`・`exclude`・`references`が違えば、2/2でも置換条件は成立しない。**NOT_RUNはPASSではない**。旧CIを消してから初めて欠落に気づくのではなく、並行して同じ失敗を検出した証拠を先に残す。[TypeScript tsconfig](https://www.typescriptlang.org/tsconfig/)

## 同等になった後のtie-breaker

機能、correctness、UI/UX、運用性が同等なら、私は次を小さい方へ寄せる。

| metric | prefer |
|---|---|
| CI commands | fewer |
| config files | fewer |
| dependencies | fewer |
| custom LOC | fewer |
| files | fewer |
| duplicate authorities | fewer |

今回の候補ならcommand数は **2 → 1** にできる可能性がある。しかしreal-repo `--type-check`が **NOT_RUN → NOT_RUN** のままなので、削減はまだ実行しない。

小ささは重要な設計品質だ。ただし、小さくするために未確認をPASSへ変換しない。

## この記事が言っていないこと

Oxlint `typeCheck`が不正確だとは言っていない。今回の2 faultでは2/2だった。また、将来もexperimentalのままだとも言っていない。

反転条件は明確だ。real repoで同じsurfaceを実行し、必要なconfig/diagnostic coverageとstability条件を満たせば、`tsc --noEmit`削除を再評価できる。

**同じ価値を出せるなら、コードも設定もcommandも少ない方がよい。そのために必要なのは、新toolの採用条件ではなく、古いgateを安全に削除できる条件である。**

## この規律を別の置換へ移すなら

監視サービス、バックアップ先、セキュリティスキャナの置換でも、「候補が一度動いた」より「旧方式が検出できた失敗を本番相当の入力で検出するか」を先に問う。これは**応用仮説**で、他分野で置換実験をした報告ではない。

同じ対象、同じ失敗・正常入力、同じ設定で代替が確認され、復旧や保守性も満たすなら旧方式は消してよい。旧gateを永久に残すのが原則ではない。**NOT_RUNとPASSを分けることが、削除へ進むための条件になる。**
