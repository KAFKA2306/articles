---
title: "Claude Codeにテストを全部任せるなら、先に「合格条件」を固定する"
emoji: "🧪"
type: "tech"
topics: ["claudecode", "testing", "ai", "ci", "automation"]
published: true
published_at: 2026-08-15 09:33
---

AIに実装もテストも修正も任せられるようになると、最後に残る人間の仕事は「全部を見ること」ではない。

**何を満たせば合格なのかを、実装するagentの外側に固定すること**だ。

Claude Codeの公式ドキュメントは、コードを読み、編集し、commandやtestを実行して検証できるagentic coding toolとして説明している。また、Claudeが自分の仕事を検証できるよう、test caseや期待出力のような「照合対象」を与えることを勧めている。

- https://code.claude.com/docs/en/overview
- https://code.claude.com/docs/en/how-claude-code-works

ここで実務上の落とし穴がある。同じagentがproduction code、test、fixture、configのすべてを変更できると、greenは「実装を直した」だけでなく「合格条件を弱めた」ことでも作れてしまう。

## 問題はAIではなく、oracleまで同じ変更scopeに入ること

たとえば次の依頼は便利だ。

```text
この機能を実装して。
必要なテストも追加して。
失敗したら直して。
全部通ったら終わり。
```

しかし、この依頼には4つの別問題が混ざっている。

1. 何を作るか
2. 何を合格とするか
3. どう直すか
4. 何を証拠として残すか

3をagentへ強く委譲しても、2までその場の最適化対象にすると完了判定が弱くなる。

## 実務では4層に分ける

```text
Outcome / Contract
  何を実現し、何を壊してはいけないか
        ↓
Policy / Oracle
  tests / schema / invariants / required checks
        ↓
Execution
  Claude Code / hooks / CI / runner
        ↓
Evidence
  test result / diff / artifact / exact-head CI
```

Claude CodeはExecutionを強くする。だがExecutionが強いこととPolicyが正しいことは別だ。

Claude Code Hooksも、LLMが実行を選ぶことに依存しないdeterministic controlとして公式に説明されている。`TaskCompleted` hookでtest suiteを走らせ、失敗時に完了扱いを止める例もある。

- https://code.claude.com/docs/en/hooks-guide
- https://code.claude.com/docs/en/hooks

## 何をrepo側へ固定するか

最低限、次はagentのその場の判断から独立させる。

- 必須test suite
- acceptance criteria
- schema / invariant
- 変更してはいけないartifact
- testを弱める変更のreview条件
- mergeをblockする条件

そして可能なら1 commandにまとめる。

```bash
./scripts/verify
```

Claude CodeにもlocalにもCIにも同じcommandを実行させる。これで「Claudeが大丈夫と言った」ではなく、**同じ合格条件を別主体でも再実行できる**状態になる。

## 壊れた例

```text
agent: 実装
agent: test追加
agent: test失敗
agent: fixtureを簡略化
agent: green
```

greenは事実でも、最初の期待を満たした証拠とは限らない。

## 改善後

```text
人間/repo: acceptance criteria固定
agent: 実装・test追加・修正
CI: 固定verifyをexact headで再実行
```

agentは速く回し、人間は毎回すべてを手作業で確認しない。代わりに、**完了条件の所有者を分ける**。

## 読者向けチェックリスト

Claude Codeへテスト自動化を委譲する前に、次の5問だけ確認すればよい。

1. 合格条件はコードと同じagentが自由に弱められるか
2. 必須checkは1 commandで再実行できるか
3. test/fixture/config変更もdiffでreview対象になるか
4. CIはexact headで同じ条件を再実行するか
5. greenが「何を証明したか」を説明できるか

1がyesで、残りがnoなら、委譲範囲より先にoracleを固定した方がよい。

## 証拠の境界

この記事は「Claude Codeがtestを改ざんする」と主張していない。主張しているのは、**最適化する主体と合格条件を変更できる主体を同一scopeに置くと、完了判定の独立性が弱くなる**という設計上の事実だ。

AI coding agentを信用するかどうかではない。速いagentほど、合格条件を外側へ固定した方が委譲できる範囲が広がる。

**AIに多く任せたいなら、人間が多く確認するのではなく、合格条件を先に固定する。**