---
title: "自動化を増やしても、品質は増えない"
emoji: "🪝"
type: "tech"
topics: ["git", "ci", "automation", "testing", "developerexperience"]
published: true
published_at: 2026-08-15 09:33
---

目覚まし時計を2個にしても、**「何時に起きるべきか」というルールは2倍にはならない**。

ソフトウェアの自動化でも、同じことが起きる。

チェックを走らせる仕組みを増やす。CIを増やす。hook runnerを2つ残す。新しいagentやschedulerを追加する。すると、なんとなく「安全性が増えた」ように見える。

しかし本当に増えたのが**実行経路**だけなら、正しさを決める能力は増えていない。

この記事の結論は単純だ。

> **実行する仕組みと、正しさを決める仕組みを分けて考える。**

この区別ができると、ツール移行で「何を残すべきか」「何を消してよいか」「何を比較すべきか」がかなり明確になる。

ここでは `pre-commit` と `prek` のcontrolled experimentを使って、この原則を実測する。

## 3分でわかる要点

ソフトウェア品質の自動化には、少なくとも2種類の責務がある。

```text
Git event
   ↓
hook runner          ← いつ・どこで・何を起動するか
   ↓
Ruff / formatter / tests / custom checker
   ↓                  ← 何を正しいと判定するか
pass / fail / patch
```

この記事では前者を **trigger authority**、後者を **policy authority** と呼ぶ。

`pre-commit` を `prek` に置き換えるとき、本当に確認したいのは「新しいrunnerを入れたか」ではない。

**同じpolicyを起動した結果が保存されるか**である。

今回のcontrolled fixtureでは、同じhook policyを `pre-commit` と `prek` から実行した結果、次の4条件がすべて一致した。

- changed files
- 最終content SHA-256
- diff SHA-256
- 2回目の実行で変更を生まないこと（idempotence）

つまり、このfixtureで観測された範囲では、runnerの交換は**品質policyの変更ではなく、trigger実装の置換**として扱えた。

これは「prekが常に優れている」という話ではない。

もっと再利用可能な結論は、**ツール名ではなく、そのツールが何のauthorityを持っているかを比較する**ことだ。

## なぜこの区別に価値があるのか

ツールを増やすことは簡単だ。

難しいのは、増えたツールが本当に新しい能力を追加したのか、それとも既存能力を別経路でもう一度起動しているだけなのかを見分けることだ。

この区別をしないと、移行のたびに次のような状態になりやすい。

```text
旧runner + 新runner
旧formatter + 新formatter
旧lint + 新lint
旧CI job + 新CI job
```

見た目のチェック数は増える。しかし同じconcernに複数のblocking authorityを残すと、設定・実行時間・失敗理由・保守対象も増える。

一方、authorityを分解して考えると判断が変わる。

```text
何を正しいとするか？      → policy
いつ実行するか？          → trigger
どの範囲に適用するか？    → scope
結果をどこでblockingするか？ → enforcement
```

この4つを分けるだけで、「新しいツールを追加した」という事実を「品質が上がった」という代理指標にしなくて済む。

## 今回、何を証明したのか

Verification Stack v2では、結果を見る前に `HOOK-PATCH-PARITY-001` を固定した。

比較対象に求めたのは次の4点だけだ。

1. 同じファイルが変更される
2. 最終content SHA-256が一致する
3. diff SHA-256が一致する
4. 再実行がidempotentである

raw diagnosticの件数は欠陥数として数えない。速度もcorrectnessを上書きする条件にはしない。

このfixtureで問うたのは、**runnerを交換しても既存policyのobservable effectを保存できるか**だった。

再現用のcontrolled summaryは固定commitに残している。

- https://github.com/KAFKA2306/articles/blob/aa33a88e5bf165ac4085c7462e67f23283647926/benchmarks/verification-stack-v2/results/controlled/summary.json

## 観測結果

`hook_patch_parity` は4条件をすべて満たした。

| 観測 | 結果 |
|---|---|
| same changed files | true |
| same content SHA-256 | true |
| same diff SHA-256 | true |
| both idempotent | true |

ここから言えることは限定的だ。

**このfixtureでは、runnerを `pre-commit` から `prek` に交換しても、hookが作ったpatchのobservable resultは変わらなかった。**

一方、全repo・全hookで完全互換だとは証明していない。language-specific hook、network依存hook、特殊stage、CI環境差は今回のground truth外だ。

## 公式ドキュメントでも責務は分かれている

`pre-commit` の公式ドキュメントは、自身をmulti-language pre-commit hooksを管理・保守するframeworkと説明している。設定したhookをインストールし、Git eventに応じて実行するのが中心責務だ。

https://pre-commit.com/

`prek` も既存の `.pre-commit-config.yaml` をそのまま利用できるdrop-in replacementを志向している。互換性ドキュメントでも、既存configや一般的なworkflowを継続利用できることを明示している。

https://prek.j178.dev/configuration/
https://prek.j178.dev/compatibility/

一方、たとえばRuffでは、lint ruleの有効化・無効化は `lint.select`、`lint.extend-select`、`lint.ignore` などの設定で決まる。

https://docs.astral.sh/ruff/linter/

つまり、少なくともこの構成では責務を次のように分けられる。

```text
pre-commit / prek
  → hookを起動する

Ruff / formatter / tests / custom checker
  → pass / fail / patchを決める
```

Ruffのlint ruleを変えたならpolicyが変わる。formatter設定を変えたなら生成patchが変わる。

しかし、同じ設定と同じtoolを別runnerから起動しただけなら、policyを二重化したことにはならない。

## 「両方残す」は安全策とは限らない

移行時に旧runnerと新runnerを永久に併存させると、一見安全に見える。

しかし同じhook集合を二重に起動するだけなら、品質authorityは増えない。

確認すべきなのは**parity**だ。

1. fixtureを固定する
2. 旧runnerでpatchを保存する
3. 新runnerで同じfixtureを実行する
4. changed filesとcontent/diff hashを比較する
5. 2回目がidempotentか確認する
6. parityを満たした範囲だけ旧runnerを削除する

この順なら「新しいrunnerを追加したから安全」という代理指標を使わずに済む。

## この考え方はhook runner以外にも持ち込める

今回の実証対象は `pre-commit` と `prek` だけだ。

ただし、**authorityを分離してから比較する**という判断方法そのものは、他の自動化にも持ち込める。

たとえば、新しいCI runner、task runner、test runner、formatter、agent、schedulerを導入するとき、最初にこう問える。

> この新しい仕組みは、何を新しく判断できるようにするのか？

答えが「同じものを別経路で実行する」だけなら、それは品質能力の追加ではなく、実行基盤の変更かもしれない。

逆に、新しいpolicy、検出能力、境界条件、runtime validation、blocking ruleが追加されるなら、それは実際に判断能力を増やしている可能性がある。

この問いを先に置くと、流行しているツールを集めることより、**システムが何を判断できるようになったか**を設計の中心にできる。

## changed-file ratchetでlegacy migrationを止めない

大きなrepoでは、全ファイルを一度に新policyへ合わせることが現実的でない場合がある。

その場合もrunnerをpolicy authorityに昇格させる必要はない。

新policyをchanged filesにだけ適用するratchetを置き、既存違反は別のbacklogとして縮小する。重要なのは、同じconcernに旧policyと新policyのblocking authorityを永久併存させないことだ。

移行完了条件は「新toolを導入した」ではなく、**predeclared parityを満たし、superseded configを削除できた**ことに置く。

## 何を測っていないか

今回のcontrolled evidenceはhook patch parityを測ったもので、runnerの普遍的な速度順位、全pre-commit featureの互換性、全repositoryでのmigration costは測っていない。

したがって「prekは常にpre-commitより優れている」という結論には使えない。

また、real-repo observationはexternal validityの確認用であり、ground truthがないdiagnostic量を品質ランキングには使っていない。

## 判断を反転させる反証条件

この結論は、runner自身が他方にはないblocking policyを持ち、そのpolicyがrepositoryの必須要件であると実証された場合には反転する。

また、同一fixtureでchanged files、最終content、diff、idempotenceのいずれかが一致しないなら、runner交換を単なるtrigger置換とは扱えない。

それまでは、hook runnerの選択と品質policyの選択を別の意思決定として扱う方が証拠に忠実だ。

## 持ち帰るべき1文

**自動化を増やす前に、「何を実行する仕組みなのか」と「何を正しいと決める仕組みなのか」を分ける。**

runnerはpolicyを起動する。

**policyそのものではない。**

## 一次情報

- pre-commit documentation: https://pre-commit.com/
- prek configuration: https://prek.j178.dev/configuration/
- prek compatibility: https://prek.j178.dev/compatibility/
- Ruff linter documentation: https://docs.astral.sh/ruff/linter/
- controlled evidence: https://github.com/KAFKA2306/articles/blob/aa33a88e5bf165ac4085c7462e67f23283647926/benchmarks/verification-stack-v2/results/controlled/summary.json
- experiment protocol and artifacts: https://github.com/KAFKA2306/articles/tree/aa33a88e5bf165ac4085c7462e67f23283647926/benchmarks/verification-stack-v2
