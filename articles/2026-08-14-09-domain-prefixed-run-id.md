---
title: "一意なIDだけでは、誤った保存先を防げない"
emoji: "🧭"
type: "tech"
topics: ["typescript", "backend", "workflow", "design"]
published: false
created_at: "2026-08-14"
updated_at: "2026-11-28"
---

複数の顧客や制作企画を同じ実行基盤で扱うとき、実行ごとにUUIDを発行すれば識別子の衝突は防ぎやすくなる。だが、ある実行が別の企画の設定を使って保存されたとき、UUIDの一意性は何の助けにもならない。

守りたいのは識別子の重複だけではない。**実行の所属と、設定・保存先の整合性である。** 動画制作基盤の実装から、一意性と所属を分けて考える方法を導く。

## 正しいIDと正しい設定の組み合わせが、間違っている

[yt3の実行入口](https://github.com/KAFKA2306/yt3/blob/849592ae98ce4ea1ea179ae5dd8997b227301791/src/index.ts)は、用途を表すBUCKETとRUN_IDを受け取る。例えば次の入力を考える。

```text
BUCKET=humanity_observatory
RUN_ID=2026-08-14
```

所属のないIDは `humanity_observatory/2026-08-14` に正規化され、同じ値が実行状態と保存処理に渡る。

ところが次の入力では事情が違う。

```text
BUCKET=humanity_observatory
RUN_ID=daily_pulse/2026-08-14
```

二つの文字列はそれぞれ有効に見えても、所属が矛盾している。公開実装では期待する接頭辞と一致しない入力を例外として扱う。[導入時の変更](https://github.com/KAFKA2306/yt3/commit/d1e2c42cfdfdb18d9962d15c38b87bab919df285)

ここで接頭辞を自動的に書き換えると、別用途の実行を再開するつもりだったのか、単なる入力ミスなのかという重要な情報を失う。所属が明示されているのに矛盾する場合、推測で修復しない。

## 入口で意味を確定し、保存先へ所属を運ぶ

[保存処理の実装](https://github.com/KAFKA2306/yt3/blob/849592ae98ce4ea1ea179ae5dd8997b227301791/src/io/core.ts)では、所属のないIDを拒否し、IDから用途別設定を読み、保存ディレクトリを決める。

この設計では、入口が実行の意図とIDの整合性を扱い、保存層が識別子と保存先の構造を扱う。別のCLIや再実行処理が保存層を直接呼ぶ場合にも、所属のない入力を受け取らない契約になる。

UUIDと信頼できる所属メタデータを組み合わせる方法も成立する。所属をIDへ含める利点は、ログやキューへIDだけを渡した場合にも所属を読み取れることだ。ただし、文字列を信頼できる認可情報の代わりにしてはいけない。

## 三つの入力から設計を始める

次は外部ライブラリを使わないNode.jsの例である。実際の製品コードではなく、所属を確定する処理の最小例として使える。 `run-id.mjs` として保存し、`node run-id.mjs` で実行する。

```js
function normalizeRunId(domain, raw) {
  const valid = s => /^[A-Za-z0-9_-]+$/.test(s);
  if (!valid(domain)) throw new Error("invalid domain");
  const parts = raw.split("/");
  if (parts.length === 1 && valid(parts[0])) {
    return domain + "/" + parts[0];
  }
  if (parts.length !== 2 || !parts.every(valid)) {
    throw new Error("invalid run id");
  }
  if (parts[0] !== domain) throw new Error("domain mismatch");
  return raw;
}

for (const raw of ["2026-08-14", "alpha/2026-08-14", "beta/2026-08-14"]) {
  try {
    console.log(normalizeRunId("alpha", raw));
  } catch (error) {
    console.log(error.message);
  }
}
```

期待する出力は次のとおりだ。

```text
alpha/2026-08-14
alpha/2026-08-14
domain mismatch
```

この例は許可する文字を限定するが、実際の保存処理には認可、パスの安全性、同じ所属内でのIDの一意性も必要である。日付をIDにする場合は同日に複数回実行する条件にも注意する。

複数用途で実行基盤を共有するとき、自分のシステムで所属、設定、保存先を一組ずつ書き出し、矛盾した組み合わせがどこで拒否されるかを調べる。用途が一つで保存先も分離されているなら、新しい接頭辞を強制する必要はない。目的は命名規則を増やすことではなく、誤った所属のまま処理を進めないことである。
