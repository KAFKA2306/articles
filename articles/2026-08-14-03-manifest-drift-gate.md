---
title: "再生成できることと、完成品を届けたことは違う"
emoji: "🧾"
type: "tech"
topics: ["python", "githubactions", "dataengineering", "testing", "ci"]
published: false
created_at: "2026-08-14"
updated_at: "2026-11-28"
---

元データを更新したのに、配布する一覧表は古いままだった。ところがCIは、一覧表を再生成してから内容を調べるため、成功と表示する。利用者が受け取る版と、CIが調べた版は同じではない。

生成物を配布物として保存するなら、**生成できることと、生成済みの成果物が提出されていることを分ける。** 半導体決算データの来歴を記録するマニフェストの実装から、その差を考える。

## 入力を修復すると、最初の欠陥が見えなくなる

決算データのマニフェストには、対象ファイルのパス、SHA-256、バイト数などが記録される。[当時の生成処理](https://github.com/KAFKA2306/semiconductor-earnings-model/blob/7595f0b0b7f7535d9eaea182fe5f2ba415bce8f4/scripts/build_earnings_lineage_manifest.py)は入力からマニフェストを作り、[照合処理](https://github.com/KAFKA2306/semiconductor-earnings-model/blob/7595f0b0b7f7535d9eaea182fe5f2ba415bce8f4/scripts/verify_earnings_lineage_manifest.py)は記録された値と実ファイルの整合性を扱う。

例えば入力だけを更新し、古いマニフェストをコミットしたとする。これは失敗条件を説明するための仮定であり、実際に公開データを壊した報告ではない。

CIが先にマニフェストを再生成すると、その後の照合は新しい内容を対象にする。元のコミットに不整合があったかどうかは、その成功結果から分からない。

[当時のワークフロー](https://github.com/KAFKA2306/semiconductor-earnings-model/blob/7595f0b0b7f7535d9eaea182fe5f2ba415bce8f4/.github/workflows/earnings-lineage.yml)では、再生成と内容の照合に加え、コミットされたマニフェストとの差分を扱っている。

```sh
git diff --exit-code -- data/earnings_ledger/lineage_latest.json
```

終了コード1は、再生成した追跡ファイルが元のコミットと異なることを示す。未追跡のファイルはこのコマンドだけでは分からないため、必要なら git status で対象を把握する。

## そもそも生成物を保存する必要はあるか

ここで選ぶべき設計は二つある。

| 配布の契約 | 適した扱い |
| --- | --- |
| 正本の入力と生成器から配布時に必ず生成する | 生成物を重複して管理しない |
| コミットだけで完成した成果物を取得できる | 入力変更と生成物更新を同じ変更として届ける |

前者なら、保存していない生成物との差分を確認する必要はない。後者では生成器の成功だけでなく、配布する版に生成結果を含めることが必要になる。管理の手間を減らしたいなら、差分確認を増やすより、生成物を保存する理由を先に問う。

## 二つのファイルで違いを見てみる

Gitとuv、Pythonを利用できる環境で、次を空の一時ディレクトリ内で実行する。元の実験を簡略化した再現例であり、実データを変更しない。

```sh
(
  set -eu
  scratch=$(mktemp -d)
  trap 'rm -rf "$scratch"' EXIT
  cd "$scratch"
  git init -q

  digest() {
    uv run --no-project python -c 'from hashlib import sha256; from pathlib import Path; print(sha256(Path("input.txt").read_bytes()).hexdigest())'
  }

  printf 'v1\n' > input.txt
  digest > manifest.sha256
  git add input.txt manifest.sha256
  git -c user.name=Example -c user.email=example@example.com commit -qm initial

  printf 'v2\n' > input.txt
  digest > manifest.sha256
  git diff -- manifest.sha256
)
```

再生成後のマニフェストは新しい入力のハッシュを持つが、最後の差分には変更が現れる。作業中に正しい成果物を作れたことは、コミットにその成果物が含まれていたことを意味しない。

この区別はロックファイル、生成型定義、静的カタログにも適用できる。配布時に正本から生成する方式を選べるなら、重複保存をやめる。保存が必要なら、入力と成果物を一緒に更新する。利用者が追加作業なしで必要な版を使えることが目的である。
