---
title: "「Push on Green」を誤解しない。GitHub Pagesで学ぶ、検証とデプロイを分離するCI/CD"
emoji: "🚦"
type: "tech"
topics: ["cicd", "githubactions", "githubpages", "testing", "sre"]
published: false
published_at: 2026-08-13 16:04
---

> **“Push on Green”**

Google SREのRelease Engineeringに出てくる有名な表現だ。

意味は、単に「CIが緑なら本番へ出す」ではない。
Googleでは、**すべてのテストを通ったbuildをdeployする**運用モデルとして説明されている。

- Google SRE, *Release Engineering*: https://sre.google/sre-book/release-engineering/

ここで重要なのは `Push` より **Greenの定義** である。

Google SRE WorkbookがRelease Engineeringの基本原則として並べるのは、

> **“Reproducible builds / Automated builds / Automated tests / Automated deployments”**

である。

- Google SRE Workbook, *Canarying Releases*: https://sre.google/workbook/canarying-releases/

つまり、一般的な順序はこうなる。

```text
再現可能にbuildする
        ↓
自動でtestする
        ↓
合格した成果物をdeployする
        ↓
productionで確認する
```

**deployは品質確認そのものではない。品質確認を通過した後段である。**

この原則は、大規模サービスだけの話ではない。
GitHub Pagesのような小さな静的サイトでも、そのまま使える。

## GitHub自身もbuildとdeployを分けている

GitHub Pagesの公式ドキュメントには、そのまま

> **“Linking separate build and deploy jobs”**

という節がある。

公式例は `build` と `deploy` を別jobにし、`deploy` に `needs: build` を置く。
さらにPagesへのdeploymentは `github-pages` environmentに結びつける。

- GitHub Docs, *Using custom workflows with GitHub Pages*: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- GitHub Docs, *Using jobs in a workflow*: https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs

GitHubのpublishing sourceの説明も、Pull Requestではbuildまでは行い、deploy stepはskipする流れを示している。

- GitHub Docs, *Configuring a publishing source for your GitHub Pages site*: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

ここから導ける一般原則は単純である。

```text
Pull Request
   ↓
validate / build / test
   ↓
artifact
   ↓
main・権限・environmentなどの条件を満たしたときだけdeploy
   ↓
production verification
```

**「公開できるか」と「公開してよい品質か」は別の問いとして扱う。**

## CI/CDで混ぜない方がよい4つの状態

CIを1個の赤/緑だけで見ると、原因が違う状態を同じものとして扱ってしまう。

| 状態 | 意味 | 次のaction |
|---|---|---|
| validation failed | 成果物が壊れている | code / test / buildを直す |
| validated, deploy unavailable | 成果物は通ったが公開条件がない | environment / permission / Pages設定を直す |
| deployed, production check failed | deployは完了したが公開結果が壊れている | routing / base path / runtime差分を直す |
| validated and deployed | 検証と公開確認の両方を通過 | release完了 |

この区別があると、ログを全部読まなくても「次に誰が何を直すべきか」が分かる。

## stagingやproductionがなくても、Webとして検証できる

「公開URLがまだないからE2Eできない」も、必ずしも正しくない。

Playwrightは `webServer` を使ったlocal server testingを公式に用意しており、

> **“when you don't have a staging or production url to test against”**

という状況を明示的な用途として挙げている。

- Playwright Docs, *Web server*: https://playwright.dev/docs/test-webserver

静的サイトなら、deploy前に少なくとも次は確認できる。

```text
build outputを作る
   ↓
localhostでHTTP配信する
   ↓
主要routeを開く
   ↓
CSS / JS / data assetを取得する
   ↓
必要ならbrowser testを走らせる
```

build commandがexit 0だったことと、**Webとして配信できることは同じではない。**

だから、公開環境がなくても「今その場で証明できること」は先に証明する。

## deployment固有の条件はenvironment側へ寄せる

productionへのdeployには、品質とは別の条件がある。

GitHub ActionsのEnvironmentでは、required reviewers、branch制限、wait timer、custom deployment protection rule、environment secretsなどをdeployment gateとして扱える。

- GitHub Docs, *Deployments and environments*: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments

これは重要な分離である。

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
- secret / permissionが利用可能である
```

前者が落ちたら成果物を直す。
後者が満たせなければrelease条件を整える。

同じfailureにしない方が、復旧が速い。

## 実例: Pages未設定でもvalidationを止めなかった

この設計を `KAFKA2306/finBI` で試した。

2026年8月13日のcommitでは、workflowを `validate` と `deploy` に分離した。

- commit: https://github.com/KAFKA2306/finBI/commit/bc928ab7806c727086992df838f8ccae62f58040
- workflow run #5: https://github.com/KAFKA2306/finBI/actions/runs/31672724045

Run #5では `validate` が成功した。

検証内容は、

- Python compile
- offline unit tests
- browser asset checks
- static site build
- localhost HTTP route smoke test
- generated residue cleanup
- clean checkout assertion

だった。

一方、この時点ではGitHub Pagesが有効ではなかった。
そのため `deploy` job内の

```text
Build Pages artifact
Configure Pages
Upload Pages artifact
Deploy Pages
```

はすべてskipされた。

ここで重要なのは、**Pages未設定でもvalidation結果は失われなかった**ことだ。

```text
artifact quality = passed
deployment capability = unavailable
```

という2つの事実を同時に残せた。

## その後Pagesが有効になると、同じ境界のままproductionまで進めた

その後Pagesが利用可能になり、workflowは `public-e2e` まで拡張された。

2026年8月15日のRun #27では、

```text
validate     success
    ↓
deploy       success
    ↓
public-e2e   success
```

まで通っている。

- current workflow: https://github.com/KAFKA2306/finBI/blob/main/.github/workflows/static-bi.yml
- workflow run #27: https://github.com/KAFKA2306/finBI/actions/runs/31825777595

`validate` ではfast quality gates、public root build、HTTP smoke test、clean checkoutを確認し、`deploy` 後にはdesktop/mobile幅で公開Pagesを確認している。

これは「Pages未設定時だけの特殊な逃げ道」ではなかった。

**公開前の検証と公開後の検証を別stageにしたことで、環境が未準備な時期から、環境が整った後まで同じ考え方を維持できた。**

## ただし、この実例にも改善余地がある

`finBI` の現在のworkflowは、`validate` でpublic rootをbuildしてsmoke testした後に削除し、`deploy` でPages artifactをもう一度buildしている。

一般論としては、GitHub Pages公式例のように、**検証したbuild artifactをuploadし、そのartifactを後段のdeployが使う**方が境界はさらに明確になる。

```text
build once
   ↓
test that artifact
   ↓
store that artifact
   ↓
deploy that artifact
```

「テストしたもの」と「本番へ出したもの」の差を小さくできるからだ。

ここは `finBI` の成功例を一般化するときに、むしろ隠さない方がよい。

**実例はbest practiceの証拠にはなるが、実例そのものをbest practiceだと思わない。**

公式設計と照合し、ずれている部分は次の改善点として扱う。

## 実務で使うなら、この7項目から始める

1. **PRでもvalidationを必ず走らせる**
2. **deployはvalidation成功後だけにする**
3. **build/testとdeployment permissionを別job・別gateにする**
4. **build outputをlocalhostで実際に配信して確認する**
5. **可能なら検証済みartifactそのものをdeployする**
6. **production URLはdeploy後に別のE2Eで確認する**
7. **failed / validated / deploy skipped / deployed / production failedを区別する**

GitHub Pagesなら、概念的には次の形になる。

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

細かなtoolは変わってよい。
RuffでもBiomeでもPlaywrightでもcurlでもよい。

変えない方がよいのはstageの意味である。

```text
validate = これは出してよい成果物か

deploy = この環境へ今出してよいか

production test = 実際に出したものは利用可能か
```

## Greenは「deploy commandが成功した色」ではない

Googleの **“Push on Green”** を小さなWeb開発へ持ち込むなら、覚えるべきなのは自動deployの格好良さではない。

**何を通過したらGreenと呼べるのかを、先に設計することだ。**

GitHub Pagesがまだ無効でも、unit testはできる。
静的buildもできる。
localhostでHTTP配信もできる。
browser testもできる。

Pagesが有効になったら、その検証済み成果物をdeployすればよい。
そして最後にproductionを確認する。

```text
Build → Test → Deploy → Verify
```

これはGitHub Pages専用の小技ではない。
Google SREのrelease engineering、GitHub Actionsのjob dependency、GitHub Pagesの公式workflow、Playwrightのlocal web server testingが同じ方向を指している。

**公開できないから検証しないのではなく、検証できたものだけを公開する。**

その方が再現可能で、失敗理由が明確で、次のactionも決めやすい。

## 一次情報

- Google SRE, *Release Engineering*: https://sre.google/sre-book/release-engineering/
- Google SRE Workbook, *Canarying Releases*: https://sre.google/workbook/canarying-releases/
- GitHub Docs, *Using custom workflows with GitHub Pages*: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- GitHub Docs, *Configuring a publishing source for your GitHub Pages site*: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- GitHub Docs, *Using jobs in a workflow*: https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs
- GitHub Docs, *Deployments and environments*: https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
- Playwright Docs, *Web server*: https://playwright.dev/docs/test-webserver
