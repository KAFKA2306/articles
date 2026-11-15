# 軒下で雨が消えた。そのテストは何を見ている？

ゲームのキャラクターが軒下に入る。画面から雨粒が消えたので、テストは合格を返す。もし肩に新しい滴が付き続けていたら、そのテストは気づけるだろうか。

Unityで雨の演出を作るとき、この二つは別々に起こり得る。カメラに映る空中の雨を止めても、肌や布への付着処理は動き続けるからだ。逆に、軒下に入った瞬間に濡れまで消せば、新規付着はゼロでも不自然に見える。そこで、雨の見た目を比べる前に、採点器へ意図的に壊した例を通してみた。

## 採点器に四つの例を通す

題材は、軒下で新しい水滴の付着が止まり、付いた水は残って流れる『Toon Rain』。vrmineの設計では、空中の雨だけを消す例と、残留水まで消す例をそれぞれ失格にする。以下はその判定の一部を切り出した合成データで、Unityを使わずに採点の穴を再現できる。単位は1部位・1観測区間あたりの滴数。残留水は軒下に入る直前に付いた滴を、入った直後に追跡した数とする。 [作者による挙動の説明](https://www.patreon.com/SakuraRabbit/posts/toon-rain-174541842) · [vrmineの検証設計](https://github.com/KAFKA2306/vrmine/issues/508)

合成データを使った実行では、「軒下の空中雨が0」だけを見る判定が4件とも合格にした。屋外・軒下での新規付着と遮蔽直後の残留水を測る判定では、正常1件が合格、欠陥2件が不合格、観測が欠けた1件が未判定になった。

| 例 | 軒下の空中雨 | 屋外の新規付着 | 軒下の新規付着 | 遮蔽直後の残留水 | 状態を測る判定 |
| --- | ---: | ---: | ---: | ---: | --- |
| 正常 | 0 | 3 | 0 | 2 | 合格 |
| 空中の雨だけ消えた | 0 | 3 | 2 | 2 | 不合格 |
| 濡れまで消えた | 0 | 3 | 0 | 0 | 不合格 |
| 軒下の付着を計測できなかった | 0 | 3 | 欠測 | 2 | 未判定 |

下のSQLをDuckDB 1.5.3のCLIに貼ると、両方の採点結果を比較できる。 [DuckDB 1.5 CLIの公開記録](https://duckdb.org/2026/03/09/announcing-duckdb-150) · [1.5.3の公開記録](https://duckdb.org/2026/05/20/announcing-duckdb-153)

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

## 次の演出に持ち込む手順

まず、プレイヤーが普段使う操作を一つ選ぶ。次に、その操作で**変わるもの、残るもの、観測できなかったときの扱い**を書く。布なら、同じ箇所を短く引いて離したときは形状差が縮まり、長く引いて裂けたときは離しても開口が残る。この二つを再生して、常に元に戻る欠陥版が長い引きの試験で落ちることを確かめる。 [布デモの検証設計](https://github.com/KAFKA2306/vrmine/issues/507)

制作者が調整値を変えるときも同じ手順を使える。雨量だけを変えるなら、同じ操作列で一定時間の付着数を比べる。流下速度なら同じ滴の移動距離、乾燥時間なら同じ開始状態から濡れ面積が基準に戻る時刻を見る。採点器を更新するときは、正常例・欠陥例・欠測例から先に再実行する。定型判定は保存した値をSQLに通すだけで回る。

この方法を持ち込めるのは、操作と観測区間を揃え、変化を部位や状態に結びつけられる演出だ。この記事で実行したのは採点ロジックの比較まで。水膜の自然さや変形中の追従、描画負荷は、実機で同じ操作を再生し、映像と計測値を揃えて確かめる。UnityのGraphics Test Frameworkは、9.0.0-pre.30で画像比較の実測値と閾値を構造化して送る機能を追加した。この画像差と、表面の状態を測る判定を同じ操作区間に結びつけると、どの変化が失格を引き起こしたかを追える。 [Windows Playerでの検証設計](https://github.com/KAFKA2306/vrmine/issues/504) · [Graphics Test Frameworkの変更履歴](https://docs.unity3d.com/Packages/com.unity.testframework.graphics@9.0/changelog/CHANGELOG.html)
