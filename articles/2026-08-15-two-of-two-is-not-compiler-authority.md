---
title: "2/2で通っても、コンパイラはまだ消せない"
emoji: "🧪"
type: "tech"
topics: ["typescript", "oxlint", "ci", "testing", "tooling"]
published: false
---

新しいツールが、既存のコンパイラと同じテストを通った。

それならCIから古いgateを消してよい――とは限らない。

今回の実験では、TypeScriptの型エラーを1つずつ埋め込んだ固定fixtureに対し、TypeScript compilerとOxlintのtype-check機能を同じground truthで検証した。対象となる2つの型mutantでは、どちらも **2/2** を検出した。clean baselineのblocking false positiveも0だった。

それでも、今回の条件では `tsc --noEmit` をdefaultの型authorityから外さない。

理由は速度でもブランドでもない。**「このfixtureで正しく動いた」という証拠と、「CIの最終判定者を任せられる」という証拠は別物だからだ。**

## まず、何を測ったのか

比較前にprotocolを固定した。

- 1 mutant = 1 root fault
- raw diagnostic数を欠陥数として数えない
- clean baselineをblockする候補はdefault authorityから失格
- correctnessを速度より先に判定する
- Experimentalなsemantic featureをdefault authorityにする場合は、結論自体をexperimental adoptionに限定する

Protocol:
https://github.com/KAFKA2306/articles/blob/81848adca34e077835735a1f8586c6e8cd8cd511/benchmarks/verification-stack-v2/PROTOCOL.md

今回のTypeScript corpusには、syntax、lint、type argument、type return、promise misuse、runtime boundaryを別々のroot faultとして入れている。formatter、linter、compiler、runtime validatorを同じ「エラー検出ツール」として合算しないためだ。

Fixture design:
https://github.com/KAFKA2306/articles/blob/81848adca34e077835735a1f8586c6e8cd8cd511/benchmarks/verification-stack-v2/FIXTURE_DESIGN.md

実行環境のreauditでは、TypeScript 7.0.2、Oxlint 1.76.0を記録した。

Installed versions:
https://github.com/KAFKA2306/articles/blob/81848adca34e077835735a1f8586c6e8cd8cd511/benchmarks/verification-stack-v2/results/controlled/installed-versions.json

## 観測結果: 型mutantでは同点だった

controlled summaryでは次の結果になった。

| authority candidate | in-scope type mutants | detected | clean blocking false positives |
|---|---:|---:|---:|
| `tsc` | 2 | 2 | 0 |
| Oxlint `typeCheck` | 2 | 2 | 0 |

`tsc` はsyntax mutantも担当範囲に含めたためsummary全体では3/3、Oxlint `typeCheck` は型mutant2件を担当して2/2である。したがって「3対2だからtscの勝ち」という読み方もしてはいけない。責務の異なる分母を足すと、またraw count比較に戻ってしまう。

Controlled summary:
https://github.com/KAFKA2306/articles/blob/81848adca34e077835735a1f8586c6e8cd8cd511/benchmarks/verification-stack-v2/results/controlled/summary.json

この結果だけを見るなら、少なくとも今回の2つの型faultについてOxlint `typeCheck`が見逃した、とは言えない。

ここで重要なのは、**2/2という結果をどこまで昇格させてよいか**である。

## 同じcorrectnessでもauthorityは同じにならない

TypeScript公式は `noEmit` を、JavaScript等を出力せずTypeScriptをsource code type-checkerとして使う設定として説明している。

https://www.typescriptlang.org/tsconfig/noEmit.html

一方、Oxlint公式はtype-aware lintingとtype checkingを分けている。`--type-aware` はTypeScriptの型情報を必要とするlint ruleを有効にする機能で、`--type-check` はTypeScript compiler diagnosticsを併せて報告する機能だ。

https://oxc.rs/docs/guide/usage/linter/type-aware.html

そしてOxlintのconfiguration referenceは、`options.typeCheck` を現在も **experimental type checking** と明記している。

https://oxc.rs/docs/guide/usage/linter/config-file-reference

つまり今回得た証拠はこう分かれる。

- **観測した証拠**: 固定した2つの型mutantでは両者2/2、clean baseline false positive 0
- **公式仕様の証拠**: `tsc --noEmit` はTypeScriptのsource type-checkerとして使える
- **公式statusの証拠**: Oxlint `typeCheck` はexperimental

最初の証拠が良好でも、3番目は消えない。

## 「動いた」と「default authority」は別のgateにする

CIのtool migrationで危険なのは、parity testをそのままreplacement authorizationにしてしまうことだ。

例えば次の移行を考える。

```text
before
  oxlint
  tsc --noEmit

after
  oxlint --type-aware --type-check
```

コマンドが1本減る。今回の2 mutantも検出できた。魅力的に見える。

しかし、この変更には少なくとも2つの別判定がある。

1. **correctness gate**: 事前に固定したfaultを落とさないか
2. **authority gate**: その機能のstatus・互換範囲・運用条件を含め、defaultのblocking authorityを任せる条件を満たすか

今回、1は通った。2は通していない。

これはOxlintを否定する判断ではない。むしろ逆で、**experimental challengerとして比較対象に残せるだけのcorrectness evidenceは得られた**。ただし「試す価値がある」と「既存authorityを削除してよい」の間にgateを置く。

## 壊れた判断例: 2/2だから置換する

次の推論は成立しない。

```text
Oxlint typeCheck: 2/2
TypeScript compiler: 2/2
        ↓
同等
        ↓
tscを削除
```

2件のmutantは完全なTypeScript compiler conformance suiteではない。また、今回のreal-repository probeでは `investor2` の `tsc` と通常の `oxlint` は実行したが、Oxlint `--type-check` のexternal-validity probeは記録していない。

External-validity summary:
https://github.com/KAFKA2306/articles/blob/81848adca34e077835735a1f8586c6e8cd8cd511/benchmarks/verification-stack-v2/results/external/summary.json

そこでは `tsc` はexit 0、通常の`oxlint`はexit 1だったが、real repoには完全なdefect ground truthがない。したがって、このexit codeや出力行数をaccuracy比較には使えない。まして通常lintの結果を`--type-check`の実証に読み替えることもできない。

**external `--type-check` は未検証**。ここは空欄のまま残すのが正しい。

## 改善後: replacementを3段階に分ける

実務では、置換を次の3段階に分けると判断が崩れにくい。

### 1. Candidate

公式に責務を持つかを確認する。

Oxlintの場合、type-aware lintとtype-checkは別surfaceである。単に「型が分かるlinter」だからcompiler replacement候補、と推測しない。

### 2. Evidence-qualified challenger

自分のrepoで重要なfailure classをfixture化し、clean baselineとmutantを固定して比較する。

今回の2/2はここまでを支持する。

### 3. Default authority

correctnessに加えて、機能status、対応するcompiler/config surface、real-repo compatibility、upgrade時の回帰gateまで満たした時だけ既存authorityを削除する。

この段階では「新しいtoolを追加できるか」ではなく、**古いauthorityを安全に削除できるか**を問う。

## 他のtoolにも同じauthority modelを使う

この考え方はTypeScript type checkingだけの話ではない。

Ruff公式はlinterの入口を `ruff check`、formatterの入口を `ruff format` と分け、formatterはimport sortingを行わないと明記している。Biomeもformatter、linter、assistを別surfaceとして設定する。prekは既存の`.pre-commit-config.yaml`を実行できるhook managerであり、hook内部のpolicyそのものではない。

- Ruff linter: https://docs.astral.sh/ruff/linter/
- Ruff formatter: https://docs.astral.sh/ruff/formatter/
- Biome configuration: https://biomejs.dev/reference/configuration/
- prek compatibility: https://prek.j178.dev/compatibility/

workspaceでも同様だ。Turborepoはtask execution/cacheを提供し、`--affected`でGit履歴から対象packageを絞れる。一方、Boundaries/Tagsは公式support policy上experimentalである。Nxはaffected calculationにGit historyとproject graphを使い、JavaScript/TypeScriptのboundary enforcementには`@nx/enforce-module-boundaries`という別surfaceを持つ。

- Turborepo caching: https://turborepo.dev/docs/crafting-your-repository/caching
- Turborepo `--affected`: https://turborepo.dev/docs/reference/run#--affected
- Turborepo support policy: https://turborepo.dev/docs/support-policy
- Nx affected: https://nx.dev/docs/features/ci-features/affected
- Nx module boundaries: https://nx.dev/docs/technologies/eslint/eslint-plugin/guides/enforce-module-boundaries

**1つのbinaryに機能が増えたことと、1つのauthorityに統合してよいことは同義ではない。**

## 再現する

この結果はrepositoryに固定してある。

```bash
git clone https://github.com/KAFKA2306/articles.git
cd articles
git checkout 81848adca34e077835735a1f8586c6e8cd8cd511

cat benchmarks/verification-stack-v2/PROTOCOL.md
cat benchmarks/verification-stack-v2/results/controlled/summary.json
cat benchmarks/verification-stack-v2/results/controlled/installed-versions.json
cat benchmarks/verification-stack-v2/results/external/summary.json
```

raw artifactまで追う場合は `benchmarks/verification-stack-v2/results/controlled/source-runtime.json` を確認する。diagnostic行数ではなく、mutant IDとexpected authorityに対するdetected booleanを見る。

## 何を測っていないか

今回の結論には明確な境界がある。

- 型mutantは2件であり、TypeScript全仕様のconformanceを測っていない
- Oxlint `--type-check` のreal-repository external-validity runを実施していない
- editor/LSP体験を比較していない
- upgrade間の互換性を長期観測していない
- vendorの速度倍率を自分たちの性能結果として使っていない

したがって「Oxlint typeCheckは不正確」とは結論していない。今回言えるのは、**観測したcorrectness parityだけではdefault authorityへの昇格条件を満たさない**、ということだけだ。

## 何が起きれば判断を反転するか

recommendationを固定観念にしないため、反転条件も決めておく。

少なくとも次が揃えば、`tsc --noEmit`を削除する再評価に進める。

1. Oxlintのtype checkingが公式にdefault-authority用途へ十分なstability statusになる
2. repoで重要な型failure corpusをclean baseline付きで継続的に通す
3. frozen real repoで`--type-check`自体のcompatibilityを確認する
4. 必要なTypeScript configuration/compiler diagnostic surfaceに欠落がないことを確認する
5. 置換後にsuperseded gateを削除し、二重authorityを恒久化しない

逆に、このどれかが欠ける間は、Oxlintをlint authorityとして使うことと、compiler authorityまで移譲することを別の意思決定として扱う。

## 結論

modern toolchainの統合で見るべきなのは「何本のcommandを1本にできるか」ではない。

見るべきなのは、**その1本にどの判定権限まで移してよい証拠があるか**だ。

今回、Oxlint `typeCheck` は固定した型mutantで2/2を検出した。それは有力なchallengerである証拠にはなる。しかし、公式にexperimentalで、external `--type-check`も未検証の状態では、`tsc --noEmit`をdefault authorityから外す証拠にはならない。

correctness parityは、移行の入口であって出口ではない。
