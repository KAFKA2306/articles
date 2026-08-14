---
title: "『AIを使い倒す人』で終わらせない。公開成果を並べたら、何を任せられる人かが見えた"
emoji: "🪞"
type: "idea"
topics: ["ai", "learning", "career", "communication"]
published: false
published_at: 2026-08-13 18:11
---

人から「AIをものすごく使っている人」と言われることがある。

GitHubを見れば、そう見えるのは自然だと思う。

投資、データ分析、本棚DB、VRChat、AI agent、自動化、Web UI。

入口が多い。

ただ、この説明には少し違和感があった。

**AIをたくさん使うこと自体は、誰かにとっての価値ではない。**

仕事や相談で知りたいのは、むしろ次だと思う。

> この人に、どんな曖昧な問題を渡すと、どんな状態まで持っていってくれるのか。

そこで自己分析ではなく、公開している成果物を4つ並べてみた。

すると、domainは違っても同じ動きがかなり繰り返されていた。

```text
曖昧な問題
  ↓
一次情報・現状を調べる
  ↓
正準な状態を決める
  ↓
実装する
  ↓
失敗条件をテストする
  ↓
公開・運用できる成果物にする
  ↓
後から検証できる証拠を残す
```

この記事で言いたいのは「何でもできます」ではない。

**私が比較的強いのは、曖昧な意図を、後から確かめられる仕組みへ変える仕事らしい**、ということだ。

現時点ではプロフィール候補として `published: false` のままにする。

## 1. 本棚CSV：欲しかったのはimporterではなく「書き込む前に分かる」ことだった

`KAFKA2306/books` では、本の記録をWork / Edition / Holdingへ分けて管理している。

CSV移行を作るとき、最初にimporterを作らなかった。

先に、正準catalogを変更せず、

```text
この行は既所蔵
この行は新規Work
この行は類似titleなので人間確認
このISBNは不正
```

を返す診断coreを作った。

その後CLIとbrowserを追加しても、どちらも同じ診断coreを使えた。

- article: `csv-migration-dry-run-before-write.md`
- source repo: https://github.com/KAFKA2306/books

ここでやったのはCSV処理ではない。

**「データを入れたい」という曖昧な要求を、「書き込む前に何が起きるか説明できる状態」へ変えた。**

私はこういう変換が好きらしい。

## 2. 投資データ：856件が7,699件になっても、どちらを信じるか説明できるようにした

`KAFKA2306/investor2` では、同じテーマの集計が856から7,699へ大きく変わったケースがあった。

数字だけ見れば、前が間違いだったように見える。

実際にはscopeが違った。

そこで、

- primary source
- observed value
- derived aggregate
- external parser cross-check
- scope
- method

を分けてsnapshotへ残した。

- article: `primary-source-derived-data-provenance.md`
- source repo: https://github.com/KAFKA2306/investor2

これで「数字を出す」から、

**数字が変わったときに理由を説明できる**

へ進めた。

ここでも、作ったものより「なんとなく信じるしかない状態を減らした」ことの方が自分には重要だった。

## 3. AIにPC作業を任せる：自動化より先に「どこまで触ってよいか」をコードにした

GitHub Issueを中継して、ローカルPC上のAIへ仕事を渡すbridgeも作った。

ただし、最初から何でも実行できるようにはしていない。

- 命令できるGitHub userを限定する
- `AllowedRoot` 外のdirectoryを拒否する
- 通常はread-only
- writeが必要な仕事だけworkspace-write
- tool起動ではなくE2E最終結果まで確認する

- article: `codex-chatgpt-github-issue-bridge.md`
- public implementation: https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge

ここで価値があるのは「AIでPCを操作できた」ことではない。

**どこまでなら安心して委任できるかを、自然言語ではなく機械的な境界へ変えたこと**だと思う。

## 4. AIペットの記憶：聞いたログを、勝手に本人の事実へしなかった

`KAFKA2306/vlog` のVRCPet adapterでは、壊れた3行のfixtureを使っている。

```text
{"text":"hello"}
{"broken":
{"text":"world"}
```

期待値は、

```text
valid records = 2
parse issues  = 1
```

である。

読めた2件はObservationとして残す。

壊れた1件もissueとして残す。

しかし、読めた会話をそのまま本人のMemoryClaimにはしない。

- article: `vrcpet-observation-source.md`
- source repo: https://github.com/KAFKA2306/vlog

これも同じだった。

**観測したことと、事実として断定してよいことの間に境界を置く。**

## 4つ並べると、domainより作業の型の方が一貫していた

本、投資、AI agent、VRChatペット。

題材だけ見れば別々である。

しかし、自分がやっていることはかなり似ていた。

### 1. 「何が正しい状態か」を先に決める

コードを書く前に、

```text
何を成功と呼ぶか
何を未確認と呼ぶか
何が起きたら止めるか
```

を分ける。

### 2. 一次情報・実データへ戻る

それらしい説明より、今のrepository、実file、公式資料、実行結果を確認する。

### 3. 失敗条件を成果物へ入れる

READMEへ注意を書くより、test、CI、schema、stateとして残す。

### 4. 「動いた」を完成にしない

tool success、build success、runtime success、publish successを必要に応じて分ける。

### 5. 後から再現できる証拠を残す

commit、source URL、hash、fixture、verification recordを成果物とセットにする。

この5つは、技術stackより再利用されている。

## だから「AIの人」より、「曖昧さを減らして運用へ持っていく人」の方が近い

AIはかなり使う。

GitHubも使う。

PythonもTypeScriptも使う。

でも、それらは結果を作る手段である。

自分が嬉しいのは、

```text
よく分からない
```

だったものが、

```text
何が分かっているか
何が未確認か
どうすれば動くか
何をもって完了か
```

へ変わったときだ。

以前「世界の中にある『なんとなく』を減らしたい」と書いていた。

今はもう少し業務的に言える。

**曖昧な要求・散らばった情報・一回限りの手作業を、検証可能で繰り返し使える仕組みへ変えること**が、自分の中心に近い。

## 何を任せると相性がよさそうか

公開成果から言える範囲なら、次のような仕事と相性がよい。

### 「毎回人が確認している」を減らしたい

手作業を単にscript化するのではなく、失敗時に止まり、証拠が残るところまで設計する。

### データはあるが「どれが正しいか」が曖昧

source、scope、canonical state、derived valueを分け、利用側が判断できる形へする。

### AIを導入したいが、どこまで任せてよいか分からない

権限・入力・出力・completion boundaryを分け、委任可能な範囲を小さく固定する。

### prototypeは動いたが、運用へ持っていけない

test、CI、state、failure case、production verificationを追加して、「動いた」から「任せられる」へ寄せる。

逆に、完成した仕様どおりに大量実装するだけなら、この強みはあまり必要ないかもしれない。

**問題そのものがまだ曖昧な段階の方が、自分の価値は出やすい。**

## 「何でもできる」は目標にしない

domainが多いと、「何でもできる人」に見えることがある。

しかし、それは使いやすい説明ではない。

何でもできる、では依頼側が何を渡せばよいか分からない。

今回4つの公開成果へ接地してみて、少なくとも次の表現なら証拠と一致すると思う。

> **曖昧な問題を調べ、正準状態と失敗条件を決め、実装・検証・運用までつなぎ、あとから確かめられる形にする。**

AIはその速度を大きく上げる。

ただし、AIを使うこと自体が商品ではない。

その結果、**人が毎回考え直さなくても使える仕組みが残ること**が価値である。

## この原稿をまだ公開しない理由

これは自己紹介としては以前より具体的になった。

一方、営業資産として公開するなら、さらに各成果のproduction利用状況や利用者価値を揃えた方が強い。

そのため現時点では `published: false` を維持する。

根拠のない「高出力」「何でもできる」といった自己評価は使わない。

公開するなら、**何を任せられるかを、公開成果から読者自身が判断できる状態**にしてからにしたい。
