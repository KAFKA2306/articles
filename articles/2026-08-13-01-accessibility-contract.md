---
title: "UI改修で読み上げ通知や動きの軽減に必要な記述が消えたら、CIで止める"
emoji: "♿"
type: "tech"
topics: ["accessibility", "css", "html", "githubactions"]
published: false
published_at: 2026-08-13 16:58
---

**UIを刷新するなら、以前できたことを壊す条件を先に固定せよ。**

見た目もJavaScriptも動いていても、動きを減らしたい人の設定や状態更新の読み上げが失われれば後退だ。[finBIのUI改修](https://github.com/KAFKA2306/finBI/commit/bc928ab7806c727086992df838f8ccae62f58040)では、[HTML](https://github.com/KAFKA2306/finBI/blob/bc928ab7806c727086992df838f8ccae62f58040/web/index.html)のstatusと[CSS](https://github.com/KAFKA2306/finBI/blob/bc928ab7806c727086992df838f8ccae62f58040/web/styles.css)のmotion軽減を[CI](https://github.com/KAFKA2306/finBI/blob/bc928ab7806c727086992df838f8ccae62f58040/.github/workflows/static-bi.yml)で守る最低条件へ変えた。

失敗の仕組みは単純だ。見栄えを評価する検査では、目立たない利用者の能力を測っていない。**大切な体験を「気をつける」から「失われたら止まる」へ移す。** ただしCSS/ARIAの文字列確認だけで実際の読み上げを検証したとは言わない。

## UI刷新で失われやすいのは、目立たない要件だった

一般的な機能テストは、ボタンが押せる、計算できる、routeが開く、といった主要機能をよく守ってくれる。

一方で、次のような要件はHTML/CSSの大きな書き換えで静かに消えやすい。

```css
@media (prefers-reduced-motion: reduce) {
  .card {
    animation: none;
  }
}
```

```html
<div id="result" role="status">計算中...</div>
```

MDNは `prefers-reduced-motion` を、利用者が端末側で非本質的なmotionを減らす設定を有効にしているか検出するmedia featureとして説明している。

- https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/%40media/prefers-reduced-motion

WAI-ARIA 1.2では `role="status"` はlive regionで、`aria-live="polite"` と `aria-atomic="true"` を暗黙に持つと定義されている。したがって、一般論として `role="status"` と明示的な `aria-live="polite"` の両方を常に要求する必要はない。

- https://www.w3.org/TR/wai-aria/#status
- https://www.w3.org/WAI/WCAG21/Techniques/aria/ARIA22

`finBI` の対象commitでは、実装上 `role="status"` と `aria-live="polite"` の両方を置いているため、CIもその実装契約をそのまま確認している。

ここで守りたいものは属性名そのものではない。

**UIを作り直した人が、意図せず利用体験の一部を削除しても、reviewerの記憶に頼らず気づけること**だ。

## 最初から重いE2Eを作らなかった

アクセシビリティを自動検証しようとすると、いきなり「すべてをbrowser testや支援技術testで証明したい」と考えやすい。

しかし、それを最初の一歩にすると導入コストが上がる。

今回の `finBI` では、まず「消えたことなら安く検出できる」要件をCIへ置いた。

```sh
node --check web/app.js
node --check web/worker.mjs
test -s web/styles.css
grep -q 'prefers-reduced-motion' web/styles.css
grep -q 'aria-live="polite"' web/index.html
grep -q 'role="status"' web/index.html
```

これなら、HTML/CSSを全面改稿して必要なmarkerを消した変更は、その場で止められる。

この設計で優先したのは、**完全性より「安く、毎回、確実に実行される防波堤」**だった。

## `grep` が証明しないものを、はっきり分ける

ここは重要である。

次のHTMLでも文字列検査は通る。

```html
<div role="status"></div>
<div id="actual-result">計算結果</div>
```

`role="status"` が存在しても、実際の更新内容と正しく接続されているとは限らない。

同様に `prefers-reduced-motion` がCSSにあるだけでは、ページ内のすべての問題あるmotionが適切に扱われているとは証明できない。

だから検証責務を分ける。

| Gate | 守るもの | 守らないもの |
|---|---|---|
| static contract | 必須markerが消えていない | 実際の読み上げ、keyboard操作、contrast |
| browser/DOM test | DOM更新と対象要素の接続 | assistive technologyごとの最終体験 |
| manual / AT test | 実際の利用体験 | 将来の改修時の自動回帰 |

**一つのテストへ「アクセシビリティ合格証」を背負わせない。**

安い退行検出を毎回走らせ、より重い検証は必要な層へ置く。

## 既存UIへ入れるなら、まず3つだけ選ぶ

この方法は大規模なaccessibility programがなくても始められる。

最初に、変更する画面のHTMLとCSSを開き、「次の改修で消えたら困る体験」を3つ選ぶ。

たとえば:

1. reduced motionへの対応
2. status messageのsemantic role
3. keyboard操作に必要なfocusable control

そのうち、**静的に存在を確認できるものだけ**を最初のCI contractにする。

CIに入れる前に、元のHTMLと `role="status"` を消したコピーへ同じ検査をかける。

```sh
(
  set -eu
  broken_html=$(mktemp)
  trap 'rm -f "$broken_html"' EXIT
  grep -q 'role="status"' web/index.html
  sed 's/role="status"//g' web/index.html > "$broken_html"
  if grep -q 'role="status"' "$broken_html"; then
    exit 1
  else
    test "$?" -eq 1
  fi
)
```

元のHTMLで一致し、コピーで一致しなければ、記述の削除は検出できる。通知が実際に読み上げられるかは、画面を操作して別途確認する。

## grepの後に実画面で試す2操作

`finBI`の静的検査はCSSの`prefers-reduced-motion`とHTMLの`role="status"`・`aria-live="polite"`の存在を確かめる。[対象HTML](https://github.com/KAFKA2306/finBI/blob/bc928ab7806c727086992df838f8ccae62f58040/web/index.html)・[CSS](https://github.com/KAFKA2306/finBI/blob/bc928ab7806c727086992df838f8ccae62f58040/web/styles.css)

次の操作は**追加の検証手順**であり、本稿の改稿時に実機で再試験した結果ではない。

1. OSの「視差効果を減らす」などの動き軽減設定を有効・無効にして同じ画面を操作する。非本質的な動きが抑えられなければ、CSSに記述があっても不合格。
2. 結果が更新される操作を行い、値の表示更新と支援技術への状態通知を分けて確かめる。`role="status"`が残っていても、実際に変更されるテキストがその要素に入っていなければ「読み上げ確認済み」とはしない。

静的CIの終了コード、ブラウザーとOSの版、設定の状態、支援技術での観測は別に残す。後者を未実施ならWCAG適合や通知の実動作まで証明したと書かない。

## このやり方が向いているチーム

特に効くのは、次のような環境だと思う。

- UI改修頻度が高い
- 少人数でfrontendを触る人が入れ替わる
- AI coding agentや大規模refactorでHTML/CSSを一気に書き換える
- accessibility専門担当が毎PRを見る体制ではない
- それでも最低限の利用体験を「善意」だけに依存させたくない

`finBI` でやったこと自体は数行の検査でしかない。

しかし価値は、**「覚えていた人がいたから守れた」状態を、「消したら自動で失敗する」状態へ変えたこと**にある。

## 何を提供できるか

この考え方はaccessibilityだけに限定されない。

既存Web UIを見て、

1. 利用者が失うと困る体験を特定する
2. static / browser / manualのどこで検証するか分ける
3. 最も安い自動gateからCIへ入れる
4. 意図的に壊すnegative testで検出能力を確認する
5. UI刷新後も同じ契約が残るようにする

という形で、**変更速度を落としすぎずに回帰を減らす設計**へ変えられる。

ただし、static marker checkだけでWCAG適合や支援技術上の正しさを保証することはできない。必要な品質水準に応じてbrowser test、accessibility testing tool、実際の支援技術確認へ広げる必要がある。

## まとめ

UIをきれいにすることと、利用者が使い続けられることは別である。

`finBI` では、motion軽減と動的status通知に関する実装をCIの失敗条件へ変えた。これは小さな仕組みだが、**UI刷新のたびに人が思い出さなくても、最低限の利用体験を残す**方向へ開発プロセスを変えられた。

私がこの実装から再利用したいのは `grep` ではない。

**重要なUX要件を「注意事項」から「壊したら止まる契約」へ変えること。**

その境界を小さく始めれば、改修速度と退行防止を両立しやすい。


## 規律を適用・撤回する条件

管理画面や音声UIの再設計でも、旧版の利用者が失うと困る操作があるなら、先に代表入力と失敗条件を固定する。これは**別分野への応用仮説**であって回帰件数を測った結果ではない。

旧挙動が不適切で意図的に廃止するなら、守るのではなく代替手段と影響を評価する。静的検査が通っても支援技術の実操作は別に確認する。**機能が残ったことと、体験が残ったことを混同しない。**
