# Unity / VRChatで「片目だけ変」「VRだけ二重」「突然ピンク」になったときのShaderトラブルQA

UnityやVRChatでアバターを触っていると、次のような症状に遭遇することがあります。

- Unity上では普通なのに、VRChatに入ると見た目がおかしい
- Desktopでは正常なのに、VRでは二重に見える
- 左右の目で見え方が違う
- ある日突然、マテリアルがピンクになる
- Shaderを入れ直しても直らない

このページは、**lilToon と Poiyomi Toon Shader の実際のGitHub Issueをもとに、「何が起きているか分からない人」向けに整理したQA**です。

専門用語を知らなくても、上から順番に確認できる構成にしています。

---

## Q1. 「左右の目で見え方が違う」のは、本当に起こるの？

はい。過去に実際の報告があります。

Poiyomi Toon Shader の Issue #4 `Seeing Double's` では、**Desktopユーザーには正常なのに、VRユーザーにはアバターが二重に見える**症状が報告されています。

https://github.com/poiyomi/PoiyomiToonShader/issues/4

さらに Issue #24 `Panosphere Left/Right Eye Phase Issue` では、**左目と右目でエフェクトの位相がずれる**事例が報告されています。Desktopやミラーでは正常だったという点も重要です。

https://github.com/poiyomi/PoiyomiToonShader/issues/24

つまり、

> 「Unityでは普通だからShaderは正常」

とは限りません。

VRでは左右の目を別々に描画するため、**VRでしか露出しないShader側・Stereo描画側の不具合**があります。

---

## Q2. 「VRだけおかしい」なら、まず何を疑えばいい？

最初に疑うのは、アバター固有のMeshやMaterialだけではありません。

複数のアバターや複数のMaterialで同じ症状が出ているなら、より上位の共通部分を疑います。

確認順は次の通りです。

1. Shaderのimport / compile状態
2. Shader package自体の状態
3. UnityのLibrary / Asset import結果
4. VR用のStereo描画経路
5. Graphics APIやUnityバージョン
6. 最後に個別Material / Mesh

「この服だけ壊れた」と思っていたのに、実際には**共通Shader側が壊れていた**ということがあります。

---

## Q3. Shaderは「入っている」のに壊れることがある？

あります。

lilToon Issue #406 では、`lil_vert_encryption.hlsl` を開けないShader compile errorが発生し、複数のlilToon Shaderが壊れ、モデルがピンクになる症状が報告されています。

https://github.com/lilxyzw/lilToon/issues/406

また Issue #366 では、lilToonのShader内部エラーによりMaterialが正常にロードできない事例があります。

https://github.com/lilxyzw/lilToon/issues/366

Poiyomiでも Issue #25 に `Failed to compile`、Issue #40 に大量のcompile error、Issue #70 にShader compilation中のUnity終了が報告されています。

https://github.com/poiyomi/PoiyomiToonShader/issues/25

https://github.com/poiyomi/PoiyomiToonShader/issues/40

https://github.com/poiyomi/PoiyomiToonShader/issues/70

重要なのは、**「Package Managerに表示されている」ことと「Shaderが正常にコンパイルされている」ことは別**だという点です。

---

## Q4. 「再インストールしたのに直らない」はおかしい？

おかしくありません。

Unityでは、元のassetだけでなく、import後に生成された状態もLibrary等に保持されます。

そのため、Shader packageを入れ直しても、**既存のimport結果や別packageとの競合が残っている場合、同じ症状が続く**ことがあります。

Poiyomi Issue #36では、Rim Lightingがランダムに壊れ、packageをre-importしても改善しなかったと報告されています。

https://github.com/poiyomi/PoiyomiToonShader/issues/36

lilToon Issue #375では、Unity起動ごとに異常が出るMaterialが変わるという、状態依存性の強い症状も報告されています。

https://github.com/lilxyzw/lilToon/issues/375

したがって、単純な「入れ直し」だけで直らない場合は、**import状態・cache・他package・Graphics経路まで切り分ける必要があります**。

---

## Q5. 「Unityでは正常、VRChatにアップロードすると壊れる」こともある？

あります。

lilToon Issue #307では、UnityやGesture Managerでは正常なのに、VRChatへアップロードすると服・耳・尻尾・メガネ等の表示が壊れる事例が報告されています。

https://github.com/lilxyzw/lilToon/issues/307

Issue #308でも、Unity上では正常なのに、特定のDissolve設定があるとVRChatアップロード後にShader全体が壊れる事例があります。

https://github.com/lilxyzw/lilToon/issues/308

このため、確認場所を混同しないことが重要です。

- Scene Viewで正常
- Game Viewで正常
- Play Modeで正常
- VRChat Clientで正常
- VRの左右眼で正常

これらは**同じテストではありません**。

---

## Q6. 「片目だけおかしい」とき、最初に何をする？

いきなりMaterialを全部作り直すより、次の順番が安全です。

### 1. DesktopとVRを比較する

Desktopでも壊れるのか、VRだけ壊れるのかを確認します。

VRだけならStereo描画やVR向けShader variantの疑いが上がります。

### 2. 別のアバターでも同じ症状が出るか確認する

複数アバターで出るなら、個別Meshより共通Shader / Unity環境を優先します。

### 3. Unity ConsoleのShader errorを確認する

`Shader error`、`failed to compile`、`failed to open source file`、`incompatible keyword space` などがないか確認します。

lilToonでは実際に `State comes from an incompatible keyword space` の報告があります。

https://github.com/lilxyzw/lilToon/issues/361

### 4. Shaderのバージョンを確認する

「最新なら安全」とは限りません。

特定バージョンで壊れ、旧バージョンへ戻すと直る事例もあります。

lilToon Issue #311では、1.10.3では動作するが2.x系でURPがピンクになると報告されています。

https://github.com/lilxyzw/lilToon/issues/311

### 5. それでも原因不明ならimport / Library状態を疑う

ここで初めて、再importやLibrary再生成を検討します。

ただし、プロジェクト全体を壊す可能性があるので、**Git管理またはバックアップを取ってから**行います。

---

## Q7. lilToonとPoiyomi、どちらにも似た事故はある？

あります。

両方のIssueを横断すると、少なくとも次の系統が繰り返し現れます。

- Shader compile失敗
- include fileが見つからない
- Unityバージョン差
- Graphics API差
- DesktopとVRの差
- 左右眼差
- Upload前後の差
- Shader最適化後の差
- package更新後の回帰

つまり、今回のような症状を「このアバターが壊れている」と即断するより、**過去Issueと症状を照合する方が速い**ことがあります。

---

## Q8. 過去Issueはどれくらいある？

2026年8月12日時点で、GitHub Search APIの `is:issue` 条件で確認できた件数は次の通りです。

- lilToon: 337件
- Poiyomi Toon Shader: 66件

一次情報:

https://api.github.com/search/issues?q=repo%3Alilxyzw%2FlilToon+is%3Aissue&per_page=1

https://api.github.com/search/issues?q=repo%3Apoiyomi%2FPoiyomiToonShader+is%3Aissue&per_page=1

このため、1件ずつGoogle検索するより、**Issue群そのものを知識基盤として保存し、症状から横断検索できるようにする**方が効率的です。

---

## Q9. 今回のような問題を再現可能な形で報告するには？

最低でも次の情報を残します。

- Unity version
- VRChat SDK version
- lilToon / Poiyomi version
- Desktopでは正常か
- VRでだけ壊れるか
- 左目 / 右目のどちらで異常が出るか
- Scene / Game / Play Mode / VRChatのどこで再現するか
- ConsoleのShader error全文
- 問題が複数アバターで再現するか
- package更新前後で変化したか

これが揃うと、

> 「Materialがおかしい気がする」

という曖昧な状態から、

> 「VRのStereo経路のみで再現し、複数アバター共通、Shader compile errorあり」

という診断可能な状態に変わります。

---

## まとめ

左右眼差、VRだけの二重表示、突然のピンク化は、珍しく見えても**過去に実際の報告があります**。

最も重要なのは、最初から個別Materialを疑い続けないことです。

複数のアバターで同じ症状が出るなら、

> Shader → import / compile → Unity環境 → Stereo描画 → 個別Material

の順で上から切り分ける方が効率的です。

そして、lilToonとPoiyomiのIssue履歴そのものを検索可能な知識基盤にしておくと、「過去に同じ事故があったか」をすぐ確認できます。

## 参考一次情報

- lilToon Issues: https://github.com/lilxyzw/lilToon/issues?q=is%3Aissue
- Poiyomi Toon Shader Issues: https://github.com/poiyomi/PoiyomiToonShader/issues?q=is%3Aissue
- Poiyomi #4 Seeing Double's: https://github.com/poiyomi/PoiyomiToonShader/issues/4
- Poiyomi #24 Panosphere Left/Right Eye Phase Issue: https://github.com/poiyomi/PoiyomiToonShader/issues/24
- lilToon #307: https://github.com/lilxyzw/lilToon/issues/307
- lilToon #308: https://github.com/lilxyzw/lilToon/issues/308
- lilToon #361: https://github.com/lilxyzw/lilToon/issues/361
- lilToon #406: https://github.com/lilxyzw/lilToon/issues/406
