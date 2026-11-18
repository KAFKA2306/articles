---
type: audit
description: "articles全MarkdownへのKafstyler適用進捗と未検証範囲"
tags:
  - articles/audit
  - kafstyler/review
---

# 全MarkdownのKafstyler適用台帳

## 目的

記事の読者が、タイトルから必要な答えを見つけ、根拠を確認し、自分の作業で結果を再現できるようにする。対象は記事だけでなく、README、契約、運用文書、報告書など全Markdown。各ファイルに `charter`、`schema`、`humanizer`、`scrutiny`、`benchmark`、`deliver`、`prune` を適用する。

## 現在の結果

| ファイル | 実施したこと | 未完了 |
| --- | --- | --- |
| `AGENTS.md` | 全Markdown・全7スキルの適用と記録を作業規約に追加（commit `44f13010`） | 実際の全件適用・検証 |
| `articles/kafstyler-agent-quality-loop.md` | 読者の問題と実験結果が先に伝わるタイトル・冒頭に改稿（commit `868bc9c`） | 7スキルそれぞれの完全なレビュー、読者テスト、現行ソース再検証 |

上記は全件レビュー完了を意味しない。未記載のMarkdownは未点検として扱う。

## 各ファイルの記録項目

- ファイルパスと対象blob SHA
- 参照したKafstylerのコミットSHAと7つのSKILL.md
- charter：想定読者、読む目的、読後にできる操作
- schema：frontmatter、タグ、リンク、台帳の一貫性
- humanizer：タイトル、冒頭、見出し、語彙の修正理由
- scrutiny：反例、根拠が届かない主張、誤読の可能性
- benchmark：同じ読者タスクでの修正前後と実行結果
- deliver：利用者の入口で確認した成果とコミット
- prune：重複、陳腐化、不要なファイル・文章の削除または保持理由

## 完了条件

全Markdownのファイル一覧を確定し、各ファイルの7スキル記録を埋め、必要な改稿と整理をコミットする。適用した版の監査・テスト・リンク確認を実行し、実際の結果を記録する。公開済み記事の公開状態は勝手に変えない。

## 全件対象の確定（2026-11-18）

GitHub main のツリー `e26d36d07eeca20e1a2edc408ab6b5f2a874a344` でMarkdown 100件（記事 53件、その他 47件）を確認した。下記のSHAは棚卸し時点のblob SHA。棚卸しだけで各スキルの適用を完了したとは扱わない。

| 対象ファイル | blob SHA | 7スキル実査 |
| --- | --- | --- |
| `AGENTS.md` | `bc061a93f7ee` | 未完了 |
| `README.md` | `f69cbd7b1c65` | 未完了 |
| `articles/2026-08-13-01-accessibility-contract.md` | `252ee4307836` | 未完了 |
| `articles/2026-08-13-02-how-people-compress-a-person.md` | `48db04d201de` | 未完了 |
| `articles/2026-08-13-03-dont-infer-domain-from-language.md` | `3f085f2fb90f` | 未完了 |
| `articles/2026-08-13-04-effect-size-is-not-a-conclusion.md` | `98edc84fcd78` | 未完了 |
| `articles/2026-08-13-04-legacy-limit-complete-archive.md` | `1de667aaead4` | 未完了 |
| `articles/2026-08-13-05-pin-assets-commit-sha256.md` | `23d763a73302` | 未完了 |
| `articles/2026-08-13-06-python-one-source-browser.md` | `d6fd37ba0204` | 未完了 |
| `articles/2026-08-14-01-audit-generated-image-claims.md` | `a46171f1c952` | 未完了 |
| `articles/2026-08-14-02-publish-destination-guard.md` | `dde348e41c3f` | 未完了 |
| `articles/2026-08-14-03-manifest-drift-gate.md` | `e158b657651a` | 未完了 |
| `articles/2026-08-14-04-controlled-vocabulary-promotion-gate.md` | `8a41b0f85714` | 未完了 |
| `articles/2026-08-14-05-compatibility-is-not-validation.md` | `0c8b3c133a40` | 未完了 |
| `articles/2026-08-14-06-top-n-boundary-evidence.md` | `ac392d78ec20` | 未完了 |
| `articles/2026-08-14-07-public-catalog-boundary.md` | `c34ac9d46b45` | 未完了 |
| `articles/2026-08-14-08-severity-aware-quality-gate.md` | `904e31759fba` | 未完了 |
| `articles/2026-08-14-09-domain-prefixed-run-id.md` | `6d01d25dd1b2` | 未完了 |
| `articles/2026-08-15-affected-set-is-a-contract.md` | `42dfc50cf449` | 未完了 |
| `articles/2026-08-15-ai-character-intelligence-muchio.md` | `9e34317b59b0` | 未完了 |
| `articles/2026-08-15-hook-runner-is-not-policy.md` | `7df214b8c759` | 未完了 |
| `articles/2026-08-15-runtime-validation-boundary.md` | `139ab4ee6c51` | 未完了 |
| `articles/2026-08-15-two-of-two-is-not-compiler-authority.md` | `6881bd5d0093` | 未完了 |
| `articles/2026-08-15-type-checker-config-is-authority.md` | `4a0b4f59e673` | 未完了 |
| `articles/2026-08-16-01-standard-terms-not-rigid-workflows.md` | `26b4f6a59054` | 未完了 |
| `articles/2026-08-16-ai-added-decision-cost-audit.md` | `1042e0b31035` | 未完了 |
| `articles/2026-11-07-01-metr-takeoff-terms.md` | `4a2738ef4b7d` | 未完了 |
| `articles/2026-11-07-02-ai-agent-safety-blind-spots.md` | `200aef447b76` | 未完了 |
| `articles/2026-11-09-01-portable-agent-contracts.md` | `4dfad89f384b` | 未完了 |
| `articles/2026-11-09-portable-agent-contracts.md` | `fd853da0ce63` | 未完了 |
| `articles/2026-11-15-01-kioxia-per-cashflow.md` | `c9fd150cf2c2` | 未完了 |
| `articles/2026-11-15-codex-evidence-mission.md` | `41e0c67f1e57` | 未完了 |
| `articles/3d-animation-contact-timing.md` | `afe399b56a66` | 未完了 |
| `articles/ai-research-acceleration-metr-2026.md` | `d8a77cbe84b3` | 未完了 |
| `articles/chatgpt-multiproject-autonomy.md` | `b80c7be91a8b` | 未完了 |
| `articles/claude-watermark-secret-key-detection.md` | `cfbc890304dd` | 未完了 |
| `articles/codex-chatgpt-github-issue-bridge.md` | `0adaa035b503` | 未完了 |
| `articles/comfyui-8-missions-selection-20261107.md` | `99e6e1f1361f` | 未完了 |
| `articles/csv-migration-dry-run-before-write.md` | `e1d52292c0b8` | 未完了 |
| `articles/financial-ratio-denominator-check.md` | `68176d65343a` | 未完了 |
| `articles/headline-reader-check.md` | `337f02ad1127` | 未完了 |
| `articles/issue-driven-development.md` | `baf6f9838665` | 未完了 |
| `articles/kafstyler-agent-quality-loop.md` | `dd016ede3e18` | 未完了 |
| `articles/muchio-shiroinu-body-adapter.md` | `9edea4fb9937` | 未完了 |
| `articles/opencode-go-deepseek-v4-chatgpt-usage-scale.md` | `c4aa022cf84e` | 未完了 |
| `articles/primary-source-derived-data-provenance.md` | `c8b91a6fb47b` | 未完了 |
| `articles/stage-specific-quality-gates.md` | `a648c4d987cd` | 未完了 |
| `articles/sts2-one-hp-choice-test.md` | `2ac129b6f60e` | 未完了 |
| `articles/unity-mcp-editor-boundary.md` | `18c5b6fe777a` | 未完了 |
| `articles/validate-before-pages-deploy.md` | `b5960ac35f3b` | 未完了 |
| `articles/video-storyboard-ir-provider-compile.md` | `0c47c257f2e9` | 未完了 |
| `articles/vote-leverage-audit-2021-2026.md` | `acbfb2dc8f52` | 未完了 |
| `articles/vrcpet-observation-source.md` | `a9e2a909048d` | 未完了 |
| `articles/web-dialog-keyboard-eval.md` | `d9b8a41b6e74` | 未完了 |
| `articles/why-i-could-buy-the-crash.md` | `f7808488ca0c` | 未完了 |
| `artifacts/archive/README.md` | `b7f738bc7e62` | 未完了 |
| `artifacts/archive/fail-close-data-pipeline-notes.md` | `e5c76c88750d` | 未完了 |
| `artifacts/candidates/2026-08/2026-08-11-engineering-evidence-2026-08-6877fbd762.md` | `c266ca595f03` | 未完了 |
| `artifacts/candidates/2026-08/2026-08-11-engineering-evidence-2026-08-ab25a976.md` | `a38817b65768` | 未完了 |
| `artifacts/candidates/2026-08/2026-08-12-codex-chatgpt-github-issue-bridge.md` | `0350f1fbcd0c` | 未完了 |
| `artifacts/candidates/2026-08/2026-08-13-chatgpt-multiproject-autonomy.md` | `84a94bd88252` | 未完了 |
| `artifacts/candidates/2026-08/2026-08-13-engineering-evidence-2026-08-3802662c08.md` | `65cf8189e56b` | 未完了 |
| `artifacts/candidates/2026-08/2026-08-15-false-success-is-the-real-failure.md` | `da909a3cc050` | 未完了 |
| `artifacts/candidates/2026-08/2026-08-31-engineering-evidence-2026-08-6322b3da65.md` | `9256803be09d` | 未完了 |
| `artifacts/candidates/2026-09/2026-09-14-engineering-evidence-2026-09-d9e9b015e3.md` | `d391ec263360` | 未完了 |
| `artifacts/candidates/2026-10/2026-10-12-engineering-evidence-2026-10-e7fe93227d.md` | `e06f71684e1c` | 未完了 |
| `artifacts/candidates/2026-10/2026-10-26-engineering-evidence-2026-10-9b0bc12684.md` | `05771dfc94a6` | 未完了 |
| `artifacts/candidates/2026-11/2026-11-07-01-ai-agent-ops-evidence-gates.md` | `4cc733444bdb` | 未完了 |
| `artifacts/candidates/2026-11/2026-11-15-test-the-test-with-rain.md` | `f977cb537d8d` | 未完了 |
| `artifacts/reports/2026-08/2026-08-15-false-success-is-the-real-failure.md` | `0e5686ba8974` | 未完了 |
| `artifacts/reports/2026-08/verification-stack-v2/STATUS.md` | `276264918e1c` | 未完了 |
| `artifacts/reports/2026-11/2026-11-15-article-reuse-audit.md` | `534b49b27b76` | 未完了 |
| `artifacts/reports/2026-11/2026-11-15-title-audit.md` | `ee74bd4cd716` | 未完了 |
| `artifacts/reports/2026-11/kafstyler-full-markdown-review.md` | `22121beb635b` | 未完了 |
| `benchmarks/verification-stack-v2/AMENDMENT-v2.1-before-comparison.md` | `294f07dc3162` | 未完了 |
| `benchmarks/verification-stack-v2/AMENDMENT-v2.2-supported-environment-profiles.md` | `5b7c0f15aead` | 未完了 |
| `benchmarks/verification-stack-v2/AMENDMENT-v2.3-real-repo-sampling.md` | `dc6fccda9085` | 未完了 |
| `benchmarks/verification-stack-v2/AMENDMENT-v2.4-controlled-harness-repair.md` | `13d2e36d4979` | 未完了 |
| `benchmarks/verification-stack-v2/AMENDMENT-v2.5-post-merge-evidence-integrity.md` | `da04eaf842bd` | 未完了 |
| `benchmarks/verification-stack-v2/AUTONOMY.md` | `180a0ebccf8c` | 未完了 |
| `benchmarks/verification-stack-v2/EDITORIAL_GOAL.md` | `875e339c68d1` | 未完了 |
| `benchmarks/verification-stack-v2/FIXTURE_DESIGN.md` | `1da622c2dcbc` | 未完了 |
| `benchmarks/verification-stack-v2/PROTOCOL.md` | `812f4aceca7c` | 未完了 |
| `benchmarks/verification-stack-v2/RESULTS_SCHEMA.md` | `3bd2625ed85c` | 未完了 |
| `docs/ARCHITECTURE.md` | `d97d74f06e3d` | 未完了 |
| `docs/EDITORIAL_DESIGN.md` | `599310b817da` | 未完了 |
| `docs/GRAPHITI_WEEKLY.md` | `fa0e459efd93` | 未完了 |
| `docs/PUBLICATION.md` | `cfffd9e195d0` | 未完了 |
| `docs/SALES_FIRST_EDITORIAL_POLICY.md` | `10c3ef280617` | 未完了 |
| `docs/article-portfolio-audit-2026-08-14.md` | `2069a07c27e2` | 未完了 |
| `docs/editorial-review-2026-08-12.md` | `a53de69b8962` | 未完了 |
| `docs/sales-portfolio-audit-2026-08-14.md` | `8222a5446dcd` | 未完了 |
| `docs/short-context-issue-contract.md` | `97c08a238033` | 未完了 |
| `docs/title-entry-audit-2026-08-13.md` | `f58fdfe203b2` | 未完了 |
| `docs/zenn-portfolio-audit-2026-08-15.md` | `7346c9dbf7b4` | 未完了 |
| `pipeline/AGENTS.md` | `9186a75ee128` | 未完了 |
| `pipeline/contracts/article.md` | `c05beb8a3334` | 未完了 |
| `research/aidev-vocabulary-study/CONTROLLED_EXPERIMENT.md` | `f41d5011fa21` | 未完了 |
| `research/aidev-vocabulary-study/FINDINGS.md` | `fc0433c77eba` | 未完了 |
| `research/aidev-vocabulary-study/README.md` | `545db5d9f3a8` | 未完了 |

### 今回の具体的な編集

- `articles/headline-reader-check.md`：読者に比較対象が分からない問題を冒頭で明示し、人物の紹介文を修正（commit `e26d36d`）。公開フラグは変更していない。
- `articles/2026-11-09-01-portable-agent-contracts.md` と `articles/2026-11-09-portable-agent-contracts.md`：同一テーマの重複候補として発見。内容・引用・公開用途の比較前なので削除しない。

### 残る作業

全100件の本文と参照先を確認し、7スキルの評価・改稿・削除判断・前後比較を個別に記録する。リンク検証やテストは未実施。既存の公開設定を維持する。
