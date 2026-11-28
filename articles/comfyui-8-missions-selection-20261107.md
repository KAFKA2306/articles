---
title: "「見つかった順」は「使える順」ではない"
emoji: "🧪"
type: "tech"
topics: ["comfyui", "githubactions", "python", "workflow", "ai"]
published: false
created_at: "2026-11-07"
updated_at: "2026-11-28"
---

公開されているAIワークフローを集め、上位候補を並べる。数千件から数十件へ絞れれば、技術選定が進んだように見える。だが制作担当者が知りたいのは、自分の環境で目的の成果を作れるかどうかだ。

候補の発見と採用は違う仕事である。ComfyUIの公開ワークフローを22,213件集めた選定では、上位40枠すべてが実機未検証だった。ここでは推薦一覧ではなく、なぜランキングを採用判断へ直結させてはいけないかを扱う。

## 点数の分母が欠けたランキング

2026年11月7日09:08 JSTの[GitHub Actions成果物](https://github.com/KAFKA2306/comfyui-workflows-factory/actions/runs/42316197788)を取得した。[入力台帳](https://github.com/KAFKA2306/comfyui-workflows-factory/blob/11a51ff718b84b5ed08dd6a2778bb345a5ab4e73/data/workflow_registry.json)のSHA-256は `37e0c8459306be28b281ee3988e7118fa0bc11f39eb5efd2b6c364d83cab6880` で、選定JSONの記録と一致した。内容ハッシュなどで統合した候補は20,340件、8用途ごとに5枠を選んだ。採用実績の記録は0件だった。

[評価処理](https://github.com/KAFKA2306/comfyui-workflows-factory/blob/68397e6b13920cef1f10f6eda633322af1ca01a4/src/gwp/evaluate.py)の配点と取得状態を分けると、何を比較できたかが見える。

| 指標 | 配点 | 当時の状態 |
| --- | ---: | --- |
| 公開元リポジトリの人気 | 30 | 全候補でnull |
| 公開元リポジトリの更新 | 30 | 全候補でnull |
| 制作用途への適合 | 40 | 算出済み |

欠損した60点は低評価ではない。人気と更新が未取得なのである。仮に取得できても、リポジトリの人気は個々のワークフローの品質を直接測った値ではない。

このときの40/40は用途適合の上限であって、総合品質の満点ではない。実機で失敗したという意味でもない。実際に動くかどうかは記録されていなかった。

## 同点でも、制作条件が異なる

YouTube向けに選ばれた[LTX 2.3 Image to Video](https://github.com/comfy-org/workflow_templates/blob/60d0d2c2f5c98ab50116abd837156e4010534657/templates/video_ltx2_3_i2v.json)と[Text to Video](https://github.com/comfy-org/workflow_templates/blob/60d0d2c2f5c98ab50116abd837156e4010534657/templates/video_ltx2_3_t2v.json)は、用途適合でともに36点だった。

一方は画像、他方は文章を入力とする。手持ちの画像の構図を維持して動画にしたいなら、同点であっても両者を同じ条件で比較することはできない。まず必要な入力を受け取れるかを判断する。

この差から、選定の状態を四つに分けられる。

| 状態 | 何が分かれば進めるか |
| --- | --- |
| 発見 | 原典と版を特定できる |
| 用途適合 | 必要な入力・出力・目的に合う |
| 実行確認 | 対象環境で処理が完了する |
| 制作採用 | 品質・費用・権利・後工程の条件を満たす |

一つの段階で得た証拠を、次の段階の成功として扱わない。実行に必要なモデルが欠けていれば、作品の品質を評価する段階には達していない。逆に実機結果と制作条件がそろえば、それに基づいて採用順位を決めてよい。

## 上位候補を、比較の出発点として使う

当時の用途別首位は以下のとおりだ。リンクは収集時の版に固定し、点数は用途適合のみを示す。実行成功や品質を保証する一覧ではない。

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

8領域の首位は重複を除くと6種類だった。同じ素材生成処理を別の用途で利用できる可能性があるが、用途ごとの成功は別々に判断する必要がある。Actions成果物の保存期間は7日であり、後から調べる場合は固定台帳と評価コードを参照する。

## 一件を実用品へ移すための最小記録

まず自分が今使っているワークフローと、新しい候補一つを選ぶ。目的を「同じ静止画から編集可能な動画を生成する」のように固定し、必要条件をそろえる。候補のJSONを開いて入力と依存関係を調べるところから始められる。

| 項目 | 記録する内容 |
| --- | --- |
| 原典 | コミットとファイル |
| 用途 | 入力・出力・採用条件 |
| 実行環境 | モデル、Custom Node、VRAM、利用条件 |
| 比較条件 | 入力画像、解像度、seed、設定 |
| 実行結果 | 成否、出力、生成時間 |
| 採否 | 品質、後工程への接続、権利、費用 |

未確認の欄には未確認と書く。条件がそろってから実行し、現在の制作工程で使える出力かを比べる。この手順は読者向けの実践案であり、上の候補で生成成功を確認した記録ではない。

公開テンプレート、OSS、AIツールの選定にもこの区別は使える。新しい候補の数を増やす前に、既に発見した一件を実行・制作採用へ進めるために不足している情報を調べる。検索順位を改善する仕事と、使える成果を得る仕事を取り違えない。
