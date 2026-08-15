---
title: "Claude Codeにテストを全部任せるなら、「何を正しいとするか」を先に固定する"
emoji: "🧪"
type: "tech"
topics: ["claudecode", "testing", "ai", "ci", "automation"]
published: true
published_at: 2026-08-15 09:33
---

「実装して。テストも書いて。失敗したら直して。全部通ったらPRまで作って」

Claude Codeを使っていると、ここまでまとめて任せられる。

Anthropic自身もClaude Codeを、コードベースを読み、複数ファイルを変更し、テストを実行し、commitされたコードまで届けるagentic coding systemとして説明している。

- [Claude Code | Anthropic](https://www.anthropic.com/product/claude-code)

さらにClaude Code Hooksでは、Claudeが作業を終える前にunit testがすべて通ることを検証する `Stop` hook の例まで公式に示されている。

- [Automate workflows with hooks | Claude Code Docs](https://code.claude.com/docs/en/hooks-guide)
- [Hooks reference | Claude Code Docs](https://code.claude.com/docs/en/hooks)

では、テスト実行も修正も再実行もClaude Codeに任せられるようになったとき、人間側に何が残るのか。

この記事の答えは1つだ。

> **「何をすればpassなのか」を、実行するagentとは別に固定する。**

Claude Codeにテストを任せることが問題なのではない。

むしろ、反復的な実行と修正はagentに委譲しやすい。

問題になるのは、**実装する主体・テストを選ぶ主体・合格を宣言する主体が全部同じになったとき、何を根拠に「終わった」と判断するのかが曖昧なままになること**だ。

## 「テストが全部通った」は、何を証明したのか

緑色のtest resultは重要だ。

しかし、それが直接意味するのは、**実行されたテストが定義した条件を満たした**ということまでである。

たとえば、Claude Codeに次のように頼める。

```text
この機能を実装して。
必要なテストを追加して。
失敗したテストを直して。
全部通るまで続けて。
```

ここでClaude Codeは、実装、テスト作成、test commandの実行、失敗解析、再修正を1つのloopにまとめられる。

便利である。

ただし、このloopの外側に次の問いが残る。

```text
そもそも何を守るべきか？
どのテストを必須にするか？
何を壊してはいけないか？
どの条件を満たしたらmergeしてよいか？
```

この層まで暗黙のままagentに渡すと、「テストが通った」という観測と「欲しかったものが正しい」という判断が同じものに見えやすくなる。

そこで、実行とpolicyを分ける。

## Claude Code時代の4層

私は自動化を次の4層に分けて考えるのがよいと思っている。

```text
1. Outcome / Contract
   何を実現し、何を壊してはいけないか

            ↓

2. Policy Authority
   tests / type checks / schema / invariants / custom checks
   何をpass・failとするか

            ↓

3. Execution / Trigger
   Claude Code / hooks / CI / runner
   いつ、どのcheckを実行するか

            ↓

4. Evidence
   test result / diff / hash / artifact / CI result
   何が実際に起きたか
```

Claude Codeは3層目を非常に強くできる。

実装して、commandを実行し、失敗を読み、直して、もう一度実行するloopを高速化できるからだ。

しかし3層目が強くなったことと、2層目の**「正しさの定義」**が増えたことは同じではない。

ここを混ぜないことが重要になる。

## これはClaude Code公式の設計とも整合する

Claude CodeのHooks guideは、hooksを「user-defined shell commands」と説明し、LLMが実行するかどうかを選ぶことに依存せず、特定のactionを必ず起こすための **deterministic control** と位置づけている。

さらに、project rulesのenforcementやrepetitive taskのautomationを用途として明記している。

- [Automate workflows with hooks | Claude Code Docs](https://code.claude.com/docs/en/hooks-guide)

Hooks referenceでは、agent-based hooksは現在experimentalであり、production workflowではcommand hooksを優先するよう明記されている。

- [Hooks reference | Claude Code Docs](https://code.claude.com/docs/en/hooks)

つまりClaude Code自身の拡張モデルにも、次の区別がある。

```text
LLMに判断させる
        ≠
決定的なcommandを必ず実行する
```

AI agentを信用するか、しないかという話ではない。

**判断が必要な場所と、決定的に強制したい場所を分ける**という話だ。

## では、Claude Codeには何を任せるのか

テスト自動化をClaude Codeへ委譲するとき、私は次のように分ける。

| 委譲しやすい | repo側に固定したい |
|---|---|
| test commandの反復実行 | 必須test suite |
| failure logの解析 | acceptance criteria |
| 実装修正 | invariant |
| regression testの追加案 | mergeをblockする条件 |
| lint / type checkの実行 | lint / type ruleそのもの |
| 修正後の再検証 | 最終的に保存するevidence |

ここで重要なのは、右側を必ず人間が毎回手作業で実行することではない。

**右側をagentのその場の判断から独立した、再実行可能な形にしておく**ことだ。

たとえば、

```text
./scripts/verify
```

の1commandに、必須test、lint、type check、schema validation、必要なcustom checkerを集約する。

Claude CodeにもCIにも同じcommandを実行させる。

すると「Claudeが大丈夫と言った」ではなく、

```text
同じpolicyを
Claude Codeでも
local hookでも
CIでも
再実行できる
```

状態になる。

これがagentを安心して働かせるための境界になる。

## 小さな実験で、runnerとpolicyを分離してみた

この考え方を確認するために、Verification Stack v2では `pre-commit` と `prek` を使ったcontrolled fixtureを作った。

これはClaude Codeそのものの比較実験ではない。

**「実行するrunnerを替えたとき、同じpolicyのobservable effectが保存されるか」**を測るための小さな実験だ。

結果を見る前に `HOOK-PATCH-PARITY-001` として、次の4条件を固定した。

1. 同じファイルが変更される
2. 最終content SHA-256が一致する
3. diff SHA-256が一致する
4. 再実行がidempotentである

controlled resultは次の通りだった。

| 観測 | 結果 |
|---|---|
| same changed files | true |
| same content SHA-256 | true |
| same diff SHA-256 | true |
| both idempotent | true |

証跡は固定commitに保存している。

- [controlled summary](https://github.com/KAFKA2306/articles/blob/aa33a88e5bf165ac4085c7462e67f23283647926/benchmarks/verification-stack-v2/results/controlled/summary.json)
- [experiment protocol and artifacts](https://github.com/KAFKA2306/articles/tree/aa33a88e5bf165ac4085c7462e67f23283647926/benchmarks/verification-stack-v2)

このfixtureで観測された範囲では、runnerを `pre-commit` から `prek` に交換しても、hookが作ったpatchのobservable resultは変わらなかった。

つまり、このケースではrunnerの変更を**policy変更ではなくtrigger実装の置換**として扱えた。

全repo・全hookで完全互換だと証明したわけではない。language-specific hook、network依存hook、特殊stage、CI環境差は今回のground truth外である。

しかし、この小さな実験はClaude Code時代にも使える1つの見方を与える。

> **実行主体が変わっただけなら、正しさの定義が増えたとは限らない。**

## Claude Codeを追加しても、品質ルールが自動的に増えるわけではない

たとえば、既にCIで次を実行しているとする。

```text
Ruff
Pyright
test suite
schema validation
```

そこへClaude Codeを追加して、同じcommandを実装中にも実行させる。

これは大きな価値がある。

feedback loopが短くなり、失敗をagent自身が修正できるからだ。

ただし、新しく増えたのは主に**実行能力**である。

Ruff rule、type policy、test oracle、schema invariantが同じなら、policy authorityそのものが自動的に増えたわけではない。

逆に、Claude Codeに新しいregression testを作らせ、そのtestをレビューして正準suiteへ追加したなら、そこで初めてrepositoryが検出できるfailure conditionが増える可能性がある。

見るべきなのは「Claude Codeを導入したか」ではない。

**repositoryが昨日より何を検出できるようになったか**である。

## 「agentに全部任せる」を成立させるのは、強いpromptではなく外部化されたpolicy

Claude Codeへ長いpromptを書けば、かなり多くのことを任せられる。

しかし、毎回promptの中で、

```text
必ずtestして
lintして
type checkして
このファイルは触らないで
この条件を壊さないで
```

と頼み続けるより、決定的に強制できる条件はrepository側へ外部化した方が再利用しやすい。

AnthropicのHooks documentationも、まさにLLMが実行を選択することに依存しないdeterministic controlをhooksの用途として説明している。

Claude Codeを賢くするだけではなく、**Claude Codeが働く環境そのものを賢くする**。

この方が、agentを増やしてもpolicyが散らばりにくい。

## 最小構成ならこうする

Claude Codeに実装とテストloopをかなり委譲するなら、最小でも次の形にする。

```text
明示したOutcome / Acceptance Criteria
             ↓
正準verification command
             ↓
Claude Codeが実装・修正・再実行
             ↓
Hooks / CIが同じpolicyを再実行
             ↓
Evidenceを残す
```

たとえば、終了条件を、

```text
Claude Codeが「完了」と言った
```

ではなく、

```text
正準verification commandがexit 0
+ 必須artifactが生成された
+ diffが許可scope内
```

のような観測可能な条件へ寄せる。

Claude Codeはその条件を満たすために自由に試行できる。

しかし、**完了条件そのものは試行loopの外側に置く**。

この分離があるほど、より大きな仕事をagentへ渡しやすくなる。

## 誤解しないでほしいこと

この記事は「Claude Codeにテストを任せるな」という話ではない。

逆である。

**もっと任せるために、正しさの定義をagentの外へ出す。**

反復実行、failure解析、修正、再検証はagentが強い領域だ。

その能力を活かすほど、

```text
何を正しいとするか
何がblocking conditionか
何を証拠として残すか
```

を明示する価値が上がる。

## 持ち帰るべき1文

**Claude Codeにテストを全部任せるなら、テストの実行ではなく「何をpassとするか」を先に固定する。**

agentは何度でも実行できる。

だからこそ、**正しさの定義は実行loopの外に置く。**

## 一次情報・実験証跡

- [Claude Code | Anthropic](https://www.anthropic.com/product/claude-code)
- [Automate workflows with hooks | Claude Code Docs](https://code.claude.com/docs/en/hooks-guide)
- [Hooks reference | Claude Code Docs](https://code.claude.com/docs/en/hooks)
- [pre-commit documentation](https://pre-commit.com/)
- [prek compatibility](https://prek.j178.dev/compatibility/)
- [controlled evidence](https://github.com/KAFKA2306/articles/blob/aa33a88e5bf165ac4085c7462e67f23283647926/benchmarks/verification-stack-v2/results/controlled/summary.json)
- [experiment protocol and artifacts](https://github.com/KAFKA2306/articles/tree/aa33a88e5bf165ac4085c7462e67f23283647926/benchmarks/verification-stack-v2)
