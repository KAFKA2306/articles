---
title: "ドラムの3Dアニメで、音が合っても叩く場所がずれる"
emoji: "🥁"
type: "tech"
topics: ["blender", "3d", "アニメーション", "gltf", "自動化"]
published: false
---

ハイハットの音が鳴った瞬間にスティックは落ちています。手元を寄って見ると、先端が触れたのはスネア。音と腕の動きがそろって見えても、叩く場所の間違いは残ります。3Dキャラクターに演奏させるなら、音が鳴る時刻と、どの打面に触れたかをそれぞれ確かめると、直す工程が分かります。

Blenderでこのずれを意図的に作り、GLBに書き出してから読み戻しました。三打とも時刻が合った版でも、打面まで合ったのは二打でした。

## 同じ三打で、時刻と打面を一つずつずらす

30 fpsのBlender 4.3.2で、スネアとハイハットを二つの座標に置き換えました。正解は10フレーム目にスネア、20フレーム目にハイハット、30フレーム目にスネアです。正解表を音源の代わりに使い、スティック先端を表すオブジェクトを動かして、GLBを新規シーンに読み込んでから、各フレームで先端と打面の距離を測りました。距離が1 cm未満のフレームを接触として数えています。 [BlenderのglTF入出力仕様](https://docs.blender.org/manual/en/4.3/addons/import_export/scene_gltf2.html)

| GLBに入れた動き | 時刻が一致 | 打面が一致 | 両方が一致 |
| --- | ---: | ---: | ---: |
| 正解どおり | 3/3 | 3/3 | 3/3 |
| 二打目をスネアに変更 | 3/3 | 2/3 | 2/3 |
| 二打目を2フレーム遅らせる | 2/3 | 3/3 | 2/3 |

この実験は、各テイクの三打を順番に対応させた単純な例です。実際の曲では打ち漏れ、余分な打撃、同時打ちが入るので、先に許容時間内で一対一に対応付け、余った打撃も数えます。タイミングだけの精度と打面込みの精度を両方出すと、正しい時刻に別の楽器を叩いた例を拾えます。

## 打面の判定と、手をそこまで動かす処理

「元音源 → 打音の時刻と打面 → スティックの接触 → 書き出し後の接触」の順に確認します。採譜の段階でスネアとハイハットが逆なら、直すのは採譜や打面の割り当てです。採譜が合っていて先端だけが外れるなら、腕の動きや接触補正を調べます。Blender内で合っていて出力先だけでずれるなら、ベイク、読み込み、再生時の補間を調べます。

同じ「時刻・動かす部位・対象点」を、全身動作の入力と出力後の検査に渡すと、どの工程でずれたか追えます。ベースなら音が鳴る時刻と押弦する位置、足運びなら接地の区間と床上の位置に置き換えられます。音源だけがあるときの弦・フレットは、元演奏の断定を避け、調弦と前後の運指に合う演奏案として扱います。 [ベースの音声入力と運指割り当ての実装](https://github.com/scottvr/gtrsnipe/blob/main/README.md)

## 制作パイプラインに組み込む

短い定型モーションなら、打面と時刻からキーフレームを組み、手足の接触を決めます。体の揺れや踏み替えまで含むシーンなら、同じイベント列から要所の姿勢を作って全身動作の候補を生成し、納品先の骨格で接触を補正します。候補を比較するときは、キャラクター、イベント列、カメラ条件をそろえます。

素材と骨格にはTripo P2とAuto Rigの公式API、音源しかないドラムの採譜にはDrumScript、全身動作には手足の位置・姿勢を条件にできるKimodoのCLIを使う構成が考えられます。Blenderのバックグラウンド実行で補正・ベイク・検査を回し、ゲーム用の納品では対象エンジンの再生結果を測ります。ここで実測したのは座標で表した打面への接触と、BlenderのGLB往復です。採譜、全身動作生成、別エンジンへの受け渡しは検証対象です。 [Tripo P2](https://developers.tripo3d.com/en/models/p2) · [Auto Rig](https://developers.tripo3d.com/en/docs/animations-rig) · [DrumScript](https://github.com/DrumScript/DrumScript) · [Kimodo CLI](https://research.nvidia.com/labs/sil/projects/kimodo/docs/user_guide/cli.html)

自動化では、各工程に渡すファイルとツールの版を固定し、採譜を直したら該当区間の動作以降を再計算します。接触距離と同期誤差はスクリプトで判定し、演出の評価には短いプレビューと意図した拍を渡します。現行手順と比べるときは、誤った打面や遅れを通した件数と、検査を通った一件あたりのトークンを集計します。映像を一から作り直す前に、まず一打だけずらした対照例を通し、どの工程で落ちるか確かめられます。

## GLBの読み戻しを再現する

下のコードを `drum-contact.py` に保存し、`blender --background --factory-startup --python-exit-code 1 --python drum-contact.py` で実行します。各行の出力は、時刻一致、打面一致、両方一致の順です。一時GLBは実行後に消えます。

```python
import bpy
import tempfile
from pathlib import Path

FPS = 30
PADS = {"snare": (0, 0, 0), "hihat": (1, 0, 0)}
EXPECTED = [(10, "snare"), (20, "hihat"), (30, "snare")]

def score(name, strikes, dest):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.unit_settings.system = "METRIC"
    scene.frame_start, scene.frame_end = 1, 31
    tip = bpy.data.objects.new("StickTip", None)
    scene.collection.objects.link(tip)
    for frame, pad in strikes:
        x, y, z = PADS[pad]
        for offset, lift in [(-1, 0.15), (0, 0), (1, 0.15)]:
            tip.location = (x, y, z + lift)
            tip.keyframe_insert(data_path="location", frame=frame + offset)
    path = str(dest / f"{name}.glb")
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    bpy.ops.import_scene.gltf(filepath=path)
    tip = bpy.data.objects["StickTip"]
    actual = []
    for frame in range(1, 32):
        scene.frame_set(frame)
        x, y, z = tip.matrix_world.translation
        for pad, (px, py, pz) in PADS.items():
            distance_squared = (x - px) ** 2 + (y - py) ** 2 + (z - pz) ** 2
            if distance_squared < 0.01 ** 2:
                actual.append((frame, pad))
    assert len(actual) == len(EXPECTED), actual
    pairs = list(zip(EXPECTED, actual))
    times = sum(f == got for (f, _), (got, _) in pairs)
    pads = sum(p == got for (_, p), (_, got) in pairs)
    both = sum(expected == observed for expected, observed in pairs)
    print(f"RESULT {name} {times}/3 {pads}/3 {both}/3 {actual}", flush=True)

with tempfile.TemporaryDirectory() as tmp:
    dest = Path(tmp)
    score("baseline", EXPECTED, dest)
    score("wrong-pad", [(10, "snare"), (20, "snare"), (30, "snare")], dest)
    score("late-hit", [(10, "snare"), (22, "hihat"), (30, "snare")], dest)
```
