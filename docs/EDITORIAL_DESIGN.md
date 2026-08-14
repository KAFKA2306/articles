# Editorial Design

## Purpose

この文書は、記事生成器の編集判断を固定するための設計資料です。
目標は、正確な記事を大量に作ることではありません。
**検証できる一つの発見を、最後まで読みたくなり、読後に具体的な判断・行動・運用へつながる形で届けること**です。

本文は単独で意味が通ることを前提にし、過去のrepository履歴や既存記事を読んでいることへ依存しません。

## Zenn一次情報から固定する方針

Zennは2026年2月のガイドライン更新で、一般知識をまとめ直すことより、具体的な試行錯誤と書き手固有の視点を重視すると明示しました。現行ガイドラインでも、読者が理解しやすい構成、冒頭で得られる情報の明示、正確なタイトル、実体験や考察を推奨し、誇張したタイトルや生成AIによる乱造を避けるよう示しています。

- https://info.zenn.dev/2026-02-03-community-guidelines-update
- https://zenn.dev/guideline
- https://info.zenn.dev/2026-03-10-ai-contents-guideline

したがって、このrepoでは「一般知識を正しく説明できた」を公開理由にしません。
実装、観測、失敗、比較、測定のどれかによって、書き手が実際に得た知見が必要です。

## 2026/Q2の高反応Publicationを観察する

Zenn公式の2026/Q2表彰は、2026年4月〜6月に9本以上投稿した123 Publicationを対象に、1記事あたりの平均いいね数で紹介しています。

- 1位 エアークローゼットテックブログ: 平均65
- 2位 ナレッジセンス: 平均51
- 3位 LayerX: 平均50

公式記事:
https://info.zenn.dev/2026-07-02-publication-quarterly-award-2026q2

Zenn公式は1位Publicationの代表例として、次の記事が300を超えるいいねを獲得したと紹介しています。

https://zenn.dev/aircloset/articles/d416342f46f16b

この記事を構造として見ると、技術用語の定義より先に「PRが無人でマージされる」「障害が気づく前に直っている」という二つの具体的なシーンを提示しています。その後で業界の技術概念を説明し、123 apps、約63万行の実装、約56万行のテスト、月別PR数などの具体値を出し、最後には自動化できない領域も明示しています。

ここから採用するのは文体ではなく、次の順序です。

```text
具体的な現象
  ↓
なぜそうなるのかという問い
  ↓
必要になった技術だけ説明
  ↓
実測・実装証拠
  ↓
成立条件と限界
  ↓
読者がそのまま使える判断・手順
```

## Zennfes Spring 2026受賞例を観察する

Zenn公式は2026年7月24日にZennfes Spring 2026の受賞作を公開しています。

https://info.zenn.dev/2026-07-24-zennfes-spring-2026-result

「この春、始めたこと」最優秀賞:
https://zenn.dev/harumikun/articles/cd898e4032ca37

この記事は冒頭のTL;DRで、Excel VBAとAIエージェントの相性が悪い具体点を列挙し、それを解決するOSSを作ったこと、さらに株価ダッシュボードやゲームを自然言語指示だけで作れたことまで先に見せています。本文ではGUIダイアログやログがAIから見えないという具体的な障害から実装へ進み、250倍高速化という実運用の結果も提示しています。

TiDBテーマ特別賞:
https://zenn.dev/optimisuke/articles/tidb-kobe-population-insight

この記事は「RDB・ベクトルDB・全文検索を別々に管理するのが面倒」という具体的な痛みから始め、神戸市の人口統計CSVと政策PDFを組み合わせたアプリを作る、という実験へ直結しています。抽象的なRAG論を先に展開せず、作りたいものを先に定義しています。

## 採用する編集原理

### 1. 一つの発見を選ぶ

記事は「知っていることを全部書く場所」ではありません。
候補探索では、次のいずれかに分類できる現象を探します。

- anomaly: 値や挙動が通常の予想から外れる
- contradiction: 同時に成立しそうにない二つの事実が並ぶ
- failure: もっともらしい方法が具体的に失敗する
- unexpected-connection: 離れた技術やデータが一つの因果でつながる
- counterintuitive-result: 自然な予想と測定結果が逆になる
- magnitude: 桁差や急変があり、その理由を説明できる

どれにも入らない場合、説明テーマとして有用でも、主記事候補としては弱いと判定します。

### 2. 仮説を途中で更新する

完成した知識を最初から順番に説明すると、調査の手触りが消えます。
記事生成器は必ず次を持ちます。

```text
central_question
initial_hypothesis
observation / experiment
hypothesis_update
surprising_finding
technical_payoff
```

最初の予想が最後まで一度も変わらない場合、本当に記事として面白い発見があるかを再確認します。

### 3. 用語は後から出す

読者が疑問を持つ前に、provenance、RAG、MCP、fail-closeなどを定義しません。
先に具体的な困りごとや数字を示し、その現象を説明するために必要になった位置でだけ用語を導入します。

### 4. 面白さと正確さを別々に採点する

従来の5軸は残します。

- logic
- utility
- readability
- originality
- clarity

しかし、これだけでは「正しいが続きを読みたくない」記事を排除できません。
そのため別に4軸を持ちます。

- interest
- discovery
- narrative
- context

技術品質が高くても編集品質が基準未達なら公開しません。

### 5. タイトルの引きは本文の証拠から作る

強いタイトルは必要ですが、誇張は不要です。
数字、失敗、矛盾、実測結果など、本文で検証できるものだけをタイトルの引きに使います。

### 6. Reader before → afterを候補段階で決める

実装テーマが見つかっても、すぐ記事にしません。
先に次を埋めます。

```text
reader_before
  ↓
reader_after
```

`reader_before` は「MCPを知らない」のような知識不足ではなく、

```text
AIへPC作業を任せたいが、どこまで触るか分からず怖い
```

のような利用者の摩擦です。

`reader_after` は、

```text
MCPを理解できる
```

ではなく、

```text
低risk taskへAllowedRoot / read-only / result evidenceを置き、どこまで委任するか判断できる
```

のように具体的な判断・行動・運用へします。

### 7. Design philosophyは技術選定ではなくtrade-offを書く

`FastAPIを使った`、`GitHub Actionsを追加した` はdesign philosophyではありません。

読者価値のため、何を優先し何を捨てたかを書きます。

例:

```text
自動化率より誤投稿を防ぐことを優先し、remote identityを確認できないrunはpublishしない
```

これなら、別のtool stackでも同じ判断を再利用できます。

### 8. Commercial pullはproofから作る

sales-firstは広告文を足すことではありません。

```text
実際にどこまで動いているか
何を止めたか
どの規模で使ったか
何が未実証か
```

を証拠付きで見せ、読者自身が「自分でも使えそう」「この種類の問題なら任せられそう」と判断できる状態を作ります。

`お問い合わせください` を足してもproofは増えません。
読者の次actionは、checklist、template、最小導入手順、decision tableなど本文から自然に導きます。

### 9. 弱い記事は公開せず、統合・退役できる

技術的に正しいから残す、という判断はしません。

- 同じreader jobなら強い1本へ統合する
- 固有proofがなければarchiveへ落とす
- runtime証拠が不足するなら`published:false`を維持する
- article countをKPIにしない

2026-08-14の棚卸しでは、同じreader jobを扱う旧稿を統合し、固有incidentを証明できなかったfail-close稿をarchiveへ移しました。

- `docs/article-portfolio-audit-2026-08-14.md`

## Reader value blocking gate

技術品質・story品質が基準を満たしても、次が残る記事は公開しません。

- `weak_reader_value`: before→afterが本文だけで説明できない
- `weak_differentiation`: 一般tutorial / docs / AI要約で代替できる
- `missing_proof_of_value`: 価値主張とpublic evidenceが接続していない
- `forced_commercial_cta`: 本文から自然に導けない問い合わせ・契約等を要求する
- `technical_value_as_product`: 技術名・repository名・実装行為を価値そのものにしている

これらはscore低下ではなくblocking issueです。

## 固定見出しを強制しない

候補dataには `reader_before` / `reader_after` / `design_philosophy` / `why_this_article` / `proof_of_value` / `desired_reader_action` / `non_goal` を必須化します。

一方、公開本文に、

```text
## Vision
## Design philosophy
## Why
## Commercial intent
```

を強制しません。

意味構造は必要ですが、scene→問い→観測→仮説更新→proof→持ち帰りのstoryへ自然に統合します。
テンプレート見出しを埋めただけの記事を増やさないためです。

## Publication gate

公開可能になるには、一次情報ゲートに加えて次を満たします。

- technical `overall >= 3.8`
- technical 全軸 `>= 3.5`
- `story_overall >= 4.0`
- editorial 全軸 `>= 3.8`
- `interest >= 4.1`
- reader value blocking issueが0件
- `proof_of_value` と本文の実証範囲が一致する

月末の候補比較では、技術品質より先に `story_overall`、`interest`、`discovery` を比較します。
これにより、正確さが同程度なら、より強い発見、読ませる構造、具体的なreader outcomeを持つ記事が選ばれます。
