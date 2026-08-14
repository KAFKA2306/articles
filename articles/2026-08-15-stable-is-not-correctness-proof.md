---
title: "Stableは型チェッカーの正しさを証明しない"
emoji: "🧭"
type: "tech"
topics: ["python", "typechecking", "ci", "testing", "developerexperience"]
published: false
---

「stableになった。production readyとも書いてある。ではCIのblocking type checkerにしてよい」

この判断は自然だ。しかし、release statusとsemantic correctnessは同じ証拠ではない。

今回、Pythonの型検査候補を製品比較から選ぶのをやめ、先にground truthを固定した。1つのmutantには1つのroot faultだけを入れ、clean baselineをblockした候補は既定authorityにできない、という条件を比較前に決めた。

結果は単純だった。

| checker | frozen in-scope mutants detected | clean blocking false positives |
|---|---:|---:|
| mypy 2.3.0 | 5 / 5 | 0 |
| Pyright 1.1.411 | 5 / 5 | 0 |
| ty 0.0.71 | 5 / 5 | 0 |
| Pyrefly 1.2.0 | 2 / 5 | 0 |

Pyreflyは2026年5月12日にv1をstableとし、project自身がproduction readyと説明している。一方、AstralはtyをBetaと位置付けながら、motivated usersにはproduction利用を勧めている。

それでも、この小さなpreregistered corpusではBetaのtyが5/5、stableのPyreflyが2/5だった。

この記事の結論は「tyが最強」ではない。

**release channelは運用成熟度の証拠にはなる。しかし、自分のrepositoryでblocking authorityに必要なsemantic coverageの証明にはならない。**

## 何を証明したかったか

実験前に置いたnull hypothesisは、新しい高速toolが、ground truth・false positive・setup cost・repeated timingを統制した後でも、incumbentより明確に良いengineering trade-offを示すとは限らない、というものだった。

型検査については、さらに小さく問いを切った。

> release statusやvendor positioningを見ずに、固定したroot faultsだけを見たとき、候補はblocking authorityとして必要なfaultを検出できるか。

反証条件も先に決めた。

- required mutantをmissしたら、そのtested configurationではdefault authorityに昇格させない。
- clean baselineをblocking false positiveで止めたら、同じくdefault authorityに昇格させない。
- raw diagnostic countはdefect countとして足さない。
- real repositoryでは完全なground truthがないため、recallを主張しない。

この順序にしたのは、結果を見てから評価軸を都合よく変えないためだ。

Preregistered protocol:
https://github.com/KAFKA2306/articles/blob/3bf9406308e96c4a9131a54792abdb287a15dba0/benchmarks/verification-stack-v2/PROTOCOL.md

## ground truthは5種類に絞った

Python static type authorityに対して使ったin-scope corpusは次の5つである。

- syntax failure
- incompatible argument type
- incompatible declared return type
- undefined name
- async misuse

1 mutant = 1 root faultとし、別のfailureが連鎖して件数を膨らませないようにした。

Controlled summary:
https://github.com/KAFKA2306/articles/blob/3bf9406308e96c4a9131a54792abdb287a15dba0/benchmarks/verification-stack-v2/results/controlled/summary.json

ここで重要なのは、5件がPython typingの全世界を代表しているわけではないことだ。このfixtureが証明できるのは、この5つのpreregistered faultに対するtested configurationの挙動だけである。

## stableのPyreflyがmissし、Betaのtyが通った

Pyrefly 1.2.0は5つのうち2つを検出した。

検出したのはsyntax failureとundefined name。今回missしたのは次だった。

```text
PY-TYPE-ARG-001
PY-TYPE-RETURN-001
PY-ASYNC-001
```

同じfixtureで、mypy 2.3.0、Pyright 1.1.411、ty 0.0.71は5/5を検出した。4候補ともclean baselineのblocking false positiveは0だった。

この結果だけで「Pyreflyは精度が低い」と一般化してはいけない。configuration、typing semantics、未収録のfault class、third-party integrationなどを含む全体性能は、この5 mutantでは測れないからだ。

しかし、次の命題は支持される。

> **stableというrelease labelだけでは、repositoryのblocking type authorityとして必要なsemantic coverageを証明できない。**

これはPyreflyだけの話ではない。release channelとsemantic authorityを別の評価軸にする、という設計判断の話である。

## 公式の「production ready」と矛盾するのか

矛盾しない。

Pyrefly projectは2026年5月12日のv1.0 announcementで、stable version 1に到達しproduction useへreadyだと説明している。また、Instagramを含むproduction codebaseでの利用も説明している。

https://pyrefly.org/blog/v1.0/

これは重要なoperational maturity evidenceである。

一方、Astralは2025年12月16日のty Beta announcementで、tyをBetaと明記している。同時に、自社projectで使っており、motivated usersにはproduction利用をrecommendできる段階だとしている。Stableはその後のmilestoneとして説明されている。

https://astral.sh/blog/ty

つまり公式情報だけを読んでも、次の2軸は分離されている。

```text
release maturity
    stable / beta / experimental

semantic authority
    自分がblockしたいfailureを十分に検出するか
```

stableは後者のtest reportではない。

## real repositoryでもう一度止めた

controlled fixtureだけで記事にすると、toy benchmark固有の話かもしれない。

そこでcontrolled candidate-level outputを記事選定に使う前に、実repository sampleを決定論的にfreezeした。Python sampleは次である。

```text
KAFKA2306/2511youtuber
95a0f6b4f5270d1463c15f301a2bd4f0d709c109
```

選定ruleはeligible repository集合からrepository fullnameのSHA-256がlexicographically smallestなものを選ぶ、というものに固定した。結果を見て都合のよいrepoへ差し替えていない。

Frozen sample:
https://github.com/KAFKA2306/articles/blob/3bf9406308e96c4a9131a54792abdb287a15dba0/benchmarks/verification-stack-v2/real-repo-sample.json

4つのPython checkerはすべてこのrepositoryで実行でき、いずれもnonzero exitとdiagnostic outputを返した。

ただし、ここで「どれが一番多くbugを見つけた」とは言わない。

real repositoryには完全なdefect ground truthがない。missing dependency、stub不足、project configuration、実際のtype defectが混ざるため、output line数はrecallではない。

External summary:
https://github.com/KAFKA2306/articles/blob/3bf9406308e96c4a9131a54792abdb287a15dba0/benchmarks/verification-stack-v2/results/external/summary.json

external stageから言えるのは、少なくともcandidateがfrozen real repository上で実行可能であり、controlled resultが「実repoでは起動すらしない候補だけの比較」ではないことまでである。

## authorityを決めるとき、release statusをどこに置くか

私はtype checkerの採用判断を、少なくとも次の2 gateに分ける。

### Gate 1: semantic authority

blockingしたいfailureを、repositoryに近いground truth fixtureで検出するか。

たとえば、

```text
argument mismatch
return mismatch
undefined name
async misuse
project固有のtyping contract
```

を1 root faultずつfixture化する。

ここでcritical mutantをmissするなら、速さやstable statusより先に止める。

### Gate 2: operational maturity

semantic gateを通った候補の中で、次を見る。

- stable / beta / experimental status
- configuration migration
- editor / CI integration
- third-party library support
- upgrade policy
- teamが許容できるcompatibility risk

この順序なら「Betaだから自動的に不採用」にも、「stableだから自動的に採用」にもならない。

## tyを今すぐdefaultにすべき、でもない

今回の結果でty 0.0.71は5/5だった。

しかしAstral自身がBetaと明記している以上、それは無視してよい情報ではない。Betaはcorrectness failureの証拠ではないが、compatibilityやstabilityのrisk budgetを考える材料である。

したがって実務の判断は、たとえば次のようになる。

| 状況 | 判断 |
|---|---|
| incumbentがcritical fixtureを通る | 急いで置換しない |
| challengerだけがcritical fixtureを通る | shadow CIや限定scopeで評価を進める |
| stable candidateがcritical fixtureをmissする | stableだけを理由にblocking authorityへ昇格させない |
| Beta candidateがfixtureを通る | correctness候補として残すが、maturity riskを別途評価する |
| real repoで大量diagnosticが出る | ground truthなしに「検出力」と数えない |

ここでのポイントはtool名ではなく、**authority promotionの手順**である。

## 何が出れば逆の結論にしたか

もしcontrolled fixtureで、stable candidateがrequired 5/5を通り、Beta challengerがcritical mutantをmissしていたら、この証拠から「release statusとsemantic authorityを分ける必要がある」という主張はかなり弱くなった。

少なくとも今回のheadlineにはしなかった。

また、real-repository stageでcandidateが再現可能に実行できなければ、controlled resultをそのままoperational recommendationへ持ち込むことも止めた。

反対の結果でも同じ記事を書くなら、それは実験ではなくadvocacyである。

## 再現するときは、製品比較から始めない

この実験から再利用したいのはtool rankingではない。

1. repositoryで絶対に止めたいfailure classを決める。
2. 1 root faultずつ最小fixtureを作る。
3. clean baselineを固定する。
4. candidate名を見る前にdisqualifierを決める。
5. exact versionをpinする。
6. 同じfixtureへ候補を当てる。
7. required mutant missとblocking false positiveを先に見る。
8. survivorにだけ速度・migration・maturityを評価する。
9. real repoではrecallを主張せず、compatibilityとoperational frictionを見る。

この順番なら、新しいtoolが出るたびに「速そう」「stableになった」「有名企業が使っている」という理由だけでCI authorityを入れ替えずに済む。

## 結論

release statusは必要な情報だ。しかし、それが答えている問いは「このprojectはどの成熟段階か」であって、「あなたのrepositoryで何を正しくblockできるか」ではない。

今回の小さなground-truth experimentでは、stableのPyrefly 1.2.0が2/5、Betaのty 0.0.71が5/5だった。これは万能なaccuracy rankingではない。

それでも、1つの実務判断は変えられる。

**blocking authorityを決める前に、release labelではなく自分のground truthを通す。**

それが通った後で初めて、stableかBetaか、速いか、移行しやすいかを比較すればよい。
