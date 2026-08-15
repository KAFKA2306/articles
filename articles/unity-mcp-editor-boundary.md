---
title: "2026年、Unity MCPはどこまで実用になったのか――14件の公開実例と自前repoで見る完成境界"
emoji: "🛠️"
type: "tech"
topics: ["unity", "mcp", "codex", "claudecode", "ai"]
published: false
published_at: 2026-08-12 16:03
---

# 2026年、Unity MCPはどこまで実用になったのか――14件の公開実例と自前repoで見る完成境界

「AIがUnity Editorを操作できる」は、もう面白デモだけの話ではありません。

2026年には、自然言語から数分〜十数分で小さなゲームを作った例、既存projectのbugを直した例、EditMode / PlayMode testまで通した例、複数sessionにまたがって一本のゲームを完成させた例まで公開されています。

一方で、49分かけて7回自己テストし5件を自己修正したのに、実際のplayerは最初の部屋から出られなかった例があります。Visual Effect Graphに長時間使って完成しなかった例、Editorでは変更されたように見えても保存されなかった例、「Connected」と表示されていても操作不能だった例もあります。

さらに私たち自身のrepoでも、同じ構造の失敗を経験しています。

- `image2outfit`では、Blender MCP + Unity MCP + Codex integrationを実装しても、live Blender / Unity MCP接続とend-to-end callが`NOT_RUN`なら成功とは呼べなかった
- `vrmine`では、84 commits、48 changed files、約4,000 additionsまで進んでも、2-client、late join、owner leave、private uploadを証明できずreleaseは`BLOCKED`のままだった

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

この記事では、2026年8月15日までに公開されたUnity MCP / Unity Editor agentの実運用記録14件を同じ物差しで読み直し、最後に私たち自身のBlender / Unity / VRChat系repoの失敗記録を重ねます。

14件は14人の独立再現ではありません。越井琢巳氏とmiya氏がそれぞれ2件を公開しているため、中心サンプルは**12の発信主体による14事例**です。

結論を先に書きます。

**prototype生成、Scene操作、script実装、既存bug修正、console / testを使った反復修正はすでに実用域です。問題は「AIがUnityを触れるか」から「何を証拠に完成と判定するか」へ移っています。**

---

## 引用と要約のルール

この記事では、外部の実運用記録と筆者の解釈を混ぜません。

- `> 「……」` は原文からの**直接引用**
- 直接引用の直下に、著者名・記事名・公開日・URLを明記
- 引用符を付けていない説明は、原文に基づく**筆者要約**または本記事の分類
- 数字、日付、version、test件数などは元記事または一次情報で確認できたものだけを使用
- 体験談は「その環境で起きた観測」であり、製品全体の成功率には読み替えない
- 私たち自身のrepoについても、Issue / PRに残っている状態とevidenceを根拠にし、未実行を成功へ昇格させない

この記事の「実用域」「不安定」「完成境界」というラベルは引用ではなく、複数事例を比較した本記事の判断です。

---

## これはsystematic reviewではない

対象は次を満たす公開記録を優先しました。

- Unity EditorをAI agent / MCPから実際に操作している
- setup紹介だけで終わらず、Scene、game、test、build、debug等の結果がある
- 成功だけでなく、失敗、修正、人間介入の情報を読み取れる
- 公開日、環境、成果のいずれかを確認できる

note、Zenn、Qiita、DevelopersIO、企業・個人blog、GitHub、Unity公式情報を調査しました。Redditも探索しましたが、中心表では環境・成果物・失敗条件まで追える記録を優先しました。

無作為抽出ではなく、成功体験を公開しやすいselection biasもあります。そのため、

```text
14件中10件成功 → 成功率71%
```

のような数字は出しません。

代わりに、**どのtask classで、どの到達段階まで、どれくらい人間が介入したか**を比較します。

---

## 誰が試したのか――肩書きより「証拠密度」を見る

作者の属性も無視できません。ただし「会社員だから信頼できる」「個人blogだから弱い」とは扱いません。

中心サンプルには、個人開発者、企業技術blog、会社名義の検証、Qiita上の技術記録、長期の個人ゲーム開発記が混在しています。目的もtutorial、既存project修正、game prototype、長期game制作、workflow設計と異なります。

そこで本記事では知名度より、第三者が観測を追跡できるかを重く見ます。

```text
E3  高い証拠密度
    environment / task / 所要時間 / failure / test / screenshot・video・code等が複数ある

E2  中程度
    実際の操作結果と画像・動画はあるが、再現条件やfailure記録が限定的

E1  低い
    感想や完成報告が中心で、環境・検証条件・失敗情報が少ない
```

E3だから主張が正しいという意味ではありません。**何が起きたかを第三者が追いやすい**という意味です。

| 発信の種類 | 本記事での扱い | 信頼性を見るポイント |
| --- | --- | --- |
| 企業技術blog | 実務寄りの検証記録 | 実行条件、失敗、再試行、画像・数値 |
| 個人の長期開発記 | production frictionを見る材料 | 複数日・複数feature、失敗の具体性 |
| 個人の単発検証 | task別の成立可否を見る材料 | prompt、環境、成果物、動画・screenshot |
| workflow / code公開 | 再現可能な運用設計を見る材料 | test、commit、gate、公開code |
| 公式情報 | capability / support範囲の確認 | version、beta status、正式仕様 |

同じ「成功」でも、10分のtutorialと複数sessionの製品開発は同じ重さでは扱いません。

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

| 日付 | 発信主体 | 実例 | 到達 | 証拠密度 | 人間介入 | 観測された境界 |
| --- | --- | --- | --- | --- | --- | --- |
| 2/19 | 増田恭隆 / note | Unity MCP vs CoPlayでブロック崩し | L2 | E2 | bug修正あり | MCP実装による差が大きい |
| 2/24 | unsoluble_sugar / Zenn | uLoopMCPで2D→3Dブロック崩し | L2〜L3 | E3 | 動作確認・修正指示 | 観測→修正loopが効く |
| 2/28 | よなよな@AIゲーム開発 / note | Unity 6 + Codexでヴァンサバ系 | L2 | E3 | 接続・画面・初期化を復旧 | Connected ≠ operable |
| 3/8 | 越井琢巳 / DevelopersIO | Unity公式MCPでTPS scene改造 | L1 | E3 | 人間がPlay確認 | object生成 ≠ usable space |
| 3/11 | miya / note | CatchGame全自動生成 | L2 | E2 | 公開記録上は小さい | 単純gameは自然言語から成立 |
| 3/13 | 越井琢巳 / DevelopersIO | 2D game 3テーマ比較 | L2〜L3 | E3 | 最終playで人間が欠陥発見 | self-test ≠ playability |
| 3/22 | umezu_y / Qiita | 企画→WebGL公開workflow | 運用設計 | E3 | phase間で承認 | completion contractが重要 |
| 4/5 | 四駒アイ / note | Claude Code→Codexでgame改修・build | L2 + build | E2 | setupと操作性調整 | draft生成には有効 |
| 4/11 | ティー / note | 神経衰弱 + Unity CLI Loop | L2 | E2 | 別観測toolを追加 | generationよりobservationが重要 |
| 4/17 | miya / note | マグネットスイーパー移植 | L2未満〜L2 | E2 | UI等の追加修正必要 | 自動実装しても未完成 |
| 5/7 | 株式会社ユニスポット | 既存3D projectのbug / shader / VFX | task依存 | E3 | 目視評価 | bug fix強、art/VFX不安定 |
| 6/20 | zuqqhi2 / 個人blog | Codexで3D鬼ごっこ + tests | L3 | E3 | cameraを追加修正 | test条件を先に渡すと強い |
| 6/24 | TsuchiyaK / Qiita | Unity公式MCPでRoll-a-Ball | L2 | E2 | 追加prompt | tutorial規模は短時間で成立 |
| 7/5〜9 | bunnoneta / note | 『昭和サバイバル』継続開発 | L4 | E3 | balance・debug・判断を人間が担当 | 長期開発可能、完成判断は人間 |

重要なのはL2の件数ではありません。

**taskの複雑さが上がるほど、agentの「観測方法」と人間の「完成基準」が支配的になる**ことです。

---

# 1. 同じブロック崩しでも3時間と1時間

増田恭隆氏は、同じブロック崩しを異なるUnity MCP系で比較しています。前者は実装約3時間、CoPlay側は約1時間で、人間が4箇所のbugを修正したと報告しています。

### 直接引用

> 「実質的な実装時間は3時間。率直な感想は『使い物にならない』。」

— 増田恭隆「Unity本家のAI参入と、これまでのUnityでのノーコード検証」2026-02-19  
https://note.com/yasutaka_masuda/n/n74397dbf2abf

**本記事の判断:** 「Unity MCP」というカテゴリ名だけで性能を語れません。modelだけでなく、agentへUnity操作をどう見せるかが結果を左右します。

---

# 2. 2D→3D化で効いたのは生成より観測

uLoopMCPをClaude Codeから使った検証では、白紙projectから数字付きブロック崩しを作り、2D版から3D版へ拡張しています。3D化では壁へのめり込みや反射不良があり、人間が動作確認しながら修正を投げています。

### 直接引用

> 「雑なプロンプトでも、一発目で出てきたものは土台がほぼできていました。」

— unsoluble_sugar「uLoopMCP × Claude Code、AI駆動でUnityゲーム開発がどこまで自走できるか試してみた」2026-02-24  
https://zenn.dev/unsoluble_sugar/articles/cd8d59be7b8f85

Hierarchy取得、capture、test結果取得があるため、AI自身も失敗を観測して修正できます。

**本記事の判断:** Unity agentの価値は「C#を書くこと」だけではなく、`Editor state → observation → repair`を閉ループ化することにあります。

---

# 3. 「Connected」でも操作できない

よなよな@AIゲーム開発氏は、Unity 6 + Codex + MCPでVampire Survivors系gameを作る過程を記録しています。

Unity側はConnectedでもCodex側からprojectを操作できない状態、Main Camera消失、初期化順序、freeze、UI責務重複などを解消して、最終的に遊べる状態まで進めています。

### 直接引用

> 「Connected表示だけでは判断できないということです。」

— よなよな@AIゲーム開発「Unity 6 × Codex × MCPで『30分ヴァンサバ』を作るつもりが、白画面から始まった話」2026-02-28  
https://note.com/yonayona_ai_game/n/nb1ec6a528bbd

**本記事の判断:** connection healthはproduct completionとは別の監視対象です。

---

# 4. 12 objectを作れても、部屋には入れない

DevelopersIOはUnity公式MCPとClaude Code / Claude Opus 4.6でTPS templateを改造しています。

AIは壁、床、天井、doorway、柱、高台、slopeを生成しました。しかしPlay Modeで確認すると既存壁がdoorwayを塞ぎ、部屋へ侵入できませんでした。内部light不足、scale不整合、material不統一等も残っています。

### 直接引用

> 「ドアウェイの位置に既存の壁が存在しており、部屋に侵入できませんでした。」

— 越井琢巳「Unity MCP で TPS ゲームを Claude Code に改造させたら何が起きたか」2026-03-08  
https://dev.classmethod.jp/articles/unity-mcp-tps-game-claude-code-modification/

AIは外部視点をcaptureしていましたが、playerが実際に部屋へ入れるかを見ていませんでした。

```text
geometry generated: PASS
human traversal: FAIL
```

**本記事の判断:** screenshotの枚数ではなく、**何を観測したか**が重要です。

---

# 5. 自然言語だけでCatchGameを生成

miya氏はUnity MCPのAssistant windowからCodexを使い、簡単なcasual game「CatchGame」を自然言語のみで全自動開発したと報告しています。

### 直接引用

> 「自然言語の指示のみで全自動開発しました。」

— miya「〖UnityMCP〗簡単なUnityゲームを全自動で実装させました。」2026-03-11  
https://note.com/miya19/n/n4503e377dc45

記事には生成過程、play、生成codeのvideo timelineがあります。

**本記事の判断:** tutorial / casual game規模でL2 PLAYABLEへ到達すること自体は、すでに珍しい成功ではありません。ただしproduction qualityへ一般化はできません。

---

# 6. 7回test、5件自己修正。それでも最初の部屋から出られない

この14件の中で、completion oracleの重要性を最も分かりやすく示す事例です。

DevelopersIOは弾幕shooting、athletics、探索型dungeonの3テーマを比較しました。単純な前2つは短時間で成立しましたが、複雑なdungeonは約49分。Claude Codeは7回Play Mode testを実行し、5件を自己修正しました。

しかし人間がplayすると、初期jumpでは出口へ届かず、最初の部屋から出られませんでした。

### 直接引用

> 「スタート部屋から出られませんでした。」

— 越井琢巳「Unity MCP × Claude Code に 2D ゲームの弾幕処理・アスレチック生成・ダンジョン生成をさせて破綻するかどうか観察してみた」2026-03-13  
https://dev.classmethod.jp/articles/unity-mcp-claude-code-2d-game-verification/

agentはplayerをMCP経由でwarpさせて各部屋を検査していました。

```text
state consistency: PASS
actual traversal: FAIL
```

**本記事の判断:** 間違ったoracleを高速に回すと、「何度も検証した未完成品」ができます。

---

# 7. 強いworkflowは「AIに任せる」よりcompletion contractを固定する

umezu_y氏はCoplayDev/unity-mcp + Claude Code向けworkflowを公開し、接続確認、企画、仕様、test仕様、task list、実装、検証、releaseを分離しています。

### 直接引用

> 「仕様がないと AI は『なんとなくそれっぽいもの』を作ってしまい、手戻りが大きくなります。」

— umezu_y「Claude Code × unity-mcp でゲーム開発の企画→公開をワークフロー化した話」2026年3月  
https://qiita.com/umezu_y/items/090a0fd25f9f915ad375

**本記事の判断:** productionではmodel intelligenceを期待するだけより、completion contractを強くする方が再現性を上げやすいです。

---

# 8. 雑な指示からgameを作れても、setupには1〜2時間かかった

四駒アイ氏はWindows 11 / Unity 6.4 / Cursor環境でClaude CodeとCodexの両方からUnity MCPを利用しています。

接続設定へ辿り着くまで1〜2時間かかった一方、接続後はかなり雑な指示からgameを生成し、Codexから修正・buildまで進めています。

### 直接引用

> 「ゲーム完成です。」

— 四駒アイ「2026/4/5 UnityのMCPサーバ設定をしてみる in Cursor」2026-04-05  
https://note.com/4komaai/n/nafd4090dc068

同じ記事で作者は「叩き台」としての評価も残しています。

**本記事の判断:** 「完成」という一語だけを抜き出さず、同じ記事の留保まで読む必要があります。

---

# 9. 生成したら大量error。観測toolを足すと遊べた

ティー氏はCoplayDev/unity-mcpに神経衰弱を依頼しました。一見完成したものの、Playすると大量errorが発生。その後Unity CLI Loopを追加してPlay Modeとerrorを観測させ、遊べる状態まで修正しています。

### 直接引用

> 「いざプレイしてみるとエラーが大量に出力されてしまいました。」

— ティー「Unityに関するMCPを実際に入れてみた所感」2026-04-11  
https://note.com/mindpower/n/nba514492f5a5

**本記事の判断:** generation能力ではなく、observation / repair能力を足したことが効いています。

---

# 10. 全自動移植できても作者自身が「未完成」と評価

miya氏は既存game「マグネットスイーパー」をUnityへ全自動移植しています。実装自体は進みましたが、UI等の修正が必要でした。

### 直接引用

> 「ゲームとしてはまだまだ未完成でUIの修正などが必要な状態」

— miya「〖UnityMCP〗マグネットスイーパーの移植を試しました。」2026-04-17  
https://note.com/miya19/n/n8df417077cb0

**本記事の判断:** 「自動実装」と「完成」は同義ではありません。

---

# 11. 既存bug fixは強い。shader / VFXは不安定

株式会社ユニスポットはClaude Code + Unity MCPで既存3D projectを検証しています。

VRM characterのanimation不具合では修正へ到達した一方、shader調整は期待した変化が出ず、Visual Effect Graphも長時間処理したものの完成しませんでした。

### 直接引用

> 「『既存の処理や不具合の修正』はかなり得意」

— 株式会社ユニスポット「本当にゲーム開発もAIで出来る?『Claude Code + Unity MCP』でどこまで出来るか試してみた。」2026-05-07  
https://www.uni-spot.com/blog_post/claude-unity-mcp/

```text
existing bug fix    → strong
structured editing  → strong
art direction       → variable
complex VFX graph   → high-cost / unstable
```

**本記事の判断:** Unity MCPを一つのscoreで評価するのは雑です。task classで分けるべきです。

---

# 12. EditMode 4件 + PlayMode 3件が全PASS

zuqqhi2氏はCoplayDev版unity-mcp + Codexで最小限の3D鬼ごっこを作らせ、promptの時点でEditMode / PlayMode test作成も要求しています。

生成後、EditMode 4件、PlayMode 3件がすべてPASSしました。一方、camera framingは追加修正が必要でした。

### 直接引用

> 「EditModeをみると、ちゃんと4つテストケースがあって全部通りますね。」

— zuqqhi2「CoplayDev 版 unity-mcp を使用して Codex に Unity を操作させてテスト込みの開発をさせる」2026-06-20  
https://zuqqhi2.com/coplaydev-unity-mcp-codex-game-dev

**本記事の判断:** completion conditionをpromptに含めるのは有効です。ただしtest coverageと視覚品質は別です。

---

# 13. Roll-a-Ballは約10分でplayable

花王株式会社のTsuchiyaK氏はUnity公式MCP Server + Claude CodeでRoll-a-Ballを作らせています。作業開始から約10分でPlayでき、その後の追加promptで演出やenemy等を追加しています。

### 直接引用

> 「エラーなくプレイできるゲームができあがりました。」

— TsuchiyaK「Unity AI × Claude Code でゲームを作ってみた」2026-06-24  
https://qiita.com/TsuchiyaK/items/a3de1ac034bf94cf905b

**本記事の判断:** tutorial規模・既知patternでは、自然言語→playableまでの摩擦はかなり小さくなっています。

---

# 14. 全6stageのgameを継続開発した例

「小さいdemoしか作れないのでは？」への強い反例が、bunnoneta氏の『昭和サバイバル』です。

Unity MCPを使いながらbalance調整、bug修正、gamepad対応、演出等を進め、全6stageまで継続開発しています。

### 直接引用

> 「ついに全6ステージが完成しました。」

— bunnoneta「〖開発記〗Unity製サバイバルゲーム『昭和サバイバル』全6ステージ完成までにClaudeと乗り越えた壁」2026-07-05  
https://note.com/bunnoneta/n/ndd6c132b1abf

同じ開発記録には、型解決、`EditorUtility.SetDirty()`、Prefab保存、C# version差、改行差、compile/domain reload待ち、freeze調査など、Unity実運用特有のfrictionが多数記録されています。

**本記事の判断:** L4 SUSTAINEDは実例があります。ただしその実態は一発生成ではなく、**生成→観測→failure発見→修正→再検証**です。

補助:
https://note.com/bunnoneta/n/n91bbcd3fd700

---

# 私たち自身のrepoを同じ物差しで見る

外部事例だけなら、「他人はそうだった」で終わります。

当初は自前の失敗を5例に分けていましたが、記事の論点を最もよく示す**2と5の2例だけ**に集約します。

- `image2outfit`: integration codeとstatic contractが揃っても、live MCP E2Eが未実行ならoperation成功ではない
- `vrmine`: verificationを作り込んでも、real multi-client evidenceまで閉じなければruntime completionではない

---

## 自前失敗例2：MCP integrationを実装しても、live E2Eが`NOT_RUN`なら成功ではない

`KAFKA2306/image2outfit` PR #212では、Blender MCP + Unity MCP + Codex integrationを実装しました。

PR #212:
https://github.com/KAFKA2306/image2outfit/pull/212

PRには、Windows setup entry point、version pin、localhost限定、doctor command、Blender-side Assistant UI、static tests等が入り、9 files / 859 additionsまで進んでいます。

しかしPR自身が次を`NOT_RUN`としています。

- local Windows PowerShell setup
- live Blender MCP connection
- live Unity MCP connection / package resolution
- Blender Assistant → Codex → MCP end-to-end call

PRはDraftのままです。

```text
integration code exists
static contract exists
        ↓
live editor operation: NOT_RUN
```

この例で問題なのは、設定やadapterを書くことに失敗した点ではありません。むしろstatic integrationはかなり進んでいます。

失敗したのは、**「実装した」ことを「実際のEditorで動いた」ことへ昇格できる証拠がまだない**点です。

外部の「Connected表示でも操作不能だった」事例と同じく、connection/configurationの存在とactual operationは別のstateです。

**感想:** MCPを扱う側ほど、「設定ファイルがある」「toolが登録されている」「CIが通った」をoperation successと錯覚しやすい。live callを実行して、その結果を再観測するまで成功とは呼ばない方が安全です。

---

## 自前失敗例5：`vrmine`――約4,000行追加しても、releaseはBLOCKEDだった

`KAFKA2306/vrmine`は、この記事に最も近い**runtime completion failure**です。

PR #18:
https://github.com/KAFKA2306/vrmine/pull/18

このPRはRULEFORGE、ECHO MINE、CHESSの3ゲームworldをrelease-gatedにする大きな変更です。現在でも、

- 84 commits
- 48 changed files
- +3,989 / -338
- three-game implementation
- two-client verification logic
- static repository integrity CI
- fail-closed upload-readiness gate
- GitHub Pages landing page

まで実装されています。

それでもPRは**open / Draft**で、release statusは明示的に`BLOCKED`です。

理由は単なる慎重さではありません。PR本文には、以前のG3について次の事実が記録されています。

- previous G3はfailed
- 旧実装はclient evidenceがなくてもPASSを書ける経路があった
- recent run同士のevidenceを混ぜ得た
- そのため過去のG1/G2/G3 evidenceをinvalidatedした

つまり、ここでは実際に

```text
verification implementation exists
report can say PASS
```

と

```text
current runの2-client runtimeを本当に証明した
```

が一致していませんでした。

release blocker Issue #19もopenです。

https://github.com/KAFKA2306/vrmine/issues/19

残っているのは、たとえば次です。

- exact Unity 2022.3.22f1 / Worlds SDK 3.10.4でcompile
- G1 / G2
- two-client Build & Test
- 同一`RunToken`で2 distinct player IDsを確認
- ownership transfer / republish / restoration
- G4 upload readiness
- private world upload
- delayed second-account join
- late-join state restoration
- current owner leave
- RULEFORGE 3P/4P/5P
- ECHO MINE 2P/3P/4P/5P
- CHESSの各runtime path

Issue #43では、multi-client、late join、owner leave、PC/Questを独立したregression matrixとして残しています。

https://github.com/KAFKA2306/vrmine/issues/43

さらに2026年8月には、それらをU1〜U4へ分解して自動化するEpic #54まで作りました。

https://github.com/KAFKA2306/vrmine/issues/54

```text
U1 package graph
U2 exact Unity compile / EditMode
U3 PlayMode + ClientSim
U4 real Windows + VRChat multi-client
U5 private upload smoke
```

ここで重要なのは、`vrmine`を「AI開発は失敗した」と雑にまとめないことです。

Editor code、scene generation、static verification、game logic、release gate設計には大量の成果があります。

失敗したのは、**それらをL5 RUNTIME_COMPLETEDと呼べるところまで証拠を閉じること**です。

```text
L1 Editor操作       → かなり進んだ
L2 Playable         → 実装あり
L3 Verification     → 多数あり。ただし旧G3に偽陽性経路
L4 Sustained        → 長期開発できている
L5 Runtime complete → BLOCKED
```

**感想:** 実装量が増えるほど「ほぼ完成」に見えます。しかしVRChatでは、late join、ownership、real serialization、multi-client、Quest、private uploadというEditor外のauthorityが最後に残ります。

`vrmine`から得た教訓は、

> GitHub CIが全部緑でも、VRChat worldが完成したとは限らない。

というだけではありません。

より正確には、

**証拠を生成するコード自体にもbugが入り得るため、verification pipelineにもprovenance、freshness、run isolation、runtime authorityが必要**

ということです。

---

# 外部事例と自前repoは同じ場所で壊れた

2つに絞ると対比が明確になります。

| 観測 | 外部事例 | 自前repo |
| --- | --- | --- |
| connection/config ≠ operation | ConnectedでもCodexから操作不能 | `image2outfit`: static integration後もlive MCP E2Eは`NOT_RUN` |
| tool registration ≠ editor evidence | toolが見えてもcall/状態確認で失敗例 | `image2outfit`: Blender / Unityのactual live call未証明 |
| simulation ≠ real networking | 公開事例では証拠が薄い | `vrmine`: ClientSimではlate join / ownershipを証明しない |
| report PASS ≠ valid evidence | test oracleの欠陥 | `vrmine`: 旧G3にclient evidenceなしでPASSし得る経路 |
| L3 VERIFIED ≠ L5 RUNTIME_COMPLETED | test/build成功例でも最終runtimeは別 | `vrmine`: 長期実装後もrelease `BLOCKED` |

外部レビューの結論は、自前repoを足しても変わりません。

むしろ、**「設定された」「検証された」「実runtimeで成立した」を別stateにする必要**が具体化されます。

---

## 一番重要な発見：AIの弱点は「操作」より「oracle」

14件と自前repoを並べると、より深い問題が見えます。

```text
AIが操作できない
```

より、

```text
AIが何を確認すべきかを間違える
```

方がproductionでは危険です。

3月13日のdungeonでは7回testしてもplayer traversalを見ていませんでした。

`image2outfit`ではMCP integration codeとstatic testsが存在しても、live Blender / Unity callを実行していない以上、Editor operationを証明できません。

`vrmine`ではverification reportを作る実装そのものに、current client evidenceなしでPASSし得る穴がありました。

つまり、

```text
more tool calls
more tests
more screenshots
more CI
```

だけでは完成へ近づきません。

必要なのは、**正しいcompletion oracleと、そのoracle自身の証拠設計**です。

---

## 2026年5月、Unity自身もMCPを公式toolchainへ入れた

Unityは2026年にAI toolsをopen betaとして公開し、その構成要素に公式MCP Serverを含めています。

公式一次情報:
https://unity.com/blog/unity-ai-how-to-get-started
https://unity.com/blog/unity-ai-mcp-how-to-get-started
https://unity.com/blog/mcp-servers-game-development

これは大きな変化です。

MCPそのものを「toyだからproductionでは無意味」と切り捨てる段階ではありません。

一方、official integrationが存在することと、個々のprojectでL5まで証明できることは別です。

---

## task class別の現在地

| task class | 2026年の観測 | 本記事の判断 |
| --- | --- | --- |
| GameObject / Scene生成 | 多数の成功例 | 実用域 |
| script生成・attach | 多数の成功例 | 実用域 |
| tutorial / casual prototype | 10分前後の例もある | 実用域 |
| 既存bug調査・修正 | animation等で成功 | 強い |
| console-driven repair | 成功例複数 | 強い |
| EditMode / PlayMode tests | 全PASS例あり | 有効。ただしcoverage依存 |
| build | 実例あり | 利用可能 |
| 複雑なprogression | self-test後も詰み例 | human play必須 |
| visual consistency | 見落とし例あり | human / vision review必須 |
| art direction | 成功・失敗が混在 | 不安定 |
| shader / VFX | 高コスト失敗例 | 不安定 |
| connection lifecycle | Connectedでも失敗例 | 運用監視が必要 |
| MCP integration / registration | `image2outfit`でstatic実装まで | live E2Eを別gateにする |
| save / reload persistence | 公開事例で境界あり | 明示gateが必要 |
| real VR networking | `vrmine`で未完了 | ClientSimだけでは不可 |
| late join / owner leave | `vrmine`でrelease blocker | real clients必要 |
| external playerの面白さ | 強い自動評価証拠なし | 人間 / player側 |

---

## 導入するなら、MCPをcompletion gateにしない

現実的な構造はこれです。

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
save → reload
        ↓
actual player traversal / visual review
        ↓
build
        ↓
real target runtime
        ↓
external user / multi-client / device-specific checks
```

最低でもstateを分けます。

```text
TOOL_SUCCESS
EDITOR_VALIDATED
PERSISTENCE_VALIDATED
PLAYABLE_VALIDATED
BUILD_VALIDATED
RUNTIME_COMPLETED
```

例えば、

```json
{
  "tool_success": true,
  "editor_validated": true,
  "persistence_validated": true,
  "playable_validated": false,
  "runtime_completed": false,
  "reason": "NOT_RUN"
}
```

ならcompletedではありません。

VRChatのようにruntime authorityが強いprojectなら、さらに分けます。

```text
STATIC_VALID
UNITY_VALID
CLIENTSIM_VALID
REAL_MULTICLIENT_VALID
PRIVATE_UPLOAD_VALID
RELEASED
```

---

## 読者別：2026年8月に導入する価値はあるか

### Unity初心者

**価値あり。ただしAIの出力を正解教材にしない。**

小規模prototypeはかなり作りやすくなっています。一方、serialization、Prefab、physics、lifecycleを知らないと偽成功を見抜きにくいです。

### Unity engineer

**かなり価値あり。特に反復作業、既存bug、test、variant生成。**

architectureとacceptance criteriaを人間側が持てるため、恩恵を受けやすい層です。

### game designer / planner

**prototype速度には価値あり。完成判断は握り続ける。**

「面白い」「難しい」「見づらい」は機械testだけでは決まりません。

### VRChat / networked-world developer

**Editor automationだけ見て採用判断しない。**

ClientSim、real multi-client、late join、ownership、PC/Quest、uploadを別gateとして設計する必要があります。`vrmine`はその境界を越えられずreleaseが止まった実例です。

### production team

**version pin、logs、test、provenance、human review、target-runtime evidenceを前提にする。**

MCPをproduction gateにせず、authoring adapterとして扱う方が安全です。

---

## 結論

14件の公開実例と、自分たちのBlender / Unity / VRChat repoを並べて見えてきたのは、「Unity MCPはすごい」でも「まだ使えない」でもありません。

すでにAIは、

```text
Sceneを作る
scriptを書く
Playする
errorを読む
testする
直す
buildする
複数sessionで開発を続ける
```

ところまで来ています。

だから、

> Unity MCPは実用になったのか？

への答えは、かなりの範囲で**Yes**です。

しかし、

> Unity MCPに完成を任せられるのか？

への答えは別です。

外部では7回testしても最初の部屋から出られないgameがありました。

自分たちの`image2outfit`では、Blender / Unity MCP integrationを実装しても、live E2Eが`NOT_RUN`ならoperation successとは呼びませんでした。

そして`vrmine`では約4,000行を追加し、verificationとrelease gateを作っても、real multi-client / late join / owner leave / private upload evidenceを閉じられずreleaseは`BLOCKED`のままです。

したがって2026年8月時点の最も実務的な結論はこれです。

**Unity MCPは「使えるか？」の段階を越えた。次の問題は、AIに何を操作させるかではなく、何を証拠に完成と判定し、その証拠自体をどう信頼するかである。**

---

## 参照した2026年実運用記録・一次情報

1. 増田恭隆「Unity本家のAI参入と、これまでのUnityでのノーコード検証」  
https://note.com/yasutaka_masuda/n/n74397dbf2abf

2. unsoluble_sugar「uLoopMCP × Claude Code、AI駆動でUnityゲーム開発がどこまで自走できるか試してみた」  
https://zenn.dev/unsoluble_sugar/articles/cd8d59be7b8f85

3. よなよな@AIゲーム開発「Unity 6 × Codex × MCPで『30分ヴァンサバ』を作るつもりが、白画面から始まった話」  
https://note.com/yonayona_ai_game/n/nb1ec6a528bbd

4. 越井琢巳「Unity MCP で TPS ゲームを Claude Code に改造させたら何が起きたか」  
https://dev.classmethod.jp/articles/unity-mcp-tps-game-claude-code-modification/

5. miya「〖UnityMCP〗簡単なUnityゲームを全自動で実装させました。」  
https://note.com/miya19/n/n4503e377dc45

6. 越井琢巳「Unity MCP × Claude Code に 2D ゲームの弾幕処理・アスレチック生成・ダンジョン生成をさせて破綻するかどうか観察してみた」  
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

### 補助・公式資料

- bunnoneta「〖開発記③・完結〗AIと二人三脚で作ったゲーム『昭和サバイバル』、ついに完成しました」  
https://note.com/bunnoneta/n/n91bbcd3fd700
- Unity「Unity's AI tools in beta: How to get started」  
https://unity.com/blog/unity-ai-how-to-get-started
- Unity「Unity AI open beta: How to get started with MCP」  
https://unity.com/blog/unity-ai-mcp-how-to-get-started
- Unity「MCP servers in game development explained」  
https://unity.com/blog/mcp-servers-game-development
- CoplayDev/unity-mcp  
https://github.com/CoplayDev/unity-mcp

### 私たち自身のfield evidence

- image2outfit PR #212 — Blender + Unity MCP integration, live E2E still `NOT_RUN`  
https://github.com/KAFKA2306/image2outfit/pull/212
- vrmine PR #18 — three-game release remains `BLOCKED`  
https://github.com/KAFKA2306/vrmine/pull/18
- vrmine Issue #19 — target-machine G0–G4 and private upload release blocker  
https://github.com/KAFKA2306/vrmine/issues/19
- vrmine Issue #43 — real multi-client / late-join / owner-leave regression matrix  
https://github.com/KAFKA2306/vrmine/issues/43
- vrmine Issue #54 — U1–U4 automated verification redesign  
https://github.com/KAFKA2306/vrmine/issues/54