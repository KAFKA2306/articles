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

## 自分の公開データで一列増やしてみる

先ほどの架空の入力を使い、公開する項目を明示する方式へ変える。

```python
source["planned_at"] = "internal schedule"
fields = ("name", "players", "duration_minutes_min")
public = {k: source[k] for k in fields}
print(public)
```

出力に残るのは作品名、人数、所要時間の三項目である。内部項目をさらに追加しても、許可一覧を変えない限り出力されない。これは構造の比較例であって、実際に漏洩事故が起きたという記録ではない。

実データでは公開側の各値を公式資料へ結びつけ、秘密の入力を生成処理へ渡さない。匿名化統計のように内部情報を処理しなければ公開物を作れない場合は、処理を隔離し、集計結果の再識別可能性も評価する。項目の許可一覧だけでは匿名性を保証できない。

公開側が知る必要のない内部情報を増やさずに済むか。次にデータモデルを変更するときは、その問いから公開経路を設計する。
