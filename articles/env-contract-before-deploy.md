---
title: "環境変数は設定済みなのに認証が動かない。デプロイ前に名前の契約を検証する"
emoji: "🔐"
type: "tech"
topics: ["vite", "ci", "deployment", "security"]
published: false
---

環境変数をホスティング側に登録しただけでは、アプリがその値を読めているとは限りません。特にフロントエンドのビルドツールには「クライアントへ公開する環境変数名」の規則があり、設定側とコード側の名前が1文字でも違えば、デプロイ自体が成功しても機能は無効なままになり得ます。

この記事では、公開GitHubリポジトリで実際に修正された `VITE_` 環境変数の不一致を題材に、**デプロイ前に「必要な名前が存在し、空でない」ことを機械検証する**設計を整理します。値そのものをログへ出さず、設定ミスだけをfail-closeで止めます。

## 1. 問題：設定したのに、アプリからは見えない

具体例は `KAFKA2306/rule-scribe-games` のPR #85です。修正前のフロントエンドは次の名前を参照していました。

```js
const supabaseUrl = import.meta.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = import.meta.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
```

修正後は次の名前になっています。

```js
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY
```

差分そのものは公開PRで確認できます。

- https://github.com/KAFKA2306/rule-scribe-games/pull/85
- https://github.com/KAFKA2306/rule-scribe-games/blob/main/frontend/src/lib/supabase.js

Vite公式ドキュメントの正準ソースでも、既定では `VITE_` prefixを持つ環境変数が `import.meta.env` 経由でクライアントコードへ公開される仕様です。

- https://github.com/vitejs/vite/blob/main/docs/guide/env-and-mode.md
- https://github.com/vitejs/vite/blob/main/docs/config/shared-options.md

したがって、ここでの問題は「値を登録したか」ではなく、**デプロイ環境の名前と、ビルド時にコードが読む名前が一致しているか**です。

## 2. 原因：環境変数は文字列ではなくインターフェースである

環境変数を単なる設定値の集合として扱うと、次の3層が独立に変更されます。

1. ホスティング側に登録するキー名
2. CI/CDが取得・検査するキー名
3. アプリケーションコードが読むキー名

壊れた例では、アプリケーションが `NEXT_PUBLIC_*` を読んでいました。一方、修正PRでは実際の契約を `VITE_SUPABASE_URL` / `VITE_SUPABASE_ANON_KEY` / `SUPABASE_URL` に統一し、フロントエンドとバックエンドとdeploy workflowを同じ名前へ合わせています。

ここで重要なのは、**デプロイ成功と設定契約の成立は別の状態**だということです。ホスティングへのuploadが成功しても、必要な変数がアプリから参照できなければ機能は成立しません。

## 3. 設計判断と代替案

### 採用：deploy直前に名前と非空だけを検証する

PR #85ではPreviewとProductionの両方で、Vercelから取得したenv fileを読み、次の3キーが存在して空でないことを検査してからdeployします。

```text
VITE_SUPABASE_URL
VITE_SUPABASE_ANON_KEY
SUPABASE_URL
```

不足があれば終了コード1で停止します。一方、成功時にも値は表示せず `Supabase auth environment contract: OK` だけを出します。

- https://github.com/KAFKA2306/rule-scribe-games/blob/main/.github/workflows/deploy.yml

### 代替案A：アプリ起動後だけ検出する

runtimeで `null` を検出する方法は必要ですが、それだけでは壊れた成果物を先に公開してしまいます。deploy前に検出できる静的な設定不一致は、deploy前に止める方が失敗範囲を小さくできます。

### 代替案B：CIログへ値を表示して確認する

採用しません。必要なのは「存在するか」「空でないか」であり、値そのものをログへ出す必要はありません。検証器はsecretの観測面を増やさない方が単純です。

### 代替案C：すべての環境変数をクライアントへ公開する

採用しません。Viteの `envPrefix` にはクライアントへ公開する変数を制限する役割があります。公式ドキュメントも、prefixを空文字にして全変数を公開する設定を安全上避けるよう明記しています。

- https://github.com/vitejs/vite/blob/main/docs/config/shared-options.md

## 4. 実装：小さなcontract checkerをdeployの前に置く

公開PRのworkflowはPython標準ライブラリだけでenv fileを読みます。一般化すると、最小実装は次のようになります。

```python
import sys
from pathlib import Path

path = Path(sys.argv[1])
required = sys.argv[2:]
values = {}

if path.exists():
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        values[key.strip()] = value

missing = [key for key in required if not values.get(key)]
if missing:
    print("Missing required environment variables: " + ", ".join(missing))
    raise SystemExit(1)

print("Environment contract: OK")
```

workflowでは、deployコマンドより前にこれを実行します。

```yaml
- name: Verify environment contract
  run: python check_env.py .env.production VITE_API_URL API_URL

- name: Deploy
  run: your-deploy-command
```

この順序が契約の本体です。checkerが失敗したらdeployへ進みません。

## 5. 検証：正常系だけでなく4境界を試す

最低限、次の4ケースを固定します。

| 入力 | 期待結果 |
| --- | --- |
| 必須キーがすべて非空 | exit 0 |
| キーが1つ欠落 | exit 1 |
| キーはあるが空文字 | exit 1 |
| コメントや無関係キーだけ | exit 1 |

たとえば読者が手元で試すなら、次のファイルを用意します。

```dotenv
VITE_API_URL="https://example.invalid"
API_URL="https://example.invalid"
```

```bash
python check_env.py .env.production VITE_API_URL API_URL
```

ここではURLへ接続する必要はありません。このgateが保証するのは**名前と非空性**だけです。URLの到達性、credentialの有効性、OAuth設定の正しさは別gateで検証すべきです。

## 6. 失敗と学び：存在確認を「動作確認」と呼ばない

壊れた失敗例は、ホスティング側に設定があっても、アプリ側が別名を読むことです。PR #85の差分では `NEXT_PUBLIC_SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_ANON_KEY` から `VITE_SUPABASE_URL` / `VITE_SUPABASE_ANON_KEY` へ修正されています。

改善後は、コード側の名前を揃えるだけでなく、PreviewとProductionのdeploy直前に同じ契約を検査します。これにより「設定したつもり」をCIの成功条件から排除できます。

ただし、このcheckerを通過したことから「認証が動く」と推論してはいけません。確認できるのは次だけです。

```text
required names exist
AND
required values are non-empty
```

この境界を狭く保つほど、CIの緑色が何を意味するかが明確になります。

## 7. 再現方法：5分で壊して直す

1. 上の `check_env.py` を保存する。
2. `.env.production` に `API_URL=x` だけを書く。
3. `python check_env.py .env.production VITE_API_URL API_URL` を実行し、exit 1を確認する。
4. `VITE_API_URL=x` を追加する。
5. 同じコマンドを再実行し、exit 0を確認する。
6. CIではこのstepをdeploy stepより前へ置く。
7. 値をログへ表示する処理は追加しない。

この再現例の目的は特定サービスへの接続ではなく、**環境変数名をデプロイ契約として扱う**ことです。

## まとめ

環境変数の事故は、secret管理だけの問題ではありません。名前もAPIの一部です。

実務では、次の順序にすると責務が分かれます。

```text
設定を取得
  ↓
必須キーの存在・非空を検証
  ↓
ビルド
  ↓
デプロイ
  ↓
runtime / E2Eで実機能を検証
```

PR #85の改善点は、認証サービス固有の設定方法ではなく、**設定契約を副作用の前に検証する**ところにあります。これはAPI URL、feature flag、storage endpointなど、環境依存の設定を持つCI/CDへそのまま転用できます。

## 一次情報

- https://github.com/KAFKA2306/rule-scribe-games/pull/85
- https://github.com/KAFKA2306/rule-scribe-games/blob/main/frontend/src/lib/supabase.js
- https://github.com/KAFKA2306/rule-scribe-games/blob/main/.github/workflows/deploy.yml
- https://github.com/vitejs/vite/blob/main/docs/guide/env-and-mode.md
- https://github.com/vitejs/vite/blob/main/docs/config/shared-options.md
