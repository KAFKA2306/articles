---
title: "AIが作った確認画面をEscで閉じたら、次の入力は元のボタンに届くか"
emoji: "⌨️"
type: "tech"
topics: ["html", "playwright", "accessibility", "ai", "evals"]
published: false
created_at: "2026-11-15"
updated_at: "2026-11-15"
---

「公開する」を押したあとで考え直し、確認画面を `Escape` で閉じる。そこで次にキーを押すと、どこに入力が届くでしょうか。

同じ見た目の確認画面を二つ作って試すと、どちらも `Escape` で閉じました。片方では「公開する」ボタンにフォーカスが戻り、もう片方ではページの見出しに移りました。AIに作らせた画面を確かめるときも、閉じた直後のフォーカスをテストに入れると、この違いを拾えます。

## 閉じた直後に、フォーカスが分かれた

二つとも `<dialog>` を `showModal()` で開きます。片方にだけ、閉じたときにページ見出しへフォーカスを移す処理を足しました。画面幅390pxで、Tab、Enter、Tab、Escapeの順にキーを押しました。使用したのはPlaywright 1.64.0とChromium 153.0.8010.0です。 [Playwrightの使用版](https://github.com/microsoft/playwright/releases/tag/v1.64.0)

| 観測した動作 | 標準の動作 | 閉じたあと見出しへ移す実装 |
| --- | --- | --- |
| Enterで開き、「キャンセル」にフォーカスする | 通過 | 通過 |
| Tabで「公開を確定」へ移る | 通過 | 通過 |
| Escapeで閉じる | 通過 | 通過 |
| 「公開する」ボタンへ戻る | 通過 | 失敗。見出しへ移動 |

この画面では、公開を見送っても「公開する」ボタンが残ります。そこで、テストの期待値をそのボタンにしました。W3Cも、原則として開く操作に使った要素へフォーカスを戻すよう案内しています。その要素が消えた場合や、次の操作に適した場所がある場合は、作業の流れに合わせて戻り先を選びます。 [W3Cのモーダルダイアログのパターン](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) ／ [HTMLのdialogを使う手法](https://www.w3.org/WAI/WCAG22/Techniques/html/H102)

### 自分の画面で再現する

既存のPlaywright Testに加えるなら、URLとボタン名、ダイアログ名を自分の画面に合わせてください。この例では、開いた直後に「キャンセル」にフォーカスし、閉じた後は「公開する」に戻ることを確かめます。

```ts
import { expect, test } from '@playwright/test'

test('確認を取り消すと公開ボタンに戻る', async ({ page }) => {
  await page.goto('/settings')
  const trigger = page.getByRole('button', { name: '公開する', exact: true })
  const dialog = page.getByRole('dialog', { name: '公開しますか？' })
  await trigger.focus()
  await page.keyboard.press('Enter')
  await expect(dialog).toBeVisible()
  await expect(dialog.getByRole('button', { name: 'キャンセル' })).toBeFocused()
  await page.keyboard.press('Tab')
  await expect(dialog.getByRole('button', { name: '公開を確定' })).toBeFocused()
  await page.keyboard.press('Escape')
  await expect(dialog).toBeHidden()
  await expect(trigger).toBeFocused()
})
```

戻り先の間違いを拾えるか、自分でも試せます。見出しに一時的に `tabindex="-1"` を付け、`close` イベントでその見出しを `focus()` します。この変更を入れた画面では、閉じたことの検査は通過し、最後の `toBeFocused()` が失敗します。ページ全体を通して検査するなら、冒頭の `trigger.focus()` に代えて、Tabで「公開する」ボタンまでたどります。ボタンやダイアログはロールと名前で探すので、同じ操作を実現する既存コンポーネントにもテストを使えます。 [Playwrightのアクセシビリティ検査](https://playwright.dev/docs/accessibility-testing)

## ガイドを使うと手戻りは減るか

この確認画面を題材に、Web標準の実装例を検索できるModern Web Guidance 1.0.0も試しました。`confirmation modal dialog` で検索すると、先頭に `dialog` が出ました。そのIDでガイド本文を取得し、既存コードの走査がJSONを返すことも確認しました。スキルはリリースコミット、CLIはnpmのバージョンを固定し、実行時は `DISABLE_TELEMETRY=1` を渡しました。 [導入と動作確認のPR](https://github.com/KAFKA2306/agent-resources/pull/586) ／ [検証時の配布設定](https://github.com/KAFKA2306/agent-resources/blob/035cec2ac8a9929e942406d20f516ff39dbdb5b7/.agents/plugins/marketplace.json) ／ [公式CLIとテレメトリー](https://github.com/GoogleChrome/modern-web-guidance#telemetry--privacy)

公式ベンチマークは、同じ課題でガイドを使った場合と使わない場合のチェック通過率を集計しています。今回の実測は、ガイドを取得できることと、二つの画面でフォーカスの戻り先が異なることまでです。 [公式評価ダッシュボード](https://googlechrome.github.io/modern-web-guidance-src/) ／ [noteの導入比較](https://developer.chrome.com/blog/mwg-with-internal-component)

自分のチームで試すなら、課題・開始時のコミット・テストをそろえ、「ガイドを使わない」「必要に応じて検索する」「ガイドIDを指定する」の三通りを比べます。対応ブラウザーで主要操作と既存テストを通したうえで、初回で合格した課題の割合と、合格までの修正回数を数えます。品質が同等なら、失敗と再試行も含めた総トークンを合格課題数で割り、値が最も小さい構成を採用します。合格が0件なら、総トークンと合格件数を記録します。

繰り返し測るなら、`legacy-scan --json` で既存コードから候補を拾い、WebDX Baselineで対応状況を確かめます。Playwrightの結果、ガイドID、トークン数は、スクリプトで課題ごとにJSONLへ記録できます。モデルに渡すのは差分、選んだガイド、失敗したテストです。ガイドを更新したときも同じ課題を回し、テストに落ちた場合は元の版を使い続けます。 [既存コードを走査する公式手順](https://developer.chrome.com/docs/modern-web-guidance/modernization-workflow) ／ [WebDX Baseline](https://github.com/web-platform-dx/web-features/blob/main/docs/baseline.md) ／ [PlaywrightのJSONレポーター](https://playwright.dev/docs/test-reporters)

まずは、テストが「閉じた」で終わっている画面を一つ選んでください。閉じた人が次にどこから操作を続けるかを決めて、そこにフォーカスがあることをテストの最後に加えます。メニューを閉じるときや、フォームの編集を取り消すときにも使える確認です。
