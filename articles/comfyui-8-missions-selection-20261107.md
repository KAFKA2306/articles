---
title: "22,213件集めても「最良」とは言えなかった：ComfyUIの8用途別Workflow選定結果"
emoji: "🧪"
type: "tech"
topics: ["comfyui", "githubactions", "python", "workflow", "ai"]
published: false
---

公開されているComfyUIのWorkflowを見つけても、どれから試せばよいのか分からない。動画、音声、3Dモデルでは必要なものが違うし、GitHubでよく見かけるWorkflowが自分のPCで動くとは限らない。

そこで公開Workflowを継続収集する仕組みを作り、**22,213件の候補から8つの制作用途ごとに上位5件を選定**した。候補自体は見つかったが、集計したところ、予想以上にはっきりした限界も分かった。

**選定した40枠はすべて実機未検証だった。しかも、採点に使うはずの「人気」「更新」のデータが、このスナップショットでは全候補で未取得だった。**

この記事は「動作保証付きのおすすめ8選」ではない。**実際に試す候補を素早く絞り込み、どこを検証すれば採用できるか判断するための選定結果**を紹介する。

## まず、何をどれだけ調べたのか

2026年11月7日 09:08 JSTのGitHub Actions成果物を取得し、入力台帳のSHA-256を独立に再計算して一致を確認した。

| 項目 | スナップショットで確認した数値 |
| --- | ---: |
| 収集台帳の候補数 | 22,213件 |
| 内容ハッシュなどに基づく統合後のグループ数 | 20,340件 |
| 制作用途 | 8領域 |
| 用途別の上位選定枠 | 40枠（各5件） |
| 上位40枠の実機検証済み | 0枠 |
| 台帳に記録された採用実績 | 0件 |

入力台帳のSHA-256は `37e0c8459306be28b281ee3988e7118fa0bc11f39eb5efd2b6c364d83cab6880`。選定JSONに記録されたハッシュとも一致した。

- [収集・選定を実行したGitHub Actions](https://github.com/KAFKA2306/comfyui-workflows-factory/actions/runs/42316197788)
- [台帳の固定リビジョン](https://github.com/KAFKA2306/comfyui-workflows-factory/blob/11a51ff718b84b5ed08dd6a2778bb345a5ab4e73/data/workflow_registry.json)
- [評価処理の実装](https://github.com/KAFKA2306/comfyui-workflows-factory/blob/68397e6b13920cef1f10f6eda633322af1ca01a4/src/gwp/evaluate.py)

Actionsの成果物には `selection.json` が含まれる。ただし保存期間は7日間なので、後から確認する場合は固定リビジョンの台帳と評価コードを使う。

## 8領域で上位に選ばれたWorkflow

以下は**各領域の首位候補**と、その用途で最初に確かめたいポイント。リンクは収集時点のGitコミットに固定している。点数は後述する事情から、合計100点の総合評価ではなく、実際に算出できていた「用途適合40点」の値を示す。

| 制作用途 | 上位候補のWorkflow | 用途適合 | 実行時に確かめたいこと |
| --- | --- | ---: | --- |
| VRChatワールド | [Qwen Image 360 LoRA](https://github.com/comfy-org/workflow_templates/blob/60d0d2c2f5c98ab50116abd837156e4010534657/templates/template_qwen_Image_2512_360_lora.json) | 32/40 | 360度背景のつなぎ目、ワールドへの組み込み |
| アバター・衣装 | [Character Sheet](https://github.com/comfy-org/workflow_templates/blob/60d0d2c2f5c98ab50116abd837156e4010534657/templates/templates-character_sheet.json) | 32/40 | 同じキャラクターの向き・表情の一貫性 |
| BOOTH商品 | [Trellis2 Image to Model](https://github.com/comfy-org/workflow_templates/blob/60d0d2c2f5c98ab50116abd837156e4010534657/templates/3d_pixal3d_trellis2_image_to_model.json) | 34/40 | メッシュ品質、販売・再配布に必要な権利 |
| YouTube・Shorts | [LTX 2.3 Image to Video](https://github.com/comfy-org/workflow_templates/blob/60d0d2c2f5c98ab50116abd837156e4010534657/templates/video_ltx2_3_i2v.json) | 36/40 | 動きの破綻、画質、生成時間 |
| Podcast・音声 | [Chatterbox TTS Dialogue](https://github.com/comfy-org/workflow_templates/blob/60d0d2c2f5c98ab50116abd837156e4010534657/templates/audio-chatterbox_tts_dialog.json) | 36/40 | 発話の聞き取りやすさ、話者の一貫性 |
| 映画・アニメーション | [LTX 2.3 Image to Video](https://github.com/comfy-org/workflow_templates/blob/60d0d2c2f5c98ab50116abd837156e4010534657/templates/video_ltx2_3_i2v.json) | 34/40 | 複数カット間の映像の連続性 |
| 3Dモデル | [Trellis2 Lowpoly](https://github.com/aaroncose/comfyui-trellis-wan-workflows/blob/4bca9c91c9e9d1cb17e1e50c23e625e77344a656/workflows/trellis2/img2glb-lowpoly.json) | 40/40 | 穴のないメッシュ、ポリゴン数、UV |
| ゲーム制作 | [Trellis2 Lowpoly](https://github.com/aaroncose/comfyui-trellis-wan-workflows/blob/4bca9c91c9e9d1cb17e1e50c23e625e77344a656/workflows/trellis2/img2glb-lowpoly.json) | 36/40 | ゲームエンジンへの取り込みと実行負荷 |

8領域でも、首位のWorkflowは**重複を除くと6種類**。同じ素材生成処理が複数の作品づくりに使えそうだ、という「用途上の候補」の重なりであり、各用途での品質が同じと確認されたわけではない。

同点候補もある。YouTubeでは[LTX 2.3 Text to Video](https://github.com/comfy-org/workflow_templates/blob/60d0d2c2f5c98ab50116abd837156e4010534657/templates/video_ltx2_3_t2v.json)が36点で並び、映画・アニメーションではこれと[Wan 2.2 5B](https://github.com/comfy-org/workflow_templates/blob/60d0d2c2f5c98ab50116abd837156e4010534657/templates/video_wan2_2_5B_ti2v.json)も34点で並んだ。3Dモデルの次点には[Hunyuan3D Image to Model](https://github.com/comfy-org/workflow_templates/blob/60d0d2c2f5c98ab50116abd837156e4010534657/templates/3d_hunyuan3d_image_to_model.json)が34点で入っている。

これらは、**対応する制作物を比較するための候補**であって、商用利用・VRAM・必要モデル・実行成功を保証するものではない。

## 100点満点なのに、実際には40点分しか比較できなかった

評価設計は次の3軸で構成されている。

- GitHubリポジトリの人気：30点
- GitHubリポジトリの更新状況：30点
- 制作用途への適合：40点

大事なのは、人気と更新は**個別Workflowの人気や更新頻度ではなく、公開元リポジトリ単位の代理指標**だということだ。たとえ取得できたとしても、星の多いリポジトリ内のすべてのWorkflowが優秀だとは言えない。

さらに、今回の `selection.json` では、統合後の**20,340候補すべてで `score_components.popularity` と `score_components.freshness` が `null`** だった。つまり未取得であり、人気・更新が低いことを示す「0点」ではない。

今回の順位は、事実上、用途適合の手掛かりで決まっていた。たとえば「40/40」は**用途適合の上限に達した**という意味で、「総合的に40%しか使えない」でも「品質が満点」でもない。

候補が多いほどランキングは精密そうに見える。しかし**比較に必要な情報が欠けたまま件数を増やしても、選定の確実性は自動的には上がらない**。これは、同じように公開コードや制作テンプレートを自動収集する場合にも当てはまる。

## 実際に使うなら、こういう順で採否を決める

候補ごとに、次の順番で確認する。

1. **原典を固定する**：リンク先のコミットとWorkflowの内容を保存する。別の日の最新版と混ぜない。
2. **使える条件を確認する**：Workflow自体と使用モデルのライセンス、必要モデル、Custom Node、対応バージョン、VRAMを調べる。未確認なら採用扱いにしない。
3. **同じ課題で動かす**：たとえば画像から動画なら同じ入力画像・解像度・条件で、候補ごとの成功率、出力品質、生成時間を記録する。
4. **制作物に接続して判断する**：VRChatならUnityへの組み込み、音声なら実際の聞き取りやすさ、3Dならメッシュの利用可否まで確認する。JSONが読み込めただけでは完成ではない。

ここで初めて、「見つけたWorkflow」から「使えるWorkflow」へ進む。

汎用化できる判断基準は、**発見・用途の仮選定・実行確認・制作採用を別の状態として管理すること**。大量の公開サンプルを比較するときには使える考え方だが、用途別のキーワード適合点をそのまま品質点に変換することはできない。

## この選定結果が証明していないこと

今回確かめたのは、**特定時点の台帳から、どのWorkflowが用途別の上位に挙がるか**という事実である。GPU上での動作、作品の品質、商用利用の可否、最新モデルとの互換性、個別Workflowの人気は実証していない。選定枠40件はすべて `readiness: unverified` だった。

次に必要なのは候補をもっと増やすことよりも、各領域でひとつずつ実行し、**同条件の制作結果を残すこと**だ。少なくとも、最初に試す候補を探す作業は、この固定スナップショットから始められる。

**再検証の条件**：収集台帳、評価コード、モデル依存関係、公開元のWorkflowが更新された場合は、同じ評価時刻・同じ入力条件で順位と動作を再確認する。この記事の順位は2026年11月7日のスナップショットに限定される。

参考：[ComfyUI Workflows Factory](https://github.com/KAFKA2306/comfyui-workflows-factory) / [GitHub Actionsの保存済み実行](https://github.com/KAFKA2306/comfyui-workflows-factory/actions/runs/42316197788) / [Zennコミュニティガイドライン](https://zenn.dev/guideline)
