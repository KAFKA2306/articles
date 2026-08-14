<!-- pipeline_meta: {"idea_source":"public-github-engineering","idea_only":true,"raw_private_content_persisted":false,"topic":{"title":"CIが壊れたrepoに最新precheckを当てたら、0.1秒で1000件出た。でも件数比較は罠だった","audience":"GitHub ActionsやAI coding agentで複数repositoryを保守する開発者","central_question":"状態の悪いrepositoryを最短で診断するには、最新lint/type checkerを全部並べればよいのか、それとも検査順序を設計すべきか","surprising_finding":"Ruff 1,076件、Pyrefly 723件という大きな数字は独立した1,799件ではなく、Pyreflyの723件中508件がparse errorで、壊れた構文が後段の型診断を大きく汚染していた","initial_hypothesis":"RuffとPyreflyを併用すれば短時間で広く、ほぼ補完的な故障面を得られる","hypothesis_update":"壊れたrepoでは診断数を足すより、syntax→environment/import→type→runtime contractの順にgateを分け、前段failureが残る間は後段の件数を独立欠陥として扱わない方が有用","stakes":"AI agentやCIが大量diagnosticを返しても、修正順が悪ければ人間もagentもノイズ処理に時間を使う","story_type":"falsified-counting-assumption","reader_before":"CIが赤いrepositoryに複数linter/type checkerを追加したが、数百〜数千件のdiagnosticのどこから直すべきか分からない","reader_after":"precheckをsyntax→lint→type→runtime contractに段階化し、後段diagnosticが信頼できる条件を判断できる","design_philosophy":"ツール数や総diagnostic数をKPIにせず、最初に直すと後段ノイズが減るfailure boundaryを優先する。速度比較も単発runner差を一般化しない","why_this_article":"実際に壊れていた公開repositoryの固定commitへRuff/Pyrefly/ty/pre-commit/prekを同一Actions harnessから当て、raw artifactを分類した結果、見かけ上の件数加算が破綻した実測がある","proof_of_value":"KAFKA2306/DeepCode@088059855d2c9187c51d674db02a06f70c37f087、GitHub Actions run 31812751114、Ruff 1,076件、Pyrefly 723件、うちparse-error 508件、pre-commit/prekの生成patch SHA-256一致","desired_reader_action":"自分の壊れたrepoで最初にsyntax gateを独立させ、type checkerの件数を前段修復前後で比較する","non_goal":"RuffとPyreflyの優劣を件数で決めない。prekが常に約4倍速いとは主張しない。Pydantic/Biome/Oxlint/tsc/Zodはこの実験では未実測"},"public_evidence":["https://github.com/KAFKA2306/articles/pull/115","https://github.com/KAFKA2306/articles/actions/runs/31812751114","https://github.com/KAFKA2306/DeepCode/commit/088059855d2c9187c51d674db02a06f70c37f087","https://docs.astral.sh/ruff/linter/","https://pyrefly.org/en/docs/pydantic/","https://prek.j178.dev/compatibility/","https://biomejs.dev/formatter/","https://oxc.rs/docs/guide/usage/linter/type-aware.html","https://www.typescriptlang.org/tsconfig/noEmit.html","https://zod.dev/basics"]} -->

# CIが壊れたrepoに最新precheckを当てたら、0.1秒で1000件出た。でも件数比較は罠だった

CIが赤いrepositoryに新しいlinterを入れる。

すると、たくさん問題が見つかる。

さらにtype checkerを入れる。

また大量に見つかる。

数字だけを見ると、検査器を増やすほどrepositoryの故障面が詳しく見えているように思えます。

実際に状態の悪い公開repositoryへ2026年のprecheck候補を当てたところ、最初の結果はかなり派手でした。

```text
Ruff      1,076 findings
Pyrefly     723 findings
```

Ruffのscan部分は99 ms、Pyreflyは361 msでした。

「合計1,799件の問題を1秒未満で発見した」と書きたくなる数字です。

しかしraw diagnosticsを分類すると、その解釈は間違っていました。

**Pyreflyの723件のうち、508件はparse errorでした。Ruff側にも508件の`invalid-syntax`がありました。**

つまり、ツールを増やしたことで独立した問題が723件追加されたわけではありません。

壊れた構文が、後段の型検査まで大量のdiagnosticを伝播させていました。

この記事では「2026年の最強lint一覧」ではなく、**壊れたrepositoryでは何を先に直すと後段のノイズが減るのか**を、固定commitの実測から考えます。

実験:
https://github.com/KAFKA2306/articles/pull/115

GitHub Actions run:
https://github.com/KAFKA2306/articles/actions/runs/31812751114

対象commit:
https://github.com/KAFKA2306/DeepCode/commit/088059855d2c9187c51d674db02a06f70c37f087

## 「正常なrepoで何ms」はやめて、壊れたrepoをそのまま使った

速度比較だけなら、整ったsample repositoryを作る方が簡単です。

でも実際に困るのは、たいてい逆です。

- 既存CIが失敗している
- 古いlint設定が残っている
- 構文エラーがある
- importやdependencyの状態も怪しい
- 自動fixすると大量diffが出る
- どのdiagnosticを先に信用すべきか分からない

そこで、`KAFKA2306/DeepCode` の実在commitを固定して、その状態を変更せず検査しました。

対象SHAは次です。

```text
088059855d2c9187c51d674db02a06f70c37f087
```

実験側のGitHub ActionsからこのSHAをcheckoutし、各toolを別jobで実行しています。

今回のDiscovery runで使われた主なversionは次でした。

| tool | version | scan observation |
|---|---:|---:|
| Ruff | 0.16.3 | 99 ms |
| Pyrefly | 1.2.0 | 361 ms |
| ty | 0.0.71 | 264 ms |
| prek | 0.4.11 | 2,326 ms |
| pre-commit | 4.6.2 | 8,765 ms |

ここでの時間は**1回のGitHub Actions観測値**です。

jobは別々のGitHub-hosted runner VMで動いており、特に`pre-commit`と`prek`のscan区間にはhook環境準備も含まれます。したがって「一般に何倍速い」というbenchmark結論には使いません。

今回重視したのは、同じ固定commitで、何がどう壊れていると診断されたかです。

## Ruffの1,076件を分解すると、半分近くがsyntaxだった

Ruff 0.16.3は47 filesから1,076 findingsを返しました。

上位を分類するとこうなりました。

| category | count |
|---|---:|
| `invalid-syntax` | **508** |
| `UP006` | 147 |
| `BLE001` | 143 |
| `I001` | 44 |
| `RUF010` | 42 |
| `UP045` | 33 |
| `UP035` | 29 |
| `S110` | 28 |
| `ASYNC230` | 21 |

`invalid-syntax`だけで508件あります。

14 filesに集中しており、たとえば`deepcode.py`ではclosing quoteの欠落が検出されました。

```text
missing closing quote in string literal
```

この時点で重要なのは、残り568件を全部並列に直し始めないことです。

構文が壊れているfileでは、後段の解析器が正しいprogram structureを作れません。

Ruff公式でも`ruff check`はPython filesを再帰的にlintする入口として定義されています。

https://docs.astral.sh/ruff/linter/

## Pyrefly 723件は「Ruffでは見えなかった723件」ではなかった

次にPyrefly 1.2.0を同じcommitへ当てました。

raw JSONをcategory別に数えると、723件の内訳は**これで全部**でした。

| category | count |
|---|---:|
| `parse-error` | **508** |
| `unknown-name` | 108 |
| `missing-import` | 86 |
| `invalid-syntax` | 12 |
| `unexpected-keyword` | 9 |
| **total** | **723** |

ここで仮説が崩れました。

私は最初、Ruffがsource quality、Pyreflyが型整合性を見るので、両者を並べれば比較的補完的な故障面が得られると考えていました。

しかし最初のbroken-repo runでは、Pyreflyの最大categoryも508件のparse errorでした。

```text
Ruff invalid-syntax = 508
Pyrefly parse-error = 508
```

さらに86件の`missing-import`には、zero-dependencyのDiscovery環境でmoduleを解決できなかったものが含まれます。

つまり、Pyreflyの723件をすぐ「型の問題723件」と扱うのも違います。

**syntaxとenvironmentが壊れたままでは、type checkerの総件数はrepository固有の型品質だけを表していません。**

## ここでprecheckの設計を変えた

最初に考えていたのは、こんな構成でした。

```text
prek
├─ Ruff
├─ Pyrefly
├─ Pydantic
├─ Biome
├─ Oxlint
├─ tsc
└─ Zod
```

全部高速なら全部走らせればいい。

しかしbroken repoでは、単に横並びで全部実行すると大量の重複・派生diagnosticを人間やagentへ返します。

今回の結果から、役割ではなく**依存順序**も明示する必要があると考え直しました。

```text
Gate 1: parse / syntax
        ↓ PASS
Gate 2: formatter + lint
        ↓ PASS
Gate 3: dependency / import context
        ↓ PASS
Gate 4: static type check
        ↓ PASS
Gate 5: runtime schema / fixture validation
        ↓ PASS
Gate 6: tests / integration / heavier CI
```

前段が失敗したら後段を完全に止める必要はありません。

調査目的なら後段も走らせてよい。

ただしUIやagentへの出力では、

```text
723 errors
```

と一括表示するのではなく、

```text
BLOCKING ROOT FAILURE
  syntax: 508

DOWNSTREAM / LOWER-CONFIDENCE WHILE SYNTAX IS BROKEN
  unknown-name: 108
  missing-import: 86
  ...
```

のように扱う方が、次の修正行動へつながります。

## prekは同じ修正patchを作れた

もう一つ確認したかったのが、既存`pre-commit`から`prek`へrunnerだけ差し替えられるかです。

対象repoには既存`.pre-commit-config.yaml`がありました。

同じconfigを`pre-commit 4.6.2`と`prek 0.4.11`で実行しました。

単発観測では次でした。

| | install | scan | measured total |
|---|---:|---:|---:|
| pre-commit | 1,534 ms | 8,765 ms | 10,299 ms |
| prek | 293 ms | 2,326 ms | 2,619 ms |

この1 runだけなら約3.93倍の差です。

ただしrunner VMやnetwork条件が完全には同一でないので、私はこれを「prekは常に4倍速い」という結論にはしません。

今回もっと重要だったのは、実行後に生成されたpatchでした。

```text
SHA-256(pre-commit.diff.patch)
30275602cf6b35644199d3a7fe949c038a10eaa9e6685074de4f7c8d62b36bf1

SHA-256(prek.diff.patch)
30275602cf6b35644199d3a7fe949c038a10eaa9e6685074de4f7c8d62b36bf1
```

**このrepository、このconfig、このrunではbyte-identicalでした。**

prek公式も既存`.pre-commit-config.yaml`との互換を目的にしています。

https://prek.j178.dev/compatibility/

少なくとも今回のfixtureでは、「高速化したいからhook定義まで作り直す」必要はありませんでした。

## Pydantic / Zodはlint件数に足してはいけない

ここまでの実験から、もう一つ整理できます。

PydanticやZodをRuff/Pyrefly/Oxlintと同じ「何件見つけたか」ランキングへ入れるべきではありません。

Pydanticはruntime data validation、Zodはruntime schema parsingの層です。

たとえば型上は`dict[str, object]`や`unknown`として受け取れても、実際のAPI responseや設定JSONがcontractを満たすとは限りません。

Pydantic:
https://docs.pydantic.dev/2.10/concepts/validation_decorator/

Zod:
https://zod.dev/basics

したがってPython側の完成形は、今のところ次を候補にしています。

```text
Ruff
  ↓
Pyrefly
  ↓
Pydantic contract tests with real fixtures
```

ただし**今回実測したのはRuffとPyreflyまで**です。

PydanticをDeepCodeの実データ境界へ入れた結果は、まだありません。

## TypeScript側も同じ仮説で次に壊す

TypeScript側は次を候補にしています。

```text
Biome formatter
  ↓
Oxlint
  ↓
tsc --noEmit
  ↓
Zod contract tests
```

Biomeはformatterとして使い、Oxlintをsource lint、`tsc --noEmit`をcompiler/type authority、Zodをruntime boundaryにする案です。

Biome formatter:
https://biomejs.dev/formatter/

Oxlint type-aware linting:
https://oxc.rs/docs/guide/usage/linter/type-aware.html

TypeScript `noEmit`:
https://www.typescriptlang.org/tsconfig/noEmit.html

Zod:
https://zod.dev/basics

Oxlintにはtype checkingをまとめる機能もありますが、現在のconfig referenceでは`typeCheck`はexperimentalと記載されています。

https://oxc.rs/docs/guide/usage/linter/config-file-reference

そのため、少なくとも次の実証までは`tsc --noEmit`を独立gateとして残します。

そして重要なのは、**このTypeScript stackはまだ今回の実験結果ではない**ことです。

次は実際に状態の悪いTypeScript repositoryを固定し、同じやり方で測ります。

## 次は「syntaxを直したら723件が何件まで減るか」を測る

今回のDiscovery runで一番知りたくなったのは、ツールの絶対速度ではありません。

```text
syntax 508件を直す
        ↓
Pyrefly 723件は何件残る？
```

です。

さらにdependencyを正しくinstallしたら、86件の`missing-import`はどこまで減るのか。

この前後差を取れば、

- root causeに近いdiagnostic
- 前段failureから派生したdiagnostic
- environment不足によるdiagnostic
- 修正後も残る本当のtype issue

を分離できます。

precheckで欲しいのは「たくさん怒ってくれること」ではありません。

**最初の1つを直したとき、次の100個が消える順序を教えてくれること**です。

今回、壊れたrepoへ最新toolを横並びで当てたことで、むしろその設計の方が重要だと分かりました。

## 現時点の結論

この実験から言える範囲は限定します。

- Ruff 0.16.3は固定したbroken repoで1,076 findingsを返した
- Pyrefly 1.2.0は723 findingsを返した
- Pyreflyの723件中508件はparse errorだった
- Ruffにも508件の`invalid-syntax`があった
- したがって1,076 + 723を独立欠陥数として扱えない
- 同じ`.pre-commit-config.yaml`を実行したpre-commitとprekは、このrunでは同一SHA-256のpatchを生成した
- 単発timingはprek側が短かったが、別runner条件なので一般性能比にはしない
- Pydantic / Biome / Oxlint / `tsc` / Zodは今回の実験では未実測

最初の仮説は「高速toolを積み重ねれば故障面が広く見える」でした。

今は少し違います。

> **壊れたrepositoryでは、toolの数よりdiagnosticの依存関係を設計した方がよい。syntaxとenvironmentが壊れたまま、後段の件数を品質指標にしてはいけない。**

次の実験では、508件のsyntax failureを先に除去し、同じPyrefly 1.2.0を再実行します。

そこで723という数字がどこまで縮むかを見ます。
