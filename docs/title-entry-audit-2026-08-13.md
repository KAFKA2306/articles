# Title Entry Audit — 2026-08-13

## 目的

`articles/*.md` のタイトルを、技術名を知っている読者だけでなく、問題そのものに関心がある読者まで届く入口になっているかで横断監査する。

分類:

- **A**: タイトル前半だけで一般語の問題・疑問・具体的事件が成立している。
- **B**: 記事内容は一般化できるが、技術名・API名・内部語彙が入口を狭めている。改題する。
- **C**: タイトル以前に主題が狭すぎる、または複数主題が混在する。記事設計から見直す。

「入口を広くする」は証拠範囲を広げる意味ではない。タイトルの問いは一般化してよいが、本文では実測したケースと一般原則を分ける。

## 全件監査

| article | class | 判定 | action |
|---|---|---|---|
| `claude-watermark-secret-key-detection.md` | A | 「誰のため？」という疑問が先に立ち、秘密鍵・検出は後半で意味づけされる | 維持 |
| `codex-chatgpt-github-issue-bridge.md` | A | 「AIにPCを触らせる橋は信用できるか」が技術名なしでも分かる | 維持 |
| `csv-migration-dry-run-before-write.md` | B | `CSV importer` / `dry-run` / CLI が入口になり、記録を使えるデータへ変える一般問題が隠れている | 改題 |
| `fail-close-data-pipeline.md` | A | 「取れなかったを0件にしない」が一般語で問題を表している | 維持。ただし本文の主題再設計Issueは別管理 |
| `muchio-shiroinu-body-adapter.md` | A | 「モデル差し替えを作ろうとしたら設計が変わった」という失敗・反転が先にある | 維持 |
| `one-diagram-one-message-image-pipeline.md` | A | 「生成AIの図にCI成功と書いてあった」という具体的事故が入口 | 維持 |
| `primary-source-derived-data-provenance.md` | B | 数字の反転は強いが、`scope` が結論語になっている | 改題 |
| `python-bulk-sync-syntax-gate.md` | B | 事故は分かるが `Python` / `compileall` が解決策の入口を狭める | 改題 |
| `unity-mcp-editor-boundary.md` | A | 「AIが操作できた＝完成か？」という一般的な成功判定の問いが先にある | 維持 |
| `unity-vrchat-shader-troubleshooting-qa.md` | A | 「VRだけ二重に見えた」という症状から始まり、Shader/Uploaderは探索の後に出る | 維持 |
| `video-storyboard-ir-provider-compile.md` | B | Kling / MiniMax / API / Storyboard compile が先行し、「同じ指示がサービスごとに壊れる」一般問題が隠れている | 改題 |
| `vrcpet-observation-source.md` | A | 「聞いた会話を記憶にしてよいか」という問いが技術名なしで成立する | 維持 |

## B判定の改題

### csv-migration-dry-run-before-write.md

旧:

`CSV importerを作る前にdry-runしか作らなかったら、CLIとブラウザの判定が1本になった`

新:

`バラバラな記録を「使えるデータ」にするには？ 書き込む前に判定だけを作った`

入口を「CSVの実装」から「人間の記録を、あとで検索・集計・更新できるデータへ変える」に広げる。`books` はケーススタディとして本文で扱う。

### primary-source-derived-data-provenance.md

旧:

`856件を7,699件に直したとき、問題は『計算ミス』ではなくscopeだった`

新:

`856件が7,699件になった。でも計算ミスではなかった：「どこまで数えたか」を残す`

`scope` を知らなくても問題が分かる日本語へ置き換え、正式語は本文で導入する。

### python-bulk-sync-syntax-gate.md

旧:

`一括同期でPythonが壊れた。6ファイルだけ巻き戻してcompileallを門番にした`

新:

`一括同期でコードが壊れた。6ファイルだけ戻して「壊れたら止まる」門番を置いた`

Python固有の事故から、「広範囲変更のあとに最小単位だけ復旧し、再発を自動停止する」という一般問題へ入口を広げる。`compileall` は本文で正式な実装手段として説明する。

### video-storyboard-ir-provider-compile.md

旧:

`KlingとMiniMaxの仕様差を、APIエラーになる前にStoryboardのcompile errorへ変えた`

新:

`同じ動画指示なのに、生成AIを変えると壊れる。仕様差を実行前に止めた`

provider名やIRを知らなくても、「同じ意図がサービスごとの仕様差で壊れる」という問題が分かる入口にする。

## 今後の運用

新規記事では候補選定時に次の3案を必須にする。

1. `general_problem`: 一般語の問題・欲求
2. `concrete_anomaly`: 実測できる異常・失敗・数字
3. `searchable`: 一般語の入口 + 正式技術名

採用タイトルは3案のいずれかとし、専門用語だけで入口が成立している場合は `narrow_technical_title_entry` として公開不可にする。

## 完了条件

- 全既存記事をA/B/C分類済み
- Bの4記事を実ファイル上で改題
- 新規候補で3タイトル案を必須化
- 選択タイトルが3案のいずれかであることをコードで検証
- 公開前査読で狭い技術タイトルをblocking扱い
- タイトルを広げても本文の証拠範囲を超えない契約を正準化
