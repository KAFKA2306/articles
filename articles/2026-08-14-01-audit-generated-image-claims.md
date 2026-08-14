---
title: "生成AIの図に「CI成功」と書いてあった。見栄えより先に「信じてよい」を作る"
emoji: "🔎"
type: "tech"
topics: ["chatgpt", "imagegeneration", "testing", "automation", "zenn"]
published: false
---

生成AIに技術記事の図を頼むと、かなりそれらしいものが出てくる。

GitHub風の緑のチェック。

`CI SUCCESS`。

改善率。

PR番号。

URL。

問題は、**実行していないCIまで成功したように描ける**ことだ。

```text
画像内
✓ lint
✓ test
✓ deploy

実GitHub
未確認
```

画像ファイルは存在する。

Markdownの参照も正しい。

Zennにも表示できる。

それでも、画像の中の主張は真実とは限らない。

そこで `KAFKA2306/articles` では、生成画像を最終成果物ではなく、**もう一度検証する必要があるuntrusted input** として扱うことにした。

この記事で扱うのは画像生成の上手なpromptではない。

**読者が「分かりやすい」と「信じてよい」を同時に得られる図を、どう公開するか**である。

## 「表示できる」と「信じてよい」は別のgateにする

技術記事の画像には、少なくとも2種類の検証がある。

```text
artifact gate
  - ファイルが存在する
  - 対応拡張子である
  - サイズ制限内である
  - Markdown参照先が正しい

evidence gate
  - 数値の元データがある
  - URLが実在する一次情報である
  - CI状態をGitHubからread-backした
  - PR / commitをGitHubからread-backした
  - 因果表現に仕様・コード・実験の根拠がある
```

前者だけ通すと、**きれいに表示されるが根拠のない図**を公開できる。

だから、画像の存在確認と画像内claimの検証を同じ `passed` にしない。

この分離が最初の設計判断だった。

## `CI SUCCESS` は、pixelでは証拠にならない

生成画像はGitHub風UIを非常に自然に描ける。

```text
CI SUCCESS
P99: 42 ms
改善率: 37%
PR: #123 merged
commit: abcdef1
```

見た目だけなら、かなり説得力がある。

しかし、この5項目はすべて別の証拠が必要だ。

| 画像内claim | 採用条件 |
|---|---|
| CI SUCCESS | 実workflow run / checkをread-back |
| P99 42 ms | 計測条件とraw resultがある |
| 37%改善 | before / afterと計算方法がある |
| PR #123 merged | 実PR stateをread-back |
| commit abcdef1 | 実commitが存在し、対象変更と一致 |

**画像そのものをevidence sourceにしない。**

CIを記事へ書くならGitHubを確認する。

性能値を書くなら計測artifactへ戻る。

画像は説明する。

証拠は別に持つ。

## 一番危険なのは、生成AIが「分かりやすくするため」に数字を補うこと

比較図には数字がある方が理解しやすい。

そのため生成AIは、promptに存在しない値まで自然に置くことがある。

```text
Before 18.7%
After   0.6%
95% improved
```

しかし、計測ログがなければこの3つはすべて使わない。

必要なのは、少なくとも次である。

```text
before source
+ after source
+ same measurement definition
+ calculation
+ observed_at
```

「95%」という数字が見栄えを良くしても、読者の理解はむしろ壊れる。

**正確な図は、派手な図より長く使える。**

## URLやPR番号も、画像の文字列ではなく外部状態として確認する

URLは画像に描かれていてもclickできない。

PR番号も、それらしい番号を生成できる。

そこで画像内に外部entityを出す場合は、本文側に実URLを持たせる。

```text
visual label
   ↓
article claim
   ↓
source URL / GitHub state
```

画像と本文が同じclaimを持つなら、**本文のevidence chainを正準**にする。

画像はそこへ従属させる。

## 「1記事10枚」より「1図1つの理解障壁」を見る

以前は、図を増やすことで記事を分かりやすくしようと考えやすかった。

しかし、画像枚数は読者価値のKPIではない。

`KAFKA2306/articles` の現行方針でも、画像は `objective: reader_comprehension`、固定枚数ではなく `require_explanatory_value: true` として扱っている。

- https://github.com/KAFKA2306/articles/blob/main/pipeline/config.json
- https://github.com/KAFKA2306/articles/blob/main/pipeline/audit.py

そこで残す基準を変えた。

悪い基準:

```text
各節に1枚ある
10枚作った
見栄えが統一されている
```

良い基準:

```text
この図がないと理解しにくい境界が1つある
その境界を図が本文より短く説明できる
図内の事実claimをすべて証拠へ戻せる
```

**one diagram / one message は画像枚数ルールではなく、cognitive loadを減らすルール**として使う。

## 生成図を公開するまでの最小flow

実運用では、次の順にすると分かりやすい。

```text
1. 本文のcentral claimを決める
      ↓
2. 図が解く理解障壁を1つ決める
      ↓
3. 生成AIで図を作る
      ↓
4. 画像内のtext / number / URL / stateを列挙する
      ↓
5. claimごとにevidenceへ照合する
      ↓
6. 根拠がないclaimを削除・再生成する
      ↓
7. artifact gateを通す
      ↓
8. 本文と画像の意味が一致しているか確認する
      ↓
9. 公開
```

重要なのは、生成直後を完成にしないことだ。

**画像生成は制作工程であって、検証工程ではない。**

## claim inventoryを作ると監査しやすい

複雑な図なら、画像内の主張を簡単な表へ落とす。

```yaml
claims:
  - text: "CI SUCCESS"
    type: github_state
    evidence: workflow_run_url

  - text: "37% improvement"
    type: measured_metric
    evidence: benchmark_artifact

  - text: "PR #123"
    type: github_entity
    evidence: pull_request_url
```

この形にすると、画像監査を「なんとなく目視」から、claim単位のverificationへ変えられる。

すべての図にYAMLを持たせる必要はない。

ただし、数値・URL・状態・比較結果を多く含む図では効果が大きい。

## 画像に書かない方がよい情報もある

変化が速い情報は、画像へ焼き込むほど更新コストが上がる。

例えば、

- current CI state
- current issue count
- current version
- current price
- current model availability

は、本文やlive UIの方が向くことがある。

画像へ固定するなら、観測日時を明示する。

**図は静的artifactであることを忘れない。**

## この設計で得たいのは「AI画像を使わない」ことではない

生成AIの図は便利だ。

文章だけでは重いarchitecture、state transition、before/afterを短く見せられる。

だから禁止したいわけではない。

むしろ、**安心して多く使えるように、事実確認の境界を別にする**。

- 生成は速くする
- claim verificationは厳しくする
- 画像枚数は固定しない
- 読者理解に効かない図は作らない
- 画像を証拠にしない

この分離があると、生成AIの速度と技術記事の信頼性を両立しやすい。

## まず1枚だけ監査するなら

既存の記事や資料から、数字やステータスを含む生成画像を1枚選ぶ。

そして画像内の文字を、次の4種類へ分ける。

```text
説明ラベル
実測値
外部状態
因果・結論
```

説明ラベルはそのままでよい。

残り3つにはevidenceを要求する。

それだけでも、「それっぽい図」と「信じてよい図」の差はかなり見える。

生成AIで図を作ること自体は簡単になった。

だから次に必要なのは、**図を作れる能力ではなく、どの図なら公開してよいか判断できる能力**だと思う。
