---
title: "AIを替えるたびに同じ指示を書かない。作業契約をGitで共有する設計"
emoji: "🧩"
type: "tech"
topics: ["aiagents", "github", "mcp", "codex", "unity"]
published: false
---

同じ開発作業をCodexからClaude Codeへ引き継ぐ。別のGitHubリポジトリでも、過去に学んだ失敗や完了条件を使いたい。

このとき毎回、長いプロンプトを貼り直すのはつらい。一方で、各リポジトリの `AGENTS.md`、`CLAUDE.md`、Skill、設定ファイルへ同じ規則をコピーしていくと、今度はどれが最新なのか分からなくなる。

私は複数のリポジトリをAIで運用する中で、この「説明の重複」が新たな仕事になることを経験した。[過去の運用記録](https://github.com/KAFKA2306/articles/blob/main/articles/chatgpt-multiproject-autonomy.md)では、123個の非forkリポジトリを横断した際、作業状態の再発見と完了判定が問題になり、ルールを増やしすぎると逆に判断コストが上がることを書いている。

そこで今回は、**AIの記憶を統一するのではなく、仕事の入力・専門知識・実行能力・結果の形式だけをGitで共有する**案を整理した。

これは2026年11月9日時点の**設計稿**である。以下の `avatar-agent-pack` という共有リポジトリは設計上の仮名で、公開済みの実装や複数AIでの成功率を示すものではない。実際に動かした証拠がない部分は設計と明記する。

## 以前の方針と矛盾しないか

以前は、各リポジトリに独自の用語・台帳・検証手順を足しすぎる問題も経験した。[その記録](https://github.com/KAFKA2306/articles/blob/main/articles/2026-08-16-01-standard-terms-not-rigid-workflows.md)では、既存のGit・テスト・レビューで十分なら、新しい枠組みを増やさない方針にした。

今回の設計でも、最初からすべてのファイルを必須にはしない。

| 共有したいもの | 第一候補 | 増やす条件 |
| --- | --- | --- |
| リポジトリ固有の開発規則 | 既存の `AGENTS.md` | 他環境でも本当に再利用する規則がある |
| AIが発見できる専門作業手順 | `SKILL.md` | 作業領域・呼び出し条件が明確 |
| 依頼と完了条件 | JSON + JSON Schema | 自動検証・他AIへの受け渡しが必要 |
| 実ツールへの接続 | MCPの実際の `tools/list` | 接続先ごとの能力差を吸収したい |
| 繰り返す失敗・固有判断 | 出典付きの小さな記録 | 原典をその場で再発見するだけでは不十分 |
| 手順の状態遷移 | `workflow.yaml` | 単なる指示文では再開・失敗処理が曖昧 |
| 共有コードの固定版 | Git submodule | 複数リポジトリで同じ実行資産を参照する |

**最初に試すのは既存の指示ファイル＋Skill＋作業JSONだけ**。それで十分なら、workflowや独自adapterを実装しない。

## 公式仕様で決まっていること

この設計は、すでにある形式の役割を混同しない。

- [Agent Skills仕様](https://agentskills.io/specification)：Skillは `SKILL.md` のYAML frontmatterと本文からなり、`name` と `description` が必要。追加スクリプトや参照ファイルを持てる。
- [AGENTS.md](https://agents.md/)：開発エージェント向けのリポジトリ指示。標準化された必須フィールドはなく、Markdownで記述する。
- [MCP Tools仕様](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)：接続されたサーバーは `tools/list` でツール名や `inputSchema` を提示する。ツール名を推測して呼び出す必要はない。
- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/)：作業JSONと結果JSONの構造を検査するために利用する。

**これらを組み合わせた独自の `pack.yaml`、`workflow.yaml`、`knowledge.jsonl` は、標準仕様ではない。** 任意のAIが自動認識するファイルだと勘違いしないことが重要だ。

## 共有方法は3つを比較した

| 方法 | 利点 | 欠点 | 採用の判断 |
| --- | --- | --- | --- |
| 各リポジトリへコピー | 導入が容易 | 更新の重複、古い規則が残る | ごく少数・変更頻度が低い場合 |
| Git submodule | Gitコミット単位で版を固定できる | 初期化・更新・ツール対応が必要 | Gitを読めるエージェント同士で同じ資産を使う場合 |
| レジストリ／パッケージ配布 | 配布と依存解決を自動化しやすい | 配布基盤・認証・互換性管理が増える | 利用者・環境が増えてから |

今回の具体例はsubmoduleを採用する。ここでの採用は**設計上の選択**であり、実測比較で勝ったという意味ではない。

## ファイルの責務を一つずつ分ける

~~~text
avatar-agent-pack/                # 共有側。設計上の名前
├── pack.yaml                     # Packの入口・契約
├── skills/
│   └── avatar-modification/
│       └── SKILL.md              # Skill標準入口
├── workflow.yaml                 # 状態遷移。独自形式
├── knowledge.jsonl               # 根拠付きの固有知識
├── schemas/
│   ├── job.schema.json           # 入力検証
│   └── result.schema.json        # 出力検証
├── adapters/
│   └── unity-mcp.yaml            # 抽象能力の対応表
└── scripts/
    └── validate.py               # 機械的な整合性確認

consuming-repository/
├── AGENTS.md                     # ホスト側の入口
├── .agent-pack.yaml              # 共有Packの参照先
├── .agent-jobs/
│   └── sample.json               # 個別の依頼
└── .agent-packs/
    └── avatar/                    # Git submodule
~~~

すべてを`SKILL.md`へ詰め込まない。発見される入口は短くし、実際の作業時に必要な契約と知識だけを読む。

## 1. pack.yaml：何を共有するか

~~~yaml
schema_version: 1
id: kafka.avatar-modification
version: 1.0.0

entrypoint: skills/avatar-modification/SKILL.md
workflow: workflow.yaml
knowledge: knowledge.jsonl

contracts:
  input: schemas/job.schema.json
  output: schemas/result.schema.json

adapters:
  - adapters/unity-mcp.yaml

capabilities:
  required:
    - filesystem.read
    - filesystem.write
    - asset.identity.inspect
    - evidence.persist
  conditional:
    - unity.editor.inspect
    - unity.editor.mutate
    - visual.compare
    - vrchat.sdk.build_test

policy:
  no_permission_escalation: true
  preserve_vendor_originals: true
  no_automatic_publication: true
  no_completion_without_fresh_evidence: true
~~~

`filesystem.read` や `unity.editor.mutate` はこの設計で定めた**抽象能力名**であって、MCPの実際のツール名ではない。実行時に現在のツール一覧とスキーマを取得して照合する。

能力が無ければ「成功したふり」をせず、`BLOCKED` として次に必要な操作を返す。

## 2. SKILL.md：各AIが読む入口

Agent Skills仕様の`name`とディレクトリ名を揃える。

~~~markdown
---
name: avatar-modification
description: >
  Modify and validate Unity/VRChat avatar assets.
  Use for outfit fitting, materials, rigging,
  expressions, animations, and reference repair.
---

# Execution

1. Read the consuming repository's AGENTS.md.
2. Read .agent-pack.yaml and the pinned pack.yaml.
3. Validate the selected job against job.schema.json.
4. Read only matching records from knowledge.jsonl.
5. Discover current tools and input schemas.
6. Follow workflow.yaml; scope each mutation.
7. Reinspect assets after saving and reloading.
8. Write evidence and result.json.
9. Validate result.json against result.schema.json.
10. Never claim COMPLETE without fresh evidence.

No tool, permission, project state, or success
may be inferred from this document alone.
~~~

`SKILL.md`が読めても、AIへUnityの操作権限が生えるわけではない。入口の発見と、実行できる能力は別問題だ。

## 3. workflow.yaml：止まる・直す・引き継ぐ

ここは標準のエンジンが読み取るものではなく、ホストエージェントが解釈する**独自の状態遷移契約**。したがって、実装側にはこの形式を解釈する処理が必要になる。

~~~yaml
schema_version: 1
name: avatar-task

states:
  discover:
    actions:
      - inspect_job_and_local_repository_rules
      - inspect_live_target_and_available_tools
      - select_relevant_knowledge
    next: plan
    on_missing_capability: blocked

  plan:
    actions:
      - lock_target_identity
      - declare_expected_and_forbidden_changes
      - checkpoint_original_state
    next: mutate
    on_ambiguous_identity: blocked

  mutate:
    actions:
      - apply_one_scoped_change
      - save_and_reload
      - record_diff_and_tool_result
    next: verify
    on_failure: diagnose

  verify:
    actions:
      - independently_reinspect_current_target
      - compare_expected_and_actual_diff
      - run_required_job_acceptance
      - record_fresh_evidence
    on_all_pass: complete
    on_failure: diagnose
    on_unobservable: blocked

  diagnose:
    actions:
      - record_failure_and_attempt
      - find_evidence_based_alternative
      - rollback_if_needed
    on_safe_remedy: mutate
    on_no_remedy: blocked

terminal: [complete, blocked, failed]

invariants:
  - never_modify_vendor_original
  - never_use_name_alone_as_asset_identity
  - do_not_repeat_failed_action_without_new_evidence
  - old_evidence_does_not_validate_new_mutations
  - no_external_publication_without_user_action
~~~

重要なのは「AIなら修復できる」と想定することではなく、**修復する根拠が見つからなかったときの停止条件**を持つことだ。

## 4. knowledge.jsonl：知識をルールと観測に分離する

1行1件のJSON。例は架空のテストフィクスチャであり、特定の購入アセットや非公開リポジトリの情報ではない。

~~~jsonl
{"id":"native-outfit-first","kind":"design_rule","status":"PROPOSED","scope":"outfit_fit","condition":"source_character == target_character","action":"Prefer the native target prefab before cross-character retargeting.","evidence_url":"https://example.com/replace-with-public-source"}
{"id":"ambiguous-bone-map","kind":"failure_pattern","status":"HYPOTHESIS","scope":"rig_retarget","condition":"left_right_bone_mapping_ambiguous","action":"BLOCKED until live bone identity and poses are independently verified.","evidence_url":"https://example.com/replace-with-public-source"}
~~~

実際に運用するときは、`evidence_url`を本物の公開一次資料やコミットへ置き換える。出典未確認の行は`VERIFIED`へ昇格しない。

ここを自由作文の「長期記憶」にすると、古い誤りまで共有される。少なくとも`status`、`condition`、`action`、`evidence_url`を持ち、現在の対象に当てはまるものだけを選択する。

## 5. job.schema.jsonと依頼JSON：仕事の契約

「服をいい感じに着せる」だけでは、エージェント間で完了条件を共有できない。

入力の最小契約をJSON Schemaで定義する。

~~~json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "job_id", "target", "changes", "acceptance", "publication"],
  "properties": {
    "schema_version": {"const": 1},
    "job_id": {"type": "string", "minLength": 3},
    "target": {
      "type": "object",
      "additionalProperties": false,
      "required": ["asset_path", "asset_guid"],
      "properties": {
        "asset_path": {"type": "string", "minLength": 1},
        "asset_guid": {"type": "string", "pattern": "^[0-9a-f]{32}$"}
      }
    },
    "changes": {
      "type": "array",
      "minItems": 1,
      "items": {"type": "string", "minLength": 5}
    },
    "acceptance": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "expected"],
        "properties": {
          "id": {"type": "string", "minLength": 2},
          "expected": {"type": "string", "minLength": 5}
        }
      }
    },
    "publication": {"enum": ["none", "manual_only"]}
  }
}
~~~

例えば、実行前に対象GUIDを検査できないなら実装へ進まない。次のJSONのGUIDは**例示用で、実アセットのGUIDではない**。

~~~json
{
  "schema_version": 1,
  "job_id": "sample-outfit-reference-repair",
  "target": {
    "asset_path": "Assets/Example/DerivedAvatar.prefab",
    "asset_guid": "11111111111111111111111111111111"
  },
  "changes": [
    "Repair missing references in the derived avatar only."
  ],
  "acceptance": [
    {
      "id": "reference-audit",
      "expected": "Fresh reference audit has no unexpected missing entries."
    },
    {
      "id": "visual-review",
      "expected": "Saved multi-view comparison shows no new visible defect."
    }
  ],
  "publication": "none"
}
~~~

JSON Schemaが証明するのは**依頼の形**であって、「その変更で見た目がよくなること」ではない。

## 6. result.schema.json：完了の形式

「終わりました」は文字列としては簡単だが、後任エージェントはどこまで実行されたかを復元できない。

~~~json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "job_id", "pack_revision", "status", "checks", "changes", "next_action"],
  "properties": {
    "schema_version": {"const": 1},
    "job_id": {"type": "string", "minLength": 3},
    "pack_revision": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
    "status": {"enum": ["COMPLETE", "BLOCKED", "FAILED", "UNVERIFIED"]},
    "checks": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "status", "evidence"],
        "properties": {
          "id": {"type": "string", "minLength": 2},
          "status": {"enum": ["PASS", "FAIL", "BLOCKED", "UNVERIFIED"]},
          "evidence": {
            "type": "array",
            "items": {"type": "string", "minLength": 1}
          }
        },
        "allOf": [{
          "if": {"properties": {"status": {"const": "PASS"}}, "required": ["status"]},
          "then": {"properties": {"evidence": {"minItems": 1}}}
        }]
      }
    },
    "changes": {"type": "array", "items": {"type": "string"}},
    "next_action": {"type": ["string", "null"]}
  },
  "allOf": [{
    "if": {"properties": {"status": {"const": "COMPLETE"}}, "required": ["status"]},
    "then": {
      "properties": {
        "checks": {"items": {"properties": {"status": {"const": "PASS"}}}}
      }
    }
  }]
}
~~~

「すべてPASS」を要求するだけでは不十分だ。`checks`に依頼側のすべての`acceptance.id`が一意に含まれるかは、入力・結果を並べた検証スクリプトで比較する。存在しないチェックを省いたまま`COMPLETE`とする抜け道を塞ぐ。

## 7. adapters/unity-mcp.yaml：実ツールの名前を仮定しない

~~~yaml
schema_version: 1
id: unity-capability-resolver

discovery:
  protocol: mcp
  method: tools/list
  inspect_input_schema: true
  follow_pagination: true

capabilities:
  asset.identity.inspect:
    requires:
      - inspect_live_scene
      - inspect_prefab_references

  unity.editor.mutate:
    requires:
      - update_scoped_asset
      - save_and_reload

  visual.compare:
    optional: true
    requires:
      - capture_target_views
      - compare_before_after

resolution:
  - map_required_operation_to_real_tool
  - validate_arguments_against_live_input_schema
  - if_ambiguous_or_absent_mark_blocked
~~~

ここでも`inspect_live_scene`などは**欲しい操作の意味**であって、実際に存在すると確認したMCPツール名ではない。ツールの発見・対応付け・呼び出しはAIホスト側が行う必要がある。

## 8. scripts/validate.py：最小限の独立チェック

検証は新しい巨大なCIではなく、まず既存のJSON Schemaライブラリで行う。以下はJobとResultの**構造・チェック集合・完了状態**を照合する最小例で、Unityの実物検査は含まない。

~~~python
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

root = Path(__file__).resolve().parents[1]
job_path = Path(sys.argv[1])
result_path = Path(sys.argv[2])

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def check(schema_name, data):
    schema = load(root / "schemas" / schema_name)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(
        schema,
        format_checker=FormatChecker()
    ).validate(data)

job = load(job_path)
result = load(result_path)

check("job.schema.json", job)
check("result.schema.json", result)

assert job["job_id"] == result["job_id"]

expected = [x["id"] for x in job["acceptance"]]
observed = [x["id"] for x in result["checks"]]
assert len(expected) == len(set(expected))
assert len(observed) == len(set(observed))
assert set(expected) == set(observed)

if result["status"] == "COMPLETE":
    assert all(x["status"] == "PASS" for x in result["checks"])
    assert all(x["evidence"] for x in result["checks"])

print("contract valid")
~~~

実運用ではさらに、Git submoduleのGitlink SHAと`pack_revision`の一致、証拠パスのリポジトリ外脱出禁止、ファイルのSHA-256、タイムスタンプ、変更後の再検証などが必要だ。**上のスクリプトだけで完全性を証明したとは言わない。**

## 利用側リポジトリはできるだけ薄くする

~~~yaml
# .agent-pack.yaml
schema_version: 1
pack:
  id: kafka.avatar-modification
  path: .agent-packs/avatar
jobs: .agent-jobs
results: .agent-runs
~~~

~~~markdown
# AGENTS.md への追記例

For avatar work, read .agent-pack.yaml and the
pinned skills/avatar-modification/SKILL.md.

Follow existing repository instructions.
Never assume a tool or permission is available.
Validate the job and record evidence before
claiming completion.
~~~

Claude CodeやGemini CLIが`AGENTS.md`を自動発見するかは、その製品と設定で異なる。必要なら既存の`CLAUDE.md`・`GEMINI.md`から同じSkillを指す。各ファイルへ長い規則をコピーしない。

~~~bash
# 共有リポジトリを作成済みの場合の導入例
git submodule add \
  https://github.com/OWNER/avatar-agent-pack.git \
  .agent-packs/avatar

# 他の環境で取得するとき
git submodule update --init --recursive
~~~

URL中の`OWNER/avatar-agent-pack`はプレースホルダー。実在する配布先として断言していない。親リポジトリがsubmoduleの特定コミットを記録するため、利用側で版を個別に更新できる。

## 他のエージェントへ渡す結果は何か

~~~json
{
  "schema_version": 1,
  "job_id": "sample-outfit-reference-repair",
  "pack_revision": "0000000000000000000000000000000000000000",
  "status": "BLOCKED",
  "checks": [
    {"id": "reference-audit", "status": "BLOCKED", "evidence": []},
    {"id": "visual-review", "status": "UNVERIFIED", "evidence": []}
  ],
  "changes": [],
  "next_action": "Connect a supported Unity inspection tool and inspect the actual target."
}
~~~

これは`BLOCKED`形式の**ダミー例**であり、実行結果ではない。`pack_revision`は本番では実際のGitコミットSHAへ置き換える。

引き継ぐ側が必要とするのは、前任AIの長い自己説明より、対象、現在の変更、合格条件、証拠、未完了の理由だ。イベントログ（`events.jsonl`）には、呼び出した実ツール名・結果・証拠への参照を残す。ただし秘密情報や非公開アセット自体を公開リポジトリへ置かない。

## これで解決する問題と、解決しない問題

| 問題 | この設計が助ける部分 | 未解決・別途必要な部分 |
| --- | --- | --- |
| AIを乗り換えると説明を繰り返す | 同じSkillとJobを参照する | すべてのAIが自動でSkillを発見するわけではない |
| リポジトリ間で規則がずれる | GitコミットでPackを固定する | 各リポジトリ固有の規則の優先順位 |
| 「完了」の意味が違う | Schemaと合格条件を共有する | 実ツールによる独立の観測 |
| ツール名が環境ごとに違う | MCPの実ツールを発見する | そのツールが必要な操作を本当に提供すること |
| 作業中断で失敗理由を忘れる | Resultとイベントログを保存する | 実行エンジン、継続起動、チェックポイント復旧 |
| AIが「視覚確認済み」と誤報する | 証拠がなければ`COMPLETE`を拒否する | 画像そのものの品質判定と実機検証 |

画像を見ないで「見た目PASS」と答えるAIも、別AIへ渡しただけでは賢くならない。この点は、[Unity MCPと視覚・動作検証の既存調査](https://github.com/KAFKA2306/articles/blob/main/articles/unity-mcp-editor-boundary.md)で扱った問題と連続している。

今回追加したい価値は監査方法そのものではなく、**その監査の必要条件を別AIへ引き継げる形式**である。

## 別プロジェクトへ移せる判断

この設計はUnity固有の方法ではない。例えばデータパイプライン、3D制作、Webアプリ修復でも、同じ分離を試せる。

~~~text
repository-local rules
      ↓
shared domain skill
      ↓
typed job + acceptance
      ↓
live capability discovery
      ↓
scoped execution
      ↓
evidence + typed result
~~~

ただし次の条件でだけ移植を検討する。

1. 共有したい**専門知識**が本当に複数プロジェクトで再利用できる。
2. 実行主体が変わっても**合格条件**は同じ意味を持つ。
3. 実際に操作できるツールを**実行時に検出**できる。
4. 実行結果を別主体が**独立に再確認**できる。
5. パッケージの維持費が、重複指示の修正費より低い。

逆に、一度きりの作業、リポジトリごとに権限や合格条件が根本的に違う仕事、必要な実ツールが存在しない環境には、共通Packを導入しても自律化できない。

### 実装前に行う比較実験

同じ依頼を、同じアセット・同じ検証手段で次の3条件に分ける。

| 条件 | 渡すもの | 比較するもの |
| --- | --- | --- |
| A | 自然言語の依頼のみ | 説明の追加回数、作業の漏れ |
| B | ローカルAGENTS.md＋Skill | 同じ漏れと修正回数 |
| C | 固定版Pack＋Schema＋証拠付きResult | 同じ漏れと修正回数、別AIへの引き継ぎ可否 |

見るべき数字はファイル数ではない。**合格条件の取りこぼし、根拠のない完了報告、実際の修復時間、共通Packの維持費**である。

この比較はまだ実施していない。したがってCが優れているとは結論づけない。

## 結論

AI同士で共有すべきなのは、長い人格設定でも、全リポジトリを支配する巨大な設定でもない。

- **何を頼まれたか**：Job
- **何を知っておくべきか**：必要なSkillと根拠付き知識
- **何を実際に操作できるか**：接続時点のツール一覧
- **何をもって完了とするか**：Acceptanceと証拠
- **どこから再開するか**：Resultとイベントログ

最小の形で再開できるなら、そこから先は増やさない。複数AIでどうしても同じ判断を渡す必要が出たときだけ、その判断を共通Packへ昇格させる。

**次のAIが前のAIを信じる必要はない。同じ契約と実物を読めば、仕事を再開できる。** これが検証したい設計仮説だ。

---

調査・設計日：2026年11月9日。対象は公開仕様と公開済みの開発記録。共有Packそのものの実装、異種エージェント比較、Unity実機での効果測定は未実施。