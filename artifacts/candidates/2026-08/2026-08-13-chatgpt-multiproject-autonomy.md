---
title: "個人開発が123個に増えたので、「次に何をするか」までChatGPTに任せた"
emoji: "🛰️"
type: "tech"
topics: ["chatgpt", "github", "automation", "githubactions"]
published: false
---

GitHubに公開リポジトリが146個ある。そのうち、forkを除く123個が自作側の個人開発だ。

金融、VRChat、ボードゲーム、動画、家計、旅行、論文、3D制作、データ収集、AI agent。

最初から一つの製品群として設計したわけではない。用途もデータも実行環境もかなり違う。

それなのに2026年夏、これらをChatGPTを介して横断して扱うようになった。

あるrepoのIssueを読み、次に進める作業を選び、実装し、CIを確認し、PRをmergeし、productionを確認する。終わったら別のrepoを見る。

**なぜ、もともと何の関係もなかった大量の個人プロジェクトを、一つの制御ループで扱えるようになったのか。**

この記事で書きたいのは、その理由だ。

![123個の個人開発をGitHubとChatGPTで横断運用する全体像](/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-01.webp)

## 直近1か月だけ見ると、急に何かが起きたように見える

2026年8月13日18:27:30 JST時点でGitHub Search APIを取得すると、2026年7月13日から同時刻までに `KAFKA2306` アカウントで作成されたIssue / PRと、同期間にmergeされたPRは次の規模になっている。

- Issues: 387
- Pull Requests: 813
- Merged Pull Requests: 686

一次情報:

- Profile: https://api.github.com/users/KAFKA2306
- Issues: https://api.github.com/search/issues?q=author%3AKAFKA2306+is%3Aissue+created%3A2026-07-13..2026-08-13T09%3A27%3A30Z
- Pull Requests: https://api.github.com/search/issues?q=author%3AKAFKA2306+is%3Apr+created%3A2026-07-13..2026-08-13T09%3A27%3A30Z
- Merged Pull Requests: https://api.github.com/search/issues?q=author%3AKAFKA2306+is%3Apr+is%3Amerged+merged%3A2026-07-13..2026-08-13T09%3A27%3A30Z

検索結果が後から増えないよう、上限時刻を `2026-08-13T09:27:30Z` に固定している。

## この数字の中身は、たとえばこんな成果だった

`813 PR` とだけ書くと、単にコードを大量生成したように見える。

実際に同じ時期に起きていたことは、もう少し種類が違う。

![813 PRの中で達成された4つの具体的成果](/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-02.webp)

### 公開前に「未来の金利データ」を弾いた

`finBI` では、`retrieved_at = 2026-07-24T20:17:00Z` のsnapshotに `2026-07-24 = 4.69` が入っていた。

ところがFRED公式の当時の表示を確認すると、その時点で利用可能だった最新観測は `2026-07-23 = 4.71` で、7月24日の4.69は7月27日の更新で初めて現れていた。

つまり、値そのものは正しくても、**「その時点ではまだ知り得なかった未来の値」が混ざっていた。**

公開前にこれをblockerとして検出し、source availability / vintage timestampまで検証するfail-close契約と回帰testへ落とした。

![finBIで未来の金利データを弾くpoint-in-time検証](/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-03.webp)

- https://github.com/KAFKA2306/finBI/issues/10

### 画面の3/4が空白になったWebアプリを、原因特定からproductionまで直した

`rule-scribe-games` では、desktopのゲーム詳細ページ全体が左約320pxへ押し込まれ、右側がほぼ空白になっていた。

原因は見た目のCSS値ではなく、`body` にgridを定義したのに、実際の `header / aside / main` がReactの `#root` 配下にいたという **layout ownershipの構造バグ**だった。

`#root` へgrid ownershipを移し、1280px / 800pxのPlaywright実寸回帰を追加し、Vercel PreviewとProduction deployを通し、公開 `/games/big-shot` とAPIのHTTP 200まで確認して完了にした。

![rule-scribe-gamesの320pxレイアウト崩れを本番まで修復する流れ](/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-04.webp)

- https://github.com/KAFKA2306/rule-scribe-games/issues/76

### 別repoの画像を、公開後にもう一度取得してhash一致まで確認した

`prompt-vault` で管理する共有assetを `travel` のPagesへ配るときは、画像を単にコピーしなかった。

Prompt Vaultのsource commit、source SHA-256、consumer側destination SHA-256をlockし、`travel` のbuildとPages deployを実行。その後、公開URLから画像をもう一度取得して `sha256sum -c` が `OK` になるところまで確認した。

つまり、**source repoで正しい → consumer repoで正しい → 公開後も同じものが見えている**を一続きのDone条件にした。

![Prompt Vaultからtravelへ共有画像を配布し公開後にhash検証する流れ](/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-05.webp)

- https://github.com/KAFKA2306/travel/issues/20

### 複数repoのデータをprivate bucketへ定期publishし、全objectを検証した

`semiconductor-earnings-model` では、GitHub側をcontrol plane、private Hugging Face Storage Bucketをdata planeとして分けている。

2026年8月13日のscheduled Actions runでは、GitHub OIDCでprivate bucketへ認証し、allow-listされたprefixだけをexact mirrorし、**publish後にevery objectをverifyするところまで成功**した。

![GitHubをControl Plane、private bucketをData Planeに分ける構成](/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-06.webp)

- https://github.com/KAFKA2306/semiconductor-earnings-model/actions/runs/31680400569

金融データの時点整合性、Web UIの構造バグ、repo間asset配布、private data planeへのpublish。

同じ「AI開発」と言っても、成功条件はまったく違う。

それでも共通しているのは、**「コードを書けた」で止めず、何をもってDoneとするかをrepo側に明示していること**だった。

数字だけ見ると、最近になって突然「大量の開発をAIへ任せ始めた」ように見える。

しかし、面白いのはPRの本数そのものではない。

コードを書く速度だけなら、プロジェクト数が増えるほど別の仕事が増える。

```text
次はどのrepoを見る？
↓
前回どこまで終わった？
↓
PRは残っていない？
↓
CI successはproduction successなのか？
↓
Issueをcloseしてよい？
↓
似た作業を別repoでまたやっていない？
```

AIへ実装を渡しても、**仕事の選択と完了判定が人間に残る**。

repoが増えるほど、人間自身がオーケストレーターになる。

2026年夏に変わったのは、コード生成の量より、**この「次を決めるループ」まで機械が扱えるようになったこと**だった。

## 123個の個人開発は、同じ種類のrepoではない

ここで重要なのは、123個の自作側repoを一つの年代順ストーリーへ押し込まないことだった。

2026年8月13日時点のGitHub profile APIは `public_repos: 146` を返す。

Repository Searchで分けると、

```text
146 public repositories
├─ 123 non-fork repositories
└─ 23 forks
```

となる。

- non-fork側: https://api.github.com/search/repositories?q=user%3AKAFKA2306+is%3Apublic+fork%3Afalse
- forkのみ: https://api.github.com/search/repositories?q=user%3AKAFKA2306+fork%3Aonly

123個のnon-forkを広く見ると、金融、VR/3D、ゲーム、情報収集、動画・音声、生活・個人データ、MCP/agent基盤などが並行している。

だからこの記事の主題は、

```text
2023 = app
2024 = pipeline
2025 = agent
2026 = orchestration
```

という一本の進化史ではない。

むしろ逆で、**全然違う問題を解いていたrepoが、なぜ後から同じAI制御へ接続できたのか**を見る。

## 金融では「いつの数字か」を曖昧にできなかった

金融系だけでもかなり多い。

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

たとえば `auto-invest` は市場価格からKelly基準、ボラティリティ、Expected Shortfallなどを計算し、入力不足や品質不良時には確信的な数値を出さない。

`semiconductor-earnings-model` は企業IR・規制開示などのsourceと、実績・ガイダンス・コンセンサス・市場観測・推計・シナリオなどの値種別を分けて保持し、JSON / SQLite / Webへ投影する。

`finBI` では、単に値が存在するかではなく、その時点で本当に利用可能だった値かというpoint-in-time provenanceまで問題になった。

- https://github.com/KAFKA2306/auto-invest
- https://github.com/KAFKA2306/semiconductor-earnings-model
- https://github.com/KAFKA2306/finBI

金融で必要になったのは、AIらしさより、

```text
観測値
推定値
シナリオ
判断
```

を混ぜないことだった。

さらに、source、observation date、availability、unit、計算式、派生値を後から辿れる必要がある。

ここで育ったのは、**provenance / PIT / unit / evidence** という契約だった。

## VR・3Dでは「ファイルがある」だけでは成功にならなかった

VRChatや3D制作では問題がまるで違う。

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

FBX、BlendShape、bone、material、Unity asset、Prefab、Modular Avatar、外部3Dツール。

この世界では、処理がexit code 0でも成果物が壊れていることがある。

`AutoPhotogrammetry` の現在READMEでは、実写画像の収集元とSHA-256を保存し、特徴抽出、クラスタリング、選別、外部photogrammetry実行を分離している。

`boothitemmanager` では、販売者が明示した事実とシステム側の派生タグを分け、根拠不足を `UNKNOWN` / `quarantine` に落とす。

- https://github.com/KAFKA2306/AutoPhotogrammetry
- https://github.com/KAFKA2306/boothitemmanager

ここでは、

```text
sourceを壊さない
identityを曖昧にしない
生成物を保存する
実環境を再取得する
見た目と内部参照の両方を見る
```

という契約が必要になった。

つまり **source immutability / identity / artifact validation / visual evidence** である。

## ゲームでは「自分のPCで動いた」を捨てる必要があった

ゲーム系も独立した系統として存在する。

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

`rule-scribe-games` はAIによるルール生成だけでなく、cache、deploy、data fix、search verificationなど運用側のworkflowも持つ。

- https://github.com/KAFKA2306/Swiss-Tournament-Manager
- https://github.com/KAFKA2306/rule-scribe-games

ここで必要になったのは、**clean install / reproducible build / smoke test / regression test** だった。

AIを使う以前に、「別環境でも同じ状態から同じ確認ができる」ことが必要になる。

## 情報収集では「原情報」と「見せるもの」を分ける必要があった

情報・知識・出版系では別の境界が生まれた。

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

`know` では観測、推定、主張、test、evidence、decisionを共通語彙へ整理している。

VRChat Event Calendarでは `cast_event_cal` を正本、`vrc_cast_event_calender` を配信projectionとして分け、source commit、snapshot、hash、production確認を別段階にしている。

- https://github.com/KAFKA2306/know
- https://github.com/KAFKA2306/cast_event_cal
- https://github.com/KAFKA2306/vrc_cast_event_calender

ここで育ったのは、**canonical source / derived data / projection / publication boundary** だった。

「取得できた」「分類できた」「公開できた」「利用者が正しいものを見ている」は全部別の状態になる。

## 動画と日記では、同じ生成AIでも境界が逆だった

動画・音声・生成コンテンツにも複数repoがある。

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

`2511youtuber` はニュース候補取得から台本、VOICEVOX音声、字幕、動画、metadata、YouTube公開までを一つのpipelineにしている。

一方 `vlog` は、VRChatの音声・写真・会話を単純にAI日記へ変換するのではなく、Evidence → Human Memory → Narrative Artifact → Public Projectionという層へ分けている。

- https://github.com/KAFKA2306/2511youtuber
- https://github.com/KAFKA2306/vlog

同じ生成AIでも、前者ではproduction pipelineが中心になり、後者ではmemory / privacy / publication boundaryが中心になる。

## 家計では、自動化する前に「外へ出さない」を決める必要があった

生活・個人データ系には次のようなrepoがある。

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

`kakeibo` は銀行・カード明細を扱うため、実データ、ログ、認証情報をGit外へ隔離し、privacy guard、local-only review、入力SHA-256、決定論的monthly snapshotを持つ。

- https://github.com/KAFKA2306/kakeibo

ここでは「もっと自動化する」より前に、

```text
何をGitへ出さないか
何を外部へ送らないか
何を匿名化するか
何を再現可能な形で残すか
```

を決める必要がある。

つまり **privacy / local-only / redaction / reproducible snapshot** が契約になる。

## MCPでは、AIを強くするより権限を狭くした

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

`mastramcp` ではWeb検索、filesystem、package管理、GitHub操作を役割別に分け、読み取りと書き込み、最小権限、人間承認の境界を検討していた。

- https://github.com/KAFKA2306/mastramcp

ここで必要だったのは、**tool boundary / least privilege / approval boundary** だった。

自律化を強くするために、何でも触れるAIを作るのではなく、むしろ「何を触ってよいか」を狭くする。

## 全然違うrepoなのに、同じ形が見えてくる

ここまでを並べると、各分野で必要になったものは違う。

```text
金融
  provenance / PIT / unit / evidence

VR・3D
  identity / source immutability / artifact validation

ゲーム
  clean install / reproducible build / smoke test

情報収集
  canonical source / derived data / projection

動画・生成
  provider boundary / production pipeline / publish gate

生活・個人データ
  privacy / local-only / redaction / reproducible snapshot

agent・MCP
  tool boundary / least privilege / orchestration
```

ところが、抽象度を一段上げると共通点がある。

どのrepoも最終的には、

```text
今どういう状態か
何を成功とするか
何を根拠にしたか
何を機械がしてよいか
何を人間へ返すか
```

を外へ出す必要があった。

**異なるプロジェクトが、偶然同じアプリ構造になったのではない。異なる理由から「状態・契約・証拠を機械可読にする」方向へ寄っていった。**

![金融・VR・ゲーム・情報・家計・MCPが状態・契約・証拠へ収束する図](/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-07.webp)

ここが、後から全部をつなげられた理由だった。

## GitHubが共通状態になった

複数repoをまたいでも共通して読めるものは、最終的にGitHub上へ寄った。

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

中央管理用の `agent-resources` では、repository、Issue / PR、Actionsを収集し、状態を機械可読なJSONへ落とす方向へ進めている。

- https://github.com/KAFKA2306/agent-resources

大事なのは、ChatGPTが123個の個人開発の中身を全部記憶することではない。

**各repoが自分の真実をGitHubへ出し、ChatGPTはその時点の状態を読む。**

これなら、会話履歴の長さに依存しない。

## 状態を4つへ圧縮すると「次」が選べる

生のGitHub状態は多い。

Issueのopen / closed、PRのdraft / open / merged、workflowのqueued / in_progress / completed、conclusionのsuccess / failure / cancelled。

そのままでは「次に何をするか」が分からない。

そこで横断側では、行動につながる状態へ圧縮する。

```text
working  = 機械が次へ進められる
waiting  = 人間判断または外部依存待ち
done     = 完了証拠がある
failed   = 失敗または再確認が必要
```

![working waiting done failedの4つの横断状態](/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-08.webp)

この4状態が成立するのは、各repo側で先に、

```text
何を成功とするか
何を公開してよいか
何を証拠として残すか
何がUNKNOWNか
どこで停止するか
```

が定義されているからである。

つまり中央のAIが賢いから状態を理解できるのではなく、**repo側が理解可能な状態を出している**。

## 自律化したのは「作業」より「次を決めるループ」だった

現在の制御ループは、だいたい次の形になる。

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
branch / PR / 一時ファイルをcleanupする
↓
もう一度全体を見る
```

![ChatGPTが全体確認からcleanupまで次の仕事を選ぶ制御ループ](/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-09.webp)

以前から各repoの中では、

```text
取得する
計算する
生成する
検証する
公開する
```

を自動化していた。

2026年夏に加わったのは、**その外側で「どのrepoの何を次に進めるか」を扱うループ**だった。

ここまで来ると、コード生成は一工程にすぎない。

## 人間を消したわけではない

分野ごとに、人間へ残す境界も違う。

金融なら売買判断そのもの。

VR/3Dなら見た目やcreative choice。

動画なら公開してよい内容か。

個人データなら、何を記憶として採用し、何を公開するか。

OSS forkなら、上流をそのまま使うか、自分の設計へ持ち帰るか。

共通するのは、

```text
機械的に証明できるもの
→ 機械へ

意味・価値・不可逆性を含むもの
→ 人間へ
```

![機械へ渡す仕事と人間へ残す判断の境界](/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-10.webp)

という境界である。

自律化は、人間をループから消すことではない。

**人間が毎回やらなくてよい調整仕事を状態と契約へ移し、本当に人間が決める必要のある場所だけを残すこと**だった。

## 146公開repoを全件見た理由

この記事では、代表例だけを並べて「123個の個人開発すべてがこの設計思想で作られた」とは言わない。

母集団を先に固定した。

2026年8月13日時点で、

```text
146 public repositories
├─ 123 non-fork
└─ 23 fork
```

である。

詳細な設計上の主張は、READMEや実装を確認したrepoだけに限定した。

一方、名前だけでは安全に分類できないrepoも消さず、付録に全件残す。

また、古いrepoのREADMEは2026年の横断監査で更新されたものがある。repoの作成日は「そのテーマがGitHub上に現れた時点」の証拠として使い、現在READMEの高度な設計が作成当初から存在したとは主張しない。

forkも無価値という意味ではない。

既存OSSを読み、変更し、自分の用途へ適合するか試す重要な実験場になっている。

ただし、それを「ゼロから作った自作repo」と同じ証拠には数えない。

## 結論：123個を一つにしたのは、AIではなく「読める状態」だった

金融、VR、ゲーム、動画、家計、旅行、情報収集、AI agent。

これらは最初から一つのシステムとして作ったものではない。

しかし、別々の問題を真面目に自動化していくと、それぞれで

```text
状態
契約
証拠
権限境界
停止条件
```

が必要になった。

それがGitHubという共通状態へ出るようになると、初めてChatGPTがrepoをまたいで扱えるようになった。

```text
123 non-fork repositories
        ↓
それぞれが状態・契約・証拠を出す
        ↓
GitHubを共通状態として読む
        ↓
ChatGPTが次の1件を選ぶ
        ↓
実装・検証・公開
        ↓
状態を更新して次へ
```

だから、123個を一つにしたのは「同じ技術スタック」でも「同じAIモデル」でもなかった。

**各プロジェクトが、自分の真実を機械が読める形で外へ出せるようになったこと。**

それが、バラバラな個人開発をマルチプロジェクト制御へ変えた。

## 付録A：123 non-fork public repositories 全件

GitHub Search APIの `user:KAFKA2306 is:public fork:false` で得た123件。

<details>
<summary>123件を表示</summary>

```text
anime
vrpoker
2510youtuber
books
nlm
yt4
mitsuikaggle
furutsatotax
investor2
know
vrc_cast_event_calender
BestEthernet
prompt-vault
CrewTrade
DominionDeckDrawSimlator
vrmine
image2outfit
WealthAudit
hitaiall
magicaltexture
alpha
patent
salary
agent-resources
VRPhotoJourney
Swiss-Tournament-Manager
kafin3
finAnalist
us-swing-strategy-bi-pages
expense2
Year2035
trahist
nk225seasonality
molecularshader
vrcrelator
bodogenomikata2
articles
readable-github
vrcviewer
gennote
rule-scribe-games
kafka
cedar-pollen-bi
vrcgimmicknetwork
shaderGPT
vmatch2
mastramcp
fin_age_cfd
pal-atlas
dancer
factory
jhr
KAFKA2306
x
vrcplat
irr
com
SecureVCC
hitaiou
RooBrawser
chat-code-architect-ai2
m2
backend
vrc-pilot-test
oil
semiconductor-earnings-model
chat-code-architect-ai
skew
VeilVoice
AutoPhotogrammetry
kakeibo
photoprism
fx
UnityMCPforUbuntu22.04
NVII
abestudy
launcher
aboutkafka
furuyoni
game-library-dashboard
bpyutils
auto-invest
summer
vlogrs
PictureChangerTools
detective
fit
adaptive_wear_generator_pro
investor
kindle2
pamiq-poker
2511youtuber
nonfarmpayroll
kafin2
CantStopExpressLearn
blendshapedeformer
vmatching
option
cast_event_cal
boothitemmanager
kimeraassist
uranium
bonus
dmovie2511
VRChat-bolt
boardgamelist
yt3
vlog
finBI
tradermade_cfd
mstr
kindle
ytmanager
financeLLM
vtttv
econalert
333
marvelousdesigner
mj
BMAX
hf-cache-hub
etf
travel
```

</details>

`factory`、`jhr`、`KAFKA2306`、`x`、`com`、`SecureVCC`、`hitaiou`、`m2`、`333`、`BMAX`、`kimeraassist` のように、名前だけでは安全に一つの系統へ分類できないrepoも、このinventoryからは落としていない。

## 付録B：23 forks 全件

GitHub Search APIで `fork:only` を指定して得た23件。

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

この23件は、自作repoの成熟度の証拠には混ぜない。

一方で、

```text
既存OSSを読む
→ 手元で変更する
→ 自分の用途へ適合するか検証する
→ 必要なら自作repoへ考え方を持ち帰る
```

という別の開発経路として残す。