---
title: "テストが通っても作業ツリーが汚れていたら未完了：CIの最後にclean checkoutを置く"
emoji: "🧹"
type: "tech"
topics: ["githubactions", "ci", "git", "testing"]
published: false
---

CIではテスト成功と、検証後のrepository状態がcleanであることは別の契約です。公開repository `KAFKA2306/finBI` の2026年8月13日のworkflowを題材に、final-state assertionを設計します。

## 1. 問題

実装ではPython compile、unit test、JavaScript syntax check、静的site build、HTTP smoke testを実行します。その途中で `site/` や `__pycache__` が生成されます。テストが成功しても、それらが残らないことまでは保証しません。

一次情報:
- https://github.com/KAFKA2306/finBI/commit/bc928ab7806c727086992df838f8ccae62f58040
- https://github.com/KAFKA2306/finBI/blob/bc928ab7806c727086992df838f8ccae62f58040/.github/workflows/static-bi.yml

実際の状況では `site/` にHTML、JavaScript、CSS、snapshot、Python moduleをコピーしてHTTP smoke testを行います。生成は正常系ですが、検証後に残してよいとは限りません。

## 2. 原因

CIは各commandのexit codeを主に観測します。buildやtestがcheckout内へファイルを生成しても、最終状態を観測するstepがなければ検出できません。

そこで behavioral state と repository state を分離します。前者はcompile/test/smoke testの成功、後者は検証終了後のtracked/untracked fileの状態です。

## 3. 設計判断と代替案

採用する順序は「生成を伴う検証 → 既知の生成物をcleanup → git statusで最終状態をassert」です。

代替案として `.gitignore` へ追加する方法はありますが、残骸自体は残ります。runnerの一時directoryでbuildする方法は強い分離ですが、公開directory構造をcheckout相対で再現する場合には設定が増えます。cleanupだけで終了する方法も、取りこぼしを検出できません。

したがってcleanupは操作、`git status` は検証として分離します。

## 4. 実装

```yaml
- name: Remove generated residue
  run: |
    rm -rf site
    find . -type d -name __pycache__ -prune -exec rm -rf {} +

- name: Verify clean checkout
  run: test -z "$(git status --porcelain --untracked-files=all)"
```

このgateが確認するのはrepository checkoutにGitが報告する差分がないことです。runner全体の副作用ゼロを証明するものではありません。

## 5. 検証

読者が試せる最小再現です。

```bash
git init clean-gate-demo
cd clean-gate-demo
printf 'hello\n' > source.txt
git add source.txt
git -c user.name=demo -c user.email=demo@example.invalid commit -m init
printf 'generated\n' > build.tmp
git status --porcelain --untracked-files=all
```

`build.tmp` が表示されるため、次のassertionは失敗します。

```bash
test -z "$(git status --porcelain --untracked-files=all)"
```

改善後は `rm build.tmp` の後に同じassertionを置きます。処理成功とcheckout復元を別々に確認できます。

## 6. 失敗と学び

壊れた失敗例はclean gateを処理の前だけに置くことです。

```yaml
- run: test -z "$(git status --porcelain --untracked-files=all)"
- run: ./test-that-generates-files.sh
```

これでは開始時点がcleanだったことしか確認できません。副作用を検査するgateは、副作用を起こし得る処理の後に置く必要があります。

また、GitHub公式はcacheをrun間で再利用する依存物や再生成可能な中間物、artifactをrun後に保存・job間で共有するbuild output等として区別しています。意図して保存するcache/artifactと、意図せずcheckoutに残ったfileは別の設計対象です。

- https://docs.github.com/en/actions/concepts/workflows-and-actions/dependency-caching
- https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts

## 7. 再現方法

自分のrepositoryで通常のtest/build後に次を実行します。

```bash
./your-test-command
git status --porcelain --untracked-files=all
```

表示されたものを「commitすべきsource」「意図的なcache/artifact」「終了時に削除すべき一時生成物」に分類します。3つ目をcleanupし、最後にclean assertionを置きます。

さらに一度だけ意図的にuntracked fileを残し、gateがfailすることを確認します。成功例だけでなく、壊したときに閉じることまで確認するとgate自体を検証できます。

## まとめ

テスト成功とclean checkoutは別契約です。必要な生成を行い、既知の一時生成物を消し、最後にrepository状態をassertする。この小さなfinal-state gateで、検証プロセス自身がrepositoryを汚す退行を検出できます。
