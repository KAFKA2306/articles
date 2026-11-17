---
title: "AIの「できました」をどう確かめるか｜Kafstylerの設計と二段階の検証"
emoji: "🔎"
type: "tech"
topics: ["ai", "claudecode", "codex", "agentskills", "testing"]
published: true
published_at: 2026-11-17 22:03
---

AIエージェントに手順書を書かせ、リンクも表示も正常だったとします。それでも、その手順書を頼りに設定すると機能が起動しないことがあります。たとえば、Codexでプラグインを導入する手順に、フックを承認する操作が抜けていた場合です。リンク先も画面表示も、そのまま通ります。

Kafstylerは、Claude CodeとCodexで、作業を始める前に「誰がどの入口で何を確認できれば完了か」を決め、提出前に実物をその条件で確かめるプラグインです。今回はこの原稿にKafstylerの手順を使い、さらに**誤りを入れた原稿を使って、その評価手順も確かめました**。見出しと出典URLの確認を通過した2つの誤りを、読者の操作と実装に照らした確認では識別できました。

対象は2026年11月17日時点のKafstyler 0.5.6です。実装へのリンクは調査した版に固定しました。 [対象コミット](https://github.com/KAFKA2306/kafstyler/commit/43178a5d62b405e7d469f5dc7f46e596a001f456)

## 1. プラグインが引き受ける仕事

「READMEを改善して」という依頼では、文章を整えた時点で終えることも、初めて読む人が起動できた時点で終えることもできます。Kafstylerの `charter` は後者のように、利用者の入口と観測できる結果を先に定めます。たとえば「空の作業ディレクトリで、READMEに書かれた操作を上から実行すると、サンプルへのリクエストがHTTP 200を返す」です。起動できない読者がいてもその条件を満たせる場合は、誰の環境を対象にするかも条件に加えます。 [目標設定](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/skills/charter/SKILL.md)

プラグインは作業規約をモデルの文脈に渡し、必要に応じて呼び出せる7つのスキルを同梱します。実際の起動コマンド、テスト、公開APIは、対象プロジェクトで使えるものをエージェントが選んで実行します。検証ツールの終了コードや公開ページは、完了を判断するための観測です。フックが渡すのは確認の指示です。成果物の合否は、エージェントが実物とその作業の合格条件を照らして判断します。 [作業規約](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/AGENTS.md) · [配布ファイル一覧](https://github.com/KAFKA2306/kafstyler/tree/43178a5d62b405e7d469f5dc7f46e596a001f456)

## 2. 依頼から提出までに起きること

Claude CodeとCodexのマニフェストは、同じ `hooks/quality.sh` を呼びます。違いが出るのは、ホストに応じたプラグインのルート指定と、最初の `Stop` に対する応答です。 [Claude Codeのマニフェスト](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/.claude-plugin/plugin.json) · [Codexのマニフェスト](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/.codex-plugin/plugin.json) · [フックの実装](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/hooks/quality.sh)

| イベント | 同梱フックが返すもの |
| --- | --- |
| `SessionStart` | プラグイン同梱の `AGENTS.md` を含む作業規約 |
| `SubagentStart` | 作業規約に加え、親から受け取った合格条件で調べるよう委譲先に伝える追加コンテキスト |
| `UserPromptSubmit` | 作業前に `charter`、提出前に `benchmark`、人向け文書に `humanizer` を使う指示 |
| `Stop` | 初回は成果物を照合する指示。Claude Codeには追加コンテキスト、Codexには `decision: "block"` と続行理由を返す。フックで続行したあとの入力では `{}` を返す |

Codexの導入後、`/hooks` でKafstylerのフックを確認して承認します。承認前も、スキルは手動で選べます。 [Kafstylerの導入手順](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/README.md#codex) · [Codexのフック承認](https://learn.chatgpt.com/docs/hooks#review-and-trust-hooks)

`Stop` は提出前の再確認を1回促します。定期実行を登録するのは、Claude Codeの `/loop` です。Claude Codeで `deliver` を使うとき、Kafstylerは `/loop` で同じ依頼を再実行し、各回で前回の結果を引き継ぐよう定めています。完了か中止、または人の操作を待つ状態になったら、対象ジョブを `CronDelete` で解除し、`CronList` で確認します。`/loop` の定期実行はセッションに属します。 [Kafstylerの連携手順](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/skills/deliver/SKILL.md) · [Claude Codeの定期実行](https://code.claude.com/docs/en/scheduled-tasks) · [Claude CodeのStop](https://code.claude.com/docs/en/hooks#stop-decision-control) · [CodexのStop](https://learn.chatgpt.com/docs/hooks#stop)

### 導入と呼び出し

次はKafstylerのREADMEに掲載されている導入コマンドです。Claude Codeは2.1.292以降を使い、配布元は `KAFKA2306/agent-resources` です。Codexの配布元は `KAFKA2306/kafstyler` です。導入後は対象プロジェクトでホストを起動し、普段どおり依頼できます。スキルを直接指定するときは、Claude Codeで `/kafstyler:charter` のように呼び、Codexでは `$` で選びます。 [導入と更新の手順](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/README.md#プラグインの使い方) · [Claude Codeの導入コマンドの要件](https://code.claude.com/docs/en/discover-plugins#add-and-install-from-your-shell)

```sh
# Claude Code
claude plugin install kafstyler --marketplace KAFKA2306/agent-resources --scope user

# Codex
codex plugin marketplace add KAFKA2306/kafstyler
codex plugin add kafstyler@kafstyler
```

Claude Codeで変更の実装と利用経路の検証を続ける例です。間隔は例の値です。

```text
/loop 5m /kafstyler:deliver READMEの起動手順を空の作業ディレクトリから試し、サンプルにアクセスできるまで直す
```

## 3. 7つのスキルと一次資料の置き場所

スキルを選ぶときは、どの判断や作業が欠けているかを見ます。目標が曖昧なら `charter`、合格条件が当てにならないなら `scrutiny`、同じ入力で改善を比べたいなら `benchmark` です。作業の途中で別スキルを呼ぶときは、対象、版、入力、期待する結果、依頼範囲を渡します。実行中のスキルには戻らず、同じ対象・版・前提で済んだレビューは再利用します。 [スキル間の連携](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/AGENTS.md#コマンドの連携)

| スキル | 渡すものと得られる結果 |
| --- | --- |
| [`charter`](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/skills/charter/SKILL.md) | 依頼、利用者、普段の入口から、合格条件と確認手段を決める |
| [`scrutiny`](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/skills/scrutiny/SKILL.md) | 前提、現行方式、候補、合格条件から、重大な反例とその判別手順を探す |
| [`benchmark`](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/skills/benchmark/SKILL.md) | 公式資料、外部の実践、数理モデル、今月の関連論文を先に調べ、同じ入力と合格条件で合否と改善幅を測る |
| [`deliver`](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/skills/deliver/SKILL.md) | 許可された変更を実装し、普段の入口から結果を確かめる |
| [`humanizer`](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/skills/humanizer/SKILL.md) | 原稿、読者、一次資料から、手順を追えて主張を検証できる文章に直す |
| [`schema`](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/skills/schema/SKILL.md) | 答えたい問いと実データから、記録の粒度、識別子、来歴、検証方法を決め、定義ごとに正本を置く |
| [`prune`](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/skills/prune/SKILL.md) | 重複や使われない経路を削り、残した入口、参照、動作を確かめる |

`AGENTS.md` は作業の共通規約、`MISSION.md` はKafstylerの目的と保守手順、`BIBLES.md` は判断に使う資料の台帳です。たとえばフックの挙動を説明するときは、同梱の台帳から両ホストの公式仕様に進み、実際の `quality.sh` と照合できます。台帳は日次保守で一分野ずつ見直す設計です。候補資料の採用は、同じ作業で判断か操作が改善するかで決めます。 [ミッションと更新手順](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/MISSION.md) · [資料の見直し](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/BIBLES.md#資料の見直し)

## 4. 一段目では原稿を確認した

今回の読者の仕事は、プラグインの導入後に「何が起動するか」「追加操作は何か」「いつ完了と判断できるか」を説明し、自分の案件で導入を判断することです。固定したコミットの作業規約とスキルのMarkdownを読み、執筆と評価の手順に使いました。原稿の説明を、マニフェスト、フック、ホストの公式仕様に照らしました。さらに、`Stop` の説明が指しているシェルをBashで直接実行しました。

次のコマンドは、参照したコミットをチェックアウトしたKafstylerのルートで実行できます。

```sh
for active in false true; do
  printf '{"stop_hook_active":%s}\n' "$active" |
    CLAUDE_PLUGIN_ROOT="$PWD" bash hooks/quality.sh review
  printf '{"stop_hook_active":%s}\n' "$active" |
    PLUGIN_ROOT="$PWD" bash hooks/quality.sh review codex
done
```

| 入力 | Claude Code向けの標準出力 | Codex向けの標準出力 |
| --- | --- | --- |
| `stop_hook_active: false` | `hookSpecificOutput.additionalContext` に提出前の確認指示 | `decision: "block"` と `reason` |
| `stop_hook_active: true` | `{}` | `{}` |

これはシェルに4通りの入力を渡して観測した結果です。ホストがフックを読み込んでモデルが指示に沿って修正するところまでは、この実験の確認範囲外です。ここで再現できるのは、提出前の見直しを要求する応答と、同じ確認を再要求しない条件です。 [テスト対象のシェル](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/hooks/quality.sh)

## 5. 二段目では原稿の確認方法を試した

見出しと出典URLの確認は、本文の手順が誤っていても通るでしょうか。第2節を対象に、正しい記述を残した版と、次の誤りを一つずつ加えた版を用意しました。評価結果を説明するこの節は判定対象から外し、3版の見出しと出典URLをそろえて調べました。

| 原稿 | 見出しと出典URLを照合 | 読者の操作と実装を照合 |
| --- | --- | --- |
| 正しい記述を残した版 | 合格 | 合格 |
| Codexの `/hooks` 承認操作だけ削除 | 合格 | 不合格。導入後に読者が行う操作が抜けている |
| `Stop` が定期実行を登録するという記述に変更 | 合格 | 不合格。シェルの出力と公式の `/loop` の仕様に反する |

形式だけでは、用意した誤りを **2件中2件** 見逃しました。操作と実装の照合では、正しい版を残し、誤りを **2件中2件** 検出できました。後者の判定根拠には、原稿を生成した手順から独立して読めるホストの仕様と、シェルの出力を使いました。件数はこの2つの誤りに限ります。 [Codexのフック承認](https://learn.chatgpt.com/docs/hooks#review-and-trust-hooks) · [Claude Codeの定期実行](https://code.claude.com/docs/en/scheduled-tasks)

この比較で追加したのは、形式では確認できなかった2つの問いです。

1. Codexで導入が済んだ直後、読者はフックを動かすために何をするか。原稿で該当箇所を示せるか。
2. 初回の `Stop` が返すものと、定期実行を登録する操作を区別できるか。原稿の説明はシェルの出力と一致するか。

Kafstylerの `benchmark` には、既知の不合格例を落とし、合格例を通す確認がすでにあります。今回はその手順を記事の判定に適用しました。共通手順そのものに不足が見つかったときは、使った版と再現入力を残し、元の案件と別分野の案件で修正前後を試します。記事の評価に固有の不足なら記事側で直します。今回の見逃しは、記事側の確認に読者の操作を加えることで解消しました。 [評価手順](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/skills/benchmark/SKILL.md) · [変更を本体に戻す手順](https://github.com/KAFKA2306/kafstyler/blob/43178a5d62b405e7d469f5dc7f46e596a001f456/MISSION.md#更新手順)

## 自分の手順書で試す

手順書を1本選び、読者が一番よく使う操作を一つ決めます。「初回の利用者が権限を有効にして、実際に機能を使える」のように、読み終わった人が達成する結果を一文にします。

次に、正しい原稿から、その操作に必要な権限、前提、コマンドのどれか一つを外したコピーを作ります。2版に同じレビューをかけます。両方が通るなら、原稿の文体や項目数を見直すより先に、欠けた操作を検出できる判定を一つ足してください。判定に開く資料や実行するコマンドも書き、同じ2版でもう一度試します。

プラグインを選ぶときも同じです。現在の `AGENTS.md` と既存のテストでその失敗を検出できるなら、それを使えます。目標の決め方や提出前の確認を案件ごとに繰り返し書いているなら、共通のスキルとフックを導入する価値を比較できます。実機や認証が必要な操作は実行できる人と環境を決め、観測が取れるまで合格を保留します。 [Claude Codeの実践ガイド](https://code.claude.com/docs/en/best-practices) · [Agent Skillsの仕様](https://agentskills.io/specification)

この記事の調査・執筆・実験にはAIエージェントを使用しました。
