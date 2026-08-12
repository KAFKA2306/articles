# Unity / VRChatで「VRだけ見え方がおかしい」をどう考えるか

Unity上では普通に見える。自分のDesktop表示でも異常が分からない。しかしVRの人から「見え方がおかしい」と言われる。さらに、浴衣だけではなく、新しい衣装も、犬も同じタイミングでおかしくなった。lilToonをreimportし、アセットも更新したが、見た目からは状態が変わったのか分からない。

この状況で一番危険なのは、いきなり

> Shaderが壊れた

あるいは逆に

> Unityでは正常だからShaderではない

と決めることです。

過去のlilToon / Poiyomi / Unity / VRChatの一次情報を並べると、もっと一般的な原理が見えてきます。

**「見た目」はMaterialだけで決まらない。どのShader programが、どの描画コンテキストで、どちらの目に対して実行されたかまで含めて初めて決まる。**

この記事では、過去Issueからその仕組みを抽出し、最後に今回の事象へ視点を戻します。

---

## 1. 最初に分けるべきもの：観測事実と原因仮説

今回わかっているのは、少なくとも次の観測です。

- VRユーザーから見たときに見え方がおかしいという報告がある
- 浴衣、新しい衣装、犬など、複数の対象で同時に異常が出た
- lilToonのreimportとアセット更新を試した
- しかし、通常の見た目では状態変化を確認できなかった

一方、まだ分かっていないことがあります。

- 左目だけなのか、右目だけなのか、両目なのか
- 「二重」「位置ずれ」「色」「透明」「影」「輪郭」のどの種類の異常なのか
- VRChat Desktopの直接視認では再現するのか
- VRの直接視認では再現するのか
- VRChat内のミラーでは再現するのか
- Unity ConsoleにShader compile errorがあるのか
- どのMaterial / Shader機能で再現するのか
- 現在のlilToon、VRCSDK、Unityの正確なバージョンは何か

したがって、現時点では**Shaderが原因だと確定していません**。

ただし、「VRだけ」「複数対象で同時」という観測から、個別Meshだけを見るよりも、複数対象が共有している描画経路を先に調べる合理的な理由があります。

---

## 2. 原理：同じMaterialでも、常に同じ処理が走るわけではない

画面に最終的な色が出るまでを単純化すると、次のように考えられます。

```text
Mesh
  + Material properties
  + Shader source
  + Shader keywords
  + Build target / Graphics API / SDK
        ↓
   compiled Shader Variant
        ↓
Camera / render path / eye / screen-space inputs
        ↓
      pixels
        ↓
Editor / Desktop / Mirror / VR Left Eye / VR Right Eye
```

つまり、見た目 `P` は概念的には次のような関数です。

```text
P = f(
  Mesh,
  Material,
  ShaderSource,
  ShaderVariant,
  BuildContext,
  RenderContext,
  Eye
)
```

このどれかが変われば、同じアバター、同じMaterial名、同じShader名でも結果は変わり得ます。

Unity公式はShader Variantを、同じShader programの「異なる条件に対応する別バージョン」と説明しています。実行時には現在の条件に合うvariantが選ばれます。

一次情報:

- Unity Manual — Shader variants
  https://docs.unity3d.com/ja/2022.2/Manual/shader-variants.html

ここから最初の原則が得られます。

> **「Shaderが入っているか」と「今回の描画条件で必要なShader Variantが正しく動くか」は別問題である。**

---

## 3. Stereo Renderingでは「目」が描画条件になる

VRでは1つの平面画像を1回だけ描けば終わりではありません。

Unity XRはStereo Renderingとして、少なくともMulti-passとSingle Pass Instancedを説明しています。

- Multi-pass: 左右それぞれに対してレンダリングする
- Single Pass Instanced: instanced draw callを使って1回のpass内で左右眼を扱う

一次情報:

- Unity Manual — Stereo rendering
  https://docs.unity3d.com/ja/2022.1/Manual/SinglePassStereoRendering.html

Single Pass Instanced対応のカスタムShaderでは、Unity公式ドキュメントに `UNITY_VERTEX_OUTPUT_STEREO`、`UNITY_SETUP_INSTANCE_ID()`、`UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO()` などの処理が示されています。

特に `UNITY_SETUP_INSTANCE_ID()` は、GPUが現在どちらの目を描いているかに応じて `unity_StereoEyeIndex` を設定します。

また、screen-space textureのサンプリングも通常の2D back bufferとSingle Pass Instancedでは扱いが異なるため、Unityは専用マクロを使うよう説明しています。

一次情報:

- Unity Manual — Single-pass instanced rendering and custom shaders
  https://docs.unity3d.com/ja/current/Manual/SinglePassInstancing.html

ここから第二の原則が得られます。

> **Desktopで通る描画経路と、VRの左右眼で通る描画経路は同一とは限らない。**

したがって、Desktopで正常だったことは重要な観測ですが、それだけでStereo経路の正常性は証明できません。

---

## 4. 過去事例1：Desktop正常、VRだけ二重になる

Poiyomi Toon Shader Issue #4 `Seeing Double's` では、報告者が次の症状を記録しています。

- VRユーザーからは二重に見える
- 自分自身もVRでは二重に見える
- Desktopユーザーには正常に見える

一次情報:

- Poiyomi Toon Shader Issue #4
  https://github.com/poiyomi/PoiyomiToonShader/issues/4

このIssue本文だけでは、内部原因が `unity_StereoEyeIndex` だったとまでは証明できません。

重要なのは、**同じアップロード済みアバターでもVRとDesktopで結果が分岐した実例がある**ことです。

### この事例から言えること

- Desktop正常はVR正常の十分条件ではない
- 観測者の描画モードは診断情報である

### この事例だけからは言えないこと

- 今回もPoiyomiと同じ原因である
- Stereo Eye Indexの処理が直接の原因である
- MeshやMaterialが絶対に無関係である

過去Issueは「原因をコピペするもの」ではなく、**故障可能な層を知るための証拠**として使います。

---

## 5. 過去事例2：左右眼でエフェクトのphaseがずれる

Poiyomi Issue #24 `Panosphere Left/Right Eye Phase Issue` は、さらにStereo差が明確です。

報告では、Panningのphaseが左目と右目でずれ、Stereo modeでは異常になる一方で、Desktop modeでは正常でした。さらにVRChat内のミラーでも正常だったと記録されています。

一次情報:

- Poiyomi Toon Shader Issue #24
  https://github.com/poiyomi/PoiyomiToonShader/issues/24

この事例が重要なのは、次の比較が成立しているからです。

```text
同じアバター
同じMaterial
同じVRChat

直接のStereo表示     → 異常
Desktop non-stereo   → 正常
Mirror               → 正常
```

つまり、**ミラーで正常だったことも、直接Stereo表示の正常性を保証しません。**

「ミラーを見て正常だったからOK」は、少なくともこのクラスの問題に対しては十分なテストではありません。

---

## 6. 過去事例3：lilToonでも「VRだけ壊れる」regressionが実在した

今回に特に近いのがlilToon Issue #46 `Refraction material broken in VR with 1.3.5` です。

報告内容は次の通りです。

- lilToon 1.3.5への更新後に発生
- Refraction materialがVRで壊れた
- VRChatのミラーでは正常
- Desktop modeでは正常
- VRで直接見ると異常
- lilToon 1.3.4では正常だった

一次情報:

- lilToon Issue #46
  https://github.com/lilxyzw/lilToon/issues/46

その後、報告者は修正版をVRでテストして正常になったとコメントし、lilToon作者は修正を1.3.6へ入れると回答しています。

- Issue #46 comments
  https://github.com/lilxyzw/lilToon/issues/46#issuecomment-1239775190
  https://github.com/lilxyzw/lilToon/issues/46#issuecomment-1242675841

ここから第三の原則が得られます。

> **再importは「そのversionをもう一度importする」操作であって、そのversion自身のVR限定regressionを直す操作ではない。**

したがって、再importして直らなかったことだけでShader仮説を棄却することはできません。

逆に、最新版へ上げれば必ず直るとも言えません。Issue #46そのものが「version更新をきっかけにVR限定regressionが入った」事例だからです。

必要なのは「最新化」ではなく**versionを記録したA/B比較**です。

---

## 7. lilToonのCHANGELOGにもStereo固有の修正が残っている

lilToonの公式CHANGELOGには、Issue単体よりさらに一般化できる記録があります。

### 1.2.7

`Fixed refraction shader behavior in Single Pass Instanced`

つまり、Single Pass Instanced環境に固有のRefraction Shader修正が実際に入っています。

同じ1.2.7では、Rim LightにVR時のparallax強度を調整する機能も追加されています。

### 1.9.0

`FakeShadow's parallax in VR` の修正が記録されています。

一次情報:

- lilToon CHANGELOG
  https://github.com/lilxyzw/lilToon/blob/master/Assets/lilToon/CHANGELOG.md
- 日本語CHANGELOG
  https://github.com/lilxyzw/lilToon/blob/master/Assets/lilToon/CHANGELOG_JP.md

これは重要です。

Refraction、MatCap、FakeShadow、parallax、screen-space由来の計算など、**cameraやviewに依存する機能ほど、Stereoという追加の座標系・視点条件を持つ**ことになります。

「Shader」という巨大な箱を1個疑うのではなく、

```text
Shader
  ├─ 通常のsurface計算
  ├─ screen-space計算
  ├─ refraction
  ├─ MatCap / view-dependent UV
  ├─ parallax
  ├─ outline
  └─ Stereo対応
```

のように機能単位で見る必要があります。

---

## 8. VRChat側にもStereo用Shader Variantという境界がある

VRChat 2022.1.2の公式Release Notesでは、VRCSDKについて重要な変更が記録されています。

以前はMonoとSingle-Pass Stereo用のShader Variantをcompileしていましたが、将来のUnity更新に向けてSingle-Pass Stereo Instanced（SPS-I）のvariantも必要になるとして、**build時に全ShaderのSPS-I compilationを有効化**しています。

一次情報:

- VRChat 2022.1.2 Release Notes
  https://docs.vrchat.com/docs/vrchat-202212

ここで分かるのは、VRChatへのUploadは単なる「Unity Sceneをそのままサーバーへコピー」ではないということです。

少なくともShaderについては、**SDK / build時にどのvariantを用意するか**という境界があります。

したがって、

```text
Unity Scene Viewで正常
```

と

```text
VRChat buildで必要なStereo variantが正常
```

は別の検証項目です。

---

## 9. 「突然ピンク」は症状であって原因名ではない

「ピンクになったらShaderがない」と覚えると、診断を誤ります。

Unity公式によれば、通常のShaderで描画できない場合にDefault Error Shaderが使われ、その色はmagentaです。

例として公式ドキュメントは、

- Materialが割り当てられていない
- Shaderがcompileできない
- Shaderがsupportされていない

などを挙げています。

一次情報:

- Unity Manual — Error and loading shaders
  https://docs.unity3d.com/ja/current/Manual/shader-error.html

さらにUnityは、必要なShader Variantがbuildからstripされ、類似variantも見つからない場合にもmagenta error shaderを使うと説明しています。

- Unity Manual — How Unity loads and uses shaders
  https://docs.unity3d.com/2022.3/Documentation/Manual/shader-loading.html

したがって、第四の原則はこうなります。

> **ピンクは「元のShader経路で描画できなかった」というエラー信号であり、それ自体はMissing Shader、compile failure、unsupported、missing variantなどを区別しない。**

「ピンク」という観測から、原因を1つに即断してはいけません。

---

## 10. 故障オントロジー：何が、何に依存しているのか

今回のような問題を毎回ゼロから考えないために、対象を次のentityへ分けます。

### Entity

**Mesh**
: 頂点、法線、UV、bone weightなどのgeometry。

**Material**
: Shaderの選択とproperty値を保持する。

**Shader Source**
: HLSL/ShaderLab/include等のsource。

**Feature**
: Refraction、MatCap、Parallax、Outline、Fur、Dissolveなどの機能。

**Keyword Set**
: 有効化されたShader keywordの組み合わせ。

**Shader Variant**
: keywordやbuild条件に応じてcompileされた実行用Shader programのvariation。

**Build Context**
: Unity、VRCSDK、build target、Graphics APIなど、variantを生成する条件。

**Render Context**
: camera、Stereo mode、eye、screen-space inputなど、実行時の条件。

**Observation Surface**
: Unity Scene、Game View、VRChat Desktop、Mirror、VR Left Eye、VR Right Eyeなど、ユーザーが結果を見る場所。

**Symptom**
: 二重、左右差、透明崩れ、黒化、ピンク化などの観測結果。

### Relation

```text
Material        --uses------> Shader Source
Material        --enables---> Feature / Keyword Set
Build Context   --compiles---> Shader Variant
Render Context  --executes---> Shader Variant
Eye             --changes----> Render Context
Observation     --sees-------> rendered pixels
Symptom         --is diff between--> Observation Contexts
```

このモデルにすると、「Shaderが壊れた」という曖昧な言い方を分解できます。

例えば、

```text
Shader Source自体は存在する
        ↓
Desktop用経路は正常
        ↓
Stereo用variant / view-dependent計算だけ異常
        ↓
UnityやDesktopでは発見できない
        ↓
VRの直接視認で初めて症状化
```

という故障が構造的に可能になります。

---

## 11. 診断原則：症状は「物」ではなく「比較」に宿る

この問題で最も役立つ考え方は、

> 「どのMaterialが壊れたか」

より先に、

> **「どの条件を変えたときに、正常→異常へ変化するか」**

を見ることです。

例えば、

```text
Desktop → VR
```

でだけ壊れるなら、DesktopとVRの間で変わる要素を調べます。

```text
Left Eye → Right Eye
```

でだけ変わるなら、左右眼で変わるStereo入力を調べます。

```text
Mirror → Direct View
```

でだけ変わるなら、ミラー確認を「正常の証拠」とせず、異なるObservation Surfaceとして扱います。

```text
Version A → Version B
```

でだけ変わるなら、assetそのものよりversion regressionを疑う根拠が増えます。

これは原因名を先に当てる方法ではありません。

**差分を作る変数を1つずつ見つける方法**です。

---

# ここから今回の事象へ戻る

## 12. 「浴衣も新衣装も犬も壊れた」は何を意味するか

ここが今回の重要な観測です。

もし浴衣だけが壊れたなら、浴衣固有のMesh、Material、設定を最初に見るのが自然です。

しかし、今回の会話では、

- 浴衣
- 新しい衣装
- 犬

まで同時に見え方がおかしいとされています。

これは**共通原因を優先して調べるべきサイン**です。

3つの対象が共有し得るものとして、例えば次があります。

```text
同じlilToon package
同じUnity project
同じVRCSDK / build pipeline
同じStereo render path
同じGraphics環境
共通のShader設定や最適化処理
```

これは「lilToonが犯人」と確定するという意味ではありません。

意味するのは、**3つの独立Meshが同時に偶然壊れた、という仮説より先に、3つが共有する上流依存を検査する価値が高い**ということです。

---

## 13. 「自分では普通に見える」も重要な証拠である

今回、本人の通常の見た目では状態変化を確認できていません。

これは「問題が存在しない」という情報ではありません。

過去事例には実際に、

- Desktop正常 / VR異常 — Poiyomi #4
- Desktop・Mirror正常 / Stereo左右眼異常 — Poiyomi #24
- Desktop・Mirror正常 / VR direct異常 — lilToon #46

があります。

したがって今回必要なのは「もっとUnity画面を見る」だけではありません。

**異常が報告されたObservation Surfaceを再現すること**です。

---

## 14. 「reimportしたけど変わらない」から何が言えるか

言えることは限定的です。

reimport後も同じ症状なら、少なくとも「単純な一時import失敗をreimportだけで解消する」という仮説の優先度は下がります。

しかし、次は残ります。

- 同じversionに存在するVR限定regression
- 同じ設定から再生成される不正なvariant
- Build時だけ露出するStereo経路
- Material feature固有のview-dependent問題
- Shader以外の共通原因

lilToon #46では、1.3.5そのものにVR限定の問題があり、修正版をテストして解消し、1.3.6へ修正が入る流れでした。

したがって、今回も「何度入れ直したか」より、

```text
何を固定し
何を変え
どの観測面で結果が変わったか
```

を残す方が診断力が高くなります。

---

## 15. 今回の仮説を、原因ではなく「調べる層」の優先順位にする

現時点で原因確率を数値化する根拠はありません。

代わりに、調査順を次のように置けます。

### 優先A：共通のStereo / Shader Variant / build経路

理由:

- VRユーザーから異常報告がある
- 複数対象が同時に壊れた
- 過去にDesktop / Mirror正常でもVRだけ壊れる事例がある
- VRChat自身がSPS-I variantをbuild時に扱っている

### 優先B：lilToonのversion / view-dependent feature

理由:

- 今回使われているShaderがlilToonとされている
- lilToonにはSingle Pass InstancedのRefraction修正、VR parallax修正などの履歴がある
- 過去にversion更新でVR限定regressionが発生した実例がある

### 優先C：Material設定・共通最適化・package競合

個々のMaterial設定だけでは複数対象同時発生を説明しにくい場合がありますが、共通設定やbuild処理なら説明可能です。

### 優先D：個別Mesh / 個別衣装

除外はしません。

ただし、浴衣、新衣装、犬が同時に壊れたという観測が正しければ、最初から3対象を個別に修理するより上流を先に見る方が効率的です。

---

## 16. 次に行うべき最小A/Bテスト

大量の再インストールを続ける前に、原因を最もよく分離するテストを行います。

### Test 0: 現在状態を固定する

最初に記録します。

```text
Unity version
VRCSDK version
lilToon version
現在のgit commit
問題が出ているavatar / material
```

原因調査中にversionを次々変えると、どの変更で直ったのか分からなくなります。

### Test 1: Observation Matrixを作る

同じアバターを次で比較します。

| 観測面 | 正常 / 異常 | 記録 |
|---|---|---|
| Unity Scene View |  | screenshot |
| Unity Game View |  | screenshot |
| VRChat Desktop direct |  | screenshot |
| VR direct |  | video / screenshot |
| VR Left Eye |  |  |
| VR Right Eye |  |  |
| VRChat Mirror |  | screenshot |
| 別VRユーザー direct |  | screenshot |

これだけで、故障層が大きく狭まります。

### Test 2: 1個のMaterialだけ別Shaderへ差し替える

必ず複製したMaterial / test avatarで行います。

問題Materialを、ローカル比較用にStandardなど別系統の単純なShaderへ一時差し替えます。

- 症状が消える → 元Shaderまたはその描画経路側の疑いが増える
- 症状が残る → Mesh、animation、camera側などShader以外も強く残る

「全部直す」のではなく、**1 Materialだけをprobeとして使う**のが目的です。

### Test 3: view-dependent機能だけを1個ずつ切る

Materialで使用している場合に限り、例えば次を1個ずつOFFにします。

```text
Refraction
MatCap
Parallax
screen-space系機能
特殊UV / panning
FakeShadow
```

全部同時に切ると、どの機能が境界だったか分かりません。

### Test 4: versionをA/Bする

無作為に最新版へ更新し続けるのではなく、隔離したcopy / branchで

```text
現在version
vs
比較対象version
```

を同じObservation Matrixで比較します。

lilToon #46が示すように、version差そのものが診断変数になります。

### Test 5: Console / Editor.logを証拠として保存する

次の語を探します。

```text
Shader error
failed to compile
failed to open source file
variant
keyword
unsupported
```

ピンク化している場合は特に、見た目だけでMissing Shaderと決めず、compile / support / variantのどれかをログで分離します。

---

## 17. やらない方がいい切り分け

### 「とりあえず全部reimport」だけを繰り返す

状態を大きく変えるのに、診断情報がほとんど増えません。

### 「ミラーで正常だから直った」と判断する

Poiyomi #24とlilToon #46では、ミラー正常・直接Stereo異常という実例があります。

### 「ピンクだからShaderファイルが消えた」と決める

Unity公式上、compile failureやunsupported、missing variantでもmagentaになり得ます。

### 「Shaderを更新したからShader原因ではない」と判断する

version regressionは実在します。

### 複数の変更を同時に行う

Shader更新、Material再作成、SDK更新、Library削除を一度に行うと、直っても原因が分かりません。

---

## 18. 今回の問題を一文で表すなら

現時点での最も正確な表現は、

> **複数のlilToon使用対象で、通常観測では異常を確認できない一方、VR観測者から見た目の異常が報告されている。過去にはDesktop / Mirrorと直接Stereo表示で結果が分岐するShader不具合が実在するため、個別Mesh修正より先にStereo・Shader Variant・buildを含む共通描画経路をA/Bテストする。原因がShaderであること自体はまだ未確定である。**

です。

これなら、証拠より先に原因を決めていません。

同時に、「何が起こっているのか分からない」状態から、次に何を観測すればよいかが決まります。

---

## 19. この記事から得られる原則

1. **見た目の異常はMaterial単体の属性ではなく、描画コンテキストとの関係で発生する。**
2. **Desktop正常はStereo正常を証明しない。**
3. **Mirror正常もDirect VR正常を証明しない。**
4. **Shader packageの存在と、必要なShader Variantの正常性は別である。**
5. **reimportはversion regressionを修正しない。**
6. **ピンクは診断名ではなくError Shaderという症状である。**
7. **複数の独立対象が同時に壊れたら、共有する上流依存を先に調べる。**
8. **原因名を当てるより、正常→異常へ変わる1変数を見つける。**

この8つを使えば、次に別のアバター、別の衣装、別のShaderで似た事故が起きても、Issue検索からやり直す必要はありません。

過去事例は個別の修理手順ではなく、**故障メカニズムの知識**として再利用できます。

---

## 参考一次情報

### Unity

- Stereo rendering
  https://docs.unity3d.com/ja/2022.1/Manual/SinglePassStereoRendering.html
- Single-pass instanced rendering and custom shaders
  https://docs.unity3d.com/ja/current/Manual/SinglePassInstancing.html
- Shader variants
  https://docs.unity3d.com/ja/2022.2/Manual/shader-variants.html
- Error and loading shaders
  https://docs.unity3d.com/ja/current/Manual/shader-error.html
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
