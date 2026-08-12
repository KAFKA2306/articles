---
title: "ペットが聞いた会話を、そのまま『記憶』にしてはいけない：壊れた1行から観測と事実を分ける"
emoji: "👂"
type: "tech"
topics: ["python", "dataengineering", "privacy", "architecture", "vrchat"]
published: true
published_at: 2026-08-12 13:21
---

synthetic fixtureに、3行の会話ログを置きました。

```text
{"text":"hello"}
{"broken":
{"text":"world"}
```

真ん中の1行は壊れています。前後の2行は読めます。

ここで選択肢は3つあります。

- ファイル全体を捨てる
- 壊れた行だけ黙って消す
- 読めた2行をそのまま「人間の記憶」として保存する

どれも採用しませんでした。

実装した `KAFKA2306/vlog` のVRCPet/Muchio adapterでは、期待値を次にしています。

```text
valid records = 2
parse issues  = 1
```

2件の観測は残す。壊れた1件も「失われた」という監査情報として残す。しかし、読めた会話断片を **MemoryClaimには昇格させない**。

ここで記事の中心となる問いが決まりました。

**ペットが聞いたログは、どの時点から「記憶」と呼んでよいのか。**

結論を先に型へ固定すると、VRCPet adapterの責務は記憶を作ることではなく、**後から検証できるObservationを保存すること**になりました。

実装はPR #28でmainへmerge済みです。

- PR: https://github.com/KAFKA2306/vlog/pull/28
- merge commit: https://github.com/KAFKA2306/vlog/commit/46884310417d17dd71f544741795a2490eb354ad
- adapter README: https://github.com/KAFKA2306/vlog/blob/main/adapters/vrcpet/README.md
- test: https://github.com/KAFKA2306/vlog/blob/main/tests/test_vrcpet_adapter.py

## 1. 「聞いたテキスト」と「本人がそう言った」は同じではない

adapterが扱う観測入力は次の4系統です。

```text
logs/**/*.jsonl
pet.log
profile.json
heard_nouns.json
```

ここには、

- 会話断片
- operational log
- profile状態
- 覚えた語彙の状態

が混ざっています。

会話断片ですら、「実際に人間がその通り発言した」という確定事実ではありません。音声認識や前処理を経た観測結果だからです。

さらに、

```text
heard text == 本人の発言
learned word == 本人の関心
profile change == 本人の状態変化
pet log == 人間の記憶
```

も自動的には成立しません。

そこでVRCPet adapterには `MemoryClaim` を作る責務を持たせず、`associate_episode()` も既存Episodeへ `source_object_ids` を関連付けるだけにしました。

![Observation is not MemoryClaim](/images/vrcpet-observation-source/02-observation-not-memory.webp)

**同じ出来事の証拠になることと、その証拠だけで事実を確定できることは別です。**

この境界を最初に置いたことで、後の設計判断もかなり絞れました。

## 2. 壊れた1行だけを隔離し、「失ったこと」も保存する

会話JSONLでは、途中終了や書き込み競合で一部だけ壊れる可能性があります。

全面fail-closeなら安全ですが、正常な前後行まで失います。一方、エラー行を黙ってskipすると、何を失ったか分からなくなります。

そこでparserはrecord単位で隔離します。

```text
{"text":"hello"}   -> observation
{"broken":          -> parse issue
{"text":"world"}   -> observation
```

![Tolerant JSONL parsing](/images/vrcpet-observation-source/04-tolerant-parse.webp)

不正JSONは `line_number` と `raw_fragment` を持つissueとして残します。

Python標準の `json.loads()` が不正JSONで `JSONDecodeError` を送出することは公式ドキュメントで確認できます。

- https://docs.python.org/3.14/library/json.html

この設計で守りたいのは「できるだけ多く取り込むこと」ではありません。

**正常recordと異常recordの境界を、後から監査できる形で残すこと**です。

## 3. read-onlyでも、読み取り途中にsourceが変わればrejectする

外部アプリのdata directoryを読むadapterでは、「書き込まない」だけでは十分ではありません。

読み取り中にファイルが伸びると、同じsourceとしてhash化したつもりでも、stat・bytes・manifestが別時点を指す可能性があります。

実装では読み取り前後の状態を比較します。

```python
before = path.stat()
raw_bytes = path.read_bytes()
after = path.stat()

if (
    before.st_size != after.st_size
    or before.st_mtime_ns != after.st_mtime_ns
    or len(raw_bytes) != after.st_size
):
    raise UnstableSourceError(...)
```

さらに、

- rootを `resolve(strict=True)` する
- allowlist外rootを拒否する
- absolute pathや `..` escapeを拒否する
- 結合後の実pathがroot配下に残るか再確認する

という境界を置いています。

![Read-only boundary](/images/vrcpet-observation-source/03-read-only-boundary.webp)

ここでの成功条件は「読めた」ではなく、**安定した同一状態を読めた**ことです。

## 4. identityをファイル名ではなくraw bytesへ寄せる

同じログがbackupやrenameで別pathに現れたとき、pathをidentityにすると重複登録されます。

そこでraw bytesのSHA-256をcontent fingerprintとして使い、そのdigestとobservation typeから決定的IDを作ります。

```python
digest = sha256(raw_bytes).hexdigest()
source_id = uuid5(namespace, f"{observation_type}:{digest}")
```

![Content addressed SourceObject](/images/vrcpet-observation-source/05-content-addressing.webp)

重要なのは暗号アルゴリズムの説明ではなく、次の挙動です。

```text
logs/a.jsonl       -> same bytes
logs/renamed.jsonl -> same bytes

source id   -> equal
source hash -> equal
```

つまり、renameを新しい観測と誤認しません。

同時にmanifestへWindows absolute pathを残さず、source rootからのrelative pathだけを保持します。

```json
{
  "metadata": {
    "source": "vrcpet",
    "observation_type": "conversation",
    "source_relative_path": "logs/2026-08-12.jsonl"
  }
}
```

回帰テストではmanifest全体に `C:\Users\` が含まれないことも確認しています。

![Privacy boundary](/images/vrcpet-observation-source/06-privacy-boundary.webp)

## 5. 「現在値」も記憶ではなくsnapshotとして残す

`profile.json` や `heard_nouns.json` はイベント列ではなく状態です。

現在値だけで昨日を上書きすると、

- 何が増えたか
- 何が減ったか
- parser変更で見え方が変わっただけか

を後から区別できません。

そこでexact raw bytesをimmutable snapshot candidateとして保持し、差分を別に計算します。

```text
profile:
  added / removed / changed

vocabulary:
  new / increased / decreased / missing
```

![Snapshot and diff](/images/vrcpet-observation-source/08-snapshot-diff.webp)

ここでも `missing` を `0` に変えません。

ファイルが部分的だったのか、schemaが変わったのか、本当にcountが0なのかは別の状態だからです。

## 6. Episodeへ束ねても、MemoryClaimにはしない

同じ1時間について、

```text
primary audio
VRCPet conversation observation
profile snapshot
vocabulary snapshot
```

が存在することはあり得ます。

これらを同じEpisodeへ関連付けることはできます。しかし、VRCPet観測だけで「本人はXに関心がある」「本人はYと言った」というMemoryClaimを作ることはしません。

![Episode association without MemoryClaim](/images/vrcpet-observation-source/09-episode-no-claim.webp)

センサーが増えるほど、この境界は重要になります。

Observationを追加しただけなのに「真実」が自動的に増える構造を避けるためです。

## 7. 日記は正本ではなく、何度でも作り直せるprojectionにする

adapterには `すいの目から見た1日` というdaily projectionがあります。

表示には、

- 会話観測件数
- parse issue件数
- state snapshot件数
- よく聞いた言葉
- profile変化
- pet utterance

などを含められます。

しかし、このMarkdown自体を正準データにはしません。

![Rebuildable daily projection](/images/vrcpet-observation-source/10-rebuildable-view.webp)

E2E fixtureでは、壊れたconversationを含む入力から、

```text
conversation records = 2
parse issues          = 1
snapshots             = 2
```

を確認したうえでdaily viewを再構築します。

ここで重要なのは、日記が便利かどうかより、**元のevidenceから同じviewを作り直せること**です。

## 8. 境界はテストで固定する

今回の回帰テストは、設計判断をそのままfailure conditionへしています。

| 境界 | テストすること |
| --- | --- |
| parser | malformed JSONLの前後の正常recordを失わない |
| input | allowlist外rootを拒否する |
| path | `..` escapeを拒否する |
| stable read | 読み取り中にsourceが変化したらrejectする |
| identity | 同じbytesならrename後も同じIDになる |
| privacy | Windows absolute pathをmanifestへ残さない |
| snapshot | exact bytesを保持し、diffを分ける |
| semantics | Episode associationしてもMemoryClaimを作らない |
| E2E | evidenceからdaily viewを再構築できる |

mainのmerge commitに対して、GitHub Actionsの `Lint` と `Test and Security Audit` はsuccessになっています。

- Lint: https://github.com/KAFKA2306/vlog/actions/runs/31557522611
- Test and Security Audit: https://github.com/KAFKA2306/vlog/actions/runs/31557522419

最小fixtureで追試する場合は、実データを使う必要はありません。

```text
{"text":"hello"}
{"broken":
{"text":"world"}
```

期待値を、

```text
records == 2
issues == 1
```

として `tests/test_vrcpet_adapter.py` を含むsuiteを実行できます。

repository:
https://github.com/KAFKA2306/vlog

## まとめ

この実装で難しかったのはJSONL parserではありませんでした。

壊れた1行をどう扱うか考えると、さらに根本の問題が見えます。

**読めたデータは、どこまで意味を持ってよいのか。**

VRCPet adapterでは、

```text
log
  -> Observation
  -> Episode association
  -> rebuildable projection
```

までは進めますが、adapter自身に

```text
Observation -> MemoryClaim
```

をさせません。

ペットが聞いたことは有用な観測です。しかし、**有用な観測であることと、本人についての真実として保存してよいことは別です。**

## 一次情報・再現証拠

- PR #28: https://github.com/KAFKA2306/vlog/pull/28
- merge commit: https://github.com/KAFKA2306/vlog/commit/46884310417d17dd71f544741795a2490eb354ad
- adapter README: https://github.com/KAFKA2306/vlog/blob/main/adapters/vrcpet/README.md
- reader: https://github.com/KAFKA2306/vlog/blob/main/adapters/vrcpet/reader.py
- parser: https://github.com/KAFKA2306/vlog/blob/main/adapters/vrcpet/parser.py
- normalizer: https://github.com/KAFKA2306/vlog/blob/main/adapters/vrcpet/normalizer.py
- snapshot: https://github.com/KAFKA2306/vlog/blob/main/adapters/vrcpet/snapshot.py
- daily view: https://github.com/KAFKA2306/vlog/blob/main/adapters/vrcpet/daily_view.py
- test: https://github.com/KAFKA2306/vlog/blob/main/tests/test_vrcpet_adapter.py
- Python `json`: https://docs.python.org/3.14/library/json.html
