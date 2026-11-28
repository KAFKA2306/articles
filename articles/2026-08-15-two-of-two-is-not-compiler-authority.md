---
title: "新しい道具が動いたことと、古い道具を捨てられることは違う"
emoji: "🧪"
type: "tech"
topics: ["typescript", "oxlint", "ci", "testing", "tooling"]
published: false
created_at: "2026-08-15"
updated_at: "2026-11-28"
---

二つのコマンドで行っていた仕事を、一つの新しい道具にまとめたい。小さなサンプルでは両方とも同じエラーを検出できた。ならば古い道具は不要だろうか。

置換で問うべきことは、新しい道具の能力が存在するかではない。**旧方式に任せている必要な仕事が、移行後も残るかである。** 型チェックの統合を検討した際、比較表の空欄がこの違いを明確にした。

## 小さなサンプルでは同点だった

TypeScriptのコンパイラtscとOxlintの型チェック機能を、二つの固定した型エラーで比較した。[当時の測定結果](https://github.com/KAFKA2306/articles/blob/81848adca34e077835735a1f8586c6e8cd8cd511/benchmarks/verification-stack-v2/results/controlled/summary.json)は次のとおりである。

| 道具 | 型エラーの検出 | 正常入力の誤拒否 |
| --- | ---: | ---: |
| tsc | 2/2 | 0 |
| Oxlint typeCheck | 2/2 | 0 |

この二件ではOxlintも必要な診断を出した。一方、[実リポジトリでの測定記録](https://github.com/KAFKA2306/articles/blob/81848adca34e077835735a1f8586c6e8cd8cd511/benchmarks/verification-stack-v2/results/external/summary.json)には別の状態が残っていた。

| 実行した機能 | 当時の記録 |
| --- | --- |
| tsc | 観測済み |
| 通常のOxlint | 観測済み |
| 置換に必要なOxlint --type-check | NOT_RUN |

通常のOxlintを実行した事実を、型チェック機能を実行した事実へ置き換えることはできない。旧コマンドの削除を見送った理由は、新方式が失敗したからではなく、対象環境で必要な仕事を実行した記録がなかったからだ。

[Oxlintの型チェック機能の説明](https://oxc.rs/docs/guide/usage/linter/type-aware)にはtscを置換する利用例がある。元の調査時点では[CLI](https://oxc.rs/docs/guide/usage/linter/cli.html)と[設定仕様](https://oxc.rs/docs/guide/usage/linter/config-file-reference)でexperimentalとされていた。これらの機能説明と、個々のプロジェクトの移行可否は別の情報である。

## 置換されるのはコマンドではなく責務である

同じ型エラーを拾えても、対象ファイルが異なれば一方の道具だけが見ている範囲が残る。TypeScriptでは[tsconfig](https://www.typescriptlang.org/tsconfig/)のinclude、exclude、referencesなどが対象を左右する。[noEmit](https://www.typescriptlang.org/tsconfig/noEmit.html)は出力ファイルを生成せず型チェックするための設定である。

古いコマンドを廃止する前に、そのコマンドが必要とされる理由を列挙する。不要になった責務は削ればよい。必要な責務だけ新方式へ移す。この区別をせず、古い検査の全部を永久に維持するのも、新しい道具の採用を理由に全部を削るのも適切ではない。

## 五分で置換の空欄を探す

自分のプロジェクトで置換したい処理を一つ選び、次の表に既存の設定、実行結果、必要な仕事を記入する。

| 確認する責務 | 旧方式 | 新方式 |
| --- | --- | --- |
| 対象範囲・設定 | 実際の設定 | 対応する設定 |
| 正常な入力への挙動 | 観測結果 | 観測結果 |
| 必要な失敗への挙動 | 観測結果 | 観測結果 |
| 運用上必要な安定性 | 現在の条件 | 受け入れ可能な条件 |

必要な欄が未実行なら、その状態のまま判断材料にする。空欄を不合格とも合格とも決めつけない。旧方式の仕事そのものが不要と判断できる場合は、その廃止と新方式による代替を区別する。

監視サービスやバックアップ先の変更にも応用できる。旧方式に残す必要がある役割が新方式で満たされれば、重複する設定やコマンドを退役させる。新しい道具を一つ増やすことではなく、必要な仕事を失わずに道具を減らすことが統合の成果である。
