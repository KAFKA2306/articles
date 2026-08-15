---
title: "速く出すために、勝手に出さない。GitHubとShopifyに学ぶRelease Engineering"
emoji: "🚦"
type: "tech"
topics: ["cicd", "githubactions", "githubpages", "testing", "sre"]
published: true
published_at: 2026-08-13 16:04
---

> **“Sorry, I couldn’t deploy github/my-feature: github and enterprise are still building.”**

これは架空のCI/CD教材ではない。

GitHubがGitHub.comをdeployするとき、実際にHubotが返していたメッセージである。

CIがまだ終わっていない。
だからdeployしない。

CIが失敗した場合も同じだった。

> **“Sorry, I couldn’t deploy github/my-feature: github and enterprise failed to build.”**

GitHubはこの仕組みを **Deploy Guards** と呼んでいた。2015年公開、2024年更新のGitHub Engineeringの記事によれば、このworkflowでGitHub.comには週に数百回の変更がdeployされていた。

- GitHub Engineering, *Deploying branches to GitHub.com*
  - https://github.blog/engineering/engineering-principles/deploying-branches-to-github-com/

一見すると、これは慎重な会社がdeployを遅くするための仕組みに見える。

実際は逆である。

**「何を満たせば次へ進めるか」を機械に判断させることで、人間は安心して速くshipできる。**

この記事では、Google SRE、GitHub、Shopify、DORAの一次情報と実運用を使って、この考え方を確認する。

最後にGitHub Pagesへ落とし込み、Pagesがまだ使えない状況でも何を検証すべきかを整理する。

## 「速さ」と「安定性」は本当にtrade-offなのか

CI/CDの議論では、ときどき次の二択になってしまう。

```text
速く出す
vs
慎重に検証する
```

しかしDORAの研究史では、2015年の時点で、高performerはdeliveryの速度と安定性の両方で優れていたと整理されている。

現在のDORAもsoftware delivery performanceを、単なるdeploy回数ではなく、throughputとinstabilityの両方で測る。

- change lead time
- deployment frequency
- failed deployment recovery time
- change fail rate
- deployment rework rate

- DORA, *A history of DORA’s software delivery metrics*
  - https://dora.dev/insights/dora-metrics-history/
- DORA, *DORA’s software delivery performance metrics*
  - https://dora.dev/guides/dora-metrics/

重要なのは、**速くdeployすること自体が目的ではない**ことだ。

```text
変更を速く届ける
        +
失敗を減らす
        +
失敗しても速く戻す
```

を同時に改善する。

そのために、release processを曖昧な人手判断ではなく、再現可能なstate transitionへ変えていく。

## Googleの“Push on Green”は「緑なら押す」ではない

Google SREのRelease Engineeringには、有名な表現がある。

> **“Push on Green”**

Googleでは、一部のteamがhourly buildの中からtest結果を見てproductionへ出すversionを選び、別のteamはすべてのtestを通ったbuildをdeployするmodelを採用している。

- Google SRE, *Release Engineering*
  - https://sre.google/sre-book/release-engineering/

Google SRE Workbookのrelease engineering原則はさらに明快である。

- reproducible builds
- automated builds
- automated tests
- automated deployments
- small deployments

- Google SRE Workbook, *Canarying Releases*
  - https://sre.google/workbook/canarying-releases/

順序が重要である。

```text
source
  ↓
reproducible build
  ↓
automated test
  ↓
validated artifact
  ↓
deployment
  ↓
production evaluation
```

**deployは品質検査の代用品ではない。検証を通った成果物を次の環境へ進める操作である。**

## GitHubはgateを機械化して、ship待ちを33%減らした

GitHubのDeploy Guardsは分かりやすいが、古い事例だけではない。

2024年、GitHubはGitHub.comで使うmerge queueの内部運用を公開した。

一般公開前にGitHub.comで処理した規模は、

- **30,000超のPull Request**
- **450万回のCI run**

だった。

その後、大規模monorepoでは、

- 月に **500人超** のengineer
- 月に **2,500 Pull Request**
- 平均ship待ち時間 **33%短縮**

を報告している。

- GitHub Engineering, *How GitHub uses merge queue to ship hundreds of changes every day*
  - https://github.blog/engineering/engineering-principles/how-github-uses-merge-queue-to-ship-hundreds-of-changes-every-day/

merge queueは候補PRをgroup化し、GitHub Actionsでbuildとtestを実行する。
失敗するcommitでmain branchが更新されないようbranch protectionも使う。
conflictするPRは自動でqueueから外す。

以前のdeploy trainでは、developerが8時間以上待った後、conflictによってtrainから外されることもあった。

つまり、ここで得られた33%は、

```text
gateをなくした結果
```

ではない。

```text
gateの判定とqueue運用を自動化した結果
```

である。

**安全確認をなくすのではなく、安全確認から人間の待ち仕事を減らす。**

これがCI/CD automationの重要な方向である。

## Shopifyは5%で止め、10分見てから100%へ進める

Shopifyが公開しているrelease pipelineも同じ思想を持っている。

```text
Pull Request
    ↓
CI / Merge Queue
    ↓
Canary
    ↓
Production
```

Merge Queueが変更を統合可能と判断すると、Canaryへdeployする。

Canaryが受けるのは **random 5% of incoming requests** である。

developerはそこで **10分間** 変更をtestできる。
manual interventionがなく、automated canary analysisがalertを出さなければProductionへ進む。

- Shopify Engineering, *Software Release Culture at Shopify*
  - https://shopify.engineering/software-release-culture-shopify

ここで重要なのはCanaryという名前ではない。

Shopifyは、検証できることをstageごとに分けている。

```text
CIで分かること
        ↓
限定されたproduction trafficで分かること
        ↓
100% rollout後に分かること
```

unit testがgreenでも、real trafficでしか見つからないfailureはある。

だから前段のtestを信用しつつ、後段の観測も消さない。

**「前で検証したから後ろは見なくてよい」ではなく、「前を通ったものだけ後ろで検証する」。**

## 2026年のGitHubは「障害時にもdeployできるか」まで検証している

release engineeringの境界は、testとdeployだけではない。

2026年4月、GitHubはdeployment toolingの循環依存をeBPFで検出・遮断する仕組みを公開した。

GitHubは自社source codeをGitHub.comでhostしている。
そのため、GitHub.com自体が障害になると、「GitHubを直すためにGitHubへアクセスする」という循環依存が生まれうる。

GitHubはその対策として、source codeのmirrorとrollback用のbuilt assetsを維持している。
さらにdeployment scriptだけをcGroupへ入れ、eBPFを使って問題のあるnetwork dependencyを検出・blockする仕組みを構築した。

この検出processは **6か月のrollout後にlive** になったとGitHubは報告している。

- GitHub Engineering, *How GitHub uses eBPF to improve deployment safety*, 2026-04-16
  - https://github.blog/engineering/infrastructure/how-github-uses-ebpf-to-improve-deployment-safety/

これは高度なplatform engineeringの例だが、原則は小さなCI/CDにもそのまま使える。

**deployが必要な瞬間に、deploy先や外部serviceが利用できるとは限らない。**

だから、

```text
artifactは正しいか
```

と、

```text
今このenvironmentへdeploy可能か
```

を同じcontractにしない。

## 4つのcontractに分けるとfailureが読める

ここまでのGoogle、GitHub、Shopifyの事例を小さくすると、少なくとも4つに分けられる。

| Contract | 問い | 失敗したら |
|---|---|---|
| Build | 同じinputから成果物を作れるか | build / dependencyを直す |
| Validate | 成果物は要求を満たすか | code / testを直す |
| Release | 今このenvironmentへ出してよいか | permission / approval / environmentを直す |
| Verify | 出したものが実際に使えるか | routing / runtime / production差分を直す |

全部を1個の赤/緑にすると、原因が混ざる。

例えばPagesが無効なだけなのに、unit testまで「失敗」に見える必要はない。

逆にPagesが無効だからといって、unit testやbuildまでskipしてよいわけでもない。

```text
VALIDATION_FAILED

VALIDATED / RELEASE_BLOCKED

DEPLOYED / PRODUCTION_FAILED

VERIFIED
```

くらいは意味を分けた方が、次のactionが明確になる。

## GitHub Pages自身もbuildとdeployを別jobにしている

この考え方は大規模企業だけのものではない。

GitHub Pagesの現在の公式ドキュメントには、明示的に

> **“Linking separate build and deploy jobs”**

という節がある。

公式例では `build` jobがPages artifactを作ってuploadし、`deploy` jobは `needs: build` でその後に動く。

- GitHub Docs, *Using custom workflows with GitHub Pages*
  - https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

概念的にはこうなる。

```text
build
  ↓
test
  ↓
upload validated artifact
  ↓
deploy
```

この形の良いところは、**testしたartifactとdeployするartifactの差を小さくできる**ことだ。

理想は、

```text
build once
→ test that artifact
→ store that artifact
→ promote that artifact
```

である。

## release条件はquality gateへ混ぜない

GitHub ActionsのEnvironmentは、deployment固有の条件を別contractとして扱える。

公式ドキュメントでは、

- required reviewers
- wait timer
- deployment branch / tag restrictions
- custom deployment protection rules
- environment secrets

をdeployment protectionとして扱っている。

- GitHub Docs, *Deployments and environments*
  - https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
- GitHub Docs, *Deploying with GitHub Actions*
  - https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments

つまり、

```text
quality gate
- lint
- type check
- unit test
- build
- local browser test

release gate
- branch
- permission
- approval
- secret
- environment readiness
```

は別物である。

前者が落ちたらcodeを直す。
後者が落ちたらrelease条件を直す。

## production URLがなくてもWebとして検証できる

「公開URLがないからWeb testできない」も、多くの場合は言い過ぎである。

Playwrightは `webServer` optionを公式に提供している。
その用途として、stagingやproduction URLがまだない開発時のlocal server testingを明示している。

- Playwright Docs, *Web server*
  - https://playwright.dev/docs/test-webserver

静的siteならdeploy前でも、

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

**公開できないことと、検証できないことは同義ではない。**

## 小さな追試: Pages未設定でもvalidationは通せた

ここまでの一般原則を、小さなGitHub Pages repositoryでも再現できるか試した。

`KAFKA2306/finBI` では2026年8月13日にworkflowを `validate` と `deploy` に分離した。

- commit
  - https://github.com/KAFKA2306/finBI/commit/bc928ab7806c727086992df838f8ccae62f58040
- workflow run
  - https://github.com/KAFKA2306/finBI/actions/runs/31672724045

この時点ではGitHub Pagesが有効ではなかった。

それでも `validate` jobでは、

- Python compile
- offline unit tests
- browser asset checks
- static site build
- localhost HTTP route smoke test
- generated residue cleanup
- clean checkout assertion

がすべて成功した。

一方、`deploy` jobではPagesが利用可能かを確認した後、

- Build Pages artifact
- Configure Pages
- Upload Pages artifact
- Deploy Pages

がすべてskipされた。

つまり結果は、

```text
artifact quality        = passed
deployment availability = unavailable
```

だった。

Pages未設定という1つの環境問題のために、検証可能な品質情報まで捨てずに済んだ。

## Pagesが有効になると、同じ境界のままproductionまで進んだ

その後Pagesが有効になり、workflowには `public-e2e` が追加された。

Run #27では、

```text
validate     success
    ↓
deploy       success
    ↓
public-e2e   success
```

まで通った。

- current workflow
  - https://github.com/KAFKA2306/finBI/blob/main/.github/workflows/static-bi.yml
- workflow run #27
  - https://github.com/KAFKA2306/finBI/actions/runs/31825777595

この事例の価値は、`finBI` がbest practiceの起源だったことではない。

**Google、GitHub、Shopifyが大規模releaseで使っている「stageを分ける」という原則を、小さなPagesでも再現できたこと**にある。

## そして追試には改善点もある

現在の `finBI` workflowは、`validate` でpublic rootをbuildしてsmoke testした後に削除し、`deploy` jobでもう一度Pages artifactをbuildしている。

動作はしているが、一般的な設計としてはさらに改善できる。

GitHub Pages公式例のように、

```text
build once
    ↓
test the artifact
    ↓
upload the artifact
    ↓
deploy the same artifact
```

へ寄せた方がよい。

「検証したもの」と「本番へ出したもの」の差を減らせるからだ。

成功例を載せるときこそ、成功した実装をそのまま正解扱いしない。

**実例は原則を検証する材料であり、原則そのものではない。**

## まず既存CI/CDを直すなら、この8項目を見る

1. PRでもbuild / testが必ず動くか
2. deploy失敗でtest結果まで意味不明になっていないか
3. deployはvalidation成功後だけに進むか
4. buildした成果物をHTTPやbrowserで実際に確認しているか
5. 可能なら検証したartifactそのものをdeployしているか
6. release permissionやapprovalをquality testと分離しているか
7. productionへ出した後にもhealth / E2E確認があるか
8. failed / validated / blocked / deployed / verifiedを区別できるか

GitHub Pagesなら、最小形はこれでよい。

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

toolは変わってよい。

RuffでもBiomeでもPlaywrightでもcurlでもよい。

守りたいのはtool名ではなく、contractの意味である。

```text
Build    = 同じinputから成果物を作れる
Validate = その成果物を出してよい
Release  = 今この環境へ出してよい
Verify   = 実際に出したものが使える
```

## 速いreleaseは、gateが少ないreleaseではない

GitHubはCIが終わる前のdeployを拒否した。

Shopifyは5%のtrafficで止めてからProductionへ進めた。

Google SREは再現可能なbuild、自動test、自動deploy、small deploymentをrelease engineeringの原則としている。

DORAはdelivery performanceをthroughputだけでなくinstabilityと一緒に測っている。

2026年のGitHubは、障害時にdeployを妨げる隠れたnetwork dependencyまで機械的に検出している。

共通するのは、慎重さではない。

**次へ進める条件を明示し、その判定を再現可能にすることだ。**

```text
検証できることは先に検証する
        ↓
通った成果物だけをrelease候補にする
        ↓
release可能な環境へだけdeployする
        ↓
productionでしか分からないことを最後に確認する
```

公開環境がないからtestしないのではない。

**testを通ったものだけを、公開できるときに公開する。**

それが、速さと安全性を同時に上げるRelease Engineeringの基本形である。

## 一次情報

- Google SRE, *Release Engineering*
  - https://sre.google/sre-book/release-engineering/
- Google SRE Workbook, *Canarying Releases*
  - https://sre.google/workbook/canarying-releases/
- DORA, *A history of DORA’s software delivery metrics*
  - https://dora.dev/insights/dora-metrics-history/
- DORA, *DORA’s software delivery performance metrics*
  - https://dora.dev/guides/dora-metrics/
- GitHub Engineering, *Deploying branches to GitHub.com*
  - https://github.blog/engineering/engineering-principles/deploying-branches-to-github-com/
- GitHub Engineering, *How GitHub uses merge queue to ship hundreds of changes every day*
  - https://github.blog/engineering/engineering-principles/how-github-uses-merge-queue-to-ship-hundreds-of-changes-every-day/
- GitHub Engineering, *How GitHub uses eBPF to improve deployment safety*
  - https://github.blog/engineering/infrastructure/how-github-uses-ebpf-to-improve-deployment-safety/
- Shopify Engineering, *Software Release Culture at Shopify*
  - https://shopify.engineering/software-release-culture-shopify
- GitHub Docs, *Using custom workflows with GitHub Pages*
  - https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- GitHub Docs, *Deployments and environments*
  - https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
- GitHub Docs, *Deploying with GitHub Actions*
  - https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments
- Playwright Docs, *Web server*
  - https://playwright.dev/docs/test-webserver
