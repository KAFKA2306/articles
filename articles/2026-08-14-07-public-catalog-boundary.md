---
title: "公開データは、秘密を消すのではなく公開できる情報から作る"
emoji: "🧱"
type: "tech"
topics: ["dataengineering", "privacy", "github", "testing"]
published: false
created_at: "2026-08-14"
updated_at: "2026-11-28"
---

社内データから公開ダッシュボードを作るとき、秘密の列を取り除けば公開できると考えがちだ。だが新しい内部項目が追加されるたびに、公開側でも除外を忘れないようにする仕事が生まれる。

公開に必要な情報が独立して取得できるなら、**秘密を含む入力を公開処理へ渡さない**設計を選ぶ。公開カタログの実例から、その違いと実装の最小単位を考える。

## 項目が増えたときに何が起きるか

作品情報と参加予定を同じデータに置く場合を考える。次は架空の入力である。

```python
source = {
    "name": "Example Game",
    "players": 4,
    "duration_minutes_min": 60,
    "participants": ["Alice", "Bob"],
    "private_note": "internal only",
}
blocked = {"participants", "private_note"}
public = {k: v for k, v in source.items() if k not in blocked}
```

この時点では内部項目を除外できる。ところが新しく `planned_at` を加えると、除外一覧も変えなければ公開データへ流れる。内部機能の変更が公開側の安全性を変えてしまうのである。

最終画面で非表示にしても、元のJSONが公開リポジトリに入っていれば問題は残る。[GitHubの公開リポジトリの説明](https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories)によれば誰でもアクセスでき、[機密情報の削除手順](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)では履歴の書き換えやコピーへの対応が必要になる場合がある。

## 公開物の入力を独立させる

2026年8月14日の[ボードゲームカタログの変更](https://github.com/KAFKA2306/boardgamelist/commit/9ce9aa8c7eab27b650dd06a478c21319949dc575)では、[公式メタデータ](https://github.com/KAFKA2306/boardgamelist/blob/9ce9aa8c7eab27b650dd06a478c21319949dc575/data/official-metadata/apollo-no-shinpan-2026-08-14.json)に出典のアクセス条件 `public-web` を記録した。[作品ページの原稿](https://github.com/KAFKA2306/boardgamelist/blob/9ce9aa8c7eab27b650dd06a478c21319949dc575/docs/games/apollo-no-shinpan.md)には参加者、通過状況、個人の予定を保存しない方針がある。

公開側は公式情報から取得した作品名、人数、所要時間などを使う。内部の予定管理は別の責務である。こうすれば、予定管理に項目を追加するだけで公開カタログの入力が増えることはない。

ただし公開元が閲覧可能であることは、転載権や個々の値の公開適切性まで保証しない。項目名が `notes` なら、公開方針の説明も秘密の担当者メモも入れられる。出典、公開してよい値、承認された項目を合わせて判断する必要がある。

## 公開する値を、実際の作品データから取り出す

前述の2026年8月14日のメタデータには、次の値が保存されている。

| 公開ページの項目 | メタデータの参照先 | 保存された値 |
| --- | --- | --- |
| 作品名 | `edition.name` | アポロンの審判 |
| プレイヤー数 | `edition.players` | 9人 |
| 所要時間 | `edition.duration_minutes_min` / `duration_minutes_max` | 180〜210分 |
| 出典 | `source.url` | [制作者公式BOOTH](https://booth.pm/ja/items/6508051) |

この構造を自分の公開カタログへ移すなら、公開情報だけのファイルを入力に指定し、表示する項目を明示して取り出す。次は[保存された実データ](https://github.com/KAFKA2306/boardgamelist/blob/9ce9aa8c7eab27b650dd06a478c21319949dc575/data/official-metadata/apollo-no-shinpan-2026-08-14.json)を使う実装例である。

```python
import json
from pathlib import Path

record = json.loads(
    Path("data/official-metadata/apollo-no-shinpan-2026-08-14.json")
    .read_text(encoding="utf-8")
)
edition = record["edition"]
public = {
    "name": edition["name"],
    "players": edition["players"],
    "duration_minutes_min": edition["duration_minutes_min"],
    "duration_minutes_max": edition["duration_minutes_max"],
    "source_url": record["source"]["url"],
}
print(json.dumps(public, ensure_ascii=False, indent=2))
```

指定した版のリポジトリを取得し、そのルートでこのコードを使えば、上の表に対応する値を取り出せる。これは既存の作品ページの生成処理を転載したものではなく、実データを使うための最小実装例である。

重要なのは二つの境界を設けることだ。

- 入力：公開処理には公式メタデータだけを渡す。個人の予定や参加履歴を読む必要がない。
- 出力：公開ページに必要な項目だけを取り出す。公開用メタデータに項目が増えても、自動的に表示項目を増やさない。

たとえば内部の予定管理に `planned_at` を追加しても、公開処理がそのファイルを読まなければ、追加した値は公開側へ届かない。これは構造から導ける性質であり、実際の漏洩事故を記録したものではない。

## 次に公開物を作るときの判断順序

| 必要な情報 | 選ぶ方法 |
| --- | --- |
| 公式の公開資料から取得できる | 公開資料を直接入力にする |
| 内部と公開で共通の項目がある | 公開が認められた値だけを独立した入力に渡す |
| 内部情報を集計しなければ作れない | 内部処理と公開処理を分け、公開する集計値の再識別可能性も考慮する |

匿名化統計のように内部情報が不可欠な場合、公開情報だけから作ることはできない。項目の許可一覧だけでは匿名性も保証できない。

公開側が知る必要のない内部情報を、公開処理から読めなくする。次にデータモデルを変更するときは、秘密の項目を何個除外するかではなく、そもそも何を入力する必要があるかから考える。
