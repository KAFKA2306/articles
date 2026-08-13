---
title: "見た目を直したらアクセシビリティが消えた。UI要件をCIで壊れにくくする"
emoji: "♿"
type: "tech"
topics: ["accessibility", "css", "html", "githubactions"]
published: false
published_at: 2026-08-13 16:58
---

画面を作り直したあと、アニメーション軽減や動的更新の通知だけが消えていた。この種の退行は機能テストが通っていても見逃しやすい。

`KAFKA2306/finBI` の2026年8月13日の公開commitでは、静的Web UIの再構築と同時にCIが `prefers-reduced-motion`、`aria-live="polite"`、`role="status"` の存在を検査するようになった。この記事では、**UI要件をレビュー項目だけでなく実行可能な契約へ落とす方法**を整理する。

一次情報:

- https://github.com/KAFKA2306/finBI/commit/bc928ab7806c727086992df838f8ccae62f58040
- https://github.com/KAFKA2306/finBI/blob/bc928ab7806c727086992df838f8ccae62f58040/.github/workflows/static-bi.yml
- https://github.com/KAFKA2306/finBI/blob/bc928ab7806c727086992df838f8ccae62f58040/web/index.html
- https://github.com/KAFKA2306/finBI/blob/bc928ab7806c727086992df838f8ccae62f58040/web/styles.css
- https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/%40media/prefers-reduced-motion
- https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-live
- https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Guides/Live_regions

## 1. 問題：アクセシビリティ要件だけがリファクタリングで消える

### 実際の入力・状況

対象commitのCIには次の検査がある。

```sh
node --check web/app.js
node --check web/worker.mjs
test -s web/styles.css
grep -q 'prefers-reduced-motion' web/styles.css
grep -q 'aria-live="polite"' web/index.html
grep -q 'role="status"' web/index.html
```

MDNによれば、`prefers-reduced-motion` は端末側で非本質的な動きを減らす設定を検出するCSS media featureである。`aria-live` は、初期表示後に変化する内容を支援技術へ通知する優先度を表す。

## 2. 原因：仕様が文章にしかない

壊れた失敗例は単純だ。

```html
<div id="result">計算中...</div>
```

```css
.card { animation: float 1s ease-in-out infinite; }
```

見た目もJavaScriptも動く。しかしlive regionの意味付けがなく、motionを減らしたい利用者への分岐もない。HTML/CSSを全面改稿して要件を消しても、通常のsyntax testは失敗しない。

## 3. 設計判断と代替案：まず存在契約をCIへ置く

選択肢は、レビューだけで守る、ブラウザE2Eだけで守る、静的契約と必要なE2Eを組み合わせる、の3つがある。単純な欠落は安い静的検査で止め、支援技術との実挙動など静的検査で証明できない部分を別テストへ任せる。

`grep` はアクセシビリティ検証の完成形ではない。文字列の存在は「意図した仕組みが消えていない」ことしか保証しない。

## 4. 実装：要件を小さな失敗条件に変換する

改善後の例は次の通り。

```html
<div id="result" role="status" aria-live="polite">計算中...</div>
```

```css
.card { animation: float 1s ease-in-out infinite; }
@media (prefers-reduced-motion: reduce) {
  .card { animation: none; }
}
```

CIには存在契約を追加する。

```sh
set -eu
grep -q 'role="status"' web/index.html
grep -q 'aria-live="polite"' web/index.html
grep -q 'prefers-reduced-motion' web/styles.css
```

MDNは `aria-live="polite"` を、更新を通知するが一般に現在の作業を中断しない低優先度の通知として説明している。`prefers-reduced-motion: reduce` は利用者が動きを減らす設定を有効にした場合に真になる。

## 5. 検証：壊してからCIが落ちることを確認する

正常系だけでなく、意図的に1要件ずつ削除する。

```sh
cp web/index.html /tmp/index.html
sed -i 's/ aria-live="polite"//' web/index.html
! grep -q 'aria-live="polite"' web/index.html
mv /tmp/index.html web/index.html
```

同様に `role="status"` と `prefers-reduced-motion` も削除してfailすることを確認する。`finBI` の公開workflowでは、これらに加えてPython compile、unit tests、JavaScript syntax、HTTP smoke test、clean checkout確認を同じ `validate` jobで実行している。

## 6. 失敗と学び：文字列検査を「アクセシビリティ合格証」にしない

次でも文字列検査は通る。

```html
<div aria-live="polite"></div>
<div id="actual-result">更新結果</div>
```

live regionと実際の更新要素が分離しており、期待した通知になるとは限らない。静的契約は必須マーカーの欠落、DOM/ブラウザテストは更新対象との接続、手動・支援技術テストは実際の利用体験、と責務を分ける。

## 7. 再現方法：3ファイルで試す

`web/index.html`:

```html
<!doctype html>
<meta charset="utf-8">
<div id="result" role="status" aria-live="polite">ready</div>
```

`web/styles.css`:

```css
#result { transition: transform 200ms; }
@media (prefers-reduced-motion: reduce) {
  #result { transition: none; }
}
```

`check.sh`:

```sh
#!/bin/sh
set -eu
test -s web/styles.css
grep -q 'prefers-reduced-motion' web/styles.css
grep -q 'aria-live="polite"' web/index.html
grep -q 'role="status"' web/index.html
```

`sh check.sh` を実行し、3つの必須文字列を1つずつ消して再実行する。対応する終了コードが非0になれば最小の退行防止契約として機能している。

## まとめ

アクセシビリティ要件はレビュー時に一度確認して終わりにするとUI刷新で抜け落ちる。`finBI` から一般化できるのは、**重要なUI要件を、まず安価で明示的なCI契約へ変換する**方法だ。

`grep` は完成したアクセシビリティ試験ではない。しかし「昨日まであった最低限の仕組みが今日消えた」を即座に止められる。その上で、静的検査では証明できない実挙動をブラウザテストや支援技術による確認へ段階的に委ねる。