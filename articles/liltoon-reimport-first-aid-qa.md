---
title: "VRだけ二重に見えた。lilToonをReimportする前にUploaderをA/Bすべきだった"
emoji: "👁️"
type: "tech"
topics: ["vrchat", "unity", "liltoon", "shader", "vrcsdk"]
published: true
published_at: 2026-08-12 19:12
---

# VRだけ二重に見えた。lilToonをReimportする前にUploaderをA/Bすべきだった

> **2026-08-12 23:47 JST 追記**  
> この記事の初版は「るるね本体と追加モデルの両方でVR左右眼異常が出るなら、共通lilToon Shaderを1個だけReimportする」を最初の一手としていました。今回の実機切り分けでは、その順序が誤っていました。**標準のVRChat SDK Control Panelからアップロードした経路では正常になり、Continuous Avatar Uploader（CAU）経路で問題が再現したため、最初に比較すべき変数はShaderではなくUploader / build-upload pipelineでした。**

この修正版では、Reimportを削除はしません。ただし順位を下げます。

```text
誤った初動
VRだけ二重
→ lilToon / Stereo Shaderを疑う
→ Shader Reimport
→ Material / MA / NDMFへ拡大

改善後
VRだけ二重
→ 同一Avatarを標準VRCSDKと第三者UploaderでA/B
→ Upload/build経路で結果が分岐するか確認
→ 分岐しない場合だけShader / Material / Built stateへ進む
```

この変更には一次情報上の理由もあります。

anatawa12氏が2026年1月13日に公開した `SimpleAvatarUploader.cs` は、Continuous Avatar Uploaderと同じ方法で互換性を試験するための最小Uploaderだと説明し、CAUが `IVRCSdkAvatarBuilderApi.Build` でbuildし、`VRCApi.UpdateAvatarBundle` でbundleをuploadすると明記しています。

- https://gist.github.com/anatawa12/029f749b527ed0a8d6dc853a5bcf9b94

一方、VRChat公式SDKはControl Panelから `Build & Publish` を提供しています。さらにSDK 3.9.0の公式リリースノートは、組み込みUI利用者とtool authorを明示的に分け、tool authorには `BuildAndUpload` と、手動の `Build` / `Upload` 系APIで異なる注意点があると説明しています。

- https://creators.vrchat.com/avatars/creating-your-first-avatar/
- https://creators.vrchat.com/releases/release-3-9-0/

つまり、**「同じAvatarをアップロードしたのだから、Uploaderは観測変数ではない」ではありません。** build / upload API経路そのものが比較対象です。

---

## Q1. 今回、最初に何を比較すべきだった？

同一のAvatar、同一Unity project、同一package stateを保ったまま、Uploaderだけを変えます。

```text
                 ┌─ VRChat SDK Control Panel → VR確認
同一Avatar ──────┤
                 └─ Continuous Avatar Uploader → VR確認
```

見るのは「どちらも成功したか」ではなく、**VR左右眼の結果がどこで `NORMAL → ABNORMAL` に分岐するか**です。

### 最小Observation Matrix

| 条件 | 結果 |
|---|---|
| Unity Scene | NORMAL / ABNORMAL |
| VRCSDK Build & Publish | NORMAL / ABNORMAL |
| CAU upload | NORMAL / ABNORMAL |
| VR Left Eye | NORMAL / ABNORMAL |
| VR Right Eye | NORMAL / ABNORMAL |
| VRChat Mirror | NORMAL / ABNORMAL |

Uploaderを変える試験中は、Material、Shader、Prefab、Animator、MA componentを同時に変更しません。

---

## Q2. CAUと標準VRCSDKで本当に差が出ることはある？

あります。少なくとも「第三者tool経路だけで互換性異常が出る」という事例はCAU自身のIssueにあります。

Continuous Avatar Uploader Issue #154は2026年5月4日に、VRCFuryのShader Optimizer関連エラーが **VRC SDKからのuploadでは出ず、CAUからのuploadでのみ出る** と報告しています。

- https://github.com/anatawa12/ContinuousAvatarUploader/issues/154

このIssueは今回の「左右眼二重表示」と同じ症状ではありません。したがって #154 を今回の直接原因の証拠として使ってはいけません。

ただし、次の一点は直接確認できます。

> **同一Avatar周辺でも、標準VRCSDK経路とCAU経路で結果が分岐する互換性問題は実在する。**

これだけで、Uploader A/Bを診断の上流に置く理由として十分です。

---

## Q3. ではlilToonのReimportは無意味だった？

無意味とは限りません。ただし今回のようにUploader差で結果が分岐する場合、**最初に行う操作ではありません。**

UnityにはAssetのmanual Reimport機能があります。

- https://docs.unity3d.com/Manual/ImporterConsistency.html

lilToonの通常Shader assetも公式repositoryで確認できます。

- `lts.shader`: https://github.com/lilxyzw/lilToon/blob/master/Assets/lilToon/Shader/lts.shader
- Shader directory: https://github.com/lilxyzw/lilToon/tree/master/Assets/lilToon/Shader

したがって、次の条件なら1ファイルReimportは依然として有効な診断です。

```text
標準VRCSDKでも異常
AND
第三者Uploaderでも異常
AND
問題Materialが同じShader経路を共有
```

このとき初めて、実際に使われている `lts*.shader` を1個だけReimportし、VR結果を再測定します。

---

## Q4. なぜ最初の診断が外れた？

観測「VRだけ二重」から、原因候補「Stereo Shader」へ飛びすぎたからです。

DesktopとVRで描画条件が異なること自体は正しいです。UnityはStereo RenderingとSingle Pass Instanced向けcustom Shaderの要件を公式に説明しています。

- https://docs.unity3d.com/2022.3/Documentation/Manual/SinglePassStereoRendering.html
- https://docs.unity3d.com/Manual/SinglePassInstancing.html

しかし、

```text
VRだけで壊れる
```

から直接、

```text
Shader sourceが壊れている
```

とは言えません。

実際のpipelineは少なくとも次です。

```text
Source Avatar
  ↓
Build processing
  ↓
Bundle generation
  ↓
Uploader / SDK API path
  ↓
VRChat backend
  ↓
VR runtime / stereo rendering
  ↓
見た目
```

今回抜けていたのは **Uploader / SDK API path** でした。

---

## Q5. 今後の「最初の10分」はどうする？

### Step 1: Sourceを固定

- 同一Prefab
- 同一Material
- 同一Shader package
- 同一Unity session
- 同一target platform

### Step 2: 標準VRCSDKでbuild / upload

VRChat公式の `VRChat SDK > Show Control Panel > Builder` から `Build & Publish` を使います。

- https://creators.vrchat.com/avatars/creating-your-first-avatar/

### Step 3: 実HMDで確認

左右眼、Direct view、Mirrorを記録します。

### Step 4: CAUで同一Avatarをupload

他の条件を変えません。

CAUは複数Avatarを連続uploadするtoolとして公開されています。

- https://github.com/anatawa12/ContinuousAvatarUploader

### Step 5: 結果を分類

```text
VRCSDK NORMAL / CAU ABNORMAL
→ Uploader/build-upload pipelineを最優先

VRCSDK ABNORMAL / CAU ABNORMAL
→ 共通のSource / Build / Shader / Runtimeへ進む

VRCSDK NORMAL / CAU NORMAL
→ 再現条件不足。別変数を増やさず再現条件を取り直す
```

---

## Q6. Uploader差が出なかったら次は？

ここで初めて、次の順序へ進みます。

1. Renderer / Material identity
2. Built Avatarとの差分
3. 問題Materialのfeature
4. Shader variant / Stereo compatibility
5. 必要なら対象Shader asset 1個だけReimport
6. package version A/B

一度に全部変更しません。

---

## 壊れた失敗例

今回の初版は、るるね本体と追加モデルの両方で異常が出たため、「共有lilToon経路」を最上流に置きました。

```text
複数Avatarで異常
→ 共通lilToon
→ lts.shader Reimport
```

共有依存を見る発想自体は悪くありません。しかし **「同じUploaderを使っている」も共有依存** です。そこを候補集合から落としたため、診断木が偏りました。

---

## 改善後の例

同じ症状が出たら、まず次だけ行います。

```text
A: VRCSDK標準 upload
B: CAU upload
```

AとBでVR結果が分かれた時点で、Shader編集を止められます。

これは非常に大きな差です。MaterialやShaderを変更する前に故障境界が一段上流へ確定するためです。

---

## 読者が再現できる最小テスト

1. 問題Avatarを複製せず、まずgit commit等でsource stateを固定する。
2. 同じAvatarをVRChat SDK Control Panelから `Build & Publish` する。
3. VR Left / Right / Mirrorを記録する。
4. sourceを変更せず、CAUで同じAvatarをuploadする。
5. 同じVR条件で再確認する。
6. 結果が分岐したら、Shader / Material変更を行わずUploader経路の問題として切り分ける。
7. 分岐しなければ、初めてRenderer / Material / Shaderへ降りる。

---

## まとめ

今回の教訓は「CAUが常に悪い」ではありません。

正しい一般化はこれです。

> **Avatarの見た目に異常があるとき、SourceだけでなくBuild / Upload経路も独立した変数としてA/Bする。**

CAU作者自身が、CAUと同じupload方法を切り出したcompatibility test用Gistを公開しています。さらにCAU Issue #154には、VRC SDKとCAUで結果が分岐した実例があります。

したがって今後は、**Shader Reimportより先に「標準VRCSDK vs 第三者Uploader」を比較する**のが最初の一手です。

## 一次情報

- VRChat — Creating Your First Avatar: https://creators.vrchat.com/avatars/creating-your-first-avatar/
- VRChat SDK 3.9.0 release — tool author向けBuild/Upload API差: https://creators.vrchat.com/releases/release-3-9-0/
- VRChat — Public SDK API: https://creators.vrchat.com/sdk/public-sdk-api/
- anatawa12 — SimpleAvatarUploader.cs: https://gist.github.com/anatawa12/029f749b527ed0a8d6dc853a5bcf9b94
- Continuous Avatar Uploader: https://github.com/anatawa12/ContinuousAvatarUploader
- CAU Issue #154: https://github.com/anatawa12/ContinuousAvatarUploader/issues/154
- Unity — Stereo Rendering: https://docs.unity3d.com/2022.3/Documentation/Manual/SinglePassStereoRendering.html
- Unity — Single-pass instanced custom shaders: https://docs.unity3d.com/Manual/SinglePassInstancing.html
- Unity — Importer Consistency: https://docs.unity3d.com/Manual/ImporterConsistency.html
- lilToon `lts.shader`: https://github.com/lilxyzw/lilToon/blob/master/Assets/lilToon/Shader/lts.shader
