---
title: "Unity MCPはゲームを作れる。でも『完成』を任せると危ない――実運用の成功例と失敗例"
emoji: "🛠️"
type: "tech"
topics: ["unity", "mcp", "codex", "vrchat", "ai"]
published: false
published_at: 2026-08-12 16:03
---

# Unity MCPはゲームを作れる。でも「完成」を任せると危ない――実運用の成功例と失敗例

「AIがUnity Editorを操作できる」は、もうデモだけの話ではありません。

2026年7月には、Unity MCPを使いながら全6章のサバイバルアクションを完成させた個人開発者の実録があります。別の開発者は、Claude Codeへのかなり雑な指示からゲームの叩き台を作り、その後Codexから修正してbuildまで進めています。

一方で、Unityエンジニアによる検証では、オセロを作らせても「全自動で完成」には届かず、Scene編集や細かな挙動調整は手作業の方が速かったと報告されています。

つまり、いま読む価値がある問いは、

```text
UnityをAIから操作できるか？
```

ではありません。

```text
どこまでなら本当に任せられるのか？
どこから人間の検証が必要になるのか？
長時間の実運用で何が壊れるのか？
```

です。

この記事では、MCPのsetup方法ではなく、公開されている成功例・失敗例・upstream issueを使って、**Unity MCPの実態とcompletion boundary**を整理します。

## 先に結論：プロトタイプ生成は実用域。完成保証は別問題

公開事例を並べると、2026年8月時点の実態はかなりはっきりしています。

| 実例 | 実際に起きたこと | ここから言えること |
| --- | --- | --- |
| 四駒アイ氏、2026-04-05 | Claude Codeへの雑な指示からゲームを生成。その後Codexで機能追加しbuild | 小規模な叩き台生成・反復編集は成立する |
| 株式会社アタリ、2025-05-16 | オセロを試作。コードベースは作れるが、Sceneや細かな挙動は手動の方が速い | 「ゲーム全体を自動完成」は別問題 |
| bunnoneta氏、2026-07-09 | Unity MCP併用で全6章のゲームを完成 | 長期開発でも成果物まで到達できる |
| 同氏の運用記録 | 保存漏れ、型名、C#構文、改行、compile待ち、freeze調査などを経験 | Editor操作成功と成果物の正しさは一致しない |
| CoplayDev issue群 | reconnect、batch-mode、Codex transport等の障害報告 | 接続・process lifecycle自体も運用対象になる |

成功例も失敗例もあります。

だから結論は、

```text
MCPは使える
```

でも、

```text
MCP toolが成功した = Unity成果物が完成した
```

ではない、です。

---

## 成功例1：雑な指示から、実際にゲームの叩き台ができる

四駒アイ氏は2026年4月、Windows 11 / Unity 6.4 / Cursor環境でUnity MCPをClaude CodeとCodexから利用しています。

接続設定には苦戦し、Claude Code側の設定場所へ辿り着くまで「1,2時間くらいかかってしまいました」と書いています。

しかし接続後は、Claude Codeへかなり雑な指示を与え、記事中で短く、

> 「ゲーム完成です。」

と報告しています。

さらに同じprojectをCodexから修正し、buildによって複数機能を追加できています。ただし本人の評価は「叩き台としては良さそう」であり、操作性には改善余地があるとも書いています。

出典:
https://note.com/4komaai/n/nafd4090dc068

ここで重要なのは、「できた」の中身です。

```text
自然言語
→ Scene / script生成
→ build可能なゲームの叩き台
```

までは実例があります。

しかし、

```text
面白い
操作しやすい
壊れない
公開品質
```

までは同じ証拠からは言えません。

**生成できることと、完成品質を満たすことは別stateです。**

---

## 成功例2：Unity MCPを使いながら、ゲーム1本を本当に完成させた例もある

「結局デモしか作れないのでは？」という疑問に対しては、もっと強い反例があります。

bunnoneta氏は2026年7月9日、Unity MCPを使った開発で、全6章構成のサバイバルアクション『昭和サバイバル』を完成させたと報告しています。

記事では、設計、コーディング、debugだけでなく、完成直前のbalance調整、gamepad対応、演出、敵追加、当たり判定修正までAIと往復しています。

出典:
https://note.com/bunnoneta/n/n91bbcd3fd700

これはかなり重要です。

Unity MCPは、単にcubeを置くdemoに限定されていません。

```text
長い開発
→ bug修正
→ 複数scene
→ gameplay調整
→ 入力対応
→ 最終仕上げ
→ 完成
```

まで付き合える事例が実際にあります。

ただし、その成功例こそが「tool successだけでは足りない」ことも同時に証明しています。

---

## 完成例で露呈した「見た目だけ成功」の罠

同じ開発記には、Unity MCPを長く使ったからこそ分かった地雷が具体的に残されています。

### 1. Editor上では変わったのに、保存されていない

scriptやassetの値を書き換えても、Unity側で`EditorUtility.SetDirty()`等の適切な保存処理がなければ、見た目には反映されてもEditorを閉じると消えるケースを経験しています。

Prefabではさらに保存処理が必要だったとされています。

これは典型的な偽成功です。

```text
MCP tool: success
Unity画面: changed
再起動後: lost
```

tool responseだけをcompletion evidenceにしていたら、この不具合はPASSになります。

### 2. scriptを書いた直後はUnityがまだ古い状態

Unityはscript変更後にcompile/domain reloadを挟みます。

同記事では、書き換え直後に次操作へ進むとcompile完了前の古い状態で処理が進むため、待ってconsole errorを確認する運用が必要だったとされています。

つまり、

```text
write script
→ tool success
→ next action
```

では速すぎる場合があります。

必要なのは、

```text
write script
→ compile settle
→ console readback
→ next action
```

です。

### 3. AIが一発でdebugしてくれるわけではない

最終boss撃破時のfreezeでは、原因をAIが即答したのではなく、frame単位で処理を記録する`HangWatchdog`を作り、実際にfreezeさせ、logを読んで原因を追ったと報告されています。

要するにAIの価値は、

```text
魔法の一発回答
```

というより、

```text
仮説
→ 観測器を作る
→ 再現する
→ logを読む
→ 修正する
```

という普通のengineering loopを高速に回せることにあります。

この違いは大きいです。

---

## 失敗例：Unityエンジニアが試しても「全部自動」は難しかった

株式会社アタリのUnityエンジニア赤池氏は2025年5月、Claude 3.7 SonnetとCursorを使ってUnity MCPを比較しています。

オセロを作らせた結果について、記事では、

> 「結局手動の方が早いという印象です。」

とまとめています。

コードのベース生成はできるものの、Scene編集と細かな挙動調整は全自動完成に届かなかった、という評価です。また曖昧な自然言語指示では、後から構造的に調整しにくいcodeが生成される場合も報告されています。

出典:
https://note.com/atali/n/n64b709af8411

これは「Unity MCPは役に立たない」という話ではありません。

むしろ、得意領域が見えます。

```text
強い:
- 既存codeの調査
- 部分修正
- debugging
- prototype
- repetitive Editor work

難しい:
- 曖昧な仕様からの最終品質決定
- game feel
- fine tuning
- 長い依存関係を跨ぐcompletion保証
```

後者を前者と同じ「AI操作」でまとめると期待値を誤ります。

---

## 2作目でもsetupで約1時間消える。それが実運用

さらに2026年7月の別の開発記では、前作でUnity MCPを使っていた作者が、次のprojectでも同じ構成を使おうとして初手で止まっています。

原因は、MCP for Unity packageがprojectごとのinstallだったことでした。

作者は手順を思い出すのに、

> 「小一時間溶かしました。」

と書いています。

その後、JSONで事前検証済みの30 event等をUnityへ組み込み、一通り遊べる状態まで到達しています。

出典:
https://note.com/bunnoneta/n/naa2726ea0a32

この事例が示すのは、MCPの価値と導入摩擦が同時に存在することです。

1回動いたからといって、

```text
別project
別Unity version
別client
別transport
```

でもそのまま動くとは限りません。

**MCP server自体も開発環境のdependencyとして管理する必要があります。**

---

## upstream issueを見ると、接続そのものもproduction concernになる

実運用の難しさは個人blogだけではありません。

CoplayDev/unity-mcpのissueにも、再現条件付きの障害が残っています。

### reconnect：serverを何度も再起動する状態

Issue #672では、2026年2月、server disconnectと自動reconnect不足により、利用者が「multiple times per hour」serverを再起動することがあると報告しています。

このissueは現在closedですが、重要なのは「Unity操作APIが豊富か」以前に、**長時間sessionのlifecycleが実用性を左右する**ことです。

https://github.com/CoplayDev/unity-mcp/issues/672

### batch buildがinteractive MCP serverを落とす

Issue #1196では、2026年6月、同一machine上のUnity batch-mode processが終了した際、interactive HTTP serverまで停止させる問題が再現されています。

報告者の環境では、agent-driven batch compileを頻繁に回すため、serverが1日に何度も停止したとされています。

このissueは修正PR #1235に紐づきclosedしています。

https://github.com/CoplayDev/unity-mcp/issues/1196

これは特に重要です。

```text
interactive agent session
+
CI / batch build
```

を同じmachineで併用する、本格運用ほど踏みやすい問題だからです。

### Codexからtool一覧は見えるのに、全callが失敗する例

Issue #1215では、Windows / Unity 2022.3.62f3 / MCP for Unity 9.7.3 / Codex / HTTP環境で、tool自体は見えているのに全callが`unsupported call`になる報告があります。

https://github.com/CoplayDev/unity-mcp/issues/1215

一方、CoplayDevの最新stable releaseは2026年8月2日公開の`v10.1.2`で、release noteにはCodex HTTP transport repair、Windows server launch修正、過剰なapproval prompt修正などが含まれています。

https://github.com/CoplayDev/unity-mcp/releases/tag/v10.1.2

つまり、2026年のUnity MCPは「止まった実験」ではありません。

**実用化が進んでいる一方で、transport、approval、process lifecycle、Editor state同期のような運用問題を今まさに潰している段階**です。

---

## Unity自身もMCPを提供するようになった。ただしopen beta

ここも2025年の記事とは状況が変わっています。

Unity Technologiesは2026年6月、公式blogでUnity自身がofficial MCP serverを提供していることを説明しています。

https://unity.com/blog/mcp-servers-game-development

同ページでは、UnityのAI toolsは現在open betaであり、機能・挙動・availabilityは変更、制限、終了の可能性があるとも明記しています。

つまりMCPという考え方自体は、community pluginだけの実験からUnity公式のproduct surfaceへ進みました。

しかし、officialになったことと、

```text
AIが最終成果物を自律的に保証できる
```

ことは別です。

MCPが標準化するのは**操作とcontext access**です。

completion criteriaそのものではありません。

---

## だから3種類の「成功」を分ける

実例を見た後なら、この区別の必要性が分かります。

```text
TOOL_SUCCESS
    ↓
EDITOR_VALIDATED
    ↓
RUNTIME_COMPLETED
```

### TOOL_SUCCESS

MCP clientからUnityへ命令を送り、tool responseが成功した状態です。

```text
GameObjectを作成した
Componentを変更した
scriptを編集した
test toolを呼んだ
```

これは必要です。

しかし、ここで止めると、

```text
保存されていない
compile前の古いstate
違うobjectを編集した
referenceが切れている
```

を見逃せます。

### EDITOR_VALIDATED

Unity Editor側を読み直し、期待したstateになったことを確認した状態です。

```text
tool response = success
AND
対象objectが存在
AND
期待componentが存在
AND
referenceが解決
AND
compile errorなし
AND
保存後にstateが残る
```

ここでは「AIが変更しましたと言った」ことを証拠にしません。

Editor stateを再観測します。

### RUNTIME_COMPLETED

実際の成果物に必要な最終gateを通った状態です。

gameならplaytest、build、input、performance、gameplay。

VRChat向けならproject contractに応じて、Unity import、NDMF / Modular Avatar processing、Build & Test、実機runtime等が入ります。

```text
Editor validation passed
!=
runtime completion passed
```

この境界が記事の中心です。

---

## `image2outfit` では、意図的にNOT_RUNのままにしている

`KAFKA2306/image2outfit` のDraft PR #212は、OpenAI Codexからlocal Blender + Unity MCPを使うsupportを実装しています。

2026年8月15日時点でもPRはDraftで、本文では次を明示的に`NOT_RUN`としています。

- user Windows環境でのPowerShell setup
- live Blender MCP connection
- live Unity MCP connection / package resolution
- Blender Assistant → Codex → MCP end-to-end call

PR:
https://github.com/KAFKA2306/image2outfit/pull/212

また、このintegrationはoptional local authoring supportであり、既存の`requiredCompletionGates`を変更しない設計です。

つまり、このPRから言えるのは、

```text
integration code exists
static contract exists
```

までです。

**live Unity MCP E2Eが成功した、VRChat成果物が完成した、とはまだ言いません。**

この区別を消すと、この記事自身が批判している「偽の成功」を再生産します。

---

## MCPはcompletion gateではなくauthoring adapterにする

実運用では、次の位置に置くのが安全です。

```text
Codex / Claude Code / Cursor
        ↓
MCP for Unity / Unity MCP Server
        ↓
Unity Editor
        ↓
state readback / console / tests
        ↓
build
        ↓
runtime / human validation
```

MCPを導入したことで、既存のcompletion gateを短絡しません。

これはMCPを信用しないという話ではありません。

**操作チャネルと検証チャネルの責務が違う**という話です。

---

## 実運用で「任せやすい仕事」と「任せきれない仕事」

公開事例から、現時点では次の切り分けが妥当です。

### 任せやすい

- GameObject / Componentの大量作成
- Sceneの叩き台
- script生成・部分修正
- 既存projectの検索・調査
- consoleを使ったdebug loop
- repetitiveなEditor操作
- test / buildの起動
- 小規模prototype

### 検証を別に持つべき

- reference integrity
- asset / Prefabの永続保存
- compile / domain reload後のstate
- build processor後のstate
- inputやscene transition
- performance
- game balance / game feel
- VRChat等のtarget runtime

ここを分ければ、MCPはかなり強力です。

逆に、全部を一つの`success`へ潰すと危険です。

---

## 再利用できるcompletion contract

GUI applicationをAI agentへ渡す場合は、結果をBoolean一つにしない方がいいです。

```yaml
completion:
  tool_success:
    required: true
  editor_validation:
    required: true
  runtime_validation:
    required: true
```

実行環境がなくruntime validationを回せないなら、

```yaml
runtime_validation:
  status: NOT_RUN
```

とします。

`NOT_RUN`を`PASS`へ変換しない。

単純ですが、実際の成功例・失敗例を見ると、この区別が一番効きます。

---

## まとめ：Unity MCPは「使える」。だからこそ成功条件を厳しくする

Unity MCPは、もうcube demoだけの技術ではありません。

2026年には、

- 雑なpromptからplayableな叩き台を作った例
- Codexで追加修正してbuildした例
- AIとUnity MCPを使い、ゲーム1本を完成させた例

まで公開されています。

一方で同じ実運用から、

- setupに1〜2時間かかる
- 別projectで再設定に詰まる
- 見た目だけ変わり保存されない
- compile待ちが必要
- 型名、C# version、改行差で失敗する
- freezeは再現用の観測器から作る
- MCP server自体がdisconnectする
- batch buildとinteractive sessionが干渉する

という現実も出ています。

だから評価は、

```text
Unity MCPはまだ使い物にならない
```

でも、

```text
AIにUnityを全部任せれば完成する
```

でもありません。

より正確には、

```text
AIはUnity Editorをかなり深く操作できるようになった。
しかし「操作できた」「Editor上で正しい」「成果物として完成した」は、まだ別々に証明しなければならない。
```

です。

MCPが強力になるほど、最後に重要になるのはtool数ではありません。

**何をもって完成と呼ぶかを、AIの外側に固定できるかです。**

## 参考・検証元

- Unity公式: MCP servers in game development explained  
  https://unity.com/blog/mcp-servers-game-development
- CoplayDev MCP for Unity  
  https://github.com/CoplayDev/unity-mcp
- CoplayDev v10.1.2  
  https://github.com/CoplayDev/unity-mcp/releases/tag/v10.1.2
- CoplayDev Issue #672: reconnect / server lifecycle  
  https://github.com/CoplayDev/unity-mcp/issues/672
- CoplayDev Issue #1196: batch-modeとinteractive serverの干渉  
  https://github.com/CoplayDev/unity-mcp/issues/1196
- CoplayDev Issue #1215: Codex / HTTPでのunsupported call報告  
  https://github.com/CoplayDev/unity-mcp/issues/1215
- 四駒アイ「2026/4/5 UnityのMCPサーバ設定をしてみる in Cursor」  
  https://note.com/4komaai/n/nafd4090dc068
- 株式会社アタリ「Unity × MCPを試してみた：ClaudeとCursorの比較レビュー」  
  https://note.com/atali/n/n64b709af8411
- bunnoneta「AIと二人三脚で作ったゲーム『昭和サバイバル』、ついに完成しました」  
  https://note.com/bunnoneta/n/n91bbcd3fd700
- bunnoneta「Unity MCPでReigns系ゲームを組み上げるまで」  
  https://note.com/bunnoneta/n/naa2726ea0a32
- image2outfit Draft PR #212  
  https://github.com/KAFKA2306/image2outfit/pull/212
