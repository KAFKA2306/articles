---
title: "壊れたrepoではlintを足す前に順序を決める。precheckを依存関係で設計する"
emoji: "🧪"
type: "tech"
topics: ["python", "githubactions", "ruff", "ci"]
published: false
---

CIが壊れたrepositoryにlintとtype checkerを足すと、短時間で数百〜数千件のdiagnosticが出ることがある。

問題は、**その件数をそのまま独立した欠陥数として扱えない**ことだ。

2026年8月15日に `KAFKA2306/DeepCode` の固定commitへ Ruff、Pyrefly、ty、pre-commit、prek をGitHub Actionsから当てたところ、Ruffは1,076件、Pyreflyは723件を報告した。しかしPyreflyの723件中508件は`parse-error`で、Ruff側にも508件の`invalid-syntax`があった。

つまり「1,076 + 723 = 1,799件の別々の問題」ではない。壊れた構文が後段の解析へ伝播していた。

一次情報:

- 実験PR: https://github.com/KAFKA2306/articles/pull/115
- 実験run: https://github.com/KAFKA2306/articles/actions/runs/31812751114
- 対象commit: https://github.com/KAFKA2306/DeepCode/commit/088059855d2c9187c51d674db02a06f70c37f087
- Ruff公式: https://docs.astral.sh/ruff/linter/
- Pyrefly公式設定: https://pyrefly.org/en/docs/configuration/
- prek互換性: https://prek.j178.dev/compatibility/

この記事ではツールの優劣ではなく、**壊れたrepositoryを最短で診断するためのprecheck順序**を扱う。

## 問題: diagnosticの総数は修正順を教えてくれない

実験の最初の観測値は次だった。

| tool | version | scan観測値 | 主な出力 |
|---|---:|---:|---:|
| Ruff | 0.16.3 | 99 ms | 1,076 findings |
| Pyrefly | 1.2.0 | 361 ms | 723 findings |
| ty | 0.0.71 | 264 ms | 952 concise lines |
| prek | 0.4.11 | 2,326 ms | existing hooks, exit 1 |
| pre-commit | 4.6.2 | 8,765 ms | existing hooks, exit 1 |

これは1回のGitHub Actions観測であり、jobは別々のhosted runner VMで動いた。そのため速度差を一般性能比としては扱わない。

重要なのは件数の中身だった。

Ruffの上位分類は次の通りだった。

```text
invalid-syntax  508
UP006           147
BLE001          143
I001             44
RUF010           42
```

Pyrefly 723件の内訳は次だった。

```text
parse-error         508
unknown-name        108
missing-import       86
invalid-syntax       12
unexpected-keyword    9
```

最大categoryが両方508件だった。

## 原因: 後段の診断は前段の状態に依存する

static analyzerやtype checkerは、入力programを正しくparseできることを前提にする。

構文が壊れていると、後段の名前解決やimport解決、型解析にも派生diagnosticが出る。

今回のPyreflyでは723件のうち508件が`parse-error`だった。さらに86件の`missing-import`はdependencyを入れていないDiscovery環境で得た値なので、repository固有の型欠陥だけを表しているとは言えない。

したがって、次の表示は危険だ。

```text
Ruff:    1076 errors
Pyrefly:  723 errors
Total:   1799 errors
```

この合計値には、同じroot failureから派生したdiagnosticが混ざる。

## 設計判断: 横並びではなくgateの依存順を決める

壊れたrepository向けには、precheckを次の順序で扱う。

```text
Gate 1  parse / syntax
   ↓ PASS
Gate 2  formatter + lint
   ↓ PASS
Gate 3  dependency / import context
   ↓ PASS
Gate 4  static type check
   ↓ PASS
Gate 5  runtime schema / fixture validation
   ↓ PASS
Gate 6  tests / integration / heavier CI
```

後段を完全に実行停止する必要はない。調査目的なら並列実行してもよい。

ただし結果の意味を分ける。

```text
BLOCKING ROOT FAILURE
  syntax: 508

DOWNSTREAM / LOWER-CONFIDENCE
  unknown-name: 108
  missing-import: 86
```

前段が壊れている間、後段diagnosticを独立欠陥数としてKPI化しない。

## 代替案: 全部並列に走らせる

全toolを最初から並列に走らせる設計にも利点はある。

- wall-clock timeを短くできる
- raw evidenceを一度に保存できる
- 前段failureが後段へどう伝播したかを比較できる

今回の実験でも実際にそうした。

ただし、それは**観測方法**として有効なのであって、**修正優先順位**まで横並びにする理由にはならない。

CIのUIやAI agentへの返却ではroot failureとdownstream diagnosticを区別した方がよい。

## 実装: まず固定commitを別directoryへcheckoutする

再現可能にするため、対象repositoryをbranch名ではなくcommit SHAで固定した。

説明用workflow stagesは次の形になる。

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Checkout frozen target
    uses: actions/checkout@v4
    with:
      repository: KAFKA2306/DeepCode
      ref: 088059855d2c9187c51d674db02a06f70c37f087
      path: target
      persist-credentials: false

  - name: Ruff discovery
    run: uvx ruff check --no-cache --output-format=json target

  - name: Pyrefly discovery
    working-directory: target
    run: uvx pyrefly check --output-format json
```

Ruff公式では`ruff check`がlinterのprimary entrypointで、directoryを与えた場合はPython fileを再帰探索する。Pyreflyは`--output-format json`を設定できる。

machine-readable outputを保存すると、件数だけでなくcategoryの重なりを後から検証できる。

## 実例: 508件を「2つのtoolが見つけた1,016件」と数えない

今回の入力は同一commitだった。

```text
KAFKA2306/DeepCode
088059855d2c9187c51d674db02a06f70c37f087
```

Ruff:

```text
invalid-syntax = 508
```

Pyrefly:

```text
parse-error = 508
```

この時点で「RuffとPyreflyは補完的だから計1,016件のsyntax/type問題」という説明は捨てた。

改善後は次の解釈にした。

```text
root syntax failure surface: 508
additional downstream observations:
  unknown-name: 108
  missing-import: 86
  invalid-syntax: 12
  unexpected-keyword: 9
```

同じroot failureを複数toolが観測した可能性を残したまま、後段を低confidenceとして扱う。

## pre-commitからprekへの置換は「速度」よりpatch一致を確認する

対象repoには既存`.pre-commit-config.yaml`があった。

同じ設定を`pre-commit 4.6.2`と`prek 0.4.11`で実行した結果、今回のfixtureでは生成されたworking-tree patchのSHA-256が一致した。

```text
pre-commit patch
30275602cf6b35644199d3a7fe949c038a10eaa9e6685074de4f7c8d62b36bf1

prek patch
30275602cf6b35644199d3a7fe949c038a10eaa9e6685074de4f7c8d62b36bf1
```

prek公式も、既存`.pre-commit-config.yaml`をそのまま使う実用的なdrop-in replacementを目標としている。

一方、scan観測値はpre-commit 8,765 ms、prek 2,326 msだったが、別runner VMでの単発値なので「常に何倍速い」とは結論しない。

移行検証では速度だけでなく、**同じ入力とconfigから同じpatchを作るか**を確認すると安全側になる。

## 検証: 何を証拠として残すか

最低限、各toolについて次をartifactへ残す。

```text
tool version
target commit SHA
exit code
raw machine-readable output
working tree status
diff
diff SHA-256
runner / runtime metadata
```

これがあれば、後から次を確認できる。

- 件数が同じroot failureに由来していないか
- tool変更でpatchが変わっていないか
- dependency不足によるdiagnosticを混ぜていないか
- 単発timingを一般化していないか

## 失敗と学び

最初の仮説は「高速なlintとtype checkerを複数積めば、短時間で広い故障面を得られる」だった。

実測後は変わった。

**tool数や総diagnostic数より、diagnosticの依存関係を設計した方が実務で使いやすい。**

構文とenvironmentが壊れたまま、後段の件数をrepository品質の直接指標にしてはいけない。

## 再現方法

自分のrepositoryで試す場合は次の順でよい。

1. 対象commit SHAを固定する
2. sourceを変更せずRuff等のsyntax/lint出力をJSONで保存する
3. type checkerのmachine-readable outputも保存する
4. category別件数を集計する
5. 同じfile・同じsyntax failureに由来するdiagnosticを確認する
6. syntax修復前後でtype checkerを再実行する
7. dependency install前後でも差分を取る

評価するKPIは「総diagnostic数」ではなく、**前段を1つ直したときに後段の何件が消えるか**にする。

## 今回言える範囲

この実験から確認できたのは次だけだ。

- 固定したDeepCode commitでRuff 0.16.3は1,076 findingsを返した
- 同じcommitでPyrefly 1.2.0は723 findingsを返した
- Pyreflyの723件中508件は`parse-error`だった
- Ruffにも508件の`invalid-syntax`があった
- 1,076 + 723を独立欠陥数として扱えない
- 同じ`.pre-commit-config.yaml`を実行したpre-commitとprekは、このfixtureで同一SHA-256のpatchを生成した
- timingは単発・別runner観測なので一般性能比には使わない

Pydantic、Biome、Oxlint、`tsc --noEmit`、Zodはこの実験では測っていない。これらについて性能や検出力の比較結果はこの記事では主張しない。

壊れたrepositoryのprecheckで最初に必要なのは、最強tool一覧ではない。

**「どのfailureを先に直すと、後段のdiagnosticが信頼できるようになるか」をCIの構造として表現すること**だ。
