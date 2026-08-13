---
title: "公開設定がまだでも、テストまで止めない。検証とデプロイを分離する"
emoji: "🚦"
type: "tech"
topics: ["githubactions", "githubpages", "ci", "testing"]
published: false
published_at: 2026-08-13 16:04
---

Webサイトを作った直後、GitHub Pagesの設定がまだ終わっていない。

このとき「デプロイできないからCI全体を失敗させる」と、HTMLやJavaScriptの破損まで検証できなくなる。逆に「Pagesが無効なら全部成功扱い」にすると、壊れた成果物を見逃す。

`KAFKA2306/finBI` の2026年8月13日の公開実装では、この2つを分離している。`validate` はPages設定に依存せず必ず成果物を検証し、`deploy` はその成功後だけ進む。さらにPages自体が未設定なら、公開処理だけを意図的にskipする。

一次情報:

- 実装commit: https://github.com/KAFKA2306/finBI/commit/bc928ab7806c727086992df838f8ccae62f58040
- workflow: https://github.com/KAFKA2306/finBI/blob/bc928ab7806c727086992df838f8ccae62f58040/.github/workflows/static-bi.yml
- GitHub Pages custom workflows: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- GitHub Actions job conditions: https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions
- GitHub Pages publishing source: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

この記事では、**「成果物が正しいか」と「今この環境へ公開できるか」を別の判定にする**方法として整理する。

## 1. 問題：公開できないことと、成果物が壊れていることは別

### 実際の入力・状況

`finBI` のworkflowは、PRでもmainでもまず `validate` jobを実行する。ここでは次を検証している。

- `python -m py_compile code/static_bi.py`
- Pythonのoffline unit tests
- `node --check` によるJavaScript構文検証
- CSSとアクセシビリティ契約の最低限チェック
- 公開用directoryのbuild
- `python -m http.server` と `curl` によるroute smoke test
- 生成物削除後のclean checkout

その後にだけ `deploy` jobがあり、`needs: validate` で接続されている。

つまり入力状態は2軸ある。

| 成果物 | Pages設定 | 扱い |
|---|---|---|
| 壊れている | 有効/無効 | `validate` を失敗させる |
| 正常 | 無効 | `validate` 成功、公開処理だけskip |
| 正常 | 有効 | `validate` 成功後にdeploy |

重要なのは、**Pages未設定を「成果物の失敗」に変換しない**ことだ。

## 2. 原因：CIとCDを1つの成否に潰すと、失敗理由が混ざる

壊れた設計は、たとえば次のようになる。

```yaml
jobs:
  build-and-deploy:
    steps:
      - run: ./test.sh
      - uses: actions/configure-pages@v6
      - uses: actions/upload-pages-artifact@v5
      - uses: actions/deploy-pages@v5
```

これは単純だが、Pages設定が未完了なら、テスト済み成果物まで「失敗したworkflow」に見える。反対に、Pagesがない環境ではjob全体をskipする設計にすると、`./test.sh` まで消える。

原因は、次の2問を同じbooleanにしていることにある。

1. このcommitから作った成果物は正しいか
2. このrepositoryは今、公開可能な状態か

前者はコード品質の判定、後者はdeployment capabilityの判定である。ライフサイクルが違う。

## 3. 設計判断と代替案：validateを無条件、deployを条件付きにする

今回の設計判断は次の順序だ。

```text
source
  ↓
validate ──失敗──> stop
  ↓成功
deploy job
  ↓
Pages capability check
  ├─ disabled → deployment stepsだけskip
  └─ enabled  → build artifact → configure → upload → deploy
```

GitHub公式ドキュメントでも、Pagesのcustom workflowはbuildとdeployを別jobにでき、deploy側を `needs` でbuildへ接続できる。また `jobs.<job_id>.if` / step-level `if` で条件付き実行ができる。

### 代替案A：Pages有効化までworkflowを作らない

採用しない。公開設定と無関係なsyntax、unit test、route smoke testを早期に固定できない。

### 代替案B：Pagesが無効ならworkflow全体をskip

採用しない。deployment capabilityがvalidation coverageを消してしまう。

### 代替案C：Pages未設定をfailureにする

本番公開が必須のrepositoryなら合理的な場合もある。しかし初期構築中やfork可能なtemplateでは、「コードが壊れた」と「環境設定が未完了」を区別したほうが原因を追いやすい。

## 4. 実装：成果物検証をdeploy actionより前に閉じる

最小形はこうなる。

```yaml
name: site

on:
  push:
    branches: [main]
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - run: ./test.sh
      - run: ./build.sh site
      - run: ./smoke-test.sh site
      - run: rm -rf site
      - run: test -z "$(git status --porcelain --untracked-files=all)"

  deploy:
    if: github.event_name != 'pull_request'
    needs: validate
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v7
      - name: Check deployment capability
        id: pages
        run: |
          # repository固有の方法で capability を判定し、
          # enabled=true/false を GITHUB_OUTPUT へ書く
          echo 'enabled=false' >> "$GITHUB_OUTPUT"

      - name: Build Pages artifact
        if: steps.pages.outputs.enabled == 'true'
        run: ./build.sh site

      - name: Configure Pages
        if: steps.pages.outputs.enabled == 'true'
        uses: actions/configure-pages@v6

      - name: Upload artifact
        if: steps.pages.outputs.enabled == 'true'
        uses: actions/upload-pages-artifact@v5
        with:
          path: site

      - name: Deploy
        if: steps.pages.outputs.enabled == 'true'
        id: deployment
        uses: actions/deploy-pages@v5
```

ここで例のcapability checkは意図的にダミーにしている。`finBI` の実装はGitHub REST APIのrepository Pages endpointを呼び、HTTP 200なら `enabled=true`、それ以外ならfalseとしている。認証方法や「どのstatus codeを未設定として許容するか」はrepositoryのポリシーとして別途決めるべきなので、記事の汎用例では断定しない。

GitHub公式のPages custom workflowでは、deploy jobに `pages: write` と `id-token: write` が必要で、`environment` とdeploy actionを使う構成が示されている。

## 5. 検証：公開前にローカルHTTPまで通す

`finBI` が有用なのは、単に `node --check` で終わらず、公開directoryを一度作ってHTTPで読むところまで `validate` に入れている点だ。

```bash
python -m http.server 8123 -d site >/tmp/site-http.log 2>&1 &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null || true' EXIT
sleep 1
curl --fail --silent http://127.0.0.1:8123/ >/dev/null
curl --fail --silent http://127.0.0.1:8123/styles.css >/dev/null
```

これなら、source treeにファイルが存在するだけでなく、**実際の公開rootへコピーされたか**まで検査できる。

GitHub公式ドキュメントでは、条件がfalseのjobはskippedとなり、skipped jobはSuccessとして報告される。したがって「skipしたから品質確認済み」と誤読しないためにも、品質検証を別の `validate` jobとして残す意味がある。

### 改善後の例

- CSSをbuild対象へコピーし忘れた → route smoke testが失敗する
- Pagesがまだ無効 → validationは成功し、deployment stepsだけ走らない
- Python coreがcompile不能 → Pages状態に関係なくvalidationが失敗する

この3つを別の結果として観測できる。

## 6. 失敗と学び：skipは成功の証明ではない

### 壊れた失敗例

最も危険なのは、次のように「公開できないなら検証もしない」とすることだ。

```yaml
validate-and-deploy:
  if: vars.PAGES_ENABLED == 'true'
```

この条件がfalseなら、壊れたHTMLやJavaScriptがあってもjob自体が走らない。

GitHub公式ドキュメントは、条件でskipされたjobがSuccessとして報告され、required checkでもmergeを妨げないと説明している。したがって、**緑色は必ずしも検証実行済みを意味しない**。

学びは単純である。

- validationは「コードから決まる」
- deploymentは「コード + 環境状態から決まる」
- 環境依存条件はvalidationの外側へ置く

なお、`finBI` のcommit message自体も、公開Pages E2Eはrepository Pages有効化に依存すると明記している。つまり、このworkflowが証明するのは静的成果物の検証までであり、未実行の公開E2Eまで成功したとは扱わない。

## 7. 再現方法：Pagesを有効にする前にCIの境界を試す

読者が試す最小再現は、GitHub Pagesを実際に公開しなくてもよい。

1. 空のrepositoryに `index.html`、`styles.css`、`test.sh`、`build.sh`、`smoke-test.sh` を置く
2. `validate` と `deploy` を別jobにする
3. deploy capabilityを最初は `enabled=false` に固定する
4. PRを作り、`validate` が実行されることを確認する
5. `build.sh` から `styles.css` のcopyを削除し、`validate` が失敗することを確認する
6. copyを戻し、`validate` をgreenへ戻す
7. capabilityをtrueにする前に、Pagesのrepository設定と必要permissionを公式手順で構成する
8. その後だけdeployを試す

期待する状態遷移は次の通り。

```text
Pages disabled + artifact valid   -> validation success / deploy skipped
Pages disabled + artifact broken  -> validation failure
Pages enabled  + artifact broken  -> validation failure / deploy blocked by needs
Pages enabled  + artifact valid   -> deploy eligible
```

この構造なら、公開先がまだ存在しなくてもCIを育てられる。そして公開可能になった瞬間も、すでに検証済みの境界からdeployを接続できる。

## まとめ

CI/CDを単純化するとは、すべてを1jobに押し込むことではない。

**成果物の正しさは環境設定なしで検証し、環境依存の公開処理だけを後段へ隔離する。**

これで「Pagesがないから赤」と「Pagesがないから何も検証していない」の両方を避けられる。公開設定が後から来る小さな静的サイト、template repository、fork前提のプロジェクトでも再利用しやすい境界になる。