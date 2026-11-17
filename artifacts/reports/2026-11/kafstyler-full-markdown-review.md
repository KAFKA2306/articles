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
