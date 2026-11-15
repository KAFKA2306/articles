---
title: "AIが作った確認画面、閉じたあとにどこへ戻る？"
emoji: "⌨️"
type: "tech"
topics: ["html", "playwright", "accessibility", "ai", "evals"]
published: false
---

公開前の確認画面をキーボードで開き、考え直して `Escape` で閉じます。そこでフォーカスが「公開する」ボタンへ戻れば、操作を続けられます。見出しへ飛ばされた場合は、同じ場所からやり直せません。どちらも開いている間は同じ見た目で、閉じるところまでのテストも通ります。

AIに画面を作らせるとき、確認したいのは「新しいAPIを使ったか」よりも、この一連の操作を利用者が完了できるかです。今回は、同じHTMLからフォーカスの戻り先だけを変えた二つの実装を用意し、どこまでテストすれば差が分かるかを試しました。

## 開く・移動する・閉じる。最後の一手だけ差が出た

二つともネイティブの `<dialog>` を `showModal()` で開きます。片方にだけ、閉じたときにページ見出しへフォーカスを移す処理を加えました。Playwright 1.64.0とChromium 153.0.8010.0を使い、画面幅390pxでTab、Enter、Tab、Escapeの順に操作した結果です。 [Playwrightの使用版](https://github.com/microsoft/playwright/releases/tag/v1.64.0)

| 観測した動作 | 標準の動作 | 閉じたあと見出しへ移す実装 |
| --- | --- | --- |
| Enterで開き、「キャンセル」にフォーカスする | 通過 | 通過 |
| Tabで「公開を確定」へ移る | 通過 | 通過 |
| Escapeで閉じる | 通過 | 通過 |
| 「公開する」ボタンへ戻る | 通過 | 失敗。見出しへ移動 |

同じAPIを使う実装でも、最後に追加した処理で操作は変わります。W3Cのモーダルダイアログのパターンでは、起点が残っている場合は原則としてそこへフォーカスを戻し、起点が消えた場合や作業の流れに沿う場合には別の場所を選びます。この例では、取り消した後に元のボタンが残るので、そのボタンを期待値にしました。 [W3Cのモーダルダイアログのパターン](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) ／ [HTMLのdialogを使う手法](https://www.w3.org/WAI/WCAG22/Techniques/html/H102)

### 自分の画面で再現する

既存のPlaywright Testで、開くボタンとダイアログ名を実画面に合わせます。この例ではキャンセルが初期フォーカスで、閉じた後も起点が残ることを前提にしています。

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

検査の感度を確かめるには、一時的に見出しに `tabindex="-1"` を付け、`close` イベントでその見出しに `focus()` します。閉じたことの検査は通り、戻り先の検査で落ちるはずです。全ページの回帰検査では起点までTabで到達できるかも確かめます。採点はロール・名前・フォーカスの観測で行えるので、既存のデザインシステムが同じ操作を実現していれば同じテストで判定できます。 [Playwrightのアクセシビリティ検査](https://playwright.dev/docs/accessibility-testing)

## ガイドを引けることと、採用する価値を別々に測る

Modern Web Guidance 1.0.0は、検索結果から必要なガイドをIDで取得できます。隔離環境で公式スキルを導入し、短い検索語 `confirmation modal dialog` の先頭が `dialog` になること、その本文を取得できること、既存コードの走査からJSONが返ることを確認しました。公式スキルの配布設定はリリースコミット、実行するCLIはnpm版を固定し、各呼び出しには `DISABLE_TELEMETRY=1` を渡しました。 [導入と動作確認のPR](https://github.com/KAFKA2306/agent-resources/pull/586) ／ [検証時の配布設定](https://github.com/KAFKA2306/agent-resources/blob/035cec2ac8a9929e942406d20f516ff39dbdb5b7/.agents/plugins/marketplace.json) ／ [公式CLIとテレメトリー](https://github.com/GoogleChrome/modern-web-guidance#telemetry--privacy)

公開ベンチマークは、ガイドの有無で同じ課題の自動チェック通過率を比較しています。自分のチームで投資対効果を知りたいときは、同じ課題・コミット・採点を固定し、ガイドなし、必要時の検索、ガイドID指定の三条件を回します。まず対応ブラウザーで主要操作と既存の回帰検査を通し、次に初回完了率と修正回数を比較します。同等の品質を保てた候補から、失敗・再試行を含めた総トークンを合格課題数で割り、最も小さい構成を採用します。合格が0件なら、総量と件数をそのまま残します。ここで実測したのは取得経路と一つの操作の差までです。生成品質やトークン削減は、各チームの課題で評価します。 [公式評価ダッシュボード](https://googlechrome.github.io/modern-web-guidance-src/) ／ [noteの導入比較](https://developer.chrome.com/blog/mwg-with-internal-component)

繰り返す場合は、既存コードの候補抽出を `legacy-scan --json`、互換性の照合をWebDX Baseline、操作の採点をPlaywrightのJSONレポーターに任せます。スクリプトはガイドID・判定・消費量を課題ごとのJSONLにまとめ、モデルに渡すのは対象の差分、選んだガイド、失敗した検査だけです。ガイド更新時は同じ課題を再実行し、受け入れ条件に落ちたら以前の構成を保持します。 [既存コードを走査する公式手順](https://developer.chrome.com/docs/modern-web-guidance/modernization-workflow) ／ [WebDX Baseline](https://github.com/web-platform-dx/web-features/blob/main/docs/baseline.md) ／ [PlaywrightのJSONレポーター](https://playwright.dev/docs/test-reporters)

手元で始めるなら、テストが「開いた」「閉じた」で終わっている画面を一つ選び、利用者が次に押すキーを一つ決めます。そのキーがどの要素に届くかを期待値に入れ、戻り先を変えた実装で実際に落ちることを確かめます。このやり方は、操作の前後で状態を引き継ぐメニューやフォームにも持ち込めます。
