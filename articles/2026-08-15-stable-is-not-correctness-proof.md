---
title: "型チェッカーを比較する前に、設定を比較対象から消す"
emoji: "🧪"
type: "tech"
topics: ["python", "typechecking", "ci", "testing", "developerexperience"]
published: false
---

同じ型チェッカー、同じversion、同じ5つのfaultでも、設定だけで結果が **2/5から5/5へ変わった**。

これは「どの型チェッカーが強いか」という話ではない。もっと手前の話だ。

**設定を固定していない型チェッカー比較は、製品差ではなくpreset差を測っている可能性がある。**

今回、その失敗を実際に踏んだ。最初のcontrolled resultではPyrefly 1.2.0を5 mutant中2件検出と解釈した。その後、post-merge evidence integrity re-auditで同一candidateをpreset別に再計測すると、`basic`では2/5、`default`では5/5だった。旧記事の「stableのPyreflyが2/5」という製品差の物語は撤回する。

## 先に結論を決めない

この実験系では、tool名より先にground truthを固定した。

Python static type authorityに対するin-scope faultは5つだけである。

- `PY-SYNTAX-001`: syntax failure
- `PY-TYPE-ARG-001`: incompatible argument type
- `PY-TYPE-RETURN-001`: incompatible declared return type
- `PY-NAME-001`: undefined name
- `PY-ASYNC-001`: async misuse

1 mutant = 1 root faultとし、raw diagnostic数をdefect数として足さない。さらにv2.5で、**clean baselineもblockするcandidateにはmutant検出creditを与えない**というintegrity ruleを明示した。

Protocolとamendment:

- https://github.com/KAFKA2306/articles/blob/822be109de61e5915799fcf7d79e6345dff4f6b1/benchmarks/verification-stack-v2/PROTOCOL.md
- https://github.com/KAFKA2306/articles/blob/822be109de61e5915799fcf7d79e6345dff4f6b1/benchmarks/verification-stack-v2/AMENDMENT-v2.5-post-merge-evidence-integrity.md

ここで重要なのは、v2.5が結果をよく見せるための後付け評価軸ではないことだ。旧summaryにrepaired harnessの結果が反映されていないことが判明したため、旧記事の結論を停止し、同じcandidate versions・mutants・real-repo sampleを維持したままevidenceを再生成するためのamendmentである。

## 同じPyrefly 1.2.0で結果が変わった

preset calibrationでは、Pyrefly 1.2.0に対して同じ5 mutantを `no_config`、`basic`、`default` の3条件で実行した。各mutantでclean baselineも同じ条件に通している。

観測結果の要点はこうなる。

| mode | syntax | arg type | return type | undefined name | async misuse |
|---|---:|---:|---:|---:|---:|
| no config → basic | detect | miss | miss | detect | miss |
| `basic` | detect | miss | miss | detect | miss |
| `default` | detect | detect | detect | detect | detect |

Raw calibration:
https://github.com/KAFKA2306/articles/blob/822be109de61e5915799fcf7d79e6345dff4f6b1/benchmarks/verification-stack-v2/results/controlled/pyrefly-preset-calibration.json

Pyrefly公式ドキュメントとも整合する。設定のないprojectでは`basic` presetを合成し、これはsyntax errorやmissing importなど高confidenceのerror kindに絞る。一方、`default`は通常のdefault severityを使い、`strict`はさらにerror kindを追加する。

https://pyrefly.org/en/docs/configuration/

つまり2/5は「Pyrefly 1.2.0の検出能力」ではなかった。**Pyrefly 1.2.0をbasic presetで走らせたときの、この5 faultに対する観測**だった。

## 修復後、製品ランキングは消えた

baseline-qualifiedなcontrolled summaryを再生成すると、Python static type checkerの5 mutantについて次になった。

| checker / tested configuration | detected | clean blocking false positives |
|---|---:|---:|
| mypy 2.3.0 | 5/5 | 0 |
| Pyright 1.1.411 | 5/5 | 0 |
| ty 0.0.71 | 5/5 | 0 |
| Pyrefly 1.2.0 | 5/5 | 0 |

Repaired summary:
https://github.com/KAFKA2306/articles/blob/822be109de61e5915799fcf7d79e6345dff4f6b1/benchmarks/verification-stack-v2/results/controlled/summary.json

ここから「4製品は同等」とも言えない。5 mutantしかなく、typing全体のrecall、diagnostic quality、third-party typing、incremental behavior、editor behaviorは測っていない。

言えるのはもっと限定的だ。**このground truthでは、以前の記事を支えていた2/5対5/5の製品差は、configurationを揃え直すと残らなかった。**

## authorityはbinary名ではなく実行契約に付く

CIでblocking authorityを決めるとき、`pyrefly`や`pyright`というbinary名だけを記録しても足りない。

少なくとも次を1つの実行契約として固定する必要がある。

```text
authority =
  tool version
  + preset / mode
  + config file
  + project scope
  + Python version / environment
  + blocking severity policy
```

Pyrightも公式に`off` / `basic` / `standard` / `strict`の`typeCheckingMode`を持ち、strictでは多くのruleが追加で有効になる。

https://github.com/microsoft/pyright/blob/main/docs/configuration.md

したがって「Pyrefly vs Pyright」を測るなら、まず双方で何をblocking errorとして有効化したかを固定しなければならない。presetの違いを製品差としてheadlineにしてはいけない。

## gate orderingも変わる

この結果から、型チェッカー導入gateは次の順序にする。

1. **environment/config discovery**: 実際に読まれたconfigとpresetを記録する。
2. **clean baseline**: 正常fixtureをblockしないことを確認する。
3. **ground-truth mutants**: 1 root faultずつ必要なfailure classを検出するか測る。
4. **diagnostic quality**: root causeを直接指すかを見る。件数はdefect数にしない。
5. **same-runner timing**: correctness survivorだけを同一runnerでcold/warm計測する。
6. **real repo**: frozen repositoryでoperational frictionを見る。ground truth不明なのでrecallには使わない。

速度を先に置かない。clean baselineを通らないcandidateの「検出数」も数えない。そしてpresetを記録していないrunを製品比較へ昇格させない。

## real repoは答え合わせではない

外部妥当性用のPython repositoryは結果を見る前にfreezeした。

```text
KAFKA2306/2511youtuber
95a0f6b4f5270d1463c15f301a2bd4f0d709c109
```

ここでは複数checkerが実行可能であることを確認したが、diagnostic数をrecall rankingには使っていない。実repositoryには完全なdefect ground truthがなく、dependency、stub、configuration、実際のtype defectが混在するからだ。

Frozen sample:
https://github.com/KAFKA2306/articles/blob/822be109de61e5915799fcf7d79e6345dff4f6b1/benchmarks/verification-stack-v2/real-repo-sample.json

controlled fixtureが「何を検出したか」を測り、real repoは「その実行契約を現実のrepositoryへ持ち込めるか」を見る。この2層を混ぜない。

## 3つの物語を同じ証拠で潰した

結果を見てから都合のよいheadlineを選ばないため、同じevidenceから競合する命題を作った。

### 1. Stableはsemantic correctnessを証明しない

一般論としては正しいが、今回の旧headlineを支えた「stable 2/5 vs Beta 5/5」というcontrastは修復後に消えた。この記事の中心命題には採用しない。

### 2. Pyreflyは他checkerよりcoverageが低い

棄却する。同じversionが`default`では5/5になったため、旧2/5を製品固有coverageとして扱えない。

### 3. 型チェッカー比較ではpresetもauthority contractの一部である

これだけが残った。同一binary・同一version・同一ground truthでpreset変更だけが2/5→5/5を生み、公式仕様もpresetごとのdiagnostic surface差を明示している。

## 何が出ればこの結論を変えるか

同じfrozen corpusで`basic`と`default`が同じ5/5になっていた、あるいは旧2/5がpresetではなく再現可能なchecker defectによるものだったなら、このheadlineは成立しない。

また、この実験は「defaultが最適」「strictを使うべき」とは証明していない。必要なfailure classと許容false positiveはrepositoryごとに違う。strict/default/basicのどれをauthorityにするかは、repository固有ground truthで決めるべきである。

## 再現方法

最小の再現手順は次でよい。

1. repositoryで絶対にblockしたいtype failureを1 root faultずつfixture化する。
2. 各mutantに対応するclean baselineを保存する。
3. tool versionだけでなくpreset/mode/configをpinする。
4. cleanとmutantを同じexecution contractで実行する。
5. `clean=pass && mutant=block` のときだけ検出creditを与える。
6. presetを変える場合は同じcorpusで再実行し、製品差と設定差を分離する。
7. survivorだけを速度やmigration costへ進める。

## 結論

型チェッカーの名前はauthorityではない。**versionと設定を含む実行契約がauthorityである。**

今回、Pyrefly 1.2.0はbasic presetで2/5、default presetで5/5だった。この差を無視して「Pyreflyは2/5だった」と書けば、設定差を製品差に変換してしまう。

新しい型チェッカーを評価するとき、最初に比較表を作る必要はない。

まず、何をblockする権限を与えたいかをground truthにする。その次に、実際にその権限を行使する**設定込みのexecution contract**を固定する。

製品比較は、その後でいい。
