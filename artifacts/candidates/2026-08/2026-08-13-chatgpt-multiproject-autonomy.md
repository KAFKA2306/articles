---
title: "1か月でPR803件。ChatGPTに146リポジトリを見せて分かった、コード生成より重要なこと"
emoji: "🛰️"
type: "tech"
topics: ["chatgpt", "github", "automation", "githubactions"]
published: false
---

GitHubに公開リポジトリが146個ある。

この状態になると、問題は「コードを書けるか」ではなくなります。

どのプロジェクトが止まっているか。何が人間待ちか。どのIssueを先に片付けるべきか。PRはmergeしてよいか。CIは本当に完了条件を証明しているか。deploy後に確認したか。作業branchや古いPRが残っていないか。

2026年7月13日から8月13日までの約1か月、私はChatGPTとの会話を、こうした**複数プロジェクトの状態遷移を制御する場所**として使いました。

GitHub Search APIで同期間を確認すると、`KAFKA2306` アカウントではIssueが384件作成され、PRは803件作成され、680件が同期間内にmergeされています。

- Issues: https://api.github.com/search/issues?q=author%3AKAFKA2306+is%3Aissue+created%3A2026-07-13..2026-08-13
- Pull Requests: https://api.github.com/search/issues?q=author%3AKAFKA2306+is%3Apr+created%3A2026-07-13..2026-08-13
- Merged Pull Requests: https://api.github.com/search/issues?q=author%3AKAFKA2306+is%3Apr+is%3Amerged+merged%3A2026-07-13..2026-08-13
- GitHub profile: https://api.github.com/users/KAFKA2306

ただし、この数字をそのまま「803個の成果」と読むのは間違いです。実際、誤操作で作られた一時Issueや重複Issueもありました。

- https://github.com/KAFKA2306/rule-scribe-games/issues/83
- https://github.com/KAFKA2306/furutsatotax/issues/13

自動化すると、成功だけでなく失敗も高速になります。

この1か月で一番大きかった発見は、**マルチプロジェクト開発を自律化する中心は、コード生成ではなく「状態・契約・証拠・停止条件」を機械が読める形にすること**でした。

## 最初の失敗：プロジェクトごとにAIへお願いすると、管理仕事が増える

最初は単純でした。

```text
repo Aを直す
repo Bを調べる
repo CにIssueを作る
repo Dをdeployする
```

一件ずつ見るなら、これでも動きます。

しかし対象が増えると、人間側に別の仕事が発生します。

```text
次はどのrepoを見る？
↓
前回どこまで終わった？
↓
PRは残っていない？
↓
CI成功はdeploy成功まで含む？
↓
Issueをcloseしてよい？
↓
似た作業を別repoでまたやっていない？
```

つまりAIに実装を渡しても、**仕事の選択と完了判定が人間に残る**。

ここを消さない限り、プロジェクト数が増えるほど人間がオーケストレーターになります。

## GitHubを「記憶」ではなく状態機械にした

そこで会話の内容をGitHub上の明示的な状態へ落とすようにしました。

基本単位は次です。

```text
Issue
  = 何を変えるか + Acceptance Criteria

Pull Request
  = 実装候補 + 差分

GitHub Actions
  = 機械検証の証拠

main / production
  = 正準状態
```

重要なのは、ChatGPTが「終わったと思う」ことを完了条件にしないことです。

たとえば中央管理用の `agent-resources` では、いきなりゲーム風ダッシュボードを作らず、17個の小さなIssueへ分解しました。

最初はJSON Schema、次に公開対象repoの設定、GitHub collector、lane判定、`dashboard.json`、その後でUIです。

- Schema: https://github.com/KAFKA2306/agent-resources/issues/3
- public repo config: https://github.com/KAFKA2306/agent-resources/issues/4
- repository collector: https://github.com/KAFKA2306/agent-resources/issues/5
- Issue / PR collector: https://github.com/KAFKA2306/agent-resources/issues/6
- Actions collector: https://github.com/KAFKA2306/agent-resources/issues/7
- lane logic: https://github.com/KAFKA2306/agent-resources/issues/8
- canonical dashboard JSON: https://github.com/KAFKA2306/agent-resources/issues/9
- QA: https://github.com/KAFKA2306/agent-resources/issues/19

見た目より先にデータ構造を固定した理由は単純です。

**AIが次の行動を選ぶには、プロジェクトの状態が機械可読でなければならない。**

## `working / waiting / done / failed` の4状態まで減らす

複数repoを横断すると、GitHubの生の状態は多すぎます。

Issueのopen/closed、PRのdraft/open/merged、workflowのqueued/in_progress/completed、conclusionのsuccess/failure/cancelled……。

これをそのまま人間へ見せても、次の行動は決まりません。

そこで中央ダッシュボードでは、最終的に4つへ圧縮しました。

```text
working  = AIやworkflowが進められる
waiting  = 人間判断・外部依存待ち
done     = 完了条件まで証拠がある
failed   = 失敗または要確認
```

この変換自体もUIではなく純粋な判定ロジックとしてIssue化しています。

https://github.com/KAFKA2306/agent-resources/issues/8

ここで効いたのが `laneReason` です。

単に `waiting` とするのではなく、**なぜ止まっているかを機械が説明できる**ようにする。

すると次の巡回で、ChatGPTはチャット履歴を全部思い出す必要がありません。

現在のGitHub状態を読み、`working` の中から価値の高いものを選び、`waiting` は人間へ返せます。

## 自律化したのは「作業」より「次を決めるループ」だった

この1か月で繰り返し使うようになったループは、だいたい次の形です。

```text
全体状態を監査
↓
候補を比較
↓
今もっとも価値の高い1件を選ぶ
↓
Issueの完了条件を読む
↓
実装
↓
テスト / CI
↓
PR / merge
↓
公開物・本番を確認
↓
branch / PR / 一時ファイルをcleanup
↓
次の状態を再取得
```

ポイントは「AIに好きに作らせる」ではありません。

**選択肢を広く持たせる一方、完了判定を狭くする**ことです。

実装方法はAIに任せても、DoneはAcceptance Criteriaと証拠でしか変わりません。

## 大きい仕事は、AIが迷わない大きさまで分解する

Prompt Vaultを複数Pagesの共有Asset Registryにする作業でも同じでした。

いきなり「全repoの画像管理を統一する」と頼むと、設計・移行・deploy確認が混ざります。

そこで正準registryを作るIssueと、全repoを監査するIssueを分け、consumerごとの移行はさらに小Issueにします。

- Asset Registry: https://github.com/KAFKA2306/prompt-vault/issues/55
- consumer inventory / migration: https://github.com/KAFKA2306/prompt-vault/issues/57
- 最初のconsumer `travel`: https://github.com/KAFKA2306/travel/issues/20

`travel` 側では、source SHA-256、Prompt Vault commit、destination SHA-256をlockし、build後のassetと公開URLまで確認する契約にしました。

ここで人間がやるのは「この仕組みを採用するか」の判断です。

ファイルをコピーする、hashを照合する、buildする、公開URLを確認する、といった機械的作業は、人間が毎回やる理由がありません。

## 自律化の前に、複雑性を削る

もう一つ重要だったのは、**複雑なものをそのまま自動化しない**ことでした。

`finBI` は古いStreamlit試作を延命せず、公開Web runtimeを4ファイルに縮約しました。

```text
index.html
styles.css
app.js
worker.mjs
```

金融計算はPython側の1本へ寄せ、ブラウザではPyodide Web Workerから呼びます。

- redesign: https://github.com/KAFKA2306/finBI/issues/8
- legacy縮約: https://github.com/KAFKA2306/finBI/issues/6

自動化で最も高くつくのは、実装時間より**状態数**です。

providerが5個、deployment方式が3個、計算実装がPythonとJavaScriptの2系統、旧runtimeも互換維持……となれば、AIが確認すべき分岐も増えます。

だから先に消す。

```text
機能を増やす
```

より、

```text
同じ価値をより少ない状態で実現する
```

方を優先しました。

## 「取得できた」と「正しい」を分ける

AI運用で特に危険だったのは、tool callやCIが成功すると、それを成果物の正しさまで拡大解釈しやすいことです。

`finBI` では実際に、snapshotの `retrieved_at` と、その時点ではまだ利用できなかったFRED観測値が共存するpoint-in-time不整合が見つかりました。

https://github.com/KAFKA2306/finBI/issues/10

UIも計算も正しくても、provenanceが未来を含んでいれば再現可能な分析ではありません。

そこで、単に

```text
observation_date <= retrieved_at.date()
```

を見るのではなく、source側のavailability / vintage timestampまで検証する契約へ変えました。

この考え方は他repoにも移植できます。

```text
tool success != product success
CI success != production success
file exists != verified artifact
HTTP 200 != correct content
```

自律化するほど、「成功」という1語を細かく分解する必要があります。

## 人間を残す場所も明示した

全部をAIへ渡したわけではありません。

むしろ、機械作業を減らすほど、人間が残る場所を明示しやすくなりました。

たとえば投資研究の `investor2` では、分析結果から自動売買へ進ませず、判断直前の状態をimmutableなDecision Snapshotとして固定する設計にしています。

- Decision Snapshot: https://github.com/KAFKA2306/investor2/issues/34
- Hypothesis Lab: https://github.com/KAFKA2306/investor2/issues/35

3つのgateが全てpassして初めて `eligible_for_human_review` になるだけで、売買そのものは機械に委ねません。

この境界は開発でも同じです。

```text
AIに任せる
- 状態収集
- 差分生成
- 定型検証
- hash照合
- build
- deploy確認
- cleanup候補の抽出

人間に残す
- 何を作るか
- 公開してよいか
- 不可逆な判断
- 証拠が足りない時の意味判断
```

自律化とは、人間を消すことではなく、**人間を判断だけに寄せること**でした。

## ChatGPTのScheduled Tasksは「repoごと」ではなく「制御ループ」に使う

OpenAIの公式ヘルプでは、ChatGPTのScheduled Tasksは単発・定期・監視タスクを扱え、実行頻度は最大でも1時間に1回です。またアクティブタスク数にもプラン別上限があります。

- https://help.openai.com/ja-jp/articles/10291617-scheduled-tasks-in-chatgpt

GitHub連携についても、OpenAI公式はChatGPTが接続したrepositoryのコードやREADME等を取得・検索・分析できると説明しています。

- https://help.openai.com/ja-jp/articles/11145903-connecting-github-to-chatgpt

146 repoに対して146個の監視タスクを作る発想は、最初からスケールしません。

必要なのはrepoごとの定期タスクではなく、**中央状態を見て次の1件を選ぶ制御ループ**です。

```text
146 repositories
      ↓
GitHub facts
      ↓
normalized state
      ↓
4 lanes
      ↓
priority selection
      ↓
one next outcome
```

この構造なら、プロジェクトが増えても人間の巡回回数は増えません。

## 逆に、細かなバグ解消は記事にしない

この運用を続けると、記事候補も大量に生まれます。

Pythonのquoteが壊れた。Viteの環境変数名が違った。VRChatのUploaderが途中で止まった。

技術的には書けますが、それぞれを独立した記事にすると、読者に残るのは局所的な手順です。

そこで現在は、こうした原稿をarchiveへ回しています。

https://github.com/KAFKA2306/articles/blob/main/artifacts/archive/README.md

残すのは、その事故から複数プロジェクトへ再利用できる仕組みを取り出せた場合だけです。

```text
quote破損
→ compile gate

環境変数名ミス
→ deploy前contract validation

Uploader事故
→ tool successと実環境completionの分離
```

記事の主語を「バグ」ではなく「再利用できるシステム」にする。

これは開発自体と同じ整理でした。

## 1か月後に残った設計

最終的に、ChatGPTを使ったマルチプロジェクト開発は次の形へ収束しました。

```text
Human
  └─ goal / irreversible decisions / publication

ChatGPT
  └─ portfolio audit
     → choose next outcome
     → inspect evidence
     → design bounded task
     → verify completion

GitHub
  ├─ Issue = contract
  ├─ PR = candidate change
  ├─ Actions = machine evidence
  ├─ main = canonical state
  └─ Pages / production = observed outcome

Automation
  └─ repetitive collection / validation / build / deploy / cleanup
```

AIが賢くなったから成立した、というより、**AIが迷わないように状態を減らし、成功条件を狭くし、証拠をGitHubへ残したから成立した**という方が近いです。

1か月で最も変わったのは、コードを書く速度ではありません。

人間が毎朝「今日はどのrepoを触ろう」と考える必要がなくなり、代わりに

**「今、人間にしか決められないことは何か」**

だけを見ればよい構造へ近づいたことでした。
