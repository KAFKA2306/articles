---
title: "Desktopは正常、VRだけ二重。真因はShaderではなくUploader経路だった"
emoji: "🥽"
type: "tech"
topics: ["vrchat", "unity", "shader", "liltoon", "vrcsdk"]
published: true
published_at: 2026-08-12 19:46
---

# Desktopは正常、VRだけ二重。真因はShaderではなくUploader経路だった

「VRだけ二重に見える」。

この症状から最初に疑ったのはStereo Shaderでした。PoiyomiやlilToonには、DesktopやMirrorでは正常でもDirect VRだけ壊れる過去事例が実際にあります。

- Poiyomi Issue #4: https://github.com/poiyomi/PoiyomiToonShader/issues/4
- Poiyomi Issue #24: https://github.com/poiyomi/PoiyomiToonShader/issues/24
- lilToon Issue #46: https://github.com/lilxyzw/lilToon/issues/46

しかし今回の実機切り分けでは、そこが真因ではありませんでした。

**同じAvatarを標準のVRChat SDK Control Panelからアップロードすると正常になり、Continuous Avatar Uploader（CAU）経路では問題が再現しました。**

つまり今回の故障境界は、少なくともShader sourceより上流の **build / upload pipeline差** にありました。

この記事は「CAU一般に左右眼バグがある」と主張するものではありません。今回得られた観測を、公開一次情報と照らしてどこまで一般化できるかを分けて整理します。

---

## 結論

今回の診断順序は、次のように更新します。

```text
旧
VR-only / eye-dependent
→ Shader / Material
→ Reimport
→ MA / NDMF
→ Built Avatar

新
VR-only / eye-dependent
→ 標準VRCSDK vs 第三者Uploader A/B
→ Build / Upload経路で分岐するか
→ 分岐しなければ Source / Built / Shaderへ降りる
```

最重要点は、**Uploaderを単なる最後の配送手段として扱わない**ことです。

VRChat公式SDKは、組み込みのControl PanelからAvatarを `Build & Publish` できます。

- https://creators.vrchat.com/avatars/creating-your-first-avatar/

一方、CAU作者anatawa12氏が2026年1月13日に公開した `SimpleAvatarUploader.cs` は、CAUと同じ方法でcompatibilityを検証するためのtoolだと明記し、CAUが `IVRCSdkAvatarBuilderApi.Build` と `VRCApi.UpdateAvatarBundle` を使うと説明しています。

- https://gist.github.com/anatawa12/029f749b527ed0a8d6dc853a5bcf9b94

さらにVRChat SDK 3.9.0公式リリースノートは、built-in UI利用とtool author向けAPI利用を分け、`BuildAndUpload` と手動 `Build` / `Upload` 系APIに異なる実装上の注意があると説明しています。

- https://creators.vrchat.com/releases/release-3-9-0/

したがって、Uploader / SDK API pathは独立した診断変数です。

---

## 1. なぜShader説はもっともらしかったのか

過去事例が実在したからです。

| 事例 | Desktop | Mirror | Direct VR | 症状 |
|---|---|---|---|---|
| Poiyomi #4 | NORMAL | - | ABNORMAL | Avatarが二重に見える |
| Poiyomi #24 | NORMAL | NORMAL | ABNORMAL | 左右眼でPanosphere phaseがずれる |
| lilToon #46 | NORMAL | NORMAL | ABNORMAL | Refraction materialがVRで壊れる |

一次情報:

- https://github.com/poiyomi/PoiyomiToonShader/issues/4
- https://github.com/poiyomi/PoiyomiToonShader/issues/24
- https://github.com/lilxyzw/lilToon/issues/46

UnityもStereo RenderingとSingle Pass Instanced custom Shaderの要件を公式に説明しています。

- https://docs.unity3d.com/2022.3/Documentation/Manual/SinglePassStereoRendering.html
- https://docs.unity3d.com/Manual/SinglePassInstancing.html

したがって、

```text
Desktop正常
VRだけ異常
```

からStereo経路を疑うこと自体は合理的でした。

問題は、**Stereo経路を疑うこと**と**Shader sourceを最初の原因に固定すること**を混同した点です。

---

## 2. 抜けていた層はUploaderだった

初版の診断モデルはこうでした。

```text
Source Avatar
  Mesh / Renderer / Material / Shader / Animator
        ↓
Build Processing
  Modular Avatar / NDMF
        ↓
Built Avatar
  final Renderer / Material / Shader Variant
        ↓
Render Context
  Desktop / Mirror / Direct VR / Left / Right
```

これは1層足りませんでした。

修正版はこうです。

```text
Source Avatar
        ↓
Build Processing
        ↓
Built Bundle
        ↓
Build / Upload API path
  VRCSDK Control Panel
  or third-party uploader
        ↓
VRChat backend
        ↓
Client / Stereo Rendering
        ↓
Symptom
```

今回、結果が分岐したのはこの `Build / Upload API path` を変えたときでした。

つまり、Shader、Material、Meshを変更するより前に、もっと大きな情報量を持つA/Bがありました。

---

## 3. CAUと標準VRCSDKで結果が分かれる前例はある

あります。ただし今回と同一症状ではありません。

Continuous Avatar Uploader Issue #154は、2026年5月4日にVRCFuryのShader Optimizer関連エラーについて、**VRC SDKからuploadした場合は出ず、CAUからuploadした場合だけ出る**と報告しています。

- https://github.com/anatawa12/ContinuousAvatarUploader/issues/154

Issue #154の症状は「Unlocked Shader」エラーであり、今回の左右眼二重表示とは別物です。

したがって、ここから言えるのは限定的です。

```text
言える:
標準VRCSDKとCAUで結果が分岐するcompatibility issueは実在する

言えない:
Issue #154と今回の左右眼異常が同じ内部原因である
```

この区別は重要です。

過去Issueは**原因の証明**ではなく、Uploaderを比較変数として扱う根拠です。

---

## 4. 最初に取るべきだったA/B

同一Avatarを使います。

```text
A. VRChat SDK Control Panel
   Build & Publish

B. Continuous Avatar Uploader
   upload
```

変更してはいけないもの:

- Avatar Prefab
- Material
- Shader
- MA component
- Animator
- Unity version
- target platform

比較するもの:

| 観測 | A: VRCSDK | B: CAU |
|---|---|---|
| upload/build成功 | PASS/FAIL | PASS/FAIL |
| VR Direct | NORMAL/ABNORMAL | NORMAL/ABNORMAL |
| Left Eye | NORMAL/ABNORMAL | NORMAL/ABNORMAL |
| Right Eye | NORMAL/ABNORMAL | NORMAL/ABNORMAL |
| Mirror | NORMAL/ABNORMAL | NORMAL/ABNORMAL |

ここでAとBが分岐すれば、Shaderを編集する前に故障境界を大きく狭められます。

---

## 5. `Build & Publish` は何を基準にする？

VRChat公式のAvatar作成手順では、Unityの `VRChat SDK > Show Control Panel` を開き、Builderタブから `Build & Publish Your Avatar Online` を選ぶ手順が案内されています。

- https://creators.vrchat.com/avatars/creating-your-first-avatar/

またVRChat公式はtool developer向けにPublic SDK APIを公開しています。

- https://creators.vrchat.com/sdk/public-sdk-api/

SDK 3.9.0では、組み込みUI利用者には変更なしとしつつ、tool authorにはcontent ID処理を含むAPI差について注意を出し、手動 `Build` / `Upload` よりcombined `BuildAndUpload` を強く推奨しています。

- https://creators.vrchat.com/releases/release-3-9-0/

この公式説明からも、**tool側のbuild/upload実装は診断対象になり得る**ことが分かります。

---

## 6. Shader / Materialはもう疑わなくていい？

違います。

Uploader A/Bで結果が分岐しなかった場合は、依然としてShader / Material / Built Avatarを調べます。

ただし順序が変わります。

```text
Step 1  Uploader A/B
Step 2  Renderer / Material identity
Step 3  Source vs Built
Step 4  Material feature A/B
Step 5  Shader stereo compatibility
Step 6  Shader asset 1個だけReimport
Step 7  package version A/B
```

この順序なら、最上流で説明できる変数を先に潰せます。

---

## 7. Source Avatarが正常でもBuilt Avatarは同じとは限らない

Uploader差がなければ、次はbuild transformationを見ます。

Modular Avatarはbuild時またはPlay Modeでcomponentに基づく変換を適用し、Manual Processingで変換後Avatar copyを生成できます。

- https://modular-avatar.nadena.dev/docs/manual-processing

NDMFもbuild processingをphaseとして扱います。

- https://ndmf.nadena.dev/api/nadena.dev.ndmf.BuildPhase.html

したがって、

```text
Source正常
→ MA / NDMF変換
→ Built state異常
```

は依然として有効な仮説です。

ただし、今回のように標準VRCSDKとCAUで結果が分岐したなら、ここへ降りる前にUploader層を固定するべきです。

---

## 8. Shader Reimportはどこに置く？

最初ではなく後段です。

Unityはmanual Reimportを公式に提供しています。

- https://docs.unity3d.com/Manual/ImporterConsistency.html

lilToonの通常Shader assetは公式repositoryで確認できます。

- https://github.com/lilxyzw/lilToon/blob/master/Assets/lilToon/Shader/lts.shader

Reimportが有効なのは、少なくとも次の条件を満たすときです。

```text
VRCSDKでもCAUでも異常
AND
Source / Built差だけでは説明できない
AND
問題Rendererが共通Shaderを使う
```

この条件で、実際に使用している `lts*.shader` を1個だけReimportします。

「VRだけ二重」という症状だけでは、Reimportを初手にしません。

---

## 9. 壊れた診断例

今回の失敗は、原因候補の粒度が細かすぎました。

```text
VR only
→ Stereo
→ Shader
→ lilToon
→ lts.shader
```

この推論は一見きれいですが、途中にある次の層を飛ばしています。

```text
Build / Upload API path
```

その結果、Shaderを再importしても、Materialを比較しても、故障境界を決められませんでした。

---

## 10. 改善後の診断例

同じ症状なら、まずこれだけ行います。

```text
同一Avatar
   ├─ VRCSDK → VR確認
   └─ CAU    → VR確認
```

もし、

```text
VRCSDK = NORMAL
CAU    = ABNORMAL
```

なら、次の作業はShader編集ではありません。

- CAU versionを記録
- VRChat SDK versionを記録
- CAU側build/upload pathのlogを取得
- 同一Avatarで再現
- CAUの既知compatibility Issueを確認
- 必要なら作者のSimpleAvatarUploaderでCAU方式を最小再現

anatawa12氏の `SimpleAvatarUploader.cs` はまさに「CAUと同じ方法で他toolとのcompatibilityを試す」ために公開されています。

- https://gist.github.com/anatawa12/029f749b527ed0a8d6dc853a5bcf9b94

---

## 11. 読者が試せる再現手順

### 前提

異常が出るAvatarが1体あるとします。

### A/Bテスト

1. git commit等でProject状態を固定する。
2. Unityを再起動しない。
3. Material / Shader / Prefabを変更しない。
4. VRChat SDK Control Panelから `Build & Publish` する。
5. 実HMDでDirect / Left / Right / Mirrorを記録する。
6. sourceを変更せずCAUで同一Avatarをuploadする。
7. 同じHMD、同じ確認条件で再測定する。
8. 結果が分岐したら、Uploader / build-upload pipelineを原因区間として扱う。
9. 分岐しなければ、Source / Built / Material / Shaderへ進む。

### 記録フォーマット

```text
Avatar:
Unity:
VRCSDK:
CAU:
Platform:

VRCSDK upload:
  Direct:
  Left:
  Right:
  Mirror:

CAU upload:
  Direct:
  Left:
  Right:
  Mirror:

Source changes between A/B: NONE
```

これだけで「何となくShaderが怪しい」という診断から脱出できます。

---

## 12. やってはいけないこと

### 「VRだけ二重だからShader」と確定する

Stereo依存の可能性は上がりますが、Uploader / Built stateを飛ばします。

### Shader、Material、CAU versionを同時に変える

直っても何が効いたか分かりません。

### `Reimport All` を初手にする

大量の状態を同時に変え、比較可能性を失います。

### Mirror正常だけで修正完了とする

過去のPoiyomi / lilToon IssueにはMirror正常・Direct VR異常の事例があります。

### CAU Issue #154を今回の直接原因と断定する

症状が異なります。使えるのは「標準SDKとCAUで結果が分岐する前例」の証拠までです。

---

## まとめ

今回いちばん大きかった発見は、Shaderの知識ではありません。

**診断木にUploaderが抜けていたこと**です。

VRChat Avatarの最終見た目は、Source Assetだけでは決まりません。

```text
Source
→ Build transformation
→ Bundle
→ Build / Upload API path
→ Backend
→ Client / Stereo
```

この全体を観測対象にする必要があります。

今回のような「Desktop正常 / VRだけ二重」では、過去のShader事例に引っ張られやすい。しかし、まず同じAvatarを **標準VRCSDKと第三者UploaderでA/B** すれば、はるかに上流で故障境界を切れます。

今後の第一手はこれです。

> **Shaderを触る前に、Uploaderを変えて結果が分岐するか測る。**

## 参考一次情報

### VRChat

- Creating Your First Avatar: https://creators.vrchat.com/avatars/creating-your-first-avatar/
- Public SDK API: https://creators.vrchat.com/sdk/public-sdk-api/
- SDK 3.9.0 release: https://creators.vrchat.com/releases/release-3-9-0/

### Continuous Avatar Uploader / anatawa12

- Continuous Avatar Uploader: https://github.com/anatawa12/ContinuousAvatarUploader
- CAU Issue #154: https://github.com/anatawa12/ContinuousAvatarUploader/issues/154
- SimpleAvatarUploader.cs: https://gist.github.com/anatawa12/029f749b527ed0a8d6dc853a5bcf9b94

### Unity / Shader

- Stereo rendering: https://docs.unity3d.com/2022.3/Documentation/Manual/SinglePassStereoRendering.html
- Single-pass instanced custom shaders: https://docs.unity3d.com/Manual/SinglePassInstancing.html
- Shader variants: https://docs.unity3d.com/2022.3/Documentation/Manual/shader-variants.html
- Importer consistency: https://docs.unity3d.com/Manual/ImporterConsistency.html

### Shader過去事例

- Poiyomi #4: https://github.com/poiyomi/PoiyomiToonShader/issues/4
- Poiyomi #24: https://github.com/poiyomi/PoiyomiToonShader/issues/24
- lilToon #46: https://github.com/lilxyzw/lilToon/issues/46
