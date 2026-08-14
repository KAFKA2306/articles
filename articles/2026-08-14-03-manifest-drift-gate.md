---
title: "CIが自分で直してからgreenになる。manifestの「更新忘れ」を差分で止める"
emoji: "🧾"
type: "tech"
topics: ["python", "githubactions", "dataengineering", "testing", "ci"]
published: false
---

元データだけ更新して、manifestの更新を忘れた。

本来ならCIに止めてほしい。

しかしCIが最初にmanifestを再生成すると、古かったmanifestを自分で最新へ直してから検証できてしまう。

```text
checkout時点
artifact = new
manifest = old

CI
  ↓ manifestを再生成
artifact = new
manifest = new
  ↓ verify
PASS
```

結果はgreen。

でも、PRにcommitされていた状態は不完全だった。

`KAFKA2306/semiconductor-earnings-model` では、この「勝手に直してからgreen」を防ぐため、manifestの正しさと**commit漏れがないこと**を別々に検証している。

- builder: https://github.com/KAFKA2306/semiconductor-earnings-model/blob/7595f0b0b7f7535d9eaea182fe5f2ba415bce8f4/scripts/build_earnings_lineage_manifest.py
- workflow: https://github.com/KAFKA2306/semiconductor-earnings-model/blob/7595f0b0b7f7535d9eaea182fe5f2ba415bce8f4/.github/workflows/earnings-lineage.yml
- verifier: https://github.com/KAFKA2306/semiconductor-earnings-model/blob/7595f0b0b7f7535d9eaea182fe5f2ba415bce8f4/scripts/verify_earnings_lineage_manifest.py

この記事で扱うのはmanifest formatではない。

**green CIを見たとき、「そのcommit自身が必要な生成物を全部含んでいる」と信頼できるようにする設計**について書く。

## 2種類の「正しい」を分ける

manifest運用には、似ているが別の整合性がある。

### artifact integrity

manifestに書かれたSHA-256やbyte sizeと、実fileが一致するか。

```text
manifest.sha256 == sha256(file bytes)
manifest.size_bytes == len(file bytes)
```

これはverifierで確認できる。

### repository freshness

PRへcommitされたmanifestが、現在の入力から再生成した結果と一致するか。

```text
committed manifest
      ↓
rebuild from current inputs
      ↓
git diff --exit-code
```

こちらはhash verificationだけでは分からない。

**正しいmanifestを生成できることと、そのmanifestがPRへ入っていることは別である。**

## builderが成功したことを完成条件にしない

`build_earnings_lineage_manifest.py` はartifactを読み、SHA-256とsizeを計算し、lineage manifestを生成する。

このbuilder自体が正しくても、CIの順序を間違えると stale manifest を隠せる。

悪い順序:

```text
checkout
→ build manifest
→ verify manifest
→ PASS
```

改善後:

```text
checkout
→ tests
→ build manifest
→ verify manifest
→ git diff --exit-code -- manifest
```

再生成はする。

しかし、**再生成した結果がcheckout時点と違えば失敗させる。**

これで「CIが直せた」は成功条件にならない。

## verifierとdiff gateは守る対象が違う

verifierは、manifest内の各artifactについて、

- path
- SHA-256
- byte size
- file existence
- duplicate path
- path traversal
- status

などを確認する。

これは「manifestが指している実体」を守る。

一方、

```bash
git diff --exit-code -- data/earnings_ledger/lineage_latest.json
```

は、「PRが必要なmanifest更新まで含んでいるか」を守る。

```text
verifier
→ bytes bindingの正しさ

diff gate
→ commit completenessの正しさ
```

一つの巨大な `verified: true` へ押し込まない。

## PR reviewで見たいものをrepositoryへ残すなら、drift gateが必要になる

manifestをCI artifactとして毎回作るだけなら、repositoryへcommitしなくてもよい。

しかし、

- code reviewでmanifest差分を見たい
- commit単位でlineageを残したい
- checkoutだけで状態を復元したい

なら、manifest自体がrepository stateの一部になる。

その場合、

```text
生成可能
```

だけでは足りない。

```text
そのcommitに生成結果が含まれている
```

ことまで必要になる。

## 最小例は4ファイルで再現できる

```text
data/a.txt
data/manifest.json
build_manifest.py
verify_manifest.py
```

最初に、

```bash
printf 'v1\n' > data/a.txt
python build_manifest.py
git add .
git commit -m 'initial'
```

とする。

次にsourceだけ変える。

```bash
printf 'v2\n' > data/a.txt
```

この状態で、

```bash
python build_manifest.py
python verify_manifest.py
```

だけ実行するとPASSできる。

builderがmanifestを新しいhashへ更新したからだ。

しかし、

```bash
git diff --exit-code -- data/manifest.json
```

を続ければ失敗する。

**「正しいmanifestを作れた」ではなく「最初から正しいmanifestをcommitしていたか」を観測できる。**

## generated artifactをcommitするなら、3つのstateを見る

設計を一般化すると次の3つになる。

```text
GENERATABLE
  builderが成功する

INTERNALLY_VALID
  manifestと実artifactが一致する

COMMITTED_FRESH
  再生成してもgit diffが出ない
```

この3つを別々に持つと、失敗理由が分かりやすい。

例えば、

```text
GENERATABLE = true
INTERNALLY_VALID = true
COMMITTED_FRESH = false
```

なら、ロジックではなくcommit漏れが問題だとすぐ分かる。

## green CIの価値は「何を検査したか」で決まる

CIがgreenであること自体は証拠にならない。

CIが、checkout時点の不整合を上書きしてから検査していれば、greenは弱い。

今回の設計では、

- builder
- verifier
- repository diff

を分けることで、greenの意味を強くした。

**PRを開いた人が追加作業をしなくても、そのcommitだけで再現できる状態か**を最後に見る。

## このpatternはmanifest以外にも使える

同じ問題は、commit管理するgenerated fileで起こる。

- API schema
- lock file
- generated docs
- index
- catalog
- snapshot metadata
- codegen output

CIが先に再生成すると、更新忘れを隠せる。

だから、

```text
rebuild
→ validate
→ diff must be empty
```

という順序を使う。

生成物をGitへ入れるなら、**「再生成できる」を「更新不要」と取り違えないこと**が重要だった。

manifestが古いままのPRを、CI自身が直してgreenにする。

その偽の安心を止めるために、最後の `git diff` が効いた。
