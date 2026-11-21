---
title: "ドラムの3Dアニメで、叩く時刻が合っても打面がずれる"
emoji: "🥁"
type: "tech"
topics: ["blender", "3d", "アニメーション", "gltf", "自動化"]
published: false
created_at: "2026-11-15"
updated_at: "2026-11-15"
---

ハイハットの音に合わせてスティックが下りる。先端が当たったのはスネア。ドラムの3Dアニメでこんなずれが出たら、まず「いつ叩いたか」と「何を叩いたか」を別々に見ます。音に合わせて腕が動いていると、引きの画では叩く場所の違いに気づきにくいからです。

Blenderでこの場面を三打の動きに置き換え、GLBに書き出してから測りました。二打目の打面だけを替えた例では、三打とも時刻が合い、打面まで合ったのは二打でした。

## 二打目だけを変えて、GLBを読み戻す

Blender 4.3.2で、スネアとハイハットの位置をそれぞれ一点で表しました。音源の代わりに、30 fpsで「10フレーム目にスネア、20フレーム目にハイハット、30フレーム目にスネア」を正解にしました。スティックの先端に見立てたオブジェクトを動かし、GLBに書き出して空のシーンに読み込みます。先端が打面の座標から1 cm未満に入ったフレームを一打と数えました。 [BlenderのglTF入出力仕様](https://docs.blender.org/manual/en/4.3/addons/import_export/scene_gltf2.html)

| GLBに入れた動き | 時刻が一致 | 打面が一致 | 両方が一致 |
| --- | ---: | ---: | ---: |
| 正解どおり | 3/3 | 3/3 | 3/3 |
| 二打目をスネアに変更 | 3/3 | 2/3 | 2/3 |
| 二打目を2フレーム遅らせる | 2/3 | 3/3 | 2/3 |

この例では、どのテイクも三打なので順番に照合できます。曲全体で試すなら、許容する時間差を決め、正解と実際の打撃を一対一に対応させます。打ち漏れ、余分な打撃、同時に叩いた打面も数えると、どこで演奏が崩れたか見つけやすくなります。

## 一打ずれたら、どこを直すか

譜面で二打目がスネアになっていたら、採譜か打面の割り当てを直します。譜面がハイハットを指しているのに先端がスネアに当たるなら、腕の動きや先端の位置を調べます。Blenderではハイハットに当たり、書き出した先で外れるなら、動きをキーフレームに焼き付ける処理（ベイク）や、読み込み後の補間を調べます。

各打撃に「時刻・動かす部位・触れる場所」を記録して、動きを作るときと確かめるときに同じ記録を使うと、間違いが入った段階を追えます。ベースの演奏なら、音が鳴る時刻と押さえる弦・フレットを記録します。同じ音高を複数の弦で出せるので、音源から演奏を作る場合は、調弦と前後の運指に合う位置を選びます。歩く動きなら、足が床に着いている区間と足裏の位置を記録します。 [ベースの音声入力と運指割り当ての実装](https://github.com/scottvr/gtrsnipe/blob/main/README.md)

## 制作に組み込むなら、先に打面と時刻を決める

短い定型モーションなら、打面と時刻を決めてからキーフレームを打てます。上半身の揺れや踏み替えも付けるなら、同じ記録から要所の姿勢を指定して全身の動きを生成し、使うキャラクターの骨格に合わせて接触を補正します。動きの候補は、キャラクター、譜面、カメラをそろえて比べます。

自動でつなぐなら、Tripo P2とAuto Rigで素材と骨格を用意し、音源しかない曲はDrumScriptで採譜する構成が考えられます。KimodoのCLIに手足の位置や姿勢を渡して全身の動きを生成し、Blenderのバックグラウンド実行で接触を補正し、ベイクして測ります。ゲーム向けなら、最後にゲームエンジンで再生して確かめます。今回確かめた範囲は、Blenderで先端を動かし、GLBを読み戻して接触を測るところまでです。 [Tripo P2](https://developers.tripo3d.com/en/models/p2) · [Auto Rig](https://developers.tripo3d.com/en/docs/animations-rig) · [DrumScript](https://github.com/DrumScript/DrumScript) · [Kimodo CLI](https://research.nvidia.com/labs/sil/projects/kimodo/docs/user_guide/cli.html)

工程ごとの入力とツールの版を記録しておくと、採譜を直したときに影響する区間から作り直せます。接触距離と時刻のずれはスクリプトで測り、モデルに演出を評価させるときは短いプレビューと見せたい拍を渡します。自動化の効果を比べるなら、誤った打面や遅れを通した件数と、合格した一件あたりの総トークン数を数えます。まず一打だけ外したデータを流せば、今の検査でそのずれを拾えるか確かめられます。

## Blenderで三つのケースを試す

下のコードを `drum-contact.py` に保存し、次のコマンドで実行します。各ケースの出力は、時刻が合った打数、打面が合った打数、両方が合った打数の順です。一時GLBは実行後に削除されます。

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
