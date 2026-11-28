---
title: "AIエージェントの判断箇所負債を減らす開発手法"
emoji: "🔍"
type: "tech"
topics: ["ai", "aiagent", "architecture", "design", "management"]
published: false
created_at: "2026-11-28"
updated_at: "2026-11-28"
---

**判断を効率化する前に、その判断が必要になる構造を取り除く。** 将来繰り返される判断のうち、必要な能力を保持したまま削減できる負担を判断箇所負債と呼ぶ。

## 1. 問題：生成速度だけでは保守負担を評価できない

Dell’Acquaら（2026）のBCGの知識労働者758人を対象とした実験では、GPT-4の能力範囲内として選定した18課題の完了件数が12.2%増え、完了速度が25.1%向上した。能力範囲外として選定した1課題では正答率が平均19パーセントポイント低下した [1]。

示唆：AIの採用判断では、生成件数だけでなく、正答率、監督、後続の保守負担を比較する。

## 2. MISSION：判断を必要な箇所だけに集中する

[Kafstylerの使命](https://github.com/KAFKA2306/kafstyler/blob/007137cb1ba50aa1c1d5409b935a8e7616c252f6/MISSION.md)では、規模に比例して読む量や判断を増やさず、知見と仕事の状態をセッションの外へ残す。

正本を統一し、既知の操作を共通入口に寄せ、確定処理をCLIへ移す。意味の判断は必要なときだけLLMに渡す。人間にしか行えない権限・安全・責任上の判断は残す。

## 3. 定義：判断箇所は選択が必要になる箇所である

| 判断の種類 | 発生源 |
| --- | --- |
| 探索 | 仕様・仕事・根拠の所在 |
| 選択 | コマンド、担当、モデル |
| 解釈 | 規約、例外、適用条件 |
| 調整 | 他の担当や変更との依存 |
| 復旧・保守 | 失敗原因、移行、廃止 |

同じ発生条件、選択肢、根拠、担当の役割を持つ判断は同一箇所とし、発生回数を別に数える。担当者の交代だけで箇所を増やさない。

## 4. 方針：依存関係と実行入口を分離する

Narayanan & Feigh（2026）の80人の監督実験では、エージェント間の依存がある条件で負荷が増え、情報の抽象度を変えても解消されなかった [2]。Parnas（1972）は、設計上の決定をモジュール内部に隠し、変更の影響を限定する設計を論じた [3]。

採用する方針は、内部実装の変更を利用者の新しい判断にしないことだ。必要な情報だけを参照し、利用者が覚える入口と内部実装を分ける。

## 5. 手段：判断の発生源を置き換える

| 反復判断 | 実装する手段 |
| --- | --- |
| どの仕様が最新か | 単一正本と参照リンク |
| どのコマンドを使うか | 既存CLI・miseの共通タスク |
| 実行が必要か | 入力取得と機械的な差分判定 |
| どのモデルを使うか | 共通の予算・品質・利用可能性の方針 |
| 失敗か無変更か | 終了コード、実行結果、明示的な停止 |
| 権限・安全の例外 | 必要な担当と適用条件を保持 |

[実行索引](https://github.com/KAFKA2306/kafstyler/blob/007137cb1ba50aa1c1d5409b935a8e7616c252f6/COMMANDS.md)は既知のタスクを直接実行し、未知のものだけを探す構造にしている。

## 6. 実践：共通CLIへ移行する

Kafstylerの[変更前のmise.toml](https://github.com/KAFKA2306/kafstyler/blob/25afa7800567fdd5321502ccf730d12816c27212/mise.toml)と[変更後のmise.toml](https://github.com/KAFKA2306/kafstyler/blob/c8850fbd5f1d71f3d0ce108b856dc70f0fc8ba51/mise.toml)では、モデル選定器の内部パスを移動しながら共通タスク名を保持した。

| 対象 | 変更前 | 変更後 |
| --- | --- | --- |
| 利用者の入口 | `mise run model-select` | 同じ |
| 内部実装 | `node .agents/select-models.mjs` | `node skills/adjudicate/scripts/select-models.mjs` |
| 入力 | 外部ポリシー | 同じ |

実際の利用時は、導入先で採用済みのモデル選定ポリシーを渡す。

```bash
mise run model-select --policy "$POLICY"
```

移行する対象の内部パスを直接参照する箇所は、既存Gitで検索する。対象リポジトリのルートで実行する。

```bash
git grep -n -F -e '.agents/select-models.mjs' HEAD --
```

[git grepの仕様](https://git-scm.com/docs/git-grep)。検索対象は指定版の追跡ファイルであり、外部設定・動的呼出元は別に特定する。共通入口へ参照を寄せ、旧経路を利用する必要がなくなった範囲を廃止する。

導入先でも、一つの既存操作を選び、入口、入力、出力、失敗時の意味を既存タスク定義に移す。単純なCLIをそのまま使える場合は、新しいラッパーを作らない。

## 7. 示唆：保守と失敗の原因を実行性能から分離する

Borgら（2026）はJavaのWebアプリケーションをAI支援あり・なしで作り、後から別の開発者がAIなしで変更する二段階実験を実施した。後半の75人の比較では変更時間・品質の有意差は検出されず、小〜中程度の差を検出する力には限界があった [4]。

Cemriら（2025）は7種類の複数エージェント基盤の1,600件以上の実行履歴から、システム設計、エージェント間の不整合、結果確認に関する14種類の失敗を分類した [5]。

示唆：モデル性能だけに原因を求めず、正本、依存、入出力、失敗時の挙動を設計する。

## 8. 採否：消えた判断ではなく減った負担を見る

既存の履歴から、判断箇所、担当の役割、発生回数、人間の作業時間、参照先、失敗・復旧時間を取得する。仕事の種類と収集範囲を揃える [6]。

判断箇所数が減っても、残る判断に時間がかかる、復旧が困難になる、別の担当に負担が移るなら削減とは扱わない。未取得の値はゼロにしない。

## 9. 運用仕様：一件の削減候補を実装へ渡す

入力は第1部の対象業務・受入条件・観測期間と既存の実行履歴。出力は判断の発生条件、選択肢、役割、根拠、頻度、時間、依存、失敗、削減候補、保持条件である。

モデル選定の事例なら、共通タスク名と入力契約を保持し、直接呼出元を特定する。この結果を第3部の削除・統合・置換の判断へ渡す。

## 連載

- 第1部：[組織エントロピーの反転](https://github.com/KAFKA2306/articles/blob/main/articles/2026-11-28-01-decision-load-design.md)
- 第2部：判断箇所負債（本稿）
- 第3部：[自己減算型知能機関](https://github.com/KAFKA2306/articles/blob/main/articles/2026-11-28-03-self-subtracting-agents.md)

## 参考文献

1. Dell’Acqua, F., et al. (2026). Navigating the Jagged Technological Frontier: Field Experimental Evidence of the Effects of Artificial Intelligence on Knowledge Worker Productivity and Quality. *Organization Science*, 37(2), 403–423. https://doi.org/10.1287/orsc.2025.21838
2. Narayanan, R., & Feigh, K. M. (2026). Designing for Oversight: An Empirical Investigation of the Dual Impact of AI Dependency and Information Abstraction on Human Supervision in Decision-Making Teams. *International Journal of Human–Computer Interaction*, 42(18), 15444–15473. https://doi.org/10.1080/10447318.2026.2618568
3. Parnas, D. L. (1972). On the criteria to be used in decomposing systems into modules. *Communications of the ACM*, 15(12), 1053–1058. https://doi.org/10.1145/361598.361623
4. Borg, M., et al. (2026). Echoes of AI: Investigating the downstream effects of AI assistants on software maintainability. *Empirical Software Engineering*, 31(6), 161. https://doi.org/10.1007/s10664-026-10889-1
5. Cemri, M., et al. (2025). Why Do Multi-Agent LLM Systems Fail? *Advances in Neural Information Processing Systems*, 38, Datasets and Benchmarks Track. https://doi.org/10.52202/085713-4082
6. Runeson, P., & Höst, M. (2009). Guidelines for conducting and reporting case study research in software engineering. *Empirical Software Engineering*, 14, 131–164. https://doi.org/10.1007/s10664-008-9102-8
