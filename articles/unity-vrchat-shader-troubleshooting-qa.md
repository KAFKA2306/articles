---
title: "Unity / VRChatで『VRだけ二重に見える』をどう考えるか"
emoji: "🥽"
type: "tech"
topics: ["vrchat", "unity", "shader", "liltoon", "poiyomi"]
published: true
published_at: 2026-08-12 19:46
---

# Unity / VRChatで「VRだけ二重に見える」をどう考えるか

Unityでは普通に見える。Desktopでも大きな異常は分からない。しかしVRの人から見ると二重に見える、左右の目で違って見える、あるいは直接見ると崩れる。

こういうとき、最初に

> Shaderが壊れた

と決めるのは早すぎます。

一方で、

> Unityでは正常だからShaderではない

とも言えません。

過去のPoiyomi / lilToonのIssueを調べると、**Desktopでは正常なのにVRだけ二重になる、左右眼だけ結果が分岐する、Mirrorでは正常なのにDirect VRでは壊れる**という事例が実際にあります。

ただし、ここで重要なのは「VRだけ二重 = Shader故障」という短絡ではありません。

**VRだけで症状が出ることは、Stereo描画経路で問題が露出しているという強い手掛かりです。原因そのものはShader実装だけでなく、Material設定、Shader Variant、Material Swap、Modular Avatar / NDMFのbuild時変換、最終Renderer状態まで含みます。**

この記事では、過去事例からその仕組みを抽出し、最後に今回の事象へ戻ります。

---

## 1. 症状が出る場所と、原因がある場所は一致しない

最初の原則です。

> **VRでだけ壊れることはStereo経路を疑う根拠になる。しかし、Stereo経路で壊れる状態を作った原因がShader本体とは限らない。**

たとえば次の3ケースは、最終的に同じ見え方を作り得ます。

```text
A. Shader sourceのStereo対応が間違っている

B. Shader自体は正常だが、Material設定で
   Refraction / MatCap / Parallax等のview依存機能が有効になっている

C. Source状態は正常だが、build時に
   Material / Renderer / Animationが変換され、最終状態がStereoで破綻する
```

観測だけを見ると、どれも

```text
Desktop: NORMAL
VR:      ABNORMAL
```

になり得ます。

したがって、**症状分類と原因分類を分ける**必要があります。

---

## 2. 見た目を決めるのはMaterialだけでもShaderだけでもない

画面に最終的なpixelが出るまでを単純化すると、次のように考えられます。

```text
Source Avatar
  ├─ Mesh / Renderer
  ├─ Material
  ├─ Shader
  ├─ Animator
  └─ Modular Avatar / NDMF components
          ↓
      Build processing
          ↓
Built Avatar
  ├─ final Mesh / Renderer
  ├─ final Material assignment
  ├─ final Material properties
  ├─ final animation state
  ├─ Shader keywords
  └─ compiled Shader Variant
          ↓
Render Context
  ├─ Desktop / VR
  ├─ Direct / Mirror
  ├─ Left Eye / Right Eye
  └─ camera / screen-space inputs
          ↓
        Pixels
          ↓
       Symptom
```

概念的には、見た目 `P` は次のような関数です。

```text
P = f(
  BuiltMesh,
  BuiltRenderer,
  MaterialState,
  ShaderSource,
  ShaderVariant,
  BuildContext,
  RenderContext,
  Eye
)
```

このモデルにすると、

> 「同じMaterialなのになぜVRだけ違うの？」

という疑問が少し整理できます。

**Material名が同じでも、実際に実行されるShader Variantやcamera/eye入力が同じとは限らないからです。**

Unity公式はShader Variantを、同じShaderの異なる条件に対応するprogram variationとして説明しています。

一次情報:

- Unity Manual — Shader variants
  https://docs.unity3d.com/2022.3/Documentation/Manual/shader-variants.html

---

## 3. VRでは「どちらの目か」が描画条件に加わる

VRでは1枚の平面画像だけを描画するわけではありません。

UnityはStereo Renderingについて、Multi-passやSingle Pass Instancedなどの方式を説明しています。

- Multi-pass: 左右眼についてrender passを行う
- Single Pass Instanced: instanced draw callを利用して左右眼を扱う

一次情報:

- Unity Manual — Stereo rendering
  https://docs.unity3d.com/2022.3/Documentation/Manual/SinglePassStereoRendering.html

Single Pass Instanced対応のcustom Shaderでは、Unity公式ドキュメントに次のようなStereo用macroが示されています。

```text
UNITY_VERTEX_INPUT_INSTANCE_ID
UNITY_VERTEX_OUTPUT_STEREO
UNITY_SETUP_INSTANCE_ID()
UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO()
UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX()
```

`UNITY_SETUP_INSTANCE_ID()` は、現在どちらの目を描画しているかに応じて `unity_StereoEyeIndex` を設定します。

またscreen-space textureについても、Single Pass Instancedでは専用のsampling対応が必要です。

一次情報:

- Unity Manual — Single-pass instanced rendering and custom shaders
  https://docs.unity3d.com/Manual/SinglePassInstancing.html

ここから得られる原則は単純です。

> **Desktopで正常だったことは、VR左右眼の描画経路が正常であることを証明しない。**

---

## 4. 過去事例1：Desktop正常、VRだけ二重

Poiyomi Toon Shader Issue #4 `Seeing Double's` では、次の症状が報告されています。

- VRユーザーからはavatarが二重に見える
- 本人もVRでは二重に見える
- Desktopユーザーには正常

一次情報:

- Poiyomi Toon Shader Issue #4
  https://github.com/poiyomi/PoiyomiToonShader/issues/4

このIssue本文だけでは、内部原因が `unity_StereoEyeIndex` だったとまでは証明できません。

重要なのは、

> **同じupload済みavatarでもDesktopとVRで結果が分岐する故障モードが実在する**

ということです。

したがって「VRのみ二重」は、Stereo関連層へ調査範囲を狭める症状として使えます。

**原因名ではありません。**

---

## 5. 過去事例2：Left EyeとRight Eyeだけ結果が違う

Poiyomi Issue #24 `Panosphere Left/Right Eye Phase Issue` では、Panningのphaseが左眼と右眼でずれる症状が報告されています。

報告では、

```text
Direct Stereo → ABNORMAL
Desktop       → NORMAL
Mirror        → NORMAL
```

でした。

一次情報:

- Poiyomi Toon Shader Issue #24
  https://github.com/poiyomi/PoiyomiToonShader/issues/24

この事例が重要なのは、**Mirror正常もDirect VR正常の十分条件ではない**ことです。

さらに症状はPanosphere / PanningというMaterial側で設定する機能に現れています。

したがって、診断単位を単に

```text
Poiyomi
```

とするより、

```text
Poiyomi Shader
    ↓
Panosphere feature
    ↓
Material properties
    ↓
Stereo render context
```

と分解した方が原因へ近づけます。

---

## 6. 過去事例3：lilToonでもVR限定regressionがあった

lilToon Issue #46 `Refraction material broken in VR with 1.3.5` は、今回の考え方にかなり近い事例です。

報告内容は、

- lilToon 1.3.5への更新後に発生
- Refraction materialがVRで壊れる
- VRChat Mirrorでは正常
- Desktop modeでは正常
- VRでdirectに見ると異常
- lilToon 1.3.4では正常

でした。

一次情報:

- lilToon Issue #46
  https://github.com/lilxyzw/lilToon/issues/46

その後、報告者は修正版をVRで確認して正常になったと報告し、作者は修正を1.3.6へ反映すると回答しています。

- 修正版VRテスト
  https://github.com/lilxyzw/lilToon/issues/46#issuecomment-1239775190
- 1.3.6への反映
  https://github.com/lilxyzw/lilToon/issues/46#issuecomment-1242675841

ここでは、

**Shader側のregression**

と

**Refractionを使うMaterial**

が組み合わさっています。

つまり、ShaderとMaterialは原因候補として排他的ではありません。

> **Shader code × Material feature × Stereo context**

という組み合わせで故障面が作られます。

---

## 7. lilToon自身にもStereo / VR視差の修正履歴がある

lilToon公式CHANGELOGには、StereoやVR視差に関係する修正履歴があります。

例として、

- Refraction ShaderのSingle Pass Instanced環境での挙動修正
- VRでのFakeShadow parallax修正
- VR向けparallax関連調整

が記録されています。

一次情報:

- lilToon CHANGELOG
  https://github.com/lilxyzw/lilToon/blob/master/Assets/lilToon/CHANGELOG.md
- lilToon CHANGELOG_JP
  https://github.com/lilxyzw/lilToon/blob/master/Assets/lilToon/CHANGELOG_JP.md

このため、「lilToonが正常か異常か」という1bitの見方では粗すぎます。

```text
lilToon
  ├─ ordinary surface shading
  ├─ Refraction
  ├─ MatCap
  ├─ Parallax
  ├─ FakeShadow
  ├─ screen-space calculations
  └─ Stereo handling
```

特にcamera / view / screen-space / eyeに依存する機能は、Stereoで別の故障面を持ちます。

---

## 8. Materialは「色を入れる箱」ではない

MaterialはShaderを選ぶだけではありません。

Material側の状態によって、

- property値
- Texture
- featureの有効/無効
- Shader keyword
- Render Queue

などが変わります。

したがって、

> Shader package自体は正常だが、あるMaterial設定だけStereoで破綻する

という状態は構造的にあり得ます。

Poiyomi #24のPanosphereやlilToon #46のRefractionは、この境界を理解するための具体例です。

診断時に必要なのは、Shaderを丸ごと再installすることより、

> **どのMaterialの、どのfeatureをON/OFFしたときにNORMAL→ABNORMALが切り替わるか**

を見ることです。

---

## 9. Modular Avatar / NDMFも描画状態の上流にいる

ここが今回追加すべき重要な層です。

Modular Avatarは、avatar build時やPlay Modeでcomponentに基づく変換を適用します。公式のManual Processingページでは、`Manual bake avatar` により変換適用後のavatar copyを生成できると説明されています。

一次情報:

- Modular Avatar — Manual processing
  https://modular-avatar.nadena.dev/docs/manual-processing

つまり、Unity Hierarchyで見ているsource avatarと、build後に使われるavatar stateを区別する必要があります。

さらにModular Avatarには、Materialを直接変えるReactive Componentがあります。

### Material Setter

特定RendererのMaterialを変更します。

- https://modular-avatar.nadena.dev/docs/reference/reaction/material-setter

### Material Swap

avatar内のMaterialを別Materialへ置換します。

- https://modular-avatar.nadena.dev/docs/reference/reaction/material-swap

Reactive Components一覧にも、Material Setter / Material Swapが公式に記載されています。

- https://modular-avatar.nadena.dev/docs/reference/reaction

したがって、今回のような描画トラブルでは、

```text
Source Materialは正常
        ↓
MA / animation / build processing
        ↓
別Materialまたは別stateになる
        ↓
その最終stateだけStereoで破綻
```

という因果も除外できません。

NDMF自身もbuild processingをphaseに分けており、`Transforming` phaseは一般的なavatar transformation用で、公式API documentationはModular Avatarの多くのlogicがここで動くと説明しています。

一次情報:

- NDMF BuildPhase
  https://ndmf.nadena.dev/api/nadena.dev.ndmf.BuildPhase.html

したがって、**MA関連の可能性を調べるときはsource prefabだけでなくbuild/bake後のRenderer・Material状態を比較する**必要があります。

---

## 10. 「突然ピンク」は別の症状クラス

二重表示とピンク表示は分けて考えます。

Unity公式によれば、通常のShaderで描画できない場合にはDefault Error Shaderが使われ、magentaになります。

公式ドキュメントでは例として、

- Materialが割り当てられていない
- Shaderがcompileできない
- Shaderがsupportされていない

などが挙げられています。

一次情報:

- Unity Manual — Error and loading shaders
  https://docs.unity3d.com/Manual/shader-error.html

また必要なShader Variantがbuildからstripされ、利用可能な代替variantもない場合にもError Shaderとなることがあります。

- Unity Manual — How Unity loads and uses shaders
  https://docs.unity3d.com/2022.3/Documentation/Manual/shader-loading.html

したがって、

> ピンク = Shader packageが存在しない

ではありません。

より正確には、

> **元の描画経路で正常に描画できずError Shaderへ落ちた**

という症状です。

---

## 11. 故障オントロジー

毎回事例名から検索するのではなく、故障対象をentityとして分けます。

### Source Entity

**Mesh**
: 頂点、法線、UV、bone weightなど。

**Renderer**
: MeshとMaterialを描画へ渡すcomponent。

**Material**
: Shader選択、property、keyword等の状態。

**Shader Source**
: ShaderLab / HLSL / include等。

**Feature**
: Refraction、MatCap、Panosphere、Parallax、FakeShadow等。

**Animator / Reactive State**
: runtimeでMaterialやobject stateを変更し得る状態。

**MA / NDMF Component**
: build時にavatarを変換するsource instruction。

### Build Entity

**Built Renderer**
: build後に残るRenderer。

**Built Material State**
: build後のMaterial assignmentとproperties。

**Shader Variant**
: keyword / platform / render条件等に応じたcompiled program variation。

### Runtime Entity

**Render Context**
: Desktop / Stereo / Direct / Mirror / camera等。

**Eye**
: Left / Right。

**Observation Surface**
: Unity Scene、VRChat Desktop、VR Direct、Mirror等。

**Symptom**
: 二重、左右差、透明崩れ、黒化、ピンク化等。

### Relation

```text
Material          --uses------> Shader Source
Material          --enables---> Feature / Keyword
Animator / MA     --changes---> Material / Renderer state
NDMF Build        --produces---> Built Avatar
Build Context     --compiles---> Shader Variant
Render Context    --executes---> Shader Variant
Eye               --changes----> Stereo inputs
Observation       --sees-------> Pixels
Symptom           --is diff between--> Observation Contexts
```

このモデルの利点は、

> Shaderがおかしい

を、少なくとも

```text
Shader source bug
Material configuration
Shader variant
build transformation
runtime stereo input
```

へ分解できることです。

---

# ここから今回の事象へ戻る

## 12. 今回わかっている観測

会話から確実に言える範囲では、

- VRの人から「見え方がおかしい」と報告された
- 浴衣も、新しい衣装も、犬も壊れたと認識されている
- 使用ShaderはlilToonと認識されている
- lilToon reimportを実施した
- asset更新も実施した
- 通常の見た目からは状態変化が分からない

という状態です。

まだ未確定なのは、

- 本当に「二重」なのか
- Left Eye / Right Eyeのどちらでどう違うか
- VR Directだけなのか
- Mirrorでも再現するか
- Desktop directでは再現しないか
- 問題箇所のMaterialが共通なのか
- MA / NDMF build後に何が変わっているか
- duplicate Rendererが存在するか
- Shader compile errorが存在するか

です。

したがって、現時点での正確な表現は、

> **VR-only Stereo系の故障が疑われるが、原因層はShaderに限定できない。Material設定、Material animation、MA / NDMF build transformation、Renderer状態を含めて診断する。**

になります。

---

## 13. 「浴衣・新衣装・犬が同時」は共有上流を探すサイン

もし浴衣だけなら、浴衣固有MaterialやMeshから見るのが自然です。

しかし複数の独立対象が同時期に壊れたなら、共通依存を優先します。

候補は、

```text
同じlilToon package
同じUnity project
同じVRCSDK / build pipeline
共通Material
共通Animator
共通MA / NDMF processing
同じStereo render path
```

などです。

これは「共通Shaderが犯人」という意味ではありません。

**複数対象を個別に直すより、まず共通する上流依存を調べる方が情報効率が高い**という意味です。

---

## 14. 診断順序

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

ここで最初に故障境界を取ります。

### Step 2: Renderer / Material / Shaderを静的確認

- Missing Material
- Missing Shader
- `Hidden/InternalErrorShader`
- unsupported Shader
- duplicate Renderer
- 共通Material

を確認します。

### Step 3: Material featureをA/Bする

実際に使用している場合だけ、

```text
Refraction
MatCap
Parallax
Panosphere / panning
screen-space系
FakeShadow
```

等を1つずつOFFにします。

全部同時にOFFにすると原因変数が失われます。

### Step 4: Material Swapを確認

AnimatorやMA Reactive ComponentsによってMaterialがruntime/build時に変わっていないか確認します。

### Step 5: MA / NDMF build後stateを確認

Modular AvatarのManual Bake等でbuild transformation適用後のcopyを作り、

```text
Source Renderer / Material
vs
Built Renderer / Material
```

を比較します。

### Step 6: Shader versionをA/Bする

reimport回数ではなくversion差を変数にします。

lilToon #46のように、同じpackageを何度reimportしてもversion自体のregressionなら直りません。

---

## 15. 今回の診断を一文にする

> **VRでのみ二重・左右差が出る事象はStereo描画経路に依存する不具合を強く疑わせる。ただしStereoは原因ではなく露出条件であり、根本原因はShader実装、Material feature、Shader Variant、Material Swap、MA / NDMF build transformation、duplicate Renderer等のいずれにも存在し得る。したがって、Direct VR / Left Eye / Right Eyeという観測差を起点に、最終Built Avatarへ入力される状態を上流へ遡って診断する。**

これが、過去Issueを今回へ転用したときに得られる最も一般的な原理です。

---

## 16. やらない方がいいこと

### 「VRだけ二重だからShader」と決める

Stereo経路の疑いは上がりますが、Material / build stateを飛ばしています。

### 「ShaderをreimportしたからShaderではない」と決める

version regressionや同一設定の再生成は残ります。

### 「Mirrorで正常だから直った」と判断する

Poiyomi #24とlilToon #46にはMirror正常 / Direct VR異常の事例があります。

### 「UnityでMaterialが正常だからMAは無関係」と判断する

MAはbuild時にMaterial / avatar stateを変え得ます。

### 一度に全部更新する

Shader、SDK、MA、Material、Libraryを同時に変えると、直っても原因が残りません。

---

## 17. 原理・原則

1. **症状の露出条件と原因の所在を分ける。**
2. **VR-onlyはStereoを疑う手掛かりであり、Shader故障の診断名ではない。**
3. **Desktop正常はStereo正常を証明しない。**
4. **Mirror正常はDirect VR正常を証明しない。**
5. **ShaderとMaterialは排他的な原因ではなく、組み合わせで故障面を作る。**
6. **Source AvatarとBuilt Avatarを分けて考える。**
7. **MA / NDMF / Animatorは最終Material・Renderer状態を変え得る。**
8. **複数対象が同時に壊れたら共有上流依存を先に調べる。**
9. **reimport回数ではなく、versionと状態のA/Bを取る。**
10. **原因名を当てるよりNORMAL→ABNORMALへ変わる1変数を見つける。**

過去事例は「このボタンを押せば直る」というレシピとしてではなく、**どの層が壊れ得るかを示す故障知識**として使う方が再利用できます。

---

## 参考一次情報

### Unity

- Stereo rendering
  https://docs.unity3d.com/2022.3/Documentation/Manual/SinglePassStereoRendering.html
- Single-pass instanced rendering and custom shaders
  https://docs.unity3d.com/Manual/SinglePassInstancing.html
- Shader variants
  https://docs.unity3d.com/2022.3/Documentation/Manual/shader-variants.html
- Error and loading shaders
  https://docs.unity3d.com/Manual/shader-error.html
- How Unity loads and uses shaders
  https://docs.unity3d.com/2022.3/Documentation/Manual/shader-loading.html

### VRChat

- VRChat 2022.1.2 — Single Pass Stereo Instanced compilation
  https://docs.vrchat.com/docs/vrchat-202212

### lilToon

- lilToon CHANGELOG
  https://github.com/lilxyzw/lilToon/blob/master/Assets/lilToon/CHANGELOG.md
- lilToon CHANGELOG_JP
  https://github.com/lilxyzw/lilToon/blob/master/Assets/lilToon/CHANGELOG_JP.md
- Issue #46 — Refraction material broken in VR with 1.3.5
  https://github.com/lilxyzw/lilToon/issues/46

### Poiyomi Toon Shader

- Issue #4 — Seeing Double's
  https://github.com/poiyomi/PoiyomiToonShader/issues/4
- Issue #24 — Panosphere Left/Right Eye Phase Issue
  https://github.com/poiyomi/PoiyomiToonShader/issues/24

### Modular Avatar / NDMF

- Modular Avatar — Introduction
  https://modular-avatar.nadena.dev/docs/intro
- Manual processing
  https://modular-avatar.nadena.dev/docs/manual-processing
- Material Setter
  https://modular-avatar.nadena.dev/docs/reference/reaction/material-setter
- Material Swap
  https://modular-avatar.nadena.dev/docs/reference/reaction/material-swap
- Reactive Components
  https://modular-avatar.nadena.dev/docs/reference/reaction
- NDMF BuildPhase
  https://ndmf.nadena.dev/api/nadena.dev.ndmf.BuildPhase.html
