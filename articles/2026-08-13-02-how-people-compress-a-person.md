---
title: "スキル一覧では『何を任せられる人か』は分からない。成果物を仕事の証拠に変える"
emoji: "🪞"
type: "idea"
topics: ["career", "portfolio", "github", "ai"]
published: false
published_at: 2026-08-13 18:11
---

GitHubには、技術スタック、草の数、リポジトリ数、スター数、コミット履歴が並ぶ。

職務経歴書には、Python、TypeScript、React、AWS、生成AIといったスキルが並ぶ。

どれも情報ではある。

しかし、仕事を頼む側が本当に知りたいことには、まだ答えていない。

> **この人に、どんな問題を渡すと、どんな状態まで持っていけるのか。**

これは採用だけの話ではない。

社内異動、業務委託、共同研究、個人開発、OSS、AI時代の専門家評価まで、同じ問題がある。

人を評価するとき、属性や活動量だけでは「実際に何を任せられるか」が分かりにくい。

そこで有効なのが、成果物を単なる作品ではなく **work sample（仕事のサンプル）** として見せる考え方である。

米国人事管理庁（U.S. Office of Personnel Management）は、work sampleについて、実際の職務を代表するタスクを行わせるため内容的妥当性が高く、その成績と実際の職務成績にも強い関係があると説明している。

https://www.opm.gov/policy-data-oversight/assessment-and-selection/other-assessment-methods/work-samples-and-simulations/

つまり、

```text
Pythonができます
AIを使えます
GitHubを毎日更新しています
```

よりも、

```text
この問題を受け取った
↓
この条件を成功と定義した
↓
この方法で実装した
↓
この失敗条件を検証した
↓
この状態まで運用可能にした
```

の方が、仕事の能力に近い情報を伝えやすい。

## 成果物が伝わらない最大の理由は「作った本人の言葉」で説明しているから

技術者のポートフォリオが分かりにくくなる典型例がある。

```text
独自のcanonical schemaを設計した
provenance layerを追加した
agent runnerへsandbox boundaryを実装した
```

技術的には正しい。

しかし初見の人は、まず用語を理解しなければ価値へ到達できない。

GoogleのTechnical Writing教材は、専門家が初心者の知らない前提を忘れてしまう *curse of knowledge* に注意するよう説明している。

https://developers.google.com/tech-writing/one/audience

したがって、成果物は内部実装から説明するのではなく、**読者が既に理解できる問題から説明する**方がよい。

たとえば次のように変える。

```text
canonical schemaを設計した
```

ではなく、

```text
同じ顧客が3つのExcelで別名になっており、どれが正しいか決められなかった。
そこで、1つの正準データと変換規則を決めた。
```

と書く。

あるいは、

```text
agent runnerへsandbox boundaryを実装した
```

ではなく、

```text
AIにPC作業を任せたいが、関係ないフォルダまで書き換えられる状態では運用できない。
そこで、通常は読み取り専用にし、必要な範囲だけ書き込みを許可した。
```

と書く。

専門用語を削ることが目的ではない。

**専門用語より先に、何の問題を解いたのかを見せる**ことが重要である。

## 例1：データ移行なら「何件取り込めたか」より「壊す前に止まれるか」

CSVやExcelから新しいシステムへデータを移す仕事を考える。

一見すると成果は単純である。

> 1万件を移行した。

しかし、実際に任せる側が気にするのは件数だけではない。

- 既存データとの重複はどう扱ったか
- 不正なIDや欠損値はどう扱ったか
- 曖昧な行を勝手に登録していないか
- 本番を書き換える前に結果を確認できるか
- 失敗したとき元へ戻せるか

したがって、仕事の証拠として強いのは、

```text
1万件をimportした
```

ではなく、

```text
実行前にdry-runを行い、
重複・不正値・人間確認が必要な行を分離し、
確認後にだけ本番へ書き込めるようにした
```

という成果である。

ここで示されている能力は「CSVを読める」ではない。

**破壊的な処理を、事前に判断できる処理へ変える能力**である。

この説明なら、対象が本棚でも顧客DBでも会計データでも通用する。

## 例2：数字を出す仕事なら「値」より「なぜその値を信じてよいか」

分析やダッシュボードでは、数字を出せたこと自体が成果になりやすい。

しかし同じKPIが、先月は856、今月は7,699になったとする。

利用者が知りたいのは、計算コードの美しさではない。

> なぜ変わったのか。どちらを信じればよいのか。

このとき成果物に必要なのは、値だけではない。

```text
value
source
scope
method
observed_at
status
```

のように、**どこから来て、何を対象に、どう計算した値なのか**を残す必要がある。

W3CのPROV仕様も、provenanceを、データや成果物を生成した entity・activity・agent の関係としてモデル化している。

https://www.w3.org/groups/wg/prov/publications/

W3Cはさらに、provenance情報が品質・信頼性・trustworthinessを評価するために利用できると説明している。

この考え方はデータ分析だけに限らない。

- MLモデルの学習データ
- 生成AIの回答ソース
- レポートの集計値
- 研究結果
- ソフトウェアのbuild artifact

でも同じである。

GitHubもartifact attestationsについて、software artifactが「どこで、どのようにbuildされたか」をprovenanceとして確立する仕組みを提供している。

https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations

成果として重要なのは、**数字を出せたことではなく、数字が変わっても説明できる状態を残したこと**になる。

## 例3：AIを導入するなら「何ができるか」より「どこまで任せてよいか」

生成AIやagentのデモでは、できることの多さが目立ちやすい。

```text
ファイルを読める
コードを書ける
ブラウザを操作できる
GitHubへcommitできる
```

しかし実運用では、能力が高いほど別の問いが重要になる。

> **どこまで触ってよいのか。**

NISTはleast privilegeを、ユーザーやプロセスに、割り当てられた仕事を行うために必要な最小限の権限だけを与える原則として定義している。

https://csrc.nist.gov/glossary/term/least_privilege

この原則から考えると、AI agentの成果を

```text
PCを自動操作できた
```

だけで説明するのは弱い。

むしろ、

```text
通常はread-only
対象directoryを限定
必要なtaskだけwriteを許可
外部toolはallowlist方式
実行成功ではなく最終結果まで検証
```

のように、**委任できる境界まで設計したこと**が仕事の証拠になる。

GitHub Actionsでも、GitHubはworkflowのcredentialについてleast privilegeを推奨し、`GITHUB_TOKEN` の権限を必要最小限に制限するよう案内している。

https://docs.github.com/en/actions/reference/security/secure-use

AI時代には「何でもできるagent」より、**何を安全に任せられるagentか説明できること**の方が、運用上の価値を持ちやすい。

## 良い成果物は「完成品」ではなく、判断可能な証拠を持っている

ここまでの3例には共通点がある。

成果物そのものより、その周囲に判断材料が残っている。

最低限、次の6つがあると仕事の証拠として読みやすい。

### 1. Problem — 何が困っていたか

内部用語ではなく、利用者の言葉で書く。

```text
悪い例：migration diagnosis moduleを実装
良い例：大量データを本番へ書く前に、重複や不正値を確認できなかった
```

### 2. Success — 何を成功としたか

「実装した」だけでは完成条件が分からない。

```text
処理が終了する
```

ではなく、

```text
不正データを本番へ書き込まず、問題のある行を人間が特定できる
```

まで書く。

### 3. Boundary — 何をしないと決めたか

良い設計は、できることだけでなく、しないことも明確である。

```text
不明な値を推測しない
partial dataをcompleteとして公開しない
AIへ不要なwrite権限を与えない
```

といった境界は、実運用では重要な成果になる。

### 4. Artifact — 何を残したか

コード、Web UI、データセット、schema、API、CI、dashboardなど。

ここで初めて技術スタックを書く。

### 5. Verification — どう確かめたか

```text
unit test
fixture
CI
E2E
source URL
hash
production check
```

など、第三者が確認できる証拠を置く。

### 6. Reuse — 次に何が安くなったか

一度動いただけのscriptより、次回以降も使える仕組みの方が組織的価値は大きい。

```text
手作業だった確認が自動化された
別データにも同じvalidatorを使える
次のagentにも同じpermission modelを適用できる
```

という再利用可能性まで示せると、成果の価値が分かりやすい。

## GitHubで見るべきなのは「量」ではなく変換能力

GitHubには活動量を可視化する仕組みがある。

GitHub公式ドキュメントでも、プロフィールにはrepository、contribution、skills、projectsなどを表示・紹介できる。

https://docs.github.com/en/get-started/start-your-journey/setting-up-your-profile

https://docs.github.com/en/account-and-profile/tutorials/using-your-github-profile-to-enhance-your-resume

ただし、repo数やcommit数は、それだけでは仕事の質を説明しない。

100個のrepositoryがあっても、第三者が

```text
何が問題だったのか
何を判断したのか
どこまで完成したのか
どう検証したのか
```

を読み取れなければ、依頼判断には使いにくい。

逆に、小さなrepositoryでも、

```text
Before
↓
Decision
↓
Implementation
↓
Verification
↓
Operational state
```

が見えれば、何を任せられる人かを判断しやすい。

## ポートフォリオは「作品一覧」から「委任判断の資料」へ変えられる

READMEや職務経歴書を書くとき、次のテンプレートを使うと説明を一般化しやすい。

```markdown
## Problem
誰が、何に困っていたか

## Risk / Constraint
失敗すると何が起きるか
何をしてはいけないか

## Decision
どの状態を正しいと定義したか

## Implementation
何を作ったか

## Verification
何で確認したか

## Outcome
利用者が何をできるようになったか

## Reuse
次回以降、何が不要・高速・安全になったか
```

この順番なら、技術に詳しくない読者も先に価値を理解できる。

GoogleのTechnical Writing教材も、読者が既に知っていることと、タスクを行うために必要なこととの差を埋めるよう文書を設計することを勧めている。

https://developers.google.com/tech-writing/one/audience

## 「何ができる人か」は、肩書きより変換で表現できる

人を一言で説明しようとすると、

```text
AIエンジニア
データサイエンティスト
フルスタック
自動化が得意
```

のようなラベルになりやすい。

ラベルは入口として便利だが、実際の仕事はもっと具体的である。

たとえば、

```text
曖昧な要求
↓
一次情報を確認
↓
正しい状態を定義
↓
実装
↓
失敗条件を検証
↓
運用可能な成果物
↓
後から確認できる証拠
```

という変換を繰り返せる人なら、domainが変わっても同じ能力を使える。

だから、ポートフォリオで示すべき中心は「使える技術の数」ではない。

> **どんな問題を、どんな判断を経て、どんな状態へ変え、その結果をどう確かめられるようにしたか。**

成果物をこの形で残せば、GitHubは単なる活動履歴ではなくなる。

**第三者が「この仕事を任せられるか」を判断するための証拠になる。**
