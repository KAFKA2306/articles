---
title: "AIに自分のPCを操作させるとき、何を止めるべき？ GitHub IssueでCodexを動かして分かったこと"
emoji: "🔁"
type: "tech"
topics: ["chatgpt", "codex", "github", "security", "automation"]
published: false
published_at: 2026-08-12 17:02
---

# AIに自分のPCを操作させるとき、何を止めるべき？ GitHub IssueでCodexを動かして分かったこと

「AIにコードを読ませる」だけなら、それほど怖くありません。

でも、AIに**自分のPC上でコマンドを実行させ、ファイルまで変更させる**となると話が変わります。

今回、GitHub Issueを中継地点にして、Windows上のCodex CLIへ仕事を渡す仕組みを作りました。

大まかな流れはこれだけです。

```text
指示を出す
  ↓
private GitHub Issueに仕事を書く
  ↓
自分のPCの常駐プログラムが読む
  ↓
Codexが指定されたフォルダで作業する
  ↓
結果をGitHub Issueへ返す
```

GitHub Issuesは本来、アイデア・タスク・バグなどを記録して追跡するための機能です。今回はそれを、AIへ仕事を渡すための「受け渡し箱」として使っています。

GitHub公式:
https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues

公開実装:
https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge

この記事で扱うのは導入手順ではありません。

**AIにPCを触らせるなら、どこまでを機械的に禁止すべきか**を、実際に作った仕組みを例に説明します。

## まず、登場する言葉を日本語にする

この記事ではいくつか技術用語が出てきます。先に意味だけ押さえます。

| 用語 | この記事での意味 |
|---|---|
| GitHub Issue | AIへ渡す仕事を書いておく場所 |
| worker | Issueを読み、Codexへ仕事を渡すプログラム |
| daemon | PC上で待機し続ける常駐プログラム |
| `cwd` | AIが作業するフォルダ |
| sandbox | AIにどこまで操作を許すかという制限 |
| `read-only` | 読むだけ。ファイル変更は禁止 |
| `workspace-write` | 指定した作業場所ではファイル変更を許す |
| E2E | 指示から結果まで、最初から最後まで通して確認するテスト |

用語そのものより重要なのは、**「誰が」「どこを」「どこまで」操作できるか**です。

## 最初の勘違い：「privateなら安全」ではなかった

最初は、GitHubのprivate repositoryを使えば十分安全ではないか、と考えました。

private repositoryは、アクセスできる人を限定できます。GitHub公式も、private repositoryは所有者や明示的にアクセスを与えられた人などに閲覧を制限する仕組みとして説明しています。

GitHub公式:
https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories

ただし、今回の仕組みではIssueに書かれた命令が、そのまま自分のPC上のAIへ届きます。

たとえば、次のような仕事を受け付けるとします。

```text
D:\dev\report-app を調べて、バグの原因を探して
```

ここまでは問題ありません。

しかし、もし命令を書く側が作業場所を自由に変えられたら、

```text
C:\Users\... を調べて
D:\private-data を読んで
```

のような指示まで届く可能性があります。

つまり、重要なのは「Issueがprivateか」だけではありません。

**Issueに書かれた命令のうち、何を実行してよいかを別に決める必要があります。**

今回の実装では、最初から次の制限を入れています。

```text
仕事を書く場所   = private GitHub Issue
命令できる人     = 設定したGitHubアカウントだけ
作業できる場所   = AllowedRootの下だけ
通常の権限       = read-only
変更が必要な仕事 = workspace-write
それ以上の権限   = 拒否
```

ここから先は、この制限を1つずつ見ていきます。

## 1. 「Issueに書いてある」だけでは実行しない

まず決めたのは、**誰の命令なら実行するか**です。

workerは、Issueコメントを書いたGitHubユーザー名を確認します。

そして、インストール時に設定したGitHubアカウントと一致した場合だけ仕事として受け付けます。

実装上は、概ね次の3条件です。

```text
決められた形式のコメントがある
AND
必要な識別マーカーがある
AND
コメントを書いた人 == 設定済みのGitHubアカウント
```

別のユーザーが似たコメントを書いても実行しません。

private repositoryでも、複数人にアクセス権があることはあります。

そのため、

**「この部屋に入れる人」**と、
**「PCへ命令してよい人」**は分けて考えます。

実装:
https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/bridge-daemon.ps1

## 2. AIが触れるフォルダを固定する

次は、**PCのどこを触ってよいか**です。

Codexへ仕事を渡すときには、作業フォルダを指定できます。この作業フォルダが`cwd`です。

もし`cwd`を自由に指定できると、AIの作業範囲がPC全体へ広がってしまいます。

そこで、インストール時に「このフォルダの下だけ触ってよい」という親フォルダを固定しました。実装ではこれを`AllowedRoot`と呼んでいます。

たとえば、

```text
AllowedRoot = D:\dev
```

なら、

```text
OK
D:\dev\project-a
D:\dev\project-b

REJECT
C:\Users\...
D:\private-data
```

となります。

ポイントは、AIへの自然言語の指示に

```text
他のフォルダは見ないでね
```

と書くだけではなく、**プログラム側で拒否すること**です。

実際のdaemonも、指定された`cwd`が`AllowedRoot`配下かをコードで検査しています。

実装:
https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/bridge-daemon.ps1

## 3. 普段は「読むだけ」にする

AIへ最初からファイル変更権限を与える必要はありません。

たとえば、

```text
このrepositoryのバグの原因を調べて
```

という依頼なら、まずコードを読むだけで十分です。

そこで今回のbridgeでは、通常状態を`read-only`にしました。

```text
read-only       = 読み取りだけ
workspace-write = 作業フォルダ内の変更を許可
```

ファイル修正が必要な仕事だけ、明示的に`workspace-write`へ変えます。

逆に、実装が受け付けるsandboxはこの2種類だけです。

```text
read-only
workspace-write
```

それ以外を要求すると拒否します。

これはセキュリティでよく使われる**least privilege（最小権限）**という考え方です。

「とりあえず全部できるようにする」のではなく、**その仕事に必要な権限だけを渡す**という考え方です。

実装:
https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/bridge-daemon.ps1

## 4. 普段使いのCodex設定を、そのまま自動実行へ持ち込まない

ここは実際に一度失敗しました。

最初の動作確認では、GitHub IssueからCodexへ仕事を渡す部分ではなく、Codexが追加のMCP/app層でOAuth認証を要求し、そこで止まりました。

つまり、普段人間が対話しながら使うCodex環境を、そのまま自動実行へ持ち込むと、不要な機能まで動こうとして失敗要因になります。

そこで自動実行では、普段のユーザー設定・apps・pluginsをそのまま読み込まない構成に変更しました。

現在の実装では、通常の自動実行に次の指定が入っています。

```text
--ignore-user-config
--disable apps
--disable plugins
```

必要なMCPだけは、bridge側で許可したものを明示的に有効化する方式です。

ここでの教訓は、

**自動化するAIを「普段使いAIの全部入り版」にしない**

ことです。

必要な機能だけを残した方が、権限も故障原因も減らせます。

失敗と修正の検証記録:
https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/VERIFICATION.md

## 5. 「プログラムが起動した」だけでは成功にしない

自動化では、途中まで動いただけで「成功」に見えることがあります。

たとえば、

```text
WindowsのScheduled Taskを登録できた
常駐プログラムが起動した
GitHub Issueへ指示を書けた
```

ここまで成功しても、Codexが実際に仕事を完了したとは限りません。

そこで、2026-08-12のE2E検証では、最終的にworkerが

```text
exit_code = 0
BRIDGE_OK
```

を返すことを成功条件にしました。

`exit_code = 0`は、実行したプログラムが正常終了したことを表す値として使っています。

`BRIDGE_OK`は、今回のsmoke testで最後まで処理が届いたことを確認するための期待結果です。

実際の検証記録には、

- worker `exit_code = 0`
- final Codex message = `BRIDGE_OK`

が残っています。

検証記録:
https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/VERIFICATION.md

つまり、

```text
道ができた
```

と、

```text
荷物が最後まで届いた
```

は別です。

自動化では、**最後の結果まで確認して初めて成功**とします。

## 6. AIへ渡す情報だけでなく、AIから出ていく情報も制限する

AIへ何を入力するかは気にしやすいのですが、逆方向も重要です。

Codexの実行結果には、

- ローカルのパス
- Git repositoryの状態
- 実行結果

などが含まれる可能性があります。

そのため、今回のraw queueはprivateのままにしています。

一方、公開した検証記録には、E2Eが成功したことを確認するための最小限の情報だけを残しました。

検証記録にも、raw queueを公開しない理由として、local paths・repository state・task outputが含まれ得ることを明記しています。

検証記録:
https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/VERIFICATION.md

考えるべき境界は3つあります。

```text
入力
  誰の命令か
  どのフォルダか
  どの権限か

実行
  AIに何の機能を持たせるか

出力
  PCの外へ何を返してよいか
```

「AIに何をさせるか」だけでなく、**結果として何を外へ出してよいか**まで設計対象です。

## ChatGPTからGitHubが見える = GitHubへ自由に書ける、ではない

ここは混同しやすい点です。

OpenAI公式Helpでは、ChatGPTのGitHub appは、接続したrepositoryのコードを読み取り、分析・検索・引用する用途として説明されています。

同じ公式Helpには、ChatGPTのGitHub app自体はrepositoryへのpush用途ではなく、コードの生成・編集・GitHubへのpushはCodex製品側の機能として案内されています。

OpenAI公式:
https://help.openai.com/en/articles/11145903

したがって、

```text
ChatGPTからrepositoryを読める
```

ことと、

```text
GitHub Issueへ命令を書き込み、その命令をローカルPCで実行できる
```

ことは別です。

今回のbridgeは、後者のために別の実行経路を作ったものです。

## 最終的に、何をコードで固定したか

今回の仕組みを、初心者向けの日本語に直すと次の6ルールです。

1. **命令できる人を1人に決める**
2. **AIが触れるフォルダを決める**
3. **普段は読み取り専用にする**
4. **不要な追加機能を自動実行へ持ち込まない**
5. **最後まで動いた証拠があるときだけ成功にする**
6. **AIの結果をどこまで外へ出すか決める**

実装上の設定にすると、次のようになります。

```yaml
queue:
  visibility: private

controller:
  allowed_login: fixed

filesystem:
  allowed_root: fixed

execution:
  default_sandbox: read-only
  allowed_sandboxes:
    - read-only
    - workspace-write

completion:
  require_exit_code_zero: true
  require_expected_result: true

output:
  raw_result_visibility: private
```

大事なのは、これを

```text
AIに危ないことをしないようお願いする
```

だけで終わらせないことです。

**危険な命令は、お願いではなくコードで拒否する。**

これが今回のbridgeで一番重要だった設計です。

## まとめ

最初は、GitHub IssueからCodexへ命令を渡せれば完成だと思っていました。

実際には、難しかったのは「命令を届けること」ではありませんでした。

難しかったのは、

- 誰なら命令してよいか
- PCのどこまで触ってよいか
- どの操作まで許すか
- どの追加機能を使ってよいか
- 何を成功と呼ぶか
- どの結果を外へ出してよいか

を1つずつ決めることでした。

AIにPCを触らせる仕組みでは、能力を増やすことより先に、**できないことを明確にする**必要があります。

GitHub Issueは便利な「受け渡し箱」になりました。

しかし、本当の安全装置はIssueそのものではなく、その前後に置いた制限でした。

## 一次情報・実装証拠

- Bridge implementation: https://github.com/KAFKA2306/KAFKA2306/tree/main/scripts/codex-chatgpt-bridge
- Bridge daemon: https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/bridge-daemon.ps1
- E2E verification: https://github.com/KAFKA2306/KAFKA2306/blob/main/scripts/codex-chatgpt-bridge/VERIFICATION.md
- Hardened daemon commit: https://github.com/KAFKA2306/KAFKA2306/commit/864774f15d7fc6522572a8e326dfa78573b0df74
- GitHub Docs — About issues: https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues
- GitHub Docs — About repositories: https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories
- OpenAI — Connecting GitHub to ChatGPT: https://help.openai.com/en/articles/11145903
