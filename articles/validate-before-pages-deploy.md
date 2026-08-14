---
title: "公開設定がまだでも品質確認は止めない。CI/CDを「成果物」と「公開可否」に分ける"
emoji: "🚦"
type: "tech"
topics: ["githubactions", "githubpages", "ci", "testing"]
published: false
published_at: 2026-08-13 16:04
---

Webサイトを作った。

HTMLもJavaScriptもある。

テストも書いた。

しかしGitHub Pagesの設定だけがまだ終わっていない。

このとき、deployできないからCI全体を赤くすると、別の問題が起きる。

**成果物が壊れているのか、公開環境が未準備なのか分からなくなる。**

逆に、Pagesが無効なら全部skipして成功扱いにすると、壊れたHTMLやJavaScriptまで見逃す。

`KAFKA2306/finBI` では、ここを2つのcontractへ分けた。

```text
成果物は正しいか？
        ↓
validate

今この環境へ公開できるか？
        ↓
deploy
```

Pages設定がなくても `validate` は必ず走る。

成果物が正常で、公開環境だけ未準備なら、**品質確認は成功、公開だけskip** にする。

この記事で扱うのはGitHub Pagesの設定方法ではない。

**環境準備の事情に開発品質まで巻き込まず、今確認できることを最後まで確認するCI/CD UX**について書く。

- 実装commit: https://github.com/KAFKA2306/finBI/commit/bc928ab7806c727086992df838f8ccae62f58040
- workflow: https://github.com/KAFKA2306/finBI/blob/bc928ab7806c727086992df838f8ccae62f58040/.github/workflows/static-bi.yml

## 「公開できない」と「壊れている」を同じfailureにしない

`finBI` のworkflowでは、PRでもmainでも最初に `validate` を実行する。

ここでは次を確認する。

- Python compile
- offline unit tests
- JavaScript syntax
- CSS / accessibility contract
- static site build
- HTTP route smoke test
- generated residue cleanup
- clean checkout assertion

その後にだけ `deploy` jobがある。

```text
validate
   ↓ success
check deploy capability
   ├─ unavailable → deploy skip
   └─ available   → deploy
```

状態は少なくとも次の4つへ分けられる。

| 成果物 | 公開環境 | 結果 |
|---|---|---|
| broken | available | validate failure |
| broken | unavailable | validate failure |
| valid | unavailable | validated / deploy skipped |
| valid | available | validated / deployed |

この表で重要なのは、**Pages未設定でも壊れた成果物は必ず赤くなる**ことだ。

skipは品質検査の代わりではない。

## 1つのjobへ全部入れると、failure reasonが混ざる

例えば次のworkflowは単純である。

```yaml
jobs:
  build-and-deploy:
    steps:
      - run: ./test.sh
      - uses: actions/configure-pages@v6
      - uses: actions/upload-pages-artifact@v5
      - uses: actions/deploy-pages@v5
```

しかしこのjobが失敗したとき、利用者には次が同じ赤として見える。

```text
unit test failure
JavaScript syntax error
build failure
Pages disabled
permission missing
deploy service failure
```

赤いことは分かる。

何を直せばよいかは分かりにくい。

そこで、**品質のfailureとdelivery capabilityのfailureを別のstateへする。**

## validateは公開環境へ依存させない

`validate` の価値は、いつでも同じ入力から同じ品質検査ができることにある。

```text
checkout
  ↓
compile
  ↓
test
  ↓
static checks
  ↓
build
  ↓
local HTTP smoke
  ↓
cleanup
  ↓
clean checkout
```

Pages APIへ接続できなくても、ここまでは確認できる。

だから確認する。

**外部環境が未準備だからといって、ローカルに証明できる品質まで諦めない。**

## deployはvalidate成功後だけにする

deploy側は `needs: validate` で接続する。

これにより、公開環境が有効でも成果物が壊れていれば進まない。

```text
broken artifact
→ deployしない
```

一方、artifactが正常でもPagesが未設定なら、

```text
valid artifact
→ deploy capability unavailable
→ publish stepのみskip
```

にする。

ここで `skip` を「全部成功した」に見せないことも重要である。

ログやsummaryでは、

```text
validation: passed
deployment: skipped
reason: Pages is not configured
```

のように状態を分ける方がよい。

## buildできたら終わりではない。HTTPで実際に開く

静的siteでは、build commandが0で終わってもrouteが壊れていることがある。

そこで `finBI` は公開用directoryを作った後、`python -m http.server` と `curl` でrouteを確認する。

重要なのは、deploy前に

> 実際に配信される形のdirectoryをHTTP経由で読めるか

を見ることだ。

```text
source validation
   ↓
static build
   ↓
local HTTP serving
   ↓
route smoke
```

build successとcontent delivery successを分ける。

## 検証後のrepositoryが汚れていたら、まだ完了ではない

ここでもう1つ、別のfailure modeがある。

buildやtestは正常系でもfileを生成する。

例えば、

```text
site/
__pycache__/
```

がcheckoutへ残る。

テストがgreenでも、検証後のrepository stateが変わっていれば、再実行性や差分監査を壊すことがある。

そこでworkflowの最後に、

1. 既知の生成物をcleanupする
2. `git status` で差分がないことをassertする

という順序を置く。

```yaml
- name: Remove generated residue
  run: |
    rm -rf site
    find . -type d -name __pycache__ -prune -exec rm -rf {} +

- name: Verify clean checkout
  run: test -z "$(git status --porcelain --untracked-files=all)"
```

ここで、cleanupとassertを同じものにしない。

```text
cleanup = 状態を戻す操作
status  = 本当に戻ったかの検証
```

**「片付けたつもり」を完了条件にしない。**

## `.gitignore` へ入れるだけでは解決しないことがある

生成物をignoreすればCIは赤くならない。

しかし、runner上には残る。

別stepがその残骸を読む可能性もある。

だから、

```text
ignore
```

と、

```text
cleanup + clean-state assertion
```

は役割が違う。

もちろん、すべてのworkflowでcheckoutを完全にcleanにする必要はない。

重要なのは、**何をfinal stateとして約束するかを明示すること**だ。

## 4つのstateを別々に見せると運用しやすい

CI/CDでは、少なくとも次を混ぜない方がよい。

```text
FAILED
  成果物が壊れている

VALIDATED
  成果物は正しい

DEPLOY_SKIPPED
  公開環境が未準備 / 条件外

DEPLOYED
  公開まで完了
```

このstateがあると、dashboardやissueから見ても次のactionが分かる。

```text
FAILED
→ codeを直す

VALIDATED + DEPLOY_SKIPPED
→ environment設定を直す

DEPLOYED
→ production verificationへ進む
```

**次に何をすべきかが状態から分かる。**

## Pages以外でも同じ

この分離は、GitHub Pages特有ではない。

例えば、

- staging credential未設定
- production approval待ち
- cloud account未作成
- domain未設定
- secret未投入
- deployment window外

でも同じである。

```text
artifact validity
```

と、

```text
deployment availability
```

は別の軸である。

環境がまだないからテストしない、という設計にすると開発初期ほど品質feedbackが遅れる。

逆に、検証だけ独立していれば、公開準備前から品質を上げられる。

## skipを便利な逃げ道にしない

条件付きjobは便利だが、skip条件が広すぎると壊れた成果物まで見逃す。

悪い形は、

```text
Pages disabled
→ whole workflow skipped
```

である。

良い形は、

```text
validate = unconditional quality gate

deploy = conditional delivery step
```

にすることだ。

**skipできるのはdeliveryだけ。qualityはskipしない。**

この境界を守ると、環境依存の例外が増えてもCIの意味が薄まりにくい。

## まず既存workflowを1つ直すなら

現在のCI/CDで次を確認する。

1. testとdeployが同じjobに入っていないか
2. deploy環境がないとtestまでskipしていないか
3. build後に実配信形でsmoke testしているか
4. generated residueをcleanupしているか
5. final checkout stateをassertしているか
6. `failed / validated / skipped / deployed` を区別できるか

全部を一度に変える必要はない。

最初は `validate` jobを独立させるだけでもよい。

## この設計で得たいのは、green CIではなく「何が完了したか分かる」こと

CIがgreenでも、deployされていないことはある。

CIがredでも、成果物自体は正しいことがある。

この2つを同じ色だけで表すと、運用者は毎回ログを読まなければならない。

だから、

- 成果物品質
- 公開可否
- 実際のdeploy
- 最終repository state

を別々に検証する。

公開設定がまだでも、品質確認はできる。

**今証明できることは今証明し、できないことだけを未完了として残す。**

その方が、開発を止めずに品質を積み上げやすい。
