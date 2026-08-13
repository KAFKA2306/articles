---
title: "月10ドルのAIコーディング枠は、本当に『ほぼ無限』なのか？ 自分のChatGPT利用量と比べてみた"
emoji: "♾️"
type: "tech"
topics: ["opencode", "deepseek", "chatgpt", "ai", "cost"]
published: true
published_at: 2026-08-13 12:09
---

# 月10ドルのAIコーディング枠は、本当に「ほぼ無限」なのか？ 自分のChatGPT利用量と比べてみた

2026年8月13日、OpenCode GoでDeepSeek V4 Pro / V4 Flashを見て、最初に出た感想はこれでした。

> これらってほぼ無限？

料金表だけ見ると、かなり大げさに見えます。

ところがOpenCode公式が出している推定リクエスト数を見ると、少なくとも**人間が対話的にコーディングする用途では、上限を意識しない時間がかなり長そう**です。

さらに、自分のChatGPT利用量として手元に残していた集計と比べると、数字の桁がかなり違いました。

この記事では、

- OpenCode Goで実際にどのくらい使えるのか
- DeepSeek V4 ProとV4 Flashで何が違うのか
- 自分のChatGPT利用量と比べると、どのくらい大きいのか
- なぜ「文字通り無制限」とは言えないのか

を、公開一次情報と手元の利用集計を分けて整理します。

## まず結論

OpenCode Goは、初月5ドル、その後10ドル/月です。

公式の利用上限は「回数」ではなく、利用額で決まります。

| 期間 | Goの利用上限 |
|---|---:|
| 5時間 | 12ドル相当 |
| 1週間 | 30ドル相当 |
| 1か月 | 60ドル相当 |

OpenCode公式:
https://opencode.ai/docs/go/

その上で、OpenCodeが通常の利用パターンから推定しているリクエスト数は次の通りです。

| モデル | 5時間 | 1週間 | 1か月 |
|---|---:|---:|---:|
| DeepSeek V4 Pro | 3,450 | 8,550 | 17,150 |
| DeepSeek V4 Flash | 31,650 | 79,050 | 158,150 |

この数字だけを見ると、Flashは月15万回を超えます。

ただし、ここで重要なのは**固定の回数制限ではない**ことです。

OpenCode自身が「actual request count depends on the model you use」と説明しており、上の数字は典型的な入出力・キャッシュ量を仮定した推定値です。

## 「15万回使える」ではなく「典型的な使い方なら15万回相当」

OpenCodeは推定に使った1リクエストあたりのパターンも公開しています。

DeepSeek V4 Proでは、

- input: 750 tokens
- cached: 82,000 tokens
- output: 290 tokens

DeepSeek V4 Flashでは、

- input: 790 tokens
- cached: 68,000 tokens
- output: 280 tokens

という観測パターンを置いています。

公式:
https://opencode.ai/docs/go/

つまり、巨大な未キャッシュコンテキストを何度も送り、大量出力を続ければ、推定リクエスト数より早く利用額を消費します。

逆に、キャッシュがよく効く通常のコード作業なら、かなり多くの往復ができます。

ここを省いて「月158,150回まで固定で使える」と書くのは不正確です。

## 自分はChatGPTをどのくらい使っているのか

ここで、自分のChatGPT利用量と比べてみます。

手元に保存していたChatGPT利用集計では、

- 累計メッセージ: **1,840件**
- 直近サンプル: **40会話スレッド**
- そのうち画像作成依頼を含むもの: **19会話**

でした。

この個人集計は公開Webの統計ではなく、自分のChatGPT利用履歴から作ったローカルな一次データです。

なおOpenAI公式では、ChatGPTのSettings → Data controls → Export dataから、チャット履歴を含むデータを書き出せます。

OpenAI公式:
https://help.openai.com/en/articles/7260999-exporting-your-chatgpt-history-and-data

現在の手元集計には「直近30日の送信メッセージ数」の時系列がないため、OpenCodeの月次枠と厳密に同期間比較することはできません。

そのため、ここではまず**規模感だけ**を比較します。

## 累計1,840メッセージを丸ごと比較するとどうなるか

ChatGPTの1メッセージとOpenCodeの1リクエストは同じものではありません。

それを承知で、単純に「1件」という単位だけで割るとこうなります。

| OpenCode Go | 推定リクエスト数 | ChatGPT累計1,840件の何倍か |
|---|---:|---:|
| V4 Pro / 5時間 | 3,450 | 1.88倍 |
| V4 Pro / 1週間 | 8,550 | 4.65倍 |
| V4 Pro / 1か月 | 17,150 | 9.32倍 |
| V4 Flash / 5時間 | 31,650 | 17.20倍 |
| V4 Flash / 1週間 | 79,050 | 42.96倍 |
| V4 Flash / 1か月 | 158,150 | 85.95倍 |

一番驚いたのはここでした。

**手元で集計していたChatGPTの累計1,840メッセージより、V4 Proの「5時間」の推定リクエスト数3,450回のほうが大きい。**

Flashでは、5時間枠の推定31,650回だけで、1,840件の約17倍です。

もちろん、これは期間を揃えた比較ではありません。

それでも「普通の対話利用でこの上限を意識するのか？」という規模感を見るには参考になります。

## ただし、これはChatGPTとOpenCodeの性能比較ではない

ここはかなり重要です。

この比較から、

- DeepSeekがChatGPTより86倍使える
- OpenCode 1リクエストがChatGPT 1メッセージと同じ価値
- 月158,150回のコード修正が必ずできる

とは言えません。

ChatGPTの1会話では、Web検索、ツール実行、画像生成、長い推論など複数の処理が内部で動くことがあります。

一方、OpenCodeの1リクエストも、コンテキスト量、キャッシュ、出力量によってコストが変わります。

したがって今回比較しているのは**能力ではなく、ユーザーから見た利用回数のスケール**です。

## DeepSeek V4自体の上限も大きい

DeepSeek公式APIドキュメントでは、DeepSeek V4 Flash / Proについて、

- context length: **1M**
- maximum output: **384K**
- JSON Output対応
- Tool Calls対応

とされています。

DeepSeek公式:
https://api-docs.deepseek.com/zh-cn/quick_start/pricing

OpenCodeの大量リクエスト枠だけでなく、1回のリクエストで扱えるコンテキスト自体も大きい構成です。

## では「ほぼ無限」は正しいのか

自分の使い方に限定すると、かなり近い表現だと思います。

ただし、正確には次のように言うべきです。

> **人間が対話的にコードを書く用途では、DeepSeek V4 Flashの上限はかなり意識しにくい。V4 Proも十分大きい。ただし自律エージェントを大量並列・長時間で回せば普通に到達し得る。**

OpenCodeは複数エージェントを並列に動かせます。

OpenCode公式:
https://opencode.ai/

人間が1つずつ質問する場合と、エージェントが自律的にIssueを読み、コードを調査し、修正し、テストし、再試行する場合では消費速度がまったく違います。

「人間にはほぼ無限」と「コンピュータにも無限」は別です。

## 自分ならFlashを通常運用、Proを昇格先にする

この価格と上限を見る限り、運用はかなり単純にできます。

```text
通常のIssue処理
README修正
小さな実装
テスト修正
コード探索
    ↓
DeepSeek V4 Flash

複雑な設計
大規模レビュー
Flashで詰まった問題
高い推論品質を優先したい仕事
    ↓
DeepSeek V4 Pro
```

Flashを通常系にすると、OpenCode公式推定では月158,150リクエスト相当です。

Proへ上げても月17,150リクエスト相当あります。

「高価なモデルを節約しながら使う」というより、**安いモデルを常用し、難しい仕事だけ上位モデルへ昇格する**ほうが自然です。

## 次にやるべき比較は「直近30日」

今回の弱点は明確です。

ChatGPT側の1,840件は累計値で、OpenCode側は5時間・週・月という期間別推定です。

厳密に比較するなら、ChatGPT Data Exportから各メッセージの時刻を取得し、

- 直近24時間のユーザーメッセージ数
- 直近7日のユーザーメッセージ数
- 直近30日のユーザーメッセージ数
- 1会話あたりの中央値
- 最も多く使った日の送信数

を出すべきです。

OpenAI公式のData Exportにはチャット履歴が含まれます。

https://help.openai.com/en/articles/7260999-exporting-your-chatgpt-history-and-data

この集計ができれば、次は次のような比較にできます。

```text
自分のChatGPT実利用
  1日   XXX messages
  7日   XXX messages
 30日   XXX messages

OpenCode Go推定
  Pro   8,550 requests / week
        17,150 requests / month

  Flash 79,050 requests / week
        158,150 requests / month
```

ここまで揃えば、「ほぼ無限」という感想を、単なる印象ではなく自分自身の利用実績に対する倍率で評価できます。

## まとめ

今回確認できた事実は3つです。

1. OpenCode Goは初月5ドル、その後10ドル/月で、5時間12ドル相当・週30ドル相当・月60ドル相当の利用枠を持つ。
2. OpenCode公式の典型利用推定では、DeepSeek V4 Proは月17,150回、V4 Flashは月158,150回。
3. 手元のChatGPT利用集計は累計1,840メッセージで、単純な件数比較ではPro月次枠が9.32倍、Flash月次枠が85.95倍。

ただし3は期間も処理単位も一致しないため、**倍率は性能比較ではなく規模感比較**です。

それでも、月10ドルのコーディング環境として見ると、DeepSeek V4 Flashの数字はかなり異常です。

次はChatGPT Data Exportから直近30日の実測値を取り、同じ期間に揃えて比較したいと思います。

## 一次情報

- OpenCode Go: https://opencode.ai/docs/go/
- OpenCode: https://opencode.ai/
- DeepSeek API models & pricing: https://api-docs.deepseek.com/zh-cn/quick_start/pricing
- OpenAI ChatGPT Data Export: https://help.openai.com/en/articles/7260999-exporting-your-chatgpt-history-and-data
