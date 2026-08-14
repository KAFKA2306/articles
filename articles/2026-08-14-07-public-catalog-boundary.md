---
title: "公開カタログに個人予定を混ぜない"
emoji: "🧱"
type: "tech"
topics: ["dataengineering", "privacy", "github", "testing"]
published: false
---

公開サイトに載せたいのは作品情報だけなのに、運用を続けると別のデータが近づいてくる。

「この作品は9人用」「所要時間は180〜210分」という公開メタデータの隣に、参加者、通過状況、開催予定、内部メモまで置き始めると、実装上は扱いやすい。1つのJSONにまとめれば検索もしやすい。

でも、その便利さは公開境界を壊す。

2026年8月14日、`KAFKA2306/boardgamelist` に3作品の公式メタデータを追加したcommitでは、同時に「October 2026 BlueBirdStore play plans」を扱いながら、commit messageで **`keep private play plans out of public catalog`** と明示していた。

- commit: https://github.com/KAFKA2306/boardgamelist/commit/9ce9aa8c7eab27b650dd06a478c21319949dc575

そのとき、公開側へ入った『アポロンの審判』の正準JSONはこうなっている。

```json
{
  "source": {
    "source_kind": "creator-official-marketplace",
    "access_condition": "public-web"
  },
  "edition": {
    "players": 9,
    "gm_required": true,
    "duration_minutes_min": 180,
    "duration_minutes_max": 210
  }
}
```

- metadata: https://github.com/KAFKA2306/boardgamelist/blob/9ce9aa8c7eab27b650dd06a478c21319949dc575/data/official-metadata/apollo-no-shinpan-2026-08-14.json

公開ページ側も、単に「書かなかった」ではなく境界を文章で固定している。

> 公開可能な作品メタデータだけを扱い、シナリオの真相、役職・個別情報、参加者、通過状況、個人の予定は保存しない。

- public page: https://github.com/KAFKA2306/boardgamelist/blob/9ce9aa8c7eab27b650dd06a478c21319949dc575/docs/games/apollo-no-shinpan.md

ここで面白かったのは、**privacy対策を「あとで消す工程」にしなかったこと**だった。

公開物を作る前に、公開可能なデータだけで別のprojectionを作る。その結果、公開側のコードは「秘密を隠す」必要がなくなる。

この記事では、この設計を一般化する。

## 1つのデータモデルに全部入れる方が楽だった

最初に考えやすい構造はこれだ。

```text
Game
├─ title
├─ players
├─ duration
├─ source_url
├─ participants
├─ played_by
├─ planned_at
└─ private_note
```

内部ツールだけなら、かなり便利である。

検索対象も1つ、joinも少ない。UIも1モデルを読めば済む。

しかし同じモデルをpublic site generatorへ渡すと、毎回「どのfieldを落とすか」が必要になる。

```python
def to_public(game):
    return {
        "title": game["title"],
        "players": game["players"],
        "duration": game["duration"],
        # participants は出さない
        # planned_at は出さない
        # private_note は出さない
    }
```

一見安全そうだが、これはdenylist型の運用になる。

新しいprivate fieldが追加されたとき、公開変換側の修正を忘れれば漏れる。

壊れた例はこうだ。

```python
def to_public(game):
    return dict(game)  # 新fieldも全部流れる
```

あるいは、より現実的にはこうなる。

```python
PUBLIC_BLOCKLIST = {"participants", "private_note"}

public = {
    key: value
    for key, value in game.items()
    if key not in PUBLIC_BLOCKLIST
}
```

後から `planned_at` や `passed_by` が増えれば、blocklist更新漏れが公開事故になる。

## 設計判断を逆にした

`boardgamelist` の公開メタデータは、最初から `public-web` の証拠だけで構成されている。

```text
creator-official marketplace
        ↓
public-web metadata
        ↓
official-metadata JSON
        ↓
spoiler-free public page
```

この構造なら、公開generatorへ渡す入力自体がpublic-safeである。

実装としては、private dataから不要fieldを削るのではなく、公開可能なfieldを正準schemaへ昇格させる。

```python
PUBLIC_FIELDS = {
    "name",
    "players",
    "gm_required",
    "gm_count",
    "duration_minutes_min",
    "duration_minutes_max",
    "play_environment",
    "pc_recommended",
}


def build_public_metadata(source_record):
    return {
        key: source_record[key]
        for key in PUBLIC_FIELDS
        if key in source_record
    }
```

重要なのは、このコード断片そのものではない。

**公開側のデフォルトを「全部出す」から「承認したものだけ出す」へ変えること**である。

## なぜ「あとで消す」では遅いのか

GitHub公式ドキュメントでは、public repositoryはインターネット上の誰でもアクセスできると説明されている。

- https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories

さらに、機密情報をcommitした後の除去は単純なfile deleteでは終わらない。GitHubの公式手順はhistory rewrite、cloneやforkへの対応、cached viewやPR参照への対応まで必要になり得ると説明している。

- https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository

つまり、public repoでのprivacy設計は「公開画面に表示されたか」だけで判定できない。

```text
private value
   ↓
commit history      ← ここに入った時点で問題になり得る
   ↓
generated artifact
   ↓
public page
```

だから、最終HTMLで隠すより前に、repositoryへ入れるprojectionを分ける価値がある。

## allowlistだけでも足りない

ここで1つ注意がある。

`PUBLIC_FIELDS` を作れば自動的に安全になるわけではない。

たとえば `notes` というfieldは名前だけではpublicかprivateか分からない。

```json
{
  "notes": "BOOTH公式商品ページで確認した公開メタデータのみを記録。ネタバレ本文は保存しない。"
}
```

今回の公開JSONでは、この`notes`自体が公開方針の説明であり、private情報ではない。

しかし別システムで同じfield名に担当者メモが入れば、allowlistに入れた瞬間に漏れる。

そのため、field名だけでなく **provenance** も必要になる。

```json
{
  "source": {
    "url": "...",
    "source_kind": "creator-official-marketplace",
    "access_condition": "public-web"
  }
}
```

公開対象を次の積で決める。

```text
approved field
AND
public provenance
AND
publication-safe value
```

この3条件を満たすものだけをpublic projectionへ送る。

## CIで守るなら何を検査するか

この境界は人間の注意力だけに置かない方がよい。

最低限、次をtestにできる。

```python
FORBIDDEN_PUBLIC_KEYS = {
    "participants",
    "played_by",
    "passed_by",
    "planned_at",
    "private_note",
}


def assert_public_record(record):
    leaked = FORBIDDEN_PUBLIC_KEYS & record.keys()
    assert not leaked, f"private keys in public record: {sorted(leaked)}"
    assert record["source"]["access_condition"] == "public-web"
```

さらにpublic artifact全体を走査する。

```python
for path in public_artifacts():
    record = load_json(path)
    assert_public_record(record)
```

ただし、このtestも万能ではない。

秘密が `title` に誤って貼り付けられればkey検査では検出できない。PII detectorも誤検知・見逃しがある。

したがって私は、次の順序で守るのが現実的だと考える。

```text
1. sourceをpublic/privateで分類
2. public schemaへallowlist projection
3. forbidden key / provenance test
4. generated artifactをprivacy audit
5. public repoへmerge
```

最後のscannerを主役にしない。**入力境界で落とし、CIは境界が壊れていないことを確認する。**

## 再現してみる

小さなfixtureで試せる。

```python
source = {
    "name": "Example Game",
    "players": 4,
    "duration_minutes_min": 60,
    "participants": ["Alice", "Bob"],
    "planned_at": "2026-10-08T21:00:00+09:00",
    "private_note": "internal only",
}

PUBLIC_FIELDS = {
    "name",
    "players",
    "duration_minutes_min",
}

public = {k: source[k] for k in PUBLIC_FIELDS if k in source}

assert public == {
    "name": "Example Game",
    "players": 4,
    "duration_minutes_min": 60,
}
```

改善前は `dict(source)` をそのまま公開していた。

改善後は、private fieldを知っていることではなく、**public fieldを明示的に知っていること**が公開条件になる。

この差は小さいが、schemaが成長するほど効く。

## 読後にできるようになること

この設計を使うと、公開サイトや公開APIを作るときに次を判断できる。

- そのfieldは「公開禁止リストにないから出す」のか
- 「公開sourceから得た、承認済みfieldだから出す」のか
- private modelをそのままpublic serializerへ渡していないか
- repositoryへcommitする前にpublic projectionを確定できているか
- privacy auditを最後の防波堤ではなく、境界検証として置けているか

特に、個人用DBと公開カタログ、社内分析と公開dashboard、運用ログとstatus pageを同じpipelineで扱うときに再利用できる。

## 今回の発見

私は当初、privacy対策は「private fieldを公開時に削ればよい」と考えやすかった。

しかしpublic GitHubを運用するなら、その設計では遅い。

`boardgamelist` の実例では、公開JSONに `access_condition: public-web` を持たせ、公開ページでも「参加者、通過状況、個人の予定は保存しない」と境界を固定していた。

GitHub自身も、public repositoryは誰でもアクセスでき、commit後のsensitive-data cleanupはhistory rewriteまで必要になり得ると説明している。

だから、再利用したい原則はこれである。

**private dataから何を消すかではなく、public evidenceから何を公開物として組み立てるかを先に決める。**

公開projectionを先に分ければ、公開コードは秘密を隠す役割から解放される。

それが、公開カタログを長く安全に育てるための境界になる。
