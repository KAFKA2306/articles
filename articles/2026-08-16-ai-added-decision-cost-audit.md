---
title: "AIにrepo改善を任せ続けたら、AIが作った「仕事の仕組み」が負債になった"
emoji: "🧹"
type: "tech"
topics: ["ai", "codex", "github", "refactoring", "documentation"]
published: false
---

**複数のrepository改善をAIに繰り返し任せると、AIはコードだけでなく「AIが仕事を進めるための仕組み」まで追加する。**

たとえば、

```text
AGENTS.md
README / docs
prompt / skill / memory
独自のrole / state / score / protocol
audit / verifier / harness
fallback / retry
manifest / ledger / status
workflow
```

である。

一つずつは改善のために追加されたものでも、次のAIから見れば、**読んで、意味を比較し、どれを信じるか判断し、変更時に壊していないか確認する対象**になる。

```text
AIに改善を任せる
↓
コードだけでなく「仕事の仕方」も増える
↓
次のAIがそれを解釈する
↓
1変更あたりの判断経路が増える
```

この問題を監査する単位は「独自用語」ではない。

> **このrepositoryに存在する各file / rule / test / workflow / fallback / stateは、利用者が欲しい成果を作るために本当に必要か？**

これをrepository全体に対して問う。

## 独自用語検索だけでは不十分

`canonical workline` のような独自語は、AIが独自の概念体系を増やしている兆候にはなる。

しかし、語彙検索では次のような問題を拾えない。

- 同じvalidationを2本のworkflowで実行している
- 古いpromptと新しいpromptが両方残っている
- fallback moduleが本来の失敗原因を隠している
- 同じstateをmanifestとledgerの両方へ保存している
- AI向けinstructionがREADME、AGENTS、CLAUDE、GEMINIへ複製されている

問題は名前ではなく、**同じ成果を作るための判断経路が何本あるか**である。

## なぜAI向け文書は「置いてあるだけ」ではないのか

少なくともCodexの `AGENTS.md` は、単なる人間向けメモではない。

OpenAI公式ドキュメントでは、Codexは作業開始前に `AGENTS.md` を読み、project rootからcurrent working directoryまでinstruction chainを組み立てる。該当するproject instructionsはroot側から順に連結され、合計サイズは `project_doc_max_bytes`、既定32 KiBまで取り込まれる。

- https://developers.openai.com/codex/agent-configuration/agents-md
- https://openai.com/index/unrolling-the-codex-agent-loop/

OpenAIは同じ公式ページで、code review ruleは簡潔に保ち、formattingやlintのような検査はCIへ任せるよう案内している。

つまり `AGENTS.md` にruleを足すことは、documentationを1ファイル増やすだけではない。**次のCodex runへ投入されるinstructionを増やす変更**でもある。

README、CLAUDE、GEMINI、ADR、prompt、skill、memoryはCodexがすべて自動で同じ方法で読むわけではない。しかしrepository内でそれらを探索・参照する運用なら、同じ考えを複数surfaceへ残すほど「どれが現在の正準か」を判断する仕事は増える。

GoogleのCode Review Guideも、レビューで見るべきものとしてcomplexityを挙げ、現在必要な問題以上に一般化したり、将来必要かもしれない機能を先回りして追加するover-engineeringを避けるよう明示している。またtestも保守対象のcodeであり、testだからcomplexityを許容してよいわけではないとしている。

- https://google.github.io/eng-practices/review/reviewer/looking-for.html

監査対象は、名前の珍しさではない。

**成果を作るための経路そのものが、必要以上に増えていないか**である。

## 監査する7つの対象

repository全体を見て、次を確認する。

1. **永続context** — `AGENTS.md`、README、CLAUDE/GEMINI、ADR、prompts、memories、docsへ同じ判断規則が重複していないか。
2. **独自の概念体系** — framework、role、state、level、score、rule、protocolなど、製品要件ではない分類が増えていないか。
3. **検証経路** — test / audit / smoke / harness / verifier / receiptが同じ事実を重複確認していないか。
4. **回復経路** — fallback / retry / broad catch / alternate path / compatibility modeが失敗原因を隠していないか。
5. **状態の重複** — config、manifest、ledger、status、provenance、生成物が同じ事実を複数箇所で所有していないか。
6. **残骸** — 一時調査、migration、旧prompt、旧workflow、古いmemory、superseded scriptが次の実装者やAIから見える場所に残っていないか。
7. **削除可能性** — 消しても利用者価値・正しさ・必要な証拠が変わらないなら、残す理由を再確認する。

ファイル数、テスト数、監査数を減らすこと自体が目的ではない。

**削除したとき何が壊れるかを説明できるか**を見る。

## `semiconductor-earnings-model`：造語ではなく方法論が実装へ入っている

`semiconductor-earnings-model` の `AGENTS.md` は、`BFV Kernel` をrepository-level operating policyとして定義している。

`BFV` は `Bounded Falsification & Verification` の略で、文書内には `Contract`、`Canonical Workline Rule`、`Claim`、`Deletion Test`、`Builder / Auditor Separation`、`Fixed Point`、`Final Report Contract` まで並ぶ。

- https://github.com/KAFKA2306/semiconductor-earnings-model/blob/main/AGENTS.md

問題は `BFV` という名前が珍しいことではない。

金融データのprovenance、period、unit、source validationは実装上必要である。一方、それを守るための**仕事の進め方そのもの**まで独自の方法論として永続contextへ載せると、次のAIは金融データだけでなく、その方法論も理解してから変更する必要がある。

監査すべきなのは、各ruleが既存のtest、schema、CI、GitHub reviewだけでは表現できない必要条件を持っているかどうかだ。

## `yt3`：一つの改善思想が複数surfaceへ分裂している

`yt3` のmain treeには、少なくとも次が同時に存在する。

- `AGENTS.md`
- `GEMINI.md`
- `.claude/CLAUDE.md`
- `.claude/agents/` 以下の複数agent instruction
- `.claude/skills/` 以下の複数skill
- `docs/standard/continuous-improvement-loop.md`
- `prompts/continuous_improvement_loop.txt`
- `prompts/agy_100x_viewer_loop_audit.md`
- `prompts/improvement_round_2.txt`
- `src/domain/agents/meta_audit_layer.ts`
- 複数の `audit_*.ts`

Repository tree:

- https://api.github.com/repos/KAFKA2306/yt3/git/trees/main?recursive=1

個別例:

- https://github.com/KAFKA2306/yt3/blob/main/docs/standard/continuous-improvement-loop.md
- https://github.com/KAFKA2306/yt3/blob/main/prompts/continuous_improvement_loop.txt
- https://github.com/KAFKA2306/yt3/blob/main/prompts/agy_100x_viewer_loop_audit.md
- https://github.com/KAFKA2306/yt3/blob/main/prompts/improvement_round_2.txt
- https://github.com/KAFKA2306/yt3/blob/main/src/domain/agents/meta_audit_layer.ts

独自用語検索だけでは、この構造のかなりの部分を見落とす。

問題は語ではなく、**同じ目的を説明・判定・検証するsurfaceが増殖している可能性**だからだ。

たとえば一つの品質条件が、READMEで説明され、AGENTSで命令になり、ADRで設計判断になり、promptで再記述され、skillで手順化され、audit codeで機械判定される。この6つが全部必要なら残せばよい。しかし一つ消しても出力も正しさも検証可能性も変わらないなら、次のAIにとっては選択肢ではなく判断コストになる。

## 長い文書が問題なのではない

`trahist` の `docs/DATA_STANDARDS.md` は、`trades_unified.csv` のcolumn、型、必須性、brokerごとの変換、数値・日付処理、fund unit normalizationなど、データ処理の具体的な契約を記述している。

- https://github.com/KAFKA2306/trahist/blob/main/docs/DATA_STANDARDS.md

`trade_date`、`transaction_type`、`currency`、broker固有変換のような情報は、実際の入力を同じ意味へ正規化するためのdomain contractである。

区別すべきなのは、**製品・データ・外部interfaceの意味を決める情報**と、**AIが自分の仕事の進め方を説明するために増えた情報**だ。

前者は長くても必要になり得る。後者は短くても、複数surfaceへ複製されれば負債になる。

## 監査で数えるもの

成果は「独自語を何個消したか」では測れない。

見るべき変化は次である。

- 同じruleを所有するファイル数が減ったか
- 同じ事実を確認するvalidation routeが減ったか
- fallbackを外して失敗原因が直接見えるようになったか
- 同じstateを複数保存する箇所が減ったか
- supersededなprompt / workflow / memory / scriptが減ったか
- 削除後もuser-facing outcomeと必要なtestが同じか

重要なのは削除量ではない。

**同じ成果を、より少ない判断経路で作れるようになったか。**

## 結論：AI時代の残骸は「コード」だけではない

AIはコードだけでなく、説明、分類、役割、検証、例外、fallback、state、監査手順まで高速に追加できる。

それらは追加時には改善に見えるが、蓄積すると次のAIが理解しなければならない対象そのものが増える。

だから監査対象もコード行数や独自語だけでは足りない。

**AIが追加した「仕事の仕方」まで含めて、repository全体の判断経路を監査する。**

問いは一つでよい。

> **これを消したら、利用者が受け取る価値、正しさ、必要な証拠のどれが失われるのか？**

答えがないものは削除候補である。
