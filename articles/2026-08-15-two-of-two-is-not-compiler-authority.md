---
title: "新しいCIツールが同点でも、古いgateを消してはいけないときがある"
emoji: "🧪"
type: "tech"
topics: ["typescript", "oxlint", "ci", "testing", "tooling"]
published: false
---

新しいtoolが、既存のcompilerと同じ固定テストを全部通った。

それでも、すぐに古いgateを削除してよいとは限らない。

今回、TypeScriptの型failureを1つずつ入れた2つのmutantで、`tsc`とOxlintのtype-check機能はどちらも2/2だった。clean baselineのblocking false positiveも0だった。

ここまでは置換候補として強い証拠だ。

しかし、**「このfixtureで同点」と「CIの最終authorityを移してよい」は別の判断**である。

## 読者の本当の仕事は「追加」ではなく「安全に削除できるか」

modern toolchainでは1つのbinaryがformatter、linter、type-aware lint、compiler diagnosticsまで持つことがある。

すると移行はこう見える。

```text
before
  oxlint
  tsc --noEmit

after
  oxlint --type-aware --type-check
```

commandが減る。管理対象も減る。だが、古いgateを消すには「新しいtoolが動く」以上の証拠が必要だ。

## 今回、correctness gateは通った

固定したTypeScript type mutantでは次だった。

| candidate | in-scope type mutants | detected | clean blocking FP |
|---|---:|---:|---:|
| `tsc` | 2 | 2 | 0 |
| Oxlint `typeCheck` | 2 | 2 | 0 |

controlled summary:
https://github.com/KAFKA2306/articles/blob/81848adca34e077835735a1f8586c6e8cd8cd511/benchmarks/verification-stack-v2/results/controlled/summary.json

2件だけなのでTypeScript全体のaccuracyを示さない。それでも「この2 faultをOxlintが見逃した」とは言えなくなった。

## それでも削除しなかった理由

TypeScript公式は`noEmit`を、出力せずsourceをtype-checkする用途として説明している。

https://www.typescriptlang.org/tsconfig/noEmit.html

Oxlint公式は`--type-aware`と`--type-check`を別surfaceとして扱い、configuration referenceでは`options.typeCheck`をexperimentalとしている。

https://oxc.rs/docs/guide/usage/linter/type-aware.html
https://oxc.rs/docs/guide/usage/linter/config-file-reference

さらに今回のfrozen real-repo probeでは`tsc`と通常の`oxlint`は実行したが、Oxlintの`--type-check`自体はexternal-validity未検証だった。

https://github.com/KAFKA2306/articles/blob/81848adca34e077835735a1f8586c6e8cd8cd511/benchmarks/verification-stack-v2/results/external/summary.json

つまり、correctnessの小さなground truthでは通ったが、**default authorityを置き換えるための運用証拠はまだ揃っていなかった**。

## migrationを3段階に分ける

### 1. Candidate

公式にその責務を持つか確認する。

「型情報を使えるlinter」だからcompiler replacement候補、と推測しない。実際にcompiler diagnosticsを担当する公式surfaceを確認する。

### 2. Evidence-qualified challenger

自分のrepoで絶対に落としたくないfailure classを固定し、clean baselineとmutantの両方で比較する。

今回の2/2はここまでを支持する。

### 3. Default authority

ここで初めて旧gate削除を検討する。

最低限見るのは次だ。

- stability status
- 必要なfailure corpus
- real-repo compatibility
- config/compiler surfaceの欠落
- upgrade時のregression gate
- superseded authorityを削除できるか

## 壊れた判断

```text
new tool: 2/2
old tool: 2/2
↓
同等
↓
old gate削除
```

この推論は、2件のmutantをcompiler conformance全体へ外挿している。

## 改善した判断

```text
fixed correctness corpus PASS
        ↓
real-repo / config / statusを確認
        ↓
replacement contract PASS
        ↓
old gateを削除
```

重要なのは「新しいtoolを足せるか」ではなく、**古いauthorityを安全に消せるか**である。

## 読者向けの削除チェックリスト

既存CI gateを1本消す前に、次の6問を確認する。

1. 新toolの公式責務は旧gateと同じか
2. repo固有の重要failureをclean baseline付きで通したか
3. real repoで新しいsurfaceそのものを実行したか
4. 必要なconfig/diagnostic surfaceに欠落はないか
5. feature statusはdefault blocking authorityに適するか
6. 移行後、二重authorityを恒久化せず旧gateを削除できるか

1〜4が未確認ならreplacement以前。5がexperimentalなら、採用判断もexperimental adoptionとして限定する。

## 証拠の境界

この記事はOxlintのtype checkingが不正確だとは主張しない。今回の2 mutantではむしろ2/2だった。

主張はもっと狭い。

**correctness parityは、replacement authorizationの必要条件になり得ても十分条件ではない。**

commandを1本減らすことより、判定権限をどこまで移してよい証拠があるかを見る。

新しいtoolが同点だったときこそ、次に問うべきは「勝ったか」ではなく、**古いgateを消しても同じ安全性を説明できるか**である。