# articles 実生成物・編集査読 2026-08-12

## 結論

現行10本は、**技術的な正確さ・証拠・再現性はかなり強い一方、読み物としては設計書・監査報告書へ寄りすぎている**。

最大の欠陥は文章力ではない。

**問いが弱い記事まで、丁寧な構成・図・一次情報・一般化によって「良記事らしく」仕上げてしまうこと**である。

このため、LAPRAS型の「役に立つ」評価は上げやすいが、Zennで100+級の個別記事に見られる「その人に何が起きたのか」「なぜ予想が外れたのか」「続きを読まないと答えが閉じない」という推進力が弱い。

本査読では、次を別々に見る。

- **問いレンズ**: 堀元見氏が公開している「gap spottingより前提を疑う問いを重視する」という編集原理を参考にする。文体は模倣しない。
- **LAPRASレンズ**: 論理性・実用性・読みやすさ・独自性・明確性を品質床として見る。
- **Zenn 100+レンズ**: 個別記事で確認可能ないいね数100以上だけを正例候補とし、scene、実測、著者固有の経験、失敗、制約、mechanismの順序を比較する。

一次情報:

- 堀元見「おもしろくて刺激的な知識エンタメのための、良い問いの作り方」: https://note.com/kenhori2/n/nc90dfc3f3255
- LAPRAS「AIレビュー機能について」: https://talent-help.lapras.com/ja/articles/8039514-ai%E3%83%AC%E3%83%93%E3%83%A5%E3%83%BC%E6%A9%9F%E8%83%BD%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6
- Zenn「コミュニティガイドラインをアップデートしました」: https://info.zenn.dev/2026-02-03-community-guidelines-update
- Zenn「AIによるコンテンツ執筆に関するZennの方針について」: https://info.zenn.dev/2026-03-10-ai-contents-guideline
- Zenn「Publication四半期表彰2026/Q2」: https://info.zenn.dev/2026-07-02-publication-quarterly-award-2026q2
- 100+正例として確認済みの個別記事: https://zenn.dev/aircloset/articles/d416342f46f16b

Zenn公式の2026/Q2表彰では、1位Publicationの平均いいね数は65である一方、上記の個別記事は「300を超えるいいね」と明記されている。このため、本repoの正例選抜はPublication平均ではなく個別記事単位とする。

---

## 1. codex-chatgpt-github-issue-bridge.md

### 判定: **残す。ただし冒頭を再構成**

現タイトル:

> Codexの結果コピペをやめたくて、private GitHub IssueをAI間のメッセージキューにした

### 問いレンズ

強い。単なる「GitHub Issueをqueueに使った」ではなく、実装すると難所がqueue以外へ移る。

特に記事中には、

- ChatGPT側のwrite可否
- Codexのapp / plugin / MCP初期化
- 空Git repositoryに有効なHEADがない
- private queueでもlocal agentの権限境界が必要

という**予想外の失敗列**がある。

問題は、冒頭でこの4つをほぼ全部説明してしまい、読者が探索する前に答えを渡していること。

### LAPRASレンズ

論理性・実用性・独自性は強い。E2Eの `BRIDGE_OK`、commit、verification recordがあり、一般的な解説記事では代替しにくい。

改善点は読みやすさ。公開URL・構成説明・結論が前半に密集している。

### Zenn 100+レンズ

正例に近い素材はあるが、**scene before concept** になっていない。

最初に置くべきなのは構成図ではなく、たとえば「Issue queueは動いたのにCodexの応答以前にOAuth初期化で落ちた」という失敗である。

### 具体改稿

提案タイトル:

> **GitHub IssueをAI間キューにしたら、最初に壊れたのはqueueではなくCodexの初期化だった**

冒頭の順序:

1. 最初のsmoke testがCodex本体より前で失敗した事実
2. 「Issue pollingが難所だと思っていた」という初期仮説
3. OAuth / app / plugin初期化が原因だった観測
4. そこで初めてqueue全体構成を見せる
5. HEAD、sandbox、allowlistの失敗を順に回収

削るもの:

- 冒頭の3項目まとめ
- 序盤の公開URL列挙
- 「公開版は〜という構成になりました」という早すぎる完成形

---

## 2. csv-migration-dry-run-before-write.md

### 判定: **内容は強い。結論先出しをやめる**

現タイトル:

> CSV移行でいきなり書き込まない：dry-run診断を本番ロジックと共有する設計

### 問いレンズ

「importerを作る前に、書き込まない診断だけを作る」は反直感性がある。

しかし冒頭で、

> この記事で伝えたい結論は一つです。

として答えを完全に閉じている。

これでは記事を読む必要がなくなる。

### LAPRASレンズ

非常に実用的。ISBN重複、新規Edition、類似タイトル、人間確認という意味的状態を具体化しており、CLIとbrowserで判定コアを共有する説明も明確。

### Zenn 100+レンズ

「dry-runが安全」という一般論では弱い。

強いのは、**最初にimporterを作らなかった結果、後からCLIとbrowserが同じ判定コアへ収束した**という開発上の反転である。

### 具体改稿

提案タイトル:

> **CSV importerを作る前にdry-runしか作らなかったら、CLIとブラウザの判定が1本になった**

冒頭では、ISBNの1行を例にする。

```text
ISBNは新規
タイトルは既存Workに近い
構文上は正常
でも自動importしてよいとは言えない
```

ここから「成功/失敗の2値では足りない」へ進む。

削るもの:

- 冒頭の結論全文
- URL4本の先行列挙
- dry-run一般論の重複

---

## 3. fail-close-data-pipeline.md

### 判定: **現状は公開候補から落とす。全面再構成**

現タイトル:

> 「取得できた」を成功条件にしない：fail-closeなデータパイプライン設計

### 問いレンズ

弱い。

「HTTP 200とデータ採用は別」「nullと0は別」「取得・検証・正本化・配布を分ける」は正しいが、読者の前提を大きく更新する問いではない。

現状は典型的なgap spottingで、既知のデータ品質原則を2 repositoryへ適用した説明に近い。

### LAPRASレンズ

実用性は高い。状態モデル、OIDC、null semantics、CI項目、KPIまで整理されている。

しかし**役に立つことと、記事として選ぶ価値があることは別**である。

### Zenn 100+レンズ

事件がない。誰が、何を成功だと思い、どの具体的データが危険だったのかがない。

### 具体改稿

このテーマを残す条件は、実repositoryから次のどれか1つを出せる場合だけ。

- HTTP成功なのに採用を拒否した具体レコード
- partial fetchをcomplete扱いしそうになった実例
- null→0で意味が変わった具体field
- publish flagを分離しなければ外部配布されていた具体ケース

それがないなら、**この記事は削除または候補へ戻す**。

残す場合のタイトル例:

> **HTTP 200なのに公開しなかったデータがある。取得成功を4状態へ分けた理由**

ただし、実例が証拠で確認できる場合に限る。

---

## 4. liltoon-reimport-first-aid-qa.md

### 判定: **短い応急記事として残す**

現タイトル:

> lilToonで左右の目の見え方が違うとき、最初に何をする？ — Reimportだけで切り分けるQA

### 問いレンズ

問いは狭いが明確。

「るるね本体でも追加モデルでも同じ症状」という観測から、個別meshではなく共有Shader経路を優先する推論は具体的である。

### LAPRASレンズ

実用性・明確性が強い。Renderer → Material → Shader → 1 asset Reimportという順序が、そのまま作業手順になる。

### Zenn 100+レンズ

大規模人気記事向けというより、検索流入型の実用記事。

問題はそれ自体ではなく、`unity-vrchat-shader-troubleshooting-qa.md` とreader jobが重複していること。

### 具体改稿

タイトル:

> **るるね本体と追加モデルで同じ左右眼エラーが出た。最初にReimportするShaderは1個だけ**

記事の役割を最初に明記する。

> これは原因を断定する記事ではない。最初の10分で「共有Shader import状態か」を1変数だけ動かして切り分ける手順である。

深いStereo原因説明は別記事へ送る。ここでは増やさない。

---

## 5. muchio-shiroinu-body-adapter.md

### 判定: **現行でも上位。ただし仕様列挙を後ろへ送る**

現タイトル:

> 『モデル差し替えは後日』と思っていたら、もう公式対応していた：VRChatペットを犬化する前に設計を引き直した

### 問いレンズ

強い。

「自分でモデル差し替え基盤を作る必要がある」という前提が、販売元の現行一次情報を読み直しただけで崩れる。

これは前提反転であり、記事化する理由がある。

### LAPRASレンズ

一次情報と、Prefab内部でしか確認できないことを分離しており明確。Body Adapterの責務も具体化されている。

### Zenn 100+レンズ

強い素材。ただし冒頭で `v1.3.6`、77bit、Modular Avatar等を一気に出し、**一番強い発見が仕様表に埋もれる**。

### 具体改稿

最初に出す一次情報は一つだけでよい。

> 「オリジナルペットの作り方」が、もう同梱されていた。

その1行で初期仮説を壊す。

77bit、version、SDK等は「その後確認した現行条件」に移す。

提案タイトル:

> **「モデル差し替えは未対応」の前提が、BOOTHを見直したら消えた**

副題で Muchio / VRChat を補う。

---

## 6. primary-source-derived-data-provenance.md

### 判定: **10本中、最も伸ばす価値が高い**

現タイトル:

> 一次資料と派生集計を混ぜない：公開データ分析を fail-close にする Provenance 設計

### 問いレンズ

本文には非常に強い素材がある。

- 以前の部分集合: **856行**
- 更新後の派生集計: **7,699行**
- 内訳: **5,026 purchases + 2,673 sales**
- 17件のOGE Form 278-T文書
- しかも7,699は「OGE公式集計」ではない

これは単なるprovenance解説ではない。

**856→7,699という約9倍の差が、計算ミスではなくscopeの違いだった**という話である。

現在のタイトルは、この記事の一番強い部分を完全に隠している。

### LAPRASレンズ

論理性・実用性・独自性とも強い。observed / derived / cross-check / unavailableを分ける理由も実データで説明できる。

### Zenn 100+レンズ

10本中もっとも「数字 → 謎 → 原因 → 一般化」の形へ変えやすい。

### 具体改稿

第一候補タイトル:

> **856件を7,699件に直したとき、問題は「計算ミス」ではなくscopeだった**

冒頭:

```text
最初の集計は856行だった。
後で同じテーマを取り直すと7,699行になった。
約9倍である。

では、856は誤集計だったのか。

そうではなかった。856は部分集合の値で、7,699もOGEが発表した公式合計ではない。
ここで壊れていたのは算術ではなく、「その数字が何を代表するか」というラベルだった。
```

その後に初めてProvenanceを導入する。

この順序なら、技術用語が謎を解く道具になる。

---

## 7. unity-mcp-editor-boundary.md

### 判定: **題材は良い。抽象語を減らす**

現タイトル:

> 『AIがUnityを触れた』は完成ではない：VRChat改変へMCPを入れる設計で分けた3つの境界

### 問いレンズ

「AIが操作できる」と「成果物が正しい」は別、という前提反転はある。

ただし現状は、その反転を3分類の説明へ早く変換しすぎる。

### LAPRASレンズ

MCP接続、Editor state、検証、VRChat成果物を分ける整理は有用。未検証領域を明示している点もよい。

### Zenn 100+レンズ

正例に近づけるには「操作成功だが完成ではない」具体sceneが必要。

証拠がないsceneを創作してはいけないので、現Issue / Draft PRから実際に確認できる未完了状態を1つ選んで冒頭へ置く。

### 具体改稿

タイトル:

> **AIがUnityを操作できても、VRChatアバターが完成したことにはならない**

構成:

1. 実際に「できた」操作
2. それでも未検証として残った条件
3. なぜrepoだけ / editor操作だけ / buildだけでは不足するか
4. 3境界を導入

---

## 8. unity-vrchat-shader-troubleshooting-qa.md

### 判定: **長すぎる。深掘り記事へ役割限定**

現タイトル:

> Unity / VRChatで『VRだけ二重に見える』をどう考えるか

### 問いレンズ

「Desktop正常なのにVRだけ二重」は強い現象である。

しかし記事は、Shader source、Material、variant、MA / NDMF、Renderer、Stereo renderingまで広げすぎている。

### LAPRASレンズ

網羅性と論理性は高いが、**読みやすさは網羅性のせいで落ちる**。

参照資料としては良いが、記事としての中心線がぼやける。

### Zenn 100+レンズ

100+級の読み物へ寄せるなら、百科事典をやめて「なぜShader本体に決め打ちできないのか」という一つの謎へ絞る。

### 具体改稿

役割分離:

- `liltoon-reimport-first-aid-qa.md`: 最初の10分、1変数だけ動かす応急切り分け
- 本記事: Reimportで直らなかった後に、source / material / build / render contextを区別する深掘り

提案タイトル:

> **Desktopは正常、VRだけ二重。原因をShader本体に決め打ちできない理由**

削減対象:

- Stereo一般論の網羅説明
- 同じ原則を言い換える節
- quick-fix記事と重複する手順

目安として本文を30%以上削り、decision treeを中心にする。

---

## 9. video-storyboard-ir-provider-compile.md

### 判定: **技術内容は強い。API仕様表から物語へ変える**

現タイトル:

> 動画生成APIを直接叩くのをやめた：Storyboard IRでKlingとMiniMaxの仕様差をコンパイル時に止める

### 問いレンズ

「provider差をIRで吸収する」は設計としては自然で、問いとしては弱い。

本文にある強い部分は、

- first/last frameとreference mediaの共存不可
- providerによって表現可能なrouteが違う
- unsupported mediaを黙って捨てずcompile errorへする
- timeline overlap等をnetwork request前に止める

という**『自然言語の台本としては成立しているのにproviderへ落とせない』瞬間**である。

### LAPRASレンズ

実用性・明確性は高い。Draft PRとmerged実装を区別し、live generation済みと誇張していない点もよい。

### Zenn 100+レンズ

冒頭のprovider機能一覧が長く、読者が最初にAPI仕様を読むことになる。

### 具体改稿

提案タイトル:

> **KlingとMiniMaxの仕様差を、APIエラーになる前にStoryboardのcompile errorへ変えた**

冒頭は「このShotは人間には自然だが、このproviderでは表現できない」という1ケースから始める。

IRのfield一覧は、その問題を見せた後に置く。

---

## 10. vrcpet-observation-source.md

### 判定: **アイデアは強いが、20KBの設計書になっている**

現タイトル:

> ペットが聞いた会話を、そのまま『記憶』にしてはいけない：VRChatログを観測センサー化する

### 問いレンズ

「聞いたこと = 記憶ではない」は強い前提反転。

さらに本文には、

```text
{"text":"hello"}
{"broken":
{"text":"world"}
```

から `valid records = 2`, `parse issues = 1` を残す具体fixtureがある。

これをもっと前へ出すべきである。

### LAPRASレンズ

read-only、stable read、SHA-256、UUID、privacy、snapshot、Episode、rebuildable viewまで非常に実用的。

しかし、説明が多すぎて中心の意味論が薄まる。

### Zenn 100+レンズ

「何でも正しく説明する」より、

> 壊れた1行を見て、なぜ前後2行を記憶に昇格も全捨てもさせなかったのか

というsceneを通して設計を見せる方が強い。

### 具体改稿

削る / 圧縮する候補:

- SHA-256とUUIDv5の一般説明
- pathlib/json/hashlibの教科書的説明
- 転用先9項目の網羅列挙
- 同じread-only / evidence原則の反復

残す中心線:

1. malformed 1行 + valid 2行
2. observation != claim
3. raw bytes / issueを監査可能に残す
4. Episodeへ関連付けてもMemoryClaimにしない
5. daily viewは再生成可能なprojection

目安として30〜40%短くする。

---

# 横断レビュー

## 現在の最重要アンチパターン 1: 冒頭で答えを閉じる

実生成物には次の型が複数ある。

- 「結論はこれです」
- 「結論は単純です」
- 「この記事で伝えたい結論は一つです」

検索回答では有効だが、読み物では離脱可能地点を冒頭に作る。

**答えを隠す必要はないが、答えの前にsceneを置き、結果が次の問いを生む構造にする。**

## 現在の最重要アンチパターン 2: 抽象語をタイトルで売る

以下は技術的には重要だが、タイトルの主役として弱い。

- fail-close
- Provenance
- IR
- MCP boundary
- observation source

これらは「856→7,699」「VRだけ二重」「queueより先にOAuthで落ちた」など、読者が理解できる現象を説明する**後段の道具**にする。

## 現在の最重要アンチパターン 3: すべて同じ記事構造

現行は多くが、

```text
問題
→ 原因
→ 設計判断
→ 実装
→ 検証
→ まとめ
```

へ収束する。

これは品質を揃えるが、生成物らしさも揃える。

記事ごとに、観測された事件の因果順を優先する。

```text
scene
→ 自然な予想
→ 予想外の観測
→ 調査
→ 仕組み
→ 一般化
```

または、

```text
数字A
→ 数字B
→ どちらが間違いか？
→ scopeの発見
→ provenance
```

のように、素材固有の順序を使う。

## 現在の最重要アンチパターン 4: 網羅性を品質と誤認する

正しい説明を増やすほどLAPRAS proxyは上がりやすい。
しかし、中心の問いに不要な正しい節は、100+級の読み物では摩擦になる。

**「説明できること」ではなく「この問いを解くのに必要なこと」だけを書く。**

## 現在の最重要アンチパターン 5: 内部LLM採点を目的関数にする

内部reviewerは、自分たちが定義したrubricへ適応する。
そのため、4点台を出す文章を作ることと、読者が実際に読みたいことが循環参照になる。

変更後は、

```text
実績100+の外部正例から編集原理を抽出
        ↓
問いの強さを選別
        ↓
LAPRAS proxyで技術品質を落としていないか検査
        ↓
一次情報で断定を閉じる
```

という順序にする。

# 優先順位

今すぐ本文を大きく直す順序:

1. `primary-source-derived-data-provenance.md` — 856→7,699を主役へ
2. `fail-close-data-pipeline.md` — 実事件がなければ公開候補から外す
3. `codex-chatgpt-github-issue-bridge.md` — 最初の失敗sceneから開始
4. `unity-vrchat-shader-troubleshooting-qa.md` — deep diveへ限定し30%以上削る
5. `vrcpet-observation-source.md` — 1 malformed row / 2 valid rowsを冒頭へ
6. `csv-migration-dry-run-before-write.md` — 結論先出しを撤去
7. `video-storyboard-ir-provider-compile.md` — provider incompatibilityから開始
8. `unity-mcp-editor-boundary.md` — 操作成功と完成の差を具体scene化
9. `muchio-shiroinu-body-adapter.md` — 強い前提反転を残し仕様表を後ろへ
10. `liltoon-reimport-first-aid-qa.md` — quick-fix用途へ限定

# 公開判定の新しい原則

**正しいだけの記事は公開しない。**

**役に立つだけの記事も、月1本の公開枠では公開しない。**

公開候補は最低でも次の3条件を同時に満たす。

1. 一次情報と再現証拠で正しい
2. 他のエンジニアが使える
3. 読者の予想を一次情報・実測・失敗のどれかで更新する

3がない場合は、文章を磨くのではなくテーマを捨てる。
