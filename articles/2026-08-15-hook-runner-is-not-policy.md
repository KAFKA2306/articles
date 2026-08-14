---
title: "hook runnerを増やしても品質ルールは増えない"
emoji: "🪝"
type: "tech"
topics: ["git", "ci", "python", "testing", "developerexperience"]
published: false
---

`pre-commit` を `prek` に置き換える。あるいは両方を残す。

このとき最初に決めるべきなのは「どちらが速いか」ではない。**hook runnerに品質ルールの最終決定権を持たせるのか**だ。

今回のcontrolled fixtureでは、同じhook policyを `pre-commit` と `prek` から実行した結果、changed files、最終content SHA-256、diff SHA-256がすべて一致し、両方とも2回目の実行で変更を生まなかった。観測された差はpolicyではなくtrigger実装の差として扱うべきだった。

## 先に固定した判定条件

Verification Stack v2では、結果を見る前に `HOOK-PATCH-PARITY-001` を固定した。比較対象に求めたのは次の4点だけだ。

- 同じファイルが変更される
- 最終content SHA-256が一致する
- diff SHA-256が一致する
- 再実行がidempotentである

raw diagnosticの件数は欠陥数として数えない。速度もcorrectnessを上書きする条件にはしない。このfixtureで問うたのは、runnerを交換しても既存policyのobservable effectを保存できるかだった。

再現用のcontrolled summaryは固定commitに残している。

- https://github.com/KAFKA2306/articles/blob/aa33a88e5bf165ac4085c7462e67f23283647926/benchmarks/verification-stack-v2/results/controlled/summary.json

## 観測結果

`hook_patch_parity` は次の4条件をすべて満たした。

| 観測 | 結果 |
|---|---|
| same changed files | true |
| same content SHA-256 | true |
| same diff SHA-256 | true |
| both idempotent | true |

ここから言えるのは限定的だ。このfixtureでは、runnerを `pre-commit` から `prek` に交換しても、hookが作ったpatchのobservable resultは変わらなかった。

一方、**全repo・全hookで完全互換だとは証明していない**。language-specific hook、network依存hook、特殊stage、CI環境差は今回のground truth外だ。

## runnerとpolicyを分ける

`pre-commit` の公式ドキュメントは、Git hookを管理・保守するframeworkとして説明している。`prek` も `.pre-commit-config.yaml` を利用してhookを実行するrunnerであり、既存設定との互換を移行面の中心に置いている。

つまり、この層の責務は**いつ・どのhookを起動するか**である。

実際のpolicy authorityはhookの先にいる。

```text
Git event
   ↓
hook runner          ← trigger authority
   ↓
Ruff / formatter / tests / custom checker
   ↓                  ← policy authority
pass / fail / patch
```

Ruffのlint ruleを変えたならpolicyが変わる。formatter設定を変えたなら生成patchが変わる。しかし、同じ設定と同じtoolを別runnerから起動しただけなら、policyを二重化したことにはならない。

## 「両方残す」は安全策とは限らない

移行時に旧runnerと新runnerを永久に併存させると、一見安全に見える。しかし同じhook集合を二重に起動するだけなら、品質authorityは増えない。

むしろ確認すべきなのはparityだ。

1. fixtureを固定する
2. 旧runnerでpatchを保存する
3. 新runnerで同じfixtureを実行する
4. changed filesとcontent/diff hashを比較する
5. 2回目がidempotentか確認する
6. parityを満たした範囲だけ旧runnerを削除する

この順なら「新しいrunnerを追加したから安全」という代理指標を使わずに済む。

## changed-file ratchetでlegacy migrationを止めない

大きなrepoでは、全ファイルを一度に新policyへ合わせることが現実的でない場合がある。その場合もrunnerをpolicy authorityに昇格させる必要はない。

新policyをchanged filesにだけ適用するratchetを置き、既存違反は別のbacklogとして縮小する。重要なのは、同じconcernに旧policyと新policyのblocking authorityを永久併存させないことだ。

移行完了条件は「新toolを導入した」ではなく、**predeclared parityを満たし、superseded configを削除できた**ことに置く。

## 何を測っていないか

今回のcontrolled evidenceはhook patch parityを測ったもので、runnerの普遍的な速度順位、全pre-commit featureの互換性、全repositoryでのmigration costは測っていない。したがって「prekは常にpre-commitより優れている」という結論には使えない。

また、real-repo observationはexternal validityの確認用であり、ground truthがないdiagnostic量を品質ランキングには使っていない。

## 判断を反転させる反証条件

この結論は、runner自身が他方にはないblocking policyを持ち、そのpolicyがrepositoryの必須要件であると実証された場合には反転する。また、同一fixtureでchanged files、最終content、diff、idempotenceのいずれかが一致しないなら、runner交換を単なるtrigger置換とは扱えない。

それまでは、hook runnerの選択と品質policyの選択を別の意思決定として扱う方が証拠に忠実だ。

**runnerはpolicyを起動する。policyそのものではない。**

## 一次情報

- pre-commit documentation: https://pre-commit.com/
- prek documentation: https://prek.j178.dev/
- Ruff documentation: https://docs.astral.sh/ruff/
- controlled evidence: https://github.com/KAFKA2306/articles/blob/aa33a88e5bf165ac4085c7462e67f23283647926/benchmarks/verification-stack-v2/results/controlled/summary.json
- experiment protocol and artifacts: https://github.com/KAFKA2306/articles/tree/aa33a88e5bf165ac4085c7462e67f23283647926/benchmarks/verification-stack-v2
