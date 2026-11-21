---
title: "合格の決定権を実装者に渡すな。AI時代の検証設計"
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

この話はClaude Codeの設定に限らない。

> **合格の決定権を、成果を作る主体の自己申告に委ねるな。**

これは「AIにテストを書かせるな」という意味ではない。AIが回帰テストを追加するのはよい。ただし、合格の根拠となる**要求・期待値・必要な検査範囲を、実装と同時に無審査で緩められる状態**を作らない。変更するなら、その理由と検証方法を別に審査する。

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

このリポジトリでは、存在しない `./scripts/verify` を例にするのではなく、[実際のCI定義](https://github.com/KAFKA2306/articles/blob/main/.github/workflows/article-pipeline-ci.yml)にある検査を呼ぶ。ルートディレクトリから次を実行する。

```bash
python -m compileall pipeline demos/python-syntax-gate/syntax_gate.py
python -m unittest discover -s tests -v
python -m pipeline.audit
```

Zennでの本文の描画も確認するなら `bash scripts/zenn-render-check.sh` を実行する。これはNode.jsとZenn CLIの取得・起動が必要な検査で、上のPython三つだけでは代替できない。PRでは `Article Pipeline CI` が**そのPRのhead SHA**で通ったかを確認する。

ここで守る判定は、例えば「公開を意図していない下書きを勝手に公開扱いにしない」こと。まず `git diff -- .github/workflows/article-pipeline-ci.yml tests/ pipeline/contracts/article.md` で合格条件そのものが変わっていないかを開く。実装だけを直したPRでも、これらの期待値を書き換えたら**同じテストに通った証明にはならない**。期待値の変更には別途理由とレビューが必要だ。

## なぜ「green」だけでは足りないのか

自然に考えれば「コードを書いた人がテストも書いてgreenなら完了」である。だが**同じ実装者がテストの正解も自由に変えられる**なら、コードが要求へ近づいたのか、要求の方をコードに合わせたのか区別できない。

```text
A: 「不正入力は拒否」 → 実装修正 → 拒否を検査 → green
B: 「不正入力は拒否」 → 拒否しない実装
   → テストの期待を「許可」に変更 → green
```

AもBもテスト結果はgreenになり得る。Bは**失敗の仕組みを示す仮想例**で、Claude Codeが実際にこの改ざんをしたという観測ではない。重要なのは、PRのCIが独立に実行されても、PRでCIやfixture自体を変えられるなら、**合格基準まで独立したとは限らない**ことだ。

## 別の仕事へ移す条件と、規律の反例

金融分析なら、集計コードと照合用の基準数値を同一変更で無審査に動かせる場合。制作物の評価なら、生成者が採用の物差しも変更できる場合。どちらにも「成果と物差しを別に保つ」判断が**応用候補**になる。ただし両分野での効果をここで追加実測したわけではない。

適用するのは、合否が公開・利用者の意思決定・重要な計算に影響し、守るべき要件がある場合。破棄できる試作や、要求を変えることが目的の案件では物差しを変えてよいが、変更した理由を別に確認する。**すべてのテストや仕様を永遠に固定する原則ではない。**

撤回・制限すべき条件は、独立した基準の管理によって欠陥の発見や重大な手戻りが減らず、逆に変更時間だけが増えると、同じ種類の案件で確認された場合だ。この記事はその改善率を測定していない。検証済みなのはリポジトリにCIがあり同じheadを実行できること、提案しているのは**判定を自分で動かせる構造上の危険**への対応である。

## 何をagentの外へ残すか

最低限、次の4つは明文化する。

1. **acceptance criteria** — 何ができれば完了か
2. **must-pass checks** — 必ず通すtest/schema/invariant
3. **protected assumptions** — fixtureや期待値を変えるならreviewが必要なもの
4. **merge condition** — どの結果をもって終了とするか

これらを固定したうえで、実装・テスト追加・failure解析・再修正は積極的にagentへ渡す。

## 5分でできる導入チェック

Claude Codeに修正を任せる前に、対象のIssue、既存CIが実行するコマンド、変更前のテストの期待値を開く。たとえば「無効な入力を拒否する」修正なら、入力例と期待する応答をIssueに記録してから渡す。

- 必須checkを1 commandで再実行できる
- test/fixture/configの変更もdiffに出る
- acceptance criteriaがpromptだけでなくrepoにも残る
- CIがPRのexact headで同じverifyを実行する
- greenが何を証明したか1文で説明できる

PRでは、先にfixture・期待値・CI設定の差分を見る。合格条件が動いていたら、その変更の妥当性を先に判断する。条件がそろった状態でPRの対象コミットに対するCI結果と照合すると、どの要求を確認できたか説明できる。

## この記事が言っていないこと

Claude Codeがtestを勝手に弱める、と主張しているわけではない。またHooksだけで品質が保証されるとも言っていない。

言いたいのは、実装主体が高速になるほど、完了条件を独立して再実行できる設計の価値が上がるということだ。

**AIにもっと任せたいなら、人間の監視量を増やすのではなく、合格条件を先に外へ出す。**
