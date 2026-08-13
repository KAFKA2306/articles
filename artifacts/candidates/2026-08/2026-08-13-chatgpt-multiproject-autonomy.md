---
title: "146リポジトリは突然こうならなかった。2023年からの個人開発が、ChatGPTのマルチプロジェクト制御になるまで"
emoji: "🛰️"
type: "tech"
topics: ["chatgpt", "github", "automation", "githubactions"]
published: false
---

GitHubに公開リポジトリが146個ある。

2026年7月13日から8月13日までをGitHub Search APIで再確認すると、`KAFKA2306` アカウントではIssueが385件、PRが805件作成され、680件のPRが同期間内にmergeされていました。

- GitHub profile: https://api.github.com/users/KAFKA2306
- Issues: https://api.github.com/search/issues?q=author%3AKAFKA2306+is%3Aissue+created%3A2026-07-13..2026-08-13
- Pull Requests: https://api.github.com/search/issues?q=author%3AKAFKA2306+is%3Apr+created%3A2026-07-13..2026-08-13
- Merged Pull Requests: https://api.github.com/search/issues?q=author%3AKAFKA2306+is%3Apr+is%3Amerged+merged%3A2026-07-13..2026-08-13

数字だけを見ると、この1か月で突然、大量の開発をChatGPTへ渡し始めたように見えます。

でも、GitHubの履歴を古い順に見直すと、実態は違いました。

2023年には金融分析のrepoがあり、2024年には画像収集・選別から外部3D処理までをつなぐ試作があり、2025年にはMCPで役割を分けたエージェント構成、イベント収集・配信、arXivの定期取得とAI要約がありました。

2026年夏に起きたのは、まったく新しいことではありません。

**それまでrepoごとに作ってきた自動化が、GitHubを共通状態として読み、ChatGPTが「次に何を進めるか」まで選ぶ制御ループへ合流した。**

この記事では、直近1か月の派手な件数だけではなく、そこへ至る古い試行も含めて整理します。

> 注記: 古いrepoのREADMEは2026年の監査で更新されているものがあります。したがって、repoの`created_at`は「そのテーマに取り組み始めた時期」の証拠として、現在のREADMEは「現在どのような設計へ整理されているか」の証拠として扱います。現在のREADMEに書かれた設計が、作成当初から同じ形だったとは主張しません。

## まず全体像：3年で変わった「自動化の単位」

私のGitHub上の変化を一番短く書くと、こうなります。

| 時期 | 代表例 | 自動化の単位 | 人間に残っていた仕事 |
|---|---|---|---|
| 2023 | `finBI` | 1つのアプリ | 実行、修正、次の作業選択 |
| 2024 | `AutoPhotogrammetry` | 1本の処理パイプライン | 入力選択、失敗判断、外部実行管理 |
| 2025春 | `mastramcp` | 役割別エージェント / tool | 権限境界、書込承認、役割間の調整 |
| 2025春〜 | VRChat Event Calendar | 収集→検証→配信 | 情報源監査、分類判断、公開判断 |
| 2025秋〜 | `daily-arXiv-ai-enhanced` | 定期取得→AI生成→公開 | テーマ設定、品質基準、例外判断 |
| 2026夏 | `agent-resources` ほか | 複数repoの状態遷移 | 目的、不可逆判断、公開承認 |

重要なのは、使うAIモデルの名前より、**人間が毎回やっていた調整仕事がどの順番でコードや状態へ移ったか**です。

## 2023：まずは「1つのrepoで価値を出す」段階だった

`finBI` は2023年10月25日に作成されています。

- repository: https://github.com/KAFKA2306/finBI
- GitHub API: https://api.github.com/repos/KAFKA2306/finBI

2026年の現在は、Pythonの金融計算を正本にして静的Webから呼び出し、provenanceまで検証する小さなBIへ作り直しています。

しかし、このrepoが古くから存在すること自体が重要です。

当時の自動化の単位は、基本的に**1つのアプリ**でした。

```text
データを取る
→ 計算する
→ 画面に出す
```

それぞれのrepoは独立した道具です。

この段階では「この処理をコードにする」はできても、

```text
どのrepoを直す？
どこまで終わった？
次に何をする？
```

は人間が決めます。

今のマルチプロジェクト制御から見ると原始的ですが、ここが出発点でした。

## 2024：アプリから「処理の鎖」へ広がった

`AutoPhotogrammetry` は2024年4月11日に作成されています。

- repository: https://github.com/KAFKA2306/AutoPhotogrammetry
- GitHub API: https://api.github.com/repos/KAFKA2306/AutoPhotogrammetry
- current README: https://github.com/KAFKA2306/AutoPhotogrammetry/blob/main/README.md

現在のREADMEでは、明示されたWebページから実写画像を収集し、出典とSHA-256を保存し、特徴量を計算し、クラスタリング・選別を行い、必要ならMeshroom / VisualSFM / COLMAPの外部実行へ渡す構成になっています。

ここで単位が、1画面のアプリから**複数stageを持つpipeline**へ変わりました。

```text
collect
→ validate
→ deduplicate
→ feature extraction
→ cluster
→ select
→ external photogrammetry
→ manifest / logs
```

この形になると、「最後のファイルができた」だけでは成功とは言えません。

入力は正しかったか。途中で落ちていないか。どの画像を使ったか。外部プロセスは本当に成功したか。元データを壊していないか。

後に何度も出てくる**manifest、hash、非破壊処理、stageごとの検証**の発想は、マルチrepo管理より前から必要になっていました。

## 2025春：MCPで「AIに何を触らせるか」を分け始めた

`mastramcp` は2025年3月26日に作成されています。

- repository: https://github.com/KAFKA2306/mastramcp
- GitHub API: https://api.github.com/repos/KAFKA2306/mastramcp
- current README: https://github.com/KAFKA2306/mastramcp/blob/main/README.md

現在のREADMEには、MastraとModel Context Protocol（MCP）を使い、Web検索、ファイル操作、パッケージ管理、GitHub操作を役割別エージェントへ分ける設計意図が残っています。

```text
webSearchAssistant
fileSystemNavigator
packageInstallationManager
githubRepositoryManager
```

さらに、読み取りと書き込みを分け、破壊的操作を自動実行しない、という境界も明示されています。

ここで問題は「AIがコードを書けるか」から、

**どのAIに、どのtoolを、どの権限で渡すか**

へ移りました。

これは現在の運用にもそのまま残っています。

自律化を強くするには、権限を広げるのではなく、むしろ

```text
読める範囲
書ける範囲
実行できる操作
人間承認が必要な操作
```

を狭く定義する必要があります。

## 2025春：収集系では「作る場所」と「配る場所」を分ける必要が出た

`vrc_cast_event_calender` は2025年4月15日に作成されています。

- repository: https://github.com/KAFKA2306/vrc_cast_event_calender
- GitHub API: https://api.github.com/repos/KAFKA2306/vrc_cast_event_calender
- current README: https://github.com/KAFKA2306/vrc_cast_event_calender/blob/main/README.md

現在は `cast_event_cal` を正本として、`vrc_cast_event_calender` は検証済みsnapshotを受け取って配信するprojection側に整理されています。

現在の契約では、source commit、snapshot digest、artifactごとのSHA-256、production HTTP確認まで追跡します。

ここで学んだ問題は、データ系では特に重要でした。

```text
収集できた
!=
分類できた
!=
正しいsnapshotができた
!=
deployできた
!=
利用者が正しい内容を見られた
```

「成功」を一語で扱わない。

この考え方は後に、CI successとproduction successを分ける設計、tool successとproduct successを分ける設計へつながります。

## 2025秋：人が実行しなくても回る定期AIパイプラインになった

`daily-arXiv-ai-enhanced` は2025年11月18日にforkとして作成されています。

- repository: https://github.com/KAFKA2306/daily-arXiv-ai-enhanced
- GitHub API: https://api.github.com/repos/KAFKA2306/daily-arXiv-ai-enhanced
- current README: https://github.com/KAFKA2306/daily-arXiv-ai-enhanced/blob/main/README.md

現在のREADMEでは、arXiv公開レコードを定期取得し、LLMで日本語要約を生成し、JSONL / Markdown / 静的Webを作り、GitHub Pagesへ公開する流れが定義されています。

```text
arXivを取得
→ ID / version / author / dateを検証
→ 重複検査
→ LLM要約
→ 原文と生成文を分離保存
→ 静的ページ生成
→ link / content検証
→ Pages公開
```

必要なprovenanceが欠ける成果物は公開しない、というfail-closedの考え方も現在の設計に入っています。

この段階で初めて、かなり明確に

**「人がボタンを押す」のではなく、時間が来れば収集・生成・検証・公開まで進む**

という運用になります。

ただし、まだ自律化の対象は1つのpipelineです。

「今日はどのrepoを改善すべきか」までは決めません。

## 2026夏：自動化の対象が「repoの中」から「repo間」へ出た

2026年7月13日から8月13日までの約1か月で、変化が一段進みました。

ChatGPTとの会話を、個々のrepoに指示を出す場所ではなく、**複数プロジェクトの状態遷移を制御する場所**として使うようになりました。

ここで初めて、過去の各系統が一つに合流します。

```text
2023: appを作る
2024: pipelineを作る
2025: tool / agentを分ける
2025: 定期実行する
2025: provenanceを残す
2026: 複数repoの状態を読む
2026: 次の1件を選ぶ
2026: 完了証拠まで確認して次へ進む
```

最近の件数は、この最後の段階が高速で回った結果です。

## 最初の失敗：repoごとにAIへお願いすると、管理仕事が増える

対象が少ないうちは、次で十分です。

```text
repo Aを直す
repo Bを調べる
repo CにIssueを作る
repo Dをdeployする
```

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

中央管理用の `agent-resources` では、ダッシュボードを一気に作らず、Schema、公開対象設定、collector、lane判定、canonical JSON、UI、QAへ小さく分解しました。

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

## 状態を4つまで減らした

複数repoを横断すると、GitHubの生の状態は多すぎます。

Issueのopen/closed、PRのdraft/open/merged、workflowのqueued/in_progress/completed、conclusionのsuccess/failure/cancelledなどを、そのまま人間へ見せても次の行動は決まりません。

そこで中央ダッシュボードでは、最終的に4つへ圧縮しました。

```text
working  = AIやworkflowが進められる
waiting  = 人間判断・外部依存待ち
done     = 完了条件まで証拠がある
failed   = 失敗または要確認
```

さらに `laneReason` を持たせ、なぜ止まっているかを機械が説明できるようにします。

すると次の巡回で、ChatGPTはチャット履歴を全部思い出す必要がありません。

現在のGitHub状態を読み、`working` の中から次の候補を選び、`waiting` は人間へ返せます。

## 自律化したのは「作業」より「次を決めるループ」だった

現在の制御ループは、だいたい次の形です。

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

ポイントは「AIに好きに作らせる」ことではありません。

**選択肢を広く持たせる一方、Doneの条件を狭くする**ことです。

## 最近の例は「新しい思想」ではなく、古い思想の横展開だった

直近の `Prompt Vault`、`finBI`、`investor2` は重要ですが、記事全体の主役ではありません。

それぞれ、過去から続くパターンの現在形として見る方が分かりやすいです。

### Prompt Vault：manifestとhashをrepo間へ拡張

共有Asset Registryでは、source SHA-256、source commit、destination SHA-256を固定し、consumer側のbuildと公開URLまで確認します。

- Asset Registry: https://github.com/KAFKA2306/prompt-vault/issues/55
- consumer inventory / migration: https://github.com/KAFKA2306/prompt-vault/issues/57
- first consumer `travel`: https://github.com/KAFKA2306/travel/issues/20

これは2024年のpipelineでも使っていた「入力・出力・manifestを分ける」考え方を、repo間へ広げたものです。

### finBI：古いrepoを自動化しやすい状態数へ縮約

2023年からある `finBI` は、2026年に古いStreamlit試作を延命せず、公開Web runtimeを4ファイルまで縮約しました。

- redesign: https://github.com/KAFKA2306/finBI/issues/8
- legacy reduction: https://github.com/KAFKA2306/finBI/issues/6

ここでの原則は、複雑なものをそのままAIへ渡さないことです。

**状態数を減らしてから自動化する。**

### investor2：人間が残る境界を固定

投資研究の `investor2` では、分析から自動売買へ進ませず、判断直前の状態をimmutableなDecision Snapshotとして固定します。

- Decision Snapshot: https://github.com/KAFKA2306/investor2/issues/34
- Hypothesis Lab: https://github.com/KAFKA2306/investor2/issues/35

自律化とは、人間を消すことではありません。

**機械的に判定できる作業を機械へ寄せ、価値判断と不可逆判断を人間へ残すこと**です。

## 「取得できた」と「正しい」を最後まで分ける

AI運用で危険なのは、tool callやCIが成功すると、それを成果物の正しさまで拡大解釈しやすいことです。

`finBI` では、snapshotの `retrieved_at` と、その時点ではまだ利用できなかったFRED観測値が共存するpoint-in-time不整合が実際に見つかりました。

- issue: https://github.com/KAFKA2306/finBI/issues/10
- fix PR: https://github.com/KAFKA2306/finBI/pull/13

このとき必要だったのは、単純な日付比較ではなく、その観測値がsource側でいつ利用可能になったかというavailability / vintageの検証でした。

自律化するほど、次を別物として扱う必要があります。

```text
tool success != product success
CI success != production success
file exists != verified artifact
HTTP 200 != correct content
```

これはVRChatカレンダーのprojection、arXiv pipeline、画像pipeline、現在のPages deployまで一貫して使える原則です。

## ChatGPTのScheduled Tasksも「repoごと」ではなく制御ループに使う

OpenAIの公式ヘルプでは、ChatGPTのScheduled Tasksは定期タスクやmonitoringを扱え、1時間に1回より高い頻度では実行できません。アクティブなタスク数にもプラン別上限があります。

- https://help.openai.com/ja-jp/articles/10291617-scheduled-tasks-in-chatgpt

GitHub連携についても、OpenAI公式は、接続したrepositoryからコード、README、その他のドキュメントを取得し、検索・分析・引用できると説明しています。

- https://help.openai.com/ja-jp/articles/11145903-connecting-github-to-chatgpt

146 repoに対して146個の監視タスクを作る発想ではなく、中央状態を見て次の1件を選ぶ方が、ここまでの歴史とも整合します。

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

## 失敗も高速化するので、細かな事故は「再利用できる契約」へ変える

大量に動かすと、成功だけでなく失敗も高速になります。

実際、誤操作で作られた一時Issueや重複Issueもありました。

- https://github.com/KAFKA2306/rule-scribe-games/issues/83
- https://github.com/KAFKA2306/furutsatotax/issues/13

Pythonのquote破損、環境変数名の誤り、Uploader停止のような局所事故は、それぞれを独立記事にするより、再利用できる契約へ変換する方が価値があります。

```text
quote破損
→ compile gate

環境変数名ミス
→ deploy前contract validation

Uploader事故
→ tool successと実環境completionの分離
```

そのため、細かな候補記事はarchiveへ回し、複数プロジェクトへ再利用できる仕組みが取り出せたものを残します。

- archive policy: https://github.com/KAFKA2306/articles/blob/main/artifacts/archive/README.md

## 3年分を並べると、変わったのはAIの賢さだけではなかった

ここまでを一つの図にすると、こうなります。

```text
2023
single application
    ↓
2024
multi-stage pipeline
    ↓
2025
agent / tool boundary
    ↓
2025
recurring execution + provenance
    ↓
2026
GitHub as shared state
    ↓
2026
portfolio audit + next-action selection
```

最終的な構造は次です。

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

直近1か月の805 PRは目立ちます。

でも、それをこの記事の起点にすると重要なものを見失います。

その前に、1つのアプリを作る時期があり、pipelineを作る時期があり、MCPで役割と権限を分ける時期があり、人が触らなくても定期実行する仕組みがあり、manifestやhashで証拠を残す試行がありました。

2026年夏に新しかったのは、それらを**repoの中だけで使わず、repo間の次の行動を選ぶために使い始めたこと**です。

コード生成は、そのループの一工程にすぎません。

マルチプロジェクト開発を自律化するときに本当に効いたのは、

**状態を減らすこと。契約を書くこと。証拠を残すこと。停止条件を決めること。そして、人間が判断すべき場所を最後まで消さないこと。**

でした。
