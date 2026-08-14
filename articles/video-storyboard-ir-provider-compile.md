---
title: "生成AIのAPI仕様が変わっても、映像の意図まで書き直さない。Storyboardを正準にする"
emoji: "🎬"
type: "tech"
topics: ["python", "ai", "architecture", "videogeneration", "testing"]
published: false
published_at: 2026-08-12 14:09
---

動画生成AIのadapterを作った2日後、記事を読み直すためにMiniMaxの現行docsを確認した。

すると、旧稿で中心にしていたAPI前提が、もう現在の公開仕様と一致していなかった。

2026年8月14日時点のMiniMax公式Video Generation guideは、video生成を次の4 modeとして説明している。

```text
Text-to-Video
Image-to-Video
First-and-Last-Frame Video
Subject-Reference Video
```

- Current Video Generation guide: https://platform.minimax.io/docs/guides/video-generation
- First & Last Frame API: https://platform.minimax.io/docs/api-reference/video-generation-fl2v
- Subject-Reference API: https://platform.minimax.io/docs/api-reference/video-generation-s2v

First & Last Frameは現在 `MiniMax-Hailuo-02` を使う専用contractとして公開され、Subject-Referenceは `subject_reference` を使う別modeとして案内されている。

旧稿はMiniMax H3 V2の `content[]` contractを現在仕様のように説明していたため、その部分を残さない。

一方で、実装した **Storyboard IR** は捨てなくてよかった。

なぜならStoryboard側にはMiniMaxのendpoint名もKlingのrequest fieldも入れていなかったからだ。

```text
映像として何を作りたいか
        ↓
Storyboard IR
        ↓
provider-specific compiler
        ↓
current provider request
```

この記事で扱うのはAPI差分の暗記ではない。

**生成AIを替えたり仕様が更新されたりしても、人間が書いた映像意図までprovider都合で作り直さないための設計**について書く。

## 実装は両方merge済み。でもlive generation成功とは呼ばない

2026年8月12日に作った2つのadapterは現在どちらもmerge済みである。

### Kling

- PR #1: https://github.com/KAFKA2306/kling/pull/1
- merge commit: https://github.com/KAFKA2306/kling/commit/1e014f7da47bc162afd90076ad67b66c97ba4543

PRでは、provider-neutralな `VideoStoryboard` / `Shot` から、現在のrepository request modelでlosslessに表現できる範囲だけをcompileする。

- no reference → Text-to-Video plan
- first frame + optional last frame → Image-to-Video plan
- 1–4 reference images → Multi-Image plan
- unsupported reference video/audio → fail
- provider-incompatible duration → fail

ただしtestsはfake client boundaryまでで、real Kling API callは行っていない。

### MiniMax

- PR #56: https://github.com/KAFKA2306/2511youtuber/pull/56
- merge commit: https://github.com/KAFKA2306/2511youtuber/commit/fea2a741cad9285f256bb11954e7caf10769636d

このPRもStoryboard IR、timeline validation、deterministic compiler、provider adapter、audit structureをmainへmerge済みである。

ただしPR本文自身が、verification boundaryを**deterministic request compilation / mocked / fail-closed**までとし、MiniMaxへのlive callやYouTube publishは行っていないと明記している。

つまり現在確認済みなのは、

```text
IRを作れる
validationできる
provider requestへcompileできる
unsupported intentを止められる
```

まで。

```text
実動画が高品質に生成できた
live APIが現在のprovider仕様でもそのまま通る
公開まで成功した
```

とは扱わない。

## provider-neutralにするのはpromptではなく「意図」

最初は共通interfaceを、

```python
generate_video(
    provider="...",
    prompt="...",
    duration=10,
)
```

くらいにしたくなる。

しかし動画の意味はprompt文字列の外にもある。

- 何秒から何秒までか
- 何を見せるか
- camera/composition
- subject state
- motion
- first / last frame
- reference asset
- 維持したいstyle
- 禁止したい表現
- source evidence

そこでStoryboard側へ、provider APIではなくcreative intentを置く。

```python
Shot(
    shot_id="s01",
    start_sec=0,
    end_sec=4,
    message="新製品の主役を見せる",
    composition="close-up",
    subject_state="front-facing",
    reference_asset_ids=["hero"],
    negative_constraints=["no extra text"],
)
```

ここには、

```text
MiniMax endpoint
Kling endpoint
provider model ID
request JSON field
```

を入れない。

**人間が変えたいのは映像意図で、provider fieldではない。**

## current MiniMax docsが分かれていること自体が、IRの必要性を示す

現行MiniMax guideは同じvideo generationでも複数modeを持つ。

First & Last Frameでは、

```text
first_frame_image
last_frame_image
prompt
model = MiniMax-Hailuo-02
```

というcontractがある。

Subject Referenceでは、

```text
subject_reference
prompt
model = S2V-01
```

という別のcontractがある。

利用者の意図としては、

```text
最初はこの絵
最後はこの絵
この人物らしさを維持
```

と自然に書ける。

しかしselected provider/modeが、その3つを同時にlosslessに表現できるとは限らない。

ここでadapterが勝手に1つを捨てると、APIは成功しても別の映像になる。

だからcompile結果は、

```text
representable
```

か、

```text
capability mismatch
```

にする。

**「だいたい近いrequest」へ丸めない。**

## API errorよりcompile errorの方が、利用者には分かりやすい

providerへ送ってから失敗すると、原因候補が増える。

```text
network
credential
quota
model availability
request shape
unsupported combination
creative intent itself
```

一方、requestを作る前なら、

```text
このShotはselected modeでは表現できない
```

と短く返せる。

例えば、

```python
raise CapabilityMismatch(
    provider="minimax",
    requested_roles=["first_frame", "last_frame", "subject_reference"],
    reason="selected compile target cannot preserve all roles losslessly",
)
```

のようにする。

これなら利用者は、

- modeを変える
- referenceを減らす
- Shotを分ける
- providerを変える

のどれかを選べる。

**remote taskを作る前に、設計上の不可能を人間が理解できる。**

## IR自身の矛盾はproviderより前で止める

providerが何であっても壊れているStoryboardもある。

実装では、例えば次をIR validationで止める。

- `end_sec <= start_sec`
- Shot overlap
- total duration overflow
- forbidden gap
- unknown reference asset
- duplicate Shot ID
- one-shot-one-message違反

```python
if shot.start_sec < previous_end:
    raise ValueError("overlaps the previous shot")
```

これをprovider adapterへ置かない理由は単純だ。

**KlingでもMiniMaxでも壊れているから。**

validation responsibilityを、

```text
creative / timeline invariant
→ IR

provider capability
→ compiler / adapter

network / remote task
→ provider client
```

へ分ける。

## reference assetにはURIだけでなくroleを持たせる

同じ画像でも、

```text
first frame
last frame
reference image
subject reference
```

では意味が違う。

単なる `images: list[str]` へすると、provider変換時にその意味が消える。

だからIRでは、asset identityとcreative roleを分ける。

```text
asset_id = hero
kind = image
role = first_frame
```

provider compilerはこのroleを見て、current provider modeへmapできるか判断する。

mapできなければfailする。

**URLを運ぶのではなく、意図を運ぶ。**

## provider仕様が変わったら、adapterだけを更新する

今回の再監査で一番分かりやすかった点である。

旧MiniMax adapterは、merge時点のH3 V2 contractを実装している。

2026年8月14日の現行docsは別のmodel/mode構成を案内している。

ここでStoryboardまでprovider-specificだったら、既存のShot dataやauthoring UIまで作り直す必要がある。

IRが中立なら、更新対象を狭くできる。

```text
Storyboard data        unchanged
Editorial authoring    unchanged
Timeline validation    unchanged
Asset role semantics   unchanged

MiniMax compiler       update required
Provider tests         update required
Live verification      required
```

**仕様変更のblast radiusをadapterへ閉じ込める。**

これはvendor lock-inを完全になくすという話ではない。

provider固有能力を使うほど差は出る。

それでも「人間が何を作りたかったか」を別layerに残しておけば、migration時に失うものを明示できる。

## compilerはversionとevidenceを残す

動画生成自体は非決定的でも、その前のcompileは決定的にできる。

```yaml
storyboard_id: demo-001
provider: minimax
provider_contract_observed_at: 2026-08-14
compiler_version: ...
compile_status: ...
request_summary: ...
source_evidence:
  - current MiniMax video guide
```

live callまで行った場合は、さらに、

```text
task ID
response
artifact hash
runtime verification
```

を別stateとして追加する。

`compile passed` を `generation succeeded` へ昇格しない。

## current docsへ追従できていないadapterを「対応済み」と表示しない

今回、MiniMax PR #56がmerge済みであること自体は事実である。

しかし、merge済み = current API validatedではない。

現行provider docsとadapter contractがずれているなら、stateを分ける。

```yaml
implementation:
  merged: true

provider_contract:
  current_docs_rechecked: true
  adapter_currently_revalidated: false

live_generation:
  status: NOT_RUN
```

この表示なら、

> コードはあるが、現在のproviderへそのまま投入してよいとはまだ言えない

と分かる。

これもUXである。

**「対応済み」の1bitより、どこまで確認済みかを見せる。**

## provider変更時のdecision matrix

新しいprovider/modeへ移るとき、次の表を作るとよい。

| Intent | IRに保持 | Target providerで表現可能 | Action |
|---|---|---|---|
| text message | yes | yes | compile |
| first frame | yes | yes | compile |
| last frame | yes | mode-dependent | select mode / fail |
| subject identity | yes | mode-dependent | select mode / fail |
| reference video | yes | adapter-dependent | fail if lossless mappingなし |
| exact duration | yes | provider-dependent | fail / split shot |

ここで重要なのは、`no` を自動で消さないことだ。

**差分を人が選べる状態にする。**

## この設計で減らしたいのは、API errorより書き直し

もちろんcompile-time validationでremote failureも減らせる。

しかし長期的な価値は別にある。

動画生成providerは変わる。

model名も、endpointも、request fieldも変わる。

そのたびに、

```text
台本
Shot設計
referenceの意味
editorial intent
```

までprovider仕様に引きずられて書き直すのは重い。

だから、

```text
what to create
```

と、

```text
how this provider accepts it today
```

を分ける。

今回、旧稿のMiniMax仕様がもう現行docsと違っていたことで、その設計価値がむしろ明確になった。

**APIが変わることを防ぐのではなく、APIが変わっても創作意図まで巻き込まれない構造にする。**

## 2026年8月14日時点の一次情報・実装証拠

MiniMax current docs:

- Video Generation guide: https://platform.minimax.io/docs/guides/video-generation
- First & Last Frame: https://platform.minimax.io/docs/api-reference/video-generation-fl2v
- Subject-Reference: https://platform.minimax.io/docs/api-reference/video-generation-s2v

Repository evidence:

- Kling PR #1: https://github.com/KAFKA2306/kling/pull/1
- Kling merge commit: https://github.com/KAFKA2306/kling/commit/1e014f7da47bc162afd90076ad67b66c97ba4543
- MiniMax PR #56: https://github.com/KAFKA2306/2511youtuber/pull/56
- MiniMax merge commit: https://github.com/KAFKA2306/2511youtuber/commit/fea2a741cad9285f256bb11954e7caf10769636d
