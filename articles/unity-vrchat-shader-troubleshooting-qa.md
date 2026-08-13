---
title: "VRだけ二重に見えた。Shaderを疑って遠回りした末に、Uploaderの中断へ辿り着いた"
emoji: "🥽"
type: "tech"
topics: ["vrchat", "unity", "shader", "liltoon", "vrcsdk"]
published: false
published_at: 2026-08-12 19:46
---

# VRだけ二重に見えた。Shaderを疑って遠回りした末に、Uploaderの中断へ辿り着いた

Desktopでは正常なのに、VRでは左右眼で二重に見える。

この症状を見て、最初はShaderを疑いました。Stereo Renderingでは左右眼の描画経路が分かれ、custom Shader側の対応不足でVRだけ壊れることは実際にあります。UnityもSingle Pass Stereo / Single Pass Instanced向けの実装要件を公式に説明しています。

- Unity Stereo Rendering: https://docs.unity3d.com/2022.3/Documentation/Manual/SinglePassStereoRendering.html
- Unity Single-pass instanced custom shaders: https://docs.unity3d.com/Manual/SinglePassInstancing.html

しかし今回、実機で切り分けて確認できた観測事実は別でした。

```text
CAUのupload処理が途中で止まった状態だった
↓
その状態を解消し、正常にuploadを完了させた
↓
VRの二重表示が解消した
```

ここから言えるのは、**今回の異常条件にuploadの中断状態が含まれていた**ということまでです。Continuous Avatar Uploader（CAU）内部のどの処理が左右眼表示へ影響したのかは証明していません。

この記事では、この証拠境界を崩さずに、同じ症状を最短で切り分ける順序を整理します。

## 症状から原因へ飛ばない

壊れた診断はこうでした。

```text
VRだけ異常
→ Stereo
→ Shader
→ lilToon
→ Reimport
```

この推論には「VRだけ壊れるShader問題は存在する」という根拠はあります。しかし、**症状がShaderらしいことと、今回の原因がShaderであることは別**です。

今回抜けていた変数は、Source Avatarと描画の間にあるbuild / upload状態でした。

```text
Source Avatar
→ Build processing
→ Bundle
→ Upload
→ VRChat backend
→ Client / Stereo Rendering
→ 見た目
```

## CAUには「中断・再開」という状態が実在する

CAU公式CHANGELOGでは、v0.3.8でUnity Editor crash後のupload resumeが追加されています。またupload progressを次のassetへ保存し、Editor crashやtarget platform変更後のresumeに利用すると明記されています。

`Assets/com.anatawa12.continuous-avatar-uploader.uploader-progress.asset`

さらに公式CHANGELOGには、その後もupload state周辺の修正があります。

- v0.3.10: buildをcancelできない問題を修正
- v0.3.10: platform変更後にUploaderがfreezeすることがある問題を修正
- v0.3.11: userがresumeを拒否した後もresumeする問題を修正

一次情報:
https://github.com/anatawa12/ContinuousAvatarUploader/blob/master/CHANGELOG.md

これらは「CAUのresume stateが左右眼二重表示を起こす」と証明する資料ではありません。確認できるのは、**CAUがupload progressを永続化し、中断・再開を状態として持つ**ことです。

## 今回の観測と未証明部分を分ける

### 観測できたこと

- CAU uploadが途中停止した状態だった
- その状態を解消し、uploadを正常終了させた
- その後、実HMDで二重表示が解消した

### 一次情報で確認できること

- CAUはupload progressを保存する
- Editor crash後のresume機能を持つ
- cancel / resume / platform change周辺に修正履歴がある
- VRChat公式SDKにはControl Panelからの `Build & Publish` 手順がある

VRChat公式:
https://creators.vrchat.com/avatars/creating-your-first-avatar/

### まだ言えないこと

- 中断されたprogress assetが直接左右眼レンダリングを壊した
- CAU一般に左右眼バグがある
- Shaderは常に無関係である

この3つは断定しません。

## 診断順を変える

今後はShaderを触る前に、cleanなupload baselineを取ります。

```text
1. 直前のuploadが正常終了したか確認
2. crash / cancel / platform切替 / resumeの有無を記録
3. VRChat SDK Control Panelからcleanに Build & Publish
4. HMDでDirect / Left / Right / Mirrorを確認
5. 同じSourceのままCAUで正常完了までupload
6. 同条件で再確認
7. clean uploadでも再現する場合だけBuilt / Material / Shaderへ降りる
```

重要なのは、**途中停止したrunを正常なCAU runとして比較しない**ことです。

## 最小A/Bテスト

同一Avatar・同一Project stateで次だけ比較します。

| 観測 | clean VRCSDK | CAU |
|---|---|---|
| build完了 | PASS/FAIL | PASS/FAIL |
| upload完了 | PASS/FAIL | PASS/FAIL |
| 中断 | YES/NO | YES/NO |
| resume | YES/NO | YES/NO |
| Left Eye | NORMAL/ABNORMAL | NORMAL/ABNORMAL |
| Right Eye | NORMAL/ABNORMAL | NORMAL/ABNORMAL |
| Mirror | NORMAL/ABNORMAL | NORMAL/ABNORMAL |

固定するものはPrefab、Material、Shader、Animator、Unity version、VRCSDK version、target platformです。複数の変数を同時に触りません。

## clean uploadでも壊れるならShaderへ戻る

Shader仮説を捨てるわけではありません。clean uploadでも再現するなら、次にSourceとBuilt stateを分けます。

```text
clean uploadでも異常
→ Source vs Builtを比較
→ Renderer / Material identity
→ Material feature A/B
→ Shader stereo compatibility
→ 必要なら対象ShaderだけReimport
```

Unityにはmanual Reimportの仕組みがあります。
https://docs.unity3d.com/Manual/ImporterConsistency.html

lilToonの通常Shader assetも公式repositoryで確認できます。
https://github.com/lilxyzw/lilToon/blob/master/Assets/lilToon/Shader/lts.shader

ただし、**「VRだけ二重」という症状だけを根拠にReimportを初手にはしません。**

## 失敗から得た一般則

今回の失敗は、もっともらしい既知事例を見つけたことで、観測点を下流へ飛ばしすぎたことでした。

```text
症状
→ 既知事例に似ている
→ 原因も同じだろう
```

ではなく、

```text
症状
→ pipelineを段階に分ける
→ 直前の正常固定点を作る
→ 1変数だけ変える
→ 結果が分岐した境界から調べる
```

とした方が速い。

今回なら、最初の正常固定点は**標準VRCSDKで最後まで完了したclean upload**です。

## 読者が試せる再現手順

1. 異常が出ているAvatarのSourceをgit等で固定する。
2. ShaderやMaterialを変更しない。
3. 直前のuploadに中断・crash・cancel・resumeがなかったか記録する。
4. VRChat SDK Control Panelから `Build & Publish` を最後まで完了させる。
5. 実HMDで左右眼とMirrorを確認する。
6. Sourceを変更せずCAUでuploadし、最後まで正常終了したことを確認する。
7. 同じHMD条件で再測定する。
8. CAU runが途中停止した場合、そのrunは比較対象から外す。
9. clean uploadでも再現した場合だけShader / Material / Built Avatarへ進む。

## まとめ

今回確認できたのは「CAUが左右眼を壊した」という一般論ではありません。

**中断状態を抱えたuploadの後に異常が観測され、正常完了したuploadへ戻した後に症状が消えた。** ここまでが実機観測です。

だから診断順も変えます。

VRだけ異常だからといって、最初にShaderを触らない。まずuploadが正常終了した状態を作り、clean baselineを取る。それでも壊れるなら、そこで初めてSource / Built / Material / Shaderへ降りる。

### 一次情報

- Continuous Avatar Uploader CHANGELOG: https://github.com/anatawa12/ContinuousAvatarUploader/blob/master/CHANGELOG.md
- Continuous Avatar Uploader: https://github.com/anatawa12/ContinuousAvatarUploader
- VRChat — Creating Your First Avatar: https://creators.vrchat.com/avatars/creating-your-first-avatar/
- Unity — Stereo Rendering: https://docs.unity3d.com/2022.3/Documentation/Manual/SinglePassStereoRendering.html
- Unity — Single-pass instanced custom shaders: https://docs.unity3d.com/Manual/SinglePassInstancing.html
- Unity — Importer Consistency: https://docs.unity3d.com/Manual/ImporterConsistency.html
- lilToon `lts.shader`: https://github.com/lilxyzw/lilToon/blob/master/Assets/lilToon/Shader/lts.shader
