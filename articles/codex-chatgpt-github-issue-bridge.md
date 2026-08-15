---
title: "GitHub IssueからAIにローカルPCを任せてよいのか？ Unity・動画・3Dアセット処理で見えた境界"
emoji: "🔁"
type: "tech"
topics: ["codex", "github", "unity", "security", "automation"]
published: false
published_at: 2026-08-12 17:02
---

# GitHub IssueからAIにローカルPCを任せてよいのか？ Unity・動画・3Dアセット処理で見えた境界

GitHub Issueに仕事を書き、AI coding agentへ渡す。

2026年現在、この発想自体はもう珍しくありません。

GitHub Copilotのcoding agentはIssueを割り当てて作業を行い、Pull Requestを作成して人間へレビューを依頼できます。GitHubはOpenAI Codexを含むthird-party coding agentsについても、Issueやpromptから非同期に作業を委譲し、PRでレビューする流れを公式に提供しています。

- GitHub Docs — Kick off a task with Copilot agents:
  https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/kick-off-a-task
- GitHub Docs — About third-party coding agents:
  https://docs.github.com/en/copilot/concepts/agents/about-third-party-coding-agents

では、なぜ私はわざわざ

```text
GitHub Issue
  ↓
Windowsの常駐daemon
  ↓
ローカルCodex CLI
```

というbridgeを作ったのでしょうか。

結論から言うと、この仕組みの価値は**「IssueからAIを起動できたこと」ではありません**。

repositoryのコードだけを直すなら、cloud上のcoding agent + Pull Requestの方が自然です。

local bridgeが意味を持つのは、仕事の対象がrepositoryの外へ出るときです。

例えば、

- Unity EditorでFBX、texture、Prefabをimportして検証する
- Blenderで`.blend`を開き、Python処理やbackground renderを行う
- local GPUで画像・動画生成modelを動かす
- FFmpegで生成動画をfilter、transcode、muxする
- 数GB級の動画、texture、3D assetをlocal disk上で連続処理する
- local SDK、Editor version、cache、GPU、device、既存認証に依存した処理を行う

といった仕事です。

この場合、AIが扱うのはGit diffだけではありません。

```text
source code
+ binary asset
+ local cache
+ installed application
+ GPU
+ generated media
+ build artifact
+ preview image / video
```

までが1つの実行系になります。

この記事では、自作bridgeを単独の成功談として扱いません。

GitHubのcoding agent、GitHub Actions、OpenAIが公開しているCodexの安全設計に加え、Unity、Blender、FFmpeg、Hugging Face Diffusersの公式仕様と比較しながら、**AIにlocal asset pipelineを任せるときの一般設計**としてレビューします。

公開実装:
https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge

---

## 先に結論：repositoryだけで完結するなら、自作bridgeは第一選択ではない

2026年時点の選択肢を大きく分けると、次のようになります。

| 方法 | 実行場所 | 向いている仕事 | 主な成果物 |
|---|---|---|---|
| GitHub Copilot / third-party coding agent | cloud | repositoryの調査・修正・テスト | branch / PR / CI |
| GitHub Actions GitHub-hosted runner | ephemeral VM | 再現可能なbuild・test | log / package / artifact |
| GitHub Actions self-hosted runner | 自分のmachine | 特殊hardware・社内networkが必要なCI | log / artifact |
| 自作local bridge | 自分のPC | Unity、Blender、動画生成、local asset、device、既存環境 | code + binary asset + render + build evidence |

一般的なrepository修正だけが目的なら、

```text
Issue
  ↓
agent
  ↓
branch
  ↓
Pull Request
  ↓
CI + human review
```

という既存の経路を優先する方が自然です。

GitHub自身も、Copilotが生成したPRを通常のcontributionと同じように十分reviewするよう案内しています。

GitHub Docs:
https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/review-copilot-output

**local PCを直接実行環境にする理由がないなら、local PCを実行環境にしない。**

これは変わりません。

ただしasset pipelineには、repositoryだけでは表現できない状態が大量にあります。

そこがlocal bridgeの本命です。

---

# local bridgeが本当に強いのはasset pipelineだった

## 1. Unity：Gitにあるのはsource assetであって、Editorが見ている状態の全部ではない

Unity projectを考えると、local executionが必要になる理由が分かりやすくなります。

Unityの公式ドキュメントでは、Editorを`-batchmode`で起動し、`-executeMethod`でproject内のstatic methodを実行できます。用途としてCI、unit test、build、data preparationが明示されています。

Unity Manual — Unity Editor command line arguments:
https://docs.unity3d.com/ja/current/Manual/EditorCommandLineArguments.html

例えば概念的には、

```powershell
Unity.exe \
  -quit \
  -batchmode \
  -projectPath D:\dev\avatar-project \
  -executeMethod AssetPipeline.Build
```

のように、Issueから受けたtaskをlocal Unity Editorへ渡せます。

ここで重要なのは、Unity projectが単なるGit repositoryではないことです。

UnityのAsset Databaseはsource assetをimportしてartifactを生成し、そのdatabaseをprojectの`Library` folderに保持します。Unityは`Library`内のdatabaseをversion controlから除外するよう説明しています。

Unity Manual — Asset Database:
https://docs.unity3d.com/ja/current/Manual/AssetDatabase.html

つまり、

```text
GitHub上
  Assets/model.fbx
  Assets/material.mat
  Assets/texture.png
  ProjectSettings/...

local Unity
  上記source
  + import result
  + Library database
  + installed Editor
  + installed modules / SDK
  + machine固有の実行状態
```

です。

cloud agentが`.meta`やC#を書き換えるだけでは、**そのassetを実際のUnity Editorが正しくimportし、Prefabやbuildへ到達できたか**までは確認できません。

さらにUnityは、asset fileのmetadataを管理するため、assetの作成・移動・削除を単純なfilesystem操作ではなくAsset Database経由で扱うよう案内しています。

Unity Manual — Asset Database:
https://docs.unity3d.com/ja/current/Manual/AssetDatabase.html

この性質から、AIへ任せたい仕事は例えば次のようになります。

```text
Issue
  ↓
FBX / texture / configを生成・更新
  ↓
Unity batchmodeを起動
  ↓
AssetDatabaseでimport
  ↓
Editor scriptでPrefab / material / buildを検証
  ↓
exit code + Editor log + build artifactを回収
  ↓
Issue / PRへ結果を返す
```

ここではPRのdiffだけでは足りません。

**Unityがそのassetを受理したというruntime evidence**が必要です。

---

## 2. Blender：3D assetはPythonとbackground modeで機械処理できる

Blenderもlocal bridgeと相性がよいtoolです。

Blender 5.0の公式manualでは、`-b` / `--background`でUIなしのbackground executionができ、`-P` / `--python`でPython scriptを実行できます。Python exception時のexit codeもcommand line optionで設定できます。

Blender Manual — Command Line Arguments:
https://docs.blender.org/manual/ja/5.0/advanced/command_line/arguments.html

例えば、

```powershell
blender.exe \
  -b avatar.blend \
  --python-exit-code 1 \
  --python pipeline.py
```

という形にできます。

Blenderはbackground renderも公式にサポートしています。

```powershell
blender.exe \
  -b avatar.blend \
  -o //renders/frame_ \
  -f 1
```

Blender Manual — Command Line Arguments:
https://docs.blender.org/manual/ja/5.0/advanced/command_line/arguments.html

この経路を使えば、例えば

- meshの機械処理
- scene設定
- exporterの実行
- animation frameのrender
- preview image生成
- Pythonで定義したproject固有validation

を、local taskとして扱えます。

重要なのは、成果物が`.py`のdiffではなく、

```text
.blend
.fbx / .glb
texture
rendered PNG / WebP
validation JSON
```

になることです。

またBlenderはPython auto executionをcommand lineからenable/disableするoptionも持っています。

Blender Manual — Command Line Arguments:
https://docs.blender.org/manual/ja/5.0/advanced/command_line/arguments.html

これはasset自体がcode execution surfaceになり得ることを意味します。

したがって、未知の`.blend`をlocal machineで自動処理する場合は、filesystemだけでなく**script execution policyもsecurity boundary**として扱う必要があります。

---

## 3. 画像・動画生成：local GPUそのものが実行環境になる

生成AIも、local executionの理由が明確な領域です。

Hugging Face Diffusersは画像・動画・音声のgeneration pipelineを提供しており、公式ドキュメントではmodelをlocal folderから`from_pretrained()`で読み込めます。local pathを指定した場合、そのload自体のためにHubからfileをdownloadしないことも明記されています。

Hugging Face Diffusers — Loading pipelines:
https://huggingface.co/docs/diffusers/en/using-diffusers/loading

概念的には、

```python
pipeline = DiffusionPipeline.from_pretrained(
    "D:/models/video-model",
    torch_dtype=torch.bfloat16,
    device_map="cuda",
)
```

のような処理です。

Diffusersはtext-to-videoを含むvideo generation pipelineも提供しています。

Hugging Face Diffusers — Pipelines:
https://huggingface.co/docs/diffusers/api/pipelines/overview

この場合、local machine上にあるのは

```text
model weights
GPU / VRAM
input image / video
LoRAや追加weight
生成途中のframe
生成済みvideo
```

です。

これらを毎回cloud coding agentへuploadするより、**taskだけをGitHub経由で送り、dataとcomputeはlocalに置く**方が合理的なケースがあります。

ここでbridgeは「コードを編集するAI」ではなく、

> local GPU workloadを開始し、条件を変え、生成物を検証し、結果だけをcontrol planeへ返すagent

になります。

特にvideo generationは、画像1枚よりもframe数に応じてmemory負荷が大きくなります。DiffusersのStable Video Diffusion guideも、video generationはmemory intensiveであり、CPU offloadやchunkingなどのmemory低減策を説明しています。

Hugging Face Diffusers — Stable Video Diffusion:
https://huggingface.co/docs/diffusers/main/using-diffusers/svd

つまりGPU model、VRAM、local model cacheまで含めてenvironmentを固定する意味があります。

---

## 4. FFmpeg：生成した後のasset processingもlocal pipelineの一部

動画生成はmodelが`.mp4`を出したら終わりではありません。

実運用では、

- resize
- crop
- overlay
- audio mix
- subtitle
- codec変換
- bitrate調整
- container変換
- thumbnail生成

などの後処理が続きます。

FFmpeg公式ドキュメントは、`ffmpeg`をmedia converterとして説明し、複数inputのread、filter、transcode、複数outputへのwriteをサポートしています。`-filter_complex`では複数input/outputを持つfilter graphも構成できます。

FFmpeg Documentation:
https://ffmpeg.org/ffmpeg.html

FFmpeg Filters Documentation:
https://ffmpeg.org/ffmpeg-filters.html

例えば、生成動画へ画像を重ねる処理は公式documentationにも示されています。

```text
video
  + image
  ↓
FFmpeg filter graph
  ↓
encoded video
```

ここでも数百MB〜数GBのmedia fileをGitHubへ運ぶ必要はありません。

GitHub Issueには

```text
どのinputを
どのprofileで
どのoutputへ変換するか
```

というcontrol情報だけを置き、実mediaはlocal diskで処理できます。

---

## 5. 本当のlocal workflowは1つのtoolではなくchainになる

asset処理では、実際には1つのapplicationで完結しないことが多いです。

例えば、

```text
Issue
  ↓
Codex
  ↓
Diffusers / local GPU
  生成画像・動画
  ↓
FFmpeg
  encode / filter
  ↓
Blender
  mesh / scene / render
  ↓
Unity
  import / Prefab / build
  ↓
validation
  ↓
evidence bundle
```

というchainです。

これをcloud coding agentだけで行おうとすると、問題はcode generationではなく、

- tool version
- binary assetの移動
- local cache
- GPU
- application install
- license / authentication
- OS固有tool
- intermediate artifact

の管理になります。

そのためlocal bridgeの役割は、単なるremote shellではありません。

**repository外のcapabilityを、安全な範囲でagentへ貸し出すbroker**と考えた方が正確です。

---

# asset pipelineでは「PRを作った」が完了条件にならない

coding agentの標準的な成果物はPull Requestです。

しかしasset pipelineでは、source codeに変更がないtaskもあります。

例えば、

```text
同じBlender scriptで5方向renderを再生成する
既存modelから動画を再生成する
FBXをUnityへimportしてcompatibilityを検証する
FFmpeg profileだけ変えてencode比較する
```

といった仕事です。

この場合、completion contractを広げる必要があります。

最低でも、

```text
execution
  tool exit code

provenance
  tool version
  input path / hash
  model / config identifier

artifact
  output path
  output hash
  file size / format

validation
  Unity import/build result
  Blender script result
  media probe / expected dimensions

visual evidence
  preview render
  representative frames

review
  source変更があればPR
  binary変更は対応するartifact evidence
```

のように分けます。

つまり、

```text
code workflow
  diff → PR → CI → review

asset workflow
  input → execution → binary artifact → machine validation → visual evidence → review
```

です。

AI automationでは、**agentが「終わりました」と言ったことより、再検証できるartifactが残ったこと**を成功条件にします。

---

## 一般原則1：Issueは「仕事の記録」であって「実行権限」ではない

GitHubはIssuesを、ideas、feedback、tasks、bugsなどを計画・追跡するための仕組みとして説明しています。

GitHub Docs:
https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues

Issueはcontrol planeとしては便利です。

- 誰が依頼したか残る
- 何を依頼したか残る
- commentで状態を追える
- PRやcommitと関連づけられる
- 人間が後から監査できる

しかしIssue本文やcommentをそのままshell command相当の権限へ変換すれば、Issueはremote execution interfaceになります。

```text
Issueに書かれている
```

ことと、

```text
その内容をmachine上で実行してよい
```

ことは別です。

asset pipelineの場合は特に、commandの先にUnity、Blender、GPU、media encoderまで存在します。

したがってexecution authorityはIssueとは別に制御します。

---

## 一般原則2：agentの能力より先に、実行環境を狭くする

OpenAIが公開しているCodexの安全運用では、managed configuration、constrained execution、network policies、logs、sandboxing、approvalsなどが独立したcontrolとして扱われています。

OpenAI — Running Codex safely at OpenAI:
https://openai.com/index/running-codex-safely/

AIへのpromptに

```text
危ないことはしないで
他のfolderは見ないで
```

と書くことは、境界ではありません。

```text
prompt rule
  AIへの依頼

sandbox / allowlist
  実行系による強制
```

は別物です。

asset pipelineでは、この境界をfilesystemだけでなくapplicationにも広げます。

```text
Codexは起動できる
Unityは起動できる
Blenderは起動できる
FFmpegは起動できる

しかし、それ以外のbinaryは起動できない
```

というprocess allowlistまで持てると、local executionのblast radiusをさらに狭くできます。

---

## 一般原則3：「自分のPCで動かす」はcloudより強い理由が必要

local executionには明確な利点があります。

- cloudへ置けないlocal dataを読む
- local GPUを使う
- Unity / Blenderなどinstalled applicationを使う
- local cacheやSDKを使う
- large mediaをuploadせず処理する
- local deviceやhardwareを扱う

一方、その代わりに実行環境が長寿命の実machineになります。

GitHubはself-hosted runnerについて、ephemeralでcleanなVMである保証がなく、untrusted codeによって継続的にcompromiseされる可能性があると警告しています。

GitHub Docs — Secure use reference:
https://docs.github.com/en/actions/reference/security/secure-use

つまり、

```text
cloud agent
  disposableな作業環境へ仕事を持っていく

local bridge
  普段使っているmachineへ仕事を持ってくる
```

という差があります。

local bridgeは便利だから使うのではなく、**local stateそのものが仕事の一部であるときに使う**のが妥当です。

UnityのAsset Database、Blender file、local model weight、GPU、動画assetはその典型です。

---

## 一般原則4：最小権限は5層ではなく、asset pipelineでは6層で見る

coding agent向けのleast privilegeをasset処理へ広げると、少なくとも次の6層があります。

```text
1. Identity
   誰がtaskを発行できるか

2. Filesystem
   どのproject / assetをread/writeできるか

3. Process
   Unity / Blender / FFmpegなど何を起動できるか

4. Network / Tool
   どのAPI、MCP、model repositoryへ接続できるか

5. Compute
   どのGPU、device、resourceを使えるか

6. Output
   code / binary / log / previewをどこへ返してよいか
```

特にasset pipelineでは`Process`と`Compute`を分ける意味があります。

動画生成jobへGPUを貸すことと、任意のlocal processを起動できることは同じ権限ではありません。

GitHub Copilot coding agentもinternet accessをfirewallで制御でき、GitHubはdata exfiltration riskの管理として説明しています。

GitHub Docs:
https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-the-firewall

AI systemでは、入力だけでなく、**出ていくnetwork trafficとartifactも境界**です。

---

## 一般原則5：仕事の完了点をreviewable artifactにする

GitHubのcoding agent workflowではPRがreviewable artifactになります。

PRなら、

- diff
- commit
- CI
- review comments
- approvals
- merge status

を集約できます。

GitHub Docs — Review output from Copilot:
https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/review-copilot-output

asset pipelineでは、これにbinary evidenceを足します。

```text
execution success
  + expected behavior
  + machine-verifiable checks
  + binary artifact
  + visual evidence when needed
  + source diff / PR when changed
  + human acceptance when required
```

これがasset automation向けのcompletion contractです。

---

# では、自作bridgeは何をしているのか

構成は次の通りです。

```text
ChatGPT / sender
        │
        │ controller task
        ▼
private GitHub Issue
        │
        │ GitHub CLI polling
        ▼
Windows bridge daemon
        │
        │ codex exec
        ▼
local Codex CLI
        │
        │ final response + exit code + git evidence
        ▼
private GitHub Issue
```

実装:
https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/bridge-daemon.ps1

現在の公開実装はUnityやBlender専用daemonではありません。

重要なのは、このtransportの先でlocal commandを実行できるため、**Unity / Blender / FFmpeg / local inferenceのようなcapabilityを追加するときにも同じcontrol boundaryを再利用できる**ことです。

ただし、capabilityを増やすたびにattack surfaceも増えます。

---

## 1. Identity：誰のtaskを実行するか固定する

bridge daemonはIssue commentを順番に読みますが、すべてのcommentを実行するわけではありません。

comment authorのGitHub loginがinstallerで設定した`ControllerLogin`と一致し、所定のmarkerとJSON blockを持つ場合だけtaskとして処理します。

概ね、

```text
正しい形式
AND
正しいmarker
AND
comment author == ControllerLogin
```

です。

これは

> collaboration権限とexecution authorityを分離する

という設計です。

private repositoryに入れることと、local PCへ命令できることを同一視していません。

---

## 2. Filesystem：`AllowedRoot`から外へ出さない

taskは`cwd`を指定できます。

しかしdaemonはpathを正規化し、install時に設定した`AllowedRoot`配下かを検査します。

```text
AllowedRoot = D:\dev

OK
D:\dev\unity-project
D:\dev\video-pipeline

REJECT
C:\Users\...
D:\private-data
```

この制限はpromptではなくPowerShell側で強制されます。

**自然言語で「見ないで」と頼むのではなく、path boundaryをprogramで拒否する。**

---

## 3. Process / Filesystem：既定を`read-only`にする

bridgeのsandbox既定値は`read-only`です。

許可されている値も、

```text
read-only
workspace-write
```

だけです。

asset generationやUnity importのようにfileを書き出すtaskでは`workspace-write`が必要になります。

しかし、`workspace-write`を許可したことと、任意のapplicationを自由に起動してよいことは別です。

今後Unity、Blender、FFmpegなどを本格的にbrokerするなら、

```text
filesystem sandbox
+
executable allowlist
+
argument validation
```

まで分離する方が強い設計になります。

---

## 4. Tool：interactive環境をそのままautonomous runへ持ち込まない

このbridgeで実際に起きた失敗の1つが、普段使いのCodex環境にある追加MCP/app層がOAuth認証を要求し、自動実行が停止したことでした。

検証記録:
https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/VERIFICATION.md

その後、autonomous runでは

```text
--ignore-user-config
--disable apps
--disable plugins
```

を指定し、interactive Codexの設定・apps・pluginsから分離しました。

local MCPもdeny-by-defaultです。

この原則はUnityやBlenderにもそのまま当てはまります。

```text
普段使いUnity
  全package / 個人設定 / 開発用tool

agent用Unity
  固定version / 固定project / 固定Editor method
```

```text
普段使いBlender
  user preference / add-on / interactive environment

agent用Blender
  background mode / 明示script / 明示output
```

のように、**人間のinteractive profileと無人runtimeを分ける**方が故障原因も権限も減らせます。

---

## 5. Output：結果も機密情報になり得る

bridgeはfinal messageだけでなく、task ID、exit code、sandbox、cwd、Git HEAD、Git statusなどのevidenceを返します。

一方、raw JSONL event logはlocal runtimeに保持します。

asset pipelineではさらに、

- absolute local path
- model name
- private source media
- render
- build artifact
- intermediate file

がresultへ混ざる可能性があります。

したがってraw artifactをそのままpublic Issueへ返すのではなく、

```text
publicに出せるmetadata
privateに残すraw output
```

を分ける必要があります。

---

# 実際のE2Eで分かったこと

2026-08-12の公開verificationでは、bridgeの成功条件を

```text
worker exit_code = 0
final Codex message = BRIDGE_OK
```

の両方にしました。

検証記録:
https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/VERIFICATION.md

Scheduled Task登録、daemon起動、Issue comment読取だけでは成功にしていません。

bring-up中には、

1. unrelated MCP/app layerのOAuth要求
2. smoke用Git repositoryにvalid HEADがない

というfailure classも記録され、それぞれruntime isolationとbaseline commitで修正しました。

ただしasset pipelineへ広げるなら、次のE2Eはさらに厳しくする必要があります。

例えばUnityなら、

```text
Codex exit 0
+
Unity process exit 0
+
Asset import成功
+
expected Prefab / build artifact存在
+
artifact hash記録
```

Blenderなら、

```text
Codex exit 0
+
Blender Python exit 0
+
expected .blend / export存在
+
preview render存在
```

videoなら、

```text
generation完了
+
FFmpeg完了
+
expected codec / resolution / durationをprobe
+
representative frame確認
```

までを成功契約にします。

**asset workflowは、agentの返答ではなく生成物を検査して終わる。**

---

# ただし、このbridgeにも残る弱点がある

## 1. 長寿命のlocal machineである

GitHub-hosted runnerやcloud agentのようなdisposable environmentではありません。

UnityやBlender、model weight、credentialが載ったmachineだからこそ、compromise時のblast radiusは大きくなります。

## 2. network policyをbridge独自に細かく定義していない

filesystem root、sandbox、MCP allowlistはありますが、domain単位のnetwork allowlistをbridge独自に構築しているわけではありません。

model downloadやAPI利用を許すasset pipelineでは、network policyを独立して追加する価値があります。

## 3. process allowlistがasset toolごとに定義されていない

現行bridgeはUnity / Blender / FFmpeg専用brokerではありません。

本格運用なら、許可binary、version、project path、argumentをtask schemaとして固定した方が強くなります。

## 4. `workspace-write`は最終承認ではない

agentがassetを書き換えられることと、そのassetを採用してよいことは別です。

source changeはPR、binary changeはhash・preview・machine validationを残し、人間が採否を判断できる形にします。

## 5. GitHub account自体がcontrol credentialになる

Issue commentを実行指示として使う以上、GitHub account、GitHub CLI authentication、repository accessがcontrol planeのcredentialになります。

「private repositoryだから安心」では不十分です。

---

# 2026年時点での選び方

## A. repositoryだけで完結する

**GitHub上のcoding agentを使う。**

```text
Issue / prompt
  ↓
cloud agent
  ↓
branch / PR
  ↓
CI + review
```

## B. 再現可能なbuild / testだけ必要

**GitHub-hosted Actionsを優先する。**

## C. 特殊hardwareや社内networkだけlocalに必要

**self-hosted runnerを検討する。**

GitHubのsecurity warningを前提にrunner isolationを設計します。

## D. Unity / Blender / 動画 / 3D assetのようにlocal stateそのものが仕事

**local bridgeが有力になる。**

例えば、

```text
Unity
  import / Prefab / build

Blender
  Python / export / render

Diffusers
  local GPU inference

FFmpeg
  encode / filter / mux
```

を1台のasset workstation上で連結する用途です。

この場合の設計対象は、

```text
identity allowlist
filesystem allowlist
read-only default
explicit write elevation
executable allowlist
tool-specific argument schema
network boundary
compute boundary
bounded output
artifact hash
machine-verifiable completion
visual evidence
PR / human review
```

まで広がります。

---

# 私たちが作ったのは「AIへの橋」ではなく、local capability brokerだった

最初は、GitHub Issueを使えばChatGPTとlocal Codexをつなげられる、という発想でした。

2026年のGitHub ecosystemと比較すると、Issueからagentへ仕事を渡すこと自体はすでに一般化しています。

このbridgeの独自性が出るのは、その先です。

```text
GitHubだけでは触れない
Unity Editor
Blender
GPU model
video file
3D asset
local SDK
```

へ到達するときです。

その瞬間、bridgeはremote shellではなく、**local capability broker**になります。

そしてasset処理まで含めて考えると、安全性の中心も変わります。

> AI coding agentを安全にするのは賢いpromptではない。agentの外側に置いた強制可能な境界と、再検証できる成果物である。

repositoryだけで仕事が完結するならcloud agent + PRを使う。

local stateが本当に必要なときだけbridgeを足す。

そしてlocalへ入った瞬間、codeだけでなくapplication、GPU、asset、network、outputまで権限として設計する。

Unity、Blender、動画生成を考えると、local bridgeを作る理由はむしろここにあります。

---

## 一次情報・実装証拠

### GitHub

- About issues
  https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues
- Kick off a task with Copilot agents
  https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/kick-off-a-task
- About third-party coding agents
  https://docs.github.com/en/copilot/concepts/agents/about-third-party-coding-agents
- Review output from Copilot
  https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/review-copilot-output
- Customize Copilot firewall
  https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-the-firewall
- Secure use reference for GitHub Actions
  https://docs.github.com/en/actions/reference/security/secure-use

### OpenAI

- Running Codex safely at OpenAI
  https://openai.com/index/running-codex-safely/

### Unity

- Unity Editor command line arguments
  https://docs.unity3d.com/ja/current/Manual/EditorCommandLineArguments.html
- Asset Database
  https://docs.unity3d.com/ja/current/Manual/AssetDatabase.html
- AssetDatabase.ImportAsset
  https://docs.unity3d.com/ja/current/ScriptReference/AssetDatabase.ImportAsset.html

### Blender

- Blender 5.0 Manual — Command Line Arguments
  https://docs.blender.org/manual/ja/5.0/advanced/command_line/arguments.html

### FFmpeg

- ffmpeg Documentation
  https://ffmpeg.org/ffmpeg.html
- FFmpeg Filters Documentation
  https://ffmpeg.org/ffmpeg-filters.html

### Hugging Face Diffusers

- Loading pipelines
  https://huggingface.co/docs/diffusers/en/using-diffusers/loading
- Pipeline overview
  https://huggingface.co/docs/diffusers/api/pipelines/overview
- Stable Video Diffusion
  https://huggingface.co/docs/diffusers/main/using-diffusers/svd

### このbridgeの実装証拠

- Bridge implementation
  https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge
- Bridge daemon
  https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/bridge-daemon.ps1
- E2E verification
  https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/VERIFICATION.md
- Hardened autonomous-run commit
  https://github.com/KAFKA2306/KAFKA2306/commit/864774f15d7fc6522572a8e326dfa78573b0df74
