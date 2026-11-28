---
title: "AIが増やす判断箇所負債を測る"
emoji: "🔍"
type: "tech"
topics: ["ai", "aiagent", "architecture", "design", "management"]
published: false
created_at: "2026-11-28"
updated_at: "2026-11-28"
---

**判断箇所はファイル数ではなく、仕事の中で選択が必要になる箇所として数える。** AIエージェントを採用するときは、実行速度と、将来の担当者が何を読み、何を選び、何を確認する必要があるかを別々に比較する。

本稿では、必要な能力を維持したまま削減できる反復判断の負担を「判断箇所負債」と呼ぶ。これは著者の設計上の定義であって、確立された査読済み尺度ではない。

## 1. 問題：生成速度だけでは保守負担を評価できない

Dell’Acquaら (2026) のBCGの知識労働者758人を対象とした実験では、GPT-4の能力範囲内として選んだ18課題で完了件数が12.2%増え、完了速度が25.1%向上した。一方、能力範囲外として選定した1課題では正答率が平均19パーセントポイント低下した [1]。

AIの利用効果は課題によって異なる。実行件数と正答率、監督負荷、後続担当者の負担は分けて観測する。

## 2. 中心命題：判断を速くする前に、判断の発生源をなくす

[KafstylerのMISSION](https://github.com/KAFKA2306/kafstyler/blob/007137cb1ba50aa1c1d5409b935a8e7616c252f6/MISSION.md)は判断時間を規模に比例させないこと、知見と状態をセッションの外に保持することを原則とする。

反復判断をAIに移しても、その判断が発生する構造や監督の必要性がなくなったとは限らない。Kafstylerでは確定処理と意味判断を分け、必要な判断だけをLLMへ割り当てる。

## 3. 定義：判断箇所を特定する

判断箇所は、ある条件で複数の行動から選択する必要がある箇所とする。同じ規約が複数ファイルに書かれているだけでは、独立した判断が複数あるとは限らない。

| 判断の種類 | 棚卸し対象 |
| --- | --- |
| 探索 | 仕様・仕事の状態・根拠を探す |
| 選択 | 実行入口、モデル、担当を選ぶ |
| 解釈 | 規約、例外、適用条件を解釈する |
| 調整 | 他の変更や担当との依存を扱う |
| 復旧・保守 | 失敗の原因を特定し、更新や廃止を判断する |

判断箇所負債は、これらのうち代替設計によって削減可能な反復負担を指す。安全や責任上必要な判断は件数だけで削減対象にしない。

## 4. 仕組み：判断を要求する依存と状態を分離する

Narayanan & Feigh (2026) の80人を対象とした監督実験では、AIエージェント間の依存がある条件で負荷が増えた。情報の抽象化では増加を解消できず、軽度のエラーが見落とされやすかった [2]。

Parnas (1972) は設計上の決定をモジュール内部に隠すことで、変更の影響範囲を限定する設計原理を論じた。ただし実装によっては実行効率が低下することも指摘した [3]。

Kafstylerはこの論点を、共通規約と専門手順の分離、単一正本、既存CLIへの確定処理の委譲という開発方針へ接続している。

## 5. 測定：箇所数、頻度、実際の負担を別々に記録する

以下は本稿の提案する観測仕様であり、予測妥当性の確立した尺度ではない。

| 項目 | 記録する内容 |
| --- | --- |
| 判断箇所 | 発生条件・選択肢・担当・根拠 |
| 発生頻度 | 回／観測期間 |
| 判断時間 | 人分／回、期間内の合計 |
| 依存 | 参照する正本、前後の処理、影響先 |
| 失敗 | 誤判断・手戻り・復旧時間 |
| 運用費用 | AI使用料、関連する維持費 |

時間を合計するときは重複する観測を除く。複数人が同時に判断した場合は人ごとの時間を加える。判断箇所数、発生回数、所要時間を混同せず、実際の負担を比較する。

同じ発生条件・選択肢・根拠・担当の役割で繰り返す判断は一つの箇所とし、発生回数を別に数える。担当者の交代だけで別箇所にしない。権限や例外条件によって採否が変わる場合は分ける。これは棚卸しの識別規則であり、妥当性が実証された分類尺度ではない。

## 6. 実践：判断の入口と発生条件を棚卸しする

1. 一つの反復業務と観測期間を選ぶ。
2. 実際の操作履歴から、判断が必要だった条件、参照先、選択肢、担当を抽出する。
3. 発生頻度と実際の判断時間、手戻りを把握する。観測できないものは未測定とする。
4. 確定処理へ移せる箇所、正本を統一できる箇所、必要な人間の判断を区別する。
5. 変更候補と保持条件を第3部に渡し、変更後も同じ観測項目で比較する。

この手順は観測と設計の提案である。専用の台帳は不要であり、既存のIssueや実行履歴を優先する。

### 具体例：共通の実行入口が内部変更を隠す

Kafstylerのモデル選定タスクを、[変更前のmise.toml](https://github.com/KAFKA2306/kafstyler/blob/25afa7800567fdd5321502ccf730d12816c27212/mise.toml)と[変更後のmise.toml](https://github.com/KAFKA2306/kafstyler/blob/c8850fbd5f1d71f3d0ce108b856dc70f0fc8ba51/mise.toml)で比較する。

| 対象 | 変更前 | 変更後 |
| --- | --- | --- |
| 利用者の入口 | `mise run model-select` | 同左 |
| 内部の実装 | `node .agents/select-models.mjs` | `node skills/adjudicate/scripts/select-models.mjs` |

両版ともタスク名は同じで、外部ポリシーを渡す契約も残っている。miseを利用する担当者には実装の移動先を選択させない構造になっている。これは情報隠蔽の具体例である [3]。

この資料から、次の棚卸し結果を得られる。

| 項目 | 観測・判定 |
| --- | --- |
| 発生条件 | モデル選定タスクを利用する |
| 利用者の役割 | miseを経由する実行担当 |
| 実行入口の選択 | 共通タスク名は変更されていない |
| 参照先・保持条件 | mise.toml、タスク名、外部ポリシーの入力契約 |
| 依存 | 内部実装のパスが変更された |
| 発生頻度・判断時間・失敗 | 未測定 |
| 直接呼出元 | この2ファイルからは特定不能 |
| 第3部に渡す判断 | 共通入口を保持し、直接呼出元があれば別に扱う |

構造の変更は観測できるが、利用者の反復判断が実際に何回減ったかは判定できない。未測定をゼロとせず、削減済みの負債として計上しない。

## 7. 根拠：保守性と失敗は実行性能と分けて調べられている

Borgら (2026) はJavaのWebアプリケーションをAI支援あり・なしで作り、後から別の開発者がAIなしで変更する二段階実験を行った。後半の参加者75人の比較では変更時間・コード品質の有意差は検出されなかった。小〜中程度の差を検出するには標本数が不足しており、保守性の同等性を証明したわけではない [4]。

Cemriら (2025) はNeurIPSの論文で7種類の複数エージェント基盤の1,600件以上の実行履歴を分析し、失敗をシステム設計、エージェント間の不整合、タスクの結果確認に関する14種類へ分類した [5]。

Kafstylerの参照実装では、[canonicalize](https://github.com/KAFKA2306/kafstyler/blob/007137cb1ba50aa1c1d5409b935a8e7616c252f6/skills/canonicalize/SKILL.md)で対象と正本を統一し、[Issue駆動開発](https://zenn.dev/kafka2306/articles/issue-driven-development)で仕事の状態を会話から分離する。[Crash-Driven Development](https://zenn.dev/kafka2306/articles/11cd731eebded1)では失敗を空データや成功に変えない。差分のない日常保守はLLMを起動せず、取得失敗とは区別する。

以上は実装方針の一次資料であり、Kafstylerにおける削減効果の測定結果ではない。

## 8. 反証条件：箇所数を減らしても負担が増えれば失敗である

残った判断が難しくなり、時間や失敗が増えた場合、箇所数の減少を改善とみなさない。別の担当者や下流の処理へ判断を移した場合も同様である。

必須の安全判断や権限を消した変更は採用しない。測定値だけではどの構造が原因かを確定できないため、仕事の構成や他の変更を区別する。

## 9. 標準仕様案：変更候補を渡せる形にする

入力：第1部の対象業務、観測期間、受入条件、既存の操作・実行履歴。

出力：判断箇所ごとの発生条件、選択肢、担当の役割、頻度、時間、参照先、依存、失敗、削減候補、保持条件、出典、未測定項目。

実測した判断時間は第1部の総管理時間に含め、二重計上しない。第3部にはこのうち変更候補に必要な情報を渡す。分野を越えた計測尺度としての妥当性は未確認である。

## 連載の位置づけ

第1部の観測条件を受け取り、判断箇所、依存、削減候補、保持条件を第3部へ渡す。

- 第1部：[組織エントロピーの反転](https://github.com/KAFKA2306/articles/blob/main/articles/2026-11-28-01-decision-load-design.md)
- 第2部：判断箇所負債（本稿）
- 第3部：[自己減算型知能機関](https://github.com/KAFKA2306/articles/blob/main/articles/2026-11-28-03-self-subtracting-agents.md)

## 参考文献

1. Dell’Acqua, F., et al. (2026). Navigating the Jagged Technological Frontier: Field Experimental Evidence of the Effects of Artificial Intelligence on Knowledge Worker Productivity and Quality. *Organization Science*, 37(2), 403–423. https://doi.org/10.1287/orsc.2025.21838
2. Narayanan, R., & Feigh, K. M. (2026). Designing for Oversight: An Empirical Investigation of the Dual Impact of AI Dependency and Information Abstraction on Human Supervision in Decision-Making Teams. *International Journal of Human–Computer Interaction*, 42(18), 15444–15473. https://doi.org/10.1080/10447318.2026.2618568
3. Parnas, D. L. (1972). On the criteria to be used in decomposing systems into modules. *Communications of the ACM*, 15(12), 1053–1058. https://doi.org/10.1145/361598.361623
4. Borg, M., et al. (2026). Echoes of AI: Investigating the downstream effects of AI assistants on software maintainability. *Empirical Software Engineering*, 31(6), 161. https://doi.org/10.1007/s10664-026-10889-1
5. Cemri, M., et al. (2025). Why Do Multi-Agent LLM Systems Fail? *Advances in Neural Information Processing Systems*, 38, Datasets and Benchmarks Track. https://doi.org/10.52202/085713-4082
