---
title: "ペットが聞いた会話を、そのまま『記憶』にしてはいけない：VRChatログを観測センサー化する"
emoji: "👂"
type: "tech"
topics: ["python", "dataengineering", "privacy", "architecture", "vrchat"]
published: true
published_at: 2026-08-12 13:21
---

会話を聞いて、言葉を覚え、少しずつ振る舞いが変わるペット型アプリがあるとします。

そのログをHuman Memoryのような記憶基盤へ接続するとき、最初に思いつく設計は単純です。

```text
ペットが聞いた会話 → 記憶
```

しかし、この設計は危険です。

聞き間違い、途中で壊れたJSONL、アプリ内部状態、語彙カウンタ、実行ログまでが、同じ「記憶」という意味に昇格してしまうからです。

今回 `KAFKA2306/vlog` に `adapters/vrcpet` を実装する際、逆の設計にしました。

**ペットのログは記憶ではない。記憶を作るために後から検証できる「観測証拠」である。**

この1つの判断から、read-only境界、SHA-256、決定的UUID、壊れた行の隔離、immutable snapshot、Episode association、再構築可能な日次ビューまでがほぼ一方向に決まりました。

実装はPR #28でmainへmerge済みです。

- PR: https://github.com/KAFKA2306/vlog/pull/28
- merge commit: https://github.com/KAFKA2306/vlog/commit/46884310417d17dd71f544741795a2490eb354ad
- adapter README: https://github.com/KAFKA2306/vlog/blob/main/adapters/vrcpet/README.md
- test: https://github.com/KAFKA2306/vlog/blob/main/tests/test_vrcpet_adapter.py

この記事では、特定のペット製品に依存しない形で、**「ローカルアプリの私的ログを、意味を壊さずHuman Memoryへ接続する」**ための設計を分解します。

## 1. 問題：観測と記憶を同じ型にすると、意味が壊れる

VRCPet/Muchio adapter が扱う観測済み入力は次の4系統です。

```text
logs/**/*.jsonl
pet.log
profile.json
heard_nouns.json
```

ここには性質の違う情報が混ざっています。

- 会話断片
- operational log
- profileの状態
- 覚えた語彙の状態

会話断片ですら、「実際に人間がそう発言した」という確定事実ではありません。音声認識や前処理を経た観測結果だからです。まして `profile.json` や `heard_nouns.json` は、ペット側の内部状態です。

この図で見るべき点は、入力から最終ビューまでの間に **read-only observation adapter** を置き、ログを直接「記憶」に変換していないことです。

![VRCPet observation source overview](/images/vrcpet-observation-source/01-overview.webp)

採用した流れは次です。

```text
read-only SourceFile
  -> tolerant parse
  -> SHA-256 + deterministic UUID
  -> SourceObject + source manifest
  -> IngestionRun(source_hash + pipeline_version)
  -> immutable state snapshot candidate
  -> Episode association
  -> rebuildable daily view
```

重要なのは、`daily view` すら正準データではないことです。raw evidenceから作り直せるprojectionです。

## 2. 原因：便利なprojectionを先に作ると、観測事実が逆流する

「ペット目線の日記」を最初に作ると、UIとしては面白くなります。

ただし、そこから設計を逆算すると、次の混同が起きやすくなります。

```text
heard text == 本人の発言
learned word == 本人の関心
profile change == 本人の状態変化
pet log == 人間の記憶
```

どれも自動的には成立しません。

そこで、最初の設計判断を **MemoryClaimを作らない** に固定しました。

この図では、左の「ログからMemoryClaimへ直結」と、右の「ObservationとしてEpisodeへ関連付ける」の差だけを見てください。

![Observation is not MemoryClaim](/images/vrcpet-observation-source/02-observation-not-memory.webp)

実装でも `associate_episode()` は `source_object_ids` を増やすだけです。VRCPet adapter側には `MemoryClaim` を作る責務を持たせていません。

これは単なる型の好みではありません。

**観測ソースが増えたとき、どのソースに「真実を確定する権限」があるかを曖昧にしないための境界**です。

## 3. 設計判断1：read-onlyは「書き込み関数がない」だけでは足りない

外部アプリのデータディレクトリを読むadapterでは、「こちらから書き込まない」は最低条件です。

しかし、それだけでは不十分です。

実装では読み込み前に次を確認します。

1. rootを `resolve(strict=True)` する
2. allowlistが指定されていればrootがその配下か確認する
3. relative pathに絶対パスや `..` を許さない
4. 結合後の実パスがroot配下に残っているか再確認する

さらに、読み込み中にファイルが更新された場合もfail-closeにしました。

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

この図で見るべき点は、**境界確認がreadの前だけで終わっていない**ことです。read後のsize/mtime/byte lengthまで照合します。

![Read-only boundary](/images/vrcpet-observation-source/03-read-only-boundary.webp)

Pythonの `pathlib.Path.resolve()` はシンボリックリンクを解決し、`relative_to()` は指定した親パス配下にあるかを判定できます。今回の境界実装はこの標準機能を組み合わせています。

- https://docs.python.org/3.14/library/pathlib.html

### なぜここまでやるのか

ローカルアプリのログは、こちらのpipelineとは無関係に更新されます。

読み取りの途中でファイルが伸びると、次のような中途半端な状態をhash化する可能性があります。

```text
stat: 10 KB
read: 11 KB
manifest: 10 KB
hash: 途中状態
```

この状態をcanonical evidenceとして受け入れると、後で同じ入力を再現できません。

そのため、**「読めた」ではなく「安定した同一状態を読めた」ことを成功条件**にしました。

## 4. 設計判断2：壊れた1行のせいで、1日分すべてを捨てない

会話JSONLは、1行1JSON objectという扱いやすい形式です。

ただし運用ログでは、途中終了や書き込み競合で1行だけ壊れることがあります。

全面fail-closeにすると安全ですが、正常な前後行まで失います。

そこでparserは **record単位の隔離** にしました。

fixtureでは次の入力を使っています。

```text
{"text":"hello"}
{"broken":
{"text":"world"}
```

期待結果は次です。

```text
valid records = 2
parse issues  = 1
```

この図では、2行目だけが `issues` へ移り、1行目と3行目が残ることを見てください。

![Tolerant JSONL parsing](/images/vrcpet-observation-source/04-tolerant-parse.webp)

Python標準の `json.loads()` は不正なJSONで `JSONDecodeError` を送出します。adapterはそれを行単位で捕捉し、`line_number` と `raw_fragment` を監査情報として残します。

- https://docs.python.org/3.14/library/json.html

### 失敗しやすい代替案

#### 全ファイルreject

安全ですが、1行の破損で数千行の正常観測を失います。

#### エラー行を黙ってskip

利用者には綺麗なデータだけ見えますが、「何を失ったか」が監査不能になります。

#### malformed textを正常recordへ強制変換

情報は残りますが、正常データと異常データの境界が消えます。

今回の設計は、**正常recordを保持しつつ、parse issueを一級の監査対象にする**中間案です。

## 5. 設計判断3：ファイル名ではなく、raw bytesで同一性を決める

ログファイルの名前は安定したidentityではありません。

コピー、バックアップ、renameで変わるからです。

そこで `normalize_source()` はraw bytesをSHA-256へ変換し、そのdigestとobservation typeから決定的UUIDを作ります。

概念的には次です。

```python
digest = sha256(raw_bytes).hexdigest()
source_id = uuid5(namespace, f"{observation_type}:{digest}")
```

この図では、identityが `path` ではなく `raw bytes` から始まっていることを見てください。

![Content addressed SourceObject](/images/vrcpet-observation-source/05-content-addressing.webp)

Pythonの `hashlib.sha256()` はbytes列からSHA-256 digestを生成できます。

- https://docs.python.org/3.14/library/hashlib.html

`uuid.uuid5(namespace, name)` はnamespaceとnameから決定的なUUIDを生成します。

- https://docs.python.org/3.14/library/uuid.html

ここで注意点があります。

UUIDv5自身はSHA-1ベースです。しかしこの実装で**content integrityを表すのはSHA-256 digest**です。UUIDv5は、そのdigestを安定したIDへ写像するために使っています。

つまり役割は分離しています。

```text
SHA-256 = content fingerprint
UUIDv5  = deterministic identifier
```

## 6. プライバシー境界：`C:\Users\...` をmanifestへ入れない

privateデータを扱うpipelineでありがちな事故が、内容ではなく **pathの漏えい** です。

たとえば次のような情報です。

```text
C:\Users\alice\AppData\Roaming\...
```

これだけでユーザー名、OS、ディレクトリ構成が外へ出ます。

今回のmanifestは、absolute pathを持ちません。

残すのはsource rootからのrelative pathです。

```json
{
  "metadata": {
    "source": "vrcpet",
    "observation_type": "conversation",
    "source_relative_path": "logs/2026-08-12.jsonl"
  }
}
```

object URIもprivate namespaceにします。

```text
private://vrcpet/conversation/sha256/<digest>
```

この図では、「実環境の場所」と「canonical manifestへ持ち出してよい情報」の境界を見てください。

![Privacy boundary](/images/vrcpet-observation-source/06-privacy-boundary.webp)

回帰テストではmanifest全体を文字列化し、`C:\Users\` が含まれないことまで検証しています。

## 7. 冪等性：renameされても同じ観測を二重登録しない

content addressingの効果は、テストにすると分かりやすくなります。

同じbytesを別名で渡します。

```text
logs/a.jsonl       -> {"text":"same"}
logs/renamed.jsonl -> {"text":"same"}
```

期待するのは、同じSourceObject IDと同じsource hashです。

この図では、2本の異なるpathが同じIDへ収束する点を見てください。

![Idempotent ingest](/images/vrcpet-observation-source/07-idempotency.webp)

さらにingestion側のidempotency keyは、概念的に次です。

```text
source_hash + pipeline_version
```

これにより、

- 同じsourceを同じpipelineで再実行 → 同じ処理
- 同じsourceでもpipeline versionが変化 → 再評価可能

という境界を作れます。

ファイル名や取得日時をidentityにすると、同一内容の再発見だけで重複が増えます。content hashを中心に置くと、その問題を避けられます。

## 8. 状態データは「現在値だけ」にしない

`profile.json` や `heard_nouns.json` はイベントログではなく状態です。

現在値だけ保持すると、次の問いに答えられません。

- 何が新しく増えたか
- 何が減ったか
- いつ変わったか
- parserの変更で見え方が変わっただけなのか

そこでexact raw bytesを保持するimmutable snapshot candidateを作り、差分を別に計算します。

この図では、「今日の値で昨日を上書き」していない点を見てください。

![Snapshot and diff](/images/vrcpet-observation-source/08-snapshot-diff.webp)

profile diffは次を分離します。

```text
added
removed
changed
```

vocabulary diffは次です。

```text
new
increased
decreased
missing
```

この分類を明示した理由は、たとえば「消えた語」を単純にcount=0へ変換しないためです。

**missingとzeroは意味が違います。**

vendor側schemaが変わった、ファイルが部分的だった、projectionが拾えなかった、という可能性を残す必要があります。

## 9. Episodeへ束ねても、MemoryClaimへは昇格しない

Human Memory側には、音声、画像、文書、会話など複数ソースがあります。

VRCPetもその1つとしてEpisodeに関連付けます。

この図では、複数センサーが同じEpisodeへ集約されても、VRCPet観測だけでMemoryClaimを作らないことを見てください。

![Episode association without MemoryClaim](/images/vrcpet-observation-source/09-episode-no-claim.webp)

たとえば同じ1時間について、次が存在するかもしれません。

```text
primary audio
VRCPet conversation observation
profile snapshot
vocabulary snapshot
```

これらは同じ出来事を説明する証拠にはなります。

しかし、証拠が同じEpisodeに属することと、1つの事実を確定することは別です。

この分離があると、将来別のセンサーを増やしても、勝手に「真実」が増えません。

## 10. 最終成果物は「日記」ではなく、何度でも作り直せるview

このadapterには、`すいの目から見た1日` というdaily projectionがあります。

出力例は次のような情報を含みます。

```text
会話観測件数
operational observation件数
state snapshot件数
parse issue件数
よく聞いた言葉
新しく覚えた言葉
強くなった言葉
弱くなった/消えた言葉
ペット側の発話
profile変化
```

ここで重要なのは、このMarkdownを正準データにしていないことです。

この図では、daily viewがpipelineの終端にあり、raw evidenceから再生成できることを見てください。

![Rebuildable daily projection](/images/vrcpet-observation-source/10-rebuildable-view.webp)

E2E fixtureでは、意図的に壊れたconversationを含む入力から次を確認しています。

```text
conversation records = 2
parse issues          = 1
snapshots             = 2
```

そのうえでrendered Markdownに、頻出語、profile変化、pet utteranceが再現されることをテストしています。

## 11. 検証：成功条件を「動いた」ではなく境界ごとに置く

今回の実装で重要だった回帰テストを整理すると次です。

| 境界 | テストすること |
| --- | --- |
| parser | malformed JSONLの前後の正常recordを失わない |
| input boundary | allowlist外rootを拒否する |
| path boundary | `..` によるescapeを拒否する |
| stable read | 読み取り中にsourceが変化したらrejectする |
| discovery | 既知の4系統以外を勝手に収集しない |
| identity | 同じbytesならrename後も同じIDになる |
| privacy | Windows absolute pathをmanifestへ残さない |
| idempotency | duplicate ingestを1観測へ縮約する |
| snapshot | exact bytesを保持し、diffを明示する |
| semantic boundary | Episode associationしてもMemoryClaimを作らない |
| E2E | evidenceからdaily viewを再構築できる |

mainのmerge commitに対して、GitHub Actionsの `Lint` と `Test and Security Audit` はともにsuccessになっています。

- Lint: https://github.com/KAFKA2306/vlog/actions/runs/31557522611
- Test and Security Audit: https://github.com/KAFKA2306/vlog/actions/runs/31557522419

## 12. 失敗：最初からvendor schemaを正準化しない

この種のadapterで特に避けたかった失敗は、観測したvendor構造をそのまま自分のdomain schemaにすることです。

たとえば `heard_nouns.json` では、実際に次のようなnested shapeが観測されています。

```text
words
  └─ <term>
       ├─ count
       ├─ kind
       └─ unknown fields...
```

ここで `count` だけ必要だからといって、

```text
VocabularyTerm {
  name
  count
}
```

をvendorの正式仕様だと仮定すると、将来field構造が変わったときに壊れます。

実装では、unknown fieldを「不要だから消す」のではなく、raw sourceへ残します。projection側だけが現在観測できる `count` を読む設計です。

**観測したshapeと、保証されたAPI contractは別物です。**

これはログadapter全般で使える考え方です。

## 13. 再現方法：最小fixtureで境界を追試する

この設計は実データを公開しなくても追試できます。

### 前提

- Python環境
- `KAFKA2306/vlog` のcheckout
- 実データではなくsynthetic fixtureを使う

repository:

https://github.com/KAFKA2306/vlog

### 1. adapterの対象を確認する

```bash
ls adapters/vrcpet
```

確認対象:

```text
reader.py
parser.py
normalizer.py
snapshot.py
daily_view.py
README.md
```

### 2. malformed JSONLを作る

```text
{"text":"hello"}
{"broken":
{"text":"world"}
```

期待値:

```text
records == 2
issues == 1
```

### 3. 同じbytesを別名でnormalizeする

```text
logs/a.jsonl
logs/renamed.jsonl
```

期待値:

```text
source id: equal
source hash: equal
```

### 4. path escapeを試す

```text
../outside/profile.json
```

期待値:

```text
SourceBoundaryError
```

### 5. sourceをread中に変更する

read直後にfixtureへ1byte追加するようmonkeypatchします。

期待値:

```text
UnstableSourceError
```

### 6. E2E testを実行する

repositoryの通常test手順で `tests/test_vrcpet_adapter.py` を含むsuiteを実行します。

実装済みfixtureでは、壊れたJSONLを含んだ状態からdaily projectionまで再構築します。

## 14. この設計を他のログ取り込みへ転用する

今回の本質はVRChatでもペットでもありません。

次のようなローカルアプリにも同じ境界を使えます。

- ブラウザ履歴
- 音声文字起こし
- ゲームログ
- IDE操作ログ
- wearable device export
- 個人メモアプリの変更履歴

共通する設計原則は次です。

```text
1. sourceはread-only
2. raw bytesを先にhash化
3. pathではなくcontentでidentityを作る
4. parser errorを監査可能に残す
5. vendor schemaをcanonical schemaと同一視しない
6. private locationをmanifestへ漏らさない
7. stateはsnapshot + diff
8. observationとclaimを分離する
9. viewはrebuildableにする
```

## まとめ

ローカルアプリのログをHuman Memoryへ接続するとき、難しいのはparserではありません。

**「そのデータは何を意味してよいのか」を決めることです。**

今回もっとも効いた判断は、最初に `VRCPet log != MemoryClaim` と決めたことでした。

その結果、read-only、stable-read、content addressing、privacy-safe manifest、idempotency、snapshot、Episode association、rebuildable projectionという境界を、後から継ぎ足すのではなく最初から一貫して設計できました。

ペットが聞いたことは、面白い観測です。

しかし、**面白い観測であることと、真実として保存してよいことは別です。**

この区別を型とテストで残しておくと、センサーが増えても記憶基盤の意味は壊れにくくなります。

## 参考資料

実装一次証拠:

- https://github.com/KAFKA2306/vlog/pull/28
- https://github.com/KAFKA2306/vlog/commit/46884310417d17dd71f544741795a2490eb354ad
- https://github.com/KAFKA2306/vlog/blob/main/adapters/vrcpet/README.md
- https://github.com/KAFKA2306/vlog/blob/main/adapters/vrcpet/reader.py
- https://github.com/KAFKA2306/vlog/blob/main/adapters/vrcpet/parser.py
- https://github.com/KAFKA2306/vlog/blob/main/adapters/vrcpet/normalizer.py
- https://github.com/KAFKA2306/vlog/blob/main/adapters/vrcpet/snapshot.py
- https://github.com/KAFKA2306/vlog/blob/main/adapters/vrcpet/daily_view.py
- https://github.com/KAFKA2306/vlog/blob/main/tests/test_vrcpet_adapter.py

Python公式ドキュメント:

- https://docs.python.org/3.14/library/hashlib.html
- https://docs.python.org/3.14/library/uuid.html
- https://docs.python.org/3.14/library/json.html
- https://docs.python.org/3.14/library/pathlib.html
