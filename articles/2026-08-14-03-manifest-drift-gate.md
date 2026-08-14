---
title: "再生成できるmanifestほど差分で守る"
emoji: "🧾"
type: "tech"
topics: ["python", "githubactions", "dataengineering", "testing", "ci"]
published: false
---

生成物をGit管理していると、CIで「もう一度生成して成功した」だけで安心したくなります。

しかし、manifestのような**生成物そのものが契約**になっている場合、それでは不十分です。元データだけ更新してmanifestを更新し忘れても、CIが最初にmanifestを再生成してしまえば、その不整合を自分で消してから検証できてしまうからです。

この記事では、公開GitHub上の実装を題材に、次の2つを分離する設計を整理します。

1. **artifactの内容がmanifestに記録されたSHA-256・byte sizeと一致するか**
2. **PRにcommitされたmanifestが、現在の入力から再生成した結果と一致するか**

結論は単純です。

> **生成物の正しさと、生成物をcommitし忘れていないことは別の性質なので、別々にfail-closeで検証する。**

## 問題：再生成が「古いmanifest」を隠してしまう

たとえば、次の3ファイルを1つのmanifestで束ねるとします。

```text
data/events.ndjson
data/audit.json
data/state.json
```

manifestには各artifactのpath、SHA-256、byte sizeを保存します。

```json
{
  "status": "PASS",
  "artifacts": [
    {
      "path": "data/events.ndjson",
      "sha256": "...",
      "size_bytes": 1234
    }
  ]
}
```

ここで `events.ndjson` だけ更新し、manifestの更新を忘れたとします。

壊れたCIは次の順です。

```text
checkout
  ↓
manifestを再生成
  ↓
再生成後manifestを検証
  ↓
PASS
```

この流れでは、checkout直後に存在した「artifactは新しいのにmanifestは古い」という状態が消えています。

実際の公開実装 `KAFKA2306/semiconductor-earnings-model` では、`build_earnings_lineage_manifest.py` が複数artifactからSHA-256とbyte sizeを計算して `lineage_latest.json` を生成し、workflowはその後にmanifestを検証します。PRでは最後に `git diff --exit-code -- data/earnings_ledger/lineage_latest.json` を実行し、再生成によって差分が出た場合を失敗にします。

一次情報:

- https://github.com/KAFKA2306/semiconductor-earnings-model/blob/7595f0b0b7f7535d9eaea182fe5f2ba415bce8f4/scripts/build_earnings_lineage_manifest.py
- https://github.com/KAFKA2306/semiconductor-earnings-model/blob/7595f0b0b7f7535d9eaea182fe5f2ba415bce8f4/.github/workflows/earnings-lineage.yml

## 原因：2種類の不整合を1つの検査だと思ってしまう

manifest運用には、少なくとも2種類の失敗があります。

### 1. manifestとartifactの不整合

manifestに記録されたdigestやsizeと、実ファイルが一致しない状態です。

これはverifierで検出できます。

```text
manifest.sha256 != sha256(file bytes)
manifest.size_bytes != len(file bytes)
```

### 2. repository stateと再生成結果の不整合

manifest自体は構文的に正しくても、現在の入力から作り直すと内容が変わる状態です。

これは「manifestを検証する」だけではなく、**再生成後にGit差分を見る**ことで検出できます。

```text
committed manifest
      ↓
rebuild from current inputs
      ↓
git diff --exit-code
```

この2つは似ていますが、守っている対象が違います。

- verifier: **manifestが指しているbytesは本当にそのbytesか**
- diff gate: **PRは現在のbytesに対応するmanifestまでcommitしたか**

## 設計判断：builder、verifier、repository diffを分離する

公開実装では役割が3つに分かれています。

### builder

`build_earnings_lineage_manifest.py` はrequired artifactを列挙し、欠損を拒否したうえで、それぞれのSHA-256とbyte sizeを計算します。

さらに、単にhashを作るだけではなく、複数のaudit artifactが同じrunに結びついていることや、audit statusが `PASS` であることも確認します。

つまりbuilderは、**どのartifact集合を1つのlineageとして認めるか**を定義しています。

### verifier

`verify_earnings_lineage_manifest.py` はmanifestを入力として読み、各artifactをrepository bytesから再計算します。

公開実装で拒否される条件には次が含まれます。

- manifestのstatusが `PASS` ではない
- artifactsが空
- 同じpathが重複
- SHA-256が64桁の小文字hexではない
- `size_bytes` が非整数または負数
- artifact pathがrepository rootの外へ出る
- manifest自身をartifactとしてbindする
- artifactが存在しない
- SHA-256 mismatch
- byte size mismatch

一次情報:

- https://github.com/KAFKA2306/semiconductor-earnings-model/blob/7595f0b0b7f7535d9eaea182fe5f2ba415bce8f4/scripts/verify_earnings_lineage_manifest.py

Python標準ライブラリの `hashlib` は `sha256()` にbytesを渡してdigestまたはhex digestを得るインターフェイスを提供しています。上記実装もartifactをbytesとして読み、`hashlib.sha256(payload).hexdigest()` で再計算しています。

一次情報:

- https://docs.python.org/3/library/hashlib.html

### repository diff gate

workflowはmanifestを再生成・検証したあと、pull requestでのみ次を実行します。

```bash
git diff --exit-code -- data/earnings_ledger/lineage_latest.json
```

ここで差分があれば、builderが生成した正しいmanifestをまだPRへcommitしていないことになります。

重要なのは、**再生成を禁止するのではなく、再生成して差分が出ないことを契約にする**点です。

## 代替案と落とし穴

### 代替案A：CIで毎回生成してartifactとしてだけ保存する

repositoryにmanifestをcommitしない設計なら成立します。

ただし、manifestをcode reviewの対象にしたい、commit単位でlineageを追いたい、repository checkoutだけで状態を復元したい場合は別です。その場合、commitされたmanifestと生成結果の一致が必要になります。

### 代替案B：manifestのschemaだけ検証する

path、digest、sizeの型が正しいことは確認できますが、実ファイルとの一致は確認できません。

```json
{
  "sha256": "0000...0000",
  "size_bytes": 1234
}
```

のような値でも形式だけなら通ります。

### 代替案C：hashだけ確認する

内容同一性の主検査としてSHA-256は有効ですが、公開実装はbyte sizeも別に保持して照合しています。これはmanifestの可読な整合性情報を増やし、hash mismatchとsize mismatchを別の診断として出せます。

### 採用する形：3層にする

```text
入力artifactの意味的条件
        ↓ builder
manifest生成
        ↓ verifier
bytesとのbinding確認
        ↓ diff gate
commit漏れ確認
```

1つの巨大なscriptへまとめるより、「何が壊れたか」が分かりやすくなります。

## 実装：最小構成を作る

以下は考え方を再現する最小例です。

### builder

```python
import hashlib
import json
from pathlib import Path

ROOT = Path(".")
TARGETS = [Path("data/a.txt"), Path("data/b.txt")]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

manifest = {
    "status": "PASS",
    "artifacts": [
        {
            "path": path.as_posix(),
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        }
        for path in TARGETS
    ],
}

Path("data/manifest.json").write_text(
    json.dumps(manifest, indent=2) + "\n",
    encoding="utf-8",
)
```

### verifier

```python
import hashlib
import json
from pathlib import Path

manifest = json.loads(Path("data/manifest.json").read_text())

for item in manifest["artifacts"]:
    path = Path(item["path"])
    payload = path.read_bytes()
    assert hashlib.sha256(payload).hexdigest() == item["sha256"]
    assert len(payload) == item["size_bytes"]
```

### CI

説明用workflow stagesとしては次の順です。

```text
1. test builder / verifier
2. rebuild manifest
3. verify rebuilt manifest against repository bytes
4. on pull request, require git diff to be empty for manifest
```

GitHub上の公開実装もこの順で、test → build → verify → artifact upload → PRでmanifest差分確認、というstageを持っています。

## 検証：壊れた失敗例を作る

最小例で `data/a.txt` とmanifestを生成したあと、`a.txt` だけ変更します。

```bash
printf 'v1\n' > data/a.txt
python build_manifest.py
git add data/a.txt data/manifest.json
git commit -m 'initial'

printf 'v2\n' > data/a.txt
```

### verifierを先に実行する場合

古いmanifestをそのまま検証すれば、SHA-256 mismatchで停止します。

### builderを先に実行する場合

```bash
python build_manifest.py
python verify_manifest.py
```

ここだけを見るとPASSします。builderが新しい `a.txt` に対応するhashへmanifestを書き換えたからです。

しかし続けて、

```bash
git diff --exit-code -- data/manifest.json
```

を実行すれば差分があるため失敗します。

これが今回の中心です。

> **再生成後の検証が成功したことと、PRが必要な生成物をcommit済みであることは同義ではない。**

## 改善後の例

正しい変更では、入力artifactとmanifestを一緒に更新します。

```bash
printf 'v2\n' > data/a.txt
python build_manifest.py
python verify_manifest.py
git add data/a.txt data/manifest.json
git commit -m 'update data and manifest'
```

CIで再度builderを実行してもmanifestは変わらないため、

```bash
git diff --exit-code -- data/manifest.json
```

は0で終了します。

この状態なら、少なくとも次の3条件が揃っています。

- artifact bytesとmanifest bindingが一致する
- manifestを現在の入力から決定的に再生成できる
- PRに必要なmanifest更新が含まれている

## 失敗と学び：生成物は「CIで作れた」だけでは管理できない

生成物には2種類あります。

1. repositoryに残さず、CI artifactとして毎回作ればよいもの
2. repository stateの一部としてcommitし、review・履歴・再現性に使うもの

後者を選んだなら、生成scriptが成功することだけでは品質条件になりません。

必要なのは、**checkoutされたcommitが自己完結していること**です。

そのため、commit管理するmanifestでは次を分けて考えると設計しやすくなります。

```text
生成可能性
  builderが成功する

内容整合性
  verifierが実bytesとのbindingを確認する

repository整合性
  rebuildしてもgit diffが出ない
```

## 読者が試せる再現方法

小さなrepositoryで次の4ファイルを作ります。

```text
data/a.txt
build_manifest.py
verify_manifest.py
data/manifest.json
```

1. `a.txt` を作る
2. builderでmanifest生成
3. 全ファイルをcommit
4. `a.txt` だけ変更
5. builder → verifierを実行してPASSすることを確認
6. `git diff --exit-code -- data/manifest.json` が失敗することを確認
7. manifestもcommitする
8. 同じCIを再実行し、diffが空になることを確認

これで「生成結果の正しさ」と「commitの完全性」が別問題であることを数分で再現できます。

## まとめ

manifestを生成できることは重要ですが、生成できるからこそCIが不整合を消してしまうことがあります。

commit管理するmanifestでは、少なくとも次の3層を分けます。

- builderで正準manifestを決定的に生成する
- verifierでmanifestと実artifact bytesを照合する
- PRでは再生成後にGit差分がないことを確認する

特に最後のdiff gateは地味ですが、**「入力は更新したのに生成物をcommitし忘れた」**という実務で頻出する失敗を、レビュー前に機械的に止められます。

### 主要一次情報

- https://github.com/KAFKA2306/semiconductor-earnings-model/pull/101
- https://github.com/KAFKA2306/semiconductor-earnings-model/blob/7595f0b0b7f7535d9eaea182fe5f2ba415bce8f4/scripts/build_earnings_lineage_manifest.py
- https://github.com/KAFKA2306/semiconductor-earnings-model/blob/7595f0b0b7f7535d9eaea182fe5f2ba415bce8f4/scripts/verify_earnings_lineage_manifest.py
- https://github.com/KAFKA2306/semiconductor-earnings-model/blob/7595f0b0b7f7535d9eaea182fe5f2ba415bce8f4/.github/workflows/earnings-lineage.yml
- https://docs.python.org/3/library/hashlib.html
