---
title: "GitHub IssueからAIにローカルPCを任せてよいのか？ Unity・Blender・動画生成で考える安全な橋"
emoji: "🔁"
type: "tech"
topics: ["codex", "github", "unity", "security", "automation"]
published: true
published_at: 2026-08-15 13:01
---

# GitHub IssueからAIにローカルPCを任せてよいのか？ Unity・Blender・動画生成で考える安全な橋

GitHub Issueに仕事を書き、AI coding agentに渡す。

2026年現在、この部分だけなら珍しい仕組みではありません。GitHub Copilotのcoding agentはIssueを受け取って作業し、Pull Requestを作成できます。GitHubはOpenAI Codexを含むthird-party coding agentsについても、Issueやpromptから仕事を委譲し、PRで人間がレビューする流れを提供しています。

- [GitHub Docs — Kick off a task with Copilot agents](https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/kick-off-a-task)
- [GitHub Docs — About third-party coding agents](https://docs.github.com/en/copilot/concepts/agents/about-third-party-coding-agents)

では、なぜ私はわざわざ次のような仕組みを作ったのでしょうか。

```text
GitHub Issue
  ↓
Windowsの常駐daemon
  ↓
ローカルCodex CLI
```

理由は単純です。

**コードだけならcloudで扱える。しかし、仕事がUnity、Blender、GPU、動画、3Dアセットまで広がると、リポジトリの外にあるローカル環境そのものが必要になる。**

たとえば、こんな仕事です。

- Unity EditorでFBXやTextureをimportし、Prefabやbuildを確認する
- Blenderで`.blend`を開き、Python処理やrenderを実行する
- ローカルGPUで画像・動画生成modelを動かす
- FFmpegで動画をfilter、transcode、muxする
- 数GB級の動画や3D assetをローカルディスク上で処理する
- 特定versionのEditor、SDK、cache、device、認証済み環境を使う

このときAIが触るものは、Gitのdiffだけではありません。

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

までが1つの実行環境になります。

この記事では、この自作bridgeを「AIからPCを操作できた」という成功談としては扱いません。

GitHubのcoding agentやActions、OpenAIが公開しているCodexの安全設計、Unity・Blender・FFmpeg・Hugging Face Diffusersの公式仕様、さらに実際に運用している3D衣装制作と動画制作の公開repositoryを照らし合わせながら、**AIにローカルのasset pipelineを任せるとき、何を境界として設計すべきか**を整理します。

公開実装: [KAFKA2306/KAFKA2306 — codex-chatgpt-bridge](https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge)

---

## 先に結論：コードだけならcloud、ローカル状態が必要ならlocal

最初に、使い分けを整理します。

| 方法 | 実行場所 | 向いている仕事 | 主な成果物 |
|---|---|---|---|
| GitHub Copilot / third-party coding agent | cloud | コード調査・修正・テスト | branch / PR / CI |
| GitHub Actions GitHub-hosted runner | ephemeral VM | 再現可能なbuild・test | log / package / artifact |
| GitHub Actions self-hosted runner | 自分のmachine | 特殊hardware・社内networkを使うCI | log / artifact |
| local bridge | 自分のPC | Unity、Blender、動画生成、local asset、device | code + binary asset + render + build evidence |

リポジトリの中だけで完結するなら、まず既存のcoding agentを使う方が自然です。

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

GitHubも、Copilotが生成したPRを通常のcontributionと同じように十分reviewするよう案内しています。

[GitHub Docs — Review output from Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/review-copilot-output)

つまり、**ローカルPCを実行環境にする理由がないなら、ローカルPCを使わない**。

ここは重要です。

一方、asset制作ではGitHub上のsourceだけでは表せない状態が大量にあります。その代表例がUnity、Blender、GPUによる生成処理、FFmpegです。

---

# なぜasset pipelineではローカル実行が必要になるのか

## Unity：Gitにあるassetと、Editorが見ている状態は同じではない

Unity Editorはcommand lineから`-batchmode`で起動し、`-executeMethod`でproject内のstatic methodを実行できます。Unity公式は、CI、test、build、data preparationなどの用途を案内しています。

[Unity Manual — Unity Editor command line arguments](https://docs.unity3d.com/ja/current/Manual/EditorCommandLineArguments.html)

たとえば、概念的には次のように実行できます。

```powershell
Unity.exe \
  -quit \
  -batchmode \
  -projectPath D:\dev\avatar-project \
  -executeMethod AssetPipeline.Build
```

ここで重要なのは、Unity projectが単なるGit repositoryではないことです。

UnityのAsset Databaseはsource assetをimportしてartifactを生成し、そのdatabaseをprojectの`Library` folderに保持します。Unityは`Library`をversion controlから除外するよう説明しています。

[Unity Manual — Asset Database](https://docs.unity3d.com/ja/current/Manual/AssetDatabase.html)

つまり、GitHubにある状態と、実際のUnity Editorが扱う状態には差があります。

```text
GitHub
  Assets/model.fbx
  Assets/material.mat
  Assets/texture.png
  ProjectSettings/...

ローカルUnity
  上記source
  + import結果
  + Library database
  + installed Editor
  + modules / SDK
  + machine固有の実行状態
```

cloud agentがC#やasset metadataを書き換えただけでは、**Unity Editorが本当にそのassetをimportできたか、Prefabやbuildまで到達できたか**は分かりません。

だからUnityでは、最終的にEditorを実行して確かめる工程が必要になります。

```text
Issue
  ↓
FBX / Texture / configを更新
  ↓
Unity batchmode
  ↓
Asset Databaseでimport
  ↓
Prefab / material / buildを検証
  ↓
Editor log + artifactを回収
```

ここではPRのdiffだけでは不十分です。

必要なのは、**Unityがそのassetを実際に受理したという証拠**です。

---

## Blender：3D assetはscriptとrenderまで含めて検証する

Blenderもローカル自動化と相性がよいtoolです。

Blender 5.0の公式manualでは、`-b` / `--background`でUIなしの実行ができ、`-P` / `--python`でPython scriptを起動できます。Python exception時のexit codeも指定できます。

[Blender Manual — Command Line Arguments](https://docs.blender.org/manual/ja/5.0/advanced/command_line/arguments.html)

```powershell
blender.exe \
  -b avatar.blend \
  --python-exit-code 1 \
  --python pipeline.py
```

renderもcommand lineから実行できます。

```powershell
blender.exe \
  -b avatar.blend \
  -o //renders/frame_ \
  -f 1
```

この仕組みを使えば、

- mesh処理
- scene設定
- exporter実行
- animation render
- preview生成
- project固有のvalidation

をローカルtaskとして扱えます。

そして成果物は`.py`のdiffだけではありません。

```text
.blend
.fbx / .glb
texture
rendered PNG / WebP
validation JSON
```

まで含まれます。

BlenderはPython auto executionをcommand lineからenable / disableするoptionも持っています。つまり、未知の`.blend`を無人で処理するなら、filesystemだけでなく**script executionも権限境界**として考える必要があります。

---

## 画像・動画生成：GPUとmodel cacheも環境の一部になる

生成AIでは、ローカル実行が必要になる理由がさらに分かりやすくなります。

Hugging Face Diffusersは画像・動画・音声のgeneration pipelineを提供しており、modelをlocal folderから`from_pretrained()`で読み込めます。公式documentationでは、local pathを指定した場合、その読み込みのためにHubからfileをdownloadしないことも説明されています。

[Hugging Face Diffusers — Loading pipelines](https://huggingface.co/docs/diffusers/en/using-diffusers/loading)

概念的には、次のような処理です。

```python
pipeline = DiffusionPipeline.from_pretrained(
    "D:/models/video-model",
    torch_dtype=torch.bfloat16,
    device_map="cuda",
)
```

Diffusersはvideo generation用pipelineも提供しています。

[Hugging Face Diffusers — Pipeline overview](https://huggingface.co/docs/diffusers/api/pipelines/overview)

このときローカル側には、

```text
model weights
GPU / VRAM
input image / video
追加weight
生成途中のframe
生成済みvideo
```

があります。

これらを毎回cloud側へ移すより、**指示だけを送って、dataとcomputeはローカルに残す**方が合理的な場合があります。

Stable Video Diffusionのguideでも、video generationをmemory intensiveな処理として扱い、CPU offloadやchunkingなどのmemory低減策が説明されています。

[Hugging Face Diffusers — Stable Video Diffusion](https://huggingface.co/docs/diffusers/main/using-diffusers/svd)

つまり、GPU、VRAM、model cacheまで含めて「実行環境」です。

---

## FFmpeg：動画は「生成した後」にも大量の処理がある

動画生成modelが`.mp4`を出したら終わり、ということはほとんどありません。

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

といった後処理が続きます。

FFmpegは複数inputを読み込み、filterやtranscodeを行い、outputへ書き出せます。`-filter_complex`では複数のinput / outputを持つfilter graphも構成できます。

- [FFmpeg Documentation](https://ffmpeg.org/ffmpeg.html)
- [FFmpeg Filters Documentation](https://ffmpeg.org/ffmpeg-filters.html)

この種の処理では、数百MBから数GBのmedia fileをGitHubへ移す必要はありません。

Issueには、

```text
どのinputを
どのprofileで
どのoutputへ変換するか
```

という指示だけを置き、実データはローカルで処理できます。

---

# 実例1：image2outfitでは「Blenderが終了した」だけでは完成にしない

一般論だけでは分かりにくいので、実際の公開projectを見ます。

[`KAFKA2306/image2outfit`](https://github.com/KAFKA2306/image2outfit)は、SiroinoSotai_PC向け衣装をBlenderで制作し、編集可能source、FBX、Prefab宣言、render、研究記録を1つの再現可能なworkspaceで管理するprojectです。

[image2outfit README](https://github.com/KAFKA2306/image2outfit/blob/main/README.md)

このprojectでは、Blender processが正常終了しただけでは`COMPLETE`になりません。

必要なのは、

- Blender生成成功
- 編集可能な制作source
- FBX
- Prefab資産の正規path宣言
- 正面・背面・左・右・斜めの実render
- 必須poseの実render
- 研究手法の試行記録
- 実画像を直接開いて確認する`visualAppearanceReview`

です。

さらに各工程はresult JSONへ証拠fileのSHA-256を記録し、runnerが実fileのSHA-256を再計算して一致を確認します。

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

このprojectから得られる教訓は明快です。

**binary assetは「存在する」だけでは足りない。生成経路、hash、見た目まで確認する。**

もう1つ重要なのは、確認していないことを「確認済み」と扱わないことです。

image2outfitでは、Unity import/save/reload、Modular Avatar、VRChat Build & Testなどを現在の`COMPLETE`条件から明示的に`OUT_OF_SCOPE`へ置いています。

そのため、実際にUnityを実行していない段階では「Unityで動作確認済み」とは表現しません。

```text
生成した
≠ importできた
≠ runtimeで動いた
≠ 人間が見て採用した
```

この状態を混ぜないことが、agent workflowでは重要です。

---

# 実例2：yt3では「動画ができた」と「公開できた」を分ける

動画側の実例が[`KAFKA2306/yt3`](https://github.com/KAFKA2306/yt3)です。

YT3はresearch、script、audio / visual production、audit、YouTube publishまでを扱うmedia production systemです。

[YT3 README](https://github.com/KAFKA2306/yt3/blob/main/README.md)

production flowは次のように分離されています。

```text
source / event
  ↓
research
  ↓
verified facts
  ↓
script
  ↓
audio / visual production
  ↓
audit
  ↓
channel routing audit
  ↓
publish
  ↓
publish receipt
  ↓
public visibility audit
```

video composerの実装では`fluent-ffmpeg`を使い、audio、複数overlay、thumbnail、subtitleをinputとしてcomplex filterを組み、動画を書き出しています。

[YT3 — video_composer.ts](https://github.com/KAFKA2306/yt3/blob/main/src/domain/media/video_composer.ts)

つまり実際に、

```text
local / workspace media files
  ↓
FFmpeg composition
  ↓
video artifact
```

というasset processing layerがあります。

しかし、YT3ではvideo file生成をpublication successとは扱いません。

公開成功には、少なくとも次を要求しています。

- content artifactが存在する
- content auditを通過する
- publish先のprofile / bucketが明示されている
- 認証済みchannel identityと意図が一致する
- publish receiptが残る
- public visibilityを確認する

つまり、

```text
video generated
  ≠ audited
  ≠ correctly routed
  ≠ published
  ≠ publicly visible
```

です。

image2outfitとYT3は対象が違いますが、設計思想は共通しています。

> **agentの説明ではなく、artifactとevidenceがstateを決める。**

これがlocal asset automationの中心原則です。

---

# コードとassetでは「完了」の形が違う

coding agentの標準的な成果物はPull Requestです。

コードなら、

```text
diff
  ↓
PR
  ↓
CI
  ↓
review
```

でかなりの部分を検証できます。

しかしasset pipelineでは、source codeに変更がないtaskもあります。

たとえば、

- 同じBlender scriptで5方向renderを再生成する
- 既存modelから動画を生成する
- FBXをUnityへimportしてcompatibilityを確認する
- FFmpeg profileだけ変えてencodeを比較する

といった仕事です。

この場合、完了条件は次のように広げる必要があります。

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
  Unity import / build result
  Blender script result
  expected dimensions / codec / duration

visual evidence
  preview render
  representative frames

review
  source変更ならPR
  binary変更ならartifact evidence
```

要するに、

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

**agentが「終わりました」と返したことではなく、あとから再検証できる成果物が残ったことを成功条件にする。**

ここがコード中心の自動化との大きな違いです。

---

# local bridgeは何を守るべきか

ここまでの具体例から、安全設計を整理します。

## 1. Issueは仕事の記録であって、実行権限ではない

GitHub Issuesは、ideas、feedback、tasks、bugsなどを計画・追跡するための機能です。

[GitHub Docs — About issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues)

Issueはcontrol planeの入口として便利です。

- 誰が依頼したか残る
- 何を依頼したか残る
- commentで状態を追える
- PRやcommitと関連づけられる
- 後から監査できる

ただし、Issue commentをそのままshell command相当の権限に変換すれば、Issueはremote execution interfaceになります。

```text
Issueに書かれている
```

ことと、

```text
その内容をmachine上で実行してよい
```

ことは別です。

特にasset pipelineでは、その先にUnity、Blender、GPU、media encoderまで存在します。

**collaboration権限とexecution権限は分ける必要があります。**

---

## 2. 「危ないことをしないで」は安全境界ではない

OpenAIが公開しているCodexの安全運用では、managed configuration、constrained execution、network policies、logs、sandboxing、approvalsなどが独立したcontrolとして扱われています。

[OpenAI — Running Codex safely at OpenAI](https://openai.com/index/running-codex-safely/)

AIへのpromptに、

```text
他のfolderは見ないで
危険な操作はしないで
```

と書くことはできます。

しかし、これはお願いです。

```text
prompt rule
  AIへの指示

sandbox / allowlist
  実行系による強制
```

は別物です。

asset pipelineなら、filesystemに加えて「どのapplicationを起動してよいか」まで制御対象になります。

---

## 3. 最小権限は6層に分ける

local asset agentでは、少なくとも次の6層を分けて考えると整理しやすくなります。

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

たとえば、「動画生成のためにGPUを使ってよい」と「任意のlocal processを起動してよい」は同じ権限ではありません。

GitHub Copilot coding agentもinternet accessをfirewallで制御でき、GitHubはdata exfiltration riskの管理として説明しています。

[GitHub Docs — Customize the firewall](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-the-firewall)

入力だけでなく、**外へ出ていくnetwork trafficとartifactも境界**です。

---

## 4. local machineは長寿命だからこそ慎重に扱う

local executionには、cloudにはない強みがあります。

- cloudへ置けないlocal data
- local GPU
- Unity / Blenderなどのinstalled application
- local cache / SDK
- large media
- device / hardware

しかし、そのmachineはcloud agentのような使い捨て環境ではありません。

GitHubもself-hosted runnerについて、ephemeralでcleanなVMである保証がなく、untrusted codeによって継続的にcompromiseされる可能性があると警告しています。

[GitHub Docs — Secure use reference for GitHub Actions](https://docs.github.com/en/actions/reference/security/secure-use)

違いを単純化すると、こうです。

```text
cloud agent
  disposableな作業環境へ仕事を持っていく

local bridge
  長寿命のmachineへ仕事を持ってくる
```

だからlocal bridgeは「便利だから使う」のではなく、**local stateそのものが仕事の一部であるときに使う**のが妥当です。

---

# 実際のbridgeをこの基準で見る

現在のbridgeは次の構成です。

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

実装: [bridge-daemon.ps1](https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/bridge-daemon.ps1)

安全境界を表にすると、現在は次のようになっています。

| 境界 | 現在の実装 |
|---|---|
| 誰が命令できるか | `ControllerLogin`と一致するGitHub userだけ |
| どこを触れるか | `AllowedRoot`配下だけ |
| 通常のsandbox | `read-only` |
| 書き込み | 明示した`workspace-write`だけ |
| Codex profile | user config / apps / pluginsから分離 |
| local MCP | hard-coded allowlist + task単位opt-in |
| raw result | local/private側に保持 |

### Identity

所定のmarkerとJSON blockがあり、comment authorが`ControllerLogin`と一致した場合だけtaskになります。

```text
正しい形式
AND
正しいmarker
AND
comment author == ControllerLogin
```

private repositoryに入れることと、ローカルPCへ命令できることを同一視していません。

### Filesystem

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

これはpromptではなくPowerShell側で拒否します。

### Sandbox

既定は`read-only`で、許可値も次の2つだけです。

```text
read-only
workspace-write
```

ただし、asset生成やUnity importへ広げるなら、filesystem writeとapplication起動権限を分けた方が強くなります。

今後のhardening候補は、

```text
filesystem sandbox
+
executable allowlist
+
tool-specific argument schema
```

です。

### Tool profile

bring-up時には、普段使いのCodex環境にある追加MCP / app層がOAuth認証を要求し、無人実行が停止しました。

[Verification record](https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/VERIFICATION.md)

そのためautonomous runでは、

```text
--ignore-user-config
--disable apps
--disable plugins
```

を使い、人間が普段使うinteractive profileから分離しています。

同じ発想はUnityやBlenderにも使えます。

```text
人間向けenvironment
  多数のplugin / add-on / preference

agent向けenvironment
  固定version / 固定project / 固定entry point
```

無人実行では、便利さより再現性と権限の小ささを優先した方が扱いやすくなります。

### Output

raw resultにはlocal path、repository state、private task内容などが含まれる可能性があります。

asset pipelineなら、さらにmodel名、source media、render、build artifactも加わります。

そのため、

```text
外へ出してよいmetadata
privateに残すraw output
```

を分離します。

---

# 成功条件はtoolごとに変える

2026-08-12のbridge smoke testでは、

```text
worker exit_code = 0
final Codex message = BRIDGE_OK
```

の両方を成功条件にしました。

[Bridge verification record](https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/VERIFICATION.md)

しかし、asset pipelineへ広げるならこれだけでは足りません。

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

共通する考え方は1つです。

**asset workflowは、agentの返答ではなく生成物を検査して終わる。**

---

# 現在のbridgeに残る弱点

このbridgeは「安全になった」のではなく、境界を増やして危険を狭めている途中です。

特に残る課題は次の4つです。

### 長寿命のlocal machine

Unity、Blender、model weight、credentialが載った実machineなので、compromise時の影響範囲はcloudの使い捨て環境より大きくなります。

### network policy

filesystem root、sandbox、MCP allowlistはありますが、domain単位のnetwork allowlistをbridge独自に持っているわけではありません。model downloadや外部API利用を許すなら、network policyは別に設計する必要があります。

### process allowlist

現行bridgeはUnity / Blender / FFmpeg専用brokerではありません。本格運用なら、許可binary、version、project path、argumentをtask schemaとして固定する方が安全です。

### `workspace-write`は採用承認ではない

agentがassetを書き換えられることと、そのassetを採用してよいことは別です。source changeならPR、binary changeならhash・preview・machine validationを残し、人間が採否を判断できる形にします。

また、Issue commentを実行指示として使う以上、GitHub account、GitHub CLI authentication、repository accessそのものがcontrol planeのcredentialになります。

「private repositoryだから安心」では不十分です。

---

# では、どの方法を選ぶべきか

判断基準はかなり単純です。

### リポジトリだけで完結する

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

### 再現可能なbuild / testだけが必要

**GitHub-hosted Actionsを使う。**

### 特殊hardwareや社内networkだけローカルに必要

**self-hosted runnerを検討する。**

ただしrunner isolationを先に設計します。

### Unity / Blender / 動画 / 3D assetのようにlocal stateそのものが仕事

**local bridgeが候補になる。**

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

この場合は、少なくとも次を設計対象にします。

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

---

# 作ったのは「AIへの橋」ではなく、local capability brokerだった

Issueからagentへ仕事を渡すこと自体は、2026年には一般的なworkflowになっています。

自作bridgeに意味が出るのは、その先です。

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

このときbridgeは、単なるremote shellではありません。

**ローカルPCにしかない能力を、制限付きでagentへ貸し出す仕組み**です。

私はこれを`local capability broker`と考えるのが一番しっくりきます。

そして、image2outfitとYT3を実際に運用して分かったことは、さらに単純です。

> **agentの説明ではなく、artifactとevidenceがstateを決める。**

安全なAI automationを作るために重要なのは、賢いpromptだけではありません。

agentの外側に置いた、突破できない境界。

そして、あとから再検証できる成果物です。

コードだけならcloud agent + PRを使う。

ローカル状態が本当に必要なときだけbridgeを足す。

そしてlocalへ入った瞬間、codeだけでなくapplication、GPU、asset、network、outputまで権限として設計する。

Unity、Blender、動画生成のようなasset productionを考えると、ローカルbridgeを作る理由はそこにあります。

---

## 一次情報・実装証拠

### GitHub

- [About issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues)
- [Kick off a task with Copilot agents](https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/kick-off-a-task)
- [About third-party coding agents](https://docs.github.com/en/copilot/concepts/agents/about-third-party-coding-agents)
- [Review output from Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/review-copilot-output)
- [Customize Copilot firewall](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-the-firewall)
- [Secure use reference for GitHub Actions](https://docs.github.com/en/actions/reference/security/secure-use)

### OpenAI

- [Running Codex safely at OpenAI](https://openai.com/index/running-codex-safely/)

### Unity

- [Unity Editor command line arguments](https://docs.unity3d.com/ja/current/Manual/EditorCommandLineArguments.html)
- [Asset Database](https://docs.unity3d.com/ja/current/Manual/AssetDatabase.html)
- [AssetDatabase.ImportAsset](https://docs.unity3d.com/ja/current/ScriptReference/AssetDatabase.ImportAsset.html)

### Blender

- [Blender 5.0 Manual — Command Line Arguments](https://docs.blender.org/manual/ja/5.0/advanced/command_line/arguments.html)

### FFmpeg

- [ffmpeg Documentation](https://ffmpeg.org/ffmpeg.html)
- [FFmpeg Filters Documentation](https://ffmpeg.org/ffmpeg-filters.html)

### Hugging Face Diffusers

- [Loading pipelines](https://huggingface.co/docs/diffusers/en/using-diffusers/loading)
- [Pipeline overview](https://huggingface.co/docs/diffusers/api/pipelines/overview)
- [Stable Video Diffusion](https://huggingface.co/docs/diffusers/main/using-diffusers/svd)

### 公開case study

- [image2outfit](https://github.com/KAFKA2306/image2outfit)
- [image2outfit README / completion contract](https://github.com/KAFKA2306/image2outfit/blob/main/README.md)
- [YT3 README / media operation contract](https://github.com/KAFKA2306/yt3/blob/main/README.md)
- [YT3 FFmpeg video composer](https://github.com/KAFKA2306/yt3/blob/main/src/domain/media/video_composer.ts)

### bridge実装

- [Bridge implementation](https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge)
- [Bridge daemon](https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/bridge-daemon.ps1)
- [E2E verification](https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/VERIFICATION.md)
- [Hardened autonomous-run commit](https://github.com/KAFKA2306/KAFKA2306/commit/864774f15d7fc6522572a8e326dfa78573b0df74)