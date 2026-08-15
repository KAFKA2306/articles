---
title: "個人開発が123個になって分かった。ChatGPTに任せるべきはコードより「次の1件」だった"
emoji: "🛰️"
type: "tech"
topics: ["chatgpt", "github", "automation", "githubactions"]
published: true
published_at: 2026-08-15 09:40
---

1か月で813件のPull Requestを作り、686件をmergeした。

この数字だけを見ると、「AIでコードを書く速度が上がった話」に見える。

でも、実際に一番重くなったのはコードを書く工程ではなかった。

GitHubには公開リポジトリが146個ある。そのうちforkを除く123個が自作側だ。金融、VRChat、ゲーム、動画、家計、旅行、3D、データ収集、AI agent。分野はほとんど共通していない。

プロジェクトが増えるほど、人間には別の仕事が増えた。

```text
次はどのrepoを見る？
前回どこまで終わった？
PRは残っていない？
CI successはproduction successなのか？
Issueをcloseしてよい？
```

AIへ実装を渡しても、**仕事の選択と完了判定が人間に残る。**

2026年夏に変わったのは、コード生成の量ではなく、この「次を決めるループ」までChatGPTを介して扱うようになったことだった。

**なぜ、もともと無関係だった123個の個人開発を、一つの制御ループで扱えるようになったのか。**

この記事で追うのは、その理由だ。

なお、813 PRという件数自体は品質の証明ではない。

![123個の個人開発をGitHubとChatGPTで横断運用する全体像](/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-01.webp)

## まず、規模を固定する

2026年8月13日18:27:30 JST時点でGitHub Search APIを取得すると、2026年7月13日から同時刻までの活動は次の規模だった。

- Issues: 387
- Pull Requests: 813
- Merged Pull Requests: 686

一次情報:

- Profile: https://api.github.com/users/KAFKA2306
- Issues: https://api.github.com/search/issues?q=author%3AKAFKA2306+is%3Aissue+created%3A2026-07-13..2026-08-13T09%3A27%3A30Z
- Pull Requests: https://api.github.com/search/issues?q=author%3AKAFKA2306+is%3Apr+created%3A2026-07-13..2026-08-13T09%3A27%3A30Z
- Merged Pull Requests: https://api.github.com/search/issues?q=author%3AKAFKA2306+is%3Apr+is%3Amerged+merged%3A2026-07-13..2026-08-13T09%3A27%3A30Z

検索結果が後から増えないよう、上限時刻を固定している。

Repository Searchでは、同日時点の146 public repositoriesを次のように分けた。

```text
146 public repositories
├─ 123 non-fork repositories
└─ 23 forks
```

- non-fork: https://api.github.com/search/repositories?q=user%3AKAFKA2306+is%3Apublic+fork%3Afalse
- forks: https://api.github.com/search/repositories?q=user%3AKAFKA2306+fork%3Aonly

以下では、123個すべてが同じ成熟度だとは扱わない。具体的な主張は、実装・Issue・Actionsなどを確認できた代表例に限定する。

## 813 PRの中で、実際に何が変わったのか

### 1. 公開前に「未来の金利データ」を弾いた

`finBI` では、`retrieved_at = 2026-07-24T20:17:00Z` のsnapshotに `2026-07-24 = 4.69` が入っていた。

しかし当時利用可能だった最新観測は `2026-07-23 = 4.71` で、7月24日の値は後の更新で現れていた。

値そのものが正しくても、**その時点では知り得なかった値**が混ざればバックテストや判断を汚す。

そこでsource availability / vintage timestampまで検証するfail-close契約へ変えた。

- https://github.com/KAFKA2306/finBI/issues/10
- https://fred.stlouisfed.org/series/DGS10
- https://alfred.stlouisfed.org/release?rid=18

### 2. 320pxに潰れたWebアプリをproductionまで直した

`rule-scribe-games` では、desktopのゲーム詳細ページが左約320pxへ押し込まれていた。

原因はCSSの数値ではなく、`body` とReact `#root` のlayout ownershipの不一致だった。

`#root` へgrid ownershipを移し、Playwright回帰を追加し、Vercel Preview / Productionと公開URLまで確認して完了にした。

- https://github.com/KAFKA2306/rule-scribe-games/issues/76

### 3. repo間assetを、公開後のhash一致まで確認した

`prompt-vault` から `travel` へ共有assetを配るときは、source commitとSHA-256を固定した。

consumer側へ反映した後、Pagesの公開URLから再取得し、`sha256sum -c` が `OK` になるところまでをDone条件にした。

- https://github.com/KAFKA2306/travel/issues/20

### 4. private data planeへのpublish後、全objectを検証した

`semiconductor-earnings-model` では、GitHubをcontrol plane、private storageをdata planeとして分離している。

2026年8月13日のscheduled Actions runでは、OIDC認証、allow-list prefixのmirror、publish後のevery object verificationまで成功した。

- https://github.com/KAFKA2306/semiconductor-earnings-model/actions/runs/31680400569

4例の成功条件はまったく違う。

共通していたのは、**「コードを書けた」で終わらず、何をもってDoneとするかが外へ出ていたこと**だった。

## 違う分野が、同じ構造へ収束した

分野ごとの必要条件を一段抽象化すると、次のようになった。

| 分野 | 必要になった契約 |
| --- | --- |
| 金融 | provenance / point-in-time / evidence |
| VR・3D | identity / source immutability / artifact validation |
| ゲーム・Web | reproducible build / smoke / regression |
| 情報・出版 | canonical source / projection / publication boundary |
| 個人データ | privacy / local-only / redaction |
| agent・MCP | tool boundary / least privilege / approval |

![異なる分野が状態・契約・証拠へ収束する図](/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-07.webp)

分野は違っても、最終的には次の5つを外へ出す必要があった。

```text
今どういう状態か
何を成功とするか
何を根拠にしたか
何を機械がしてよいか
何を人間へ返すか
```

**異なるrepoが同じ技術スタックへ揃ったのではない。状態・契約・証拠を機械が読める形へ揃った。**

ここが、後から全部をつなげられた理由だった。

## GitHubが共通状態になった

複数repoをまたいでも、GitHub上には共通して読めるものがある。

```text
Issue
  = 変更要求 + Acceptance Criteria

Pull Request
  = 実装候補 + 差分

GitHub Actions
  = 機械検証

main
  = repositoryの正準状態

Pages / production
  = 利用者が観測する成果物
```

大事なのは、ChatGPTが123個の中身を全部記憶することではない。

**各repoが現在の真実を外へ出し、ChatGPTはその時点の状態を読む。**

これなら、会話履歴の長さに依存しない。

## 状態を4つへ圧縮すると「次」が選べる

生のGitHub状態は細かい。

そこで横断側では、行動につながる4状態へ圧縮した。

```text
working  = 機械が次へ進められる
waiting  = 人間判断または外部依存待ち
done     = 完了証拠がある
failed   = 失敗または再確認が必要
```

![working waiting done failedの4つの横断状態](/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-08.webp)

この圧縮は公開Dashboardで確認できる。

- https://kafka2306.github.io/agent-resources/dashboard/

Dashboardではpublic repositoryのIssue / PR / workflowを横断してwork laneへ投影している。GitHub Pages版はsnapshotで、最新性を保証できない場合は `SNAPSHOT FALLBACK` / `STALE` と区別する。

重要なのは瞬間的な件数ではなく、**異なるrepoの状態を、次の行動を選べる少数の状態へ圧縮した実物が公開されていること**だ。

## 自律化したのは「作業」より「次を決めるループ」だった

現在の制御ループは、概ねこうなる。

```text
全体状態を見る
↓
次に進められる候補を選ぶ
↓
Issueの完了条件を読む
↓
実装する
↓
テスト / CIを確認する
↓
PR / merge
↓
productionを確認する
↓
状態を更新して次へ
```

![ChatGPTが次の仕事を選ぶ制御ループ](/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-09.webp)

以前から各repoの中では、取得・計算・生成・検証・公開を自動化していた。

2026年夏に加わったのは、**その外側で「どのrepoの何を次に進めるか」を扱うループ**だった。

ここまで来ると、コード生成は一工程にすぎない。

## 「ChatGPTに任せた」の境界

何も設定していない標準チャットが、123 repoを勝手に巡回して優先順位やDone条件を発明する、という意味ではない。

GitHub側へIssue、PR、Actions、main、production、証拠、権限境界を出し、接続したChatGPT / Codex側が現在状態から次の1件を扱う。

**AIへ渡したのは、全部を覚える役割ではなく、外部化された状態と契約から仕事を再開する役割だった。**

モデルが変わっても、会話が切れても、repo側の契約が残っていれば再開できる。

## 人間を消したわけではない

自律化の境界は単純だった。

```text
機械的に証明できるもの
→ 機械へ

意味・価値・不可逆性を含むもの
→ 人間へ
```

![機械へ渡す仕事と人間へ残す判断の境界](/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-10.webp)

売買判断、公開判断、削除、creative choiceのような不可逆・価値判断は人間へ残す。

**自律化とは、人間を消すことではなく、人間が毎回やらなくてよい調整仕事を状態と契約へ移すことだった。**

## 123個なくても、最小形は4つで始められる

この設計は、5個や10個のrepoでも使える。

最低限必要なのは4つだけだ。

```text
1. Issue
   何を変えるか + Done条件

2. 機械検証
   test / lint / build / CI

3. 利用者側の確認
   production / Pages / API / artifact

4. 人間へ返す境界
   公開 / 売買 / 削除 / creative choice
```

これが揃えば、AIが前の会話を覚えているかより、**repoを読めば現在地が分かるか**の方が重要になる。

巨大なagent frameworkより先に必要だったのは、この「再開可能性」だった。

## 結論：123個を一つにしたのは、AIではなく「読める状態」だった

123個の個人開発は、最初から一つのシステムとして作ったものではない。

それでも、それぞれが

```text
状態
契約
証拠
権限境界
停止条件
```

を外へ出すようになると、GitHubを共通状態として横断できるようになった。

```text
repoが状態・契約・証拠を出す
        ↓
GitHubを共通状態として読む
        ↓
ChatGPTが次の1件を選ぶ
        ↓
実装・検証・公開
        ↓
状態を更新して次へ
```

個人開発が増えすぎたとき、必要だったのは全部を覚えてくれる巨大なAIではなかった。

**忘れても再開できるrepoだった。**

そして123個まで増えて、ようやく分かった。

**AIに渡すべきだったのは、プロジェクトそのものではない。「次の1件を迷わず再開できる状態」だった。**