---
title: "146公開リポジトリを母集団にして見直した。個人開発がChatGPTのマルチプロジェクト制御へ収束するまで"
emoji: "🛰️"
type: "tech"
topics: ["chatgpt", "github", "automation", "githubactions"]
published: false
---

GitHubのプロフィールには、公開リポジトリが146個ある。

前稿では、その中から `finBI`、`AutoPhotogrammetry`、`mastramcp`、VRChat Event Calendar、`daily-arXiv-ai-enhanced` などを選び、2023年から2026年までの「自動化の成熟史」として並べた。

しかし、この見方には大きな問題があった。

**146個を先に母集団として調べたのではなく、説明しやすいrepoを先に選び、その後で歴史を作っていた。**

実際にrepository一覧を広く取り直すと、金融、VR/3D、ゲーム、情報収集、動画生成、個人データ、Web UI、MCP/agent基盤など、かなり違う系統が並行して存在していた。

したがって、この記事では一本道の「進化史」をやめる。

**複数の開発系統が別々に自動化・検証・公開・権限分離を獲得し、2026年に一部がGitHubを共通状態として読む制御ループへ収束した**、という形で整理し直す。

## まず146 repoを分解する

2026年8月13日時点のGitHub profile APIは `public_repos: 146` を返す。

- Profile: https://api.github.com/users/KAFKA2306
- 公開repo一覧 1ページ目: https://api.github.com/users/KAFKA2306/repos?per_page=100&page=1&sort=created&direction=asc
- 公開repo一覧 2ページ目: https://api.github.com/users/KAFKA2306/repos?per_page=100&page=2&sort=created&direction=asc

Repository Searchでは、通常の公開repo検索で123件、`fork:only` で23件が確認できる。

- non-fork側: https://api.github.com/search/repositories?q=user%3AKAFKA2306+is%3Apublic
- forkのみ: https://api.github.com/search/repositories?q=user%3AKAFKA2306+fork%3Aonly

つまり、最初に少なくとも次を分けないといけない。

```text
146 public repositories
├─ 123 non-fork repositories
└─ 23 forks
```

forkは無価値という意味ではない。

既存OSSを評価・改造・実験するための重要なrepoもある。

ただし、**forkを「自分がゼロから構築したシステムの歴史」と同じ証拠として数えるのは不適切**なので、以降の自作系統とは分離して扱う。

また、古いrepoのREADMEは2026年の横断監査で更新されたものがある。repoの作成日は「そのテーマがGitHub上に現れた時点」の証拠として使い、現在READMEの高度な設計が作成当初から存在したとは主張しない。

### 今回の採用ルール

前稿の失敗を繰り返さないため、今回は次の順序で見る。

```text
1. 146公開repoを母集団として取得する
2. 23 forks と 123 non-forks を先に分離する
3. repo名・metadataから広いテーマ群を作る
4. 各テーマ群から複数repoを確認する
5. 詳細な設計を本文で主張するrepoはREADMEまで読む
6. 作成日と現在READMEの設計を混同しない
```

以下の長いrepo名一覧は、**公開repository metadata上に存在するテーマの広がりを示すインベントリ**である。各repoの内部設計を名前だけから断定するためのものではない。

一方、「このrepoでは何を検証している」「このpipelineは何段階である」といった具体的な設計上の主張は、READMEや実装を実際に確認したものに限定する。

## 一番古い時期から、すでにテーマは一つではなかった

最初期の公開repoには、ゲーム学習の `CantStopExpressLearn`、VR/Unity系のfork `BoneRenamer`、金融系の `finBI` がある。

ここだけでも、

```text
ゲーム
VR / Unity
金融
```

という別々の方向が同時に現れている。

だから、

```text
2023 = app
2024 = pipeline
2025 = agent
2026 = orchestration
```

のように年ごとに一つの成熟段階を割り当てるのは、実際のrepository群を圧縮しすぎていた。

より正確なのは、**複数の系統がそれぞれの問題に応じて別の能力を獲得した**と見ることだ。

## 系統1：金融・市場・投資研究

金融系は `finBI` だけではない。

公開non-fork repoには、少なくとも次のような系統がある。

```text
finBI
etf
finAnalist
kafin2
kafin3
fx
econalert
mstr
oil
uranium
auto-invest
financeLLM
option
fin_age_cfd
tradermade_cfd
nk225seasonality
nonfarmpayroll
investor
investor2
semiconductor-earnings-model
WealthAudit
CrewTrade
us-swing-strategy-bi-pages
skew
irr
```

これらは同じ「投資アプリ」のコピーではない。

- `auto-invest` は市場価格からKelly基準、ボラティリティ、Expected Shortfallなどを計算し、入力不足や品質不良時には確信的な数値を出さない。
- `semiconductor-earnings-model` は企業開示、規制開示、業界KPI、市場観測を別の値種別として保持し、JSON / SQLite / Webまで生成する。
- `finBI` は古いUI試作を縮約し、計算とpoint-in-time provenanceを検証する方向へ再構成された。

- https://github.com/KAFKA2306/auto-invest
- https://github.com/KAFKA2306/semiconductor-earnings-model
- https://github.com/KAFKA2306/finBI

この系統で発達したのは、主に次の能力だった。

```text
データ取得
→ 単位・期間・観測時点の固定
→ 派生計算
→ 出典と計算系譜
→ fail-closedな品質判定
→ API / DB / Pagesへの投影
```

つまり金融系から得た重要な要素は「AI」より、**観測値・推定値・シナリオ・判断を混ぜないこと**だった。

## 系統2：VRChat・Unity・3D制作

別の巨大な系統がVR/3Dである。

```text
VRPhotoJourney
AutoPhotogrammetry
vrcviewer
vrcgimmicknetwork
VRChat-bolt
adaptive_wear_generator_pro
blendshapedeformer
marvelousdesigner
bpyutils
vmatching
vmatch2
UnityMCPforUbuntu22.04
boothitemmanager
fit
image2outfit
vrmine
vrcplat
magicaltexture
molecularshader
vrcrelator
dancer
vrc-pilot-test
shaderGPT
PictureChangerTools
```

この系統では、単なるWeb APIとは違う問題が起きる。

FBX、BlendShape、bone、material、Unity asset、Prefab、Modular Avatar、外部3Dツールなど、**状態を持つ制作環境とファイルの整合性**が問題になる。

`AutoPhotogrammetry` の現在READMEでは、実写画像の収集元とSHA-256を保存し、特徴抽出・クラスタリング・選別・外部photogrammetry実行を分離している。

`boothitemmanager` は、BOOTHの商品情報について販売者が明示した事実とシステムの派生タグを分け、根拠不足を `UNKNOWN` / `quarantine` に落とす。

- https://github.com/KAFKA2306/AutoPhotogrammetry
- https://github.com/KAFKA2306/boothitemmanager

この系統で育ったのは、

```text
sourceを壊さない
identityを曖昧にしない
生成物を保存する
実環境の状態を再取得する
見た目と内部参照の両方を検証する
```

という考え方だった。

後の `source immutable`、artifact manifest、visual evidence、build / upload gateは、この問題群と相性がよい。

## 系統3：ゲーム・ルール・シミュレーション

ゲーム系も古くから独立して存在する。

```text
CantStopExpressLearn
DominionDeckDrawSimlator
Swiss-Tournament-Manager
boardgamelist
rule-scribe-games
pamiq-poker
vrpoker
furuyoni
game-library-dashboard
mj
bodogenomikata2
```

`Swiss-Tournament-Manager` はReact frontendとExpress/Mongoose backendを分け、clean checkoutから `npm ci`、test、build、DB不要のstartup smokeまでCI契約にしている。

`rule-scribe-games` はボードゲーム情報を検索・構造化するWebサービスで、AIによるルール生成だけでなく、cache、deploy、data fix、search verificationなどの運用workflowsも持つ。

- https://github.com/KAFKA2306/Swiss-Tournament-Manager
- https://github.com/KAFKA2306/rule-scribe-games

ここから見えるのは、**AIを使うかどうかに関係なく、clean install・再現可能build・外部依存を切ったsmoke testが自動化の土台になる**ということだ。

## 系統4：情報収集・知識・検索・出版

情報を集めて、人間が読める形へ変える系統もある。

```text
articles
kindle
kindle2
gennote
readable-github
know
nlm
books
cast_event_cal
vrc_cast_event_calender
RooBrawser
detective
```

`daily-arXiv-ai-enhanced` と `notebooklm-py` はforkを起点にした実験なので、自作repoとは別枠で扱う。

`know` は開発・AI・金融・生活で再利用する知識を集め、観測、推定、主張、test、evidence、decisionを共通語彙へ整理する。

VRChat Event Calendarでは `cast_event_cal` を正本、`vrc_cast_event_calender` を配信projectionとして分け、source commit、snapshot、hash、production確認を別段階にしている。

- https://github.com/KAFKA2306/know
- https://github.com/KAFKA2306/cast_event_cal
- https://github.com/KAFKA2306/vrc_cast_event_calender

この系統の中心は、**生成することより、原情報・派生情報・公開物の境界を保つこと**だった。

## 系統5：動画・音声・生成コンテンツ

前稿ではほぼ抜けていたが、生成・公開系にも複数repoがある。

```text
dmovie2511
vlog
vlogrs
ytmanager
yt3
yt4
2510youtuber
2511youtuber
anime
VeilVoice
vtttv
```

`kling` と `ComfyUI-KLingAI-API` は既存OSSからのforkなので、自作側の系統には数えない。

`2511youtuber` は、ニュース候補取得から台本、VOICEVOX音声、字幕、動画、metadata、YouTube公開までを一つのpipelineにしている。

一方 `vlog` は、VRChatの音声・写真・会話を単純にAI日記へ変換するのではなく、Evidence → Human Memory → Narrative Artifact → Public Projectionという層へ分けている。

- https://github.com/KAFKA2306/2511youtuber
- https://github.com/KAFKA2306/vlog

同じ「生成AI」でも、前者は**media production pipeline**、後者は**memory / privacy / publication boundary**が中心で、設計課題はかなり違う。

## 系統6：生活・個人データ・日常ツール

生活系も、金融投資とは分けた方がよい。

```text
salary
kakeibo
furutsatotax
bonus
aboutkafka
BestEthernet
travel
expense2
cedar-pollen-bi
Year2035
```

`kakeibo` は銀行・カード明細を扱うため、実データ、ログ、認証情報をGit外へ隔離し、privacy guard、local-only review、入力SHA-256、決定論的monthly snapshotまで持つ。

- https://github.com/KAFKA2306/kakeibo

ここでは「自動化を増やす」より先に、

```text
何をGitへ出さないか
何を外部へ送らないか
何を匿名化するか
何を再現できる形で残すか
```

が重要になる。

この系統を落とすと、マルチプロジェクト自律化を単なる開発速度の話に誤読してしまう。

## 系統7：MCP・agent・開発基盤

AIそのものを扱うnon-fork repoも複数ある。

```text
mastramcp
chat-code-architect-ai
chat-code-architect-ai2
backend
hf-cache-hub
agent-resources
prompt-vault
launcher
```

fork側には `DeepCode`、`claude-code`、`openclaw`、`financial-services-plugins` など、既存agentic / domain基盤を評価するために取り込んだrepoもある。

`mastramcp` ではWeb検索、filesystem、package管理、GitHub操作を役割別に分け、読み取りと書き込み、最小権限、人間承認の境界を検討していた。

- https://github.com/KAFKA2306/mastramcp

この系統だけを見ると「AI agentが進化して今の運用になった」と言いたくなる。

しかし全repoを横断すると、それは一部にすぎない。

現在の制御ループが機能するのは、金融系のprovenance、VR系のartifact validation、ゲーム系のCI再現性、情報系のcanonical/projection分離、生活系のprivacy boundaryなど、**他系統で先に必要になった契約が持ち込まれているから**である。

## 23 forksは全件、別の集合として扱う

GitHub Searchで `fork:only` を指定して得た23件は次の通りだった。

```text
AntennaPod
BoneRenamer
Basis
unity-mcp
unity-agent
rakuten_rss
claude-code
DeepCode
UnityMCP-VRC
Unique3D
TexasSolver
openclaw
KillFrenzyAvatarText
daily-arXiv-ai-enhanced
jquants-api-quick-start
ComfyUI-KLingAI-API
koodo-reader
open-fitter
expense
notebooklm-py
TradingView-Screener
kling
financial-services-plugins
```

この23件は、自作repoの数に混ぜて成熟度の証拠にしない。

一方で、forkには別の意味がある。

```text
既存OSSを読む
→ 手元で変更する
→ 自分の用途へ適合するか検証する
→ 必要なら別の自作repoへ考え方を持ち帰る
```

この経路は「ゼロから作った歴史」ではなく、**外部OSSを実験台として採用・評価した歴史**として別枠に置く方が正確だ。

この分離をしたことで、前稿で自作側へ誤って入れていた `Unique3D`、`jquants-api-quick-start`、`kling`、`financial-services-plugins`、`notebooklm-py`、`ComfyUI-KLingAI-API`、`open-fitter` なども除外できた。

## ここまで見て初めて、2026年の横断制御を説明できる

2026年7月13日から8月13日までをGitHub Search APIで確認すると、`KAFKA2306` アカウントではIssueが385件、PRが805件作成され、680件のPRが同期間内にmergeされている。

- Issues: https://api.github.com/search/issues?q=author%3AKAFKA2306+is%3Aissue+created%3A2026-07-13..2026-08-13
- Pull Requests: https://api.github.com/search/issues?q=author%3AKAFKA2306+is%3Apr+created%3A2026-07-13..2026-08-13
- Merged Pull Requests: https://api.github.com/search/issues?q=author%3AKAFKA2306+is%3Apr+is%3Amerged+merged%3A2026-07-13..2026-08-13

この数字は大きいが、重要なのは件数そのものではない。

以前は、各repoの中で

```text
取得する
計算する
生成する
検証する
公開する
```

を自動化していた。

現在はそこに、

```text
どのrepoが止まっているかを見る
↓
次に進められる候補を選ぶ
↓
Issueの完了条件を読む
↓
実装・検証する
↓
PR / mergeする
↓
productionを確認する
↓
残骸を片付ける
↓
もう一度全体を見る
```

という**repo間の制御**が加わった。

## GitHubを共通状態にした

複数repoで共通して使える単位は、最終的にGitHub上へ寄っていった。

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

中央管理用の `agent-resources` では、repository、Issue / PR、Actionsを集め、状態を機械可読なJSONへ落とす方向へ進めている。

- https://github.com/KAFKA2306/agent-resources

ここで大事なのは、ChatGPTが146個のrepoを全部「覚える」ことではない。

**各repoが自分の状態・完了条件・証拠をGitHubへ出し、横断側はそれを読むだけにすること**だ。

## 4状態へ圧縮する理由

生のGitHub状態は多い。

Issueのopen / closed、PRのdraft / open / merged、workflowのqueued / in_progress / completed、conclusionのsuccess / failure / cancelledなどを、そのまま横断制御へ使うと複雑になる。

そこで中央側では、最終的な行動へつながる状態へ圧縮する。

```text
working  = 機械が次へ進められる
waiting  = 人間判断または外部依存待ち
done     = 完了証拠がある
failed   = 失敗または再確認が必要
```

ただし、この4状態が成立するのは、各repo側ですでに

```text
何を成功とするか
何を公開してよいか
何を証拠として残すか
何がUNKNOWNか
どこで停止するか
```

を持っているからである。

## 一本の成熟史ではなく、「契約の合流」だった

146 repoを広く見ると、最終的な見方はこう変わった。

```text
金融
  provenance / PIT / unit / evidence

VR・3D
  identity / source immutability / artifact validation

ゲーム
  clean install / deterministic build / smoke test

情報収集
  canonical source / derived data / projection

動画・生成
  storyboard / provider boundary / publish gate

生活・個人データ
  privacy / local-only / redaction / reproducible snapshot

agent・MCP
  tool boundary / least privilege / orchestration

              ↓
        GitHub上の共通契約
              ↓
  cross-repository control loop
```

つまり、2026年に突然「ChatGPTが自律化した」のではない。

**多数の別プロジェクトで必要になった契約が、GitHubという共通状態へ合流した。**

この方が、実際のrepository群に近い。

## 人間に残す仕事も、系統ごとに違う

人間境界も一種類ではない。

金融なら、売買判断そのもの。

VR/3Dなら、見た目やcreative choice。

動画なら、公開してよい内容か。

個人データなら、何を記憶として採用し、何を公開するか。

OSS forkなら、上流をそのまま使うか、自分の設計へ持ち帰るか。

そのため、マルチプロジェクト自律化の共通原則は「人間を消す」ではない。

```text
機械的に証明できるもの
→ 機械へ

意味・価値・不可逆性を含むもの
→ 人間へ
```

という境界を、repoごとに明示することになる。

## 結論

最初の原稿では、説明しやすい少数repoを採用しすぎた。

146公開repoという数字をタイトルへ置くなら、先に146を母集団として見なければならなかった。

広く調べ直すと、実態は一本の自動化史ではない。

金融、VR/3D、ゲーム、知識、イベント収集、動画、個人データ、Web UI、MCP/agentという**複数の独立した問題群**があり、それぞれが別の理由で検証、provenance、privacy、CI、artifact、権限境界を必要としていた。

その後、それらの契約がGitHub上へ集まり、ChatGPTが

```text
全体を見る
→ 次を選ぶ
→ 実行する
→ 証拠を確認する
→ 状態を更新する
```

というrepo横断ループを回せるようになった。

コード生成は、その中の一工程にすぎない。

本質は、**異なる種類のプロジェクトを同じAIへ無理に揃えることではなく、各プロジェクトが自分の真実を機械可読な状態・契約・証拠として外へ出せるようにすること**だった。
