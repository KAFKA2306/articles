---
title: "「モデル差し替え」を作ろうとしたら、公式説明の1行で設計が変わった"
emoji: "🐶"
type: "tech"
topics: ["vrchat", "unity", "modularavatar", "architecture"]
published: false
published_at: 2026-08-12 14:18
---

# 「モデル差し替え」を作ろうとしたら、公式説明の1行で設計が変わった

この原稿は、現時点では公開しません。

最初は「ムチォは既存モデルを別の犬モデルへ差し替える仕組みをこちらで作る必要がある」と考えていました。

しかし販売元の現行BOOTHページを確認すると、同梱物に **「オリジナルペットの作り方」** が含まれています。また、ムチォはModular Avatar対応Prefabとしてアバター直下へ配置する構成で、同梱モデルの改変も許可されています。

一次情報:
https://booth.pm/ja/items/8657397

この情報だけで、問題設定は変わります。

```text
旧仮説
Muchioのmodelをこちらで置換する

↓

更新後の問い
既存Bodyの機能を壊さず、Muchio側の機能とどう接続するか
```

ただし、ここから先を実装済みの事実として書くことはできません。

## 公開情報で確認できたこと

2026年8月13日に販売ページから確認できる範囲は次です。

- Modular Avatar対応Prefabとして導入する
- サンプル9体と素体が同梱される
- 「オリジナルペットの作り方」が同梱される
- 同梱モデルの改変が許可されている
- アバター本体は非改変で、Prefabの出し入れによる導入・撤去を想定している

これらは販売元が公開している仕様です。

## まだ確認できていないこと

一方、今回のAcceptance Criteriaで必要だった `happy_shiroi-nu_PC` の実Prefab内部については、この環境から観測証拠を取得できていません。

したがって、次は未確認です。

```text
Animator Controllerの実参照
idle / walk Clipの実参照
VRCPhysBoneのcomponent位置とrootTransform
Contact Sender / Receiverの実配置
Body rootとして使うべきTransform
Muchio接続後のlocomotion
Core / Body境界が実際に成立するか
```

これらを商品ページや命名から推測して埋めません。

## 設計案と観測事実を分ける

現時点で言える設計仮説は、次までです。

```text
Muchio側の機能
        ↓
接続境界
        ↓
既存Body Prefab
```

Body側に既に耳・尻尾・Animator・Contact等の挙動があるなら、それらを再実装するより保存する方がよい可能性があります。

しかし、**実Prefabに何が存在するかを観測する前に `preservePhysBones: true` や `walkClip: ...` を完成仕様として書くことはしません。**

## 実Prefabで取るべき証拠

公開再開前に、Unity上で最低限次を機械的に採取します。

| 観測対象 | 必要な証拠 |
|---|---|
| Root | 全Component一覧 |
| Animator | Controller / Playable Layer参照 |
| Armature | Transform階層 |
| PhysBone | component / rootTransform / collider参照 |
| Contact | Sender / Receiver / parameter / tag |
| Animation | idle / walk候補Clipと参照元state |
| Runtime | idle / locomotion時に実際に動くTransform |
| 統合後 | Muchio機能とBody機能の両方が維持されること |

名前だけでは採用しません。例えば `walk.anim` が存在しても、Animatorから参照され、実再生で期待したTransformが動くことまで確認します。

## Acceptance Gate

この記事を再公開する条件を次に固定します。

```text
BOOTH等の公開仕様を確認
AND
happy_shiroi-nu_PC 実Prefabを観測
AND
推測と観測を分離
AND
Core / Body境界をfixtureまたは実装で検証
AND
未実装機能を現在形で書かない
```

現時点では2つ目以降を満たしていません。

そのため、設計仮説を成功事例へ膨らませず `published: false` とします。

## まとめ

この記事で確定した発見は、実装成功ではありません。

**一次情報を読み直したことで、「モデルを置換する」という問題設定自体が怪しくなった。**

ここまでは根拠があります。

その先のCore / Body Adapterが本当に成立するかは、実Prefabを観測して初めて記事にできます。

## 一次情報

- ムチォ販売元BOOTH: https://booth.pm/ja/items/8657397
