---
title: "月10ドルのAIコーディング枠は、自分には十分か？ OpenCode Goを「回数」ではなく容量で判断する"
emoji: "♾️"
type: "tech"
topics: ["opencode", "deepseek", "ai", "cost", "capacity"]
published: false
published_at: 2026-08-13 12:09
---

OpenCode GoのDeepSeek V4 Flashには、公式表で **月158,150 requests** という数字が出ている。

最初に見ると、

> これってほぼ無限では？

と思う。

しかし、この読み方は正確ではない。

2026年8月14日にOpenCode公式docsを確認すると、Goの利用制限は固定request数ではなく**ドル換算の利用額**で定義されている。

```text
5時間  = $12 usage
1週間  = $30 usage
1か月  = $60 usage
```

公式が載せている17,150回や158,150回は、観測された典型的なtoken / cache patternから換算した**推定request数**である。

- OpenCode Go: https://opencode.ai/docs/go/
- 日本語docs: https://opencode.ai/docs/ja/go/

この記事で知りたいのは「最大何回押せるか」ではない。

**自分のAI coding workloadに対して、Goが日常の制約になるのかを判断できること**である。

## まず固定quotaではなく、capacityとして読む

OpenCode公式の2026年8月9日更新docsでは、DeepSeek V4 Pro / V4 Flashについて次の推定を掲載している。

| Model | 5時間 | 1週間 | 1か月 |
|---|---:|---:|---:|
| DeepSeek V4 Pro | 3,450 | 8,550 | 17,150 |
| DeepSeek V4 Flash | 31,650 | 79,050 | 158,150 |

大きい。

ただし、これはhard quotaではない。

公式自身が、actual request countは使うmodelによって変わり、推定値はtypical request patternに基づくと説明している。

DeepSeekについて、その想定patternは次である。

| Model | input | cached | output |
|---|---:|---:|---:|
| V4 Pro | 750 | 82,000 | 290 |
| V4 Flash | 790 | 68,000 | 280 |

つまり、同じ1 requestでも消費は同じではない。

巨大な未cache contextや長いoutputを多用すれば、推定回数より速くusageを消費し得る。

逆にcacheがよく効くrequest patternなら、多数の往復を処理できる。

**「月158,150回使える」ではなく、「公式が観測した典型patternなら月158,150 requests相当」と読む。**

## 自分に十分かを見るなら、累計message数より同じ期間の実測を見る

旧稿では、手元のChatGPT累計message数とOpenCodeの月次推定を単純比較していた。

これは規模感を見るには面白いが、契約判断には弱い。

期間が違うからだ。

```text
ChatGPT累計
vs
OpenCode 5時間 / 1週間 / 1か月
```

では同じ軸ではない。

刷新後は、**自分の直近7日または30日のAI coding workload**と比較する。

例えば、直近7日にagent/tool request相当の作業が2,000回だったとする。

```text
自分: 2,000 / week
V4 Pro typical estimate: 8,550 / week
V4 Flash typical estimate: 79,050 / week
```

この場合、単純なrequest countでは、

```text
Pro:   23.4% of typical weekly estimate
Flash:  2.5% of typical weekly estimate
```

となる。

もちろん1 requestの重さが違うので、これは最終結論ではない。

しかし「ほぼ無限」という感想よりは、はるかに自分の利用へ接続できる。

## さらに良いのは、consoleのusageを直接見ること

OpenCode公式はcurrent usageをconsoleで追跡できるとしている。

Goの制限自体がドル換算なら、本当に見たいKPIはrequest数だけではない。

```text
weekly usage consumed
monthly usage consumed
model mix
request count
```

を一緒に見る。

例えば、

```yaml
period: 7d
requests: 2500
usage_consumed_usd: 8.2
weekly_limit_usd: 30
```

なら、

```text
request utilization ≈ 参考
usage utilization = 27.3%
```

と評価できる。

**Goが制約になるかは、最終的にはusage消費率で見る方が契約構造に合っている。**

## FlashとProは「何回使えるか」だけで選ばない

現行docsでは、DeepSeek V4 ProとFlashはどちらもGoのmodel listにある。

公式表ではFlashの方がtypical request estimateが大きい。

ただし、そこから

```text
Flashを通常運用
Proを難問専用
```

と自動的に決めるのも早い。

model選択には少なくとも、

- quality
- latency
- tool behavior
- context requirements
- usage consumption

がある。

だからcapacity planningでは、先に役割を決める。

例えば、

```text
routine code search / small edits
→ cheaper high-capacity model候補

complex architecture / difficult debugging
→ higher-quality model候補
```

と分け、実測で入れ替える。

**価格表からrouting policyを決めるのではなく、自分のtask classごとの成功率とusageで決める。**

## 人間の対話利用とagent loopは分ける

同じ月158,150 request相当でも、消費速度は運用で大きく変わる。

人間が1回ずつ指示するなら、request frequencyには自然な上限がある。

一方、自律agentは、

```text
issue読む
→ search
→ edit
→ test
→ retry
→ review
```

を自動で繰り返す。

複数repoを並列で処理すれば、human interactive useより速くusageを消費できる。

だから「人間には十分そう」と「agent fleetにも十分」は分ける。

私なら最低でも次を別metricにする。

```yaml
human_interactive_requests_7d: ...
agent_requests_7d: ...
retry_requests_7d: ...
failed_work_requests_7d: ...
```

特にretry率が高いと、capacityを成果へ変換できていない。

## 「何回使えるか」より「何件の仕事を完了できるか」へ進む

AI codingで本当に欲しいのはrequest数ではない。

例えば、

```text
1000 requests
→ 30 issues completed
```

と、

```text
1000 requests
→ 5 issues completed
```

では価値が違う。

そこで運用KPIを、

```text
usage / completed issue
requests / completed issue
retry rate
human intervention rate
```

へ寄せる。

これなら、安いmodelが本当に安いのかも分かる。

request単価が低くてもretryが多ければ、完了1件あたりの消費は大きくなる。

## 5分でできるcapacity check

OpenCode Goを検討するときは、次だけ取ればよい。

### Step 1: 同じ期間を選ぶ

7日か30日。

### Step 2: 自分の実績を数える

```text
requests
completed tasks
retries
human interventions
```

### Step 3: official typical estimateと比べる

例えば7日なら、現行公式値は、

```text
V4 Pro   8,550 typical requests / week
V4 Flash 79,050 typical requests / week
```

### Step 4: 可能ならconsole usageで補正する

request countではなく実usage消費率を見る。

### Step 5: 余裕率を出す

```python
capacity_margin = 1 - actual_usage / limit
```

あるいはrequest近似なら、

```python
request_margin = 1 - actual_requests / typical_estimated_requests
```

後者はあくまで近似と表示する。

## 「ほぼ無限」という言葉を使わなくてよくなった

公式の数字は十分大きい。

DeepSeek V4 Flashの月158,150、Proの月17,150というtypical estimateは、capacityの大きさを示すには有用である。

しかし自分にとって大事なのは、数字の大きさそのものではなかった。

**自分の7日・30日の実利用を測れば、Goが制約になるかを自分で判定できる。**

その状態なら「ほぼ無限」という曖昧な感想は要らない。

余裕が80%あるのか、20%しかないのか。

どのmodelがusageを使っているのか。

1件のissueを完了するのに何requestかかっているのか。

そこまで見れば、月額プランを「安そう」ではなく、自分のworkflowに対するcapacityとして評価できる。

## 2026年8月14日時点の一次情報

- OpenCode Go: https://opencode.ai/docs/go/
- OpenCode Go 日本語docs: https://opencode.ai/docs/ja/go/

OpenCode自身が、model list・利用制限は今後変更される可能性があると明記している。この記事の数値を将来読む場合は、必ず現行docsを再確認する。
