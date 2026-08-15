# KAFKA2306/articles

**観測された失敗・異常・数字から、読者が「何を信じてよいか」「どこまで任せてよいか」「次へ進んでよいか」を判断できる技術記事を作るrepository。**

このrepoは、技術ニュース、ツール紹介、AI要約、ベストプラクティス集を量産するための場所ではありません。

公開する価値があるのは、一次情報と公開実装を追った結果、最初の予想が更新され、読者が別の現場へ持ち帰れる**判断規則**が残った記事です。

> **Observe the failure. Find the boundary. Prove the boundary. Give the reader a decision rule.**

## What we are trying to publish

過去のZenn記事を読み直すと、現在の強い記事には共通した形があります。

```text
具体的なscene / failure / number
        ↓
もっともらしい最初の解釈
        ↓
現在の一次情報 + 公開artifactで検証
        ↓
何が証明でき、何が証明できないかを分離
        ↓
最初の解釈を更新
        ↓
別の現場でも使えるdecision rule
```

主題は技術名ではなく、**authority / verification / decision boundary** です。

典型的には次を分離します。

- implementation と validation
- capability と authority
- runner と policy / oracle
- build と release と production verification
- detection と independent verification
- value と provenance
- AIが実行できること と AIへ許可してよいこと
- artifactが存在すること と visual / runtimeで完成していること
- 最新ノート と 判断時点の証拠

記事の価値は「詳しく説明した」ではなく、**読者がその境界を使って誤った判断を避けられること**です。

## The article signature

公開候補は最低でも次を持ちます。

1. **Reader job** — 読者は何を決めたいのか。
2. **Observed anomaly** — 実際に何が起きたのか。数字、失敗、矛盾、反例のどれかを置く。
3. **Initial hypothesis** — 最初は何が原因・正解だと思ったか。
4. **Evidence** — 現在取得できる一次情報と公開artifact。
5. **Boundary** — その証拠が許可する結論と、許可しない結論。
6. **Hypothesis update** — 何を見て考えを変えたか。
7. **Decision rule** — 読者が次回使える判定規則。
8. **Non-goal** — この記事が証明していないこと。
9. **Half-life** — どの事実が陳腐化しやすく、再検証が必要か。

### 良い記事の例となる問い

```text
「テストが通った」なら、誰が合格条件を決めたのか？
「Unityを操作できた」なら、見た目と実挙動まで誰が監査したのか？
「AI生成だと検出できる」なら、誰が独立して検証できるのか？
「deployできた」なら、build / validation / release / productionのどこまで成功したのか？
「数字が増えた」なら、source / scope / methodの何が変わったのか？
```

## What we do not publish

次は、正しく書けても原則として公開しません。

- 公式docsの要約
- インストール手順だけの記事
- リンク集・サービス一覧
- 「2026年の最強stack」のような比較表だけの記事
- tool / libraryの紹介だけの記事
- repoの変更履歴を記事へ変えただけのもの
- 二次情報を大量に並べたAIレポート
- 実装・測定・反証がない独自framework
- 根拠のない閾値、magic number、成功率
- 「Aを使ってBを作った」で終わる成功談
- 読む前から結論が常識的に決まっている記事
- weak questionを長文・図・引用で救った記事
- CTAを足しただけの営業記事

**技術的に正しいことは必要条件であって、公開理由ではありません。**

## Portfolio value

記事数はKPIではありません。

弱い記事は0点ではなく、読者から見た著者のsignalを薄め、古い主張の再検証コストを増やすため、**負のportfolio value** を持ち得ます。

公開後も記事を次のstateで監査します。

| State | 意味 |
|---|---|
| `KEEP` | 現在も証拠・判断規則・読者価値が強い |
| `REVALIDATE` | 核は強いが、価格・仕様・市場など陳腐化しやすい事実を再確認する |
| `REWRITE` | 核と証拠は残す価値があるが、現在の編集基準へ書き直す |
| `MERGE` | より強い記事へ統合し、単独記事を残さない |
| `RETIRE` | 誤解・重複・陳腐化・弱い証拠によりportfolioから外す |

公開済みだから永久保存、とは扱いません。

現行監査: [`docs/zenn-portfolio-audit-2026-08-15.md`](docs/zenn-portfolio-audit-2026-08-15.md)

## Evidence contract

外部事実は、公開時点で取得できる一次情報を優先します。

最低条件は `pipeline/contracts/article.md` と `pipeline/config.json` を正準とします。原則は次です。

- material claimのURLを実際に取得する
- vendor仕様はvendor公式、標準はstandards body、GitHub固有事実はGitHub上のartifactで確認する
- repo固有の主張は公開commit / PR / Issue / Actions / artifactへ接地する
- 数字には対象、期間、単位、比較基準を残す
- observation / inference / speculationを混ぜない
- inaccessible / stale / contradictoryなsourceはfail-closeする
- 取得できない事実を文章力で補完しない

**証拠が許可する以上の結論を書かない**ことを最優先します。

## Reader value contract

記事は、読者の状態を変えなければ公開価値がありません。

```text
reader_before
  ↓
この記事固有のproof / failure / comparison
  ↓
reader_after
```

`reader_after` は「理解した」「学んだ」では不十分です。

- 判断できる
- 止められる
- 採否を決められる
- 検証できる
- 再現できる
- 安全に委任できる
- 何が未確認か説明できる

のように、次のactionへ接続させます。

## Publication is human-controlled

Zenn公式は、AI利用時も**著者自身が正確性を検証し、経験・洞察を含めること**を「人が主体」として求めています。また、著者の確認が追いつかない速度の自動投稿や機械生成spamを問題視しています。

- https://info.zenn.dev/2026-03-10-ai-contents-guideline
- https://zenn.dev/guideline

したがって、このrepoではautomationの責務を次に限定します。

```text
scheduled automation
  = discover / draft / source-check / review / compare / report

manual selection
  = candidateをZenn-compatible draftへ昇格する

explicit human publication
  = published: true を許可する
```

**scheduleだけを理由に `published: true` へ変更してはいけません。**

`pipeline publish` という内部command名は「公開候補を `articles/` のunpublished draftへmaterializeする」意味であり、Zennでpublicにする権限を持ちません。

## Repository state

```text
artifacts/candidates/YYYY-MM/
  unpublished candidate。公開safeだがZenn sync surfaceではない。

artifacts/reports/YYYY-MM/
  source / review / selection evidence。

articles/
  Zenn-compatible source。published:true と明示承認された記事、および人間が選んだ published:false draftだけ。

pipeline/
  discovery / evaluation / audit implementation。

pipeline/contracts/article.md
  canonical editorial contract。
```

`published: false` はhard boundaryです。merge、CI green、選定、完成はpublication authorizationではありません。

## Candidate lifecycle

```text
public/private-safe idea seed
  ↓
current primary evidence
  ↓
reader job + anomaly
  ↓
question + initial hypothesis
  ↓
evidence / experiment
  ↓
boundary + hypothesis update
  ↓
decision rule + non-goal
  ↓
technical / editorial / reader-value review
  ↓
KEEP_PRIVATE / REWRITE / MERGE / RETIRE / human-selected draft
  ↓
explicit human publication only
  ↓
post-publication revalidation
```

候補が0本でも正常です。公開本数を埋めるために基準を下げません。

## Title rule

タイトルはtool名ではなく、読者が認識できる問題から入ります。

```text
一般語で分かるproblem
  → 本文で証明できる具体的な異常・失敗・数字
  → 必要なら検索用の正式技術名
```

例:

```text
弱い: Pyrefly / Ruff / Pydanticの比較
強い: 型チェックが通っても、外部入力は検証されていない
```

タイトルで約束した異常を本文で証明できなければ不採用です。

## Images and demos

画像は装飾quotaではなく、理解または証拠密度を上げる場合だけ使います。

- generated illustrationをscreenshot / measurement / historical evidenceとして扱わない
- 本文は画像がなくても成立させる
- diagramは1枚1messageを基本にする
- visual claimは元artifactへ接地する
- interactive demoは本文の代替にしない

## Quick verification

```bash
python -m compileall pipeline demos/python-syntax-gate/syntax_gate.py
python -m unittest discover -s tests -v
node --check demos/_shared/pyodide-worker.mjs
node --check demos/python-syntax-gate/app.mjs
python -m pipeline.audit
```

Candidate generation:

```bash
python -m pipeline.cli candidate
```

Human-triggered selection to an unpublished Zenn draft:

```bash
ARTICLE_MANUAL=1 python -m pipeline.cli publish
```

## Canonical documents

- Editorial contract: [`pipeline/contracts/article.md`](pipeline/contracts/article.md)
- Agent contract: [`AGENTS.md`](AGENTS.md)
- Architecture: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Current Zenn portfolio audit: [`docs/zenn-portfolio-audit-2026-08-15.md`](docs/zenn-portfolio-audit-2026-08-15.md)
- Historical audit: [`docs/article-portfolio-audit-2026-08-14.md`](docs/article-portfolio-audit-2026-08-14.md)

---

**最終成果は記事数ではありません。**

読者が、誤った成功判定・過剰な一般化・権限の与えすぎ・証拠の読み違いを避け、次の判断を一段良くできる記事だけを残します。
