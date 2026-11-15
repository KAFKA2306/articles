# 軒下で雨が消えた。そのテストは何を見ている？

キャラクターが軒下に入ると、画面から雨粒が消える。そこでテストは合格を返す。でも、肩に新しい滴が付き続けていたら、このテストでは見落とす。

空中に雨粒を描く処理と、肌や布に滴を付ける処理は、別々に動かせる。空中の雨だけを止めれば、肩は濡れ続ける。軒下に入った瞬間に肩の滴まで消すと、濡れていた服が急に乾いたように見える。どちらも「軒下で空中の雨が消えた」という条件を満たす。

## 雨が消えれば合格。4件とも通った

題材にしたのは『Toon Rain』だ。軒下に入ると新しい滴が付かなくなり、すでに付いた水は表面を流れる。vrmineではこの挙動を検証するために、空中の雨だけ消える例と、付いていた滴まで消える例を用意する設計にした。 [作者による挙動の説明](https://www.patreon.com/SakuraRabbit/posts/toon-rain-174541842) · [vrmineの検証設計](https://github.com/KAFKA2306/vrmine/issues/508)

判定の一部を取り出し、合成データ4件で試した。「軒下の空中雨が0」だけを見ると、4件すべてが合格した。屋外と軒下で新たに付いた滴と、軒下に入った直後に残っている滴を数えると、欠陥2件を落とせた。計測できなかった1件は未判定になった。

表の数値は滴の数。新規付着は、各観測区間で対象の部位に付いた滴を数える。残留は、軒下に入る直前に付いていた滴のうち、直後も追跡できた数だ。

| 例 | 軒下の空中雨 | 屋外で付いた滴 | 軒下で付いた滴 | 入った直後に残った滴 | 空中雨だけで判定 | 表面の状態で判定 |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| 正常 | 0 | 3 | 0 | 2 | 合格 | 合格 |
| 空中の雨だけ消えた | 0 | 3 | 2 | 2 | 合格 | 不合格 |
| 肩の滴まで消えた | 0 | 3 | 0 | 0 | 合格 | 不合格 |
| 軒下で付いた滴が欠測 | 0 | 3 | 欠測 | 2 | 合格 | 未判定 |

DuckDB 1.5.3のCLIで次のSQLを実行すると、表と同じ判定を再現できる。 [DuckDB 1.5 CLIの公開記録](https://duckdb.org/2026/03/09/announcing-duckdb-150) · [1.5.3の公開記録](https://duckdb.org/2026/05/20/announcing-duckdb-153)

```sql
WITH cases(id, label, airborne, outside, sheltered, retained) AS (
  VALUES
    (1, 'normal',         0, 3,    0, 2),
    (2, 'air_only',       0, 3,    2, 2),
    (3, 'dries_at_entry', 0, 3,    0, 0),
    (4, 'missing_count',  0, 3, NULL, 2)
)
SELECT
  label,
  CASE WHEN airborne = 0 THEN 'PASS' ELSE 'FAIL' END AS screen_only,
  CASE
    WHEN outside IS NULL OR sheltered IS NULL OR retained IS NULL
      THEN 'UNVERIFIED'
    WHEN outside > 0 AND sheltered = 0 AND retained > 0
      THEN 'PASS'
    ELSE 'FAIL'
  END AS surface_state
FROM cases
ORDER BY id;
```

## 布を引くテストにも使える

操作で何が変わり、何が残るかを先に決める。必要な値を取れなかったときの扱いも決めておく。布なら、プレイヤーがいつも使う操作で、同じ箇所を短く引く場合と長く引く場合を試す。短く引いて手を離すと、布は元の形に近づく。長く引いて裂けたら、手を離しても裂け目が残る。毎回元の形に戻る例を用意して、長く引いたときのテストが不合格を返すか確かめる。 [布デモの検証設計](https://github.com/KAFKA2306/vrmine/issues/507)

設定を調整するときは、同じ操作を再生して測る。雨量を変えたら一定時間に付く滴の数、流下速度を変えたら同じ滴の移動距離、乾燥時間を変えたら、同じ濡れ具合から面積が基準に戻るまでの時間を比べる。採点器を変更したときは、保存しておいた正常・欠陥・欠測のデータを先に通す。各判定が想定どおりか、SQLで確かめられる。

この手順は、操作と観測区間をそろえ、どの部位がどう変わったかを測れる演出に使える。今回比較したのは、合成データに対する二つの判定だ。水膜の見え方、肌や布が変形したときの滴の追従、描画負荷を調べるには、実機で操作を再生して映像と計測値をそろえる。UnityのGraphics Test Frameworkは、9.0.0-pre.30からテスト用の通信パッケージを使って画像比較の実測値と閾値を送れる。画像差も同じ操作区間にひもづけておけば、どこで基準から外れたかを追える。 [Windows Playerでの検証設計](https://github.com/KAFKA2306/vrmine/issues/504) · [Graphics Test Frameworkの変更履歴](https://docs.unity3d.com/Packages/com.unity.testframework.graphics@9.0/changelog/CHANGELOG.html)
