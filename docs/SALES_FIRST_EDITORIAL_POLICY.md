# Sales-first editorial policy

Updated: 2026-08-14

## Purpose

`KAFKA2306/articles` は技術変更履歴を公開するためのリポジトリではない。

公開記事は、読者が本文と公開証拠から次を判断できる **evidence-backed portfolio** として扱う。

- 何の問題を解決できるのか
- 導入前と導入後で何が変わるのか
- 実際にどこまで動いているのか
- 一般的な解説や公式docsだけでは得られない何があるのか
- 自分で再現する／使う／相談する価値があるのか

技術、ライブラリ、API、CI、MCP、LLMは価値そのものではなく、その価値を実現する手段である。

## Zennとの境界

Sales-first は広告文を書くことを意味しない。

Zennの現行ガイドラインは、一般知識の再掲より具体的な体験・試行錯誤・書き手固有の視点を推奨し、製品や採用の宣伝を主目的にする投稿は避けるよう求めている。AIを使った記事でも、人が主体となって正確性を確認し、経験・洞察を含めることが求められている。

一次情報:

- https://zenn.dev/guideline
- https://info.zenn.dev/2026-02-03-community-guidelines-update
- https://info.zenn.dev/2026-03-10-ai-contents-guideline

したがって、このrepoでの営業効果は **宣伝文句ではなく、成果・能力・証拠・制約を見せることで自然に生む**。

## Article value contract

候補を執筆・公開へ進める前に、最低限次を説明できなければならない。

### 1. Reader problem

誰が、何に困っているか。

NG:

- GitHub Actionsを追加した
- MCPを導入した
- schemaを変更した

OKの方向:

- 100を超える独立projectを、人が毎回「次は何をするか」選ばなくても進めたい
- 自動投稿が正常終了したのに、別channelへ誤配信される事故を止めたい
- 同じ業務計算をPythonとJavaScriptへ二重実装して答えがずれるのを防ぎたい

### 2. Reader before → after

読む前と読んだ後で、読者の判断・行動・運用がどう変わるかを書く。

`理解できる`、`学べる` だけでは弱い。できるだけ、運用上の行動へ落とす。

### 3. Proof of value

最低1つ、書き手固有の公開証拠を持つ。

優先順:

1. production / deployed result
2. 実運用規模・実測値
3. merged PR / commit / test / Actions run
4. 実際の失敗と修正
5. decision log / timestamped snapshot

公式docsだけで成立する記事は原則として公開候補にしない。

### 4. Differentiation

次の問いへ答える。

> 公式docs、一般tutorial、AI要約ではなく、なぜこの記事を読むのか。

実測、失敗、比較、制約、判断変更、複数systemをまたいだ実運用のどれかを差分にする。

### 5. Commercial pull

CTAを増やすのではなく、本文を読んだ結果として次が自然に伝わる状態を目指す。

- この仕組みを自分の仕事にも使えそう
- この人／systemへ任せると何が減るか分かる
- 実運用できる範囲を証拠から判断できる
- 自分で一から作るより相談・依頼する合理性がある

Zenn本文でpromotionを入れる場合も、本文の主目的にせず末尾の小さな導線に留める。

### 6. Non-goal / boundary

できないこと、未検証なこと、推測に留まることを残す。

Sales-firstを理由に断定を強めない。

## Lifecycle decision

すべての記事を公開する必要はない。各記事は以下のどれかに分類する。

- `KEEP`: 現状でもportfolioとして強い
- `REWRITE`: 固有証拠は強いが、実装説明が前に出ている
- `MERGE`: 単独では薄い／重複している。より強い1本へ統合する
- `KEEP_PRIVATE`: 技術メモとして価値はあるが、公開portfolioには弱い
- `DELETE / ARCHIVE`: 固有価値、証拠、将来の再利用価値が乏しい

## Fail-close publish gate

次のどれかに該当する候補は `published: true` にしない。

- 実装更新の説明が中心で、reader problemが弱い
- 公式docsの要約だけで代替できる
- 書き手固有のproofがない
- 既存記事と同じ価値を別タイトルで繰り返している
- 未検証の機能を実運用済みのように読める
- 読後のbefore → afterを説明できない
- CTAを削ると営業価値まで消える

## Portfolio benchmarks

### Investment retrospective

`articles/why-i-could-buy-the-crash.md`

良い点は、LLMやGitの紹介から始めず、**結果を知った後に過去の判断を書き換えてしまう問題を、後から反証可能にする**という価値を中心に置いていること。売買日・価格、commit、一次情報をproofとして使い、技術を手段に下げている。

### Multi-project autonomy

`artifacts/candidates/2026-08/2026-08-13-chatgpt-multiproject-autonomy.md`

良い点は、AI agentという技術名ではなく、**123個のnon-fork個人projectを横断し、「次に何をするか」「何をもって完了か」まで制御loopへ移した**という運用能力を中心に置いていること。Issue / PR / merge規模と複数repositoryのproduction evidenceを示している。

この2本の文体をコピーするのではなく、`problem → capability → evidence → boundary → reusable value` の構造をbenchmarkにする。

## Review question

公開前の最終質問は次とする。

> 技術名とrepository名を隠しても、この記事から「何を解決できる人／仕組みなのか」「本当に動いている証拠は何か」「自分が使いたい理由は何か」が伝わるか。

Noなら公開せず、REWRITE / MERGE / KEEP_PRIVATE / DELETEへ戻す。
