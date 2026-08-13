# Archived article drafts

このディレクトリは、技術的には正しいが、**単発の細かなバグ修復に閉じており、現在の編集方針では主力記事にしない原稿**の索引です。

## Archive rule

次の条件を満たす原稿は `articles/` から外します。

- 特定repo・特定日の単発不具合の修復が主題である
- 修復内容がCI、状態機械、provenance、fail-close、責務分離などの再利用可能な仕組みへ十分に昇華していない
- 読者がそのrepoを使っていない場合の価値が小さい
- より広い記事の具体例として吸収できる

逆に、個別事故から始まっていても、複数repoへ移植できる契約・検証法・安全境界まで一般化できた記事は残します。

アーカイブは削除ではありません。元原稿はGit履歴に固定し、必要なら再利用します。

## 2026-08-13 archived

Snapshot before archival: `005f0a0e6e141c1f9d58afbfd659e623b4d40673`

- `python-bulk-sync-syntax-gate.md` — Python一括同期後の構文破損という局所修復。広い自律開発記事では「機械的なgateへ落とす」実例として吸収する。
  - https://github.com/KAFKA2306/articles/blob/005f0a0e6e141c1f9d58afbfd659e623b4d40673/articles/python-bulk-sync-syntax-gate.md
- `env-contract-before-deploy.md` — Vite環境変数名不一致の局所修復。deploy前契約検証という一般原則だけを上位記事へ吸収する。
  - https://github.com/KAFKA2306/articles/blob/005f0a0e6e141c1f9d58afbfd659e623b4d40673/articles/env-contract-before-deploy.md
- `unity-vrchat-shader-troubleshooting-qa.md` — VRChat Uploader周辺の単発トラブルシュート。個別症状の記事としては主力化せず、実環境検証と完了判定の例としてのみ再利用する。
  - https://github.com/KAFKA2306/articles/blob/005f0a0e6e141c1f9d58afbfd659e623b4d40673/articles/unity-vrchat-shader-troubleshooting-qa.md
