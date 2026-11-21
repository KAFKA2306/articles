---
title: "AIに同じ指示を繰り返すのをやめた。Issue駆動開発という最小運用"
emoji: "🎯"
type: "tech"
topics: ["ai", "github", "codex", "claudecode", "automation"]
published: true
published_at: 2026-09-02 22:12
---

AI coding agentを使うほど、コードを書く以外の仕事が気になるようになった。

「前回どこまでやった？」
「この修正は本当に終わった？」
「CIは通ったけどproductionは？」

これを毎回人間が思い出して指示すると、実装を自動化しても人間の頭は空かない。

最近は、変更ごとにGitHub Issueへ次だけを書くようにしている。

```text
Goal       何を実現するか
Done when  何が成立したら終わりか
Do not     何をしないか
Verify     何で確認するか
```

そしてagentへの指示はかなり短くできる。

```text
このIssueを監査する。
Done条件が未達なら原因を解決して再検証する。
成立したらCloseする。
```

自分の中では、これをIssue駆動開発として使っている。

最初は「既存の不具合を一件直す」くらいで試せる。再現手順と対象環境をIssueに貼り、`Done when` に直ったときの画面や出力、`Verify` に同じ手順で確かめる方法を書く。次の会話にはIssueのURLを渡し、PRとCIから修正の証拠をたどる。公開先の動作も完了条件に書いたなら、公開先で再現手順を確認してからCloseする。

## 実際のIssueを4項目へ落とす

抽象的なテンプレートのままでは使いづらいので、[finBI Issue #10](https://github.com/KAFKA2306/finBI/issues/10)を一件の例にする。これは公開Issueに記載された値から作る**読み替え例**であり、元Issueの本文をそのまま転記したものではない。

```text
Goal:
  FRED DGS10のsnapshotに、取得時点では未公開の値を混ぜない。

対象:
  data/snapshots/fred-dgs10-2026-07-20_2026-07-24.json
  retrieved_at = 2026-07-24T20:17:00Z

Done when:
  その時点で最新だった2026-07-23 = 4.71までを採用し、
  availability/vintageの時刻と一次URLをsnapshotに記録する。
  未検証なら verified: true にしない。

Do not:
  観測日が取得日以前という理由だけで、公開済みと判定しない。

Verify:
  retrieved_at=2026-07-24T20:17:00Z と
  2026-07-24=4.69 の組合せを不正なfixtureとして必ず拒否する。
  UIの表示期間・取得時刻も修正後のsnapshotに一致させる。
```

2026年7月24日15:17 CDT（20:17 UTC）のFRED表示で最新だったのは7月23日の4.71。一方、7月24日の4.69を確認できたのは7月27日15:16 CDT更新時だった。同じ日付の観測値でも**公開された時刻**を見落とすと、未来の値を過去に取得したことにしてしまう。出典と要求は[Issue本文](https://github.com/KAFKA2306/finBI/issues/10)で確認できる。

この例を任せるときは、agentにIssue URLを渡すだけでなく、修正前に不正fixtureが落ちるかを固定する。修正後にPRとCIの対象コミットを確認し、Pages公開まで要求した案件なら実際の画面も読む。**IssueのClose、CIのgreen、公開画面の更新は三つの別の証拠**として扱う。実際の修正・公開をこの記事の再演で行ったとは主張しない。

## Issueは「現在仕様」ではなく、短命な変更契約

Spec-Driven Developmentは有用だ。GitHub Spec Kitも、`Spec → Plan → Tasks → Implement` の順で意図を構造化する。

- https://github.github.com/spec-kit/

一方、Spec Kit自身も、specを実装後に捨てる・維持する・source of truthにする、といった複数のpersistence modelを認めている。

- https://github.github.com/spec-kit/how-to/persisting-specs.html

自分は多くの変更で、もっと寿命を短くした方が楽だった。

```text
Issue        = 今回の変更契約
Closed Issue = 変更履歴
main         = repositoryの現在状態
production   = 利用者から見える現在状態
```

閉じたIssueは、未来の実装と同期し続けなくてよい。

ここが長寿命のMarkdownと違う。文書が古くならないのではなく、**現在仕様であり続ける責務をCloseで終わらせる**。

恒久的に守りたいものだけをtest、schema、CI、最小限のREADMEやAGENTS.mdへ移す。

## 失敗とも相性がいい

以前、Crash-Driven Developmentとして「失敗を隠さず、原因を観測できる形で落とす」と書いた。

- https://zenn.dev/kafka2306/articles/11cd731eebded1

さらに、Claude Codeへ実装もtestも任せるなら、合格条件はagentの外側へ固定した方がよいとも書いた。

- https://zenn.dev/kafka2306/articles/2026-08-15-hook-runner-is-not-policy

この2つはIssueでつながる。

```text
失敗する
↓
Issueに証拠が残る
↓
原因を直す
↓
固定したDone条件で再検証する
↓
成立したらCloseする
```

失敗のたびに人間が新しいpromptを書く必要はない。

## 人間は「次の細かい指示」から降りられる

123個の個人開発を横断したときも、効いたのは全部を記憶することではなく、Issue・PR・CI・main・productionへ状態を外部化することだった。

- https://zenn.dev/kafka2306/articles/chatgpt-multiproject-autonomy

心理学では、外部の物理的・デジタルな手段へ情報処理の一部を移し、認知要求を下げる行為をcognitive offloadingと呼ぶ。

- https://pubmed.ncbi.nlm.nih.gov/27542527/

IssueにGoalとDone条件を置くと、人間が保持する必要があるのは「次に何を指示するか」ではなくなる。

人間に残すのは、価値、優先順位、公開、削除、売買のような重要な判断でよい。

## 最小形

Issue-Driven Developmentという名前自体は新しくない。2016年にも、実装前にfeatureをIssueへ書いて進める運用が紹介されている。

- https://www.foonathan.net/2016/05/issue-driven-development/

自分の実践で重要だったのは名前ではなく、次の4点だった。

1. IssueへGoalとDone条件を書く
2. 失敗を隠さずIssueへ戻す
3. agentにはIssue解決と再検証を任せる
4. 条件が成立したらCloseし、現在の真実はmain / productionへ戻す

Markdownを増やすより、**終わった要求を終わらせられる構造**の方が、自分には合っていた。

この記事自体も、Issueを作り、Done条件を固定してから実装・検証する形で作っている。
