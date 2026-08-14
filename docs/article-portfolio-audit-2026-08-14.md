# Article Portfolio Audit — 2026-08-14

## Purpose

`articles/` を「技術的にやったことの履歴」ではなく、**何を解決できるか・どこまで実証済みか・なぜ任せる価値があるかを公開証拠で判断できるportfolio**として棚卸しする。

この監査は Issue #69 の正準成果物である。

観測基準:

- current `main`: `72ef152b232c559e57001a2bb30e5d950aa09415`
- `articles/.gitkeep` は記事数に含めない
- current article count: **25**
- この刷新で統合・退役した旧稿: **6**
- tracked total: **31 article records**
- current `articles/*.md` は全件 `published: false`

重要: **今回の刷新はpublish promotionではない。** `KEEP_PRIVATE` は品質が低いという意味ではなく、公開可否を別のpromotion gateとして残す判断である。

## Audit axes

各記事を次の7軸で見る。

1. `reader_problem` — 誰の何の摩擦・損失・不確実性を減らすか
2. `value` — 読後に何を判断・実行できるか
3. `proof` — 実測・実装・失敗・比較・一次情報の何が固有証拠か
4. `differentiation` — 一般tutorial / docs / AI要約では代替しにくい何があるか
5. `commercial_pull` — 読者が試す・導入する・相談する合理的な次actionがあるか
6. `story` — scene / 数字 / 失敗 / 仮説反転から入れているか
7. `overlap` — 他記事へ統合すべき重複が残っていないか

Lifecycle decision:

- `KEEP`
- `REWRITE`
- `MERGE`
- `KEEP_PRIVATE`
- `DELETE / ARCHIVE`

## Current portfolio — 25 articles

| article | target reader / reader problem | value after reading | proof of value | differentiation | commercial pull | story quality | overlap | decision |
|---|---|---|---|---|---|---|---|---|
| `2026-08-13-01-accessibility-contract.md` | UIを頻繁に改修するWeb開発者。見た目刷新でa11y要件だけ消える | 消えたら困る利用体験を安価なCI contractへ変えられる | `finBI` HTML/CSS/workflow、reduced-motion / live-region checks | a11y一般論ではなく「改修で消える要件を運用契約にする」 | 自分のUIで最低限のa11y contractを追加できる | UI刷新後の退行sceneから入る | なし | `KEEP_PRIVATE` |
| `2026-08-13-02-how-people-compress-a-person.md` | 活動domainが散らばり「AIを使う人」以上の能力が伝わりにくい | 何を任せると価値が出る人か判断できる | books / investor2 / Codex bridge / VRCPet の4公開成果 | 自己分析ではなく異domainで再現する同一problem-solving loop | 曖昧な問題を検証可能な仕組みへする相談候補として判断できる | 外部ラベル→公開成果4件→共通能力 | なし | `KEEP_PRIVATE` |
| `2026-08-13-03-dont-infer-domain-from-language.md` | taxonomy UIでunknownを推測分類してしまう | `unclassified` を第一級stateとして運用できる | `agent-resources` collector/tests/PR #60 | 分類精度より「分からないを嘘で埋めない」UX | 根拠のないfallbackを監査できる | PythonだからAI、という誘惑から入る | なし | `KEEP_PRIVATE` |
| `2026-08-13-04-effect-size-is-not-a-conclusion.md` | 大きいeffect sizeを予測・因果へ過大昇格しやすい分析者 | metric / evidence strength / allowed useを分離できる | `detective` pilot、各年12件、Cohen's d≈-0.760、禁止用途artifact | 統計解説ではなく解釈権限をdata contractへ実装 | 自分の分析artifactへallowed-use gateを追加できる | `d≈0.76` を見て使いたくなるscene | compatibility記事とは用途が異なる | `KEEP_PRIVATE` |
| `2026-08-13-04-legacy-limit-complete-archive.md` | legacy limitで一覧の61件目以降が静かに消える | API互換を保ちながらcomplete product semanticsへ移行できる | `vlog` PR #54/#55、pagination/count/boundary tests | pagination tutorialではなく「互換性がUXを古仕様へ縛る」問題 | 既存default/limitを監査できる | 61件目だけ消えるscene | なし | `KEEP_PRIVATE` |
| `2026-08-13-05-pin-assets-commit-sha256.md` | 中央asset更新でconsumer siteが無変更のまま変わる | central managementとconsumer stabilityを両立できる | `prompt-vault`→`travel` commit/hash/vendor/deploy read-back | permalink解説ではなく採用versionをreview可能にする運用 | 共有assetをcommit+hash lockへ移行できる | 同じURLなのにbytesが変わるscene | なし | `KEEP_PRIVATE` |
| `2026-08-13-06-python-one-source-browser.md` | Python testとbrowser JSで業務計算がdriftする | testとUIで同じcanonical calculationを使える | `finBI` Python module/worker/tests、具体9bp fixture | Pyodide紹介ではなく「正解を1か所にする」UX | frontend再実装をshared canonical pathへ寄せられる | 同じ画面で答えが違うscene | old single-source稿は統合済み | `KEEP_PRIVATE` |
| `2026-08-14-01-audit-generated-image-claims.md` | 生成図内のCI/数値/URLを視覚的説得力で信じる | artifact gateとevidence gateを分離できる | `articles` image policy/audit、CI SUCCESS等のfailure examples | image generation how-toではなく「信じてよい図」を作る | 既存生成図をclaim単位で監査できる | 「CI SUCCESSがpixelだった」scene | old one-diagram稿は統合済み | `KEEP_PRIVATE` |
| `2026-08-14-02-publish-destination-guard.md` | 自動投稿が全部greenのまま別destinationへ成功し得る | run intent / profile / remote identityをpublish直前に照合できる | `yt3` registry/PublishAgent/hardening commit、ADR drift | YouTube API tutorialではなく「間違った場所へ成功しない」routing safety | multi-channel publishの宛先確認を機械へ委任できる | ADR `daily_pulse` vs `byosan_money` drift | old three-point稿は統合済み | `KEEP_PRIVATE` |
| `2026-08-14-03-manifest-drift-gate.md` | CIがstale manifestを自分で再生成してからgreenにする | generatable / internally valid / committed freshを分離できる | semiconductor model builder/verifier/workflow + git diff gate | manifest formatではなく「CIが更新忘れを隠す」逆説 | generated artifact repoへdrift gateを導入できる | stale commitがCI内で直るscene | なし | `KEEP_PRIVATE` |
| `2026-08-14-04-controlled-vocabulary-promotion-gate.md` | 用語を即canonical化してalias・identityが分裂する | wide discoveryとstrict promotionを両立できる | `nlm` 294件、verified 32→33、needs_review 262→261、MeSH | glossary作成法ではなくcanonical identityのstate transition | AI収集を広くしつつ正規語品質を守れる | 294候補から1語だけ昇格 | なし | `KEEP_PRIVATE` |
| `2026-08-14-05-compatibility-is-not-validation.md` | OSSが動くと「判断に使える」まで意味を広げやすい | installed / runnable / validated / allowed_useを分離できる | 日本語60件pilot + import failure case + usage prohibition | OSS導入手順ではなく成功体験による過大解釈を止める | 外部model/SDK評価表へallowed-useを入れられる | 動いたのに使えない2ケース比較 | old validity稿は統合済み | `KEEP_PRIVATE` |
| `2026-08-14-06-top-n-boundary-evidence.md` | Top-Nだけでは「なぜこの候補がないか」を説明できない | candidate countとfirst excludedで境界を説明できる | semiconductor model: 51候補/50採用/QDレーザE35542 | Top-N tutorialではなくランキング自身へ説明責任を持たせる | 検索/推薦/rankingへboundary evidenceを追加できる | 51位が消える具体case | なし | `KEEP_PRIVATE` |
| `claude-watermark-secret-key-detection.md` | vendor未公開仕様と一般watermark原理を混同しやすい | embedding / secret / detection / verification interfaceを分離できる | 2026-08-14 current Anthropic Transparency Hub + SynthID | Claude内部を推測せず「何が公開確認できるか」からarchitectureを考える | provenance設計のdecision modelとして使える | Claude前提を一次情報で撤回する仮説更新 | なし | `KEEP_PRIVATE` |
| `codex-chatgpt-github-issue-bridge.md` | AIへPC作業を任せたいが権限・停止条件・結果が怖い | 最小権限で監査可能な委任境界を設計できる | public bridge、AllowedRoot/read-only/workspace-write、E2E evidence | queue tutorialではなく「安全に何を任せられるか」 | low-risk taskからAI委任を始められる | queue以外のOAuth/HEAD/sandbox failure | なし | `KEEP_PRIVATE` |
| `csv-migration-dry-run-before-write.md` | CSVをDBへ書くまで各行が何になるか分からない | mutation前に予定action/reasonを確認できる | `books` Work/Edition/Holding、shared diagnose core、browser-local CSV、non-mutation test | importer tutorialではなくpreview-before-write UX | 既存importerへdiagnose/no-writeを追加できる | 曖昧な蔵書4行から開始 | なし | `KEEP_PRIVATE` |
| `muchio-shiroinu-body-adapter.md` | 公式既存機能を知らず不要な独自差し替えを作りそうになる | 一次情報確認で作るべき責務を絞れる | BOOTHの「オリジナルペットの作り方」等 | 実装成功談ではなく「作る必要がある前提が消えた」判断変更 | 無駄なVRChat実装を始める前の調査patternとして使える | 公式説明1行で仮説反転 | Prefab/runtime proof不足 | `KEEP_PRIVATE` |
| `opencode-go-deepseek-v4-chatgpt-usage-scale.md` | 大きなrequest推定値を固定quotaのように読む | 同期間actual usageでsubscription capacityを判断できる | 2026-08-14 OpenCode official usage-value limits / typical request estimates | 料金表転載ではなく自分のworkloadとのcapacity planning | usage/task・retry/taskでmodel routingを評価できる | 「15万回=ほぼ無限？」を否定 | volatile numbers | `KEEP_PRIVATE` |
| `primary-source-derived-data-provenance.md` | KPIが856→7,699へ変わると以前の分析まで信用しにくい | source/scope/methodで変更理由を説明できる | `investor2` 17 OGE docs、5,026+2,673=7,699、derived cross-check | provenance一般論ではなく9倍近い数値反転の実例 | KPI schemaへsource/scope/methodを追加できる | 856→7,699の反転 | なし | `KEEP_PRIVATE` |
| `stage-specific-quality-gates.md` | WARNまで止めるとagent/生成loopが詰まる | scoreとblocking severityを工程別に使い分けられる | `yt3` ScriptIntegrityLinter / generation policy / publish policy | lint解説ではなく同じsignalを工程別decisionへ変換 | 安全性とthroughputの両立policyを導入できる | WARNで全部止めると詰まるscene | なし | `KEEP_PRIVATE` |
| `unity-mcp-editor-boundary.md` | MCP tool successをUnity成果物完成と誤認しやすい | TOOL_SUCCESS / EDITOR_VALIDATED / RUNTIME_COMPLETEDを分離できる | `image2outfit` Draft PR #212、live MCP/runtime NOT_RUN boundary | Unity MCP setupではなくcompletion contract | AIへUnity作業を任せる範囲を判断できる | tool success≠VR runtime | runtime evidence未完 | `KEEP_PRIVATE` |
| `validate-before-pages-deploy.md` | deploy環境未準備でcode qualityまで失敗/skip扱いになる | artifact validityとdeployment availabilityを分離できる | `finBI` compile/tests/build/HTTP smoke/clean checkout/deploy job | Pages tutorialではなく「今証明できる品質を止めない」 | CI/CDをfailed/validated/skipped/deployedへ分けられる | Pages未設定なのにcodeまで赤くなるscene | clean-checkout稿統合済み | `KEEP_PRIVATE` |
| `video-storyboard-ir-provider-compile.md` | provider仕様変更でcreative intentまで書き直しやすい | Storyboard IRを正準にしadapterだけ更新できる | Kling PR #1 merged、MiniMax PR #56 merged、2026-08-14 current MiniMax modes | API比較ではなくprovider driftのblast radiusをadapterへ閉じる | video generation基盤をprovider-portableに設計できる | 旧MiniMax前提が現行docsとずれた実例 | current MiniMax adapter revalidation/live未完 | `KEEP_PRIVATE` |
| `vrcpet-observation-source.md` | AI memoryが観測logを本人の事実へ過剰昇格する | Observation / parse issue / MemoryClaimを分離できる | `vlog` PR #28、valid=2 / issue=1 fixture、E2E | JSONL parserではなく「AIが覚えすぎない」provenance/privacy UX | personal memory/meeting botにもpromotion contractを転用できる | 壊れた3行fixture | なし | `KEEP_PRIVATE` |
| `why-i-could-buy-the-crash.md` | 成功後に当時の判断理由を後知恵で書き換えやすい | 判断をversioningし反証条件と後日結果をdiffできる | 3買付日、pre-event Git history、public primary sources | AI投資記事ではなく人間の意思決定を検証可能にする | 投資/研究/障害/企画のDecision Logへ転用できる | 「最初から分かっていた」を防ぐ3日 | privacy/financial advice boundary | `KEEP_PRIVATE` |

## Retired / merged — 6 articles

| retired article | decision | canonical target / reason |
|---|---|---|
| `one-diagram-one-message-image-pipeline.md` | `MERGE` | `2026-08-14-01-audit-generated-image-claims.md` へ `CI SUCCESS` scene・claim監査・有用な図解を吸収。画像枚数KPIを廃止 |
| `publish-destination-three-point-guard.md` | `MERGE` | `2026-08-14-02-publish-destination-guard.md` へADR driftとbefore/after hardening proofを吸収 |
| `compatibility-vs-validity-gate.md` | `MERGE` | `2026-08-14-05-compatibility-is-not-validation.md` へ日本語60件pilotを吸収 |
| `single-source-python-browser-calculation.md` | `MERGE` | `2026-08-13-06-python-one-source-browser.md` へ具体test fixtureとbrowser drift sceneを吸収 |
| `clean-checkout-final-state-gate.md` | `MERGE` | `validate-before-pages-deploy.md` へfinal-state assertionとして吸収 |
| `fail-close-data-pipeline.md` | `DELETE / ARCHIVE` | 固有のpublic incident evidence不足。一般則のみ `artifacts/archive/fail-close-data-pipeline-notes.md` に保存 |

## Portfolio-level conclusions

### 1. 技術名を価値そのものにしない

現在の強い記事は、次のような読者の状態変化で説明できる。

- 「AIを使った」→ **どこまで安全に委任できるか分かる**
- 「CIを追加した」→ **greenが何を証明したか分かる**
- 「paginationした」→ **61件目が欠けていないと説明できる**
- 「Provenanceを入れた」→ **数字が変わっても信頼を維持できる**
- 「Pyodideを使った」→ **テストとUIの正解を1つにできる**

### 2. Commercial pullはCTA文ではなく、再利用可能な能力から作る

読後actionは「お問い合わせください」を足すことではない。

- 自分のworkflowへcontractを1つ入れる
- 自分のdata modelへprovenance fieldを追加する
- 自分のagentへ最小権限boundaryを置く
- 自分の判断をDecision Logへ固定する

という、本文の価値から自然に出るactionを優先する。

### 3. 記事数をKPIにしない

同じreader jobを扱う5組は統合した。固有proofのないfail-close稿はarchiveへ落とした。

**弱い2本より、proofが集約された1本を残す。**

### 4. `published: false` は失敗ではない

今回の刷新では公開を自動昇格させていない。

特に次は明確なpublish blockerを持つ。

- Muchio: Prefab / Editor / runtime evidence不足
- Unity MCP: live MCP / runtime completion未実証
- Storyboard IR: current MiniMax adapter revalidation / live generation未実証
- OpenCode: usage limits / model listがvolatile
- watermark: vendor-specific implementation statusがvolatile
- personal profile / investment: privacy・portfolio positioningを別途判断

## Implementation evidence from this refresh

Merged waves:

- PR #103 — first 3 proof-backed rewrites
- PR #104 — five duplicate themes consolidated
- PR #105 — trust-boundary article rewrites
- PR #106 — controlled vocabulary rewrite
- PR #107 — capability profile + fail-close archive
- PR #108 — volatile articles re-grounded in current primary sources

Each merged wave passed Article Pipeline CI including compile, contract tests, JavaScript syntax, static route smoke, repository/privacy audit, and clean-checkout verification before merge.

## Done criteria for Issue #69

- current 25 articles are all present in this inventory
- all 7 audit axes are represented per article
- every active article has a lifecycle decision
- all retired articles have canonical merge/archive destinations
- weak proof was not repaired with marketing copy
- overlapping reader jobs were consolidated
- current portfolio communicates a consistent capability: **曖昧な状態を、検証可能で安心して使える運用状態へ変える**
