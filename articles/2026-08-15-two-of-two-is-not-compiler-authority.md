---
title: "Oxlintは2/2でtscと同点。それでもtscを消さなかった"
emoji: "🧪"
type: "tech"
topics: ["typescript", "oxlint", "ci", "testing", "tooling"]
published: false
---

Oxlint `typeCheck`と`tsc`に同じ型failureを当てたら、両方 **2/2**。clean blocking false positiveも **0** だった。

しかもOxlint公式は、`--type-aware --type-check`で独立した`tsc --noEmit` stepを置き換える例まで示している。

それでも私は`tsc`を消さなかった。

理由は1つ。**実repoで、置換に使うOxlint `--type-check`そのものがNOT_RUNだった。**

2 commandを1 commandへ減らすのは魅力的だ。だが、未確認をPASS扱いしてまで小さくすると、それは最適化ではなく賭けになる。

この記事では「新toolをいつ採用するか」ではなく、**古いgateをいつ安全に消せるか**を決める。

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

新toolを追加する前に、旧gateを削除できる条件を決めておく。

1. **同じ責務** — 旧gateが担うfailure classを公式に持つ
2. **fixed correctness** — repoで重要なfaultをclean baseline付きで通す
3. **real-repo parity** — replacementに使う同じsurfaceを実repoで走らせる
4. **config coverage** — 必要なtsconfig / diagnostic surfaceの欠落がない
5. **stability acceptance** — feature statusをblocking authorityとして受け入れられる
6. **actual deletion** — 条件達成後は旧gateを消し、二重authorityを常設しない

6まで行って初めて、tool consolidationがtool accumulationではなくなる。

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