---
title: "AIにコードを書かせたら、次のAIが迷う。repo監査を「造語探し」からやり直した"
emoji: "🧹"
type: "tech"
topics: ["ai", "codex", "github", "refactoring", "documentation"]
published: false
---

最初の監査方法は間違っていた。

`canonical workline` のような独自語を一つ見つけ、その周辺に似た語がないか探していた。見つかった問題自体は実在したが、探索方法が「最初に見つけた症状」に引っ張られていた。

つまり、**サンプリングバイアスがあった。**

本当に知りたかったのは、独自用語が何個あるかではない。

> このrepositoryに存在する各ファイル・rule・test・workflow・fallback・stateは、利用者が欲しい成果を作るために本当に必要か？

2026年8月16日から、監査対象をここへ変えた。

## なぜ「文書が多いだけ」では済まないのか

Codexでは、repository内の `AGENTS.md` は単なる人間向けメモではない。

OpenAIの公式説明では、`AGENTS.md` / `AGENTS.override.md` などのproject instructionsは、Git rootから現在ディレクトリまで探索され、**user instructionsとしてpromptへ集約される**。project docsの上限は既定で32 KiBである。

- https://openai.com/index/unrolling-the-codex-agent-loop/
- https://developers.openai.com/codex/agent-configuration/agents-md

つまり、AI向け文書・規則・例外をrepositoryへ残すことには実行時の意味がある。

README、AGENTS、CLAUDE、GEMINI、ADR、prompt、skill、memoryへ同じ思想をコピーすれば、単なる「整理不足」ではない。次のAIが読む規則が増え、どれを優先するか判断する仕事も増える。

GoogleのCode Review Guideも、レビュー対象を名前の珍しさではなくcomplexityとして扱っている。特にover-engineeringについて、現在必要な問題ではなく将来必要かもしれない問題を先回りして一般化しないよう明示している。

- https://google.github.io/eng-practices/review/reviewer/looking-for.html
- https://google.github.io/eng-practices/review/reviewer/standard.html

## 監査対象を7つへ広げた

今後は語彙検索から始めない。repository全体を見て、次を確認する。

1. **永続context** — `AGENTS.md`、README、CLAUDE/GEMINI、ADR、prompts、memories、docsへ同じ判断規則が重複していないか。
2. **独自の概念体系** — framework、role、state、level、score、rule、protocolなど、製品要件ではない分類が増えていないか。
3. **検証経路** — test / audit / smoke / harness / verifier / receiptが同じ事実を重複確認していないか。
4. **回復経路** — fallback / retry / broad catch / alternate path / compatibility modeが失敗原因を隠していないか。
5. **状態の重複** — config、manifest、ledger、status、provenance、生成物が同じ事実を複数箇所で所有していないか。
6. **残骸** — 一時調査、migration、旧prompt、旧workflow、古いmemory、superseded scriptが次の実装者やAIから見える場所に残っていないか。
7. **削除可能性** — 消しても利用者価値・正しさ・必要な証拠が変わらないなら、残す理由を再確認する。

最後の一点が重要だ。

ファイル数、テスト数、監査数を減らすこと自体が目的ではない。**削除したとき何が壊れるかを説明できるか**を見る。

## `semiconductor-earnings-model`：造語ではなく方法論が実装へ入っていた

`semiconductor-earnings-model` の `AGENTS.md` は、現在 `BFV Kernel` をrepository-level operating policyとして定義している。

`BFV` は `Bounded Falsification & Verification` の略で、文書内には `Contract`、`Canonical Workline Rule`、`Claim`、`Deletion Test`、`Builder / Auditor Separation`、`Fixed Point`、`Final Report Contract` まで並ぶ。

- https://github.com/KAFKA2306/semiconductor-earnings-model/blob/main/AGENTS.md

ここで問題にしたいのは `BFV` という名前が珍しいことではない。

金融データのprovenance、period、unit、source validationは実装上必要である。一方、それを守るための**仕事の進め方そのもの**まで独自の方法論として永続contextへ載せると、次のAIは金融データだけでなく、その方法論も理解してから変更する必要がある。

監査すべきなのは名前ではなく、各ruleが既存のtest、schema、CI、GitHub reviewだけでは表現できない必要条件を持っているかどうかだ。

## `yt3`：一つの改善思想が複数surfaceへ分裂している

`yt3` はさらに分かりやすい。

2026年8月16日時点のmain treeには、少なくとも次が同時に存在する。

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

これを「独自用語検索」だけで監査すると、かなりの部分を見落とす。

問題は語ではなく、**同じ目的を説明・判定・検証するsurfaceが増殖している可能性**だからだ。

たとえば一つの品質条件が、READMEで説明され、AGENTSで命令になり、ADRで設計判断になり、promptで再記述され、skillで手順化され、audit codeで機械判定される。この6つが全部必要なら残せばよい。しかし一つ消しても出力も正しさも検証可能性も変わらないなら、次のAIにとっては選択肢ではなく判断コストになる。

## 長い文書を消せばよいわけではない

逆の例もある。

`trahist` の `docs/DATA_STANDARDS.md` は、`trades_unified.csv` のcolumn、型、必須性、brokerごとの変換、数値・日付処理、fund unit normalizationなど、データ処理の具体的な契約を記述している。

- https://github.com/KAFKA2306/trahist/blob/main/docs/DATA_STANDARDS.md

これは長いから残骸、という話ではない。

`trade_date`、`transaction_type`、`currency`、broker固有変換のような情報は、実際の入力を同じ意味へ正規化するためのdomain contractである。

区別したいのは、**製品・データ・外部interfaceの意味を決める情報**と、**AIが自分の仕事の進め方を説明するために増えた情報**だ。

前者は長くても必要になり得る。後者は短くても、複数surfaceへ複製されれば負債になる。

## 監査で数えるものも変える

以前は「独自語を何個消したか」を成果にしやすかった。

今後はそれだけでは足りない。

見るべき変化は、たとえば次である。

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

だからレビュー対象もコード行数だけでは足りない。

次のAIがrepositoryを開いたとき、理解しなければならないもの全体を見る必要がある。

最初に見つけた28語は無駄ではなかった。ただし、それは全体像ではなく症状だった。

これからの問いは一つにする。

> **これを消したら、利用者が受け取る価値、正しさ、必要な証拠のどれが失われるのか？**

答えがないものから削除候補にする。
