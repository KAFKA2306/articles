# Short-context Issue Contract

GitHub Issueは、過去チャット・長いmemory・別Issue本文を読まなくても、そのIssue単体から着手できるようにする。

## 必須の先頭ブロック

各実行Issueの本文先頭に `## Short-context handoff` を置き、次だけを短く書く。

- **Goal** — このIssueで得る観測可能な最終状態を1〜2文で書く。
- **Read first** — 最初に読む正準file / URL / Issueを最大3件まで列挙する。
- **Change only** — 主な変更対象file / surfaceを限定する。
- **Start here** — 最初の3手以内を具体的に書く。
- **Do not** — このIssueでやらないこと、特に隣接Issueの責務を明示する。
- **Done when** — 完了を判定できる検証・CI・公開receiptを列挙する。

詳細な背景、調査記録、候補、過去経緯はこのブロックの後ろに置く。短いcontextのagentは、まず先頭ブロックだけで作業を開始し、必要になった情報だけ下へ読む。

## 自己完結性

Issue本文にない過去会話を前提にしない。`前に話した通り`、`いつもの方針`、`既知の問題` のような参照は禁止する。必要な制約は本文に再掲するか、正準fileへの直接linkを置く。

親Issueは全実装を抱えない。子Issueがある場合、親Issueは順序・共通gate・portfolio decisionだけを持ち、実装agentには一つの子Issueだけを渡せる状態にする。

## Scope size

一つのIssueは、一つのagentが一つのworkline / PRで完了できる責務を原則とする。次の場合は分割する。

- 複数の独立した最終状態がある。
- 異なるproduction surfaceを同時に変更する。
- 一方を完了しなくても他方を独立してmergeできる。
- acceptance criteriaが別々のverifierを持ち、依存関係がない。

逆に、同じinvariantを成立させるために不可分なcode + testは同じIssueに保つ。

## Evidence discipline

Issueの説明はground truthではない。agentは着手時にcurrent `main`、関連PR、実装file、現在の外部stateを再確認する。Issueとcurrent stateが衝突した場合はcurrent stateを優先し、Issueを更新してから実装する。

完了報告には最低限、変更file、検証command、exact-head CIまたは同等のreceipt、残blockerを残す。`CI green` だけでproduction完了を主張しない。

## Article Issue追加条件

記事Issueは `Goal / Read first / Change only / Start here / Do not / Done when` に加えて、次を本文内に持つ。

- `generalizable_insight`
- `transfer_conditions`
- `non_transfer_conditions`
- first-hand proofとして使う具体的fixture
- readerが持ち帰るdecision rule / checklist / experiment protocol

固有repo・tool・productは証拠に使ってよいが、それ自体を記事成果にしない。
