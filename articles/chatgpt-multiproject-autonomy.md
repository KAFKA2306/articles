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

実際に一番重くなったのはコードではなかった。

```text
次はどのrepoを見る？
前回どこまで終わった？
PRは残っていない？
CI successはproduction successなのか？
Issueをcloseしてよい？
```

AIへ実装を渡しても、**仕事の選択と完了判定が人間に残る。**

2026年夏に変わったのは、コード生成ではなく、この「次の1件を決める」部分までGitHub上の状態から再開できるようにしたことだった。

![123個の個人開発をGitHubとChatGPTで横断運用する全体像](/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-01.webp)

## まず、規模を固定する

2026年8月13日18:27:30 JSTを上限にGitHub Search APIで固定すると、2026年7月13日以降の活動は次だった。

- Pull Requests: 813
- Merged Pull Requests: 686

一次情報:

- https://api.github.com/search/issues?q=author%3AKAFKA2306+is%3Apr+created%3A2026-07-13..2026-08-13T09%3A27%3A30Z
- https://api.github.com/search/issues?q=author%3AKAFKA2306+is%3Apr+is%3Amerged+merged%3A2026-07-13..2026-08-13T09%3A27%3A30Z

Repository Searchでは、現在のpublic repositoryを次のように分けられる。

```text
146 public repositories
├─ 123 non-fork repositories
└─ 23 forks
```

- https://api.github.com/search/repositories?q=user%3AKAFKA2306+is%3Apublic+fork%3Afalse
- https://api.github.com/search/repositories?q=user%3AKAFKA2306+fork%3Aonly

ここで重要なのは123という数そのものではない。

**互いに無関係なrepoを増やしたとき、会話履歴ではなくrepositoryから現在地を復元できるか**が問題になった。

## 「コードを書けた」はDoneではなかった

具体例として `finBI` では、2026年7月24日20:17 UTC取得と記録されたFRED DGS10 snapshotに、当該時点ではまだ利用可能でなかった `2026-07-24 = 4.69` が入っていた。

Issue #10では、2026年7月24日15:17 CDT時点のFRED表示で最新観測が `2026-07-23 = 4.71` だったことを確認し、単なる観測日比較ではなくsource availability / vintageまで検証する方針へ変えた。

- https://github.com/KAFKA2306/finBI/issues/10
- https://fred.stlouisfed.org/series/DGS10

この例で必要だったのは「AIにもっと詳しく説明すること」ではない。

必要だったのは、

```text
何を変えるか
何を正しいとするか
何で確認するか
どこまで終われば利用者へ返せるか
```

を、その変更に必要な範囲だけ残すことだった。

## GitHubを共通の再開地点にした

複数repoをまたいでも、GitHubには既に共通して読める状態がある。

```text
Issue
  変更要求 + 完了条件

Pull Request
  実装候補 + 差分

GitHub Actions
  機械検証

main
  現在採用されている実装

Pages / production / artifact
  利用者が観測する結果
```

ChatGPTが123 repoを記憶し続ける必要はない。

**必要な事実を既存のsystem of recordから読み、次の1件を再開できればよい。**

公開Dashboardも、public repositoryのIssue / PR / workflowを横断して次に確認すべき対象を見せるための投影として使っている。

- https://kafka2306.github.io/agent-resources/dashboard/

![ChatGPTが次の仕事を選ぶ制御ループ](/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-09.webp)

## ここで一度、設計を間違えた

再開可能性が効いたため、途中から「状態・契約・証拠をもっと外へ出せばよい」と考えやすくなった。

しかし、この発想をそのまま伸ばすと別の問題が起きる。

README、`AGENTS.md`、CLAUDE/GEMINI、ADR、prompt、skill、memory、audit scriptへ同じ判断規則を書けば、再開可能性は上がるように見える。

実際には、次のAIが

```text
どの文書が現在の正準か
同じruleがなぜ複数あるか
どのvalidatorを信じるか
このfallbackはまだ必要か
どのstateが最新か
```

を判断する仕事が増える。

**外部化にも限界費用がある。**

## `AGENTS.md` は「置いてあるだけ」ではない

OpenAIの2026年1月23日のCodex解説では、`AGENTS.md` / `AGENTS.override.md` 等のproject instructionsはGit rootから現在ディレクトリまで探索され、user instructionsとしてpromptへ集約される。project docsは既定で32 KiBまで取り込まれる。

- https://openai.com/index/unrolling-the-codex-agent-loop/
- https://developers.openai.com/codex/agent-configuration/agents-md

つまりAI向けinstructionをrepositoryへ追加することは、単なるdocumentation追加ではない。

次の実行で読むcontextそのものを増やす。

GoogleのCode Review Guideも、現在必要以上の一般化や、将来必要かもしれない機能の先回りをover-engineeringとして警戒している。

- https://google.github.io/eng-practices/review/reviewer/looking-for.html
- https://google.github.io/eng-practices/review/reviewer/standard.html

この原則はAI向けのrule、role、state、score、protocol、verificationにもそのまま適用できる。

## 最小形は「新しいagent framework」ではなかった

123 repoを再開可能にするために、各repoへ独自の状態機械や方法論を持たせる必要はない。

まず既存のGitHub機能で足りるかを見る。

```text
1. Issue
   何を変えるか + Done条件

2. 機械検証
   必要なtest / lint / build / CI

3. 利用者側の確認
   production / Pages / API / artifact

4. 人間へ返す境界
   公開 / 売買 / 削除 / creative choice
```

これで再開できるなら、それ以上の永続contextを作らない。

独自のmanifest、ledger、status、receipt、verification layerを追加するのは、既存の4つでは表現できない事実が実際に存在するときだけでよい。

## 新しい基準は「消したら何が壊れるか」

複数repo運用で本当に必要なのは、情報量を最大化することではなかった。

必要な証拠だけを、次の実装者が一意に辿れることだった。

そこで今は、追加より先に次を問う。

> **このfile / rule / test / workflow / fallback / stateを消したら、利用者価値・正しさ・必要な証拠のどれが失われるのか？**

何も失われないなら、再開可能性を高める情報ではなく、次の判断を増やす残骸かもしれない。

これはtestを減らせばよい、documentationを短くすればよい、という話ではない。

金融データのschema、外部API契約、安全上必要なvalidationのように、実装の意味を直接決める情報は残す必要がある。

削る対象は、**同じ成果を作るために重複した判断経路**だ。

## 人間を消したわけではない

自律化の境界も変わらない。

```text
機械的に証明できるもの
→ 機械へ

意味・価値・不可逆性を含むもの
→ 人間へ
```

![機械へ渡す仕事と人間へ残す判断の境界](/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-10.webp)

売買、公開、削除、creative choiceのような不可逆・価値判断は人間へ残す。

自律化したいのは人間そのものではなく、毎回同じ現在地を探す作業である。

## 結論：AIに渡すべきなのは「次の1件」だけでよかった

123個の個人開発を一つの巨大なagent systemへ作り直す必要はなかった。

必要だったのは、各repoについて

```text
今何が未完了か
何を満たせば終わるか
その証拠はどこか
次に誰が動けるか
```

を既存の状態から読めることだった。

そして、そこから先は増やしすぎない。

**忘れても再開できる。しかし、再開するために新しい概念を覚え直さなくてよいrepo。**

123個まで増えて分かったのは、その両方が必要だということだった。
