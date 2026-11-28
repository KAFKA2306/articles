---
title: "不要な仕組みを自ら廃止するAIエージェント設計"
emoji: "✂️"
type: "tech"
topics: ["ai", "aiagent", "architecture", "design", "management"]
published: false
created_at: "2026-11-28"
updated_at: "2026-11-28"
---

**改善を担うエージェント自身も、不要になれば廃止する。** 必要な能力を保ち、不要な規約、ジョブ、ツール、実行経路を減らす組織を自己減算型知能機関と呼ぶ。

## 1. 問題：改善案の探索が追加に偏る

Adamsら（2021）は8実験で、人が有益な削除案を見落としやすいことを示した。第4実験の改善条件では削除案を一つ以上挙げた割合が、削除を促さない群の21%から、促した群の48%に増加した [1]。

示唆：改善案には最初から削除、統合、置換、現状維持を含める。

## 2. MISSION：改善する仕組みも仕事を終える

[Kafstylerの使命](https://github.com/KAFKA2306/kafstyler/blob/007137cb1ba50aa1c1d5409b935a8e7616c252f6/MISSION.md)は、上流の標準機能を活用し、必要な能力を保持したまま不要な仕組みを退役させることを目標とする。

差分のない保守にLLM費用を生じさせない。改善担当が自らの稼働を維持するために仕事を作る構造を採用しない。

## 3. 定義：改善案を5種類に分ける

| 選択肢 | 採用条件 |
| --- | --- |
| 削除 | 必要な成果への寄与がなく、固有情報と依存への対応が済んでいる |
| 統合 | 重複する役割を一つの後継で担える |
| 置換 | 既存の標準機能が必要な能力を引き継げる |
| 維持 | 変更の利益が費用やリスクに見合わない |
| 追加 | 既存構成では必要な能力を満たせない |

必要な能力、利用経路、データ保全、認可を満たす候補から選ぶ。

## 4. 方針：既存の構成を比較対象にする

Kimら（2026）は3系統のLLM、6種類のベンチマーク、260構成を同じ計算予算などで比較し、単一エージェントの基礎性能と協調の利点の関係を分析した [2]。Narayanan & Feigh（2026）はエージェント間の依存がある条件で監督負荷が増えたと報告した [3]。

KISS、YAGNI、疎結合を新規実装だけでなく既存の仕組みに適用する。

## 5. 手段：確定処理をLLMから取り除く

| 現在の処理 | 移管先 |
| --- | --- |
| 定期起動 | 既存OS・スケジューラ |
| 入力取得・同期 | 既存CLI |
| 変更の判定 | Git・更新識別子・数式 |
| 定型操作 | 共通タスク |
| 意味の判断 | 必要な場合だけLLM |
| 役割を終えた処理 | 後継へ移行して廃止 |

入力が変わらず成果が既に反映されている日常保守を最初の対象にする。新情報の探索、創作、時間に依存する処理は別に扱う。

## 6. 実践：入力差分があるときだけ処理を起動する

### 最後に処理した版と現在の版を比較する

既存のGitリポジトリを使う差分保守では、直前のコミットではなく、**成果の反映に成功した最後の入力版**を比較の起点とする。処理の途中で失敗した版を処理済みにしない。

次のBash関数を、既存の実行入口に組み込む。対象は必須の追跡ファイルで、比較するコミットと入力パスを渡す。

```bash
needs_work() {
  local old new path rc
  old=$(git rev-parse --verify "$1^{commit}") || return 2
  new=$(git rev-parse --verify "$2^{commit}") || return 2
  shift 2
  [ "$#" -gt 0 ] || return 2
  for path in "$@"; do
    git cat-file -e "$old:$path" || return 2
    git cat-file -e "$new:$path" || return 2
  done
  if git diff --quiet --no-ext-diff "$old" "$new" -- "$@"; then
    return 1
  else
    rc=$?
    [ "$rc" -eq 1 ] && return 0
    return 2
  fi
}
```

[git diffの仕様](https://git-scm.com/docs/git-diff)。

| 終了コード | 実行する処理 |
| --- | --- |
| 0 | 必要な後続処理を実行 |
| 1 | 正常な無変更として終了 |
| 2 | 入力取得・比較の失敗として停止 |

既存の実行処理はこの分岐を使い、成功したときだけ既存の成果の記録に処理済み版を反映する。対象入力の更新、成果の反映、処理済み版の記録は同じ担当に直列化する。ファイル以外の外部入力、ツール版、設定、時刻に依存する場合はそれらも比較条件に含める。

### 実行例

Git 2.47.3の一時リポジトリで、Aにsource.mdとpolicy.mdを登録し、Bでpolicy.mdだけを変更、Cで対象外のother.mdだけを追加した。対象はsource.mdとpolicy.mdである。

| 比較 | 実行結果 |
| --- | --- |
| A→B | 変更あり（0） |
| B→C | 変更なし（1） |
| A→C | 変更あり（0） |
| 存在しない入力パス | 停止（2） |
| 不正なコミット | 停止（2） |
| 入力パス未指定 | 停止（2） |

この実行結果が示すのは、複数の必須入力について処理の必要性を区別できることだ。LLMの起動削減は、この分岐を既存の保守処理の起動前に配置して実現する。

### 旧経路を廃止する

[decommission Skill](https://github.com/KAFKA2306/kafstyler/blob/007137cb1ba50aa1c1d5409b935a8e7616c252f6/skills/decommission/SKILL.md)に従う。

1. 目的、利用経路、依存、保持情報を特定する。
2. 削除・統合・置換・維持・追加を比較する。
3. 後継と正本を決め、必要な情報と利用経路を移す。
4. 認可範囲で不要な旧設定、ジョブ、参照を同じ変更で廃止する。
5. 改善担当自身も同じ採否条件に戻す。

## 7. 示唆：削る対象は文書の量ではなく不要な負担である

Matsuo（2026）は日本企業の知的財産部門の管理者385人の自由記述から、効率改善、ネットワークの再構成、戦略変更というアンラーニングの種類を分類し、取り組みの種類と部門間連絡の関連が異なることを示した [4]。

Kafstylerの廃止Skillは[6行の版](https://github.com/KAFKA2306/kafstyler/blob/25afa7800567fdd5321502ccf730d12816c27212/skills/decommission/SKILL.md)から[23行の版](https://github.com/KAFKA2306/kafstyler/blob/60918ff6d60aa5d2ecdc7e8c982c28ae6587f561/skills/decommission/SKILL.md)へ改訂し、依存、後継の能力、保持情報、判断不能時の扱いを明記した。

必要な判断基準は保持する。削除件数や行数を成果指標にしない。

## 8. 採否：削減によって必要な能力を失わない

同じ業務の受入条件で、成果、能力、判断時間、実際のLLM起動数、運用費用、失敗、移行費用を比較する。

必要な能力を失う、費用が増える、負担を他者へ移す変更は改善として扱わない。判断材料が不足している対象は必要な根拠を取得し、解消できないものは保持する。

## 9. 運用仕様：次の改善を必要なときだけ行う

入力は第1・第2部から受け取る対象業務、判断箇所、依存、保持条件と認可範囲。出力は採用した変更、廃止・保持した対象、後継、移行費用、変更後の成果・能力・管理負荷である。

変更後の観測を第1部へ戻す。第2部で新たに発生した判断も扱う。改善する価値のある仕事がなければ、改善ジョブ自身を維持するための仕事を作らない。

## 連載

- 第1部：[組織エントロピーの反転](https://github.com/KAFKA2306/articles/blob/main/articles/2026-11-28-01-decision-load-design.md)
- 第2部：[判断箇所負債](https://github.com/KAFKA2306/articles/blob/main/articles/2026-11-28-02-decision-point-debt.md)
- 第3部：自己減算型知能機関（本稿）

## 参考文献

1. Adams, G. S., Converse, B. A., Hales, A. H., & Klotz, L. E. (2021). People systematically overlook subtractive changes. *Nature*, 592, 258–261. https://doi.org/10.1038/s41586-021-03380-y
2. Kim, Y., et al. (2026). Capable language models can outgrow the benefits of collaboration. *Nature Machine Intelligence*, 8, 1157–1172. https://doi.org/10.1038/s42256-026-01268-y
3. Narayanan, R., & Feigh, K. M. (2026). Designing for Oversight: An Empirical Investigation of the Dual Impact of AI Dependency and Information Abstraction on Human Supervision in Decision-Making Teams. *International Journal of Human–Computer Interaction*, 42(18), 15444–15473. https://doi.org/10.1080/10447318.2026.2618568
4. Matsuo, M. (2026). Manager-initiated unlearning: A study of intellectual property departments in Japanese firms. *European Management Review*. Published online 1 March 2026. https://doi.org/10.1111/emre.70058
