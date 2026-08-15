---
title: "公式が『tscを置き換えられる』と言っても、CI gateはまだ消せない"
emoji: "🧪"
type: "tech"
topics: ["typescript", "oxlint", "ci", "testing", "tooling"]
published: false
---

CIのtoolを統合するとき、難しいのは新しいcommandを足すことではない。**古いgateを安全に消せるか判断すること**だ。

2026年8月15日時点のOxlint公式ドキュメントには、`--type-aware --type-check`について、独立した`tsc --noEmit` stepを置き換えられると書かれている。

https://oxc.rs/docs/guide/usage/linter/type-aware

ところが同じ公式ドキュメント群は、`options.typeCheck`を**experimental type checking**とも明記している。

https://oxc.rs/docs/guide/usage/linter/config-file-reference

では、既存の`tsc --noEmit`をいつ削除してよいのか。

私は先に固定したTypeScriptの型failure 2件で、`tsc`とOxlint `typeCheck`を同じground truthへ当てた。結果は両方2/2、clean baselineのblocking false positiveも0だった。

それでも`tsc`削除を結論にしなかった。

この小さな実験で見えたのは、**correctness parityはreplacement authorizationではない**ということだった。

## 最初の予想は「同点なら統合候補」だった

modern toolchainでは、1つのbinaryがlint、type-aware lint、compiler diagnosticsまで持つようになっている。Oxlintも現在、通常lintとは別に`--type-aware`と`--type-check`を提供している。

移行案は自然にこう見える。

```text
before
  oxlint
  tsc --noEmit

after
  oxlint --type-aware --type-check
```

commandが1本減り、CI設定も単純になる。

だから最初に確認したのは「新しいsurfaceが、既存compiler gateで止めていた既知failureを止められるか」だった。

## 2つのroot faultでは、両方2/2だった

比較前にmutantを固定し、1 mutant = 1 root faultとして数えた。raw diagnostic数はdefect数として合算していない。

| candidate | in-scope type mutants | detected | clean blocking FP |
|---|---:|---:|---:|
| `tsc` | 2 | 2 | 0 |
| Oxlint `typeCheck` | 2 | 2 | 0 |

controlled summary:
https://github.com/KAFKA2306/articles/blob/81848adca34e077835735a1f8586c6e8cd8cd511/benchmarks/verification-stack-v2/results/controlled/summary.json

protocol:
https://github.com/KAFKA2306/articles/blob/81848adca34e077835735a1f8586c6e8cd8cd511/benchmarks/verification-stack-v2/PROTOCOL.md

この結果から言えるのは狭い。

- 固定した2つの型failureは両方が検出した
- clean baselineでは両方ともblocking false positiveが0だった
- 少なくともこのcorpusではOxlint `typeCheck`を「型failureを検出できない」とは言えない

逆に、**TypeScript compiler conformance全体が同等**とは言えない。2 mutantを全言語機能へ外挿する証拠はない。

## ここで公式仕様が判断を難しくする

TypeScriptの`noEmit`は、JavaScript等を出力せずにtype checkingを行う用途を公式に持つ。

https://www.typescriptlang.org/tsconfig/noEmit.html

Oxlintの現行公式ドキュメントは、type-aware lintingとtype checkingを分けている。`--type-aware`は型情報を必要とするlint ruleを有効にし、`--type-check`はTypeScript compiler diagnosticsを追加する。

https://oxc.rs/docs/guide/usage/linter/type-aware

そして同じページは、`--type-aware --type-check`によって独立した`tsc --noEmit` stepを置き換える例を示す。一方、configuration referenceとCLI referenceでは`--type-check` / `options.typeCheck`をexperimentalと明記している。

https://oxc.rs/docs/guide/usage/linter/config-file-reference
https://oxc.rs/docs/guide/usage/linter/cli.html

これは矛盾として処理する必要はない。

「置換できる」はcapabilityの説明であり、「自分のrepositoryでdefault blocking authorityとして今すぐ置換してよい」はadoption decisionだからだ。

## real repoで未実行なら、2/2を削除許可へ昇格しない

このbenchmarkにはfrozen real-repository probeもある。ただしreal repoは完全なdefect ground truthがないため、recallやfalse-positive rateの証明には使っていない。見るのはexecution compatibility、diagnosticの実用性、latency、migration frictionなどである。

external summary:
https://github.com/KAFKA2306/articles/blob/81848adca34e077835735a1f8586c6e8cd8cd511/benchmarks/verification-stack-v2/results/external/summary.json

ここで重要なのは、frozen probeでは`tsc`と通常の`oxlint`は実行したが、**Oxlint `--type-check`そのものはexternal-validity未検証**だったことだ。

したがって証拠はこう分かれる。

```text
controlled correctness
  Oxlint typeCheck: 2/2
  tsc:              2/2

real-repo compatibility
  tsc:              observed
  Oxlint typeCheck: NOT_RUN
```

`NOT_RUN`をPASSへ読み替えない限り、ここから`tsc`削除までは進めない。

## 同じ証拠から3つの物語を潰す

### 1. 「Oxlint typeCheckは不正確だからtscを残す」

棄却した。

今回の固定2 mutantでは2/2だった。不正確さを示す観測ではない。

### 2. 「公式がreplacement例を出していて2/2だからtscを消す」

棄却した。

2件はcompiler conformance全体ではなく、real repoでは`--type-check`自体がNOT_RUNで、公式statusもexperimentalである。capability確認とdefault-authority移行を混同している。

### 3. 「旧gate削除には、parityとは別のreplacement contractが要る」

これだけが残る。

この命題なら、今回の2/2、external-validityの空欄、現行公式statusを同時に説明できる。

## migrationは「追加」ではなく「削除条件」を先に書く

新tool導入時にありがちな順序はこうだ。

```text
1. new toolを追加
2. CIがgreen
3. しばらく二重実行
4. いつ消せるか分からず両方残る
```

これではtool consolidationがtool accumulationになる。

先にreplacement contractを書く。

```text
1. 旧gateが所有するfailure classを列挙
2. clean baseline + 固定mutantでchallengerを照合
3. real repoでchallengerの同じsurfaceを実行
4. 必要なconfig / diagnostic surfaceを照合
5. stability boundaryを受け入れられるか決める
6. 全条件PASSなら旧gateを削除
```

ポイントは、**新toolを採用できる条件ではなく、旧toolを削除できる条件**を定義することだ。

## 6問だけ持ち帰ればよい

既存CI gateを消す前に、次を確認する。

1. 新toolの公式責務は旧gateと本当に同じか
2. repo固有の重要failureをclean baseline付きで通したか
3. real repoでreplacementに使う**同じsurface**を実行したか
4. 必要なconfig / diagnostic / language surfaceに欠落はないか
5. feature statusはdefault blocking authorityとして受け入れられるか
6. 条件を満たしたら二重authorityを残さず旧gateを削除できるか

この6問はOxlint固有ではない。formatter、linter、type checker、hook runner、workspace orchestratorを統合するときにも使える。

たとえばRuffはformatterとlinterを同じCLIに持つが、公式にも両者は独立して利用でき、formatterはimport sortingを行わない。binaryが同じでもauthority surfaceは同じではない。

https://docs.astral.sh/ruff/formatter/
https://docs.astral.sh/ruff/linter/

同様に、TypeScriptの型はcompile後にeraseされ、runtime behaviorを型によって変えない。compiler gateを統合しても、外部入力のruntime validationまで消えるわけではない。

https://www.typescriptlang.org/docs/handbook/typescript-from-scratch.html
https://zod.dev/

## 何を測っていないか

この記事は次を証明していない。

- Oxlint `typeCheck`と`tsc`の一般的なaccuracy parity
- 全`tsconfig` option / TypeScript language featureのcompatibility
- Oxlint `typeCheck`のreal-repo compatibility
- repo-local cold/warm timingの優劣
- Oxlintが将来もexperimentalであること

特に最後は変わり得る。Oxlint公式がtype checkingをstableなdefault-authority候補へ昇格し、重要failure corpusとreal-repo probeで同じsurfaceが通れば、この記事の「今は`tsc`を消さない」という判断は反転する。

## 結論

今回、Oxlint `typeCheck`は固定2 mutantで`tsc`と同じ2/2だった。だから「新しいtoolだから信用しない」という結論にはしない。

一方、公式がreplacement例を示していても、experimental statusとreal-repo NOT_RUNを無視して旧gateを削除する根拠にもならない。

**parityはchallengerになる条件であって、authorityを移す許可ではない。**

CIを統合するときは「何を追加するか」より先に、「何が確認できたら古いgateを消すか」を契約にする。そうすれば、toolchainを安全に減らせる。