---
title: "CIが終わるまでデプロイしない。GitHubとShopifyに学ぶ「Push on Green」"
emoji: "🚦"
type: "tech"
topics: ["cicd", "githubactions", "githubpages", "testing", "sre"]
published: false
published_at: 2026-08-13 16:04
---

> **“Sorry, I couldn’t deploy github/my-feature: github and enterprise are still building.”**

これは教科書の例ではない。
GitHubが実際のGitHub.comのdeployで使っていたHubotの応答である。

CIがまだ終わっていない。
だからdeployしない。

CIが失敗した場合も同じだった。

> **“Sorry, I couldn’t deploy github/my-feature: github and enterprise failed to build.”**

GitHubはこの仕組みを **Deploy Guards** と呼び、当時このworkflowでWebサイトへ週に数百回deployしていた。

- GitHub Engineering, *Deploying branches to GitHub.com*: https://github.blog/engineering/engineering-principles/deploying-branches-to-github-com/

ここで面白いのは、品質gateを増やした結果「慎重になってdeployが遅くなった」という話ではないことだ。

**deployできる条件を機械が明確にしたから、人間は速くdeployできた。**

この考え方は、その後のGitHubでも形を変えて残っている。

2024年にGitHubが公開したmerge queueの内部運用では、GitHub.comで一般公開前に **30,000超のPull Requestと450万回のCI run** を処理した。その後、大規模monorepoでは月に500人超のengineerが2,500 PRをmergeし、変更をshipする平均待ち時間を **33%短縮** したと報告している。

- GitHub Engineering, *How GitHub uses merge queue to ship hundreds of changes every day*: https://github.blog/engineering/engineering-principles/how-github-uses-merge-queue-to-ship-hundreds-of-changes-every-day/

merge queueはbuildとtestを起動し、失敗するcommitでmain branchが更新されないようにする。

つまり、これは単なるCI設定の小技ではない。

**「検証を先に機械化し、通過した変更だけを次のstageへ進める」ことは、速度と信頼性を両立するためのrelease設計である。**

この記事では、その原則をGoogle、GitHub、Shopifyの実運用から確認し、最後にGitHub Pagesの小さなrepositoryへ落とし込む。

## Googleの“Push on Green”は「緑なら押す」ではない

Google SREのRelease Engineeringには、よく知られた表現がある。

> **“Push on Green”**

Googleでは、一部のteamがhourly buildを作り、その中からtest結果と含まれるfeatureを見てproductionへ出すversionを選ぶ。別のteamは、**すべてのtestを通ったbuildをそのままdeployする**Push on Greenを採用している。

- Google SRE, *Release Engineering*: https://sre.google/sre-book/release-engineering/

Google SRE Workbookがrelease engineeringの基本原則として挙げるのは、次の4つである。

> **“Reproducible builds / Automated builds / Automated tests / Automated deployments”**

- Google SRE Workbook, *Canarying Releases*: https://sre.google/workbook/canarying-releases/

順序が重要である。

```text
reproducible build
        ↓
automated test
        ↓
validated artifact
        ↓
automated deployment
        ↓
production evaluation
```

**deployは品質確認の代用品ではない。検証を通過した成果物を次へ進めるstageである。**

Googleのrelease systemであるRapidでも、compileとunit testの後にbuild artifactをsystem testやcanary deploymentへ渡す構造になっている。

大規模なGoogleだけに必要な設計ではない。
むしろ小さなrepositoryほど、この境界を明示するとfailure reasonが理解しやすくなる。

## Shopifyは5%のproduction trafficで止めてから100%へ進める

もう一つ分かりやすい実例がShopifyである。

Shopifyが公開しているrelease pipelineは、次の順序になっている。

```text
Pull Request
    ↓
CI / Merge Queue
    ↓
Canary
    ↓
Production
```

Merge Queueが変更を統合可能だと判断するとCanaryへdeployする。
Canaryが受けるのは **random 5% of incoming requests** である。

そこでdeveloperは **10分間** 変更をtestでき、manual interventionがなく、automated canary analysisがalertを出さなければProductionへ進む。

- Shopify Engineering, *Software Release Culture at Shopify*: https://shopify.engineering/software-release-culture-shopify

Shopifyはこのpipelineについて、automationが変更の品質に一定のassuranceを与え、release velocityが問題発生時のrecoveryを速くすると説明している。

重要なのは「Canaryという高度なtoolを使おう」という話ではない。

```text
CIで分かること
        ↓
限定されたproduction trafficで初めて分かること
        ↓
100% rollout後に分かること
```

を同じものとして扱っていないことである。

**検証には段階があり、前段を通ったから後段の確認が不要になるわけではない。**

## GitHub自身のdeploy guardは、なぜ説得力があるのか

GitHubの2015年のdeploy workflowをもう少し見ると、この境界がさらに明確になる。

当時のworkflowでは、

1. branchを作る
2. CIを通す
3. stagingやbranch labで確認する
4. productionの一部または全部へdeployする
5. productionで例外やperformance regressionを監視する
6. 問題なければmergeする

という流れを取っていた。

CIが未完了ならdeploy guardが止める。
CIが失敗しても止める。
production environmentが別のdeployでlockされていても止める。

さらにriskの高い変更ではproductionの一部serverだけへdeployし、問題がなければ範囲を広げていた。

- GitHub Engineering, *Deploying branches to GitHub.com*: https://github.blog/engineering/engineering-principles/deploying-branches-to-github-com/

ここから得るべき一般原則は、

> gateを減らせば速くなる

ではない。

むしろ、

> **何を通過すれば次へ進めるかを機械が判断できるほど、releaseは速くなる**

である。

実際、GitHubが2024年に公開したmerge queueの改善でも、旧deploy trainでは8時間以上待った末にconflictで外れることがあった。一方、merge queueへの移行後は月2,500 PRを処理し、平均ship待ち時間を33%短縮している。

品質gateとvelocityは必ずしもtrade-offではない。
**曖昧な人手判断を、再現可能なstate transitionへ変えることが両方を改善する。**

## GitHub Pagesの公式workflowもbuildとdeployを分けている

ここまでの話をGitHub Pagesへ落とす。

GitHub Pages公式ドキュメントには、そのまま

> **“Linking separate build and deploy jobs”**

という節がある。

公式例は `build` と `deploy` を別jobにし、`deploy` に `needs: build` を置く。
Pagesへのdeploymentは `github-pages` environmentに結びつける。

- GitHub Docs, *Using custom workflows with GitHub Pages*: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- GitHub Docs, *Using jobs in a workflow*: https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs

GitHubのpublishing sourceの説明でも、Pull Requestではbuildまで実行し、deployは行わない構成が示されている。

- GitHub Docs, *Configuring a publishing source for your GitHub Pages site*: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

つまり、小さなPages repositoryでも基本構造は同じである。

```text
Pull Request
    ↓
validate / build / test
    ↓
artifact
    ↓
main・permission・environmentなどを満たしたらdeploy
    ↓
public URL verification
```

**「成果物が正しいか」と「今この環境へ公開できるか」は別の問いである。**

## CI/CDでは少なくとも4つのstateを混ぜない

全部を1個の赤/緑で表すと、原因が違うfailureを同じものとして扱ってしまう。

| 状態 | 意味 | 次のaction |
|---|---|---|
| validation failed | 成果物が壊れている | code / test / buildを直す |
| validated, deploy unavailable | 成果物は通ったが公開条件がない | environment / permissionを整える |
| deployed, production check failed | deployは成功したが公開結果が壊れている | routing / runtime差分を直す |
| validated and verified | 検証・公開・公開後確認を通過 | release完了 |

これなら、失敗を見た人が最初から「何を直すべきか」を判断できる。

## production URLがなくてもWebとして検証できる

「まだ公開していないからWeb testできない」も必ずしも正しくない。

Playwrightはlocal web serverをtest前に起動する `webServer` を公式に提供しており、stagingやproduction URLがない場合を明示的なuse caseとして挙げている。

- Playwright Docs, *Web server*: https://playwright.dev/docs/test-webserver

静的siteならdeploy前に少なくとも、

```text
build outputを作る
    ↓
localhostでserveする
    ↓
主要routeを開く
    ↓
CSS / JS / data assetを取得する
    ↓
browser testを走らせる
```

ところまでは確認できる。

build commandがexit 0だったことと、**Webとして配信できることは同じではない。**

だから、公開環境がなくても今証明できることは先に証明する。

## deployment固有の条件はrelease gateへ分離する

productionへのdeploymentには品質以外の条件もある。

GitHub ActionsのEnvironmentでは、required reviewers、branch制限、wait timer、custom deployment protection rules、environment secretsなどをdeployment gateとして扱える。

- GitHub Docs, *Deployments and environments*: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments

概念的には次のように分離できる。

```text
quality gate
- lint
- type check
- unit test
- build
- local smoke / browser test

release gate
- target environmentが存在する
- deploy可能なbranchである
- approval済みである
- permission / secretが利用可能である

production gate
- public routeが応答する
- browserで主要操作が成立する
- error / performance regressionがない
```

前者が落ちたら成果物を直す。
release gateが満たせなければ環境を整える。
production gateが落ちたらdeploy後の実挙動を直す。

同じfailureにしない。

## 小さな実例: Pages未設定でもvalidationを止めなかった

ここまでの一般原則を、小さなrepositoryでも再現できるか試した。

`KAFKA2306/finBI` では2026年8月13日にworkflowを `validate` と `deploy` に分離した。

- commit: https://github.com/KAFKA2306/finBI/commit/bc928ab7806c727086992df838f8ccae62f58040
- workflow run #5: https://github.com/KAFKA2306/finBI/actions/runs/31672724045

この時点ではGitHub Pagesがまだ有効ではなかった。

しかしRun #5では `validate` が成功した。

- Python compile
- offline unit tests
- browser asset checks
- static site build
- localhost HTTP route smoke test
- generated residue cleanup
- clean checkout assertion

一方、deploy job内の

```text
Build Pages artifact
Configure Pages
Upload Pages artifact
Deploy Pages
```

はskipされた。

結果として、

```text
artifact quality = passed
deployment capability = unavailable
```

を同時に記録できた。

Pages未設定を理由にtestまで捨てなかった。

## Pagesが有効になった後も、同じ境界のまま先へ進めた

その後Pagesが有効になり、workflowは `public-e2e` まで拡張された。

2026年8月15日のRun #27では、

```text
validate     success
    ↓
deploy       success
    ↓
public-e2e   success
```

となった。

- current workflow: https://github.com/KAFKA2306/finBI/blob/main/.github/workflows/static-bi.yml
- workflow run #27: https://github.com/KAFKA2306/finBI/actions/runs/31825777595

この例の価値は「finBIのworkflowがbest practiceだった」ということではない。

Google、GitHub、Shopifyが大規模なrelease engineeringで使っている境界を、**小さなGitHub Pagesでも同じ形で再現できた**ことである。

## ただしfinBIにも改善余地がある

現在の `finBI` は `validate` でpublic rootをbuildしてsmoke testした後に削除し、`deploy` でPages artifactをもう一度buildしている。

これは動作しているが、より厳密にはGitHub Pages公式例のように、検証したbuild artifactを後段へ渡す方がよい。

```text
build once
    ↓
test that artifact
    ↓
store that artifact
    ↓
deploy that artifact
```

こうすれば「testしたもの」と「productionへ出したもの」の差をさらに小さくできる。

**自分たちの成功例をbest practiceそのものだと思わず、一般原則と照合して不足を見つける。**

それも再現可能なengineeringの一部である。

## 実務ではこの7項目から始めればよい

1. **PRでもvalidationを走らせる**
2. **deployはvalidation成功後だけにする**
3. **build/testとdeployment permissionを別gateにする**
4. **build outputをlocalhostで実際にserveして確認する**
5. **可能なら検証済みartifactそのものをdeployする**
6. **production URLはdeploy後に別のtestで確認する**
7. **failed / validated / deploy unavailable / deployed / production failedを区別する**

GitHub Pagesなら概念的にはこれで十分である。

```yaml
jobs:
  validate:
    steps:
      - checkout
      - lint / typecheck / unit test
      - build
      - local HTTP / browser test
      - upload artifact

  deploy:
    needs: validate
    if: deploy条件を満たす
    environment: github-pages
    steps:
      - deploy validated artifact

  production-test:
    needs: deploy
    steps:
      - test public URL
```

RuffでもBiomeでもPlaywrightでもcurlでもよい。
tool名は本質ではない。

変えない方がよいのはstageの意味である。

```text
validate
= これは出してよい成果物か

deploy
= この環境へ今出してよいか

production test
= 実際に出したものは利用可能か
```

## Greenは色ではなく、次へ進める根拠である

Googleの **“Push on Green”** を小さなWeb開発へ持ち込むなら、自動deployの格好良さだけを真似しても意味がない。

GitHubはCIがまだ走っているbranchをdeploy guardで止めた。
ShopifyはCIを通した変更を5%のtrafficへ出し、10分のCanary確認を置いた。
Googleはtest結果でproductionへ出すbuildを選び、Rapidではartifactをsystem testとcanaryへ渡した。
GitHub Pagesの公式workflowもbuildとdeployを別jobとして接続している。

共通しているのは、

**次のstageへ進む前に、今のstageで証明できることを証明する**

という設計である。

```text
Build → Test → Deploy → Verify
```

公開環境がまだなくてもtestはできる。
Pagesが無効でもbuildはできる。
localhostでWebとしてserveできる。

そして環境が整ったら、検証済みの成果物だけを次へ進めればよい。

**公開できないから検証しないのではない。検証できたものだけを公開する。**

その方がfailure reasonは明確になり、rollbackもしやすくなり、人間の判断も減る。

GitHubの実例が示したように、guardは速度の敵ではない。

**再現可能なguardは、速くshipするためのインフラである。**

## 一次情報

- Google SRE, *Release Engineering*: https://sre.google/sre-book/release-engineering/
- Google SRE Workbook, *Canarying Releases*: https://sre.google/workbook/canarying-releases/
- GitHub Engineering, *Deploying branches to GitHub.com*: https://github.blog/engineering/engineering-principles/deploying-branches-to-github-com/
- GitHub Engineering, *How GitHub uses merge queue to ship hundreds of changes every day*: https://github.blog/engineering/engineering-principles/how-github-uses-merge-queue-to-ship-hundreds-of-changes-every-day/
- Shopify Engineering, *Software Release Culture at Shopify*: https://shopify.engineering/software-release-culture-shopify
- GitHub Docs, *Using custom workflows with GitHub Pages*: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- GitHub Docs, *Configuring a publishing source for your GitHub Pages site*: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- GitHub Docs, *Using jobs in a workflow*: https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs
- GitHub Docs, *Deployments and environments*: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
- Playwright Docs, *Web server*: https://playwright.dev/docs/test-webserver
