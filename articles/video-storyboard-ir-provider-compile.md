---
title: "動画生成APIを直接叩くのをやめた：Storyboard IRでKlingとMiniMaxの仕様差をコンパイル時に止める"
emoji: "🎬"
type: "tech"
topics: ["python", "ai", "architecture", "videogeneration", "testing"]
published: true
published_at: 2026-08-12 14:09
---

動画生成APIを増やすほど、コードは「似ているのに同じではない」仕様差に侵食されます。

Text-to-Video、Image-to-Video、First/Last Frame、複数参照画像、参照動画、参照音声。さらに provider ごとに duration、aspect ratio、media count、prompt length、endpoint が違う。そこでAPIごとに `if provider == ...` を増やしていくと、最後に壊れるのは動画そのものではなく、**「この台本を、どの制約で、どうAPIへ変換したか」を説明できる能力**です。

今回、動画生成系の実装で、台本からAPI requestへ直接落とす線をやめ、間に provider-neutral な **Storyboard IR（Intermediate Representation / 中間表現）** を置きました。

結論はこれです。

> **生成APIの差異を runtime のAPIエラーとして受け取るのではなく、Storyboard → Provider Request の compile error として先に止める。**

Kling 側の Storyboard adapter は merge 済みです。MiniMax-H3 V2 adapter は Draft PR として実装・テスト中で、この記事では **live generation を実行済みとは扱いません**。

実装証拠:

- Kling merged PR: https://github.com/KAFKA2306/kling/pull/1
- Kling merge commit: https://github.com/KAFKA2306/kling/commit/1e014f7da47bc162afd90076ad67b66c97ba4543
- MiniMax Draft PR: https://github.com/KAFKA2306/2511youtuber/pull/56
- MiniMax Storyboard implementation: https://github.com/KAFKA2306/2511youtuber/blob/feat/storyboard-ir-minimax-h3/src/storyboard.py
- MiniMax provider implementation: https://github.com/KAFKA2306/2511youtuber/blob/feat/storyboard-ir-minimax-h3/src/providers/video_generation.py

公式仕様:

- MiniMax-H3 V2 Create: https://platform.minimax.io/docs/api-reference/video-generation-v2-create
- MiniMax-H3 V2 Query: https://platform.minimax.io/docs/api-reference/video-generation-v2-query
- Kling VIDEO 3.0 User Guide: https://app.klingai.com/cn/quickstart/klingai-video-3-model-user-guide

## 1. 問題：動画生成APIは「prompt文字列」だけでは抽象化できない

最初は、provider adapter をこれくらいにしたくなります。

```python
generate_video(
    provider="...",
    prompt="...",
    duration=10,
)
```

しかし実際の差は prompt の外側にあります。

MiniMax-H3 V2 の公式Create APIは `content[]` に text / image / video / audio を入れ、各mediaに `role` を付けます。Text-to-Videoでは concrete ratio が必要で、Image-to-Videoでは画像から比率が決まり `adaptive` 扱いになります。また first/last frame と reference media は混在できません。

一方、今回 merge した Kling adapter は、既存SDKの request model が表現できる範囲に限定して、Storyboardを `text_to_video` / `image_to_video` / `multi_image_to_video` の3 routeへ compile します。現行adapterで保持できない `reference_video` / `reference_audio` は捨てずにエラーにします。

つまり共通化すべきものはAPI requestではありません。**映像として何を作りたいか**です。

この図で見るべき点は、Script と provider API の間に Storyboard IR を置き、provider差を adapter に閉じ込めていることです。

![Storyboard IR boundary](/images/video-storyboard-ir-provider-compile/01-ir-boundary.png)

## 2. 設計判断：Storyboardを「映像の意図」の正準形にする

Storyboard IR の中心は `VideoStoryboard` と `Shot` です。

`Shot` は単なる自然言語ではなく、少なくとも次を持ちます。

- `shot_id`
- `start_sec`, `end_sec`
- `message`
- `composition`
- `subject_state`
- `motion[]`
- `typography[]`
- `style_invariants[]`
- `reference_asset_ids[]`
- `negative_constraints[]`
- `source_evidence_ids[]`

ここで重要なのは、**provider-specific field を入れないこと**です。

Klingのendpoint名も、MiniMaxの`content[]`もStoryboard側には置きません。Storyboardは「何秒から何秒まで、何を伝え、何を参照し、何を維持するか」だけを表します。

この図で見るべき点は、Shotが長いprompt paragraphではなく、時間・メッセージ・参照・根拠を持つ機械検証可能な契約になっていることです。

![Shot contract](/images/video-storyboard-ir-provider-compile/02-shot-contract.gif)

## 3. 原因：runtimeまで待つと、間違いの責任範囲が広すぎる

provider APIへ直接requestすると、例えば12秒動画を要求して失敗したとき、原因候補が広がります。

- providerが12秒を受け付けない
- endpointが違う
- aspect ratioが違う
- first/last frameとreference mediaを混在させた
- shot timeline自体が重複している
- prompt compilerが壊れている
- network/authenticationの問題

そこで、まず provider に依存しない矛盾をIR生成時に落とします。

実装では以下を validation error にしています。

- shotの `end_sec <= start_sec`
- storyboard全体のduration超過
- shot overlap
- `gap_policy="forbid"` なのに空白区間がある
- unknown reference asset
- duplicate shot ID / asset ID

例えば 0–5秒のShot Aと4–8秒のShot Bは、network requestへ到達しません。

この図で見るべき点は、timelineの矛盾をAPI側の400エラーにせず、ローカルのschema validationで止めることです。

![Timeline fail close](/images/video-storyboard-ir-provider-compile/03-timeline-fail-close.gif)

実装の考え方は単純です。

```python
if shot.start_sec < previous_end:
    raise ValueError("overlaps the previous shot")
```

このチェックはKlingにもMiniMaxにも関係ありません。だからIR側に置きます。

## 4. 失敗：1つのShotに複数の論点を詰めると、provider以前に崩れる

生成動画のpromptを組み立てていると、1 Shotの `message` に箇条書きを詰めたくなります。

しかしそれを許すと、「1ショットで何を見るべきか」が不明になります。さらにproviderがmulti-shot narrativeを理解できる場合でも、こちらのタイムラインとprovider内部のshot分解が二重化します。

そこで `Shot.message` は1 non-empty lineに限定しました。list-like patternもrejectします。

```python
nonempty_lines = [
    line.strip()
    for line in self.message.splitlines()
    if line.strip()
]
if len(nonempty_lines) != 1:
    raise ValueError("one-shot-one-message")
```

この図で見るべき点は、「1図1メッセージ」と同じ原則を動画のShot contractへ持ち込んでいることです。

![One shot one message](/images/video-storyboard-ir-provider-compile/04-one-shot-one-message.gif)

これは生成品質を保証する魔法ではありません。狙いは、**失敗したときにどのShotの意味が曖昧だったかを特定できること**です。

## 5. Reference asset は URI ではなく「役割」を持たせる

画像URLを単純な `images: list[str]` にすると、provider変換時に意味が消えます。

同じ画像でも、

- first frame
- last frame
- reference image

では意味が違います。

そのため `ReferenceAsset` は `kind` と `role` を分離しています。

```python
AssetKind = Literal["image", "video", "audio"]
AssetRole = Literal[
    "first_frame",
    "last_frame",
    "reference_image",
    "reference_video",
    "reference_audio",
]
```

さらに role と kind が矛盾したらrejectします。

この図で見るべき点は、「ファイルの種類」と「生成上の役割」を別フィールドにし、組み合わせをvalidationしていることです。

![Asset role matrix](/images/video-storyboard-ir-provider-compile/05-asset-role-matrix.gif)

ここまでが provider-neutral contract です。

## 6. MiniMax-H3：公式V2仕様をadapterで検証してから `content[]` へ落とす

MiniMax-H3 V2 の公式Create APIでは、2026年8月12日時点で以下が確認できます。

- endpoint: `POST /v2/video_generation`
- model: `MiniMax-H3`
- `content[]` は text / image_url / video_url / audio_url
- promptとなる non-empty text item が必須
- resolution: `768P` または `2K`
- duration: 整数4–15秒
- Text-to-Videoはconcrete ratio必須
- first/last-frame mode と reference mode は排他的
- reference imageは最大9
- reference videoは最大3
- reference audioは最大3
- reference video/audioの合計durationは15秒以下

これらは公式Create docsに明記されています。

https://platform.minimax.io/docs/api-reference/video-generation-v2-create

adapterはStoryboardを受け取り、まずこれらをvalidateしてからrequestへcompileします。

```python
request = {
    "model": "MiniMax-H3",
    "content": content,
    "resolution": storyboard.resolution_target,
    "duration": int(storyboard.duration_seconds),
    "ratio": ratio,
}
```

この図で見るべき点は、IRのreference roleを、その意味を保持したままMiniMaxのtyped `content[]` に変換していることです。

![MiniMax compile](/images/video-storyboard-ir-provider-compile/06-minimax-compile.gif)

ここでAPIを呼ばない `compile_request()` を独立させているのが重要です。

API keyが無くてもrequest shapeまではテストできます。live call は `create_task()` 側で `MINIMAX_API_KEY` を要求します。

## 7. Kling：同じStoryboardから3つのrequest modeへcompileする

Kling側は merge 済みの `KlingStoryboardCompiler` が、reference semanticsから routeを決定します。

- referenceなし → Text-to-Video
- first frame + optional last frame → Image-to-Video
- 1–4 reference images → Multi-Image-to-Video

実装:

https://github.com/KAFKA2306/kling/blob/master/usecases/storyboard.py

この図で見るべき点は、呼び出し側がendpointを選ぶのではなく、Storyboardの意味からcompilerがrouteを決めることです。

![Kling compile modes](/images/video-storyboard-ir-provider-compile/07-kling-compile-modes.gif)

なお、Klingの公式VIDEO 3.0 user guideは現在、multi-shot、15秒、element reference、native audioなど広い製品能力を説明しています。

https://app.klingai.com/cn/quickstart/klingai-video-3-model-user-guide

ただし、**今回のadapterがその最新製品能力をすべて表現しているとは扱っていません。**

mergeしたadapterは「このrepoの現在のrequest modelがlosslessに表現できる範囲」に限定しています。この区別は重要です。

## 8. Provider capability mismatch は「丸める」のではなく止める

最も危険なのは、adapterが親切に見える変換をすることです。

例えば Kling adapter の現行request modelが5秒または10秒しか受け付けないとき、Storyboardが12秒なら10秒へ丸めることもできます。

今回はしません。

```python
if duration not in {5, 10}:
    raise ValueError(
        "current Kling request models support exact durations of 5 or 10 seconds"
    )
```

reference video/audioも同じです。現行adapterがそのroleを保持できないなら、黙ってdropせずrejectします。

この図で見るべき点は、「近いrequestに変換する」より「意味を保存できないならcompile失敗」を優先していることです。

![Capability mismatch](/images/video-storyboard-ir-provider-compile/08-capability-mismatch.gif)

これは地味ですが、後から再現性を守る上で効きます。

12秒Storyboardを10秒動画として生成してしまうと、生成は「成功」しても、設計上は別物です。

## 9. 検証：同じIRから同じprompt/requestが生成されることをテストする

生成AIは非決定的でも、**生成前のcompileは決定的にできます。**

MiniMax側のテストでは、12秒・5 shot fixtureについて同じStoryboardを2回compileし、prompt一致を確認しています。

Kling側でも同じStoryboardから同じ `KlingStoryboardPlan` が出ることをテストしています。

さらに audit に以下を残す設計にしました。

- storyboard ID
- provider
- model
- request parameters
- compiled prompt
- task ID
- response
- compiler version
- generated artifact hash

この図で見るべき点は、非決定的な動画生成の手前に、決定的に監査できるcompile chainを作っていることです。

![Audit chain](/images/video-storyboard-ir-provider-compile/09-audit-chain.gif)

ここで `artifact hash` を残す理由は、同じtask IDやURLだけでは、後から取得したbytesが同一か確認できないからです。

## 10. 検証境界：mocked API successを「動画生成成功」と呼ばない

今回の実装で最も明示したかった失敗は、テストの成功範囲を拡大解釈することです。

Kling merged PRのテストは `FakeClient` を使い、compiled endpointとpayloadがclientへ渡ることを確認します。実network callはしません。

MiniMax Draft PRでも `compile_request()` はnetworkなしで検証し、API keyなしの `create_task()` はfailします。

したがって現時点で言えるのは、

**確認済み**
- Storyboard schema validation
- timeline validation
- one-shot-one-message lint
- provider request compilation
- deterministic compilation
- fake/mock client boundary

**この記事の根拠からは言えない**
- 実MiniMax生成成功
- 実Kling生成成功
- 生成動画の品質改善率
- YouTube公開成功

です。

この図で見るべき点は、compile-time contractの成功とlive generationの成功を別のEvidenceとして扱っていることです。

![Verification boundary](/images/video-storyboard-ir-provider-compile/10-verification-boundary.gif)

## 11. 再現方法

### Kling側

merge済み実装を確認します。

```bash
git clone https://github.com/KAFKA2306/kling.git
cd kling
git checkout 1e014f7da47bc162afd90076ad67b66c97ba4543
pytest -q tests/test_storyboard_adapter.py
```

見るべきテストは次です。

- deterministic Text-to-Video plan
- first/last frame → Image-to-Video
- reference images → Multi-Image
- incompatible duration → fail
- unsupported reference video → fail
- last frame without first frame → fail
- fake client submit

### MiniMax側

現時点ではDraft PRなので、PR headを取得してテストします。

```bash
git clone https://github.com/KAFKA2306/2511youtuber.git
cd 2511youtuber
git fetch origin pull/56/head:storyboard-ir-minimax-h3
git checkout storyboard-ir-minimax-h3
pytest -q tests/test_storyboard_video_generation.py
```

MiniMax公式仕様と突き合わせる場合は、必ず現行docsを確認します。

- Create: https://platform.minimax.io/docs/api-reference/video-generation-v2-create
- Query: https://platform.minimax.io/docs/api-reference/video-generation-v2-query

## 12. 何が失敗だったか

今回の設計で避けたかった失敗は3つです。

### 失敗1：provider requestを正準データモデルにする

provider Aのfieldを正準にすると、provider Bを追加した瞬間に`Optional` fieldだらけになります。

解決は、provider-neutral IRとprovider adapterの分離です。

### 失敗2：対応できない仕様を近似して通す

12秒→10秒の丸めや、reference audioのdropは、API requestとしては通っても映像意図を変えます。

解決はfail-closeです。

### 失敗3：mock testをE2E成功と書く

request compileが正しくても、auth、rate limit、provider runtime、生成品質は別問題です。

解決はverification boundaryを明記することです。

## 13. 実務で使う最小チェックリスト

新しい動画providerを追加するとき、まず次を埋めます。

| 質問 | 置く場所 |
|---|---|
| Shotは何秒から何秒か | Storyboard IR |
| 1 Shotで何を伝えるか | Storyboard IR |
| 参照mediaの意味は何か | ReferenceAsset.role |
| timelineにgap/overlapを許すか | Storyboard validation |
| providerのduration制約 | Provider adapter |
| providerのratio制約 | Provider adapter |
| providerで表現できないrole | compile error |
| API endpoint/payload | Provider adapter |
| requestを再現できるか | deterministic compiler |
| live callしたか | audit / verification evidence |

## まとめ

動画生成providerを増やすとき、共通化する対象を「API request」にすると苦しくなります。

共通化すべきなのは、

**何を、いつ、どの参照素材を使い、どの制約を守って見せたいか**

という映像の意図です。

その意図をStoryboard IRとして固定し、

```text
Script
  -> Storyboard IR
  -> Validation
  -> Provider Compiler
  -> Provider Request
  -> Generation
  -> Audit
```

に分ける。

するとprovider差は「巨大なif文」ではなく「compile contract」になります。

特に有効だった原則は3つです。

1. **providerに依存しない矛盾はIRで止める**
2. **providerで意味を保存できない場合はfail-closeする**
3. **compile成功とlive generation成功を別のEvidenceとして扱う**

生成AIが非決定的でも、その手前の設計・変換・検証まで非決定的にする必要はありません。

---

## 参照した一次情報

- MiniMax-H3 V2 Create Video Generation Task  
  https://platform.minimax.io/docs/api-reference/video-generation-v2-create
- MiniMax-H3 V2 Query Task  
  https://platform.minimax.io/docs/api-reference/video-generation-v2-query
- Kling VIDEO 3.0 Model User Guide  
  https://app.klingai.com/cn/quickstart/klingai-video-3-model-user-guide
- KAFKA2306/kling PR #1  
  https://github.com/KAFKA2306/kling/pull/1
- KAFKA2306/kling merge commit  
  https://github.com/KAFKA2306/kling/commit/1e014f7da47bc162afd90076ad67b66c97ba4543
- KAFKA2306/2511youtuber PR #56  
  https://github.com/KAFKA2306/2511youtuber/pull/56

## LAPRAS AI Review 5軸セルフレビュー

- **論理性**: API差異という問題から、IR分離、compile validation、provider adapter、verification boundaryまで因果を一本化した。
- **実用性**: 実装field、validation例、provider compile例、再現コマンド、チェックリストを含めた。
- **読みやすさ**: 10図を「構造→契約→失敗→provider変換→監査→検証境界」の順に配置した。
- **独自性**: 実際にmergeされたKling adapterと、進行中MiniMax adapterの仕様差を同一IRから比較した。
- **明確性**: merged / Draft、compile test / live call、公式provider能力 / 現行repo adapter能力を明示的に分離した。
