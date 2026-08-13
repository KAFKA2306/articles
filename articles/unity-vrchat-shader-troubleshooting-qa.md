---
title: "Desktopは正常、VRだけ二重。真因はShaderではなくCAUの中断状態だった"
emoji: "🥽"
type: "tech"
topics: ["vrchat", "unity", "shader", "liltoon", "vrcsdk"]
published: true
published_at: 2026-08-12 19:46
---

# Desktopは正常、VRだけ二重。真因はShaderではなくCAUの中断状態だった

「Desktopでは正常なのに、VRでは左右眼で二重に見える」。

この症状から最初に疑ったのはStereo Shaderでした。PoiyomiやlilToonには、DesktopやMirrorでは正常でもDirect VRだけ壊れる過去事例が実際にあります。

- Poiyomi Issue #4: https://github.com/poiyomi/PoiyomiToonShader/issues/4
- Poiyomi Issue #24: https://github.com/poiyomi/PoiyomiToonShader/issues/24
- lilToon Issue #46: https://github.com/lilxyzw/lilToon/issues/46

しかし今回の実機切り分けでは、Shaderそのものが真因ではありませんでした。

**今回確認できた事実は、Continuous Avatar Uploader（CAU）のアップロード処理が途中で止まった状態だったこと、その状態を解消して正常なアップロードに戻した後は症状が解消したことです。**

ここで重要なのは、これを「CAUには左右眼バグがある」と一般化しないことです。公開一次情報から確認できるのは、CAUがアップロード進捗を永続化し、中断後にresumeする仕組みを持つこと、また過去にcancel・resume・platform変更後のfreeze周辺で修正履歴があることまでです。

- CAU repository: https://github.com/anatawa12/ContinuousAvatarUploader
- CAU CHANGELOG: https://github.com/anatawa12/ContinuousAvatarUploader/blob/master/CHANGELOG.md
- VRChat公式 Avatar upload手順: https://creators.vrchat.com/avatars/creating-your-first-avatar/

したがって、今回の事故は **「CAUそのもの」ではなく「中断されたCAU upload state」** の問題として扱うのが最も正確です。

---

## 結論

診断順序は次のように更新します。

```text
旧
VR-only / eye-dependent
→ Shader / Material
→ Reimport
→ MA / NDMF
→ Built Avatar

前版
VR-only / eye-dependent
→ 標準VRCSDK vs CAU
→ Uploader経路差を見る

今回の最終版
VR-only / eye-dependent
→ upload処理が正常終了したか確認
→ CAU等の中断・resume状態を確認
→ 標準VRCSDKでclean uploadしてbaselineを取る
→ それでも再現するなら Source / Built / Shaderへ降りる
```

最重要点は、**Uploader名だけを見るのではなく、upload state machineが正常終了しているかを見る**ことです。

---

## 1. なぜShader説はもっともらしかったのか

過去事例が実在したからです。

| 事例 | Desktop | Mirror | Direct VR | 症状 |
|---|---|---|---|---|
| Poiyomi #4 | NORMAL | - | ABNORMAL | Avatarが二重に見える |
| Poiyomi #24 | NORMAL | NORMAL | ABNORMAL | 左右眼でPanosphere phaseがずれる |
| lilToon #46 | NORMAL | NORMAL | ABNORMAL | Refraction materialがVRで壊れる |

UnityもStereo RenderingとSingle Pass Instanced custom Shaderの要件を公式に説明しています。

- https://docs.unity3d.com/2022.3/Documentation/Manual/SinglePassStereoRendering.html
- https://docs.unity3d.com/Manual/SinglePassInstancing.html

したがって、

```text
Desktop正常
VRだけ異常
```

からStereo経路を疑うこと自体は合理的でした。

ただし、症状の形がShaderらしいことと、Shaderが真因であることは別です。

---

## 2. 抜けていたのは「Uploader」よりさらに細かい「中断状態」だった

前版では次のように整理していました。

```text
Source Avatar
→ Build Processing
→ Built Bundle
→ Build / Upload API path
→ VRChat backend
→ Client / Stereo Rendering
```

このモデルでもまだ粗すぎました。

実際にはupload層を少なくとも次のように分ける必要があります。

```text
Build開始
  ↓
Build完了
  ↓
Upload開始
  ↓
Upload進捗保存
  ↓
Upload完了
  ↓
進捗状態の終了
```

CAUのCHANGELOGには、0.3.8でUnity Editor crash後にuploadをresumeする機能が追加され、そのために進捗ファイル

`Assets/com.anatawa12.continuous-avatar-uploader.uploader-progress.asset`

を保存すると記載されています。

また同CHANGELOGにはupload状態管理周辺の修正として、少なくとも以下が記録されています。

- buildをcancelできない問題
- platform変更後にUploaderがfreezeすることがある問題
- ユーザーがresumeを拒否した後もresumeしてしまう問題

一次情報:

- https://github.com/anatawa12/ContinuousAvatarUploader/blob/master/CHANGELOG.md

これらは今回の左右眼症状そのものを証明するものではありません。

しかし、**CAUが中断・再開・進捗永続化を持つ状態機械であり、その状態が独立した診断変数である**ことは確認できます。

---

## 3. 今回どこまで断定できるか

今回の実機観測から言えること:

```text
CAUのupload処理が途中停止した状態だった
↓
その状態を解消して正常なuploadに戻した
↓
VRの二重表示が解消した
```

公開一次情報から追加で確認できること:

```text
CAUはupload progressを保存する
CAUはEditor crash後のresume機能を持つ
cancel / resume / freeze周辺の修正履歴がある
```

一方、現時点で断定できないこと:

```text
中断されたprogress stateが
左右眼の二重描画を直接生成する内部メカニズム
```

したがって、この記事では「CAUの中断状態が今回の事故条件だった」と記述し、内部メカニズムまでは推測しません。

---

## 4. 「CAU経路が悪い」という前版の表現は強すぎた

前版では、

```text
VRCSDK = NORMAL
CAU    = ABNORMAL
```

というA/Bから、Build / Upload API pathを主な故障境界としていました。

しかし追加観測を入れると、より正確な比較はこうです。

```text
A. 中断状態を抱えたCAU upload
   → ABNORMAL

B. 正常終了したupload
   → NORMAL
```

つまり比較軸は単純な

```text
VRCSDK vs CAU
```

ではありません。

より正確には、

```text
clean / completed upload state
vs
interrupted / resumable upload state
```

です。

---

## 5. 最初に確認すべきこと

同じ症状が出たら、Shaderを触る前に次を確認します。

```text
1. 直前のuploadは最後まで正常終了したか
2. CAUが途中で止まっていなかったか
3. Unity crash / platform切替 / cancelが入っていないか
4. CAUがresume状態を持っていないか
5. cleanな標準VRCSDK uploadで症状が消えるか
```

VRChat公式は、SDK Control PanelのBuilderタブから `Build & Publish` する標準手順を案内しています。

- https://creators.vrchat.com/avatars/creating-your-first-avatar/

ここをclean baselineとして使います。

---

## 6. 改善後のA/Bテスト

同一Avatar、同一Project stateで比較します。

### A: clean baseline

```text
VRChat SDK Control Panel
→ Build & Publish
→ 完了を確認
→ HMDで確認
```

### B: CAU

```text
CAU
→ Start Upload
→ build / uploadが最後まで完了したことを確認
→ HMDで確認
```

途中停止、Editor crash、platform変更、resume promptなどが発生したrunは「CAU正常系」のデータとして扱いません。

比較時に固定するもの:

- Avatar Prefab
- Material
- Shader
- MA component
- Animator
- Unity version
- VRChat SDK version
- target platform

記録するもの:

| 観測 | baseline | CAU |
|---|---|---|
| build完了 | PASS/FAIL | PASS/FAIL |
| upload完了 | PASS/FAIL | PASS/FAIL |
| 中断発生 | YES/NO | YES/NO |
| resume発生 | YES/NO | YES/NO |
| Direct VR | NORMAL/ABNORMAL | NORMAL/ABNORMAL |
| Left Eye | NORMAL/ABNORMAL | NORMAL/ABNORMAL |
| Right Eye | NORMAL/ABNORMAL | NORMAL/ABNORMAL |
| Mirror | NORMAL/ABNORMAL | NORMAL/ABNORMAL |

---

## 7. Shader / Materialはもう疑わなくていい？

違います。

clean uploadでも再現する場合は、依然としてShader / Material / Built Avatarを調べます。

```text
Step 1  upload完了状態を確認
Step 2  clean VRCSDK uploadでbaselineを取る
Step 3  CAUの中断 / resume有無を記録
Step 4  Source vs Builtを比較
Step 5  Renderer / Material identity
Step 6  Material feature A/B
Step 7  Shader stereo compatibility
Step 8  必要ならShader assetを限定Reimport
```

この順序なら、状態機械の異常をShader問題と誤認しにくくなります。

---

## 8. Source Avatarが正常でもBuilt Avatarは同じとは限らない

upload stateに問題がなければ、次はbuild transformationを見ます。

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

---

## 9. Shader Reimportはどこに置く？

最初ではなく後段です。

Unityはmanual Reimportを公式に提供しています。

- https://docs.unity3d.com/Manual/ImporterConsistency.html

lilToonの通常Shader assetは公式repositoryで確認できます。

- https://github.com/lilxyzw/lilToon/blob/master/Assets/lilToon/Shader/lts.shader

Reimportを試すのは、少なくとも次の条件を満たす場合です。

```text
clean uploadでも異常
AND
Source / Built差だけでは説明できない
AND
問題Rendererが共通Shaderを使う
```

「VRだけ二重」という症状だけでは、Reimportを初手にしません。

---

## 10. 壊れた診断例

今回の失敗は、症状から直接Shaderへ降りたことです。

```text
VR only
→ Stereo
→ Shader
→ lilToon
→ lts.shader
```

さらに前版では、改善したつもりで

```text
VRCSDK vs CAU
```

までしか見ていませんでした。

しかし今回必要だったのは、

```text
CAUのrunは正常終了していたか？
```

という、さらに一段細かい状態確認でした。

---

## 11. 読者が試せる再現手順

異常が出たAvatarに対して、次の順に実施します。

1. Material / Shader / Prefabを変更しない。
2. 直前のCAU runが正常終了したか確認する。
3. crash、cancel、platform変更、resumeがなかったか記録する。
4. VRChat SDK Control Panelからcleanに `Build & Publish` する。
5. 実HMDでDirect / Left / Right / Mirrorを確認する。
6. sourceを変更せずCAUでuploadする。
7. CAUが最後まで正常終了したことを確認する。
8. 同じHMD、同じ条件で再測定する。
9. CAUが途中停止したrunと正常完了runを同列に比較しない。
10. clean uploadでも再現する場合だけSource / Built / Material / Shaderへ進む。

記録フォーマット:

```text
Avatar:
Unity:
VRCSDK:
CAU:
Platform:

Previous CAU run:
  Build completed:
  Upload completed:
  Interrupted:
  Resume involved:
  Platform switched:

Clean VRCSDK upload:
  Direct:
  Left:
  Right:
  Mirror:

Clean CAU upload:
  Direct:
  Left:
  Right:
  Mirror:

Source changes between runs: NONE
```

---

## 12. やってはいけないこと

### 「VRだけ二重だからShader」と確定する

Stereo依存の可能性は上がりますが、upload stateを飛ばします。

### 「CAUで再現したからCAU自体が悪い」と確定する

今回の追加観測では、問題はCAU一般ではなく **途中停止したCAU状態** でした。

### 中断runと正常完了runを同じ条件として比較する

比較条件が壊れています。

### Shader、Material、CAU versionを同時に変える

直っても何が効いたか分かりません。

### `Reimport All` を初手にする

大量の状態を同時に変え、比較可能性を失います。

---

## まとめ

今回の最大の学びは、Shaderの知識ではありません。

**診断木に「uploadの完了状態」が抜けていたこと**です。

VRChat Avatarの最終見た目を診断するときは、少なくとも次を分けて観測します。

```text
Source
→ Build transformation
→ Bundle
→ Upload state
   ├─ clean / completed
   └─ interrupted / resumable
→ Backend
→ Client / Stereo
```

今回の真因について最も正確な表現はこれです。

> **CAUが悪かったのではなく、CAUが途中で止まった状態のままになっていたことが悪かった。**

今後の第一手も変わります。

> **Shaderを触る前に、直前のuploadが本当に最後まで正常終了していたか確認する。**

## 参考一次情報

### VRChat

- Creating Your First Avatar: https://creators.vrchat.com/avatars/creating-your-first-avatar/

### Continuous Avatar Uploader

- Repository: https://github.com/anatawa12/ContinuousAvatarUploader
- CHANGELOG: https://github.com/anatawa12/ContinuousAvatarUploader/blob/master/CHANGELOG.md

### Unity / Shader

- Stereo rendering: https://docs.unity3d.com/2022.3/Documentation/Manual/SinglePassStereoRendering.html
- Single-pass instanced custom shaders: https://docs.unity3d.com/Manual/SinglePassInstancing.html
- Importer consistency: https://docs.unity3d.com/Manual/ImporterConsistency.html

### Shader過去事例

- Poiyomi #4: https://github.com/poiyomi/PoiyomiToonShader/issues/4
- Poiyomi #24: https://github.com/poiyomi/PoiyomiToonShader/issues/24
- lilToon #46: https://github.com/lilxyzw/lilToon/issues/46
