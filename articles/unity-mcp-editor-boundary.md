---
title: "2026年、Unity MCPはどこまで実用になったのか――14件の実例から見る成功・失敗・完成境界"
emoji: "🛠️"
type: "tech"
topics: ["unity", "mcp", "codex", "claudecode", "ai"]
published: false
published_at: 2026-08-12 16:03
---

# 2026年、Unity MCPはどこまで実用になったのか――14件の実例から見る成功・失敗・完成境界

「AIがUnity Editorを操作できる」は、もう面白デモだけの話ではありません。

2026年には、自然言語だけで簡単なゲームを作った例、2Dから3Dへの作り替え、EditMode / PlayMode testまで通した例、全6章のサバイバルゲームを完成させた例まで公開されています。

一方で、49分かけて7回自己テストし5件を自己修正したのに「最初の部屋から出られない」問題を見逃した例、30分考え続けてVisual Effect Graphを完成できなかった例、Editor上では変更されたのに保存されず消えた例、Connected表示なのに実際には操作不能だった例もあります。

つまり、2026年に読む価値がある問いは、

```text
UnityをAIから操作できるか？
```

ではありません。

```text
どの種類の仕事なら任せられるのか？
どこまで到達したら「成功」と呼べるのか？
実運用で人間は何を握り続ける必要があるのか？
```

です。

この記事では、2026年に公開されたUnity MCP / Unity Editor agentの実運用記録を横断し、成功例と失敗例を同じ物差しで比較します。

結論を先に書くと、**prototype生成と反復実装はすでに実用域に入っています。しかし、完成判定、体験品質、接続安定性、保存、runtime validationまで含めると、人間のverification layerはまだ外せません。**

---

## このレビューで何を数え、何を数えなかったか

これは学術的なsystematic reviewではありません。

2026年8月15日までに公開され、次の条件を満たす実運用記録を中心に比較しました。

- 2026年に実施または公開されたことが確認できる
- Unity EditorをAI agent / MCPから実際に操作している
- 「導入できた」だけでなく、ゲーム、Scene、test、build、debugなどの結果が書かれている
- 成功だけでなく、失敗・修正・人間介入の情報がある

note、Zenn、Qiita、DevelopersIO、個人・企業blog、GitHub issue、Unity公式情報を調査しました。Redditも探索しましたが、今回の中心表では、環境・成果物・失敗条件まで追える投稿を優先し、再現条件の薄いコメントは採用していません。

また、時期によって使われているものが違います。

```text
Unity公式 MCP / Unity AI MCP Server
CoplayDev/unity-mcp
uLoopMCP → Unity CLI Loop
```

AI modelもClaude Code、Codexなどが混在します。したがって、以下の事例から「製品Aの成功率は何%」のような統計は出しません。

比較するのは**到達した成果の段階**です。

---

## 「成功」を5段階に分ける

Unity MCPの記事を読むとき、最も危険なのは全部を「成功」でまとめることです。

この記事では次の5段階で読みます。

```text
L1  EDITOR_OPERATED
    Scene / GameObject / script等を操作できた

L2  PLAYABLE
    Play Modeで最低限遊べた

L3  VERIFIED
    test / console / build等の機械検証を通した

L4  SUSTAINED
    複数feature・複数sessionを跨ぐ開発を継続できた

L5  RUNTIME_COMPLETED
    公開物・実機・外部プレイヤー等、最終利用環境まで確認した
```

`tool call returned success`はL1より前の中間状態です。

これをL4やL5と同じ「できた」にすると、Unity MCPの実態を見誤ります。

---

## 2026年の実例を並べる

### 1. 2月19日：同じブロック崩しでも3時間と1時間に分かれた

増田恭隆氏は、同じ「ブロック崩し」をUnity側のMCP系とCoPlay MCPで比較しています。

前者は実装に約3時間かかり、本人はバグとtrial-and-errorの多さを厳しく評価。一方CoPlay側は約1時間で、人間が修正したのは4箇所だったと報告しています。

これは「MCPなら全部同じ」ではないことを示す初期の重要な例です。Editor APIをどう抽象化してagentへ見せるかで、同じモデルでも結果が変わります。

出典:
https://note.com/yasutaka_masuda/n/n74397dbf2abf

到達点: **L2 PLAYABLE**

---

### 2. 2月24日：2Dを作り、3D化し、修正loopまで回した

uLoopMCPをClaude Codeから使った検証では、白紙projectから数字付きブロック崩しを作り、さらに2D版を3D版へ拡張しています。

初回出力について作者は「土台がほぼできていました」と評価しています。ただし3D化では、ブロックが壁にめり込む、ボールが正しく反射しないなどの問題が発生し、人間が動作確認しながら修正を依頼しています。

重要なのは、Hierarchy取得、Editor画面capture、compile、test、Play Mode制御をagentが使えるため、単発生成ではなく**観測→修正**へ進めたことです。

出典:
https://zenn.dev/unsoluble_sugar/articles/cd8d59be7b8f85

到達点: **L2〜L3**

---

### 3. 2月28日：「Connected」なのに動かないところから遊べるまで復旧

よなよな@AIゲーム開発氏は、Unity 6 + Codex + MCPでVampire Survivors系ゲームを作る過程を記録しています。

最初は、

```text
Unity: Connected
Codex: projectを列挙できない / 操作不能
```

という状態でした。

さらにMain Camera消失、真っ白・真っ青な画面、初期化順序の問題、参照待ちによるfreeze、UI責務の重複まで発生しています。

最終的にはHP/XP、被弾、攻撃、SE等を持つ遊べる状態まで進みましたが、作者が得た教訓は「Codexに任せるほど、人間側の観測精度が重要になる」でした。

出典:
https://note.com/yonayona_ai_game/n/nb1ec6a528bbd

到達点: **L2**

この事例は、connection stateそのものをcompletion evidenceにしてはいけないことを示します。

---

### 4. 3月8日：12 objectは作れた。でも部屋に入れなかった

DevelopersIOはUnity公式MCP + Claude Code / Opus 4.6でTPS templateを改造しています。

新しい部屋を指示すると、AIは壁、床、天井、doorway等の12 objectを生成しました。

しかし人間がPlay Modeで見ると、

- 既存壁がdoorwayを塞いでいて侵入不能
- 部屋内部にlightがなく暗い
- scaleが既存sceneと不整合
- Static Editor Flagsが未設定
- materialも既存環境と不統一

でした。

AIは外部4視点からcaptureしていましたが、部屋内部へcameraを入れて確認していませんでした。

出典:
https://dev.classmethod.jp/articles/unity-mcp-tps-game-claude-code-modification/

到達点: **L1 EDITOR_OPERATED。ただしgameplay validationでは失敗**

これはこの記事の中心命題を非常に分かりやすく示します。

```text
12 objects created successfully
!=
usable room created successfully
```

---

### 5. 3月11日：自然言語だけでCatchGameを全自動生成

miya氏はUnity MCPのAssistant windowからCodexを使い、簡単なcasual game「CatchGame」を自然言語のみで全自動開発したと報告しています。記事には生成過程、play、生成codeのvideo timelineもあります。

出典:
https://note.com/miya19/n/n4503e377dc45

到達点: **L2 PLAYABLE**

これは「簡単なゲームなら、コード生成だけでなくUnity Editor操作まで含めて自然言語から成立する」という強い成功例です。

一方、この1件から大型gameやproduction qualityまで一般化はできません。

---

### 6. 3月13日：7回testして5件直したのに、最初の部屋から出られなかった

2026年の事例の中で、最も示唆が大きい検証の一つです。

DevelopersIOはClaude Code + Unity MCPに、

1. 弾幕shooting
2. athletics game
3. 探索型dungeon

を作らせています。

単純な前2つは初回出力で成立し、所要時間は7.5分、9分でした。

複雑なdungeonは49分。Claude Codeは自ら7回Play Mode testを実行し、5件の問題を自己修正しました。

それでも人間が実際に操作すると、**スタート部屋の出口に初期jumpでは届かず、最初の部屋から一歩も出られませんでした。**

原因は明確です。

agentはtest時にplayerをMCP経由でwarpして各部屋を検査していました。

```text
state consistency test: PASS
actual player traversal: FAIL
```

だったのです。

人間の指摘後、4分で出口位置は修正され、clearまで進めるようになりました。しかし複数回playすると別の詰みpatternも残っていました。

出典:
https://dev.classmethod.jp/articles/unity-mcp-claude-code-2d-game-verification/

到達点: **L3 VERIFIEDに近いが、実プレイ基準では未完了**

この事例から分かるのは、agentic test loopがあっても**test oracleが間違っていれば自律性は完成保証にならない**ということです。

---

### 7. 3月22日：企画→実装→検証→WebGL公開をworkflow化

umezu_y氏はCoplayDev/unity-mcpとClaude Codeを使い、ゲーム開発を8 phaseに分割した`hcg-workflows`を公開しています。

特に重要なのは、AIに好きに作らせるのではなく、

```text
仕様
→ task
→ 実装
→ test
→ console
→ Play Mode
→ screenshot
→ commit
→ release
```

をworkflowとして固定している点です。

L1はcompile error、L2はPlay Mode runtime error、L3はscreenshotによる視覚確認という段階的verificationも定義されています。

出典:
https://qiita.com/umezu_y/items/090a0fd25f9f915ad375

到達点: **成果物そのものより、L3以降へ進むための運用設計の証拠**

「高性能なmodelを使えば完成する」より、「completion contractを設計する」の方が実務では再現性があります。

---

### 8. 4月5日：雑な指示からゲームを作り、別agentでbuildまで進めた

四駒アイ氏はWindows 11 / Unity 6.4 / Cursor環境で、Claude CodeとCodexの両方からUnity MCPを利用しています。

Claude Codeへかなり雑な指示を与えた結果を、記事中で短く「ゲーム完成です。」と報告。そのprojectをCodexから修正し、buildによって複数機能を追加しています。

ただし本人の評価は「叩き台としては良さそう」で、操作性には改善余地があるとしています。

出典:
https://note.com/4komaai/n/nafd4090dc068

到達点: **L2 + build実行**

つまり、

```text
natural language
→ scene / script
→ playable draft
→ another agentで改修
→ build
```

は現実に起きています。

---

### 9. 4月11日：最初は大量error、別の観測loopを足すと遊べるまで修正

ティー氏はCoplayDev/unity-mcpで「簡単な神経衰弱」を作らせました。

一見完成したものの、Playすると大量のerrorが出ました。

そこでUnity CLI Loop（旧uLoopMCP）を追加し、Play Modeとerror確認を使ったdebugを依頼すると、問題なく遊べるところまで修正できたと報告しています。

出典:
https://note.com/mindpower/n/nba514492f5a5

到達点: **最初はL1止まり → observation / repair loop追加後にL2**

これも重要です。

**生成能力より、観測能力を足したことで成果が上がっています。**

---

### 10. 4月17日：既存ゲームの全自動移植はできた。ただし「未完成」

miya氏はCodex + UnityMCPで既存の「マグネットスイーパー」をUnityへ全自動移植しています。

ゲーム自体は自動実装された一方、本人はUI修正等が必要で「まだまだ未完成」と評価し、実装にもそれなりの時間がかかったと書いています。

出典:
https://note.com/miya19/n/n8df417077cb0

到達点: **L2に近いprototype。completionは未達**

成功例だけを並べるより、この「動くが未完成」が実運用の中央値に近い可能性があります。

---

### 11. 5月7日：bug fixは強い。shader / VFXは弱かった

株式会社ユニスポットはClaude Code + Unity MCPで、既存3D projectを対象に複数種類の仕事を試しています。

既存のofficial controllerを参考にVRM characterのanimation不具合を直すtaskでは、構造を確認し、script作成・attachまで行って正常にanimationするところまで到達しました。

一方、shader調整では何度か試しても期待した変化が出ず失敗。Visual Effect Graph生成では約30分処理し、5時間枠のtoken容量の約50%を消費したのに、output nodeが途中で止まり動作しませんでした。

出典:
https://www.uni-spot.com/blog_post/claude-unity-mcp/

到達点:

```text
existing bug fix: strong
art direction: weak / variable
complex VFX graph generation: failed in this case
```

「Unity MCPは強いか弱いか」ではなく、**task classで性能が違う**と考える方が正確です。

---

### 12. 6月20日：3D鬼ごっこ + EditMode 4件 + PlayMode 3件が全PASS

zuqqhi2氏はCoplayDev版unity-mcp + Codexで、最小限の3D鬼ごっこを作らせています。

要求には最初からEditMode / PlayMode testも含めています。

生成後、Unity Test Runnerで、

- EditMode: 4 testすべてPASS
- PlayMode: 3 testすべてPASS

を確認しています。

初期cameraはstage上部が見切れていましたが、追加指示で修正されています。

出典:
https://zuqqhi2.com/coplaydev-unity-mcp-codex-game-dev

到達点: **L3 VERIFIED**

この例は、completion conditionを最初からpromptに含めると「動いた」より強い証拠を作れることを示します。

---

### 13. 6月24日：Roll-a-Ballは約10分でerrorなくplayable

花王のTsuchiyaK氏はUnity公式MCP Server + Claude Codeで、Unity入門のRoll-a-Ballを作らせています。

作業開始から約10分後、実際にPlayし「エラーなくプレイできるゲーム」が完成。その後「ホラーゲームっぽくして」という曖昧な指示でも、lighting、post process、enemy、game over処理まで追加しています。

出典:
https://qiita.com/TsuchiyaK/items/a3de1ac034bf94cf905b

到達点: **L2 PLAYABLE**

単純game / tutorial規模では、自然言語からplayableまでの摩擦はかなり小さくなっています。

---

### 14. 7月9日：全6章のゲームを完成させた実例が出た

「結局、小さいdemoしかないのでは？」に対する強い反例がbunnoneta氏の『昭和サバイバル』です。

2026年7月9日、Unity MCPを使いながら設計、coding、debugを進め、全6章構成、町育成、boss、gamepad対応等を含むUnity製survival actionを完成させたと報告しています。

出典:
https://note.com/bunnoneta/n/n91bbcd3fd700

前段階の開発記:
https://note.com/bunnoneta/n/ndd6c132b1abf

到達点: **L4 SUSTAINED**

ここまで来ると、Unity MCPを「prototype toolだけ」と呼ぶのも正確ではありません。

ただし、この成功例こそ、完成までの摩擦を大量に記録しています。

- `execute_code`では型名をnamespace / assembly込みで指定しないと失敗する場面
- `EditorUtility.SetDirty()`等を呼ばず、変更が見た目だけ反映され保存されない場面
- prefab saveが必要な場面
- compile / domain reload待ち
- balanceが完成直前まで崩れていた問題
- logと観測器を作りながら原因を潰すdebug

つまり、長期成功例の実態は、

```text
AIが全部正しく作った
```

ではありません。

```text
AIと人間が
生成 → 観測 → failure発見 → 修正 → 再検証
を何度も回し、最終的に完成へ到達した
```

です。

これは十分に大きな成果ですが、意味は全く違います。

---

## 2026年の事例から見える「得意・苦手」の境界

事例をtask classでまとめると、傾向はかなり揃います。

| task | 2026年の観測 | 判断 |
| --- | --- | --- |
| GameObject / Scene生成 | 多数の成功例 | 実用域 |
| script生成・attach | 多数の成功例 | 実用域 |
| 簡単な2D / 3D game prototype | 10分前後〜短時間の成功例あり | 実用域 |
| 既存bug調査・修正 | animation修正等で成功 | 強い |
| compile / console / test loop | toolが揃えば自律修正例あり | 強いがoracle設計が必要 |
| build | 実例あり | 利用可能 |
| 複雑なgame progression | 49分 + 自己修正後も詰みを残した例 | 人間validation必須 |
| art direction / game feel | 成功例と失敗例が混在 | 不安定 |
| shader / VFX graph | 失敗例あり | 高コスト・不安定 |
| connection / process lifecycle | 複数の障害報告 | 運用設計が必要 |
| 長期game development | 全6章完成例あり | 可能。ただし人間の基準・観測が必要 |
| 外部playerが感じる面白さ | 自動評価の証拠は弱い | まだ人間側 |

---

## 研究側から見ると「修正loopが本体」という解釈とも整合する

2026年7月公開のpreprintでは、MCPとは別の条件ですが、Unity C# scene生成をsingle-passで厳しく評価しています。

4つのopen-weight model、26種類のgoal pattern、合計10,400 generationを評価したところ、**single-passではrunnable sceneまでcompileしたものが0件**でした。

出典:
https://arxiv.org/abs/2607.10187

この研究をUnity MCPの成功率へ直接読み替えてはいけません。

条件が違います。

しかし示唆は重要です。

公開demoの多くは、

```text
生成
→ compile
→ error取得
→ 修正
→ scene観測
→ 再修正
```

というiterative repair loopを使っています。

「AIが一発でUnityを理解する」ことより、**Unityを観測でき、失敗から戻れること**の方が2026年時点では重要だと考える方が、実例と整合します。

---

## Unity公式化でsetup問題は消えたのか

2026年5月、UnityはUnity AIをopen betaとして公開し、MCP Serverも公式toolchainへ入れました。

公式:
https://unity.com/blog/unity-ai-how-to-get-started
https://unity.com/blog/unity-ai-mcp-how-to-get-started

これは大きな変化です。

しかしUnity自身もopen betaについて、features、behavior、availabilityは変更・制限・終了の可能性があると明記しています。

またcommunity側も高速で変化しています。CoplayDev/unity-mcpの`v10.1.2`は2026年8月2日に公開され、release noteにはCodex HTTP transport、Windows launch、approval prompt等の修正が並びます。

https://github.com/CoplayDev/unity-mcp/releases/tag/v10.1.2

したがって、2026年2月の体験談と2026年8月の体験談は完全には同じtechnologyを測っていません。

この変化速度自体が、現時点のproduction adoptionでversion pinとregression testを必要とする理由です。

---

## 自分たちの`image2outfit`は、まだ成功例に数えない

`KAFKA2306/image2outfit`のDraft PR #212では、local Blender + Unity MCP supportを実装しています。

https://github.com/KAFKA2306/image2outfit/pull/212

しかしPRは次を明示的に`NOT_RUN`としています。

- user Windows環境でのPowerShell setup
- live Blender MCP connection
- live Unity MCP connection / package resolution
- Blender Assistant → Codex → MCP end-to-end call

またMCP integrationはoptional authoring supportであり、既存の`requiredCompletionGates`を変更していません。

つまり、現時点で言えるのは、

```text
integration code exists
static contract exists
```

までです。

```text
live Unity MCP E2E passed
VRChat runtime completed
```

とはまだ言えません。

外部事例をレビューした結果、自分たちの実装についても同じ基準を適用します。

---

## 実運用では、MCPをcompletion gateではなくauthoring adapterにする

2026年の事例を横断すると、現実的な構造はこれです。

```text
Codex / Claude Code
        ↓
Unity MCP
        ↓
Unity Editor
        ↓
compile / console / tests
        ↓
Play Mode observation
        ↓
build
        ↓
actual runtime / user validation
```

MCPの役割は、上流の操作を速くすることです。

完成条件を短絡することではありません。

最低でもstateは分けます。

```text
TOOL_SUCCESS
    ↓
EDITOR_VALIDATED
    ↓
RUNTIME_COMPLETED
```

例えば、

```json
{
  "tool_success": true,
  "editor_validated": true,
  "runtime_completed": false,
  "runtime_reason": "NOT_RUN"
}
```

なら、task全体をcompletedとは呼びません。

---

## では、2026年8月に導入する価値はあるのか

あります。

ただし「Unity開発を全部AIにするtool」として導入すると期待値を外します。

特に価値が高いのは、

```text
prototype
repetitive scene work
script scaffolding
existing bug investigation
test generation
console-driven repair
variant creation
```

です。

逆に、

```text
game feel
art direction
playability across procedural states
final visual quality
runtime-specific behavior
player experience
```

は、まだ独立したvalidationが必要です。

2026年の公開実例から得られる一番有用な判断は、

> **Unity MCPは「使えるか？」の段階を越えた。ただし「何をもって完成とするか」を人間が定義しないと、速く間違った完成へ到達する。**

だと思います。

AIがUnityを操作できたこと自体は、もうニュースではありません。

次に競争になるのは、

```text
何を任せるか
何を観測するか
何を自動検証するか
どこで人間が止めるか
```

を設計できるかです。

---

## 参照した主な2026年実例・一次情報

- Unity AI open beta: https://unity.com/blog/unity-ai-how-to-get-started
- Unity MCP getting started: https://unity.com/blog/unity-ai-mcp-how-to-get-started
- DevelopersIO TPS検証: https://dev.classmethod.jp/articles/unity-mcp-tps-game-claude-code-modification/
- DevelopersIO 2D 3テーマ検証: https://dev.classmethod.jp/articles/unity-mcp-claude-code-2d-game-verification/
- uLoopMCP / Unity CLI Loop実運用: https://zenn.dev/unsoluble_sugar/articles/cd8d59be7b8f85
- 30分ヴァンサバ復旧記録: https://note.com/yonayona_ai_game/n/nb1ec6a528bbd
- Unity MCP比較・ブロック崩し: https://note.com/yasutaka_masuda/n/n74397dbf2abf
- CatchGame全自動生成: https://note.com/miya19/n/n4503e377dc45
- マグネットスイーパー移植: https://note.com/miya19/n/n8df417077cb0
- 神経衰弱 + debug loop: https://note.com/mindpower/n/nba514492f5a5
- Claude Code / Codexのゲーム生成: https://note.com/4komaai/n/nafd4090dc068
- 企画→公開workflow: https://qiita.com/umezu_y/items/090a0fd25f9f915ad375
- 3D鬼ごっこ + EditMode / PlayMode test: https://zuqqhi2.com/coplaydev-unity-mcp-codex-game-dev
- Unity公式MCP + Roll-a-Ball: https://qiita.com/TsuchiyaK/items/a3de1ac034bf94cf905b
- Unity MCP + 3D project検証: https://www.uni-spot.com/blog_post/claude-unity-mcp/
- 『昭和サバイバル』完成記: https://note.com/bunnoneta/n/n91bbcd3fd700
- 『昭和サバイバル』全6stage開発記: https://note.com/bunnoneta/n/ndd6c132b1abf
- 『妖怪なんでも相談所』2作目実装記: https://note.com/bunnoneta/n/naa2726ea0a32
- CoplayDev/unity-mcp v10.1.2: https://github.com/CoplayDev/unity-mcp/releases/tag/v10.1.2
- 10,400 single-pass Unity generation preprint: https://arxiv.org/abs/2607.10187
- image2outfit Draft PR #212: https://github.com/KAFKA2306/image2outfit/pull/212
