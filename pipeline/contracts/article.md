# Article Contract

## Goal

公開するのは、**広い読者が自分事にできる問題を入口に、書き手固有の実体験・実測・失敗から、読後の判断や行動を一段よくする一つの発見が残った記事だけ**とする。

このrepoは記事数、更新頻度、tool coverage、word count、SEO trafficを最適化しない。

正確さ・一次情報・監査可能性は必要条件だが、記事そのものの価値ではない。

Canonical shorthand:

```text
Broad door
  -> Original insight
  -> Concrete proof
  -> Useful exit
```

## Generic-by-default rule

このrepositoryの**記事編集・評価の規則と、記事本文の中心的な知見は原則として汎用にする**。

汎用とは「抽象的に書く」ことではない。個別のrepository、製品、framework、API、会社、環境、失敗事例は、観測・実測・再現証拠として具体的に使う。一方で、記事の中心結論はその固有名詞を外しても、同じ構造の問題を持つ別project・別tool・別環境で判断に使える形へ一般化する。

```text
specific case / measurement / failure
  -> underlying mechanism or decision structure
  -> generalizable insight
  -> transfer conditions
  -> reusable decision / action
```

### 必須条件

公開候補は次を明示する。

- `generalizable_insight`: 個別事例から得た、他のprojectでも使える中心的な知見。
- `transfer_conditions`: その知見を他へ適用してよい条件。
- `non_transfer_conditions`: その知見を一般化してはいけない条件・証拠範囲外。

次は不合格とする。

- 特定repositoryの変更履歴だけで終わる。
- 特定toolの使い方・設定値・API仕様だけが読後成果になる。
- 「このprojectではこうした」から、他の読者が自分の状況へ移す判断規則が導かれていない。
- 固有名詞を別の固有名詞へ置き換えるだけで記事の価値が消える。
- 一例しか観測していないのに、条件を書かず普遍的なbest practiceとして断定する。

**事例は証拠、一般化された知見は成果**として扱う。

ただし、証拠以上に一般化してはならない。単一事例からの一般化は `INFERRED` として扱い、適用条件・不適用条件を必ず示す。汎用性のためにclaim boundaryを広げることは禁止する。

記事が狭い専門領域を対象にすること自体は問題ではない。その領域内で、別の実装・別のrepository・別の製品にも持ち帰れる判断が残ればよい。

## 超具体性の必須条件（初稿・改稿・査読の共通ゲート）

**抽象的な教訓だけで記事を完成扱いしない。** 汎用的な結論に進む前に、少なくとも一つの観測・実装・比較を、読者が根拠を追える詳細さで示す。「品質を向上した」「調査を実施した」「検証済み」だけなら不足。装飾のための冗長化や、実行していない手順を実績として書くことも不合格。

中心となる事例では、該当する情報を本文に入れる。

1. **対象と入口**：誰が何を達成するか。対象URL・ファイルパス・画面・資料IDなどを示す。個人情報や秘密の公開は禁止。
2. **版と前提**：実施日、使用したコミット・バージョン、対象期間、環境、権限、単位など、結果を左右する条件を示す。変動する条件は確認時点を付ける。
3. **入力と行動**：何を入力し、どこを押し、どのファイルの何を変更し、何を計算したか。必要ならコマンドと引数、計算式、画面の表示名をそのまま示す。
4. **結果と比較**：入力に対して何が表示・出力され、変更前と何が違ったか。数値には母数・単位・観測範囲、失敗には実際の失敗条件を付ける。
5. **根拠と反例**：結果に対応する一次URL・コミット・PR・データの版を示し、正しい版と違う版、欠損時や未到達時など、結論が崩れる条件を一つ示す。
6. **持ち帰り方と限界**：どの条件なら再現・応用でき、どの条件ではできないか。未実施の操作や確認は `未確認` と明示し、実績に混ぜない。

実装記事はファイル・コマンド・入力・出力を、UI記事は画面名・操作順・到達先を、データ記事は資料版・期間・単位・母数・計算を、考察記事は実際の判断と比較例を中心にする。すべてを表へ埋める必要はなく、読みやすい文章と図表でよい。読者の用事に関係しない細部を増やして水増ししない。

**良くない**：「出典への導線を改善した」。**十分な方向**：「決算一覧のNVIDIA行で期末日の下の『提出書類』を押し、該当する2026年7月26日期末のSEC書類を開く。従来の2クリックが1クリックになり、対象11社のうち直接リンクを持つ会社が0社から11社になった。違う四半期の書類を指す入力では照合を失敗させた」。この例の観測と根拠は[実例の記事](../../articles/kafstyler-agent-quality-loop.md#1タップの改修で出典がずれる条件を試した)にある。計測対象と資料はそこからたどる。

査読では中心事例を一つ選び、対象・入力・操作/計算・結果・根拠・反例を記事内から指し示す。足りなければ `blocking_issues` に既存の `missing_proof_of_value` を入れ、`revision_actions` に不足する具体的情報（例：「PRの番号」「テストで与えた違う四半期の入力」「母数と期間」）を列挙する。点数が高くても差し戻す。改稿後は同じ事例と反例で再判定し、確認していない測定を実績として足さない。
## System portability rule

編集coreは、特定author、repository owner、source provider、LLM provider、publication platformに依存することを前提にしない。

- author固有のsourceは入力データとして扱う。
- GitHub、Graphiti等の取得方法はsource側の責務とする。
- Zenn等のfront matter、slug、公開操作はrenderer / publisher側の責務とする。
- 特定owner名、特定publication URL、特定providerの必須条件をarticle editorial coreへ埋め込まない。
- coreのcontractは、同じ形式の証拠と記事候補を与えれば別author・別repositoryでも適用できる状態を維持する。

既存実装にこの境界違反がある場合、互換性のために正当化せず、修正対象として扱う。

## Appeal-first design rule

記事は「説明したい技術」ではなく、読者が読みたくなる具体的な魅力から設計する。魅力は煽りや装飾ではなく、読む前と後で生じる実質的な差とする。

執筆前に次の順で一文ずつ定義する。

1. **魅力**: 読者が何を意外・面白い・切実・有益と感じるか。
2. **読者の期待**: 読む前に何を予想し、何を知りたいか。
3. **発見**: 実体験や比較によって期待がどう更新されたか。
4. **根拠**: どの公開成果物・実測・一次資料が発見を支えるか。
5. **持ち帰る価値**: 読者がどの判断や行動を変えられるか。

魅力の仮説が弱ければ、見出しや文体を磨く前に題材・観測・比較を見直す。未検証の意外性を作らず、証拠のない数字や成功談を盛らない。専門用語やツール名は読者が必要とする場所で説明する。

### 文章の推敲と反証

初稿・改稿・査読の共通手順。参照版は [Kafstyler 0.7.0の作業規約](https://github.com/KAFKA2306/kafstyler/blob/36d819f5222981c88295642a6e4534f54a7582ba/AGENTS.md#コマンドの連携)。読者の用事と見出しの設計は、[英国国家統計局の編集ガイド](https://service-manual.ons.gov.uk/content/writing-for-users/user-needs)と、[Nielsen Norman Groupの視線計測](https://www.nngroup.com/articles/layer-cake-pattern-scanning/)に基づく。

- 誰がどんな場面で読み、読後に何を判断・実行するかを決める。初稿を書く前に、合格時に観測できる結果と失敗例を一つずつ決める。困り事は利用者の相談、実際の操作、観測した失敗で確かめ、確認できない場合は想定とする。
- タイトル・冒頭・見出しだけを順に読み、初見の読者が自分の用事に関係するか、答えをどこで見つけられるかを確かめる。タイトルを変えるときは、読者の困り事と得られる結果が異なる角度から伝わる案を比べる。同じ意味には同じ語を使い、用語を直したら本文、図表、手順を照合する。
- 読み終えた人が何を見てどう判断するか、または何を実行すればよいかを本文に示す。査読では、読む理由が伝わる冒頭の一節と、判断や行動ができるようになる本文の一節を、原稿から引用して確かめる。どちらかを示せなければ差し戻す。
- 査読では、記事どおりに進めても読者の用事が済まない例を一つ考え、原稿と与えられた一次証拠に照らす。たとえば件数が同じでも対象の版が違う、コマンドが成功しても公開先に届いていない、必須の承認や前提が途中で抜けている場合を疑う。URLがあることと、その資料が主張を支えることを分けて判定する。
- 査読で中心となる操作や主張を支える証拠が本文や入力資料から確認できなければ、`blocking_issues` に `missing_proof_of_value` を入れ、確認できなかった条件と必要な資料を `revision_actions` に記す。実施した記録のない測定、操作、読者テストは実施済みと書かない。
- 改稿後は同じ入力と合格条件で確認する。査読で試した条件は `revision_actions` に残し、改稿でも使う。主張の強さ、数値、条件、出典を照合し、読者の判断や再現に必要な根拠を残して重複を削る。査読用の判定や作業記録は記事本文に入れない。
- 初稿と改稿は本文だけを返す。候補を `articles/` へ昇格するときの front matter は昇格処理が生成する。`title`、`emoji`、`type`、`topics`、`published`、`published_at` はZennでの意味と型を保つ。記事の検索分類には `topics` を使い、追加の編集メタデータは候補または作業記録に置く。公開の承認と同期は[公開手順](../../docs/PUBLICATION.md)に従う。[Zenn CLI公式ガイド](https://zenn.dev/zenn/articles/zenn-cli-guide)

## People-first editorial principles

Google Search Centralのpeople-first content自己評価から、次を採用する。

- intended audienceが直接訪れても有用か
- first-hand expertise / depth of knowledgeが見えるか
- original information / research / analysisがあるか
- 他の検索結果より実質的な価値があるか
- 読後に目的達成に十分な情報を得られるか
- titleが内容を正確かつ有用に要約しているか

Primary:

- https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- https://developers.google.com/search/docs/fundamentals/creating-helpful-content?hl=ja

Zennの現行ガイドラインから、次を採用する。

- 具体的な試行錯誤
- 書き手ならではの視点
- 実体験に基づく知見
- 読者が理解しやすい構成
- 内容に合うtitle
- 未検証AI contentの乱造を避ける

Primary:

- https://zenn.dev/guideline
- https://info.zenn.dev/2026-02-03-community-guidelines-update
- https://info.zenn.dev/2026-03-10-ai-contents-guideline

これらはSEO攻略ではなく、**読者価値の自己監査**として使う。

## Canonical article shape

```text
1. broadly recognizable problem / desire / friction
2. concrete scene / number / failure / comparison
3. natural expectation
4. first-hand experience / measurement / public artifact
5. non-obvious finding / reframing
6. underlying mechanism / decision structure
7. generalizable insight + transfer conditions
8. practical consequence
9. useful exit
10. proof limits / non-goal / non-transfer conditions
```

技術名・framework名・製品名は、読者がproblemを理解した後に必要な位置で登場させる。

## Required candidate fields

執筆前に最低限次を定義する。

### Reach

- `intended_audience`: 誰が読むと得をするか。
- `broad_entry`: 技術名を知らなくても分かるproblem / desire。
- `stakes`: time / money / risk / effort / quality / capabilityの何が効くか。

### Customer value

- `reader_job`: 読者が達成・判断したいこと。
- `reader_before`: 読む前の摩擦・損失・不確実性・false confidence。
- `customer_value`: 何が安く、速く、安全に、明確に、新しく可能になるか。
- `reader_after`: 読後に可能になる具体的な判断・行動。
- `useful_exit`: checklist / decision rule / design pattern / stop condition / adoption rule / reproducible next step。

### Originality / experience

- `original_observation`: 実測・失敗・比較・運用・実装・artifactなど書き手固有の観測。
- `initial_hypothesis`: 調査前の自然な予想。
- `surprising_finding`: 一般docs / generic AI summaryでは得にくい発見。
- `hypothesis_update`: 実際の観測で何が変わったか。
- `why_this_article`: 単独記事にする理由。

### Generalization / transfer

- `generalizable_insight`: 固有事例を越えて再利用できる知見。
- `transfer_conditions`: 同じ知見を適用できる条件。
- `non_transfer_conditions`: 適用できない条件、または追加検証が必要な範囲。

### Proof / trust

- `proof_of_value`: public evidence / measurement / implementation / primary source。
- `claim_boundary`: 証拠がsupportする結論とsupportしない結論。
- `non_goal`: 証明しないこと。
- `half_life`: volatile factと再検証trigger。

### Portfolio

- `portfolio_overlap`: 既存記事で代替できない理由。
- `durable_value`: immediate product/news momentを越えて読む理由。

既存pipeline互換のため、`central_question` / `design_philosophy` / `why_interesting` / `story_type` / `evidence_urls` も保持してよい。

## Reach gate

「間口が広い」は万人向けという意味ではない。

合格条件:

- intended audienceがtitleだけでproblemを認識できる
- niche technologyを知らなくても、なぜ読む価値があるか分かる
- niche記事でも、そのaudienceにとってjob / stakesが明確

例:

```text
弱い:
Unity MCPのEDITOR_VALIDATED境界

強い:
AIに作らせたものを、誰が「完成」と判定するのか？
```

本文は専門的でよい。**入口だけを実装詳細で閉じない。**

## Customer-value gate

`reader_after` が `理解できる` / `学べる` / `知識が増える` だけなら不合格。

最低1つ必要:

- 調査時間を減らせる
- 手戻り・failureを避けられる
- risk / uncertaintyを減らせる
- 採用・導入・委任・停止を判断できる
- 再現できる
- 新しいcapabilityを使える
- 何をしないか決められる

記事のproofが強くても、customer valueを説明できなければpublishしない。

## Originality / experience gate

最低1つ必要:

- 自分で使った結果
- 自分で作ったartifact
- 自分で測った数字
- 自分で遭遇したfailure
- 自分で比較した条件
- 自分で長期運用して見えた変化
- 一次情報で当初前提を撤回した記録

公式docsの要約、二次情報の編集、AI要約だけでは通さない。

`why_this_article` は「分かりやすく説明する」では不合格。

## Generalization gate

記事本文は、固有事例から最低1段一般化する。

合格条件:

- `generalizable_insight` が特定repo名・tool名なしでも意味を持つ。
- その知見が成立する理由を、観測からmechanism / decision structureとして説明できる。
- `transfer_conditions` を満たす別projectで、読者が同じ判断規則を試せる。
- `non_transfer_conditions` により、証拠以上の一般化を止めている。
- useful exitが特定のCLI commandや設定値だけでなく、少なくとも一つの再利用可能なdecision rule / comparison lens / experiment protocolを含む。

一つでも満たさなければ、`case_specific_without_transfer` としてblockingする。

## Question / discovery gate

次の最低1つが必要。

- 読者の自然な予想と観測結果がずれた
- 一次情報によって当初前提を撤回した
- 実測値に意味のある差がある
- 簡単だと思った場所とは別の場所が難所だった
- successに見えた結果に別のfailureが残った
- 一見無関係な事象が実測可能な構造でつながった
- failureからreaderの行動が変わる知見を得た
- product / toolの使い方より「何のために使うか」が変わった

弱い問いを長文・図・引用・文体で救済しない。

## Useful-exit gate

記事の最後に最低1つ、読者が自分の仕事へ持ち帰れるものを作る。

- decision rule
- checklist
- design principle
- experiment protocol
- adoption / rejection rule
- stop condition
- reproducible minimal procedure
- comparison lens
- mental model

読者がその場で一度試せるように、使う場面、手元に用意するもの、最初に行う操作や判断、結果の見方を本文からたどれるようにする。実装記事では入力例と期待する出力、調査や論考では開く資料と照合順、保留にする条件を具体化する。既存の例や手順に組み込み、詳しい説明や根拠は必要な箇所から参照できるようにする。 [Agent Skillsの本文ガイド](https://agentskills.io/specification#body-content)

CTAはuseful exitではない。

## Evidence / trust gate

Evidence is quality infrastructure, not the product.

material claimごとに次を確認する。

```text
What does this prove?
What does it NOT prove?
Why does the reader need this proof?
```

必須原則:

1. changeable external claimはcurrent primary / official sourceで確認する。
2. vendor仕様はvendor公式、標準はstandards bodyを優先する。
3. author固有の成果はpublic commit / PR / Issue / Actions / artifact等の公開証拠で確認する。
4. historical stateが重要ならfixed commit/runを使う。
5. 数字にはtarget / period / unit / scope / comparison basisを付ける。
6. observation / inference / speculationを分離する。
7. inaccessible / contradictory / stale sourceならclaimを弱めるか削除する。
8. NOT_RUN / unknown / pendingをPASS / 0 / completeへ昇格しない。
9. citation countは品質の目的関数にしない。
10. 個別事例から一般化した部分は、その推論とtransfer条件を明示する。

`authority / verification boundary` は読者価値を生む場合だけ本文の中心に置く。

## Portfolio novelty / overlap

新規記事より `MERGE` を優先する条件:

- 同じreader job
- 同じuseful exit
- 新しいproofが既存記事の補強にすぎない
- tool名だけ違う
- 新記事のReach / customer value / originalityが既存記事以下

**記事数を増やすより、1本の価値密度を上げる。**

## Title contract

最低3案を作る。

1. `broad_problem`
2. `concrete_result`
3. `searchable`

原則:

```text
human problem / desire
  -> concrete proofable result / failure / anomaly
  -> technical search term when useful
```

タイトルは内容を正確に表す。誇張clickbaitは禁止。

冒頭500文字を目安に、

- 誰のproblemか
- 何が起きたか
- なぜ続きを読む価値があるか

が分かること。

タイトルで固有tool名を完全禁止はしない。ただし、そのtoolを知らない読者にも問題と持ち帰れる価値が分かること。

## Story contract

説明順より発見順を優先する。

```text
friction / desire
  -> scene
  -> expectation
  -> experiment / experience
  -> contradiction / discovery
  -> updated model
  -> generalizable insight
  -> transfer conditions
  -> useful exit
```

結論を隠して人工的なsuspenseを作らない。一方、冒頭で全部説明して発見を消さない。

## Technical quality floor

LAPRAS AI Reviewで公開されている5軸を参考にした内部proxyを使用する。LAPRAS上の実測値ではない。

- `logic`
- `utility`
- `readability`
- `originality`
- `clarity`

`overall` は5軸の算術平均。

現行minimum/targetは `pipeline/config.json` を正準とする。

このscoreは品質床であり、公開価値の目的関数ではない。

## Editorial blocking issues

最低限次をblockingとして扱う。

- `unclear_intended_audience`
- `narrow_technical_title_entry`
- `weak_customer_value`
- `weak_reader_value`
- `commodity_information`
- `weak_first_hand_experience`
- `weak_differentiation`
- `missing_proof_of_value`
- `missing_useful_exit`
- `case_specific_without_transfer`
- `unclear_transfer_conditions`
- `overgeneralized_from_narrow_evidence`
- `forced_commercial_cta`
- `technical_value_as_product`
- `premature_conclusion_in_opening`
- `uncalibrated_claim`
- `portfolio_redundancy`

既存実装が全codeを機械判定しなくても、人間/agent auditではblockingとして扱う。

## What we do not publish

- official docs summary
- install/setup only
- link collection
- tool/service directory
- generic best-practice article
- product roundup without reader decision
- unsupported "best stack" ranking
- repository changelog
- secondary-source AI report
- framework without first-hand implementation/measurement
- article whose intended audience is unclear
- technology-first title hiding the actual problem
- `Aを使ってBを作った` with no customer value
- case study that ends at `AでBが起きた` without a transferable insight
- tool-specific procedure with no reusable decision rule
- unsupported generalization from one repository, one environment, or one experiment
- obvious conclusion
- unsupported numeric guidance
- duplicate reader job with weaker proof

## Images

画像はreader comprehension / comparison / proofを改善する場合だけ使う。

- generated illustrationをscreenshot / measurement / historical evidenceとして扱わない
- articleは画像なしでも成立
- visual claimは元artifactへ接地
- decoration quotaは禁止

## Publication boundary

```text
schedule
  -> candidate discovery / research / drafting / review only

manual pipeline selection
  -> articles/へ published:false でmaterialize

explicit human approval
  -> published:true
```

schedule、月末、score、CI green、mergeはpublication authorizationではない。

## Lifecycle after publication

- `KEEP`: Reach / customer value / originality / experience / utility / trust / transferabilityが強い
- `REVALIDATE`: insightは強いがvolatile factあり
- `REWRITE`: core experienceは価値があるが入口・価値・構成・一般化が弱い
- `MERGE`: same reader jobをより強い記事へ集約
- `RETIRE`: 読む理由・独自性・信頼・durable value・transferabilityが不足

`RETIRE` / `REWRITE` trigger:

- intended audienceが不明
- titleがimplementation-first
- commodity information化した
- first-hand proofが薄い
- useful exitがない
- case-specificで他projectへ持ち帰れる知見がない
- transfer条件が不明
- central claimがstale / unverifiable
- newer articleに上位互換された
- title/body promise mismatch
- unsupported numberが中心
- maintenance cost > durable reader value
- portfolio signalを薄める

## Publication portfolio review cadence

公開記事を定期再監査する。

1. public URL
2. Reach
3. customer value
4. originality / first-hand experience
5. generalizable insight / transfer conditions
6. useful exit
7. source / trust
8. overlap
9. half-life
10. lifecycle state

公開記事数を増やすより、弱い記事をretireしてportfolio valueを上げる。

## Final publication test

公開承認前に一文ずつ答える。

```text
Intended audience:
Broad entry:
Reader job:
Reader before:
Customer value:
Original observation:
Natural expectation:
Surprising finding:
Generalizable insight:
Transfer conditions:
Non-transfer conditions:
Strongest proof:
Useful exit:
What the proof does NOT establish:
Why this deserves a separate article:
Half-life / revalidation trigger:
```

一つでも曖昧なら `published:false` を維持する。
