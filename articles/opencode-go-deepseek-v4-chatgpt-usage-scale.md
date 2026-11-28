---
title: "ChatGPTで方針を決めたあと、OpenCode Goにどの作業を任せるか"
emoji: "♾️"
type: "tech"
topics: ["opencode", "chatgpt", "coding", "mcp", "local"]
published: false
published_at: 2026-08-13 12:09
created_at: "2026-08-13"
updated_at: "2026-11-21"
---

OpenCode Goを見たとき、最初は単純に安いと思った。

初月$5、その後$10/月。DeepSeek V4 Flashは、公式が観測した典型的な利用パターンなら月158,150 requests相当とされている。

ただ、使い道を考えていて気づいた。

**ChatGPTの代わりにする必要はない。local実行だけ任せればいい。**

これならかなり欲しい。

## ChatGPTはもう十分使っている

普段の作業では、ChatGPTにかなり寄せている。

GitHubを横断して次に触るrepoを決める。IssueやPRを見る。調査する。記事を直す。何を優先するか決める。

以前の記事でも、個人開発が増えるほど重くなるのはコードを書くことより「次に何を進めるか」を決める仕事だと書いた。

- [個人開発が123個になって分かった。ChatGPTに任せるべきはコードより「次の1件」だった](https://zenn.dev/kafka2306/articles/chatgpt-multiproject-autonomy)

ここは今のままでいい。

欲しいのは、その続きだった。

## 最後にlocal PCへ戻る仕事が残る

ChatGPTで方針を決めても、最後は自分のPCへ戻る仕事がある。

- commit前のworkspaceを触る
- 大きなローカルデータを読む
- GPUを使う
- shellでtestを回す
- 認証済みのdesktop applicationを触る
- Unity Editorの実状態を見る
- local MCPにつないだtoolを使う

以前、local Codexとのbridgeを作ったときにも、この境界にぶつかった。

- [GitHub IssueをAIの伝言板にしたら、伝言板に全部やらせてはいけないと分かった](https://zenn.dev/kafka2306/articles/codex-chatgpt-github-issue-bridge)

GitHub上で考えられても、GitHub上に存在しない状態までは触れない。

ここをもっと任せたかった。

## OpenCode Goはlocal実行専用で使う

OpenCodeには、project環境でshell commandを実行する`bash`、fileのread/edit/write、MCP serverとの接続がある。

なので、自分の中では役割を増やしすぎないことにした。

```text
ChatGPT
調べる / 考える / 横断する / 次を決める

OpenCode Go
local repoを触る / 直す / testする / shellを回す / local MCPを使う
```

OpenCode Goに調査も記事も全部移したいわけではない。

**local executionだけを担ってもらう。**

この分け方なら、ChatGPTと競合しない。

むしろChatGPTで決めたことを、そのまま自分のPC側で進める実行役を追加できる。

自分の作業で試すなら、ローカルのリポジトリを一つ選び、小さな修正の対象ファイルと、普段使っているテストコマンドを用意する。ChatGPTで「何を直し、何が通れば終わりか」を一行にし、その一行をOpenCode Goに渡す。返ってきた差分とテスト結果を手元で開き、狙った修正が入ったか、失敗したなら何を直すべきかまで追えるかを見て、次の依頼にも使うか決める。

## ローカルで1件試すなら、この依頼と検査を分ける

ここでは、手元へcloneした `KAFKA2306/articles` の**未公開記事を1件だけ改稿する**場合を例にする。これは比較実験の設計であり、OpenCode Goで実行済みという主張ではない。

ChatGPT側で渡す情報を、曖昧な「良くして」ではなく次のように固定する。

```text
対象: articles/2026-08-14-06-top-n-boundary-evidence.md
目的: 実際の51社から50社を選んだ証拠と、N+1件目の出力を読者が追えるようにする
変更してよいもの: 上記の記事本文だけ
変えないもの: published: false、slug、他の記事、公開用ブランチ
完了条件:
  1. 51社の候補数と採用50件を区別して説明できる
  2. 除外されたQDレーザのID・売上が一次資料に結び付く
  3. slug・根拠URL・公開状態が保たれる
```

OpenCode側では、変更前後に同じリポジトリで次を確認する。

```sh
git status --short
git diff -- articles/2026-08-14-06-top-n-boundary-evidence.md
python3.12 -m unittest discover -s tests -v
python3.12 -m pipeline.evidence_gate
```

最初の `git status --short` で他人の未コミット変更があれば、自動で上書きしない。差分が対象記事以外に広がったら採用を保留する。テストが通っても**公開状態の変更やZenn本番への反映は許可しない**。追加した説明から読者が誤った見出しを落とせるか、本文と一緒に読み直す。これはローカルで試すための例で、今ここでのOpenCode Go導入結果や費用対効果の実測ではない。

## 158,150回より、何回local loopを回せるか

OpenCode Goの利用制限はrequest数そのものではなくusageで定義されている。DeepSeek V4 Flashの月158,150 requestsは、公式が典型的なtoken/cache patternから換算した推定値で、hard quotaではない。

でも、ここまで整理すると数字の見え方も変わる。

```text
直す
↓
testする
↓
失敗する
↓
また直す
```

欲しいのは大量のチャットではない。

**このlocal loopを、料金をあまり気にせず繰り返せる余裕だ。**

それが月$10なら、かなり試しやすい。

ChatGPTの使い方は変えない。

**考える場所はそのまま。local実行だけ増やす。**

OpenCode Goが刺さったのは、これだった。

## 注意：local実行とlocal推論は別

OpenCode Goはlocal LLMの契約ではない。GoのmodelはOpenCode Go provider経由で利用する。

ここでいうlocalは、実行場所とtool accessが自分のPCにあるという意味で、推論まで完全offlineという意味ではない。

## 公式情報

- OpenCode Go: https://opencode.ai/docs/go/
- OpenCode Tools: https://opencode.ai/docs/ja/tools/
- OpenCode MCP: https://opencode.ai/docs/mcp-servers/

料金・model・利用上限は変更されるため、契約時には現行docsを再確認する。
