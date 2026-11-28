---
title: "タイミングが合っていても、動作は正しいとは限らない"
emoji: "🥁"
type: "tech"
topics: ["blender", "3d", "アニメーション", "gltf", "自動化"]
published: false
created_at: "2026-11-15"
updated_at: "2026-11-28"
---

音に合わせて腕が動くアニメーションを作ったとする。ハイハットを叩く予定の時刻にスティックは振り下ろされたが、先端が触れたのはスネアだった。時刻だけを測る検査なら、この動作を成功として扱ってしまう。

3Dモーションの正しさを一つの同期指標で判定してはならない。**イベントの時刻と、接触対象・位置は別の条件である。** Blenderで書き出したGLBを読み戻す三打の実験で、その独立性を示す。

## 一つの条件だけを壊す

Blender 4.3.2でスネアとハイハットを二つの点として表現した。30 fpsで10フレーム目にスネア、20フレーム目にハイハット、30フレーム目にスネアを叩くことを正解とした。音源や人体モデルは使わず、スティック先端に見立てたオブジェクトを動かした。

GLBへ書き出した後、空のシーンへ読み込み、先端が打面の座標から1 cm未満に入ったフレームを一打と数えた。[BlenderのglTF入出力仕様](https://docs.blender.org/manual/en/4.3/addons/import_export/scene_gltf2.html)

| 書き出した動作 | 時刻の一致 | 打面の一致 | 両方の一致 |
| --- | ---: | ---: | ---: |
| 正解どおり | 3/3 | 3/3 | 3/3 |
| 二打目の打面だけ変更 | 3/3 | 2/3 | 2/3 |
| 二打目を2フレーム遅延 | 2/3 | 3/3 | 2/3 |

時刻の検査を厳しくしても、正しい時刻に別の物体へ触れる誤りは見つからない。位置の検査だけでも、正しい物体に遅れて触れる誤りは見つからない。

この実験は人間の目がどの程度誤りを見逃すかを測ったものではない。また、三打が順番に対応する簡略モデルであり、実際の楽器の形状、接触面、同時打撃、打ち漏れ、余分な打撃は扱っていない。

## 正解をイベントとして持つ

原因を特定するには、正解を時刻だけのリストにしない。各イベントに時刻、動かす部位、触れる対象を持たせ、動作の生成と評価で共有する。

| 観測された不一致 | 最初に調べる箇所 |
| --- | --- |
| 譜面自体が誤った打面を指す | 採譜・対象の割り当て |
| 譜面は正しいが先端が外れる | 軌道・骨格・接触補正 |
| Blenderでは正しくGLBで外れる | ベイク・書き出し・読み込み後の補間 |

同じ構造はベース演奏の音高と弦・フレット、歩行の接地時刻と足裏位置にも現れる。これらへ適用する場合は、それぞれの接触条件を定義する必要があり、ドラムの点モデルをそのまま流用できるわけではない。[音声からベース運指を割り当てる実装例](https://github.com/scottvr/gtrsnipe/blob/main/README.md)も、音から物理的な演奏位置を選ぶ問題を扱っている。

## 自分の検査器に一件だけ誤りを入れる

既存のモーション検査があるなら、一つのイベントだけ接触先を変更し、時刻を維持する。それを正解と判定するなら、時刻とは独立した接触条件が不足している。次に接触先を維持して時刻だけを変更する。

以下は元の三打実験を再現するスクリプトである。Blender 4.3.2を用意し、コードを drum-contact.py として保存する。出力は時刻、打面、両方の一致数の順である。実際の制作環境では時刻の許容差、一対一のイベント対応、形状に応じた接触条件を決める。GLB以降のゲームエンジンでの再生についてはこの実験の対象外である。

```sh
blender --background --factory-startup --python-exit-code 1 --python drum-contact.py
```

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
