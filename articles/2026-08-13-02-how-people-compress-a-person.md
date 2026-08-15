---
title: "『AIを使い倒す人』では、何も伝わらない。成果物を「何を任せられるか」に翻訳する"
emoji: "🪞"
type: "idea"
topics: ["ai", "learning", "career", "communication"]
published: false
published_at: 2026-08-13 18:11
---

GitHubにリポジトリがたくさんある。

PythonもTypeScriptも使う。AI agentも作る。データ分析も自動化もする。

それでも、初めて見る人には意外なほど何も伝わらない。

知りたいのは技術一覧ではなく、たぶんこちらだからだ。

> **この人に、どんな問題を渡すと、どんな状態まで持っていってくれるのか。**

以前の私は、この問いに答えるために自分の公開成果を並べた。

しかし、並べ方を間違えていた。

`Work / Edition / Holding`、`AllowedRoot`、`MemoryClaim`、856件、7,699件。

作った本人には具体的でも、初見の読者には内部事情である。

GoogleのTechnical Writing教材は、よい説明を「読者がタスクを行うために必要な知識 − 読者がすでに持つ知識」と整理し、専門家が初心者の知らない前提を忘れる *curse of knowledge* に注意を促している。

https://developers.google.com/tech-writing/one/audience

そこで、成果物から始めるのをやめた。

**誰でも分かる問題から始め、その問題をどう変えたかの証拠として成果物を置く。**

すると、自分が何を作っている人なのかも、以前よりずっと説明しやすくなった。

## 1. データを入れてから壊れたと気づくのは遅い

たとえば、1,000行のCSVを新しいシステムへ移すとする。

実行後に、

- 既存データと重複していた
- 同じ行が入力ファイル内に複数あった
- IDやISBNの形式が壊れていた
- 新規登録してよい行と、人が確認すべき行が混ざっていた

と分かっても遅い。

欲しいのは「高速に書き込めるimporter」だけではない。

**書き込む前に、何が起きるか分かること**である。

自分の本棚DBでも同じ問題があった。

そこで最初に作ったのは、正準データを書き換えない `dry-run` だった。

公開テストでは、診断後にもcatalogが変化していないことを確認しながら、少なくとも次を別々の理由コードとして返している。

```text
existing_holding     すでに所蔵している
safe_new_work        新規登録候補
invalid_isbn         ISBNが不正
duplicate_in_batch   入力内で重複
```

証拠:

- test: https://github.com/KAFKA2306/books/blob/main/tests/migration-diagnosis.test.mjs
- implementation: https://github.com/KAFKA2306/books/blob/main/src/migration-diagnosis.mjs

ここで重要なのは「本棚を作った」ことではない。

**破壊的な処理を、実行前に判断できる処理へ変えた**ことである。

この型は本棚以外にも使える。

顧客マスタ移行、商品DB更新、ファイル一括rename、生成AIによる大量編集。

書き込み処理が強力になるほど、先に「何が起きるか」を見せる価値も上がる。

## 2. 同じ数字が856と7,699なら、どちらを信じるのか

次はもっと日常的な問題だ。

昨日の分析では856件だった。

今日取り直すと7,699件になった。

このとき利用者が知りたいのは、新しい数字の方が大きいことではない。

**なぜ変わったのか。どちらを、何の目的で使ってよいのか。**

実際に `investor2` の公開データ分析で、この変化が起きた。

調べると、856と7,699は同じ母集団を数えた値ではなかった。

現在のsnapshotでは、7,699を政府機関が公表した単一の公式合計とは扱っていない。17件のOGE Form 278-T文書を対象にした外部parser cross-check由来の派生集計として、

```text
purchases: 5,026
sales:     2,673
total:     7,699
status:    derived_external_parser_crosscheck
```

と保存している。

さらに、以前の856は `previous_partial_count_856_superseded: true` として、狭いscopeだったことを履歴に残した。

証拠:

- snapshot: https://github.com/KAFKA2306/investor2/blob/main/docs/research/data/us_oge_trump_278t_trade_count_2026-08-11.json
- analysis note: https://github.com/KAFKA2306/articles/blob/main/articles/primary-source-derived-data-provenance.md

W3CのPROV仕様群も、provenanceを「データや物を生み出すのに関わったentity、activity、peopleについての情報」とし、品質・信頼性・trustworthinessを評価するために使えるものとしている。

https://www.w3.org/TR/prov-overview/

つまり、ここで作った価値は「7,699という数字」ではない。

```text
値
+ 出所
+ 対象範囲
+ 計算方法
+ 状態
+ 過去値との差分
```

を一緒に残し、**数字が変わったときにも判断を続けられる状態**にしたことである。

この型も投資だけの話ではない。

売上KPI、Webアクセス数、実験結果、製造歩留まり、AI評価スコア。

数字が意思決定に使われるなら、「値」より「なぜその値なのか」が後から追える方が長く使える。

## 3. AIに仕事を任せたい。でもPCを好き勝手触らせたくない

AI agentの話も、技術名から入ると分かりにくい。

問題はもっと単純である。

> **AIに仕事は任せたい。でも、必要以上の権限は渡したくない。**

これはAI特有の考え方でもない。

NISTはleast privilegeを、ユーザーやその代理で動くprocessの権限を、割り当てられた仕事に必要な最小限へ制限するsecurity principleと定義している。

https://csrc.nist.gov/glossary/term/least_privilege

自分が公開しているChatGPT ↔ Codex CLI bridgeでも、同じ考え方を機械的な境界にした。

現在のREADMEで確認できる境界は次の通りである。

```text
通常          read-only
書き込み時    workspace-write を明示
danger-full-access  拒否
作業directory AllowedRoot 配下だけ
queue          private repository 必須
命令元         設定したGitHub loginだけ
local MCP      deny-by-default + 明示opt-in
```

証拠:

- implementation README: https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/README.md
- verification: https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/VERIFICATION.md

ここで価値があるのは「AIがPCを操作できた」ことではない。

**どこまでなら任せてよいかを、人間の注意力ではなく実行条件へ変えたこと**である。

「気をつけて使う」は毎回判断が必要になる。

境界をコードにすると、次の仕事でも同じ判断を再利用できる。

## 3つとも、作ったものではなく「変えた状態」で見ると同じだった

本棚DB、公開データ分析、AI agent。

製品名だけ見ると別物である。

しかし、読者が理解できる問題へ翻訳すると、共通点が見える。

| 最初の状態 | 放置したときの困りごと | 変えた状態 | 残した証拠 |
|---|---|---|---|
| CSVを入れたい | 書き込んでから重複・不正に気づく | 書く前に結果を診断できる | dry-run test / reason code |
| 数字が変わった | どちらを信じるか説明できない | scope・出所・方法まで追える | snapshot / source URL / status |
| AIへ任せたい | 必要以上の権限まで渡る | 任せられる範囲を固定する | AllowedRoot / sandbox / allowlist |

自分が繰り返していたのは、特定の技術ではなかった。

```text
よく分からない要求
  ↓
失敗したら何が困るかを決める
  ↓
正しい状態と境界を決める
  ↓
機械的に判定できるようにする
  ↓
実装する
  ↓
後から確かめられる証拠を残す
```

**曖昧な問題を、他人が判断でき、機械が繰り返せる状態へ変える。**

これが、少なくとも今の公開成果から説明できる共通項だった。

## 成果物を見るとき、技術名より5つを聞く

これは自己紹介だけの話ではない。

自分のGitHub、ポートフォリオ、職務経歴書を見るときにも使える。

1. **誰にでも分かる元の問題は何だったか**
2. **失敗すると何が困ったのか**
3. **どんな境界・判定条件を置いたのか**
4. **本当にそう動くと何で確認できるのか**
5. **次に同じ問題が来たとき、何を考え直さなくてよくなったか**

「Reactを使った」「AI agentを作った」「100 repositoriesある」だけでは、この5つには答えられない。

逆に、小さな成果物でも、

> 入力としてこの問題を渡すと、こういう失敗を防ぎながら、ここまで持っていく。

と説明できれば、依頼側はかなり判断しやすくなる。

## 「何でもできます」ではなく、変換を見せる

以前は、domainの多さをどう一つのプロフィールにまとめるかを考えていた。

今は、無理にdomainをまとめなくてよいと思っている。

重要なのは、毎回何を**変換**しているかである。

```text
書いてみないと分からない
→ 書く前に分かる

数字はあるが意味が分からない
→ どこから来た数字か説明できる

AIに任せたいが怖い
→ 任せてよい範囲が機械的に決まっている
```

この方が「AIを使い倒す人」より、依頼する側にとって使いやすい説明になる。

AIは速度を上げる。

GitHubは証拠を残す。

PythonやTypeScriptは実装手段になる。

しかし商品になるのは、それらの名前ではない。

> **人が毎回迷っていた問題を、次からは迷わず扱える状態にすること。**

成果物を並べるなら、数ではなく、この変換が見えるように並べたい。

## 根拠

- Google Technical Writing, Audience: https://developers.google.com/tech-writing/one/audience
- W3C PROV Overview: https://www.w3.org/TR/prov-overview/
- NIST CSRC, Least Privilege: https://csrc.nist.gov/glossary/term/least_privilege
- books migration diagnosis test: https://github.com/KAFKA2306/books/blob/main/tests/migration-diagnosis.test.mjs
- investor2 provenance snapshot: https://github.com/KAFKA2306/investor2/blob/main/docs/research/data/us_oge_trump_278t_trade_count_2026-08-11.json
- ChatGPT ↔ Codex CLI Bridge: https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/README.md
