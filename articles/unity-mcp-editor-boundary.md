---
title: "2026年、Unity MCPはどこまで実用になったのか――14件で見えた『生成できる、でも監査できない』壁"
emoji: "🛠️"
type: "tech"
topics: ["unity", "mcp", "codex", "claudecode", "ai"]
published: false
published_at: 2026-08-12 16:03
---

# 2026年、Unity MCPはどこまで実用になったのか――14件で見えた「生成できる、でも監査できない」壁

2026年、AIがUnity Editorを操作すること自体は、もう珍しくありません。

自然言語からGameObjectを置く。scriptを書く。componentをattachする。Play Modeを起動する。consoleを読む。EditMode / PlayMode testを作る。buildする。数日にまたがってgameを作り続ける。

ここまでは、公開例がかなり増えました。

しかし実例を追うと、別の問題が残っています。

**AIは作れるようになった。しかし、自分が作ったものの「見た目」と「実際の挙動」を最後まで監査する能力は、生成能力ほど伸びていません。**

たとえば2026年には、

- 12個のobjectを正しく生成したのに、既存壁がdoorwayを塞いで部屋へ入れなかった
- 7回Play Mode testし、5件を自己修正したのに、playerは最初の部屋から出られなかった
- EditMode 4件 + PlayMode 3件が全部PASSしても、camera framingは人間が直した
- shader / VFXは「処理した」ことと「見た目が良い」ことが一致しなかった

という例が出ています。

私たち自身のrepoでも同じでした。

`image2outfit`では、201 tests、Blender hosted execution、numeric fit/build gateまでPASSした衣装を、5面と6ポーズで直接見ると袖が肩から離れ、衿が浮いていたためREJECTしました。

`vrmine`では、3ゲームworld、static CI、two-client verification logic、release gateまで作っても、real multi-client、late join、owner leave、private uploadでの挙動を監査し切れず、releaseは`BLOCKED`のままです。

つまり2026年に問うべきなのは、

```text
UnityをAIから操作できるか？
```

ではありません。

```text
AIが作ったものを、AI自身はどこまで正しく監査できるのか？
```

です。

結論を先に書きます。

**Unity MCPはauthoring toolとしてはすでに実用域です。最大の未解決点はauthoringではなくauditです。Sceneやcodeの内部状態はかなり監査できますが、「見た目として破綻していないか」「playerが本当に遊べるか」「real runtimeで同期するか」は、別のobserverとcompletion gateを必要とします。**

---

## 引用と要約のルール

この記事では、外部の実運用記録と筆者の解釈を混ぜません。

- `> 「……」` は原文からの**直接引用**
- 直接引用の直下に、著者名・記事名・公開日・URLを明記
- 引用符を付けていない説明は、原文に基づく**筆者要約**または本記事の分類
- 数字、日付、version、test件数は、元記事または一次情報で確認できたものだけを使用
- 体験談は「その環境で起きた観測」であり、製品全体の成功率には読み替えない
- 私たち自身のrepoもPR / Issueに残っているevidenceを基準とし、未実行を成功へ昇格させない

この記事でいう「実用域」「監査できない」「完成境界」は、引用ではなく複数事例を比較した本記事の判断です。

---

## これはsystematic reviewではない

対象は2026年8月15日までに公開され、次を満たす実運用記録を優先しました。

- Unity EditorをAI agent / MCPから実際に操作している
- setup紹介だけで終わらず、Scene、game、test、build、debug等の結果がある
- 成功だけでなく、失敗、修正、人間介入を読み取れる
- 公開日、環境、成果のいずれかを確認できる

note、Zenn、Qiita、DevelopersIO、企業・個人blog、GitHub、Unity公式情報を調査しました。Redditも探索しましたが、中心表では実行条件と成果を追いやすい記録を優先しています。

無作為抽出ではありません。成功体験を公開しやすいselection biasもあります。

したがって、

```text
14件中10件成功 → 成功率71%
```

のような数字は出しません。

代わりに、**何を生成できたかではなく、何を監査できたか**を比較します。

---

## 誰が試したのか――作者の多様性と証拠密度

14件は14人による独立再現ではありません。越井琢巳氏とmiya氏がそれぞれ2件を公開しているため、中心サンプルは**12の発信主体による14事例**です。

発信主体も一様ではありません。

- 個人game developer
- Zenn / note上の個人技術検証
- DevelopersIOの企業技術blog
- 企業名義のUnity検証
- Qiita上のworkflow / tutorial検証
- 複数日・複数stageにまたがる長期開発記録

本記事では肩書きそのものをauthorityにはしません。見るのは、第三者が「何が起きたか」を追える証拠量です。

```text
E3  高い証拠密度
    environment / task / failure / test / screenshot・video・code等が複数ある

E2  中程度
    実操作と成果物は見えるが、再現条件やfailure記録が限定的

E1  低い
    感想・完成報告中心で、検証条件や失敗情報が少ない
```

E3は「正しい」の意味ではなく、**観測を追跡しやすい**という意味です。

---

## 先に整理する：「操作できる」と「監査できる」は別能力

Unity MCPの能力を一列に並べると誤解しやすいので、authoringとauditを分けます。

| 層 | AIがやりやすいこと | 監査上の弱点 |
| --- | --- | --- |
| Source | C#生成、asset編集 | requirement自体が間違っていてもcompileできる |
| Editor state | GameObject、component、serialized field確認 | scene全体の意味・使いやすさは別 |
| Test | EditMode / PlayMode assertion | test oracleに書かれていない欠陥は見えない |
| Screenshot | 静止画capture | 視点外、時間変化、操作中の破綻を見逃す |
| Visual | silhouette、deformation、composition | 「良い見た目」の定義が曖昧で機械化しにくい |
| Gameplay | 実際のinputによるplayer path | warpやstate injectionでは代替できない |
| Network/runtime | ownership、late join、serialization | simulatorとreal clientが同じとは限らない |

この記事の中心命題は単純です。

```text
CAN_GENERATE
≠
CAN_AUDIT_THE_RESULT
```

---

## 「成功」を5段階に分ける

```text
L1 EDITOR_OPERATED
   Scene / GameObject / script等を操作できた

L2 PLAYABLE
   Play Modeで最低限遊べた

L3 VERIFIED
   console / test / build等の機械検証を通した

L4 SUSTAINED
   複数feature・複数sessionを跨いで開発を継続できた

L5 RUNTIME_COMPLETED
   実利用環境・外部player・real client等まで確認した
```

ここで重要なのは、**L3は「見た目と挙動が正しい」を意味しない**ことです。

`test passed`は、書かれたtestに対してPASSしたというだけです。

---

## 14件を一覧する

| 日付 | 発信主体 | 実例 | 到達 | 証拠 | 最後に人間が見たもの | 観測された境界 |
| --- | --- | --- | --- | --- | --- | --- |
| 2/19 | 増田恭隆 / note | Unity MCP vs CoPlayでブロック崩し | L2 | E2 | bug | MCP実装差が大きい |
| 2/24 | unsoluble_sugar / Zenn | uLoopMCPで2D→3Dブロック崩し | L2〜L3 | E3 | 反射・めり込み | observation loopが効く |
| 2/28 | よなよな@AIゲーム開発 / note | Unity 6 + Codexでヴァンサバ系 | L2 | E3 | 接続・画面・UI | Connected ≠ operable |
| 3/8 | 越井琢巳 / DevelopersIO | Unity公式MCPでTPS scene改造 | L1 | E3 | 実際の移動空間 | object生成 ≠ usable space |
| 3/11 | miya / note | CatchGame全自動生成 | L2 | E2 | play結果 | 単純gameは成立 |
| 3/13 | 越井琢巳 / DevelopersIO | 2D game 3テーマ | L2〜L3 | E3 | actual traversal | self-test ≠ playability |
| 3/22 | umezu_y / Qiita | 企画→WebGL workflow | 運用設計 | E3 | phase acceptance | completion contractが重要 |
| 4/5 | 四駒アイ / note | game改修・build | L2 + build | E2 | 操作性 | draft生成には有効 |
| 4/11 | ティー / note | 神経衰弱 + Unity CLI Loop | L2 | E2 | Play中error | observation追加で改善 |
| 4/17 | miya / note | マグネットスイーパー移植 | L2未満〜L2 | E2 | UI / 完成度 | 自動実装 ≠ 完成 |
| 5/7 | 株式会社ユニスポット | bug / shader / VFX | task依存 | E3 | 視覚品質 | bug fix強、VFX不安定 |
| 6/20 | zuqqhi2 / 個人blog | 3D鬼ごっこ + tests | L3 | E3 | camera framing | tests PASS ≠ visual PASS |
| 6/24 | TsuchiyaK / Qiita | Roll-a-Ball | L2 | E2 | play結果 | tutorial規模は成立 |
| 7/5〜9 | bunnoneta / note | 『昭和サバイバル』継続開発 | L4 | E3 | balance / fun / debug | 長期開発可能、完成判断は人間 |

一覧だけでも傾向が見えます。

**AIが苦戦するのは、C#を生成する場面より「最終結果をどう見るべきか」が曖昧な場面です。**

---

# 1. 同じブロック崩しでも、MCP実装差で体験が変わる

増田恭隆氏は、同じブロック崩しを異なるUnity MCP系で比較しました。

### 直接引用

> 「率直な感想は『使い物にならない』。」

— 増田恭隆「Unity本家のAI参入と、これまでのUnityでのノーコード検証」2026-02-19  
https://note.com/yasutaka_masuda/n/n74397dbf2abf

同じmodel family、同じUnityでも、agentにどのEditor操作をどう見せるかで結果が変わります。

**本記事の判断:** model intelligenceだけでなく、observation / action interface自体が性能です。

---

# 2. 2D→3D化で効いたのは、生成より観測

uLoopMCP + Claude Codeの検証では、2Dから3Dへ拡張したあと壁へのめり込みや反射不良が発生しました。人間が動作を見て修正を投げています。

### 直接引用

> 「雑なプロンプトでも、一発目で出てきたものは土台がほぼできていました。」

— unsoluble_sugar「uLoopMCP × Claude Code、AI駆動でUnityゲーム開発がどこまで自走できるか試してみた」2026-02-24  
https://zenn.dev/unsoluble_sugar/articles/cd8d59be7b8f85

**本記事の判断:** 生成能力より、`observe → detect → repair`を何で閉じるかが重要です。

---

# 3. 「Connected」でも操作できない

Unity側がConnectedでも、Codex側からprojectを正しく操作できない状態がありました。Main Camera、初期化順序、画面、UI等を復旧してplayableへ進んでいます。

### 直接引用

> 「Connected表示だけでは判断できないということです。」

— よなよな@AIゲーム開発「Unity 6 × Codex × MCPで『30分ヴァンサバ』を作るつもりが、白画面から始まった話」2026-02-28  
https://note.com/yonayona_ai_game/n/nb1ec6a528bbd

**本記事の判断:** connection healthはoperationの証拠ですらありません。まして完成の証拠ではありません。

---

# 4. 12 objectを作れても、部屋には入れない

DevelopersIOのTPS改造では、AIは壁、床、天井、doorway、柱、高台、slopeなど12 objectを生成しました。

しかしPlayすると既存壁がdoorwayを塞いでいました。

### 直接引用

> 「ドアウェイの位置に既存の壁が存在しており、部屋に侵入できませんでした。」

— 越井琢巳「Unity MCP で TPS ゲームを Claude Code に改造させたら何が起きたか」2026-03-08  
https://dev.classmethod.jp/articles/unity-mcp-tps-game-claude-code-modification/

```text
objects created: PASS
scene usable by player: FAIL
```

**本記事の判断:** Hierarchyや生成件数を監査しても、空間として使えるかは監査できません。

---

# 5. 自然言語だけでCatchGameを生成

miya氏は簡単なcasual gameを自然言語のみで全自動開発したと報告しています。

### 直接引用

> 「自然言語の指示のみで全自動開発しました。」

— miya「〖UnityMCP〗簡単なUnityゲームを全自動で実装させました。」2026-03-11  
https://note.com/miya19/n/n4503e377dc45

**本記事の判断:** tutorial / casual規模の「作る」はかなり成立しています。問題は、そこからproduction品質をどう監査するかです。

---

# 6. 7回test、5件自己修正。それでも最初の部屋から出られない

この事例は2026年のUnity agentを理解するうえで最も重要です。

複雑なdungeon生成に約49分。agentは7回Play Mode testを行い、5件を自己修正しました。

それでも人間が普通にplayすると、最初の部屋から出られませんでした。

### 直接引用

> 「スタート部屋から出られませんでした。」

— 越井琢巳「Unity MCP × Claude Code に 2D ゲームの弾幕処理・アスレチック生成・ダンジョン生成をさせて破綻するかどうか観察してみた」2026-03-13  
https://dev.classmethod.jp/articles/unity-mcp-claude-code-2d-game-verification/

agentはMCPでplayerをwarpしながら各部屋を検査していました。

```text
room state inspection: PASS
actual player traversal: FAIL
```

これは「testが少なかった」のではありません。

**監査対象を間違えていました。**

---

# 7. workflow化の価値は、監査条件を先に固定できること

umezu_y氏は企画、仕様、test仕様、task、実装、検証、releaseをphase化しています。

### 直接引用

> 「仕様がないと AI は『なんとなくそれっぽいもの』を作ってしまい、手戻りが大きくなります。」

— umezu_y「Claude Code × unity-mcp でゲーム開発の企画→公開をワークフロー化した話」2026年3月  
https://qiita.com/umezu_y/items/090a0fd25f9f915ad375

**本記事の判断:** 強いworkflowは「AIにたくさん任せる仕組み」ではなく、**何を見てPASSとするかを先に固定する仕組み**です。

---

# 8. 「ゲーム完成」と「良い操作感」は別

四駒アイ氏はsetup後、かなり粗い指示からgame生成、修正、buildまで進めています。

### 直接引用

> 「ゲーム完成です。」

— 四駒アイ「2026/4/5 UnityのMCPサーバ設定をしてみる in Cursor」2026-04-05  
https://note.com/4komaai/n/nafd4090dc068

同じ記事では操作性などに改良余地があることも述べられています。

**本記事の判断:** build artifactの存在とUXの監査は別です。

---

# 9. 生成後のerrorを観測できると、一段強くなる

ティー氏の神経衰弱では、最初に大量errorが出ました。その後、Unity CLI Loopを追加してPlay Modeとerrorを観測させることでplayableへ修正しています。

### 直接引用

> 「無事にエラーを修正してくれました。問題なく遊べるところまで持っていけました。」

— ティー「Unityに関するMCPを実際に入れてみた所感」2026-04-11  
https://note.com/mindpower/n/nba514492f5a5

**本記事の判断:** machine-readableなfailureはAIが直しやすい。これはAIが強い監査領域です。

---

# 10. 自動実装できても、作者自身が「未完成」と評価

miya氏は既存game「マグネットスイーパー」をUnityへ自動移植しましたが、UI等の修正が残りました。

### 直接引用

> 「ゲームとしてはまだまだ未完成でUIの修正などが必要な状態」

— miya「〖UnityMCP〗マグネットスイーパーの移植を試しました。」2026-04-17  
https://note.com/miya19/n/n8df417077cb0

**本記事の判断:** implementation coverageとfinished qualityは別の指標です。

---

# 11. bug fixは強い。shader / VFXの「見た目」は弱い

株式会社ユニスポットの検証では、既存3D projectのbug修正には有効だった一方、shaderやVFXは期待する視覚結果へ安定して到達しませんでした。

### 直接引用

> 「大量のトークンと時間を失うので、自分で作ったほうが良さそうです！」

— 株式会社ユニスポット「本当にゲーム開発もAIで出来る?『Claude Code + Unity MCP』でどこまで出来るか試してみた。」2026-05-07  
https://www.uni-spot.com/blog_post/claude-unity-mcp/

**本記事の判断:** error messageがあるbugと、「もっと良い見た目にする」は違うtaskです。後者はvisual oracleが弱い。

---

# 12. 7 tests全部PASSでも、cameraは人間が直した

zuqqhi2氏は3D鬼ごっこを作らせ、EditMode 4件、PlayMode 3件をすべてPASSさせました。

### 直接引用

> 「EditMode を見ると、ちゃんと 4 つテストケースがあって全部通りますね。」

— zuqqhi2「CoplayDev 版 unity-mcp を使用して Codex に Unity を操作させてテスト込みの開発をさせる」2026-06-20  
https://zuqqhi2.com/coplaydev-unity-mcp-codex-game-dev

一方、camera framingは追加修正が必要でした。

```text
tests: 7/7 PASS
visual framing: human correction
```

**本記事の判断:** test suiteが強くても、視覚監査のcoverageは自動では増えません。

---

# 13. tutorial規模なら約10分でplayable

TsuchiyaK氏はUnity公式MCP Server + Claude CodeでRoll-a-Ballを作らせています。

### 直接引用

> 「エラーなくプレイできるゲームができあがりました。」

— TsuchiyaK「Unity AI × Claude Code でゲームを作ってみた」2026-06-24  
https://qiita.com/TsuchiyaK/items/a3de1ac034bf94cf905b

**本記事の判断:** 既知patternのprototype生成はかなり実用的です。これは「生成できる」の強い証拠です。

---

# 14. 全6stageまで継続開発できた。それでも面白さの判断は人間

bunnoneta氏は『昭和サバイバル』を複数stageにわたって継続開発しています。

### 直接引用

> 「ついに全6ステージが完成しました。」

— bunnoneta「〖開発記〗Unity製サバイバルゲーム『昭和サバイバル』全6ステージ完成までにClaudeと乗り越えた壁」2026-07-05  
https://note.com/bunnoneta/n/ndd6c132b1abf

同じ開発記には保存、compile待ち、freeze、debug等のfrictionも記録されています。

**本記事の判断:** L4 SUSTAINEDはすでに可能です。ただし長期自律開発が可能であることと、fun / balance / feelを自律監査できることは同じではありません。

補助:
https://note.com/bunnoneta/n/n91bbcd3fd700

---

# 自前repoで一番痛かったのは「作れない」ではなく「監査できない」こと

外部事例だけなら、「他人の環境ではそうだった」で終わります。

私たち自身のrepoでも、同じ境界に当たりました。

ここでは当初の自前5例を、論点が最もはっきりする**2と5の2例**へ集約します。

```text
自前失敗例2 = 見た目を監査し切れない
自前失敗例5 = 挙動を監査し切れない
```

---

## 自前失敗例2：`image2outfit`――201 testsを通しても、見た目は壊れていた

`KAFKA2306/image2outfit`のSiroinoSotai_PC向け青い法被では、Blender上の生成pipelineをかなり機械化しました。

PR #197:
https://github.com/KAFKA2306/image2outfit/pull/197

検証はここまで通っています。

- JSON/schema / repository audits
- 201 unit tests
- Architecture / release-policy checks
- Production contract / Ruff
- Blender 4.4.3 hosted execution
- numeric fit / build gates

数字だけを見るとかなり強い状態です。

しかし生成した**5面と6ポーズを直接見ると**、

- sleeve headが肩から視覚的に離れている
- collar bridgeが浮いている
- arms-up / arm-cross時のdeformationが許容できない

ことが分かりました。

numeric gateをPASSしたrunも`Evidence/Rejected/`へ送り、manifestは`WORKING`のままにしています。

```text
201 tests                 PASS
numeric fit/build         PASS
Blender hosted execution  PASS

5-view / 6-pose visual audit
                          FAIL
```

ここで足りなかったのは生成能力ではありません。

**見た目を正しく採点するoracleです。**

mesh count、weight normalization、clearance、collision、file existenceは機械的に監査できます。

しかし、

- 袖が自然に肩から生えて見えるか
- 衿が浮いて見えないか
- pose時のシルエットが不自然でないか
- referenceとして欲しい衣服に見えるか

は、同じtestでは監査できません。

PR #212ではBlender MCP + Unity MCP + Codexのlocal authoring integrationも作っています。

https://github.com/KAFKA2306/image2outfit/pull/212

ただしこのPR自身も、MCPをcompletion authorityにはしていません。live E2Eも別証拠として扱っています。

**感想:** AIへBlender / Unityの操作権限を渡すほど、「作れる」問題は小さくなります。代わりに最後に残るのは、生成物を見て「これはおかしい」と止める能力です。

---

## 自前失敗例5：`vrmine`――codeとCIを作れても、実際の挙動を監査できなかった

`KAFKA2306/vrmine`は、見た目ではなく**behavior audit**側の失敗例です。

PR #18:
https://github.com/KAFKA2306/vrmine/pull/18

RULEFORGE、ECHO MINE、CHESSの3ゲームworldに対して、

- 84 commits
- 48 changed files
- +3,989 / -338
- game logic
- scene generation
- static repository integrity CI
- two-client verification logic
- fail-closed upload-readiness gate

まで作りました。

それでもPRはDraft、release statusは`BLOCKED`です。

理由は、「codeが足りない」からではありません。

**real VRChat上での挙動をまだ監査し切れていないからです。**

release blocker Issue #19では、次のような確認が残っています。

https://github.com/KAFKA2306/vrmine/issues/19

- two distinct real clientsで状態が一致するか
- ownership transfer後も動くか
- late joinしたclientへstateが復元されるか
- owner leave後も継続またはsafe resetできるか
- 3P / 4P / 5Pの各player countで進行するか
- private upload後も同じ挙動か

さらに重要なのは、旧G3 verification自体にも穴があったことです。

PR本文では、以前のG3がfailedだったことに加えて、旧実装にはclient evidenceなしでPASSを書ける経路や、recent runのevidenceを混ぜ得る問題があったため、過去evidenceを無効化したと記録しています。

```text
verification code exists
report can say PASS
        ↓
real multiplayer behavior correct ?
        ↓
NOT PROVEN
```

Issue #43では、multi-client、late join、owner leave、PC/Questを独立したregression matrixとして管理しています。

https://github.com/KAFKA2306/vrmine/issues/43

さらにIssue #54では、検証を段階化しました。

https://github.com/KAFKA2306/vrmine/issues/54

```text
U1 package graph
U2 exact Unity compile / EditMode
U3 PlayMode + ClientSim
U4 real Windows + VRChat multi-client
U5 private upload smoke
```

この分割の意味は、**U3までPASSしてもU4の挙動は監査できていない**と明示することです。

ClientSimでlocal behaviorを見ても、real networking、ownership、late joinを同じ証拠として扱いません。

**感想:** Unity agentがsceneもlogicもtestも作れるほど、「実際に複数人で遊んだらどうなるか」という最後の挙動監査が相対的に大きなボトルネックになります。

---

# 2つの自前失敗を並べると、問題はかなり単純になる

```text
image2outfit
    AI / pipelineは衣装を作れる
    ↓
    見た目が正しいかを監査し切れない

vrmine
    AI / pipelineはgame logicを作れる
    ↓
    real multiplayer挙動が正しいかを監査し切れない
```

つまり、私たちが実運用で困ったのは、

```text
AI cannot create
```

ではなく、

```text
AI cannot reliably judge what it created
```

でした。

---

## 外部14件と自前repoは、同じ場所で壊れている

| 監査対象 | 外部事例 | 自前repo |
| --- | --- | --- |
| 見た目 | camera / shader / VFXを人間が修正 | `image2outfit`: 201 tests後にvisual REJECT |
| 空間 | 12 object生成後もdoorway blocked | `image2outfit`: geometry metrics PASSでもsilhouette FAIL |
| player挙動 | 7 tests後も最初の部屋から出られない | `vrmine`: real client behavior未証明 |
| networking | 公開例では強い証拠が少ない | `vrmine`: late join / ownershipがrelease blocker |
| verification自体 | test oracleがplayer pathを見ていない | `vrmine`: 旧G3にfalse-positive経路 |

この一致は重要です。

**MCPの弱点というより、AI開発全体の「observer problem」です。**

---

## AIにとって監査しやすいもの、しにくいもの

### 監査しやすい

```text
compile error
exception
missing component
serialized reference
exact numeric threshold
unit test assertion
schema violation
file existence
known invariant
```

正解がmachine-readableです。

### 監査しにくい

```text
自然なシルエットか
見づらくないか
cameraが気持ちいいか
操作して詰まらないか
面白いか
networkで本当に同期するか
late joinで違和感なく復元するか
Quest実機で同じように見えるか
```

正解がscene stateだけに存在しません。

**視覚・時間・操作・複数client・実deviceという別observerが必要です。**

---

## 「AIにもっとtestさせる」だけでは解決しない

3月13日のdungeonは7回testしています。

`image2outfit`は201 testsを通しています。

`vrmine`はverification framework自体を作り込んでいます。

それでも欠陥は残りました。

だから問題はtest数ではありません。

```text
more tests
```

ではなく、

```text
better oracle
better observer
```

が必要です。

### 見た目なら

```text
render
→ fixed viewpoints
→ representative poses
→ temporal deformation
→ vision / human review
→ explicit accept/reject
```

### game behaviorなら

```text
spawn normally
→ use only legal player input
→ complete actual path
→ repeat state transitions
→ real client / device where required
→ retain evidence
```

MCP tool callのsuccessは、このどちらの代わりにもなりません。

---

## 2026年5月、Unity自身もMCPを公式toolchainへ入れた

Unityは2026年にAI toolsをopen betaとして公開し、その構成要素に公式MCP Serverを含めました。

公式一次情報:

https://unity.com/blog/unity-ai-how-to-get-started
https://unity.com/blog/unity-ai-mcp-how-to-get-started
https://unity.com/blog/mcp-servers-game-development

したがってMCPそのものを「toy」と切り捨てる段階ではありません。

むしろauthoringが実用化したからこそ、**auditの弱さが次の主要課題として露出した**と見る方が実態に近いです。

---

## task class別の現在地

| task class | 2026年の観測 | 本記事の判断 |
| --- | --- | --- |
| GameObject / Scene生成 | 成功例多数 | 実用域 |
| script生成・attach | 成功例多数 | 実用域 |
| tutorial prototype | 10分前後の例あり | 実用域 |
| compile / console repair | 成功例複数 | 強い |
| known bug fix | 成功例あり | 強い |
| EditMode / PlayMode tests | 全PASS例あり | 強いがcoverage依存 |
| build | 実例あり | 利用可能 |
| visual appearance | 人間修正・失敗例が複数 | 弱いaudit領域 |
| deformation / silhouette | `image2outfit`でnumeric PASS後REJECT | visual observer必須 |
| complex traversal | 7 tests後も詰み | actual player path必須 |
| game feel / balance | 最終判断は人間 | human/player側 |
| shader / VFX | 高コスト失敗例 | 不安定 |
| real networking | `vrmine`で未完了 | real clients必要 |
| late join / owner leave | `vrmine` release blocker | simulatorでは不足 |
| final production completion | 強い自動証拠が少ない | human/runtime authority必要 |

---

## 導入するなら、MCPを「作る手」にして、「見る目」は別に持つ

実務では次の分離が必要です。

```text
Codex / Claude Code
        ↓
Unity / Blender MCP
        ↓
authoring
        ↓
compile / structural checks
        ↓
render / Play Mode
        ↓
VISUAL AUDIT
        ↓
BEHAVIOR AUDIT
        ↓
real target runtime
        ↓
completion
```

最低でもstateを分けます。

```text
TOOL_SUCCESS
STRUCTURE_VALIDATED
VISUAL_VALIDATED
BEHAVIOR_VALIDATED
RUNTIME_VALIDATED
COMPLETED
```

たとえば、

```json
{
  "tool_success": true,
  "structure_validated": true,
  "visual_validated": false,
  "behavior_validated": false,
  "runtime_validated": false,
  "completed": false
}
```

これを`SUCCESS`一語で潰してはいけません。

---

## 読者別：導入する価値はあるか

### Unity初心者

**価値はある。ただしAIが作った画面を正解教材にしない。**

prototypeは速い一方、何が不自然かを自分で判断できないとfalse completionに気づきにくいです。

### Unity engineer

**かなり価値がある。**

特にstructured editing、反復作業、known bug、compile / console / test-driven repairは強いです。

ただしvisual / behavior acceptance criteriaは別に設計する必要があります。

### game designer

**prototype速度には大きな価値がある。**

その代わり、camera、feel、difficulty、funのauthorityは渡さない方がよいです。

### VRChat / networked-world developer

**Editor内で動くことを完成条件にしない。**

ClientSim、real multi-client、late join、ownership、PC/Quest、private uploadを分けて監査する必要があります。

### production team

**MCPをcompletion authorityにしない。**

MCPはauthoring adapterとして使い、visual evidence、runtime evidence、provenance、human reviewを別gateにします。

---

## 結論

14件の公開実例と自前repoを並べて、2026年のUnity MCPについて最も重要だと感じたのは、modelの賢さでもtool call数でもありませんでした。

AIはすでにかなり作れます。

```text
Sceneを作る
scriptを書く
componentを繋ぐ
Playする
errorを読む
testを書く
修正する
buildする
複数sessionで開発する
```

ここは実用域に入っています。

しかしproductionで最後に残るのは、

```text
これは見た目として正しいか？
これは人間が実際に操作して正しく動くか？
```

です。

外部では、7回testしたgameが最初の部屋から出られませんでした。

自分たちでは、201 testsとnumeric gateを通した衣装を目視でREJECTしました。

`vrmine`では、約4,000行の変更とverification infrastructureがあっても、real multiplayer挙動を監査できるまでreleaseを止めています。

したがって、2026年8月時点の結論はこれです。

**Unity MCPは「作る」ためにはかなり実用になった。まだ弱いのは「見る」ことと「遊んで確かめる」ことだ。**

そしてproductionで重要なのは、AIにもっと作らせることより、

**AIが作ったものを誰が、どの視点で、どのruntimeで監査するのかを設計すること**です。

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

- image2outfit PR #197 — 201 tests / numeric gates PASS後に5面・6ポーズvisual reviewでREJECT  
https://github.com/KAFKA2306/image2outfit/pull/197
- image2outfit PR #212 — Blender + Unity MCP authoring integration。completion authorityにはしない  
https://github.com/KAFKA2306/image2outfit/pull/212
- vrmine PR #18 — three-game release remains `BLOCKED`  
https://github.com/KAFKA2306/vrmine/pull/18
- vrmine Issue #19 — target-machine G0–G4 and private upload release blocker  
https://github.com/KAFKA2306/vrmine/issues/19
- vrmine Issue #43 — real multi-client / late-join / owner-leave regression matrix  
https://github.com/KAFKA2306/vrmine/issues/43
- vrmine Issue #54 — U1–U4 automated verification redesign  
https://github.com/KAFKA2306/vrmine/issues/54
