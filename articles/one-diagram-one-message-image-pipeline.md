---
title: "10枚の図を作ったのに読みにくい：技術記事を『1図1メッセージ』に分解する画像パイプライン"
emoji: "🖼️"
type: "tech"
topics: ["chatgpt", "imagegeneration", "zenn", "technicalwriting", "automation"]
published: true
published_at: 2026-08-13 09:21
---

技術記事に図を増やせば、読みやすくなる。

そう考えて「10枚作る」という目標を置くと、別の失敗が起きます。**枚数だけ満たして、1枚の中に複数の論点を詰め込みすぎる**失敗です。

今回 `KAFKA2306/articles` の画像運用を見直したとき、最初に出た候補画像はまさにそれでした。記事本文、評価、CI、10個の図までを1枚に押し込んだ巨大な合成図です。情報量は多いのに、読者が「いま何を見るべきか」を決めにくい。

そこで、画像生成の目標を「10枚作る」から、**先に10個の役割を決め、1回の生成で1つのメッセージだけを描く**へ変えました。

この設計は、既存の `pipeline/config.json` にある `image_policy.objective = reader_comprehension` と `require_explanatory_value = true` を、実際の制作手順へ落としたものです。

- https://github.com/KAFKA2306/articles/blob/main/pipeline/config.json

また、Zenn公式はGitHub連携時の画像をリポジトリ直下の `/images` に置けること、対応拡張子と1ファイル3MB以内という制約を公開しています。

- https://zenn.dev/zenn/articles/deploy-github-images

以下では、失敗した1枚目から、生成・保存・埋め込み・検証までを1本の再利用可能な手順にします。

## 1. 問題：図の枚数と理解しやすさは同じ指標ではない

最初の失敗例はこの画像です。

この図で見るべき点は、**1枚の中に「記事メタデータ」「レビュー」「10個の別図」「CI結果」まで同居していること**です。個々の情報が正しいか以前に、視線の入口が多すぎます。

![1枚に役割を詰め込みすぎた失敗例](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-01.png)

この失敗から、品質条件を次のように分けました。

- **count**: 必要な図が揃っているか
- **role**: 各図に固有の役割があるか
- **message**: 1図で伝える主張が1つか
- **placement**: 本文のどこで何を見る図なのかが明示されているか
- **reference**: Markdown参照先と実ファイルが一致するか

既存記事でも、図の直前に「この図で見るべき点」を置く形式を使っています。

- https://github.com/KAFKA2306/articles/blob/main/articles/csv-migration-dry-run-before-write.md

## 2. 原因：記事全体をそのまま「1枚の絵」にしようとすると責務が混ざる

画像モデルの内部理由を推測する必要はありません。制作側で観測できたのは、**記事全体の要素を同時に1枚へ載せようとした結果、複数の説明責務が混在した**ことです。

この図で見るべき点は、入力が「記事全体」のままだと、図の責務も問題・原因・実装・検証へ枝分かれすることです。生成前に責務を切らない限り、完成画像の中で分離するしかありません。

![記事全体を一度に図示すると責務が増える因果](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-02.png)

改善後は、記事アウトラインから先に図の役割を抽出します。

```text
article outline
  ├─ problem
  ├─ cause
  ├─ design
  ├─ implementation
  ├─ verification
  ├─ failure
  └─ reproduction

↓ 先に role を固定

01 anti-pattern
02 cause
03 role manifest
04 generation contract
05 production flow
06 naming contract
07 markdown placement
08 QA gates
09 failure recovery
10 reproduction
```

## 3. 設計判断と代替案：枚数ではなく「role manifest」を正準にする

採用した設計は、画像生成前に10行の role manifest を作る方法です。

この図で見るべき点は、画像ファイルより先に「何を説明するか」を固定することです。生成物を見てから役割を後付けしません。

![10枚の役割を先に固定するrole manifest](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-03.png)

今回の manifest は次です。

| # | role | 1つだけ伝えること |
|---|---|---|
| 01 | anti-pattern | 1枚に全部を詰め込むと入口が増える |
| 02 | cause | 記事全体を直接図示すると責務が枝分かれする |
| 03 | manifest | 生成前に10役を固定する |
| 04 | generation | 10回に分け、各回1図だけ作る |
| 05 | flow | outline→generate→save→embed→audit |
| 06 | naming | slugと連番を1対1対応させる |
| 07 | placement | 図の前後に読み方を書く |
| 08 | QA | count/unique/existence/size/extを検査する |
| 09 | recovery | 壊れた1枚だけを差し替える |
| 10 | reproduce | 読者が同じ手順を再現する |

代替案もあります。

### 代替案A：1枚の大きなインフォグラフィック

全体俯瞰には向きます。ただし記事本文を順に読む用途では、複数の論点を一度に見せやすい。今回は「本文の理解順」を優先したため不採用にしました。

### 代替案B：必要な箇所だけ2〜3枚

既存設定の `fixed_count` は `null` で、常に10枚を要求する設計ではありません。通常運用なら、説明価値のある箇所だけ図にする方が合理的です。

今回だけは、**ChatGPT Imagesを10回、各回1図として動かす運用そのものを検証する**ため10役へ固定しました。

この図で見るべき点は、「10枚を1回で作る」のではなく「1回=1役」を10回積み上げる点です。これはこの検証の運用契約であり、一般的な最適値だとは主張しません。

![1回1図を10回積み上げる生成契約](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-04.png)

OpenAIはChatGPTとAPIで画像生成機能を提供しています。ここではモデル内部の生成過程ではなく、**呼び出し単位を制作側の責務境界として使う**ことだけを扱います。

- https://openai.com/index/image-generation-api/

## 4. 実装：outline → role → generate → save → embed → audit

制作フローは次の6段階にしました。

この図で見るべき点は、画像生成が中央の1工程にすぎず、その前後にrole固定とファイル検証があることです。

![記事画像の制作フロー](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-05.png)

### 4.1 slugを先に決める

今回のslugは次です。

```text
one-diagram-one-message-image-pipeline
```

### 4.2 ファイル名にslugと連番を含める

```text
images/
└─ one-diagram-one-message-image-pipeline/
   ├─ one-diagram-one-message-image-pipeline-01.png
   ├─ one-diagram-one-message-image-pipeline-02.png
   ├─ ...
   └─ one-diagram-one-message-image-pipeline-10.png
```

この図で見るべき点は、Markdown側の図番号と実ファイルを目視でも機械でも突合できることです。`01.png`だけより、別ディレクトリへ移したときも由来が残ります。

![slugと連番を1対1対応させる命名規則](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-06.png)

Zenn公式のGitHub連携では、画像はリポジトリ直下の `/images` に配置し、その下の構造は自由です。対応拡張子は `.png` `.jpg` `.jpeg` `.gif` `.webp`、ファイルサイズは3MB以内とされています。

- https://zenn.dev/zenn/articles/deploy-github-images

### 4.3 図の前後に「読み方」を置く

Markdownの画像記法そのものだけでは、読者は「なぜここにこの図があるか」を本文から推測する必要があります。そこで図の直前に、見るべき点を1〜2文で固定します。

この図で見るべき点は、本文→見るべき点→画像→次の説明という順序です。画像を独立した飾りにしません。

![本文と図を接続する配置規則](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-07.png)

Zenn公式Markdownガイドは画像記法、Altテキスト、キャプションの書き方を公開しています。

- https://zenn.dev/zenn/articles/markdown-guide

## 5. 検証：10枚あるだけではpassにしない

最低限、次を機械検査できます。

1. Markdown内の対象画像参照が10個
2. 10個すべてunique
3. 各参照先ファイルが存在
4. 拡張子がZenn対応形式
5. 各ファイルが3MB以内

この図で見るべき点は、生成品質そのものと、**公開時にリンク切れしないこと**を別ゲートとして扱う点です。

![画像公開前のQAゲート](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-08.png)

再利用できる最小チェックは次のように書けます。

```python
from pathlib import Path
import re

slug = "one-diagram-one-message-image-pipeline"
article = Path(f"articles/{slug}.md").read_text(encoding="utf-8")
refs = re.findall(rf"/images/{slug}/[^)]+", article)

assert len(refs) == 10
assert len(set(refs)) == 10

allowed = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
for ref in refs:
    path = Path(ref.lstrip("/"))
    assert path.exists(), path
    assert path.suffix.lower() in allowed, path
    assert path.stat().st_size <= 3 * 1024 * 1024, path
```

この検査は「図が理解しやすい」ことまでは保証しません。そこはrole manifestとレビューで見る必要があります。機械検査が担当するのは、数・参照・実在・公開形式です。

## 6. 失敗と学び：壊れた1枚だけを捨てられる構造にする

1枚の巨大図を最後に作る方式では、1要素を直したいだけでも全体を再生成しやすくなります。

10個の責務を独立させると、たとえば `04-generation` だけが曖昧だった場合、04だけを差し替えればよい。01〜03と05〜10を巻き込みません。

この図で見るべき点は、失敗範囲を「記事全体」ではなく「1 role」に閉じ込めることです。

![壊れた1枚だけを再生成するfailure recovery](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-09.png)

学びは3つです。

- **生成回数は品質ではない**。roleが重複していれば10枚あっても弱い。
- **ファイル名は運用UI**。slug+連番ならレビュー時の突合コストが下がる。
- **画像品質と公開品質を分離する**。画像の説明価値は人間/レビュー、リンク実在や3MB制限は機械で検査する。

## 7. 改善後の例

改善後は、各画像が前節のrole manifestの1行だけを担当します。

たとえば図06は「命名規則」だけ、図08は「QAゲート」だけです。図06へCIや文章構成を足しません。逆に図08へ生成プロンプトの話を足しません。

これにより、記事をスクロールしたときに図だけ拾っても、

```text
失敗
→ 原因
→ 分解
→ 生成契約
→ 制作
→ 保存
→ 配置
→ 検査
→ 復旧
→ 再現
```

という理解順になります。

## 8. 読者が試せる再現方法

手元の技術記事1本で次を試せます。

この図で見るべき点は、再現に必要なのが特定の題材ではなく、**役割の固定→個別生成→保存→参照監査**という順序だけであることです。

![1図1メッセージ画像パイプラインの再現手順](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-10.png)

1. 記事の問題・原因・設計・実装・検証・失敗・再現を箇条書きにする
2. 図にする価値がある役割を重複なしで列挙する
3. 今回の検証を再現するなら10役へ固定する
4. ChatGPT Imagesを1回につき1図として個別に生成する
5. `/images/{slug}/` にslug+連番で保存する
6. 各図の直前に「この図で見るべき点」を書く
7. Markdown参照数・unique数・ファイル実在・拡張子・3MB上限を検査する
8. 壊れた図だけ再生成する
9. PRで記事と10画像を同時にレビューする
10. merge後のmainでも10参照と10実ファイルを再確認する

## 9. まとめ

技術記事の画像生成で、最初に管理すべきなのはプロンプトではなく**説明責務**でした。

`10 images` を品質目標にすると、10枚の似た図や、1枚の巨大な合成図でも条件を満たせます。

一方で、

```text
role manifest
→ one generation / one role
→ slug + sequence
→ explicit placement
→ existence audit
```

までを契約にすると、画像は「数」ではなく記事構造の一部になります。

既存の `image_policy.objective = reader_comprehension` を実制作へ落とすなら、**1図1メッセージは実装しやすい境界**でした。

## 一次情報・再現証拠

- KAFKA2306/articles `pipeline/config.json`  
  https://github.com/KAFKA2306/articles/blob/main/pipeline/config.json
- KAFKA2306/articles 既存の図配置例  
  https://github.com/KAFKA2306/articles/blob/main/articles/csv-migration-dry-run-before-write.md
- Zenn公式: GitHubリポジトリ連携で画像をアップロードする方法  
  https://zenn.dev/zenn/articles/deploy-github-images
- Zenn公式: Markdown記法一覧  
  https://zenn.dev/zenn/articles/markdown-guide
- OpenAI公式: image generation API  
  https://openai.com/index/image-generation-api/
