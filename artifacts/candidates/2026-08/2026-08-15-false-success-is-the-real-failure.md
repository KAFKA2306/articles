---
title: "AI開発で一番危険なのはエラーではない。「正常終了」だ"
emoji: "🚦"
type: "tech"
topics: ["ai", "githubactions", "testing", "automation", "devops"]
published: false
---

2026年1月、私は「AIを過保護にするな」と書いた。

例外を安易に握りつぶさず、失敗したら落とす。スタックトレースを、AIと人間が共有できる客観的な証拠として扱う。名前を **Crash-Driven Development** とした。

元の記事:
https://zenn.dev/kafka2306/articles/11cd731eebded1

8月まで実際の個人開発をAI agentへ渡し続けて、考えは少し変わった。

クラッシュは、確かに役に立つ。

しかし、自律化が進むほど本当に怖かったのは赤いエラーではなかった。

**緑色の成功だった。**

テストが走っていないのにgreen。

正しい処理は終わったのに、その後の別テストで落ちて「本体失敗」に見える。

CIは通ったのに、検証したcommitと公開されたartifactが違う。

外部公開まで完了したように見えるのに、remote identityを確認していない。

この状態では、AIが何十回自動実行できても、人間は最後に毎回こう聞くことになる。

> 本当に終わった？

この確認が残る限り、コード生成は自動化できても、**仕事そのものは委譲できない。**

今回の記事で更新したいのは、以前のCDDを捨てることではない。

その続きを定義することだ。

> **Fail Fastだけでは足りない。Successも疑え。**

公開GitHubで実際に起きた4つの事例から、なぜそう考えるようになったかを書く。

## Case 1: CIがgreenでも、テストが失敗していた

`KAFKA2306/yt3` のCIには、こんな行が残っていた。

```bash
bun test || echo "No tests found"
```

見た目は親切だ。

テストがないrepoでもCIを止めない。

しかし、`bun test` が本当の不具合でexit 1になっても、その後の `echo` が成功すればworkflowは前へ進める。

つまり、**failureをsuccessへ変換する経路**が存在していた。

2026年8月のPRでは、このfallbackを削除した。

同時に、publish routingとno-fallback policyのauditをCIへ入れ、`runs/*` から「最新っぽいrun」を推測する処理も削った。

- PR: https://github.com/KAFKA2306/yt3/pull/10
- exact PR-head CI: https://github.com/KAFKA2306/yt3/actions/runs/31811558191

ここで得られた価値は、「CIが厳しくなった」ことではない。

**greenの意味を狭くしたこと**だ。

```text
before
  command failed
  ↓
  fallback succeeded
  ↓
  green

now
  command failed
  ↓
  red
  ↓
  evidenceを見て直す
```

AI agentにとって、赤は扱いやすい。

失敗したjob、step、exit codeを見れば次の行動を絞れる。

厄介なのは、失敗を成功へ丸めた後だ。そこから先は、AIも人間も「何が本当だったか」を再構築しなければならない。

昔のCDDでは「例外を隠すな」と考えた。

今なら、もう少し広く言う。

**意味のある失敗を、意味のない成功へ変換するな。**

## Case 2: クラッシュした。でも、エラーメッセージの粒度が粗すぎた

逆の問題も起きた。

`KAFKA2306/books` の定期処理では、NDL/NDCを使ったcategory enrichment自体は完走していた。

ところがworkflow全体は失敗した。

原因は分類ロジックではない。

後段のrepository checkが、READMEに次のMarkdown見出しがあることを固定文字列で要求していた。

```text
### Work
### Edition
### Holding
```

READMEのUXを改善し、同じ概念を文章として説明するように変えた結果、**意味は保たれているのに見出し階層が変わっただけで失敗**した。

修正は1 test fileだけだった。

- PR: https://github.com/KAFKA2306/books/pull/73
- exact PR-head workflow: https://github.com/KAFKA2306/books/actions/runs/31849343391

この事例は、CDDの次の弱点を教えてくれた。

クラッシュさえすれば十分ではない。

```text
category enrichment failed
```

としか見えないなら、agentは分類処理を疑う。

実際には、

```text
category enrichment: completed
repository semantic contract: failed
failed_step: README contract test
```

と分かれていた方が、はるかに次の一手が安い。

**失敗を見せるだけではなく、どの境界で失敗したかを保存する。**

ここまで来ると、stack traceは「聖典」というより、evidenceの一部になる。

## Case 3: 厳しいgateを入れたら、古い負債が大量に見つかった

では、全部厳格にすればよいのか。

`KAFKA2306/investor2` で2026年のquality stackを実際に当てたところ、最初のauditで既存負債が一気に出た。

- formatter対象: 40 Python files
- Ruff: 96 errors
- Pyrefly strict: 73 errors
- Oxlint: 11 warnings

ここでrepository全体を一括修正すると、quality tool導入PRが巨大なformat/refactor PRになる。

それでは、何を直したことで何が良くなったのかが分からなくなる。

そこで採ったのは、全面改修ではなく **ratchet** だった。

- changed / maintained filesには新しいformat・lint debtを許さない
- TypeScriptのstrict type checkはrepository全体で維持
- Pyreflyの既存errorはbaselineとして固定し、新規errorだけblock
- 重複した`package-lock.json`は削除し、Bunを1つのlock authorityにする
- 未使用でlock生成を壊していたroot `vllm` dependencyを削除
- Nx / Turborepoは入れない

- PR: https://github.com/KAFKA2306/investor2/pull/96
- Quality Gates: https://github.com/KAFKA2306/investor2/actions/runs/31823096871

新しいcombined Quality Gatesは18秒で完走した。ただし、同等の旧workflowが存在しなかったため、「何倍高速化した」とは言っていない。

この設計で重要だったのはtool名ではない。

**失敗の予算を「過去の全負債」ではなく「今から増やした負債」へ変えたこと**だ。

ユーザーから見ると、これは大きい。

新しい品質基準を入れたいのに、最初に数百箇所の掃除を要求される仕組みは導入されない。

一方で「既存が汚いから何でも許す」なら品質は上がらない。

ratchetにすると、今日の仕事は今日の品質基準を満たしながら、古い負債は別の可視化されたbacklogとして残せる。

自律agentに必要なのは、最強のgateではない。

**次の1変更を安全に前へ進められるgate**だ。

## Case 4: CIが通っても、ユーザーが見るものはまだ未検証だった

最後に、もっと重要な境界がある。

CIはユーザー体験ではない。

`KAFKA2306/semiconductor-earnings-model` のGitHub Pagesでは、sourceをbuildしてartifactを作り、Pagesへdeployする。

2026年8月の更新では、現在のGitHub公式custom workflowに合わせて、

```text
configure-pages
  ↓
upload-pages-artifact
  ↓
deploy-pages
```

へ揃えた。

- PR: https://github.com/KAFKA2306/semiconductor-earnings-model/pull/116
- GitHub Pages公式: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

しかし、ここでも「deploy step success」だけでは終わらせない。

merge後のmain SHAを持ったworkflowが本当に成功したかを確認する。

- merge SHA: `4d2ab0e9fc3e489c380c3c5706c3b43a336f3516`
- exact SHA上のworkflow: https://github.com/KAFKA2306/semiconductor-earnings-model/actions/runs/31832401572

GitHub Actionsにはもう一つ罠がある。

`pull_request` eventの`GITHUB_SHA`は、状況によってPR headそのものではなくsynthetic merge commitを指す。GitHub公式も、head branch commitが必要なら`github.event.pull_request.head.sha`を使うよう説明している。

https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows

つまり、

```text
CI: green
```

だけでは情報が足りない。

最低でも、

```text
what was tested?
which SHA?
what was deployed?
which remote object / page is live?
```

まで閉じなければ、ユーザーが見ているものと検証対象が一致したとは言えない。

## CDD 2026: 「失敗を派手に」から「成功を証明可能に」へ

1月の記事では、中心ループをこう考えていた。

```text
run
↓
crash
↓
stack trace
↓
root cause
↓
fix
```

今はこう考えている。

```text
OBSERVE
  ↓
FAIL CLOSED
  ↓
FIX THE ROOT CAUSE
  ↓
VERIFY THE EXACT REVISION
  ↓
APPLY THE SIDE EFFECT
  ↓
READ BACK REMOTE STATE
  ↓
MATCH IDENTITY / PROVENANCE
  ↓
VERIFIED
```

重要なのは、最後の`VERIFIED`だ。

`exit 0`とは別のstateにする。

```yaml
execution: success
validation: success
side_effect: applied
remote_readback: success
identity_match: true
allowed_to_advance: true
```

どこか1つが未知なら、

```yaml
allowed_to_advance: false
```

にする。

**UNVERIFIEDをPASSへ丸めない。**

これが、現在のCDDで一番大きく変わった点だ。

## これは「try/catch禁止」の話ではなくなった

昔の記事では、例外処理をかなり強く敵視した。

今は、その言い方は広すぎると思っている。

ネットワークretry、transaction rollback、user-facing error conversion、resource cleanupのように、boundaryで例外を扱う合理的な理由はいくらでもある。

問題はcatchの存在ではない。

**catchした結果、失敗の意味・identity・provenanceが失われること**だ。

例えば、

```python
try:
    publish()
except Exception:
    return {"status": "ok"}
```

は危険だ。

一方で、

```python
try:
    publish()
except TemporaryNetworkError as exc:
    raise RetryablePublishFailure(run_id=run_id) from exc
```

のように、失敗の意味を狭め、上位層がretry policyを判断できるなら、evidenceは保たれる。

だから現在の原則は、

> catchするな

ではなく、

> **意味を失うならcatchするな。回復するなら証拠を残せ。**

である。

## ユーザー価値は「コードを書かなくていい」ではない

AI codingの価値は、コード入力時間を短くすることだと思われがちだ。

実際に複数repoを運用すると、別のコストが支配的になる。

```text
本当にtestした？
そのPRのHEAD？
古いrunを見ていない？
公開先は合っている？
remoteに反映された？
Issueをcloseしてよい？
もう一度全部rerunすべき？
```

この確認を毎回人間がするなら、AIは高速な実装者ではあっても、自律operatorにはならない。

逆に、success proofがmachine-readableなら、人間の仕事を次へ寄せられる。

```text
machine
  implementation
  deterministic check
  exact-head CI
  failed-step isolation
  deploy / write
  read-back
  identity verification

human
  product intent
  trade-off
  ambiguous evidence
  irreversible/high-stakes approval
```

GitHub自身もfailed jobsだけをrerunする仕組みを提供している。

https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs

全部を毎回最初からやり直すのではなく、**失敗した境界だけを狭く再実行する**方が、証拠も原因も保ちやすい。

ここに、自律化の実際の価値がある。

「AIがもっとたくさんコードを書く」ではない。

**人間がsuccessの真偽を監視し続けなくても、次へ進める範囲が増える。**

## 1つだけ導入するなら、`VERIFIED`を`SUCCESS`から分離する

大きなagent frameworkは必要ない。

既存CIの最後に、まず1つだけstateを増やす。

```text
SUCCESS
  commandが終了した

VERIFIED
  期待したrevision / artifact / remote identityまで確認した
```

そして、irreversibleなside effectやIssue closeは`VERIFIED`だけを入口にする。

例えばWeb deploymentなら、

```text
build success
  ↓
artifact created
  ↓
deploy success
  ↓
public URL fetch
  ↓
expected SHA / marker match
  ↓
VERIFIED
```

publish処理なら、

```text
upload
  ↓
remote read-back
  ↓
expected channel / object / visibility match
  ↓
VERIFIED
```

databaseなら、

```text
write
  ↓
read-back
  ↓
primary key / version / row count / checksum match
  ↓
VERIFIED
```

この1段を追加するだけで、greenという曖昧な言葉がかなり弱くなる。

## 何をまだ証明していないか

この記事は、AI agent導入で人間工数が何%減ったかを測っていない。

exact-head CIやremote verificationを入れれば障害がゼロになる、とも言っていない。

また、すべての処理に複雑なprovenance graphが必要だとも考えていない。

単一processで外部side effectがなく、毎回人間が結果を見る小さなscriptなら、普通の例外とtestだけで十分なこともある。

今回の結論が効くのは、**AIが人間の確認なしに次のactionへ進む範囲を広げたいとき**だ。

そのとき、失敗を見せるだけでは足りない。

成功したと主張する側にも、証拠が必要になる。

## AIを「過保護」にするな。その次は、AIの成功を過信するな

Crash-Driven Developmentを書いたとき、敵は「失敗を隠すコード」だった。

今もそれは変わらない。

ただ、運用して分かったのは、その先にもう一つ大きな敵がいたことだ。

**成功を早く宣言しすぎるシステム**である。

クラッシュは目立つ。

false greenは目立たない。

だから、自律化が進むほど設計の重心を、

```text
How do we expose failure?
```

から、

```text
What evidence authorizes success?
```

へ移した方がいい。

AIに失敗する権利を与える。

そして、成功を名乗るには証拠を要求する。

2026年の私たちにとって、それがCrash-Driven Developmentの続きになった。