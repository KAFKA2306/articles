---
title: "一括同期でコードが壊れた。6ファイルだけ戻して「壊れたら止まる」門番を置いた"
emoji: "🧯"
type: "tech"
topics: ["python", "githubactions", "testing", "ci"]
published: false
published_at: 2026-08-13 11:00
---

大規模な置換や同期処理は、差分がきれいに見えても安全とは限りません。

`KAFKA2306/2510youtuber` では、2026年2月11日のglobal sync後に、複数のPythonファイルで文字列リテラルが壊れていました。2026年8月13日の修復PRでは、現在の `main` を丸ごと過去へ戻すのではなく、壊れていた6ファイルだけをsync直前のblobへ戻し、その後に依存追加なしのsyntax gateを通しています。

この記事では、この修復を「古いcommitへ戻した成功談」ではなく、**広範囲変更のあとに、壊れた最小単位だけを復元し、Python標準機能で再発をCIに固定する方法**として分解します。

## 1. 問題：bulk rewriteは「差分が適用できた」と「Pythonとして有効」を別々に壊す

実際に壊れていた `app/metadata.py` の一部では、長い説明文を組み立てる文字列の終端が欠け、次のような状態になっていました。

```python
enhanced += '\n\n⚠️ 免責事項：\n本動画の内容は情報提供を目的としており、投資勧誘ではありません。\n投資判断は自己責任で行ってください。\n\n
return enhanced
```

この形は、レビュー画面では「長い日本語文字列の一部」に埋もれやすい一方、Python parserにとってはsyntax errorです。

同repoの修復PR #65では、文字列リテラルが壊れた対象として次の6ファイルが明示されています。

```text
app/background_theme.py
app/crew/agent_review.py
app/discord.py
app/metadata.py
app/metadata_storage.py
app/youtube.py
```

ここで重要なのは、**壊れたのが6ファイルだからrepo全体を昔の状態へ戻したわけではない**ことです。修復branchは当時の最新 `main` を基点にし、この6 blobだけをglobal sync直前のcommit `bd64002387cfd348afc7465fee8ac588d708c34b` から復元しました。

一次情報:

- 修復PR: https://github.com/KAFKA2306/2510youtuber/pull/65
- 壊れていた `metadata.py` の修復前状態: https://github.com/KAFKA2306/2510youtuber/blob/1dfabc3c3e3ba30780cf01a9b794c432a7166a81/app/metadata.py

## 2. 原因：text-levelの成功条件だけではlanguage-levelの破損を検出できない

bulk sync、formatter、codemod、AIによる一括修正などは、最終的にはテキストを書き換えます。

しかし「全対象ファイルを書き換えられた」「conflict markerが残っていない」「git diffが生成された」は、Pythonとしてparseできることを保証しません。

検査レイヤを分けると分かりやすくなります。

```text
text operation succeeded
        ↓
git diff exists
        ↓
merge conflict marker absent
        ↓
Python parser accepts every source file
        ↓
imports / tests / runtime behavior
```

今回抜けていたのは、少なくとも **Python parser accepts every source file** の固定ゲートです。

これはunit testの不足とは少し違います。syntax errorは、対象moduleをtestがimportしなければ見逃すことがあります。一方、全 `.py` をcompileする検査なら、実行経路に入っていないファイルも対象にできます。

## 3. 設計判断と代替案：repo全体rollbackではなく「最新main + 壊れたblobだけ復元」

復旧方法には少なくとも3案あります。

### 案A：global sync commitを丸ごとrevertする

利点は単純なことです。しかしsync後に積み上がった正常な変更まで巻き戻す可能性があります。

今回のPRはこの方法を採りませんでした。

### 案B：6ファイルを手編集してquoteだけ直す

変更量は最小に見えますが、長い文字列やescape sequenceが複数箇所壊れている場合、手作業で「元の意味」まで復元できたかを別途確認する必要があります。

### 案C：最新mainを保ち、壊れた6ファイルだけsync直前のblobへ戻す

今回採用されたのはこれです。

```text
latest main
  ├─ healthy files: keep current versions
  └─ corrupted 6 files: restore pre-sync blobs
```

この方法なら、修復対象をPR上で明示でき、正常な後続変更をrepo全体ごと失うリスクを抑えられます。

ただし、blob restore自体も「正しいPythonへ戻った」ことを自動では保証しません。そこで次のsyntax gateを組み合わせます。

## 4. 実装：標準ライブラリの `compileall` を最初の門番にする

`2510youtuber` の現行workflow `Python syntax safety` は、Python 3.11をsetupしたあと、次の3段階を実行しています。

```yaml
- name: Validate pyproject
  run: python -c "import pathlib,tomllib; tomllib.loads(pathlib.Path('pyproject.toml').read_text(encoding='utf-8'))"

- name: Reject merge conflict markers
  shell: bash
  run: |
    if git grep -nE '^(<<<<<<<|=======|>>>>>>>)' -- '*.py' '*.toml' '*.yml' '*.yaml'; then
      echo 'Unresolved merge conflict markers found.' >&2
      exit 1
    fi

- name: Compile Python sources
  run: python -m compileall -q app tests
```

一次情報:

- 実装workflow: https://github.com/KAFKA2306/2510youtuber/blob/main/.github/workflows/python-syntax-safety.yml
- Python `compileall` 公式ドキュメント: https://docs.python.org/3/library/compileall.html
- Python `py_compile` 公式ドキュメント: https://docs.python.org/3/library/py_compile.html

Python公式ドキュメントでは、`compileall` はdirectory tree内のPython sourceをcompileするための標準モジュールとして提供されています。個別ファイルを扱う `py_compile` は、compileできない場合にnonzero exitを返すCLIとしても利用できます。

今回の用途で重要なのは、アプリ依存をinstallしなくても、少なくともsourceの構文破損を早期に落とせる点です。

### なぜ `pytest` だけにしないのか

`pytest` が十分なrepoもあります。しかしsyntax gateは役割が違います。

```text
compileall: source treeがPythonとしてparse可能か
pytest:     実装の期待動作を満たすか
```

重いdependency installや外部service fixtureより先に `compileall` を走らせると、壊れたquoteのような低レイヤの失敗を安価に切り分けられます。

## 5. 検証：修復PRのheadでsyntax workflowがsuccessになった

修復PR #65 のhead commitは `331d89ca8fdc61521045e0d20561966b4b603822` です。

このcommitに対する `Python syntax safety` workflow run #3 は `success` で完了しています。

- PR: https://github.com/KAFKA2306/2510youtuber/pull/65
- head commit: https://github.com/KAFKA2306/2510youtuber/commit/331d89ca8fdc61521045e0d20561966b4b603822
- workflow: https://github.com/KAFKA2306/2510youtuber/actions/workflows/python-syntax-safety.yml

ここで言えるのは「6ファイルを復元したheadが、追加したsyntax safety workflowを通過した」までです。syntax checkがbusiness logicの正しさまで証明するわけではありません。

この境界を明示しておくと、CI successを過大評価しません。

## 6. 失敗と学び：syntax errorを見つけてからgateを足すのでは遅い

今回の壊れた例から得られる最も再利用しやすい学びは、**bulk rewriteの安全性を、rewrite tool自身の成功判定に任せない**ことです。

### 壊れた失敗例

```python
text = 'line 1\nline 2
print(text)
```

編集ツール側は「2行を書き換えた」と成功を返せます。しかしPythonとしては失敗です。

### 改善後の例

```bash
python -m compileall -q app tests
```

これをpull requestごとの必須checkにすると、少なくとも構文破損はmerge前に検知できます。

さらに、今回のworkflowはmerge conflict markerも別途検査しています。

```bash
git grep -nE '^(<<<<<<<|=======|>>>>>>>)' -- '*.py' '*.toml' '*.yml' '*.yaml'
```

compileできるかどうかと、conflict markerが残っていないかは別問題なので、検査も分ける方が失敗理由を読みやすくできます。

### 学び1：rollback単位をrepoではなく破損単位にする

「いつ壊れたか」が分かっていても、その時点へrepo全体を戻す必要はありません。最新mainを基点に、証拠のある破損blobだけを復元できます。

### 学び2：syntax gateはdependency-freeに近いほど前段へ置ける

依存installが必要なtest suiteより前に標準ライブラリだけのcheckを置けば、問題の切り分けが早くなります。

### 学び3：CI successの意味を狭く書く

`compileall` successは「Python parserが対象sourceを受理した」という証拠です。「動画生成機能が正常」や「API連携が正常」まで広げてはいけません。

## 7. 再現方法：5分でbulk-edit向けsyntax gateを追加する

読者が試せる最小例です。

### Step 1: 壊れたファイルを作る

```bash
mkdir -p demo
cat > demo/broken.py <<'PY'
message = 'hello
print(message)
PY
```

### Step 2: `compileall` を実行する

```bash
python -m compileall -q demo
```

syntax errorがあるため成功しません。

### Step 3: 修正する

```bash
cat > demo/broken.py <<'PY'
message = 'hello'
print(message)
PY
python -m compileall -q demo
```

今度はcompileできます。

### Step 4: GitHub Actionsへ固定する

```yaml
name: Python syntax safety

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  syntax:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: '3.11'
      - name: Reject conflict markers
        run: |
          if git grep -nE '^(<<<<<<<|=======|>>>>>>>)' -- '*.py' '*.toml' '*.yml' '*.yaml'; then
            exit 1
          fi
      - name: Compile Python sources
        run: python -m compileall -q app tests
```

GitHub Actionsのworkflow syntax自体は公式ドキュメントで確認できます。

- https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions

## まとめ

bulk syncやAI一括修正で怖いのは、変更量の大きさそのものではありません。

**「書き換え処理が成功した」という事実と、「言語として有効なsourceが残った」という事実を同じ成功判定にしてしまうこと**です。

今回の修復では、最新mainを維持したまま壊れた6ファイルだけをsync直前のblobへ戻し、その結果をdependency-freeなsyntax gateで検証しました。

再利用するなら、次の順序が最小です。

```text
bulk edit
→ conflict marker check
→ compileall
→ unit/integration tests
→ runtime validation
```

`compileall` は地味ですが、bulk rewriteの直後に置くにはちょうどよい門番です。
