---
title: "「取れなかった」を0件にしない：fail-close記事の公開を止めた"
emoji: "🧭"
type: "tech"
topics: ["python", "dataengineering", "testing"]
published: false
published_at: 2026-08-11 19:48
---

# 「取れなかった」を0件にしない：fail-close記事の公開を止めた

この原稿は、現時点では公開しません。

理由は単純です。

`fail-close`、`null != 0`、`partial != complete` という原則自体は妥当でも、この記事固有の**実事故**を一次証拠付きで提示できていないからです。

複数の実装例を並べれば技術記事らしくはできます。しかし、それでは「既知の原則を自分のrepositoryへ適用した」という説明を超えません。

Issue #22で要求した公開条件は、次です。

```text
具体的な1事故
→ 何を誤って成功扱いしそうになったか
→ before
→ failure fixture
→ after
→ 実測証拠
```

今回、公開repository内からこの因果を一意に復元できる一次証拠を確認できませんでした。

したがって、事故を推測して本文を完成させることはしません。

## 残してよい一般則

将来、実事故の証拠が揃ったときに使う最小contractだけを残します。

```text
ACQUIRED
  ↓
VALIDATED
  ↓
CANONICAL
  ↓
PUBLISHABLE
```

ここで、

```text
取得できなかった
```

を、

```text
0件だった
```

へ変換しません。

同様に、母集団の一部しか取得できていない状態をcompleteとして公開しません。

## 公開再開に必要なfixture

記事を再開するには、実事故を再現するfailure fixtureをrepositoryへ固定します。

例えば構造だけなら次の形です。

```json
{
  "expected_sources": 3,
  "acquired_sources": 2,
  "records": 0,
  "complete": false
}
```

期待する挙動は、

```text
HTTP/process success
AND partial acquisition
→ publish rejected
```

です。

ただし、このfixtureを置いただけで「過去にこの事故が起きた」とは書きません。過去事故として公開するには、その事故を示すcommit、run、log、rejected artifactなど別の一次証拠が必要です。

## 判定

現段階の公開判定は次です。

```text
原則         : 妥当
再現設計     : 作成可能
実事故証拠   : 未確認
公開         : REJECT
```

一般論を水増しして公開するより、具体事件が取れるまで止めます。

## 再開条件

次のすべてを満たしたときだけ、この記事を再度公開候補にします。

- 実際のpartial / missing事故を一次証拠で特定できる
- その事故のbefore/after実装を示せる
- failure fixtureで再現できる
- `missing -> 0` または `partial -> complete` をCIで拒否できる
- 修正後のrunを実測できる

それまでは `published: false` を維持します。
