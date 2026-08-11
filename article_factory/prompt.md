# Monthly Article Factory Prompt

## Goal

毎月1本以上、LAPRAS AI Reviewで3.5以上を狙える技術記事を自律生成する。量ではなく、公開可能な最高品質の1本を選ぶ。

## Official LAPRAS rubric

記事を以下の5軸で0.0〜5.0評価する。

- 論理性
- 実用性
- 読みやすさ
- 独自性
- 明確性

内部ゲートでは平均4.1を目標、3.8未満は公開しない。各軸3.5未満も公開しない。

## Article contract

1. 冒頭で「誰の、どの問題を、この記事でどう解決するか」を3文以内で明示する。
2. 一般論ではなく、KAFKA2306の実装・設計判断・失敗・改善結果を中心にする。
3. 少なくとも2件のKAFKA2306 GitHub上の一次証拠（commit / PR / file / workflow等）を含める。
4. 外部仕様・数値・挙動は一次情報URLで裏付ける。一次情報を確認できない主張は削除する。
5. 数値には対象、期間、単位、比較基準を付ける。
6. コードを載せる場合は、なぜその設計にしたか、代替案、失敗条件、検証方法まで書く。
7. 「やってみた」「便利だった」で終わらず、再現可能な手順・判断基準・検証結果を残す。
8. 読者がそのまま使えるチェックリスト、最小実装、検証コマンドのいずれかを必ず含める。
9. 最後に「適用範囲」「限界」「次に検証すべきこと」を明示する。
10. 誇張表現、根拠のない最上級、未検証の性能主張は禁止する。

## Topic selection priority

優先順位は以下。

1. backend / infrastructure の実装証拠
2. product engineering の成果とユーザー導線
3. technical leadership / architecture decision
4. data engineering / AI agent reliability
5. その他、直近30〜45日の公開GitHub活動から強い一次証拠があるテーマ

同じ主題の焼き直しは避ける。既存記事より新規性が低い候補は棄却する。

## Evaluation output

評価器はJSONのみを返す。

```json
{
  "logic": 0.0,
  "utility": 0.0,
  "readability": 0.0,
  "originality": 0.0,
  "clarity": 0.0,
  "overall": 0.0,
  "blocking_issues": [],
  "revision_actions": []
}
```

overallは5軸の算術平均とする。
