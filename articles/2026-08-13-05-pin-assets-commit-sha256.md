---
title: "中央の画像を更新しても、公開サイトが勝手に変わらない。共有assetをcommitとhashで固定する"
emoji: "📌"
type: "tech"
topics: ["github", "ci", "frontend", "architecture"]
published: false
published_at: 2026-08-13 23:40
---

複数のサイトで同じ画像やアイコンを使いたい。

一番簡単なのは、中央repositoryの `main` を直接参照することだ。

```text
https://raw.githubusercontent.com/example/assets/main/hero.webp
```

しかし、このURLは同じままでも中身は変わる。

中央repoで `hero.webp` を差し替えれば、consumer側は1行も変更していないのに公開サイトの見た目が変わる。

404にもならない。buildも通る。

**reviewしていない変更が、正常な配信として利用者へ届く。**

`KAFKA2306/prompt-vault` と `KAFKA2306/travel` では、ここを次の境界へ変えた。

```text
asset IDを選ぶ
  ↓
canonical commitを固定
  ↓
SHA-256を照合
  ↓
consumerへvendor
  ↓
build後も同じhashか確認
  ↓
deploy後も同じhashか確認
```

この記事で扱うのはhashの計算方法ではない。

**中央管理の便利さを残しながら、consumerの公開物が知らない間に変わらない運用UX**について書く。

一次情報:

- Prompt Vault: https://github.com/KAFKA2306/prompt-vault/commit/f96a2d6b5bb257080f235f04cdfb5745e8700ed3
- Prompt Vault: https://github.com/KAFKA2306/prompt-vault/commit/a6ef582f7112b0f504bea3d535b9c45437c107f9
- travel consumer: https://github.com/KAFKA2306/travel/commit/cbc7aeae37398a0f50b76c6de6e85319653dfbfe
- GitHub permalink: https://docs.github.com/en/repositories/working-with-files/using-files/getting-permanent-links-to-files?apiVersion=2022-11-28

## `main` URLは場所を示すが、採用versionは示さない

branch URLは便利である。

常に最新のassetへ追従できる。

しかしconsumerに必要なのは、

> 今どこにassetがあるか

だけではない。

> **このサイトは、どのversionのどのbytesを採用したのか**

も必要である。

そこで識別を2段階に分ける。

1. commit ID — どのrepository snapshotを採用したか
2. SHA-256 — そのsnapshotから取り出したbytesが期待値と同じか

commitはsource versionを固定する。

hashはconsumerへ入った実体まで照合する。

## consumerはasset pathではなくIDを選ぶ

中央manifestでは、共有assetをIDで管理する。

```json
{
  "id": "travel-basic",
  "file": "travel-basic-illustration.webp",
  "sha256": "8c45dfb3c32aa5d2991b9d3b9d710b66722f0ef10fb62a0b5dea2582f36ea383"
}
```

consumer側はsource pathを自由記述せず、

```json
{
  "id": "travel-basic",
  "destination": "public/assets/kafka-signal/travel-basic-illustration.webp"
}
```

のように採用対象と配置先を宣言する。

これにより、source側のdirectory構造より**assetの意味的なID**をcontractにできる。

## vendorした時点でlockを残す

`travel` では、採用したsourceをlockへ残した。

```json
{
  "canonical_repository": "KAFKA2306/prompt-vault",
  "canonical_commit": "90111f8953dd2a45aca2da7053bfdeef57459b41",
  "consumer_repository": "KAFKA2306/travel",
  "source_sha256": "8c45dfb3c32aa5d2991b9d3b9d710b66722f0ef10fb62a0b5dea2582f36ea383"
}
```

これでasset更新は、

```text
中央repoで差し替えた
```

だけではconsumerへ届かない。

consumer側でも、新commitと新hashを採用する変更としてreviewされる。

**共有assetの更新を、review可能なversion changeへ変える。**

## commit pinだけではconsumer内の実fileまでは確認できない

commit permalinkでsource versionは固定できる。

しかしcopy後のfileが本当に同じbytesかは別である。

例えば、

- vendor scriptのbug
- local edit
- build processでの置換
- deploy時の別asset混入

があれば、source commitは正しくても公開物は違う。

そこで各段階でhashを取り直す。

```text
canonical source
  ↓ SHA-256
consumer checkout
  ↓ SHA-256
build artifact
  ↓ SHA-256
deployed file
```

すべて同じdigestを要求する。

## `travel` ではdeploy後までread-backする

consumer側では、source treeだけでなく `dist/` のbuild後fileもhash確認する。

さらにPages deploy後、公開URLからassetを取得し、同じSHA-256になることを検証する。

つまり、

```text
正しいsourceを選んだ
```

だけで終わらず、

```text
利用者へ配られたbytesも同じだった
```

まで確認する。

ここまで追うと、asset更新の責任範囲が明確になる。

## 中央管理と自動追従は同じではない

共有asset基盤を作ると、全consumerを常に最新版へ自動追従させたくなる。

しかし、ブランド画像やhero imageのように公開UXへ直接効くassetでは、それが望ましいとは限らない。

```text
central source = 1か所で管理
```

と、

```text
automatic adoption = 全consumerへ即反映
```

は別の設計判断である。

今回の構成は、中央sourceを持ちながらconsumer adoptionを明示的な更新にした。

速度より、**consumerがいつ何を採用したかを説明できること**を優先した。

## silent overwriteも止める

vendor先に既存fileがあり、期待hashと違う場合に、そのまま上書きするとlocal changeを消す可能性がある。

そのため、

```text
managed file + expected old hash
→ update可能

unknown file / locally modified bytes
→ fail
```

のように扱う。

共有基盤だから強制的に上書きするのではなく、consumer側の状態も尊重する。

## このpatternが向く場面

特に効くのは、

- 複数GitHub Pagesで共通画像を使う
- design system assetを複数repoへ配る
- ロゴやiconのversionを固定したい
- build/releaseの再現性が必要
- 中央更新をconsumer reviewなしで反映したくない

といった場合である。

逆に、常に最新を表示すること自体が要件ならruntime hotlinkも合理的である。

大事なのは、**変更追従を意図しているのか、偶然そうなっているのか**を区別することだ。

## 最小導入はcommit + hashだけでもよい

大きなregistryを最初から作る必要はない。

1つの共有fileについて、

```yaml
source_repo: KAFKA2306/prompt-vault
source_commit: 90111f8...
source_sha256: 8c45dfb3...
destination: public/assets/hero.webp
```

をlockへ置く。

CIでdestinationのSHA-256を再計算する。

それだけでも、`main` hotlinkよりかなり説明可能になる。

中央assetを更新しても、consumerが勝手に変わらない。

consumerが更新するときは、その差分がPRとして見える。

**中央管理と公開安定性を両立するには、「最新を共有する」のではなく「採用versionを共有する」方が扱いやすかった。**
