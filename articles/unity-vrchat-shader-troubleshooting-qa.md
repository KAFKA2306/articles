---
title: "Desktopは正常、VRだけ二重。原因をShader本体に決め打ちできない理由"
emoji: "🥽"
type: "tech"
topics: ["vrchat", "unity", "shader", "liltoon", "poiyomi"]
published: true
published_at: 2026-08-12 19:46
---

# Desktopは正常、VRだけ二重。原因をShader本体に決め打ちできない理由

過去のlilToon Issue #46では、**Desktopでは正常、VRChat Mirrorでも正常なのに、VRで直接見るとRefraction materialが壊れる**という報告がありました。

- lilToon Issue #46: https://github.com/lilxyzw/lilToon/issues/46

Poiyomiでも、Desktopでは正常なのにVRで二重に見えるIssue #4、Direct Stereoだけ左右眼のphaseがずれるIssue #24があります。

- Poiyomi Issue #4: https://github.com/poiyomi/PoiyomiToonShader/issues/4
- Poiyomi Issue #24: https://github.com/poiyomi/PoiyomiToonShader/issues/24

この3件だけでも、一つのことが分かります。

**「VRだけ壊れる」はStereo描画経路を疑う強い手掛かりですが、それ自体は「Shader sourceが犯人」という診断名ではありません。**

Material feature、compiled Shader Variant、AnimatorによるMaterial state、Modular Avatar / NDMFのbuild変換、最終Renderer状態のどこでも、VRでだけ露出する状態を作れます。

この記事は応急処置ではありません。まず1個のlilToon ShaderをReimportして切り分ける手順は、別記事に限定しています。

- 最初の10分の切り分け: `liltoon-reimport-first-aid-qa.md`

ここでは、**Reimportだけでは直らない、または原因層まで特定したいときに、どこを比較するか**だけを扱います。

---

## 1. 3つの過去事例を、症状の差だけで並べる

| 事例 | Desktop | Mirror | Direct VR | 主な症状 |
|---|---|---|---|---|
| Poiyomi #4 | NORMAL | - | ABNORMAL | avatarが二重に見える |
| Poiyomi #24 | NORMAL | NORMAL | ABNORMAL | Left / Right EyeでPanosphere phaseがずれる |
| lilToon #46 | NORMAL | NORMAL | ABNORMAL | Refraction materialがVRで壊れる |

一次情報:

- https://github.com/poiyomi/PoiyomiToonShader/issues/4
- https://github.com/poiyomi/PoiyomiToonShader/issues/24
- https://github.com/lilxyzw/lilToon/issues/46

ここで重要なのは、3件の内部原因を同一視することではありません。

**同じ「Desktop正常 / VR異常」という観測から、原因をShader package全体へ一足飛びに固定できない**ことです。

特にPoiyomi #24とlilToon #46ではMirrorが正常でもDirect VRが異常でした。

したがって、

```text
Mirrorで正常だった
        ↓
VRでも正常なはず
```

という推論は成立しません。

---

## 2. 症状が出る場所と、原因がある場所を分ける

最終的な見た目までを、診断に必要な粒度だけに縮めると次の4層です。

```text
Source Avatar
  Mesh / Renderer / Material / Shader / Animator / MA components
        ↓
Build Processing
  Modular Avatar / NDMF / animation transformation
        ↓
Built Avatar
  final Renderer / final Material state / Shader Variant
        ↓
Render Context
  Desktop / Mirror / Direct VR / Left Eye / Right Eye
        ↓
Symptom
```

Unity公式はShader Variantを、同じShaderの異なる条件に対応するprogram variationとして説明しています。

- Unity Manual — Shader variants: https://docs.unity3d.com/2022.3/Documentation/Manual/shader-variants.html

またStereo Renderingでは左右眼を別の描画条件として扱い、Single Pass Instanced対応のcustom ShaderではStereo用macroが必要です。

- Unity Manual — Stereo rendering: https://docs.unity3d.com/2022.3/Documentation/Manual/SinglePassStereoRendering.html
- Unity Manual — Single-pass instanced rendering and custom shaders: https://docs.unity3d.com/Manual/SinglePassInstancing.html

したがって、Desktopで正常だったという観測は、**左右眼を含むVR描画条件まで正常だった証明にはなりません。**

一方で、VRでだけ壊れたからといって、source Shaderだけを原因に固定することもできません。

---

## 3. ShaderとMaterialは排他的な原因ではない

lilToon #46は、Shader側のregressionとRefractionを使うMaterialが組み合わさった事例として読めます。

報告では、lilToon 1.3.5へ更新後にRefraction materialがVRで壊れ、1.3.4では正常でした。その後、報告者は修正版をVRで確認し、作者は1.3.6へ反映すると回答しています。

- Issue: https://github.com/lilxyzw/lilToon/issues/46
- 修正版VR確認: https://github.com/lilxyzw/lilToon/issues/46#issuecomment-1239775190
- 1.3.6への反映: https://github.com/lilxyzw/lilToon/issues/46#issuecomment-1242675841

Poiyomi #24も、症状はPanosphere / PanningというMaterial側で設定する機能に現れています。

つまり診断単位は、

```text
Shader package
```

では粗すぎます。

より有用なのは、

```text
Shader source
  × Material feature / property
  × compiled variant
  × Stereo context
```

です。

そのため、Materialを確認するときは「同じMaterial名か」ではなく、**どのfeatureをON/OFFしたときにNORMAL→ABNORMALが切り替わるか**を見ます。

一度に全部OFFにすると、どの変数が効いたか分からなくなります。

---

## 4. Source Avatarが正常でも、Built Avatarは同じとは限らない

Modular Avatarはbuild時やPlay Modeでcomponentに基づく変換を適用します。公式のManual Processingでは、`Manual bake avatar` により変換適用後のavatar copyを生成できると説明しています。

- Modular Avatar — Manual processing: https://modular-avatar.nadena.dev/docs/manual-processing

さらにMaterialを変更するReactive Componentもあります。

- Material Setter: https://modular-avatar.nadena.dev/docs/reference/reaction/material-setter
- Material Swap: https://modular-avatar.nadena.dev/docs/reference/reaction/material-swap
- Reactive Components: https://modular-avatar.nadena.dev/docs/reference/reaction

NDMFもbuild processingをphaseに分け、`Transforming` phaseをavatar transformation用として定義しています。

- NDMF BuildPhase: https://ndmf.nadena.dev/api/nadena.dev.ndmf.BuildPhase.html

したがって、Unityのsource状態でMaterialが正常でも、

```text
Source Material
      ↓
Animator / MA / NDMF
      ↓
Built Material / Renderer
      ↓
Direct VRでだけ異常
```

という経路は残ります。

MA / NDMFを疑うときは、「componentがあるか」だけではなく、**SourceとBake後でRenderer / Material assignment / propertiesが変わったか**を比較します。

---

## 5. 今回の症状で、確定していることと未確定なこと

今回の観測として確実に扱えるのは、複数対象でVR上の見え方に異常が認識され、lilToonのReimportやasset更新を試しても、通常の見た目だけでは原因を確定できていないことです。

一方、まだ切り分ける必要があるのは次です。

- 本当に「二重」なのか
- Left Eye / Right Eyeのどちらでどう違うか
- Direct VRだけなのか
- Mirrorでも再現するか
- Desktop directでは再現しないか
- 問題箇所のMaterial / featureが共通なのか
- MA / NDMF build後に何が変わっているか
- duplicate Rendererが存在するか
- Shader compile errorが存在するか

したがって、現時点での診断は、

> **VR-only / eye-dependentな描画経路で故障が露出している可能性は高いが、原因層はShader sourceに限定できない。**

までです。

---

## 6. 複数の衣装・モデルで同時に壊れたら、共有上流を先に見る

一つの衣装だけなら、そのMaterialやMeshから見るのが自然です。

しかし複数の独立対象で同じ時期に症状が出るなら、個別対象より共有依存を先に調べる方が情報量があります。

候補は、

```text
同じlilToon package
同じUnity project
同じVRCSDK / build pipeline
共通Material / Animator
共通MA / NDMF processing
同じStereo render path
```

です。

これは「共通Shaderが犯人」と言っているのではありません。

**一度の比較で複数対象の説明力を持つ変数から調べる**という診断順序です。

---

## 7. Reimportで直らなかった後の診断順序

### Step 1: Observation Matrixを埋める

| Observation | Result |
|---|---|
| Unity Scene | NORMAL / ABNORMAL |
| Unity Game | NORMAL / ABNORMAL |
| VRChat Desktop direct | NORMAL / ABNORMAL |
| VR direct | NORMAL / ABNORMAL |
| VR Left Eye | NORMAL / ABNORMAL |
| VR Right Eye | NORMAL / ABNORMAL |
| VRChat Mirror | NORMAL / ABNORMAL |

最初に「どこから壊れるか」を固定します。

### Step 2: Renderer / Material / Shaderを静的確認する

- Missing Material
- Missing Shader
- `Hidden/InternalErrorShader`
- duplicate Renderer
- 共通Material
- 問題Materialで有効なview / screen-space依存feature

なお、Unity公式では通常のShaderで描画できない場合にDefault Error Shaderが使われ、magentaになることを説明しています。ピンク表示は二重表示とは別の症状クラスです。

- Unity Manual — Error and loading shaders: https://docs.unity3d.com/Manual/shader-error.html

### Step 3: Material featureを1つずつA/Bする

実際に使用しているfeatureだけを対象にします。

```text
Refraction
MatCap
Parallax
Panosphere / panning
screen-space系
FakeShadow
```

全部同時に変えません。

### Step 4: Material Swap / animationを確認する

AnimatorやMA Reactive Componentsで、runtime/build時にMaterialが変わっていないか確認します。

### Step 5: SourceとBuiltを比較する

Manual Bake等で変換適用後のcopyを作り、

```text
Source Renderer / Material
vs
Built Renderer / Material
```

を比較します。

### Step 6: versionをA/Bする

reimport回数ではなくversion差を変数にします。

lilToon #46のように、同じversionを何度reimportしてもversion regression自体は消えません。

---

## 8. やらない方がいいこと

### 「VRだけ二重だからShader」と決める

Stereo依存の疑いは上がりますが、Material / Built stateを飛ばしています。

### 「ShaderをReimportしたからShaderではない」と決める

version regressionや同一設定の再生成は残ります。

### 「Mirrorで正常だから直った」と判断する

Poiyomi #24とlilToon #46にはMirror正常 / Direct VR異常の報告があります。

### 「Unity上のMaterialが正常だからMAは無関係」と判断する

build後にMaterial / Renderer stateが変わる可能性があります。

### Shader、SDK、MA、Material、Libraryを一度に変える

直っても原因変数が残りません。

---

## まとめ

「VRだけ二重」は、原因名ではなく**故障境界を狭める観測**です。

過去のPoiyomi / lilToon Issueが示しているのは、DesktopやMirrorが正常でもDirect VRだけ壊れる故障モードが実際に存在することでした。

そこから先は、Shader packageを丸ごと疑うのではなく、

```text
Material feature
→ Source / Built state
→ Shader Variant
→ Direct VR / Left / Right Eye
```

のどこでNORMAL→ABNORMALへ変わるかを1変数ずつ取ります。

**原因名を当てるより、最初に結果が分岐する境界を見つける方が、次の操作を一意にできます。**

## 参考一次情報

### Unity

- Stereo rendering: https://docs.unity3d.com/2022.3/Documentation/Manual/SinglePassStereoRendering.html
- Single-pass instanced rendering and custom shaders: https://docs.unity3d.com/Manual/SinglePassInstancing.html
- Shader variants: https://docs.unity3d.com/2022.3/Documentation/Manual/shader-variants.html
- Error and loading shaders: https://docs.unity3d.com/Manual/shader-error.html

### lilToon

- Issue #46: https://github.com/lilxyzw/lilToon/issues/46

### Poiyomi Toon Shader

- Issue #4: https://github.com/poiyomi/PoiyomiToonShader/issues/4
- Issue #24: https://github.com/poiyomi/PoiyomiToonShader/issues/24

### Modular Avatar / NDMF

- Manual processing: https://modular-avatar.nadena.dev/docs/manual-processing
- Material Setter: https://modular-avatar.nadena.dev/docs/reference/reaction/material-setter
- Material Swap: https://modular-avatar.nadena.dev/docs/reference/reaction/material-swap
- Reactive Components: https://modular-avatar.nadena.dev/docs/reference/reaction
- NDMF BuildPhase: https://ndmf.nadena.dev/api/nadena.dev.ndmf.BuildPhase.html
