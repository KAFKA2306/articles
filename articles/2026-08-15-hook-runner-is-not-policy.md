---
title: "Claude Codeに全部任せるなら、合格条件だけはClaudeに任せない"
emoji: "🧪"
type: "tech"
topics: ["claudecode", "testing", "ai", "ci", "automation"]
published: true
published_at: 2026-08-15 09:33
---

Claude Codeに実装、テスト追加、失敗修正まで全部任せる。

そのとき一番危ないのは、AIがコードを書くことではない。**「何をもって合格とするか」まで同じ変更ループに入ること**だ。

テストがgreenでも、実装が正しくなったとは限らない。fixtureや期待値の方が動けば、同じgreenは作れる。

だから私は、Claude Codeの監視を増やすのではなく、逆に1つだけClaudeから切り離した。

**合格条件である。**

Anthropic公式でも、Claude Code Hooksの`TaskCompleted`はtestやlintなどの完了条件を実行し、失敗時はtask completionをblockできる。

- https://code.claude.com/docs/en/hooks-guide
- https://code.claude.com/docs/en/hooks

## 私が変えたのは、agentではなく合格条件の置き場所だった

危ないのはAIそのものではない。production code、test、fixture、config、完了判定を同じ変更ループへ全部入れることだ。

```text
agent: 実装
agent: test追加
agent: test失敗
agent: fixture/configも変更
agent: green
```

このgreenだけでは、「実装が要件へ近づいた」のか「要件側が動いた」のかを区別しにくい。

そこで作業を3つに分ける。

```text
1. Contract
   何を実現し、何を壊してはいけないか

2. Verifier
   tests / schema / invariant / required checks

3. Worker
   Claude Codeが実装・修正・反復実行する
```

Workerは何度でも変えてよい。ContractとVerifierは、変更するならその変更自体をレビュー対象にする。

## 実運用では、同じverifyをagentとCIの両方から呼ぶ

この`articles` repositoryでも、PRのArticle Pipeline CIはcompile、contract tests、publication transition guard、Zenn render、privacy audit、clean checkoutをrepository側に固定している。

https://github.com/KAFKA2306/articles/blob/main/.github/workflows/article-pipeline-ci.yml

Claude Codeが何を実装したかに関係なく、CIは同じ条件をもう一度実行する。この構造なら「Claudeが大丈夫と言った」ではなく、**別主体が同じ合格条件を再実行した**と言える。

自分のrepoでも、入口を1 commandへ寄せると扱いやすい。

```bash
./scripts/verify
```

中身はprojectごとに違ってよい。重要なのは、Claude Code、ローカル、CIで同じ判定を呼べることだ。

## 何をagentの外へ残すか

最低限、次の4つは明文化する。

1. **acceptance criteria** — 何ができれば完了か
2. **must-pass checks** — 必ず通すtest/schema/invariant
3. **protected assumptions** — fixtureや期待値を変えるならreviewが必要なもの
4. **merge condition** — どの結果をもって終了とするか

これらを固定したうえで、実装・テスト追加・failure解析・再修正は積極的にagentへ渡す。

## 5分でできる導入チェック

Claude Codeへ「全部通るまで直して」と頼む前に、次だけ確認する。

- 必須checkを1 commandで再実行できる
- test/fixture/configの変更もdiffに出る
- acceptance criteriaがpromptだけでなくrepoにも残る
- CIがPRのexact headで同じverifyを実行する
- greenが何を証明したか1文で説明できる

この5つが揃えば、人間は全diffを逐語監視するのではなく、**合格条件の変更と最終証拠に集中できる**。

## この記事が言っていないこと

Claude Codeがtestを勝手に弱める、と主張しているわけではない。またHooksだけで品質が保証されるとも言っていない。

言いたいのは、実装主体が高速になるほど、完了条件を独立して再実行できる設計の価値が上がるということだ。

**AIにもっと任せたいなら、人間の監視量を増やすのではなく、合格条件を先に外へ出す。**