---
title: "AIが書いたrepositoryを読みにくくする独自用語と略語を減らす"
emoji: "🧹"
type: "tech"
topics: ["ai", "codex", "github", "nlp", "documentation"]
published: true
published_at: 2026-08-16 12:24
---

AIにREADME、Issue、`AGENTS.md`、設計文書を書かせると、文章はすぐ増やせる。

しかし最近、自分のrepositoryを読み返していて、ファイル数や文章量より先に引っかかるものがあった。

**そのrepositoryでしか通じない用語と略語である。**

実際に現在の `KAFKA2306/semiconductor-earnings-model` の `AGENTS.md` を開くと、冒頭から次の名前が並ぶ。

```text
BFV Kernel
Bounded Falsification & Verification
Contract
Canonical Workline Rule
Deletion Test
Builder / Auditor Separation
Fixed Point
Final Report Contract
```

- https://github.com/KAFKA2306/semiconductor-earnings-model/blob/main/AGENTS.md

個々のルールには妥当な内容も多い。金融データなら、一次情報、期間、単位、出所、再現性、テストは必要である。

問題は、それらを守るために**新しい概念名まで覚える必要があるか**である。

たとえば「作業範囲をIssueに限定する」「必要なテストを実行する」「完了したら止める」で十分なら、`BFV Kernel` や `Fixed Point` という別の名前を覚えなくても同じ行動は説明できる。

さらに `BFV` のような独自略語を作ると、読む側は略語を展開し、その定義を探し、他の文書でも同じ意味か確認しなければならない。

この記事では、AIが作ったコード量ではなく、**読むために別途覚えなければならない独自用語と独自略語を減らす**ことに絞る。

## 一般的な専門用語と、repository固有の名前は分ける

専門用語を全部なくしたいわけではない。

たとえば、

```text
Git
pull request
CI
JSON Schema
SQL
regression test
operating margin
```

は、それぞれ既存の技術、標準、業界で意味が共有されている。

一方、

```text
BFV Kernel
Canonical Workline Rule
Final Report Contract
```

は、少なくともその名前自体はrepository側で定義しないと読者に意味が伝わらない。

GoogleのDeveloper Documentation Style Guideも、特定集団だけに通じるjargonは明確なコミュニケーションを妨げることがあり、可能なら平易な表現へ置き換えるよう勧めている。

- https://developers.google.com/style/jargon

略語についても、対象読者に馴染みの薄いものや過度に専門化されたものを避けるよう案内している。

- https://developers.google.com/style/abbreviations

したがって、判断したいのは「専門用語かどうか」ではない。

**外部でも意味が共有されている語か、それともこのrepositoryを読むためだけに追加で覚える名前か**である。

## 略語は独自用語より厳しく見る

独自用語を一度説明すれば、その後は文脈から意味を推測できることがある。

独自略語はさらに情報を落とす。

```text
Bounded Falsification & Verification
             ↓
            BFV
```

`BFV` だけを別のIssueやPull Requestで見ても、意味は推測しにくい。

repositoryは一冊の本のように最初から最後まで読むものではない。READMEだけ読む人もいれば、Issueから入る人もいる。AIも必要なファイルだけを読む場合がある。

そのため、

```text
最初に正式名称を書いた
    ↓
以後は独自略語でよい
```

という運用でも、別文書では再び辞書が必要になる。

自分のrepositoryでは、次の方針が読みやすい。

```text
API / HTTP / JSON / CI
→ 対象読者に広く定着しているなら使う

repository内で新しく作った略語
→ 略さなくても困らないなら作らない
```

略語を禁止するのではなく、**略語によって節約できる文字数より、意味を復元する負担が大きくないか**を見る。

## LLMの語彙選択そのものは測定できる

ここで「AIは独自用語を作りたがる」と決めつける必要はない。

Large Language Model（LLM）の語彙選択が人間と異なることは、別の形で研究されている。

JuzekとWardはCOLING 2025で、科学論文における `delve`、`intricate`、`underscore` などの増加を調べ、LLM利用による増加である可能性が高い21語を抽出した。一方で、なぜそれらが過剰に選ばれるのかについて、モデル構造、アルゴリズム、学習データを原因とする証拠は得られなかったと報告している。

- https://aclanthology.org/2025.coling-main.426/

さらにJuzek、Ming、Hernandezの2026年研究は、手作業の「AIっぽい語リスト」を前提にせず、人間の文章と6つのモデルファミリーの生成文を比較した。

そこで使われているのが、単純な総出現回数ではなく、一定の窓の中にその語が現れたかを見る **windowed document prevalence** である。

- https://arxiv.org/abs/2606.03165

一つの文書で同じ語を何十回も繰り返したケースと、多数の文書に同じ語が広がっているケースを分けて考えられる。

これはrepositoryを見るときにも参考になる。

ただし、この研究は「AIがsoftware repositoryで独自の概念名を作る」「それが別文書へ自己増殖する」「独自略語が読解時間を何%増やす」と証明した研究ではない。

**語彙選択の差を測れることと、repository固有語彙の原因を説明することは分ける。**

2026年8月のRudnickaとJuzekのpreprintも、複数LLMにモデルごとの異なるlinguistic profileがある可能性を論じているが、これもrepository内の独自用語生成を直接調べた研究ではない。

- https://arxiv.org/abs/2608.06589

## 単語だけでなく、複数語の表現を抜く

自分のrepositoryで気になったのは、`delve` のような単語一個より、次のような複数語の名前だった。

```text
Canonical Workline Rule
Final Report Contract
Builder / Auditor Separation
```

この候補抽出にはAutomatic Term Extractionの研究が参考になる。

ChunらのACL 2025論文は、専門用語抽出で意味的に近い例だけでなく、**構文的に近い例を使う方法**を検証し、3つの専門分野benchmarkでF1-scoreを改善したと報告している。

- https://aclanthology.org/2025.findings-acl.516/

したがって、最初から「怪しいAI語の一覧」を作るより、文章から名詞句や複数語の用語候補を構文的に抜く方がよい。

例えば候補として、

```text
ADJ + NOUN
NOUN + NOUN
X-ready
X-driven
level + noun
名詞化された表現
```

を見る。

ここで重要なのは、**この形をした語を禁止することではない**。

`access control` や `regression test` のような普通の技術用語も同じ構造を持つ。

構文解析は判定ではなく、見落とさず候補を集めるために使う。

## repositoryでは「何回出たか」より「何文書に出たか」を見る

候補を抜いたら、次に各表現がどこに出ているかを見る。

```text
README.md
AGENTS.md
Issue
Pull Request
設計文書
prompt
その他のdocs
```

一つの文書に10回ある表現と、10個の文書に1回ずつある表現では意味が違う。

後者は、そのrepositoryを横断して使われる語彙になっている。

そこで最低限、各用語について次を記録する。

```text
出現回数
出現した文書数
最初に確認できる出現
現在も使われている文書
```

独自略語なら、正式名称と略語の両方を数える。

ここでも新しいスコア名は作らない。件数をそのまま見る。

## 外部で通じるか確認する

repository内で繰り返されているからといって、独自用語とは限らない。

次に、外部で意味が定着しているかを確認する。

優先するのは、

1. 標準仕様
2. APIやframeworkの公式documentation
3. upstream project
4. 公的な用語集
5. 分野のcorpusや主要文献

である。

たとえば `JSON Schema` なら公式仕様へ接続できる。`CI` ならGitHub Actionsを含む一般的なsoftware engineeringの文脈で広く使われる。

一方、`BFV Kernel` は現在のrepository自身が `BFV means Bounded Falsification & Verification` と定義している。

- https://github.com/KAFKA2306/semiconductor-earnings-model/blob/main/AGENTS.md

つまり読む人は、このrepository固有の定義を取得しなければならない。

この時点で削除と決める必要はない。

次の質問へ進む。

> **その名前を普通の語または既存の標準用語へ置き換えると、どの意味の区別が失われるか？**

具体的な区別が失われないなら、置き換え候補になる。

## 用語集を作る前に、用語を減らす

独自用語が増えると、「なら用語集を作ろう」という発想になりやすい。

しかし、用語集を作ると意味を調べられるようになるだけで、覚える語の数は減らない。

例えば、

```text
Evidence Completion Gate (ECG)
```

という名前を作り、用語集へ

```text
ECG = 必要な証拠がそろったか確認する段階
```

と書くことはできる。

でも本文を最初から

```text
必要な証拠がそろったか確認する
```

と書けば、用語集も略語も不要である。

用語集が必要なのは、外部標準の専門用語、データモデル上区別が必要な概念、公開APIの名称など、**普通の文章へ置き換えると意味が失われるもの**である。

独自語を大量に作ってから辞書で救済するより、辞書を必要とする語を減らす方を先にする。

## `AGENTS.md` は特に影響が大きい

Codexでは `AGENTS.md` の内容が作業時のinstructionsに入る。

OpenAIが2026年1月に公開したCodex agent loopの説明では、Git/project rootからcurrent working directoryまでの `AGENTS.md` などが、既定32 KiBの上限のもとでuser instructionsへ集約されることが説明されている。

- https://openai.com/index/unrolling-the-codex-agent-loop/

つまり `AGENTS.md` の独自語は、人間が読むdocumentationに残るだけではない。Codex自身が次の作業で読むinstructionsにもなる。

だから、ここへ

```text
新しいrole
新しいlevel
新しいgate
新しいworkflow名
独自略語
```

を追加する前に、本当に名前が必要かを見る。

自分なら、まず次のような普通の指示へ戻す。

```text
既存のIssueを確認してから作業する。
標準的な技術用語を使う。
独自の略語を作らない。
同じ情報を複数の文書へ書かない。
必要以上のコード・設定・依存関係を追加しない。
完了前にテストまたは実際の出力で確認する。
```

これなら、別の概念体系を理解してから作業を始める必要がない。

## 実際の監査は5段階で十分だった

現在考えている監査手順は次の通りである。

```text
1. README / AGENTS.md / docs / Issues から
   名詞句・複数語の用語候補と大文字略語を抽出する

2. ADJ+NOUN / NOUN+NOUN / X-ready など
   語の作り方を記録する

3. 標準仕様・公式documentation・外部corpusで
   同じ表現が定着しているか確認する

4. repository内で何文書に反復しているか数える

5. 既存の一般語・標準用語へ置き換えても
   意味の区別が失われないものを置き換える
```

略語は別に、

```text
repository内で新しく定義された大文字略語
```

を抽出し、原則として正式名称か普通の説明へ戻す。

この方法なら、「AIっぽい」という印象だけで語を消さない。

外で通じるか、repository内でどれだけ反復しているか、置換すると意味が失われるか、という観測可能な情報で判断できる。

## まだ分かっていないこと

ここまでで確認できているのは、

- 自分の公開repositoryに独自の複合語と略語が実在すること
- Googleの技術文書ガイドが、不要なjargonや馴染みの薄い略語を避けるよう案内していること
- LLMの語彙選択差をprevalenceで測る研究が存在すること
- 構文情報を使ったAutomatic Term Extractionの研究が存在すること

である。

一方、まだ実測していないこともある。

- AIを多用したrepositoryは、人間中心のrepositoryより独自用語が多いか
- 独自用語が何個増えると読解時間がどれだけ増えるか
- 一度生成された用語が、AIによって別文書へ伝播する頻度
- 独自略語を削除したとき、人間やAIの作業時間がどれだけ変わるか

ここは結論を先に置かず、比較できるcorpusを作って測る必要がある。

## 結論

AIを使ったrepositoryの読みにくさを考えるとき、最初に見るべきなのはファイル数でも文書量でもなかった。

**読む前に覚えなければならない、repository固有の用語と略語だった。**

標準的な専門用語は使う。

必要な概念の区別も残す。

しかし、普通の「検証」「完了条件」「作業手順」で伝わるものに新しい名前を付けない。

さらに、その新しい名前を頭文字で略さない。

監査するときは、複数語の用語候補と略語を抽出し、外部での使用とrepository内の文書数を確認する。

最後に一つだけ聞く。

> **この名前を普通の言葉へ戻すと、何の意味が失われるのか？**

何も失われないなら、その名前を覚える必要もない。
