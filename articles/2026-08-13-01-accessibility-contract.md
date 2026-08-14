---
title: "見た目を直したらアクセシビリティが消えた。UI要件をCIで壊れにくくする"
emoji: "♿"
type: "tech"
topics: ["accessibility", "css", "html", "githubactions"]
published: false
published_at: 2026-08-13 16:58
---

画面をきれいに作り直したあと、アニメーション軽減や動的更新の通知だけが消えていた。

この種の退行は、機能テストが通っていても見逃しやすい。アクセシビリティ要件が「実装者が覚えておく注意事項」のままだからだ。

`KAFKA2306/finBI` の2026年8月13日の公開commitでは、静的Web UIの再構築と同時に、CIが `prefers-reduced-motion`、`aria-live="polite"`、`role="status"` の存在を検査するようになった。この記事では、この実装を題材に、**UI要件をレビュー項目だけでなく実行可能な契約へ落とす方法**を整理する。

一次情報:

- finBI commit: https://github.com/KAFKA2306/finBI/commit/bc928ab7806c727086992df838f8ccae62f58040
- workflow: https://github.com/KAFKA2306/finBI/blob/bc928ab7806c727086992df838f8ccae62f58040/.github/workflows/static-bi.yml
- HTML: https://github.com/KAFKA2306/finBI/blob/bc928ab7806c727086992df838f8ccae62f58040/web/index.html
- CSS: https://github.com/KAFKA2306/finBI/blob/bc928ab7806c727086992df838f8ccae62f58040/web/styles.css
- MDN `prefers-reduced-motion`: https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/%40media/prefers-reduced-motion
- MDN `aria-live`: https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-live
- MDN live regions: https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Guides/Live_regions

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

JavaScriptの構文だけでなく、アクセシビリティ上必要としたマーカーも検査対象になっている。

MDNによれば、`prefers-reduced-motion` は端末側で非本質的な動きを減らす設定が有効かを検出するCSS media featureである。また `aria-live` は、初期表示後に変化する内容を支援技術へ通知する優先度を表す。したがって、どちらも単なる装飾ではない。

## 2. 原因：仕様が文章にしかない

壊れた失敗例を最小化するとこうなる。

```html
<div id="result">計算中...</div>
```

```css
.card {
  animation: float 1s ease-in-out infinite;
}
```

見た目もJavaScriptも動く。しかし、動的に結果が変わる領域にlive regionの意味付けがなく、motionを減らしたい利用者への分岐もない。

問題は「担当者がアクセシビリティを知らない」ことに限定されない。レビューで一度正しく実装しても、HTML/CSSを全面改稿すれば消せるのに、通常のsyntax testはそれを失敗として扱わないことが原因になる。

## 3. 設計判断と代替案：まず存在契約をCIへ置く

今回の設計判断は、重要なUI要件を静的な存在契約としてCIに置くことだ。

代替案は3つある。

1. **レビューだけで守る**: 導入コストは低いが、自動検出できない。
2. **ブラウザE2Eだけで守る**: 実挙動に近いが、環境構築とテスト設計が重くなる。
3. **静的契約 + 必要なE2E**: 単純な欠落は数秒の検査で止め、支援技術との実挙動など静的検査で証明できない部分だけを別テストへ任せる。

ここで重要なのは、`grep` をアクセシビリティ検証の完成形と誤解しないことだ。文字列の存在は「意図した仕組みが消えていない」ことしか保証しない。正しい位置、実際の読み上げ、十分なコントラスト、キーボード操作などは別問題である。

## 4. 実装：要件を小さな失敗条件に変換する

改善後の最小例は次のようになる。

```html
<div id="result" role="status" aria-live="polite">計算中...</div>
```

```css
.card {
  animation: float 1s ease-in-out infinite;
}

@media (prefers-reduced-motion: reduce) {
  .card {
    animation: none;
  }
}
```

そしてCIに存在契約を追加する。

```sh
set -eu
grep -q 'role="status"' web/index.html
grep -q 'aria-live="polite"' web/index.html
grep -q 'prefers-reduced-motion' web/styles.css
```

MDNは `aria-live="polite"` について、更新を通知するが一般に現在の作業を中断しない低優先度の通知として説明している。`prefers-reduced-motion: reduce` は、利用者が動きを減らす設定を有効にした場合に真になる。

## 5. 検証：壊してからCIが落ちることを確認する

存在契約は、正常系だけでは弱い。意図的に1要件ずつ削除し、検査が失敗するかを見る。

```sh
cp web/index.html /tmp/index.html
sed -i 's/ aria-live="polite"//' web/index.html
! grep -q 'aria-live="polite"' web/index.html
mv /tmp/index.html web/index.html
```

同様に `role="status"` と `prefers-reduced-motion` も削除してfailすることを確認する。

`finBI` の公開workflowでは、これらの検査に加えてPython compile、unit tests、JavaScript syntax、静的サイトのHTTP smoke test、最後のclean checkout確認を同じ `validate` jobで実行している。アクセシビリティ契約だけを特別扱いせず、成果物の検証項目の1つにしている点が再利用しやすい。

## 6. 失敗と学び：文字列検査を「アクセシビリティ合格証」にしない

この方式の典型的な失敗は、CIが通ったことをもって「アクセシブル」と宣言することだ。

たとえば次でも文字列検査は通る。

```html
<div aria-live="polite"></div>
<div id="actual-result">更新結果</div>
```

live regionと実際に更新される要素が分離しており、期待した通知になるとは限らない。

学びは、静的契約の責務を狭く定義することにある。

- 静的契約: 必須マーカーの欠落を止める
- DOM/ブラウザテスト: 更新対象との接続を確認する
- 手動・支援技術テスト: 実際の利用体験を確認する

1つのgateに万能性を持たせるのではなく、安い検査を前段に置いて明白な退行を早く止める。

## 7. 再現方法：3ファイルで試す

読者が試せる最小構成は `web/index.html`、`web/styles.css`、`check.sh` の3ファイルだけでよい。

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

実行する。

```sh
sh check.sh
```

次に3つの必須文字列を1つずつ消して再実行する。削除した要件に対応して終了コードが非0になれば、最小の退行防止契約として機能している。

## まとめ

アクセシビリティ要件は、レビュー時に一度確認して終わりにするとUI刷新で抜け落ちる。

`finBI` の実装から一般化できるのは、**重要なUI要件を、まず安価で明示的なCI契約へ変換する**という方法だ。`grep` は完成したアクセシビリティ試験ではない。しかし「昨日まであった最低限の仕組みが今日消えた」を即座に止める用途には明確な価値がある。

その上で、静的検査では証明できない実挙動をブラウザテストや支援技術による確認へ段階的に委ねる。これなら、品質ゲートを重くしすぎず、UIの作り直しにも耐えやすい。