---
title: "AIの独自用語を増やさない。過去の説明ではなく、毎回一次資料を見る"
emoji: "🧭"
type: "idea"
topics: ["codex", "llm", "softwareengineering", "github", "aiagent"]
published: false
---

Codexを長く使っていたら、開発の説明に見覚えのない用語が増えていた。

私は `canonical workline`、`Validation Ladder`、`Claim Provenance` を定義していない。普通のGit・test・review・CIを説明する途中で、Codexが名前を付けていた。

2026年8月16日にGitHubを検索すると、`canonical workline` は少なくとも8 repositoryの `AGENTS.md` に残っていた。  
https://github.com/search?q=org%3AKAFKA2306+%22canonical+workline%22&type=code

```text
booth_json / 2510youtuber / AdLessTwitter / AdaptiveWearGeneratorPro
yt3 / semiconductor-earnings-model / mesh_sync_2 / hitaiallconnect
```

`AGENTS.md` は保存先の一例だが、Codexでは特に影響が大きい。OpenAIのagent loop解説では、repository内の `AGENTS.md` / `AGENTS.override.md` などがuser instructionsへ組み込まれ、既定ではproject rootから作業directoryまで合計32 KiBまで収集される。  
https://openai.com/index/unrolling-the-codex-agent-loop/

つまり、そこへAI製の用語を残せば、後のCodexへ再び入力され得る。

## 普通の開発に別名が増えていた

実際の作業は、ほぼ次で説明できた。

| AIが作った表現 | 実際にしていたこと |
|---|---|
| `canonical workline` | 既存PR / branchを使う |
| `Validation Ladder` | unit test / integration test / CI |
| `fixed point` | 完了条件を満たして終える |

問題は難しい専門語ではない。**既存の言葉で足りる行為に別名を作り、その別名を次の判断材料として残すこと**である。

一度残れば、次のAIはそれを現在のルールとして受け取れる。Codexでは少なくとも `AGENTS.md` が実際にinstruction inputへ入る。  
https://openai.com/index/unrolling-the-codex-agent-loop/

## 28語の棚卸しは、一時的な現状確認だった

独自語がどこまで増えたかを見るため、28項目を一度だけ棚卸しした。恒久的な用語管理を始めるためではない。

ところが、この記事を作る途中でChatGPTが、その一時資料を `controlled vocabulary` と呼び、恒久ファイル、denylist、専用CIへ発展させようとした。

ユーザーはそれを要求していない。

**現状を見るための一時資料を、AIが勝手に維持対象へ変えようとした。**

元の造語問題と同じだった。説明を整えるために、新しい名前、新しい状態、新しい検証経路を追加していた。

用語集、denylist、terminology専用CIは削除した。現在のPR差分にもそれらは残していない。  
https://github.com/KAFKA2306/articles/pull/146

## 以前から嫌っていた問題と同じだった

2026年1月30日に公開した記事では、retry、default値、広い `try-except` によって原因の違う失敗が同じ戻り値へ丸められ、原因特定が難しくなる問題を書いていた。  
https://zenn.dev/kafka2306/articles/11cd731eebded1

同記事では、ネットワークretryをapplication logicへ埋め込まず、運用層へ分離する考えも書いている。  
https://zenn.dev/kafka2306/articles/11cd731eebded1

2026年3月27日の記事では、`AGENTS.md` やrulesを短く保つ、生成物を隔離する、不要ファイルを削除する、重複を避ける、という方針を書いていた。  
https://zenn.dev/kafka2306/articles/5c21f4d010baeb

当時の記事に書いたdirectory構成を現在も丸ごと正解としている、という意味ではない。現在も残っている判断基準は、**不要な状態・経路・文書を増やさない**ことである。

retry、fallback、広いcatch、目的の薄いtestやsmoke check、古い文書、使い終わった診断表。必要性がなければ、どれも判断候補と保守対象を増やす。

しかもこの記事を書き直す途中で、私は公開済みZennをWebで確認せず、用語管理の仕組みを追加しようとした。

**過去のローカルな会話だけを基準にした結果、すでに公開していた方針と逆の提案をした。**

## Codexの仕様と研究から確認できること

OpenAIはCodexの実運用で「1つの巨大な `AGENTS.md`」を試し、contextを圧迫する、重要な制約を見落とす、すべてが重要になって指針として機能しなくなる、古いruleが残る、と報告している。  
https://openai.com/index/harness-engineering/

OpenAI自身の解決策はstructured documentationとprogressive disclosureであり、私の「文書を増やしたくない」という運用と同一ではない。  
https://openai.com/index/harness-engineering/

ここから言えるのは、**instructionsを増やせば増やすほど良いわけではない**という点までである。

ICML 2024の *How Language Model Hallucinations Can Snowball* では、最初の誤答に続く説明で追加の誤りが生じた。  
https://proceedings.mlr.press/v235/zhang24ay.html

同論文では、その追加誤りを単独で問うとGPT-4は87%を誤りだと識別できた。初期の誤りへの整合が、本来なら避けられる後続誤りを増やし得る。  
https://proceedings.mlr.press/v235/zhang24ay.html

Findings of EMNLP 2025の *Context Length Alone Hurts LLM Performance Despite Perfect Retrieval* は、5つのopen/closed-source LLMをmath、question answering、codingで評価した。  
https://aclanthology.org/2025.findings-emnlp.1264/

同論文では、必要情報を完全に取得できていても、入力が長くなるだけで性能が13.9〜85%低下した。  
https://aclanthology.org/2025.findings-emnlp.1264/

不要部分を空白へ置換した条件、maskした条件、relevant evidenceをquestion直前へ置いた条件でも性能低下が残った。  
https://aclanthology.org/2025.findings-emnlp.1264/

これらは「文書を一つ増やすと何%悪化する」と示した研究ではない。

示しているのは、**過去の誤りが後続誤りを増やし得ること**と、**必要情報を取得できても入力長自体が性能を落とし得ること**である。  
https://proceedings.mlr.press/v235/zhang24ay.html  
https://aclanthology.org/2025.findings-emnlp.1264/

だから私は、永続的な説明を追加する側に理由を求める。

## 現在の運用

用語について、新しい辞書や専用CIは作らない。

記事や技術文書を作るたびに、その作業で重要な用語を特定し、現在の一次資料・公式資料をWeb検索する。以前検索したことがあっても省略しない。

```text
現在の一次資料を検索
→ 既存の専門語があれば、その意味で使う
→ 専門語が不要なら、具体的な行為をそのまま書く
→ AIが要求されていない名前や分類を追加しない
→ 一時的な診断物は使い終わったら残さない
```

Codex自身の仕様を説明するときはOpenAI公式資料へ戻る。  
https://openai.com/index/unrolling-the-codex-agent-loop/

自分自身の既存方針を説明するときは、公開済みの記事もWebで取り直す。  
https://zenn.dev/kafka2306/articles/11cd731eebded1  
https://zenn.dev/kafka2306/articles/5c21f4d010baeb

今回の競合解消では、現在の `main` にある `AGENTS.md` を記事PRから変更しない。記事本文だけを残し、既存のrepository運用規約を別目的の変更で上書きしない。

> **現在の事実を取り直す。既存の言葉で足りるなら増やさない。使い終わったものを残さない。**

独自用語の問題は、辞書を充実させて解決する問題ではなかった。判断材料と経路を増やし続けないことが重要だった。
