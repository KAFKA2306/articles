---
title: "なぜあなたのコードは、AIに改善させるほど直しにくくなるのか"
emoji: "🧹"
type: "tech"
topics: ["ai", "codex", "github", "refactoring", "documentation"]
published: false
---

GitHubのrepositoryをChatGPTやCodexに渡して、こんな依頼を繰り返す。

```text
CIを直して
READMEを分かりやすくして
品質チェックを追加して
失敗時に自動復旧できるようにして
次のAIでも作業を再開できるようにして
```

AIはコードだけを書くわけではない。

依頼をこなすために、`AGENTS.md`、docs、prompt、test、audit script、fallback、status file、workflowなども追加する。

一つずつを見ると、どれも合理的に見える。

しかし追加を繰り返すと、別の問題が起きる。

```text
同じルールが3つの文書に書かれている
同じ確認を2つのworkflowが実行している
古いpromptと新しいpromptが両方残っている
fallbackが本当のエラーを隠している
同じ状態を複数のJSONへ保存している
```

こうなると、次に作業する人やAIはコードを直す前に、

**「どれが今も必要で、どれを信じればいいのか」**

を調べなければならない。

この記事で扱うのは、この問題である。

**AIが追加したコードだけでなく、AIが追加した“仕事を進めるための仕組み”まで整理しないと、repositoryは徐々に変更しにくくなる。**

## 何を問題にしているのか

対象は、変わった名前や長い文書そのものではない。

たとえば次の二つは意味が違う。

```text
A. CSVのcolumn名、型、単位、変換規則を定義した仕様書
B. AIが作業するときの独自role、score、level、protocolを定義した文書
```

Aは製品やデータの意味を決めるために必要かもしれない。

Bも必要な場合はあるが、testやCIやGitHubの標準機能で同じ目的を達成できるなら、別の仕組みを増やす必要はない。

判断基準は単純である。

> **これを消したら、利用者が受け取る機能、正しさ、必要な証拠のどれが失われるのか？**

何も失われないなら、削除候補になる。

## なぜ `AGENTS.md` まで見るのか

Codexでは `AGENTS.md` は単なるメモではない。

OpenAI公式ドキュメントによると、Codexは作業開始前に `AGENTS.md` を読み、project rootからcurrent working directoryまでのinstructionを連結する。project instructionの合計サイズは `project_doc_max_bytes` で制限され、既定値は32 KiBである。

- https://developers.openai.com/codex/agent-configuration/agents-md
- https://openai.com/index/unrolling-the-codex-agent-loop/

つまり `AGENTS.md` にruleを追加すると、次のCodex runが読むinstructionそのものが増える。

OpenAIは同じ公式ドキュメントで、code review ruleは簡潔に保ち、formattingやlintはCIへ任せるよう案内している。

GoogleのCode Review Guideも、現在必要な問題以上に一般化したり、将来必要かもしれない機能を先回りして増やすover-engineeringを避けるよう求めている。

- https://google.github.io/eng-practices/review/reviewer/looking-for.html

AI向けのrule、test、fallback、workflowも例外ではない。

## repository全体で見る7項目

確認する対象は次の7つで足りる。

1. **AIが読む文書**  
   `AGENTS.md`、README、CLAUDE/GEMINI、ADR、prompt、memory、docsに同じ指示が重複していないか。

2. **独自の分類**  
   role、state、level、score、rule、protocolなどを、製品上の必要性なしに増やしていないか。

3. **同じ確認の重複**  
   test、audit、smoke、harness、verifierが同じ事実を何度も確認していないか。

4. **失敗を隠す仕組み**  
   fallback、retry、broad catch、compatibility modeが、本来直すべき原因を見えなくしていないか。

5. **同じ状態の重複保存**  
   config、manifest、ledger、status、provenanceに同じ事実を何度も持っていないか。

6. **使われなくなった残骸**  
   古いprompt、migration、旧workflow、古いmemory、superseded scriptが残っていないか。

7. **削除しても結果が変わらないもの**  
   消しても機能・正しさ・証拠が変わらないなら、本当に必要かを再確認する。

目的はファイル数を減らすことではない。

**同じ成果を、より少ない仕組みで作れる状態にすること**である。

## 例1：`semiconductor-earnings-model`

`semiconductor-earnings-model` の `AGENTS.md` には `BFV Kernel` というrepository-level operating policyがある。

中には `Contract`、`Canonical Workline Rule`、`Claim`、`Deletion Test`、`Builder / Auditor Separation`、`Fixed Point`、`Final Report Contract` などが定義されている。

- https://github.com/KAFKA2306/semiconductor-earnings-model/blob/main/AGENTS.md

ここで問題なのは `BFV` という名前ではない。

金融データでは、source、period、unit、provenanceの検証は必要である。

しかし、それを守るために独自の作業方法まで常時AIへ読ませる必要があるかは別問題だ。

たとえば既存のschema、test、CI、PR reviewだけで同じ正しさを守れるruleなら、`AGENTS.md` に別の方法論として残す必要は薄い。

## 例2：`yt3`

`yt3` には、AIの作業方法や品質改善に関係するファイルが複数の場所にある。

- `AGENTS.md`
- `GEMINI.md`
- `.claude/CLAUDE.md`
- `.claude/agents/`
- `.claude/skills/`
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

一つの品質条件が、READMEで説明され、AGENTSで命令になり、promptで再記述され、skillで手順化され、audit codeでも判定されているなら、すべてを残す理由が必要になる。

一つ消しても出力も正しさも変わらないなら、そのファイルは次の作業者にとって情報ではなく確認項目になる。

## 例3：長い文書でも必要なものはある

`trahist` の `docs/DATA_STANDARDS.md` は長い。

しかし中身は、`trades_unified.csv` のcolumn、型、必須性、brokerごとの変換、数値・日付処理、fund unit normalizationなど、実際のデータ処理を決める仕様である。

- https://github.com/KAFKA2306/trahist/blob/main/docs/DATA_STANDARDS.md

これは「文書が長いから消す」という対象ではない。

`trade_date` や `currency` の意味を消せば、同じ入力から同じ結果を作れなくなる。

見るべきなのは文書量ではなく、**その情報が製品やデータの意味を決めているか**である。

## 削除の成果をどう測るか

「何ファイル消したか」だけでは不十分である。

見るべきなのは、たとえば次の変化だ。

- 同じruleを書く場所が3か所から1か所になった
- 同じvalidationを実行する経路が2本から1本になった
- fallbackを消して元のエラーが直接見えるようになった
- 同じstateの保存先が2つから1つになった
- 古いpromptやworkflowを削除した
- 削除後もtestとuser-facingな結果が変わらない

これなら、削除量ではなく**変更時に確認しなければならない対象が減ったか**を見られる。

## 結論

AIはコードを書く速度だけでなく、文書、test、workflow、fallback、分類、監査手順を増やす速度も上げる。

そのため、AIを使って継続的にrepositoryを改善するなら、追加されたコードだけを見るのでは足りない。

**AIが仕事を進めるために追加した仕組みも、定期的に削除対象として見る必要がある。**

基準は一つでよい。

> **これを消したら、利用者が受け取る機能、正しさ、必要な証拠のどれが失われるのか？**

何も失われないなら、残す理由を説明できるか確認する。
