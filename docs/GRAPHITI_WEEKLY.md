# Graphiti Weekly Reading Contract

Graphitiの週間記録は「保存量」より**1分で週の意味を掴めること**を優先します。

`articles/pipeline/graphiti.py` は旧形式にも対応しますが、今後のweeklyは次の順序を正準とします。

```markdown
# Weekly Diary — YYYY-Www

## brief
3〜6行。今週何が進み、何が変わったかだけ。

## highlights
- [theme] 成果 / 変化 / 数値
- [theme] 成果 / 変化 / 数値
最大8〜12件。

## decisions
- 採用した設計判断と理由
- 棄却した案と理由

## next
- 次週へ持ち越す具体的な未完了事項
- 検証待ち、外部依存、blocked

## timeline
### YYYY-MM-DD
- 詳細イベント
  - Evidence: https://github.com/...
```

## Reading order

通常は `brief → highlights → decisions → next` だけ読めば十分です。`timeline` は監査・再現時にだけ使います。

## Evidence rule

- URLは事実の直下に置く
- 「取得成功」と「採用」を分離する
- `observed / derived / assumption / unavailable` を混ぜない
- 未検証値は断定しない
- 同じ自動更新を何度もsummaryへ列挙せず、状態変化だけをhighlightへ昇格する

## Article pipeline use

private weekly本文はpublic `articles` repoへ保存しません。pipelineはweeklyから読みやすいin-memory contextを作り、技術テーマを発見した後、公開GitHub証拠へ再接地します。記事中でGraphitiを出典にはしません。
