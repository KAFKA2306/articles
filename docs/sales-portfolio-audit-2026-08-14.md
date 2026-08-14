# Sales portfolio audit — 2026-08-14

Related: #67, #69, #70

This audit applies `docs/SALES_FIRST_EDITORIAL_POLICY.md` to the 31 Markdown articles currently under `articles/`.

The goal is not to preserve article count. The public surface should show a small number of strong, evidence-backed capabilities instead of a long stream of implementation updates.

## Summary

| Decision | Count |
|---|---:|
| KEEP | 2 |
| REWRITE | 12 |
| MERGE | 10 |
| KEEP_PRIVATE | 6 |
| DELETE / ARCHIVE | 1 |
| **Total** | **31** |

## Decisions

| Article | Decision | Portfolio rationale / next action |
|---|---|---|
| `2026-08-13-01-accessibility-contract.md` | REWRITE | 実装説明より「UI刷新後も利用者が昨日できたことを失わない」を主役にする。Issue #70でreader before/afterとproofを定義済み。 |
| `2026-08-13-02-how-people-compress-a-person.md` | MERGE | 個人紹介としては良いが単独の営業資産として成果proofが薄い。`chatgpt-multiproject-autonomy` の「何ができる人か」を説明する一節へ統合する。 |
| `2026-08-13-03-dont-infer-domain-from-language.md` | KEEP_PRIVATE | explicit metadataとunknownを守る原則は妥当だが、現状はrepository分類の実装説明が主。より大きい「AI運用で推測を事実にしない」実績へ統合できるまで非公開。 |
| `2026-08-13-04-effect-size-is-not-a-conclusion.md` | MERGE | `compatibility-vs-validity-gate.md` と同じ「計算できる/動く != 意思決定に使える」価値。descriptive pilotを第2ケースとして統合する。 |
| `2026-08-13-04-legacy-limit-complete-archive.md` | MERGE | `top-n-boundary-evidence` と同じ「見えているN件の外側を失わない」問題。互換性より完全性・境界証拠を主役にして1本へ。 |
| `2026-08-13-05-pin-assets-commit-sha256.md` | REWRITE | Prompt Vault→travelのcross-repo実績が強い。「consumerを変えていないのに公開物が変わる」を防ぐasset supply-chain reliabilityとして見せる。 |
| `2026-08-13-06-python-one-source-browser.md` | MERGE | `single-source-python-browser-calculation.md` と実質重複。後者をcanonicalにし、追加証拠だけ移す。 |
| `2026-08-14-01-audit-generated-image-claims.md` | MERGE | `one-diagram-one-message-image-pipeline.md` と同一価値。後者の具体的な「CI SUCCESSという画像内の嘘」を入口に一本化。 |
| `2026-08-14-02-publish-destination-guard.md` | MERGE | `publish-destination-three-point-guard.md` と同一のyt3証拠。ADR差分から始まる後者へ統合。 |
| `2026-08-14-03-manifest-drift-gate.md` | KEEP_PRIVATE | manifest driftは重要だが、単独では内部CIロジックの説明に見える。公開物の再現性という上位成果へ接続できるまで非公開。 |
| `2026-08-14-04-controlled-vocabulary-promotion-gate.md` | KEEP_PRIVATE | 294件/verified 32→33の実測はあるが、読者が何を導入したくなるかがまだ弱い。knowledge baseの検索品質/運用品質の成果が出てから再評価。 |
| `2026-08-14-05-compatibility-is-not-validation.md` | MERGE | `compatibility-vs-validity-gate.md` と同じ価値。dependency failureと日本語妥当性の境界を補助ケースとして統合。 |
| `2026-08-14-06-top-n-boundary-evidence.md` | REWRITE | 50位/51位という具体的境界証拠が強い。「ランキングを顧客が監査できる」価値へ寄せ、legacy-limit記事を吸収する。 |
| `claude-watermark-secret-key-detection.md` | KEEP_PRIVATE | 現在唯一 `published: true` だが、中心は公開研究/制度の整理で、書き手固有の実装・運用proofがない。営業portfolio基準では公開面から外す。 |
| `clean-checkout-final-state-gate.md` | MERGE | 単独CI Tipsでは弱い。multi-project autonomy記事の「Doneをコード生成で終わらせない」completion contractの証拠へ統合。 |
| `codex-chatgpt-github-issue-bridge.md` | REWRITE | 「AIにPCを触らせる際の禁止境界」という顧客価値が明確。private Issue→local Codex→resultの実装proofを、agentic developmentを安全に委任できる能力として再構成。 |
| `compatibility-vs-validity-gate.md` | REWRITE | 「動いた != 判断に使える」は実務価値が広い。複数detective pilotを統合し、AI/OSS評価を安全に業務へ持ち込む能力として一本化。 |
| `csv-migration-dry-run-before-write.md` | REWRITE | booksのWork/Edition/Holdingとdry-run実装が具体的。「壊さずに既存データを移行する」導入価値を前面に出す。 |
| `fail-close-data-pipeline.md` | DELETE / ARCHIVE | 本文自身が「固有事故の一次証拠がないので公開しない」と結論。一般則は他の強い記事へ吸収でき、単独記事を維持する理由がない。 |
| `muchio-shiroinu-body-adapter.md` | KEEP_PRIVATE | 公式説明で仮説は更新されたが、本文自身が実装済み証拠不足を認めている。Unity/VRChatで完成proofが得られるまで非公開。 |
| `one-diagram-one-message-image-pipeline.md` | REWRITE | 「画像内のCI SUCCESSは証拠ではない」という具体的失敗像が強い。生成AIをproduction contentへ安全に入れる監査能力として構成する。 |
| `opencode-go-deepseek-v4-chatgpt-usage-scale.md` | KEEP_PRIVATE | 料金/usage limitが変わりやすく、現状は製品比較ニュース寄り。継続運用の実コスト・成果と接続できるまで公開しない。 |
| `primary-source-derived-data-provenance.md` | KEEP | 856→7,699という強い反転、scope差の説明、OGE一次資料、実装snapshotが揃う。金融/公開データを監査可能に扱える能力が技術名なしでも伝わる。 |
| `publish-destination-three-point-guard.md` | REWRITE | 自動投稿の「成功したまま誤配信」がreader problemとして強い。bucket/profile/remote identityの3点照合を、複数brand/channelsを安全に自動運用する価値として見せる。 |
| `single-source-python-browser-calculation.md` | REWRITE | 同じ計算の二重実装によるdriftというreader problemが明確。finBI実装を「Web UIでも業務ロジックを一つの正解に保つ」価値へ寄せる。 |
| `stage-specific-quality-gates.md` | MERGE | OK/WARN/FAILの段階差はmulti-project autonomyで重要なoperating contract。単独のlinter解説より、agentが止まる/進む判断のproofとして使う。 |
| `unity-mcp-editor-boundary.md` | REWRITE | TOOL_SUCCESS→EDITOR_VALIDATED→RUNTIME_COMPLETEDはUnity/VRChat自動化の顧客価値に直結。「AIが触れた」ではなく「実機完了まで偽成功を出さない」能力として見せる。 |
| `validate-before-pages-deploy.md` | MERGE | Pages設定のTipsとして分離せず、multi-project autonomyの「validationとdeployment stateを分ける」Done contractへ統合。 |
| `video-storyboard-ir-provider-compile.md` | REWRITE | provider-neutral storyboard IRは「生成AI providerを替えても映像意図を失わない」価値にできる。Kling merged / MiniMax draftという境界を明示し、未実行を誇張しない。 |
| `vrcpet-observation-source.md` | REWRITE | 壊れた1行、valid=2/parse issue=1、MemoryClaimへ昇格しないという具体的proofが強い。「AI memoryへ観測を安全に取り込む」能力として再構成。 |
| `why-i-could-buy-the-crash.md` | KEEP | hindsight biasという広い問題、実売買日/価格、timestamped Git evidence、判断を反証可能にする方法が一貫。portfolio benchmarkとして維持。 |

## Canonical merge targets

重複を残さず、以下を1テーマ1本へ寄せる。

### 「動く」と「判断に使える」を分ける

Canonical: `compatibility-vs-validity-gate.md`

Merge:

- `2026-08-14-05-compatibility-is-not-validation.md`
- `2026-08-13-04-effect-size-is-not-a-conclusion.md`

### 公開先の誤配信を止める

Canonical: `publish-destination-three-point-guard.md`

Merge:

- `2026-08-14-02-publish-destination-guard.md`

### 業務計算を一つの正解に保つ

Canonical: `single-source-python-browser-calculation.md`

Merge:

- `2026-08-13-06-python-one-source-browser.md`

### 生成画像を証拠扱いしない

Canonical: `one-diagram-one-message-image-pipeline.md`

Merge:

- `2026-08-14-01-audit-generated-image-claims.md`

### Top-Nの外側まで監査できるようにする

Canonical: `2026-08-14-06-top-n-boundary-evidence.md`

Merge:

- `2026-08-13-04-legacy-limit-complete-archive.md`

### 大量projectを「次を決める」ところまで自律運用する

Canonical candidate: `artifacts/candidates/2026-08/2026-08-13-chatgpt-multiproject-autonomy.md`

Merge as supporting proof / story material:

- `2026-08-13-02-how-people-compress-a-person.md`
- `clean-checkout-final-state-gate.md`
- `stage-specific-quality-gates.md`
- `validate-before-pages-deploy.md`

## Immediate publication changes

1. `claude-watermark-secret-key-detection.md` は `published: false` へ戻す。技術的な内容の正誤ではなく、portfolioとして「自分が何を実現できるか」を示すproofが弱いため。
2. `fail-close-data-pipeline.md` は `articles/` から外す。固有proof不足を本文自身が明記しており、一般則は他記事へ吸収する。
3. その他は現在 `published: false` のため、REWRITE/MERGEが終わるまで非公開を維持する。

## Promotion priority

公開候補を次の順で磨く。

1. `why-i-could-buy-the-crash.md` — benchmark / KEEP
2. `chatgpt-multiproject-autonomy` — benchmark / candidate→article
3. `primary-source-derived-data-provenance.md` — KEEP
4. `codex-chatgpt-github-issue-bridge.md` — safe agentic development
5. `csv-migration-dry-run-before-write.md` — safe data migration
6. `unity-mcp-editor-boundary.md` — verifiable Unity automation
7. `video-storyboard-ir-provider-compile.md` — provider-portable video generation
8. `publish-destination-three-point-guard.md` — safe multi-channel automation

## Done condition

`articles/` の本数が減ってもよい。

公開面だけを見た第三者が、技術名の一覧ではなく、少なくとも次の能力を具体的な証拠付きで理解できる状態をDoneとする。

- 大量のAI/agent/projectを完了条件込みで運用できる
- 金融・公開データを一次情報とprovenance付きで検証できる
- AI/OSSの「動く」と「業務判断に使える」を分離できる
- データ移行・公開・自動投稿を壊す前に検証できる
- Unity/VRChatや生成AIの自動化をtool successで終わらせずruntimeまで検証できる
