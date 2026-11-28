---
title: "AI組織を成長させながら管理負荷を減らす設計"
emoji: "🧭"
type: "tech"
topics: ["ai", "aiagent", "architecture", "design", "management"]
published: false
created_at: "2026-11-28"
updated_at: "2026-11-28"
---

組織の成長とともに、人間の管理業務まで増える設計を採用しない。**利用者に届く成果を増やしながら、必要な能力を保ち、人間の管理時間を減らす。** これを組織エントロピーの反転と呼ぶ。

## 1. 問題：実行能力と管理負荷は別の指標である

Cuiら（2026）は、3社の開発者4,867人を対象とした無作為化実験の統合分析で、AIコーディング支援による完了タスク数の26.08%増加を報告した（標準誤差10.3%）[1]。

Narayanan & Feigh（2026）の80人を対象とした監督実験では、エージェント間の依存関係がある条件で人間の監督負荷が増加した。情報の抽象度を変えても、その増加は解消されなかった [2]。

示唆：エージェントの処理能力を増やすことと、管理業務の発生源を減らすことを別々の設計課題にする。

## 2. MISSION：利用者の成果と人間の余力を増やす

[Kafstylerの使命](https://github.com/KAFKA2306/kafstyler/blob/007137cb1ba50aa1c1d5409b935a8e7616c252f6/MISSION.md)を、組織設計の成功条件に接続する。

- 成果を利用者の入口まで届ける。
- 担当AIやセッションが変わっても仕事を再開できるようにする。
- 案件が増えても、読む量と重複運用を増やさない。
- 差分のない日常保守でLLMを起動しない。
- 既存の標準ツールを利用し、モデルや基盤を交換可能にする。

エージェントの追加、生成量、報告件数を目的にしない。

## 3. 定義：組織の成長を何で判定するか

| 指標 | 数える対象 |
| --- | --- |
| 成果 | 利用者が受け取れる、同じ受入条件の完了件数 |
| 能力 | 必要な品質・安全性で提供できる業務の範囲 |
| 規模 | 対象案件数、利用者数、仕事量 |
| 管理時間 | 探索、判断、調整、監督、引き継ぎ、保守に要する人時間 |
| 運用費用 | AI・外部サービス・維持に要する費用 |

異なる種類の成果は分けて扱う。管理時間と費用は別の指標とする。

## 4. 方針：処理能力を増やす前に処理需要を減らす

Galbraith（1974）は、情報処理能力を増やす方法と、情報処理の必要性を減らす方法を区別した [3]。Kimら（2026）は3系統のLLM・6種類のベンチマーク・260構成を比較し、単一エージェントの基礎性能が協調の利点を説明する重要な要因になると報告した [4]。

採用する設計方針は、単一の既存担当を比較の基準とし、独立した仕事は並行化し、相互依存する仕事の調整を必要最小限にすることだ。役割ごとにエージェントを作らない。

## 5. 手段：目的・仕事・実装・成果の正本を分離する

新しい管理基盤を作る前に、既存の課題管理とGitを使う。

| 役割 | 正本 | 廃止候補 |
| --- | --- | --- |
| 目的 | MISSION・事業目的 | 担当別の目的の再掲 |
| 仕事と再開条件 | Issue | 会話だけの進捗、重複台帳 |
| 実装と履歴 | Git | 差分の転記 |
| 実行 | 既存CLI・担当・起動基盤 | 同じ対象の重複担当 |
| 成果 | 公開先・利用者の入口 | 成果物のない報告 |

参照実装：[KafstylerのAGENTS.md](https://github.com/KAFKA2306/kafstyler/blob/007137cb1ba50aa1c1d5409b935a8e7616c252f6/AGENTS.md)、[自律実行Skill](https://github.com/KAFKA2306/kafstyler/blob/007137cb1ba50aa1c1d5409b935a8e7616c252f6/skills/autocatalyze/SKILL.md)。

## 6. 実践：一件の仕事を成果まで進める

既存のエージェント指示書に、次の方針を取り込む。新規の規約ファイルや進捗台帳は不要である。

```markdown
- MISSIONに沿う既存の未完了案件を一件選ぶ。
- 利用者が受け取る成果と受入条件を特定する。
- 対象・入力・権限・担当・現状を既存の正本から取得する。
- 認可された範囲で既存CLIを使い、成果まで実装する。
- 未確認を理由に止まらず、必要な情報を取得する。
- 失敗と正常な無変更を区別し、解消可能な障害を修正する。
- 完了案件は閉じ、未完了案件には原因と再開条件を残す。
```

GitHubを使う環境では、認証済みの既存CLIで後続担当が同じIssueを読む。対象リポジトリ名と番号は既存案件のものを渡す。

```bash
gh issue view "$ISSUE" --repo "$REPO" \
  --json number,title,body,state,comments,url
```

[GitHub CLIの実行契約](https://cli.github.com/manual/gh_issue_view)。取得失敗を空の仕事一覧に変換しない。実際の成果の状態から再開地点を決める。

## 7. 示唆：協業は担当の増加ではなく必要な能力で設計する

Dell’Acquaら（2026）のP&Gの専門職791人を対象とした商品開発実験では、AIを利用した個人がAIなしの2人チームに匹敵する成果を出した [5]。Josephら（2026）の病院における電子カルテ導入研究では、意思決定の分散と役割・手順に関する共通理解の関連が報告された [6]。

Kafstylerでは実行契約の入口を[209行の文書](https://github.com/KAFKA2306/kafstyler/blob/bc5d2cc801a364bf580d86de441d7754903762e3/COMMANDS.md)から[36行の索引](https://github.com/KAFKA2306/kafstyler/blob/25afa7800567fdd5321502ccf730d12816c27212/COMMANDS.md)へ変更し、詳細を4領域に分離した。

示唆：仕事単位を自立させ、必要な契約だけを参照する。入口の行数と実際の管理時間は別に測る。

## 8. 採否：効率化と負荷の反転を区別する

| 変更前後の結果 | 判定 |
| --- | --- |
| 成果増加・管理時間減少・運用費用非増加 | 反転 |
| 成果増加・管理時間一定・運用費用非増加 | 負荷非増加 |
| 成果当たり時間減少・総管理時間増加 | 効率化 |
| 時間減少・費用増加 | トレードオフ |
| 必要な能力・品質・安全の低下、負担の転嫁 | 不採用 |
| 観測値不足 | 判定不能 |

比較には同じ種類の業務、観測期間、受入条件を使う。旧構成を対照とし、モデル版・予算・権限を揃える。独立した仕事への割付や担当者の技能差を考慮する [7]。失敗、再試行、救済を含める。変更後の成果と管理時間の観測がそろった段階で、表の判定を適用する。

## 9. 運用仕様：次の改善対象へ接続する

入力は既存案件、成果の受入条件、業務の範囲と観測期間。出力は利用者に届いた成果、能力、総管理時間、運用費用、品質、失敗、判定、出典である。

第2部で管理時間の発生源を特定し、第3部で不要な実行経路を取り除く。変更後の値を同じ条件で比較し、次に取り組む仕事を選ぶ。

## 連載

- 第1部：組織エントロピーの反転（本稿）
- 第2部：[判断箇所負債](https://github.com/KAFKA2306/articles/blob/main/articles/2026-11-28-02-decision-point-debt.md)
- 第3部：[自己減算型知能機関](https://github.com/KAFKA2306/articles/blob/main/articles/2026-11-28-03-self-subtracting-agents.md)

## 参考文献

1. Cui, K. Z., Demirer, M., Jaffe, S., Musolff, L., Peng, S., & Salz, T. (2026). The Effects of Generative AI on High-Skilled Work: Evidence from Three Field Experiments with Software Developers. *Management Science*, 72(11), 9408–9420. https://doi.org/10.1287/mnsc.2025.00535
2. Narayanan, R., & Feigh, K. M. (2026). Designing for Oversight: An Empirical Investigation of the Dual Impact of AI Dependency and Information Abstraction on Human Supervision in Decision-Making Teams. *International Journal of Human–Computer Interaction*, 42(18), 15444–15473. https://doi.org/10.1080/10447318.2026.2618568
3. Galbraith, J. R. (1974). Organization Design: An Information Processing View. *Interfaces*, 4(3), 28–36. https://doi.org/10.1287/inte.4.3.28
4. Kim, Y., et al. (2026). Capable language models can outgrow the benefits of collaboration. *Nature Machine Intelligence*, 8, 1157–1172. https://doi.org/10.1038/s42256-026-01268-y
5. Dell’Acqua, F., et al. (2026). The Cybernetic Teammate: A Field Experiment on Generative AI and Teamwork. *Organization Science*, 37(4), 1217–1242. https://doi.org/10.1287/orsc.2025.20702
6. Joseph, J., Wilson, A. J., Park, J., & Chow, D. (2026). Information processing, mutual understanding, and organization design in healthcare. *Strategic Management Journal*. Published online 20 August 2026. https://doi.org/10.1002/smj.70116
7. Kitchenham, B., & Madeyski, L. (2024). Recommendations for analysing and meta-analysing small sample size software engineering experiments. *Empirical Software Engineering*. https://doi.org/10.1007/s10664-024-10504-1
