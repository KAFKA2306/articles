---
title: "生成図は一次情報ではない：ChatGPT Imagesを10回回して『架空のCI・数値・URL』を公開前に落とす"
emoji: "🔎"
type: "tech"
topics: ["chatgpt", "imagegeneration", "zenn", "testing", "automation"]
published: true
published_at: 2026-08-13 09:21
---

技術記事の図は、コードより危険なことがあります。

コードならテストで落とせます。しかし生成画像の中に「CI成功」「5.0/5.0」「95%改善」「PR #42」のような**もっともらしい表示**が入っても、Markdownのリンクチェックは通ります。PNGやWebPが存在することと、その中身が事実であることは別だからです。

今回 `KAFKA2306/articles` の公開フローを1回通す試行で、ChatGPT Imagesを **10回、各回1画像**として実行しました。その候補画像には、実行時に一次情報で確認していない評価値・CI状態・性能値・URL・PR/commit表記が複数含まれました。

ここで画像モデルの内部原因は推測しません。観測できた問題だけを扱います。

**生成図を「証拠」ではなく「未検証の入力」として受け取り、公開前に factual claim を別ゲートで落とす必要がある。**

既存の `pipeline/config.json` でも画像方針は `objective: reader_comprehension`、`require_explanatory_value: true` です。この記事では、その方針に **evidence audit** を追加する設計を具体化します。

- https://github.com/KAFKA2306/articles/blob/main/pipeline/config.json
- https://github.com/KAFKA2306/articles/blob/main/articles/csv-migration-dry-run-before-write.md

## 1. 問題：画像リンクが正しくても、画像内の主張は未検証のまま通る

最初に見るのは、生成候補の一部です。

この図で見るべき点は **LAPRAS AI Review 5軸がすべて5.0/5.0と表示されていること**です。この数値は今回のLAPRAS実測値ではなく、画像生成物の中に描かれたテキストです。

![生成画像内に描かれた未検証のレビュー値](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-01.webp)

この画像ファイルが存在し、Markdownから正しく参照できても、5.0/5.0という値の根拠にはなりません。

ここで分けるべきゲートは2つです。

```text
artifact gate
  └─ 画像が存在する / 参照できる / Zennで扱える

evidence gate
  └─ 画像内の数値・状態・因果・URLが一次情報で確認済み
```

Zenn公式はGitHub連携時の画像をリポジトリ直下の `/images` に配置できること、対応拡張子、1ファイル3MB以内という公開条件を説明しています。これは **artifact gate** の根拠になります。

- https://zenn.dev/zenn/articles/deploy-github-images

一方、画像内部に書かれた技術的主張の真偽まではZennの画像配置ルールでは検証されません。

## 2. 原因：生成画像を「出力」として扱い、再び「入力」として査読していない

2枚目には、PRがmerge済みで複数のCI checkが成功したような画面が描かれています。

この図で見るべき点は **緑のチェックが並ぶと、それだけで実CI結果に見える**ことです。今回の画像生成時に、この表示と実GitHub Actions runを1対1照合したわけではありません。

![生成画像内の未検証CI成功表示](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-02.webp)

問題は「生成AIが画像を作る」ことではなく、工程設計です。

```text
article facts
  ↓
image generation
  ↓
generated image
  ↓
そのまま publish   ← ここが危険
```

生成画像にはテキスト・数値・UI・コード断片が再構成されます。したがって、生成後は再び **untrusted input** として扱う方が安全です。

改善後はこうします。

```text
verified article facts
  ↓
image generation
  ↓
untrusted generated image
  ↓
visual claim inventory
  ↓
primary-source verification
  ↓
verified / illustrative / reject
  ↓
publish
```

## 3. 具体例：それらしく見える因果を、一次情報なしで採用しない

3枚目はDocker Composeのヘルスチェック失敗例です。

この図で見るべき点は、`start_period` が短いことと再起動ループを因果で結んでいることです。図としては理解しやすい一方、**この具体的な設定と結果は今回の実測ではありません**。

![生成画像内の未検証な因果説明](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-03.webp)

生成図を公開する前に、少なくとも次を区別します。

- **構造図**: コンポーネント関係だけを示す。数値や成功結果を持たない
- **比較図**: 比較軸の根拠URLが必要
- **因果図**: 因果を裏付ける仕様・実験・コード証拠が必要
- **結果図**: 元データ・実行条件・取得日時が必要

「因果・比較・構造・流れ」を1図1メッセージにするだけでは不十分で、**その1メッセージが factual claim なら evidence を要求する**、という二段階が必要でした。

## 4. 壊れた失敗例：グラフは最も危険な“もっともらしさ”を作れる

4枚目には、KafkaのthroughputとP99 latencyらしきグラフが描かれています。

この図で見るべき点は、軸・系列・数値が揃うと「ベンチマーク済み」に見えることです。しかしこのグラフは、今回のリポジトリで実行したベンチマーク結果ではありません。

![生成画像内の未検証ベンチマーク](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-04.webp)

この種の図には、画像ファイル以外に最低でも次が必要です。

```text
benchmark evidence
├─ source data
├─ command / script
├─ environment
├─ timestamp
├─ commit SHA
└─ result artifact
```

1つでも追跡できないなら、結果図としてではなく「概念図」へ落とすか、削除します。

## 5. URLも画像内に書かれただけでは一次情報にならない

5枚目には、Apache KafkaやConfluent風の一次情報URLが並んでいます。

この図で見るべき点は **URL文字列がもっともらしくても、画像内テキストはクリックもHTTP検証もできない**ことです。

![生成画像内に描かれた未検証URL一覧](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-05.webp)

記事本文ではURLをテキストとして保持し、実際に開ける一次情報URLだけを残します。画像内URLは装飾ではなく factual claim の一種として扱います。

今回の記事で使う外部仕様は、公開前に実URLを確認した次のものだけです。

- OpenAI公式の画像生成機能: https://openai.com/index/image-generation-api/
- Zenn公式の画像配置ルール: https://zenn.dev/zenn/articles/deploy-github-images
- Zenn公式Markdown画像記法: https://zenn.dev/zenn/articles/markdown-guide

## 6. 数字には必ず「どの実験の値か」を要求する

6枚目は、Idempotency導入でRPSが大きく上がったように見える性能グラフです。

この図で見るべき点は、**性能倍率らしき結論が視覚的に強く提示されていること**です。生成画像に描かれた数値は、計測ログの代わりにはなりません。

![生成画像内の未検証性能倍率](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-06.webp)

結果図を許可する条件を、次のように固定できます。

```yaml
claim:
  kind: benchmark
  status: verified
  value: "..."
  evidence:
    - command: "..."
    - commit: "..."
    - artifact: "..."
    - source_url: "https://..."
```

`status: verified` を埋める材料がなければ、画像から数値を外します。

## 7. 「改善率」は特に二重チェックする

7枚目には、Flaky test発生率が `18.7% → 0.6%`、約95%改善したような棒グラフがあります。

この図で見るべき点は、**before/afterと改善率が揃うと、実測結果として非常に強く読める**ことです。今回この数値を実測したログはありません。

![生成画像内の未検証before-after値](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-07.webp)

### 壊れた例

```text
改善前 18.7%
改善後 0.6%
約95%改善
```

根拠データがないまま図だけ公開する。

### 改善後の例

```text
計測なし
→ 数値を図から削除
→ 「固定時刻・固定seed・外部依存のmock化」の構造だけを示す
```

測っていないものを「N/A」にする方が、もっともらしい数字を埋めるより再利用可能です。

## 8. PR番号・commit SHA・merge状態も画像から信用しない

8枚目には `PR #42`、commit、merge completedという表示があります。

この図で見るべき点は、**GitHub UI風の見た目と実GitHub状態を分離すること**です。

![生成画像内の未検証PRとcommit表示](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-08.webp)

公開レポートへPR番号やcommit SHAを書くなら、GitHub API/実URLから取得した値だけを本文へ転記します。生成画像を逆に情報源としてはいけません。

この原則は、今回の公開フロー自体にも適用します。最終報告のPR/commitは、merge後にGitHubから再取得した値だけを使います。

## 9. 実装：figure manifestで「何を検証したか」を画像の外に置く

9枚目には、モデル名、プロンプト長、リクエスト数、TTLなどのベンチマーク条件らしき表が描かれています。

この図で見るべき点は、**条件表そのものも生成できるため、条件が細かいほど真実らしく見える**ことです。

![生成画像内の未検証ベンチマーク条件](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-09.webp)

そこで、画像の外に正準manifestを置く設計にします。

```json
{
  "figures": [
    {
      "id": "01",
      "role": "failure-example",
      "mode": "illustrative",
      "factual_claims": [],
      "evidence_urls": []
    },
    {
      "id": "08",
      "role": "pr-state-example",
      "mode": "anti-pattern",
      "factual_claims": ["PR number", "commit SHA", "merge status"],
      "evidence_urls": []
    }
  ]
}
```

公開用の結果図なら、`mode` を `verified` にし、`evidence_urls` を空にできないようにします。

擬似コードなら次です。

```python
def validate_figure(item):
    if item["mode"] == "verified":
        assert item["evidence_urls"]
    if item["factual_claims"] and item["mode"] == "illustrative":
        raise ValueError("illustrative figure must not carry factual claims")
```

重要なのはOCR精度ではありません。**生成前に「この図に事実を入れるか」を宣言し、事実を入れる図だけ証拠必須にする**ことです。

## 10. 検証：リンク10/10は必要条件であって十分条件ではない

最後の生成候補には「画像リンク確認 10枚すべて存在・参照一致」という表示まで描かれました。

この図で見るべき点は、**“確認済み”という文字自体も生成できる**ことです。したがって、確認結果は画像ではなく実ファイルとMarkdownを機械的に照合します。

![生成画像内に描かれたリンク確認表示](/images/one-diagram-one-message-image-pipeline/one-diagram-one-message-image-pipeline-10.webp)

Zenn互換のartifact gateは、たとえば次で再現できます。

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

このtestが通っても、画像内の `5.0/5.0` や `95%改善` が正しいとは証明しません。そこで公開ゲートを分離します。

```text
Gate A: artifact
- 10 refs
- 10 unique files
- supported extension
- <= 3 MB

Gate B: evidence
- 数値 → 元データあり
- 因果 → 一次仕様/実験あり
- URL → HTTPで実在確認
- PR/commit → GitHubで実在確認
- CI → workflow runで確認

Gate C: editorial
- 1図1メッセージ
- 本文直前に「何を見るか」
- 重複役割なし
```

## 11. 設計判断と代替案

### 採用：生成図をuntrusted inputとして再査読する

長所は、生成モデルの内部挙動へ依存しないことです。どのモデルでも、画像に factual claim があれば同じgateを適用できます。

### 代替案A：図から文字を完全に禁止する

安全側ですが、設定値・比較表・コード断片を見せたい記事では表現力を失います。

### 代替案B：画像生成を使わずSVG/Mermaidだけにする

検証可能性は上がりますが、今回の目的はChatGPT Imagesを実際に使うことです。また、画像生成を使わないこと自体は「生成画像のevidence audit」の解決ではありません。

### 代替案C：生成画像を人間が目視するだけ

必要ですが、PR番号・URL・数値の実在確認を毎回目視だけにすると漏れます。artifactとURL/commit/CIの存在確認は機械へ寄せる方が再現できます。

## 12. 読者が試せる再現方法

手元の記事で、次の最小実験ができます。

1. 技術記事から factual claim を1つだけ選ぶ
2. ChatGPT Imagesでその概念図を1枚生成する
3. 画像内に、入力していない数値・URL・成功状態・コード・PR表記がないか確認する
4. factual claim を一覧化する
5. 各claimへ一次情報URLまたは実行artifactを割り当てる
6. 割り当てられないclaimは画像から削るか、`illustrative` として事実表現を外す
7. 画像を `/images/{slug}/` に保存する
8. Markdown参照・実在・拡張子・3MB上限を機械検査する
9. PRで「見た目」と「証拠」を別項目としてレビューする
10. merge後にmain上の画像・参照・一次情報URLを再確認する

今回の10枚は、まさに **「生成画像内の文字を証拠と誤認しない」ための失敗教材**として使いました。

## 13. 失敗と学び

今回の最大の失敗は、最初から「生成された画像は記事本文と同じ事実性を持つ」と暗黙に扱いかけたことです。

10回実行してみると、生成物にはレビュー点数、CI成功、性能グラフ、改善率、ベンチ条件、URL、PR/commitなど、**技術記事でそのまま使うと危険な情報形式**が一通り現れました。

一方で、ここから得た設計は単純です。

> 画像生成の完了をpublication readyと呼ばない。

`generated → audited → verified` を別状態にするだけで、生成図を一次情報と混同しにくくなります。

## 14. まとめ

技術記事でChatGPT Imagesを使うとき、品質ゲートは「画像が綺麗か」だけでは足りません。

- **artifact gate**: 画像10枚が存在し、Markdown参照と一致する
- **evidence gate**: 数値・因果・URL・PR・CIが一次情報と一致する
- **editorial gate**: 1図1メッセージで、役割が重複しない

この3つを分離すると、画像生成ツールを止めずに使いながら、生成物をそのまま証拠にはしない運用ができます。

## 一次情報・再現証拠

- KAFKA2306/articles `pipeline/config.json`  
  https://github.com/KAFKA2306/articles/blob/main/pipeline/config.json
- KAFKA2306/articles 既存の画像配置記事  
  https://github.com/KAFKA2306/articles/blob/main/articles/csv-migration-dry-run-before-write.md
- OpenAI公式: 画像生成APIの紹介  
  https://openai.com/index/image-generation-api/
- Zenn公式: GitHubリポジトリ連携で画像をアップロードする方法  
  https://zenn.dev/zenn/articles/deploy-github-images
- Zenn公式: Markdown記法一覧  
  https://zenn.dev/zenn/articles/markdown-guide
