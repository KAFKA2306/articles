---
title: "2026年、Unity MCPはどこまで実用になったのか――14件の実運用メタレビュー"
emoji: "🛠️"
type: "tech"
topics: ["unity", "mcp", "codex", "claudecode", "ai"]
published: false
published_at: 2026-08-12 16:03
---

# 2026年、Unity MCPはどこまで実用になったのか――14件の実運用メタレビュー

「AIがUnity Editorを操作できる」は、もう面白デモだけの話ではありません。

2026年には、自然言語だけで簡単なゲームを作った例、2Dから3Dへ作り替えた例、EditMode / PlayMode testまで通した例、そして複数ステージのゲームを継続開発して完成まで持っていった例が公開されています。

一方で、49分かけて7回自己テストし5件を自己修正したのに、実際のプレイヤーは最初の部屋から出られなかった例もあります。Visual Effect Graphに30分使って完成できなかった例、Editor上では変更されたように見えても保存されず消えた例、「Connected」と表示されているのに操作不能だった例もあります。

2026年に知りたいのは、もはや

```text
UnityをAIから操作できるか？
```

ではありません。

```text
何なら本当に任せられるのか？
どこで人間が介入したのか？
何をもって「完成」と呼んだのか？
自分の開発へ導入する価値があるのか？
```

です。

この記事では、2026年に公開されたUnity MCP / Unity Editor agentの実運用記録14件を同じ物差しで読み直します。

結論を先に書くと、**prototype生成、Scene操作、script実装、既存bug修正、console / testを使った反復修正はすでに実用域です。一方、複雑なplayability、game feel、視覚品質、長時間session、保存、最終runtime品質まで「AIが確認したから完成」とするには証拠が足りません。**

---

## 引用と要約のルール

この記事では、外部の実運用記録と筆者の解釈を混ぜません。

- `> 「……」` は原文からの**直接引用**
- 直接引用の直下に、著者名・記事名・公開日・URLを明記
- 引用符を付けていない説明は、原文に基づく**筆者要約**または本記事の分類
- 数字、日付、version、test件数などは元記事または公式一次情報で確認できたものだけを使用
- 体験談は「その環境で起きた観測」であり、製品全体の成功率には読み替えない

つまり、この記事の「実用域」「不安定」というラベルは引用ではなく、14件を比較した本記事の判断です。

---

## これはsystematic reviewではない

対象は、2026年8月15日までに公開され、次を満たす実運用記録です。

- Unity EditorをAI agent / MCPから実際に操作している
- setup紹介だけで終わらず、Scene、game、test、build、debug等の結果がある
- 成功だけでなく、失敗、修正、人間介入の情報を読み取れる
- 公開日、環境、成果のいずれかを確認できる

note、Zenn、Qiita、DevelopersIO、企業・個人blog、GitHub、Unity公式情報を調査しました。Redditも探索しましたが、中心表では環境・成果物・失敗条件まで追える記録を優先しました。

これは無作為抽出ではありません。成功体験を公開するselection biasもあります。そのため、

```text
14件中10件成功 → 成功率71%
```

のような数字は出しません。

代わりに、**どのtask classで、どの到達段階まで、どれくらい人間が介入したか**を比較します。

---

## 「成功」を5段階に分ける

Unity MCPの記事を読むとき、最も危険なのは全部を「成功」でまとめることです。

```text
L1 EDITOR_OPERATED
   Scene / GameObject / script等を操作できた

L2 PLAYABLE
   Play Modeで最低限遊べた

L3 VERIFIED
   console / test / build等の検証を通した

L4 SUSTAINED
   複数feature・複数sessionを跨ぐ開発を継続できた

L5 RUNTIME_COMPLETED
   公開物・実機・外部player等、最終利用環境まで確認した
```

`MCP tool returned success`はL1ですらありません。単なるtransport / operation successです。

---

## 14件を先に一覧する

| 日付 | 実例 | 到達 | 人間介入 | 観測された境界 |
| --- | --- | --- | --- | --- |
| 2/19 | Unity MCP vs CoPlayでブロック崩し | L2 | bug修正あり | MCP実装による差が大きい |
| 2/24 | uLoopMCPで2D→3Dブロック崩し | L2〜L3 | 動作確認・修正指示 | 観測→修正loopが効く |
| 2/28 | Unity 6 + Codexでヴァンサバ系 | L2 | 接続・画面・初期化を復旧 | Connected ≠ operable |
| 3/8 | Unity公式MCPでTPS scene改造 | L1 | 人間がPlay確認 | object生成 ≠ usable space |
| 3/11 | CatchGame全自動生成 | L2 | 公開記録上は小さい | 単純gameは自然言語から成立 |
| 3/13 | 2D game 3テーマ比較 | L2〜L3 | 最終playで人間が欠陥発見 | self-test ≠ playability |
| 3/22 | 企画→WebGL公開workflow | 運用設計 | phase間で承認 | completion contractが重要 |
| 4/5 | Claude Code→Codexでgame改修・build | L2 + build | setupと操作性調整 | draft生成には有効 |
| 4/11 | 神経衰弱 + Unity CLI Loop | L2 | 別観測toolを追加 | generationよりobservationが重要 |
| 4/17 | マグネットスイーパー移植 | L2未満〜L2 | UI等の追加修正必要 | 自動実装しても未完成 |
| 5/7 | 既存3D projectのbug / shader / VFX | task依存 | 目視評価 | bug fix強、art/VFX不安定 |
| 6/20 | Codexで3D鬼ごっこ + tests | L3 | cameraを追加修正 | test条件を先に渡すと強い |
| 6/24 | Unity公式MCPでRoll-a-Ball | L2 | 追加prompt | tutorial規模は短時間で成立 |
| 7/5〜9 | 『昭和サバイバル』継続開発 | L4 | balance・debug・判断を人間が担当 | 長期開発可能、完成判断は人間 |

ここで重要なのは、L2が多数あることでも、L5がほぼ見当たらないことでもありません。

**taskの複雑さが上がるほど、agentの「観測方法」と人間の「完成基準」が支配的になる**ことです。

---

# 1. 2月19日：同じブロック崩しで3時間と1時間

増田恭隆氏は、同じブロック崩しをUnity側のMCP系とCoPlay MCPで比較しています。前者は実装約3時間、CoPlay側は約1時間で、人間が手を入れたのは4箇所のbug修正だったと報告しています。

### 直接引用

> 「実質的な実装時間は3時間。率直な感想は『使い物にならない』。」

— 増田恭隆「Unity本家のAI参入と、これまでのUnityでのノーコード検証」2026-02-19  
https://note.com/yasutaka_masuda/n/n74397dbf2abf

同じ作者・同じ題材でも、MCP側のEditor abstractionを変えるだけで体験が大きく変わりました。

**本記事の判断:** 「Unity MCP」というカテゴリ名だけで性能を語れません。modelだけでなく、agentへどのUnity操作をどう見せるかが結果を左右します。

---

# 2. 2月24日：2Dから3Dへ。強かったのは生成より観測

uLoopMCPをClaude Codeから使った検証では、白紙projectから数字付きブロック崩しを作り、2D版から3D版へ拡張しています。記事では2D/3D合計18 scripts、Scene構築、compile、動作確認、testまでのloopが報告されています。

### 直接引用

> 「雑なプロンプトでも、一発目で出てきたものは土台がほぼできていました。」

— unsoluble_sugar「uLoopMCP × Claude Code、AI駆動でUnityゲーム開発がどこまで自走できるか試してみた」2026-02-24  
https://zenn.dev/unsoluble_sugar/articles/cd8d59be7b8f85

3D化では壁へのめり込みや反射不良があり、人間が動作確認しながら修正を投げています。一方、Hierarchy取得、capture、test結果取得があるため、AI自身も失敗を観測して修正できます。

**本記事の判断:** Unity agentの価値は「C#を生成すること」より、`Editor state → observation → repair`を閉ループ化することにあります。

---

# 3. 2月28日：「Connected」でも操作できない

よなよな@AIゲーム開発氏は、Unity 6 + Codex + MCPでVampire Survivors系gameを作る過程を記録しています。

Unity側はConnectedでも、Codex側ではproject一覧を取得できず操作不能という状態が発生。process整理、再接続、Main Camera消失、初期化順序、freeze、UI責務の重複などを潰し、最終的に遊べる状態へ進めています。

### 直接引用

> 「Connected表示だけでは判断できないということです。」

— よなよな@AIゲーム開発「Unity 6 × Codex × MCPで『30分ヴァンサバ』を作るつもりが、白画面から始まった話」2026-02-28  
https://note.com/yonayona_ai_game/n/nb1ec6a528bbd

**本記事の判断:** MCP connection healthはproduct completionとは別の監視対象です。`Connected`をacceptance testにしてはいけません。

---

# 4. 3月8日：12 objectを作れても、部屋には入れない

DevelopersIOはUnity公式MCP `com.unity.ai.assistant 2.0.0-pre.1`とClaude Code / Claude Opus 4.6でTPS templateを改造しています。

AIは壁、床、天井、doorway、柱、高台、slopeの計12 objectを生成しました。しかしPlay Modeで確認すると、既存壁がdoorwayを塞ぎ、部屋へ侵入できませんでした。内部light不足、scale不整合、material不統一、Static Editor Flags未設定も確認されています。

### 直接引用

> 「ドアウェイの位置に既存の壁が存在しており、部屋に侵入できませんでした。」

— 越井琢巳「Unity MCP で TPS ゲームを Claude Code に改造させたら何が起きたか」2026-03-08  
https://dev.classmethod.jp/articles/unity-mcp-tps-game-claude-code-modification/

AIは外部4視点をcaptureしていましたが、部屋内部へcameraを入れていませんでした。

```text
geometry generated: PASS
human traversal: FAIL
```

**本記事の判断:** screenshotを撮った回数ではなく、**何を観測したか**が重要です。

---

# 5. 3月11日：自然言語だけでCatchGameを全自動生成

miya氏はUnity MCPのAssistant windowからCodexを使い、簡単なcasual game「CatchGame」を自然言語のみで全自動開発したと報告しています。

### 直接引用

> 「自然言語の指示のみで全自動開発しました。」

— miya「〖UnityMCP〗簡単なUnityゲームを全自動で実装させました。」2026-03-11  
https://note.com/miya19/n/n4503e377dc45

記事には生成過程、play、生成codeのvideo timelineがあります。

**本記事の判断:** tutorial / casual game規模でL2 PLAYABLEへ到達すること自体は、もはや珍しい反例ではありません。ただし、この証拠からAAAやproduction qualityへ一般化はできません。

---

# 6. 3月13日：7回test、5件自己修正。それでも最初の部屋から出られない

この14件の中で、実運用の限界を最も分かりやすく示す事例です。

DevelopersIOはUnity MCP + Claude Code / Opus 4.6で、弾幕shooting、athletics、探索型dungeonの3テーマを比較しました。

単純な前2つは約7.5分、9分で初回出力から成立。複雑なdungeonは約49分で、Claude Codeは7回Play Mode testを実行し、5件を自己修正しました。

しかし人間が実際にplayすると、初期jumpでは出口へ届かず、最初の部屋から出られませんでした。

### 直接引用

> 「スタート部屋から出られませんでした。」

— 越井琢巳「Unity MCP × Claude Code に 2D ゲームの弾幕処理・アスレチック生成・ダンジョン生成をさせて破綻するかどうか観察してみた」2026-03-13  
https://dev.classmethod.jp/articles/unity-mcp-claude-code-2d-game-verification/

原因はtest oracleです。agentはplayerをMCP経由でwarpさせて各部屋を検査していました。

```text
state consistency: PASS
actual traversal: FAIL
```

**本記事の判断:** 自律test loopそのものは価値があります。しかし、間違ったoracleを高速に回すと「何度も検証した未完成品」ができます。

---

# 7. 3月22日：強い人は「AIに任せる」のではなくworkflowを固定した

umezu_y氏はCoplayDev/unity-mcp + Claude Code向けに`hcg-workflows`を公開し、Phase 0〜8として接続確認、企画、機能仕様、技術仕様、test仕様、task list、実装、検証、releaseまでを分離しています。

実装では1 task 1 commitとし、test、console、Play Mode確認を通してからcommitする構造です。

### 直接引用

> 「仕様がないと AI は『なんとなくそれっぽいもの』を作ってしまい、手戻りが大きくなります。」

— umezu_y「Claude Code × unity-mcp でゲーム開発の企画→公開をワークフロー化した話」2026年3月公開  
https://qiita.com/umezu_y/items/090a0fd25f9f915ad375

**本記事の判断:** model intelligenceよりcompletion contractを強くする方が、production workflowでは再現性を上げやすいです。

---

# 8. 4月5日：雑な指示からgameを作り、Codexでbuildまで進める

四駒アイ氏はWindows 11 / Unity 6.4 / Cursor環境でClaude CodeとCodexの両方からUnity MCPを利用しています。

Claude Code側の設定場所へ辿り着くまで1〜2時間かかった一方、接続後はかなり雑な指示からgameを生成。そのprojectをCodexから修正し、buildで機能追加しています。

### 直接引用

> 「ゲーム完成です。」

— 四駒アイ「2026/4/5 UnityのMCPサーバ設定をしてみる in Cursor」2026-04-05  
https://note.com/4komaai/n/nafd4090dc068

ただし同じ記事で作者は、まだ改善余地があり「叩き台としては良さそう」と評価しています。

**本記事の判断:** 「完成」という単語だけを抜き出すと過大評価になります。同一記事の留保まで読む必要があります。

---

# 9. 4月11日：生成したら大量error。観測toolを足すと遊べた

ティー氏はCoplayDev/unity-mcpに「簡単な神経衰弱」を依頼しました。一見完成したものの、Playすると大量のerrorが出ました。

そこでUnity CLI Loop（旧uLoopMCP）を追加し、Play Modeとerror確認を使ったdebugを依頼すると、問題なく遊べる状態まで修正できたと報告しています。

### 直接引用

> 「いざプレイしてみるとエラーが大量に出力されてしまいました。」

— ティー「Unityに関するMCPを実際に入れてみた所感」2026-04-11  
https://note.com/mindpower/n/nba514492f5a5

**本記事の判断:** generation capabilityを足したのではなく、observation / repair capabilityを足したことでL1からL2へ進んだ点が重要です。

---

# 10. 4月17日：全自動移植できても「未完成」

miya氏は既存game「マグネットスイーパー」をUnityへ全自動移植しています。game自体は自動実装されましたが、UI等の修正が必要でした。

### 直接引用

> 「ゲームとしてはまだまだ未完成でUIの修正などが必要な状態」

— miya「〖UnityMCP〗マグネットスイーパーの移植を試しました。」2026-04-17  
https://note.com/miya19/n/n8df417077cb0

**本記事の判断:** 「自動実装」と「完成」は同義ではありません。この区別を作者自身が明記している点が重要です。

---

# 11. 5月7日：bug fixは成功、shader / VFXは失敗

株式会社ユニスポットはClaude Code + Unity MCPで既存3D projectを検証しています。

VRM characterのanimation不具合では、既存official controllerを参照して構造を確認し、script作成・attachまで行い、正常なanimationへ到達しました。

一方、shader調整は複数回試しても期待した変化が出ず失敗。Visual Effect Graphは約30分処理し、5時間枠のtoken容量の約50%を消費したものの、Output nodeが途中で止まり動作しませんでした。

### 直接引用

> 「『既存の処理や不具合の修正』はかなり得意」

— 株式会社ユニスポット「本当にゲーム開発もAIで出来る?『Claude Code + Unity MCP』でどこまで出来るか試してみた。」2026-05-07  
https://www.uni-spot.com/blog_post/claude-unity-mcp/

**本記事の判断:** Unity MCPを一つのscoreで評価するのは雑です。task classで分けるべきです。

```text
existing bug fix    → strong
structured editing  → strong
art direction       → variable
complex VFX graph   → high-cost / unstable
```

---

# 12. 6月20日：3D鬼ごっこ + EditMode 4件 + PlayMode 3件が全PASS

zuqqhi2氏はCoplayDev版unity-mcp + Codexで最小限の3D鬼ごっこを作らせ、promptの時点でEditMode / PlayMode test作成も要求しています。

生成後、Unity Test RunnerでEditMode 4件、PlayMode 3件がすべてPASS。cameraがstage上部を切っていた問題は追加指示で修正されています。

### 直接引用

> 「EditModeをみると、ちゃんと4つテストケースがあって全部通りますね。」

— zuqqhi2「CoplayDev 版 unity-mcp を使用して Codex に Unity を操作させてテスト込みの開発をさせる」2026-06-20  
https://zuqqhi2.com/coplaydev-unity-mcp-codex-game-dev

**本記事の判断:** completion conditionを最初からpromptに含めると、単なる「動いた」より強いevidenceを作れます。ただしcamera問題が残ったことから、test coverageと視覚品質は別です。

---

# 13. 6月24日：Roll-a-Ballは約10分でerrorなくplayable

花王株式会社のTsuchiyaK氏はUnity公式MCP Server + Claude CodeでUnity入門のRoll-a-Ballを作らせています。

作業開始から約10分後、実際にPlayでき、さらに「ホラーゲームっぽくして」という追加promptから約5分でlighting、post process、enemy、game over等が追加されています。

### 直接引用

> 「エラーなくプレイできるゲームができあがりました。」

— TsuchiyaK「Unity AI × Claude Code でゲームを作ってみた」2026-06-24  
https://qiita.com/TsuchiyaK/items/a3de1ac034bf94cf905b

**本記事の判断:** tutorial規模・既知patternのgameでは、自然言語→playableまでの摩擦はかなり小さくなっています。

---

# 14. 7月：複数stageのgameを完成まで継続開発した例

「小さいdemoしか作れないのでは？」への強い反例が、bunnoneta氏の『昭和サバイバル』です。

2026年7月5日の開発記では全6stageの完成を報告。続く完結記事では、Unity MCPを使いながらbalance調整、bug修正、gamepad対応、演出等を進め、game一本を完成させた経験がまとめられています。

### 直接引用

> 「ついに全6ステージが完成しました。」

— bunnoneta「〖開発記〗Unity製サバイバルゲーム『昭和サバイバル』全6ステージ完成までにClaudeと乗り越えた壁」2026-07-05  
https://note.com/bunnoneta/n/ndd6c132b1abf

ここは成功例だからこそ重要です。

同じ開発記録には、

- full pathの型名が必要になる場面
- `EditorUtility.SetDirty()`を呼ばず変更が保存されない場面
- Prefab保存忘れ
- C#構文差
- 改行差による置換失敗
- compile / domain reload待ち
- freeze原因調査用の`HangWatchdog`作成

が記録されています。

完結記事で作者は、最終的な「面白いかどうか」の判断を人間側に残しています。

**本記事の判断:** L4 SUSTAINEDは実例があります。しかし、その実態は「AIが一発で完成させた」ではなく、**生成→観測→failure発見→修正→再検証を人間とAIで何度も回した**ものです。

---

## 14件から見えるtask class別の現在地

| task class | 観測 | 2026年8月時点の判断 |
| --- | --- | --- |
| GameObject / Scene生成 | 多数の成功例 | 実用域 |
| script生成・attach | 多数の成功例 | 実用域 |
| tutorial / casual prototype | 10分前後の例もある | 実用域 |
| 既存bug調査・修正 | animation等で成功 | 強い |
| console-driven repair | 成功例複数 | 強い |
| EditMode / PlayMode tests | 全PASS例あり | 有効。ただしcoverage依存 |
| build | 実例あり | 利用可能 |
| 複雑なprogression | self-test後も詰み例 | 人間play必須 |
| visual consistency | 見落とし例あり | 人間レビュー必須 |
| art direction | 成功・失敗が混在 | 不安定 |
| shader / VFX | 高コスト失敗例 | まだ不安定 |
| connection lifecycle | Connectedでも失敗例 | 運用監視が必要 |
| 長期game development | 全6stage完成例 | 可能 |
| 外部playerの面白さ | 強い自動評価証拠なし | 人間 / player側 |

この表から見える境界は、code / editor operationとexperience evaluationの間です。

---

## 一番重要な発見：AIの弱点は「操作」より「oracle」

2026年の事例を読む前は、Unity MCPの問題は「AIがEditorを上手く触れないこと」だと思いやすいです。

しかし14件を並べると、より深い問題が見えます。

```text
AIが操作できない
```

より、

```text
AIが何を確認すべきかを間違える
```

方がproductionでは危険です。

3月13日のdungeonでは7回testしています。それでもplayer traversalをtestしていなかった。

3月8日のTPSでは4視点captureしています。それでも部屋内部を見なかった。

6月20日の鬼ごっこではtestsは全PASSしました。それでもcamera framingは人間が追加修正しています。

つまり、

```text
more tool calls
more tests
more screenshots
```

だけでは完成へ近づきません。

必要なのは、**正しいcompletion oracle**です。

---

## 研究側の結果も「repair loopが本体」という読み方と整合する

2026年7月公開のpreprintでは、MCPとは異なるsingle-pass条件でUnity C# scene生成を評価しています。

4つのopen-weight model、26 goal patterns、合計10,400 generationsを評価し、single-passでrunnable sceneまでcompileしたものは0件と報告されています。

https://arxiv.org/abs/2607.10187

これはUnity MCPの成功率ではありません。条件が違うので直接比較は禁止です。

ただし、公開実例の多くが

```text
generate
→ compile
→ observe
→ repair
→ play
→ observe again
```

を使っていることとは整合します。

**一発生成能力より、失敗から戻れる閉ループの方が現在の実用性を説明しやすい**、というのが本記事の解釈です。

---

## 2026年5月、Unity自身もMCPを公式toolchainへ入れた

Unityは2026年5月5日、Unity 6.0以降向けAI toolsをopen betaとして公開し、その構成要素に公式MCP Serverを含めています。

公式一次情報:
https://unity.com/blog/unity-ai-how-to-get-started
https://unity.com/blog/unity-ai-mcp-how-to-get-started

Unity公式MCP Serverは、scene state、GameObjects、components、console logs等を外部AI agentから扱えるintegration pathとして案内されています。

一方、Unity自身もopen betaについて、features、behavior、availabilityが変更・制限・終了され得ると明記しています。

つまり2026年2月と8月では、同じ「Unity MCP」という言葉でも測っているsoftware versionが違います。

このversion driftがあるため、この記事でも過去の失敗を「現在も必ず再現するbug」とは扱いません。

---

## 自分たちの`image2outfit`も、まだ成功例には数えない

`KAFKA2306/image2outfit`のDraft PR #212では、local Blender + Unity MCP supportを実装しています。

https://github.com/KAFKA2306/image2outfit/pull/212

しかしPRでは、次が明示的に`NOT_RUN`です。

- user Windows環境でのPowerShell setup
- live Blender MCP connection
- live Unity MCP connection / package resolution
- Blender Assistant → Codex → MCP end-to-end call

したがって現在言えるのは、

```text
integration code exists
static contract exists
```

までです。

```text
live E2E passed
VRChat runtime completed
```

とは言いません。

外部事例にcompletion boundaryを要求するなら、自分たちにも同じ基準を適用します。

---

## 導入するなら、MCPをcompletion gateにしない

2026年の実例から、現実的な構造はこれです。

```text
Codex / Claude Code
        ↓
Unity MCP
        ↓
Unity Editor
        ↓
compile / console
        ↓
EditMode / PlayMode tests
        ↓
actual player traversal
        ↓
visual review
        ↓
build
        ↓
actual runtime / external user
```

最低でもstateを分けます。

```text
TOOL_SUCCESS
EDITOR_VALIDATED
PLAYABLE_VALIDATED
BUILD_VALIDATED
RUNTIME_COMPLETED
```

例えば、

```json
{
  "tool_success": true,
  "editor_validated": true,
  "playable_validated": false,
  "runtime_completed": false,
  "reason": "NOT_RUN"
}
```

ならcompletedではありません。

---

## 読者別：2026年8月に導入する価値はあるか

### Unity初心者

**価値あり。ただしAIの出力を正解教材にしない。**

Roll-a-Ballやcasual gameのような小規模prototypeはかなり作りやすくなっています。一方、Unity固有のlifecycle、Prefab、serialization、physicsを知らないと、AIの偽成功を見抜きにくいです。

### Unity engineer

**かなり価値あり。特に反復作業、既存bug、test、variant生成。**

人間側がarchitectureとacceptance criteriaを持てるため、最も恩恵を受けやすい層です。

### game designer / planner

**prototype速度には価値あり。完成判断は握り続ける。**

「面白い」「難しい」「見づらい」は機械testだけでは決まりません。

### production team

**導入するならversion pin、logs、test、human reviewを前提にする。**

MCPをproduction gateにせず、authoring adapterとして扱う方が安全です。

---

## 結論

14件を調べて、一番重要だったのは「Unity MCPはすごい」という話でも「まだ使えない」という話でもありませんでした。

2026年の公開実例からは、すでに

```text
Sceneを作る
scriptを書く
Playする
errorを読む
testする
直す
buildする
長期開発を続ける
```

ところまで到達しています。

だから、

> Unity MCPは実用になったのか？

への答えは、かなりの範囲で**Yes**です。

しかし、

> Unity MCPに完成を任せられるのか？

への答えは、まだ別です。

3月13日のdungeonは、7回testして5件直しても最初の部屋から出られませんでした。

7月の完成例は、AIが魔法のように一発生成したものではなく、人間がbalance、体験、failure、completionを見続けたから完成しています。

したがって2026年8月時点の最も実務的な結論はこれです。

**Unity MCPは「使えるか？」の段階を越えた。次の問題は、AIに何を操作させるかではなく、何を証拠に完成と判定するかである。**

---

## 参照した2026年実運用記録・一次情報

1. 増田恭隆「Unity本家のAI参入と、これまでのUnityでのノーコード検証」  
https://note.com/yasutaka_masuda/n/n74397dbf2abf

2. unsoluble_sugar「uLoopMCP × Claude Code、AI駆動でUnityゲーム開発がどこまで自走できるか試してみた」  
https://zenn.dev/unsoluble_sugar/articles/cd8d59be7b8f85

3. よなよな@AIゲーム開発「Unity 6 × Codex × MCPで『30分ヴァンサバ』を作るつもりが、白画面から始まった話」  
https://note.com/yonayona_ai_game/n/nb1ec6a528bbd

4. DevelopersIO「Unity MCP で TPS ゲームを Claude Code に改造させたら何が起きたか」  
https://dev.classmethod.jp/articles/unity-mcp-tps-game-claude-code-modification/

5. miya「〖UnityMCP〗簡単なUnityゲームを全自動で実装させました。」  
https://note.com/miya19/n/n4503e377dc45

6. DevelopersIO「Unity MCP × Claude Code に 2D ゲームの弾幕処理・アスレチック生成・ダンジョン生成をさせて破綻するかどうか観察してみた」  
https://dev.classmethod.jp/articles/unity-mcp-claude-code-2d-game-verification/

7. umezu_y「Claude Code × unity-mcp でゲーム開発の企画→公開をワークフロー化した話」  
https://qiita.com/umezu_y/items/090a0fd25f9f915ad375

8. 四駒アイ「2026/4/5 UnityのMCPサーバ設定をしてみる in Cursor」  
https://note.com/4komaai/n/nafd4090dc068

9. ティー「Unityに関するMCPを実際に入れてみた所感」  
https://note.com/mindpower/n/nba514492f5a5

10. miya「〖UnityMCP〗マグネットスイーパーの移植を試しました。」  
https://note.com/miya19/n/n8df417077cb0

11. 株式会社ユニスポット「本当にゲーム開発もAIで出来る?『Claude Code + Unity MCP』でどこまで出来るか試してみた。」  
https://www.uni-spot.com/blog_post/claude-unity-mcp/

12. zuqqhi2「CoplayDev 版 unity-mcp を使用して Codex に Unity を操作させてテスト込みの開発をさせる」  
https://zuqqhi2.com/coplaydev-unity-mcp-codex-game-dev

13. TsuchiyaK「Unity AI × Claude Code でゲームを作ってみた」  
https://qiita.com/TsuchiyaK/items/a3de1ac034bf94cf905b

14. bunnoneta「〖開発記〗Unity製サバイバルゲーム『昭和サバイバル』全6ステージ完成までにClaudeと乗り越えた壁」  
https://note.com/bunnoneta/n/ndd6c132b1abf

補助資料:

- bunnoneta「〖開発記③・完結〗AIと二人三脚で作ったゲーム『昭和サバイバル』、ついに完成しました」  
https://note.com/bunnoneta/n/n91bbcd3fd700
- Unity公式「Unity's AI tools in beta: How to get started」  
https://unity.com/blog/unity-ai-how-to-get-started
- Unity公式「Unity AI open beta: How to get started with MCP」  
https://unity.com/blog/unity-ai-mcp-how-to-get-started
- Unity公式「MCP servers in game development explained」  
https://unity.com/blog/mcp-servers-game-development
- CoplayDev/unity-mcp  
https://github.com/CoplayDev/unity-mcp
- Unity single-pass generation preprint  
https://arxiv.org/abs/2607.10187
- image2outfit Draft PR #212  
https://github.com/KAFKA2306/image2outfit/pull/212
