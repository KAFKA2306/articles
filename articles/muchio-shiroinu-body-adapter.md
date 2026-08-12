---
title: "『モデル差し替えは未対応』の前提が、BOOTHを見直したら消えた：Muchioを犬へつなぐ設計を引き直す"
emoji: "🐶"
type: "tech"
topics: ["vrchat", "unity", "modularavatar", "animation", "architecture"]
published: true
published_at: 2026-08-12 14:18
---

最初の前提は、こうでした。

> ムチォのモデル差し替えはまだ将来機能。ならば既存Prefabを分解し、犬モデルへ置き換える仕組みをこちらで作る必要がある。

ところが、販売元の現行BOOTHページを読み直すと、同梱物に **「オリジナルペットの作り方」** と書かれていました。

この1行で、作ろうとしていたものの前提が崩れました。

問題は「ムチォの身体をどう犬へ強引に置換するか」ではありません。

**すでに完成している犬Prefabの耳・尻尾・Animator・接触挙動を壊さず、ムチォの追従・発話・インタラクションだけをどう接続するか。**

設計の中心を、モデル置換から **Core / Body分離** へ引き直す必要がありました。

ここでは、一次情報を読み直しただけで問題設定がどう変わったか、その後に `happy_shiroi-nu_PC` の実Prefabを何から観測すべきかを追います。

## 1. 一次情報を更新したら、問題設定そのものが変わった

2026年8月12日に確認したムチォの現行BOOTHページでは、現行版は **2026-08-05 v1.3.6** とされ、重要な事実を次のように確認できます。

1. Modular Avatar対応Prefabとして導入する
2. サンプル9体＋素体が同梱される
3. 「オリジナルペットの作り方」が同梱される
4. 同梱モデルの改変は自由と明記されている

さらに、現行v1.3.6では同期パラメータ使用量が77bitと明記されています。

- ムチォ商品ページ: https://booth.pm/ja/items/8657397

ここから設計を次のように更新しました。

```text
旧い前提
Muchio Prefab
  -> meshを犬に差し替える
  -> 壊れた部分を個別修復する

更新後の前提
Muchio Core
  -> Body側の既存機能を保持する
  -> 必要な接続点だけAdapterで定義する
```

この差は大きいです。

前者では「ムチォ側が身体を所有する」ため、犬モデル固有の機能をムチォに移植し直す必要があります。

後者では「犬Prefabが身体を所有する」ため、ムチォは身体へ命令するだけです。

## 2. 「幸せのしろい～ぬ」は、置換対象ではなく既に完成したBodyだった

今回の第1号Body候補は、アトリエ・モココの **「幸せのしろい～ぬ」** です。

- 商品ページ: https://booth.pm/ja/items/8446507

販売元の現行ページでは、次の仕様が確認できます。

- 2026-07-11 ver1.0頒布開始
- 2026-07-24 ver1.01でPC版Prefabの一部Animator欠如などを修正
- Unity 2022.3、制作環境は2022.3.22f1
- VRChat SDK 3.10.4
- Modular Avatar 1.17.1
- Humanoidボーンを使用
- 尻尾は常に揺れる
- 耳は触って持ち上げられる
- PC / Android / iOS対応
- 4030 polygons
- mesh 1個
- shape key 29個

ここで重要なのはポリゴン数ではありません。

**この犬は、ムチォへ取り込む前から「身体としての挙動」を持っている**ことです。

耳や尻尾をムチォAdapter側でもう一度実装すると、同じ責務を二重に持つ可能性があります。

しかも、商品ページだけでは「耳を持ち上げる実装がどのVRCPhysBoneなのか」「接触反応がどのContactなのか」までは断定できません。

だから、ここで実装を始めてはいけません。

**公開ページで存在が確認できる機能と、Prefab内部でしか確認できない実装方式を分ける必要があります。**

## 3. Body Adapterは「耳や尻尾を実装する場所」ではない

当初は、Body Adapterへ耳PhysBone、尻尾PhysBone、なでContactまでまとめる設計を考えていました。

しかし、これは責務が大きすぎます。

VRChat公式ドキュメントでは、PhysBonesはボーンへ物理的な動きを与え、Contactsは接触を検知してAnimator Parameterやエフェクトを駆動するAvatar Dynamicsの構成要素として定義されています。

- Avatar Components: https://creators.vrchat.com/avatars/avatar-components/
- PhysBones: https://creators.vrchat.com/common-components/physbones/
- Contacts: https://creators.vrchat.com/common-components/contacts/

元Bodyがこれらを持っているなら、第一選択は **そのままBody Prefabへ残すこと** です。

Adapterが持つべきなのは、実装そのものではなく接続ポリシーです。

```yaml
bodyPrefab: happy_shiroi-nu_PC
bodyRoot: <inspect-from-prefab>
speechAnchorOffset: <inspect-and-measure>

locomotion:
  idleClip: <inspect-from-controller>
  walkClip: <inspect-from-controller>

preserve:
  physBones: true
  contacts: true

overrides: {}
```

`preservePhysBones: true` は「PhysBoneをAdapterが作る」という意味ではありません。

**Body側で見つけた既存PhysBoneを、Core接続のために壊さない**という契約です。

Contactsも同じです。

## 4. CoreとBodyの境界を、機能で切り直す

ここから、Muchio側を機能単位で分離します。

これは現行Prefab内部のGameObject名を断定するものではなく、実装前の責務分割です。

```text
Muchio Core
├─ playerへの追従
├─ grab / stretch等のペット操作
├─ idle / walk等の状態判定
├─ pet mount / constraint系の接続
├─ kiss等のペット間インタラクション
├─ enable / disable state
├─ PCアプリ / OSCとの通信
└─ speech board / 発話表示

BodyProfile / Adapter
├─ bodyPrefab
├─ bodyRoot transform
├─ speechAnchorOffset
├─ idleClip
├─ walkClip
├─ optional transform remapping
├─ optional animation overrides
├─ preservePhysBones
└─ preserveContacts
```

この設計で最も重要なのは、**Coreが「犬の耳」を知らない**ことです。

Coreが知るのは「歩いている」「発話する」「掴まれた」といった意味です。

Bodyは、それを自分のAnimationClipやTransformへ変換します。

これなら、次のBodyを追加するときもCoreを変更せずに済みます。

```text
Muchio Core
   ├─ BodyProfile: 幸せのしろい～ぬ
   ├─ BodyProfile: 狛乃
   ├─ BodyProfile: まめひなた
   ├─ BodyProfile: パグ
   └─ BodyProfile: コーギー
```

「Prefabを指定するだけ」に近づけるには、身体固有の実装をCoreへ吸い上げないことが重要です。

## 5. Modular Avatarの思想とも整合する

この分離は、Modular Avatarの使い方とも相性が良いです。

Modular Avatar公式ドキュメントでは、Merge ArmatureはGameObject階層をAvatar Armatureへ統合し、衣装セットアップ時にはPhysBonesなどのactive componentsを元の位置へ残すよう処理すると説明されています。

- Merge Armature: https://modular-avatar.nadena.dev/docs/reference/merge-armature
- Outfit tutorial: https://modular-avatar.nadena.dev/docs/tutorials/clothing

またMerge Animatorは、既存Playable Layerを置き換えるのではなく、指定したAnimator Controllerを追加統合できます。

- Merge Animator: https://modular-avatar.nadena.dev/docs/reference/merge-animator

つまり、Modular Avatar自体が目指しているのも、

```text
完成済みAvatar
+ 独立したPrefab / Animator / component
= build時に非破壊統合
```

という方向です。

Body Adapter側が元モデルの物理・接触・Animatorを破壊してから再構築する設計は、この利点を自分で消してしまいます。

## 6. VRLabs/Followerは「Coreと追従対象を分ける」先行例として面白い

OSSの比較対象として、VRLabs/Followerも確認しました。

- Repository: https://github.com/VRLabs/Follower

READMEでは、Damping ConstraintをWorld Constraint内で利用してFollowerを構成し、追従させたいオブジェクトを `Container` 配下へ置く構造になっています。

```text
Follower
|- Container
|  |- Cube
|- Look Constraint
|- Follower Target
   |- Look Target
```

さらに、READMEはFollower自体をMITで公開しています。

ここで参考にしたいのは、Constraintの具体実装ではありません。

**追従ロジックと、追従させる実体を別の階層として扱っていること**です。

VRLabs/Follower自身もQuestではunsupported components/shadersを除去する必要があると注意しており、VRChat公式ドキュメントもAndroid/QuestではUnity Constraintが無効で、VRChat Constraintsを使うよう案内しています。

- Android / Quest limitations: https://creators.vrchat.com/platforms/android/quest-content-limitations/

したがって、Followerをそのままコピーするのではなく、**境界設計の先行例**として使うのが適切です。

## 7. Walkを接続する前に、`happy_shiroi-nu_PC` を8項目だけ読む

ここまでで設計は絞れました。

次に必要なのは、公開情報を増やすことではなくUnity上の実Prefab観測です。

対象は `happy_shiroi-nu_PC`。

確認順序を次の8項目に固定します。

| # | 観測対象 | 取得する事実 |
|---|---|---|
| 1 | Rootの全Component | Avatar Descriptor / Animator / MA / VRC componentの有無 |
| 2 | Animator / Avatar Descriptor | Playable Layer、Controller参照、Avatar設定 |
| 3 | Armature全階層 | bodyRoot候補、Humanoid bone、独自bone |
| 4 | VRCPhysBone一覧 | component位置、`rootTransform`、collider参照 |
| 5 | Contact Sender / Receiver | parameter、tag、対象Transform |
| 6 | Animator Controller / Clip | idle・walk・表情・装飾のClip一覧 |
| 7 | idle / locomotion実再生 | どのTransformが実際に動くか |
| 8 | Quest版との差分 | 削除・差替されたcomponent / shader / animation |

ここで重要なのは、**名前ではなく参照関係を取ること**です。

例えば `walk.anim` という名前のClipがあっても、それだけでは採用しません。

Animator stateから参照され、実再生時に脚やBody Rootへ期待したTransform差分が出ていることを確認します。

## 8. `VelocityX/Z` は使える。ただし、先に犬側のClipを確定する

VRChatはBuilt-in Animator Parametersとして `VelocityX`、`VelocityY`、`VelocityZ`、`VelocityMagnitude` を提供しています。

- Animator Parameters: https://creators.vrchat.com/avatars/animator-parameters/

`VelocityX` は横方向速度、`VelocityZ` は前後方向速度です。

このため、Muchio Coreの移動状態をBody側locomotionへ渡す設計では、これらの値を入力に使えます。

ただし、接続順序を逆にしてはいけません。

```text
NG
VelocityX/Zがある
  -> 適当な犬Clipをwalkとして接続

OK
happy_shiroi-nu_PCのAnimatorを観測
  -> locomotionで実際に使われるClipを特定
  -> Transform差分を再生確認
  -> BodyProfile.walkClipへ登録
  -> Coreの移動状態と接続
```

**先に「どのClipが犬の正しい歩行か」を確定し、その後でCoreへ結ぶ。**

これがPhase 2の実装仕様を固定する最後の観測になります。

## 9. PC / Questは「Body互換」と「Muchio機能互換」を分ける

もう1つ、境界を分けておく必要があります。

「幸せのしろい～ぬ」は商品ページ上、PC / Android / iOS対応です。

一方、ムチォの現行商品ページはPC版VRChatでOSCを利用し、**Quest単体では喋らない**と明記しています。

したがって、次の2つを同じcompatibility flagにしてはいけません。

```text
Body platform support
  happy_shiroi-nu: PC / Android / iOS

Muchio speech support
  PC VRChat + Windows app + OSC
```

Quest版Body Adapterを作る場合も、「犬モデルが表示・動作する」と「ムチォの会話機能が動く」は別のAcceptance Criteriaにします。

## 10. 実装を開始してよい条件

`happy_shiroi-nu_PC` をMuchio化するPhase 2は、次が揃ってから開始します。

- [ ] Root component inventoryが取れている
- [ ] Armature階層が保存されている
- [ ] 全PhysBoneと`rootTransform`を列挙できている
- [ ] 全Contact Sender / Receiverを列挙できている
- [ ] Animator ControllerとClip一覧が取れている
- [ ] idle時に動くTransformを確認している
- [ ] locomotion時に動くTransformを確認している
- [ ] PC / Quest差分を確認している
- [ ] `BodyProfile.idleClip` を確定している
- [ ] `BodyProfile.walkClip` を確定している
- [ ] 元Bodyの既存挙動をAdapter側で二重実装していない

この時点で初めて、

```text
Muchio Core walk state
        ↓
BodyProfile.walkClip
        ↓
happy_shiroi-nu_PC locomotion
```

を接続します。

## 11. 以前のMuchio連携でも、同じ境界問題に当たっていた

実は、Muchioを別システムへ接続するときにも似た判断をしています。

`KAFKA2306/vlog` では、VRCPet/MuchioのログをHuman Memoryへ取り込む際、ペットログそのものを「記憶」にせず、read-onlyなobservation sourceとして分離しました。

- Issue #27: https://github.com/KAFKA2306/vlog/issues/27
- PR #28: https://github.com/KAFKA2306/vlog/pull/28

今回も構造は同じです。

```text
ログ統合
VRCPet observation != Human Memory

Body統合
Body behavior != Muchio Core
```

境界を消すと、短期的には実装量が減ります。

しかし、2体目、3体目を追加した瞬間にモデル固有処理がCoreへ漏れ始めます。

逆に、境界を維持できれば、Coreは一つのままBodyProfileだけを増やせます。

## 結論：やるべきことは「犬へ置換」ではなく「犬を壊さず接続」だった

現行BOOTHを確認したことで、最初の仮説は更新されました。

ムチォにはすでにオリジナルペット作成の導線があります。そして「幸せのしろい～ぬ」は、Humanoid、Animator、耳や尻尾の挙動、クロスプラットフォーム対応を持った完成済みのBodyです。

だから、`PetMount/muchio` を雑に犬へ置換するのは順序が逆です。

先に `happy_shiroi-nu_PC` のPrefabを読み、既存機能を棚卸しする。

そのうえで、Muchio Coreから必要な意味だけを `BodyProfile` 経由で渡す。

**Body Adapterの仕事は身体機能を再実装することではない。完成済みBodyの挙動を保存したまま、Coreとの最小接続点を定義すること。**

次の作業は、公開情報収集ではなく `happy_shiroi-nu_PC` の実Prefab監査です。

## 検証に使った一次情報

- ムチォ v1.3.6 商品ページ: https://booth.pm/ja/items/8657397
- 幸せのしろい～ぬ 商品ページ: https://booth.pm/ja/items/8446507
- Modular Avatar / Merge Armature: https://modular-avatar.nadena.dev/docs/reference/merge-armature
- Modular Avatar / Merge Animator: https://modular-avatar.nadena.dev/docs/reference/merge-animator
- Modular Avatar / clothing tutorial: https://modular-avatar.nadena.dev/docs/tutorials/clothing
- VRChat / Avatar Components: https://creators.vrchat.com/avatars/avatar-components/
- VRChat / PhysBones: https://creators.vrchat.com/common-components/physbones/
- VRChat / Contacts: https://creators.vrchat.com/common-components/contacts/
- VRChat / Animator Parameters: https://creators.vrchat.com/avatars/animator-parameters/
- VRChat / Android Content Limitations: https://creators.vrchat.com/platforms/android/quest-content-limitations/
- VRLabs/Follower: https://github.com/VRLabs/Follower
- KAFKA2306/vlog Issue #27: https://github.com/KAFKA2306/vlog/issues/27
- KAFKA2306/vlog PR #28: https://github.com/KAFKA2306/vlog/pull/28
