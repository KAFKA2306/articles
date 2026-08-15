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

GitHub Copilotのcoding agentはIssueを割り当てて作業し、Pull Requestを作成して人間へレビューを依頼できます。GitHubはOpenAI Codexを含むthird-party coding agentsについても、Issueやpromptから非同期に仕事を委譲し、PRでレビューする流れを公式に提供しています。

- GitHub Docs — Kick off a task with Copilot agents
  https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/kick-off-a-task
- GitHub Docs — About third-party coding agents
  https://docs.github.com/en/copilot/concepts/agents/about-third-party-coding-agents

では、なぜわざわざ

```text
GitHub Issue
  ↓
Windowsの常駐daemon
  ↓
ローカルCodex CLI
```

というbridgeを作るのでしょうか。

repositoryのコードだけを直すなら、cloud上のcoding agent + Pull Requestの方が自然です。

local bridgeが意味を持つのは、**仕事の対象がrepositoryの外へ出るとき**です。

例えば、

- Unity EditorでFBX、texture、Prefabをimportして検証する
- Blenderで`.blend`を開き、Python処理やbackground renderを行う
- local GPUで画像・動画生成modelを動かす
- FFmpegで動画をfilter、transcode、muxする
- 数GB級の動画、texture、3D assetをlocal disk上で連続処理する
- local SDK、Editor version、cache、GPU、device、既存認証に依存する処理を行う

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

GitHubのcoding agent、GitHub Actions、OpenAIが公開しているCodexの安全設計に加え、Unity、Blender、FFmpeg、Hugging Face Diffusersの公式仕様、さらに実際に公開している3D衣装制作・動画制作repositoryを比較しながら、**AIにlocal asset pipelineを任せるときの一般設計**としてレビューします。

bridge実装:
https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge

---

## 先に結論：repositoryだけで完結するなら、自作bridgeは第一選択ではない

| 方法 | 実行場所 | 向いている仕事 | 主な成果物 |
|---|---|---|---|
| GitHub Copilot / third-party coding agent | cloud | repositoryの調査・修正・テスト | branch / PR / CI |
| GitHub Actions GitHub-hosted runner | ephemeral VM | 再現可能なbuild・test | log / package / artifact |
| GitHub Actions self-hosted runner | 自分のmachine | 特殊hardware・社内networkが必要なCI | log / artifact |
| local bridge | 自分のPC | Unity、Blender、動画生成、local asset、device、既存環境 | code + binary asset + render + build evidence |

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

を優先する方が自然です。

GitHub自身も、Copilotが生成したPRを通常のcontributionと同じように十分reviewするよう案内しています。

GitHub Docs:
https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/review-copilot-output

**local PCを直接実行環境にする理由がないなら、local PCを実行環境にしない。**

ただしasset pipelineには、repositoryだけでは表現できない状態が大量にあります。

そこがlocal bridgeの本命です。

---

# local bridgeが本当に強いのはasset pipelineだった

## Unity：Gitにあるのはsource assetであって、Editorが見ている状態の全部ではない

Unityの公式ドキュメントでは、Editorを`-batchmode`で起動し、`-executeMethod`でproject内のstatic methodを実行できます。用途としてCI、unit test、build、data preparationが明示されています。

Unity Manual — Unity Editor command line arguments:
https://docs.unity3d.com/ja/current/Manual/EditorCommandLineArguments.html

概念的には、

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

cloud agentがC#やasset metadataを書き換えるだけでは、**実際のUnity Editorがそのassetをimportし、期待するPrefabやbuildへ到達したか**までは確認できません。

さらにUnityはasset fileのmetadataを管理するため、assetの作成・移動・削除を単純なfilesystem操作ではなくAsset Database経由で扱うよう案内しています。

Unity Manual — Asset Database:
https://docs.unity3d.com/ja/current/Manual/AssetDatabase.html

したがって、local taskは例えばこうなります。

```text
Issue
  ↓
FBX / texture / configを生成・更新
  ↓
Unity batchmode
  ↓
AssetDatabase import
  ↓
Editor scriptでPrefab / material / buildを検証
  ↓
exit code + Editor log + artifact
  ↓
Issue / PRへevidenceを返す
```

ここではPRのdiffだけでは足りません。

**Unityがそのassetを受理したというruntime evidence**が必要です。

---

## Blender：3D assetはPythonとbackground modeで機械処理できる

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

のようにできます。

background renderもcommand lineから実行できます。

```powershell
blender.exe \
  -b avatar.blend \
  -o //renders/frame_ \
  -f 1
```

この経路では、

- mesh処理
- scene設定
- exporter実行
- animation render
- preview生成
- project固有validation

をlocal taskへできます。

成果物は`.py`のdiffだけではなく、

```text
.blend
.fbx / .glb
texture
rendered PNG / WebP
validation JSON
```

です。

BlenderはPython auto executionをcommand lineからenable/disableするoptionも持っています。

Blender Manual:
https://docs.blender.org/manual/ja/5.0/advanced/command_line/arguments.html

したがって未知の`.blend`を無人処理する場合は、filesystemだけでなく**script execution policy**も境界になります。

---

## 画像・動画生成：local GPUそのものが実行環境になる

Hugging Face Diffusersは画像・動画・音声のgeneration pipelineを提供しており、modelをlocal folderから`from_pretrained()`で読み込めます。公式documentationはlocal pathを指定した場合、そのloadのためにHubからfileをdownloadしないことも説明しています。

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

です。

Diffusersはtext-to-videoを含むvideo generation pipelineも提供しています。

Hugging Face Diffusers — Pipelines:
https://huggingface.co/docs/diffusers/api/pipelines/overview

local machine側には、

```text
model weights
GPU / VRAM
input image / video
追加weight
生成途中のframe
生成済みvideo
```

があります。

これらを毎回cloud coding agentへ運ぶのではなく、**taskだけをcontrol planeから送り、dataとcomputeはlocalに残す**設計が合理的な場合があります。

DiffusersのStable Video Diffusion guideも、video generationをmemory intensiveな処理として扱い、CPU offloadやchunkingなどのmemory低減策を説明しています。

Hugging Face Diffusers — Stable Video Diffusion:
https://huggingface.co/docs/diffusers/main/using-diffusers/svd

ここではGPU、VRAM、model cacheまでがenvironmentです。

---

## FFmpeg：生成した後のasset processingもpipelineの一部

動画生成はmodelが`.mp4`を出したら終わりではありません。

実際には、

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

FFmpeg公式documentationは、複数inputをreadし、filter・transcodeしてoutputへwriteできるmedia converterとして`ffmpeg`を説明しています。`-filter_complex`では複数input/outputを持つfilter graphも構成できます。

FFmpeg Documentation:
https://ffmpeg.org/ffmpeg.html

FFmpeg Filters Documentation:
https://ffmpeg.org/ffmpeg-filters.html

数百MB〜数GBのmedia fileをGitHubへ運ばず、Issueには

```text
どのinputを
どのprofileで
どのoutputへ変換するか
```

というcontrol情報だけを置くことができます。

---

# 公開実例1：image2outfitでは、exit codeではなく「実画像」まで完了条件にした

一般論だけでは弱いので、実際の公開repositoryを見ます。

`KAFKA2306/image2outfit`は、SiroinoSotai_PC向け衣装をBlenderで制作し、編集可能source、FBX、Prefab宣言、render、研究記録を再現可能なworkspaceとして管理しています。

公開repository:
https://github.com/KAFKA2306/image2outfit

README:
https://github.com/KAFKA2306/image2outfit/blob/main/README.md

このprojectの`COMPLETE`は、単にBlender processが終了したことではありません。

READMEで要求しているものには、

- Blender生成成功
- 編集可能な制作source
- FBX
- Prefab資産の正規path宣言
- 正面・背面・左・右・斜めの実render
- 必須poseの実render
- 研究手法の試行記録
- 実画像を直接開いて確認する`visualAppearanceReview`

が含まれます。

さらに、各工程はresult JSONへ証拠fileのSHA-256を記録し、runner側で実fileのSHA-256を再計算して一致を確認します。

つまり、

```text
Blender exit 0
```

は必要条件であって、完成条件ではありません。

```text
source
  ↓
Blender execution
  ↓
editable source + FBX
  ↓
5方向 + pose render
  ↓
SHA-256 verification
  ↓
direct visual review
  ↓
COMPLETE
```

です。

これはlocal asset agentのcompletion contractとしてかなり重要です。

**binary assetは「存在する」だけではなく、生成経路・hash・見た目まで検証する。**

さらにこのrepositoryは、Unity import/save/reload、Modular Avatar、VRChat Build & Testなどを現在の`COMPLETE`条件から明示的に`OUT_OF_SCOPE`へ置いています。

つまり、実際にUnityを実行していない段階では「Unityで動作確認済み」と表現しません。

この区別は、agent workflowで非常に重要です。

```text
生成した
≠ importできた
≠ runtimeで動いた
≠ 人間が見て採用した
```

を混ぜないからです。

---

# 公開実例2：yt3では、FFmpegによる動画生成と「公開成功」を分離している

動画asset側にも公開実例があります。

`KAFKA2306/yt3`は、research、script、audio/visual production、audit、YouTube publishまでを扱うmedia production systemです。

README:
https://github.com/KAFKA2306/yt3/blob/main/README.md

production flowは、

```text
source / event
  → research
  → verified facts
  → script
  → audio / visual production
  → audit
  → channel routing audit
  → publish
  → publish receipt
  → public visibility audit
```

として分離されています。

video composerの実装では`fluent-ffmpeg`を使い、audio、複数overlay、thumbnail、subtitleをinputとしてcomplex filterを組み、codec・pixel format・audio codecを指定してoutput pathへ動画を書き出しています。

実装:
https://github.com/KAFKA2306/yt3/blob/main/src/domain/media/video_composer.ts

つまり、ここには実際に

```text
local / workspace media files
  ↓
FFmpeg composition
  ↓
video artifact
```

というasset processing layerがあります。

しかしYT3のREADMEでは、video file生成をpublication successとは扱いません。

公開成功には、少なくとも

- content artifact存在
- content audit pass
- profile / bucketの明示
- authenticated channel identityとの一致
- publish receipt
- public visibility audit

を要求しています。

これは動画系agentでありがちな

```text
mp4ができた
→ 成功
```

を否定しています。

```text
video generated
  ≠ audited
  ≠ correctly routed
  ≠ published
  ≠ publicly visible
```

だからです。

image2outfitとYT3は対象が違いますが、共通する設計原則があります。

> agentの説明ではなく、artifactとevidenceがstateを決める。

---

# 本当のlocal workflowは1つのtoolではなくchainになる

asset処理は1つのapplicationで完結しないことが多いです。

例えば、

```text
Issue
  ↓
Codex
  ↓
Diffusers / local GPU
  ↓
FFmpeg
  ↓
Blender
  ↓
Unity
  ↓
validation
  ↓
evidence bundle
```

というchainです。

ここで問題になるのはcode generationだけではありません。

- tool version
- binary asset
- local cache
- GPU
- application install
- SDK
- license / authentication
- intermediate artifact

の管理です。

したがってlocal bridgeは、単なるremote shellというより、

**repository外のcapabilityを、安全な範囲でagentへ貸し出すbroker**

と考えた方が正確です。

---

# asset pipelineでは「PRを作った」が完了条件にならない

coding agentの標準的なreviewable artifactはPull Requestです。

しかしasset pipelineでは、source codeに変更がないtaskもあります。

```text
同じBlender scriptで5方向renderを再生成する
既存modelから動画を生成する
FBXをUnityへimportしてcompatibilityを検証する
FFmpeg profileだけ変えてencode比較する
```

といった仕事です。

この場合、completion contractを広げます。

```text
execution
  tool exit code

provenance
  tool version
  input identifier / hash
  model / config identifier

artifact
  output path
  output hash
  file format

validation
  Unity import/build result
  Blender script result
  expected dimensions / codec / duration

visual evidence
  preview render
  representative frames

review
  source変更があればPR
  binary変更はartifact evidence
```

つまり、

```text
code workflow
  diff → PR → CI → review

asset workflow
  input → execution → binary artifact
        → machine validation
        → visual evidence
        → review
```

です。

AI automationでは、agentが「終わりました」と言ったことより、**再検証できるartifactが残ったこと**を成功条件にします。

---

# 一般原則1：Issueは「仕事の記録」であって「実行権限」ではない

GitHubはIssuesを、ideas、feedback、tasks、bugsなどを計画・追跡する仕組みとして説明しています。

GitHub Docs:
https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues

Issueはcontrol planeとして便利です。

- 誰が依頼したか残る
- 何を依頼したか残る
- commentで状態を追える
- PRやcommitと関連づけられる
- 人間が後から監査できる

しかしIssue commentをそのままshell command相当の権限へ変換すれば、Issueはremote execution interfaceになります。

```text
Issueに書かれている
```

ことと、

```text
その内容をmachine上で実行してよい
```

ことは別です。

asset pipelineの場合、commandの先にUnity、Blender、GPU、media encoderまで存在します。

execution authorityはIssueとは別に制御します。

---

# 一般原則2：promptより外側に境界を置く

OpenAIが公開しているCodexの安全運用では、managed configuration、constrained execution、network policies、logs、sandboxing、approvalsなどが独立したcontrolとして扱われています。

OpenAI — Running Codex safely at OpenAI:
https://openai.com/index/running-codex-safely/

AIへのpromptに

```text
危ないことはしないで
他のfolderは見ないで
```

と書くことは、強制境界ではありません。

```text
prompt rule
  AIへの依頼

sandbox / allowlist
  実行系による強制
```

は別物です。

asset pipelineではfilesystemだけでなくapplicationにも広げます。

```text
Codex
Unity
Blender
FFmpeg
```

だけを許可し、それ以外のbinaryを拒否するprocess allowlistまで持てると境界はさらに明確になります。

---

# 一般原則3：asset pipelineでは最小権限を6層で見る

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

動画generationへGPUを貸すことと、任意のlocal processを起動できることは同じ権限ではありません。

GitHub Copilot coding agentもinternet accessをfirewallで制御でき、GitHubはdata exfiltration riskの管理として説明しています。

GitHub Docs:
https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-the-firewall

入力だけでなく、**出ていくnetwork trafficとartifactも境界**です。

---

# 一般原則4：「自分のPCで動かす」はcloudより強い理由が必要

local executionには明確な利点があります。

- cloudへ置けないlocal data
- local GPU
- Unity / Blenderなどinstalled application
- local cache / SDK
- large media
- device / hardware

一方で実行環境は長寿命の実machineです。

GitHubはself-hosted runnerについて、ephemeralでcleanなVMである保証がなく、untrusted codeによって継続的にcompromiseされる可能性があると警告しています。

GitHub Docs — Secure use reference:
https://docs.github.com/en/actions/reference/security/secure-use

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

# 自作bridgeをこの基準でレビューする

現在のbridgeは、

```text
ChatGPT / sender
        ↓
private GitHub Issue
        ↓
Windows bridge daemon
        ↓
local Codex CLI
        ↓
final response + exit code + git evidence
        ↓
private GitHub Issue
```

という構成です。

実装:
https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/bridge-daemon.ps1

## Identity

comment authorのGitHub loginがinstallerで設定した`ControllerLogin`と一致し、所定のmarkerとJSON blockがある場合だけtaskとして扱います。

```text
正しい形式
AND
正しいmarker
AND
comment author == ControllerLogin
```

です。

private repositoryに入れることと、local PCへ命令できることを同一視しません。

## Filesystem

`cwd`はinstall時に設定した`AllowedRoot`配下だけです。

```text
AllowedRoot = D:\dev

OK
D:\dev\unity-project
D:\dev\video-pipeline

REJECT
C:\Users\...
D:\private-data
```

promptではなくPowerShell側で拒否します。

## Sandbox

既定は`read-only`で、許可値も

```text
read-only
workspace-write
```

だけです。

asset生成やUnity importにはwriteが必要ですが、write権限と任意application起動権限は本来別です。

Unity、Blender、FFmpegを本格的にbrokerするなら、次のhardening候補は

```text
filesystem sandbox
+
executable allowlist
+
tool-specific argument schema
```

です。

## Tool profile

bring-up時には、普段使いのCodex環境にある追加MCP/app層がOAuth認証を要求して無人実行が止まりました。

検証記録:
https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/VERIFICATION.md

そのためautonomous runでは

```text
--ignore-user-config
--disable apps
--disable plugins
```

を使い、interactive profileから分離しています。

同じ原則はUnity / Blenderにも使えます。

```text
人間向けenvironment
  多数のplugin / add-on / preference

agent向けenvironment
  固定version / 固定project / 固定entry point
```

の方が故障原因と権限を減らせます。

## Output

raw task resultにはlocal path、repository state、private task内容などが混ざり得ます。

asset pipelineならさらにmodel名、source media、render、build artifactが加わります。

```text
publicに出せるmetadata
privateに残すraw output
```

を分離します。

---

# E2Eの成功条件もassetごとに変える

2026-08-12のbridge verificationでは、

```text
worker exit_code = 0
final Codex message = BRIDGE_OK
```

の両方をsmoke成功条件にしました。

検証記録:
https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/VERIFICATION.md

asset pipelineへ広げるなら、もっと厳しくします。

### Unity

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

### Blender

```text
Codex exit 0
+
Blender Python exit 0
+
expected .blend / export存在
+
preview render存在
+
hash + visual review
```

### Video

```text
generation完了
+
FFmpeg完了
+
expected codec / resolution / duration確認
+
representative frame確認
```

**asset workflowは、agentの返答ではなく生成物を検査して終わる。**

---

# 残る弱点

## 長寿命のlocal machine

cloud agentのようなdisposable environmentではありません。

Unity、Blender、model weight、credentialが載ったmachineだからこそ、compromise時のblast radiusは大きくなります。

## network policy

filesystem root、sandbox、MCP allowlistはありますが、domain単位のnetwork allowlistをbridge独自に構築しているわけではありません。

model downloadやAPI利用を許すなら独立したnetwork policyが必要です。

## process allowlist

現行bridgeはUnity / Blender / FFmpeg専用brokerではありません。

本格運用なら、許可binary、version、project path、argumentをtask schemaとして固定する方が強くなります。

## `workspace-write`は採用承認ではない

agentがassetを書き換えられることと、そのassetを採用してよいことは別です。

source changeはPR、binary changeはhash・preview・machine validationを残し、人間が採否を判断できる形にします。

## GitHub accountがcontrol credentialになる

Issue commentを実行指示として使う以上、GitHub account、GitHub CLI authentication、repository accessがcontrol planeのcredentialです。

「private repositoryだから安心」では不十分です。

---

# 2026年時点での選び方

## repositoryだけで完結する

**GitHub上のcoding agent。**

```text
Issue / prompt
  ↓
cloud agent
  ↓
branch / PR
  ↓
CI + review
```

## 再現可能なbuild / testだけ必要

**GitHub-hosted Actions。**

## 特殊hardwareや社内networkだけlocalに必要

**self-hosted runner。**

ただしrunner isolationを先に設計します。

## Unity / Blender / 動画 / 3D assetのようにlocal stateそのものが仕事

**local bridgeが有力。**

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

この場合は、

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

までが設計対象です。

---

# 私たちが作ったのは「AIへの橋」ではなく、local capability brokerだった

Issueからagentへ仕事を渡すこと自体は、2026年には一般化しています。

local bridgeの独自性が出るのは、

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

そしてimage2outfitとYT3の実装を見ると、もう1つ共通する結論があります。

> agentの説明ではなく、artifactとevidenceがstateを決める。

AI coding agentを安全にするのは賢いpromptだけではありません。

agentの外側に置いた強制可能な境界と、再検証できる成果物です。

repositoryだけで完結するならcloud agent + PRを使う。

local stateが本当に必要なときだけbridgeを足す。

localへ入った瞬間、codeだけでなくapplication、GPU、asset、network、outputまで権限として設計する。

Unity、Blender、動画生成、実際のasset productionを考えると、local bridgeを作る理由はここにあります。

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

### 公開case study

- image2outfit
  https://github.com/KAFKA2306/image2outfit
- image2outfit README / completion contract
  https://github.com/KAFKA2306/image2outfit/blob/main/README.md
- YT3 README / media operation contract
  https://github.com/KAFKA2306/yt3/blob/main/README.md
- YT3 FFmpeg video composer
  https://github.com/KAFKA2306/yt3/blob/main/src/domain/media/video_composer.ts

### bridge実装

- Bridge implementation
  https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge
- Bridge daemon
  https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/bridge-daemon.ps1
- E2E verification
  https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/VERIFICATION.md
- Hardened autonomous-run commit
  https://github.com/KAFKA2306/KAFKA2306/commit/864774f15d7fc6522572a8e326dfa78573b0df74
