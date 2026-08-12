---
title: "lilToonで左右の目の見え方が違うとき、最初に何をする？ — Reimportだけで切り分けるQA"
emoji: "👁️"
type: "tech"
topics: ["vrchat", "unity", "liltoon", "shader"]
published: true
published_at: 2026-08-12 19:12
---

# lilToonで左右の目の見え方が違うとき、最初に何をする？ — Reimportだけで切り分けるQA

VRChatで「左目では正常なのに右目ではおかしい」「VRだけ見え方が崩れる」といった症状が出たとき、いきなりアバターやMaterialを作り直す必要はありません。

今回のように、**るるね本体でも、追加した別モデルでも同じ左右眼エラーが出ている**なら、まず個別モデルではなく、両方が共有しているShader経路を疑います。

このQAでは、最初の切り分けとして **るるね本体が実際に使っているlilToon Shaderを1個だけReimportし、VRで左右眼を確認する**ところまでを説明します。

---

## Q1. 最初に何を触ればいい？

最初に触るのは、しろい〜ぬ固有の `farbody` ではありません。

まず、**るるね本体で異常が見えているRenderer**を1つ選びます。

たとえば次のような部分です。

- Body
- Face
- Hair

Hierarchyで対象を選び、Inspectorの `Skinned Mesh Renderer` を開きます。

その中の `Materials` から、実際に使われているMaterialを1つクリックします。

---

## Q2. Materialを開いたら、何を見る？

Inspector上部にある **Shader名** を確認します。

通常のlilToonなら、公式リポジトリの次のShader assetが対応します。

`Assets/lilToon/Shader/lts.shader`

lilToon公式リポジトリでは、このファイルが次のShaderを定義しています。

```text
Shader "lilToon"
```

一次情報:

https://github.com/lilxyzw/lilToon/blob/master/Assets/lilToon/Shader/lts.shader

---

## Q3. Unityのどこに `lts.shader` がある？

ProjectウィンドウでlilToonのShaderフォルダを探します。

典型例は次の位置です。

```text
Assets
└─ lilToon
   └─ Shader
      ├─ lts.shader
      ├─ lts_cutout.shader
      ├─ lts_fur.shader
      └─ ...
```

lilToon公式リポジトリにも、少なくとも次のShader assetが存在します。

- `lts.shader`
- `lts_cutout.shader`
- `lts_fur.shader`

公式Shaderディレクトリ:

https://github.com/lilxyzw/lilToon/tree/master/Assets/lilToon/Shader

VPM / UPM経由で導入している場合は、Unity上で `Packages` 側に表示されることがあります。

見つからない場合は、Projectウィンドウの検索欄で `lts.shader` を検索します。

---

## Q4. 見つけたら何を押す？

`lts.shader` を右クリックして、**Reimport** を選びます。

```text
lts.shader
   ↓ 右クリック
Reimport
```

Unity公式ドキュメントでも、手動ReimportはAssetを右クリックして `Reimport` を選ぶ手順です。

またUnityは、手動Reimport時に新しいimport結果と以前のcached import resultを比較します。

一次情報:

https://docs.unity3d.com/Manual/ImporterConsistency.html

---

## Q5. この段階で「やらないこと」は？

最初の切り分けでは、変更範囲を広げません。

次の操作はまだ行いません。

- lilToonを削除しない
- lilToonを再インストールしない
- `Library` を削除しない
- `Reimport All` をしない
- Material設定を変更しない
- Prefabを変更しない
- Unityバージョンを変更しない

理由は単純で、複数の変数を同時に変えると「何をしたら直ったのか」が分からなくなるためです。

なお、VRChat公式のCurrent Unity Versionページでは、現在の推奨Unityを **2022.3.22f1** としています。

一次情報:

https://creators.vrchat.com/sdk/upgrade/current-unity-version/

---

## Q6. Reimport後は何を確認する？

まず、るるね本体だけをVRで確認します。

```text
るるね
├─ 左眼 → 正常？
└─ 右眼 → 正常？
```

ここではScene Viewだけで判断しません。

今回知りたいのは **VRの左右眼で症状が消えたか** だからです。

---

## Q7. るるねが直ったら？

次に、しろい〜ぬ側も確認します。

```text
lts.shader を Reimport
        ↓
るるねが直る
        ＋
しろい〜ぬも直る
        ↓
共通 lilToon import / compile 経路が
原因だった可能性が上がる
```

これは原因を100%確定する試験ではありません。

ただし、個別のMeshやMaterialを変更せず、共有Shader assetのReimportだけで複数モデルの症状が同時に変化したなら、共通Shader経路を原因候補として強くできます。

---

## Q8. `lts.shader` をReimportしても直らなかったら？

そこで初めて、るるねのMaterialが実際に使っている**別のlilToon Shader asset**を確認します。

たとえばMaterialがCutout系なら `lts_cutout.shader`、Fur系なら `lts_fur.shader` が候補になります。

重要なのは、フォルダを丸ごとReimportするのではなく、**実際に異常が出ているMaterialが利用しているShaderから1個ずつ試す**ことです。

```text
異常Materialを選ぶ
      ↓
Shader名を確認
      ↓
対応する lts*.shader を探す
      ↓
その1ファイルだけ Reimport
      ↓
VRで左右眼を再確認
```

---

## Q9. 結局、今やる操作を一行で言うと？

**るるねの異常が見えるMaterialをクリック → Shader名を確認 → Projectで対応する `lts*.shader` を探す → 右クリック → Reimport → VRで左右眼を確認**

これが最初の一手です。

---

## なぜこの順番なの？

今回の診断で重要なのは、「しろい〜ぬだけが壊れている」と仮定しないことです。

るるね本体でも同じ左右眼異常が見えているなら、個別モデルより先に、両者が共有する描画基盤を確認する方が切り分けとして情報量があります。

最初の試験では、変更を最小限にします。

```text
個別Mesh / Materialを変更する
            ↑ 後

共通Shader assetを1個だけReimportする
            ↑ 先
```

直らなければ次の仮説へ進めばよく、直った場合は「何が効いたか」を比較的明確に残せます。

---

## 一次情報

- lilToon `lts.shader`: https://github.com/lilxyzw/lilToon/blob/master/Assets/lilToon/Shader/lts.shader
- lilToon Shader directory: https://github.com/lilxyzw/lilToon/tree/master/Assets/lilToon/Shader
- Unity Manual — Importer Consistency: https://docs.unity3d.com/Manual/ImporterConsistency.html
- VRChat — Current Unity Version: https://creators.vrchat.com/sdk/upgrade/current-unity-version/
