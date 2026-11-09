---
title: "AIエージェントを替えても作業を引き継げるか"
emoji: "🔗"
type: "tech"
topics: ["ai", "mcp", "github", "unity", "automation"]
published: false
---

AIエージェントを乗り換えたり、別のリポジトリで同じ作業を委任したりするとき、説明文をコピーするだけでは引き継げないものがある。

「何を変えるべきか」は伝わっても、「どの実物を変えるか」「今のツールでできるか」「何を見て完成と判断するか」が欠けやすい。

実際、私の[Unityアバター改変リポジトリ](https://github.com/KAFKA2306/avatars2509)では、異なるアバター向けの衣装をリターゲットしたとき、数値だけでは作業を成功にできなかった。2026年10月9日の記録では、Milltina向け衣装をRuruneへ変換した際、互換性評価21.4%、不一致の骨173本、左右の骨の誤対応、見た目の破綻が残った。[当時の手順・観測記録](https://github.com/KAFKA2306/avatars2509/blob/main/Docs/MOCHIFITTER.md)

この経験を別のAIにも伝えたい。しかし「Ruruneでは気を付ける」とだけ書いても、別キャラクター、別バージョン、別のMCPツールでは使いにくい。

そこで考えたのは、**説明文の共有ではなく、作業を実行・停止・再検証するための情報を、別々の機械可読ファイルとして共有する**方式だ。

本記事はその**実装設計とコピー可能なファイル例**をまとめたもの。共有パッケージをUnity実機で横断運用できたという報告ではない。成功を実証していない部分は最後に分ける。

## 何を共有し、何を共有しないか

任意のAIへ渡したいものは4種類ある。

| 情報 | 中身 | 共有先 |
| --- | --- | --- |
| 入口 | どの作業で何を読むか | AGENTS.md / Agent Skills |
| 専門知識 | 固有の失敗、対象の同定方法、根拠 | JSONL |
| 作業契約 | 入力、許容変更、完了条件、出力 | YAML / JSON Schema |
| 実行環境 | 実際に使用できるMCPツールと権限 | 各エージェントの接続先 |

最も重要なのは最後の違いだ。**共通ファイルに「Unityを操作する」と書いても、Unity MCPが接続されるわけではない**。MCPではツールの一覧と入力スキーマを取得できるが、そのツールが接続されているか、変更権限があるかは実行環境で確認しなければならない。[MCP Tools仕様](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)

既存の共通仕様を優先して使う。

- [AGENTS.md](https://agents.md/)：リポジトリ内のエージェント向け説明の入口
- [Agent Skills](https://agentskills.io/specification)：`SKILL.md`に名前・説明・必要時に読む手順を置く形式
- [MCP Tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)：ツールの発見・呼び出しと入力スキーマ
- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/)：作業依頼・結果の構造検証
- [Git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules)：共有ファイルを利用側コミットに固定する方法

ここから先の`pack.yaml`、`workflow.yaml`、`knowledge.jsonl`などは**この記事で提案する独自ファイル**であり、公式標準ではない。

## なぜ各リポジトリへコピーしないのか

| 選択肢 | 利点 | 不利な点 |
| --- | --- | --- |
| 各リポジトリへコピー | ローカルで完結 | 同じ修正が分散し、古い規則が残る |
| 大きなAGENTS.md一つ | 読み込みが単純 | 固有の失敗と一般規則が混ざり、毎回長い |
| 共有Skillsを最新版参照 | 更新が楽 | 同じJobでも取得時点で動作が変わる |
| **共有Skillsをコミット固定** | 同じ知識版を後から再取得できる | 初期化と更新に明示的な操作が必要 |

私はGit submoduleでコミットを固定する案を選ぶ。更新は利用側リポジトリのPRで差分として確認する。

ただし、submoduleが全AIで自動ロードされるわけではない。ホスト側に入口の読込手順が必要だ。

## 具体的なディレクトリ

```text
kafka-avatar-agent-pack/
├── pack.yaml
├── workflow.yaml
├── knowledge.jsonl
├── skills/avatar-agent/SKILL.md
├── schemas/job.schema.json
├── schemas/result.schema.json
├── adapters/unity-mcp.yaml
└── scripts/validate.py

任意の利用側リポジトリ/
├── .gitmodules
├── .agent-packs/avatar/         # Git submodule
├── .agent-pack.yaml
├── AGENTS.md
├── CLAUDE.md                    # 必要な場合のみ
├── GEMINI.md                    # 必要な場合のみ
├── .agent-jobs/outfit.json
└── .agent-runs/                 # Git管理しない実行証拠
```

前半の8ファイルが共有資産で、後半は利用側の設定と実行時データだ。すでに同名の指示ファイルがある場合は**置き換えずに統合**する。

以下は全ファイルの具体例である。`kafka-avatar-agent-pack`は説明用の**未作成リポジトリ名**であり、GitHub上に存在することを保証しない。

# 共有側の8ファイル

## 1. pack.yaml：共有内容の目録

```yaml
schema_version: 1
id: kafka.avatar-agent
version: 1.0.0
entrypoint: skills/avatar-agent/SKILL.md
workflow: workflow.yaml
knowledge: knowledge.jsonl
contracts:
  job: schemas/job.schema.json
  result: schemas/result.schema.json
adapters:
  - adapters/unity-mcp.yaml
capabilities:
  required:
    - repository.read
    - repository.write
    - unity.inspect
    - unity.save_reload
    - evidence.persist
  conditional:
    - unity.modify
    - blender.modify
    - visual.review
    - vrchat.sdk.build_test
policy:
  protect_vendor_assets: true
  never_guess_object_identity: true
  no_automatic_publication: true
  no_credentials_in_records: true
  treat_missing_evidence_as_unverified: true
```

`repository.read`等はパッケージ内の能力IDであり、実在するMCPツール名ではない。利用環境のツール一覧から毎回解決する。

## 2. workflow.yaml：作業の段階と停止条件

```yaml
schema_version: 1
name: avatar-modification
states:
  - id: discover
    do:
      - read_job_and_local_repository_rules
      - retrieve_relevant_knowledge_with_sources
      - inspect_live_unity_project_and_assets
      - discover_mcp_tools_and_input_schemas
    on_success: plan
    on_missing_input: blocked
  - id: plan
    do:
      - identify_exact_target_guid_and_prefab
      - compare_requested_and_current_state
      - declare_allowed_diff_and_preserved_properties
      - save_rollback_checkpoint
    on_success: mutate
    on_ambiguous_target: blocked
  - id: mutate
    do:
      - perform_one_scoped_change
      - save_and_reload_changed_assets
      - record_exact_tool_outcome_and_diff
    on_success: verify
    on_tool_failure: diagnose
    on_missing_capability: blocked
  - id: verify
    do:
      - independently_reread_live_references
      - compare_requested_vs_observed_diff
      - run_all_applicable_acceptance_checks
      - capture_and_review_visual_evidence_when_required
    on_pass: finalize
    on_failure: diagnose
    on_unobservable: blocked
  - id: diagnose
    do:
      - record_failure_and_reproduction
      - search_related_knowledge
      - select_new_supported_repair_or_rollback
    on_safe_remedy: mutate
    on_no_remedy: blocked
    on_unexpected_damage: failed
  - id: finalize
    do:
      - write_events_jsonl_and_result_json
      - validate_result_schema
      - report_any_remaining_unverified_step
    on_success: complete
terminal: [complete, blocked, failed]
invariants:
  - never_modify_vendor_originals
  - never_select_by_display_name_alone
  - never_report_complete_without_fresh_evidence
  - never_retry_the_same_failure_without_new_evidence
  - never_publish_avatar_automatically
```

**注意：これは宣言ファイルであってワークフローエンジンではない。** Agent Skillsを読んだAIが手順を実行するか、別途オーケストレーターを作る必要がある。

## 3. knowledge.jsonl：実際の失敗を再利用する

```jsonl
{"id":"native-outfit-first","kind":"project_rule","trigger":"source_character equals target_character","decision":"Prefer the native prefab; cross-character fitting is not required.","source":"https://github.com/KAFKA2306/avatars2509/blob/main/Docs/MOCHIFITTER.md"}
{"id":"crossfit-20261009","kind":"historical_failure","trigger":"Milltina clothing to Rurune using RetargetOutfit","observed":{"compatibility":0.214,"unmatched_bones":173,"left_right_mapping_error":true,"visual_result":"FAIL"},"decision":"Do not reuse this mapping without new compatibility and visual verification.","source":"https://github.com/KAFKA2306/avatars2509/blob/main/Docs/MOCHIFITTER.md"}
{"id":"tool-popup-timeout","kind":"historical_failure","trigger":"MochiFitter native dropdown via MCP","decision":"Recheck current version and editor state before repeating the action; do not loop blindly after timeout.","source":"https://github.com/KAFKA2306/avatars2509/blob/main/Docs/MOCHIFITTER.md"}
```

ここで保持するのは「誰にでも言えるUnityの解説」ではなく、**自分のプロジェクトで初めて分かった故障条件と、そこから変更された判断**だ。

履歴の21.4%は特定の衣装・対象・方法・時点の値。別環境の普遍的な成功閾値ではない。記録の根拠を消して「一般ルール」に書き換えてはいけない。

## 4. skills/avatar-agent/SKILL.md：AIの読込入口

```markdown
---
name: avatar-agent
description: Execute scoped Unity and VRChat avatar modifications, including outfit fitting, material edits, reference repairs and verification. Use for avatar modification tasks.
---

Read the consuming repository's .agent-pack.yaml.
Read pack.yaml and workflow.yaml from the pinned checkout.
Validate the selected job with schemas/job.schema.json.
Load only matching knowledge.jsonl entries and inspect their sources.
Discover current MCP tools; never assume custom capability names are callable tools.
Identify assets by GUID, path and live serialized references.
Protect vendor originals and unrelated objects.
Make one scoped change, save and reload, then independently verify it.
Persist events.jsonl and result.json after execution.
Validate the result with scripts/validate.py.
Report COMPLETE only when all required checks have fresh passing evidence.
Otherwise report BLOCKED, FAILED or UNVERIFIED and an exact next action.
Do not upload the user's avatar to VRChat automatically.
```

Agent Skills仕様では`SKILL.md`が必須で、`name`と`description`を持つ。その他のJSON/YAMLは独自契約だ。[Agent Skills仕様](https://agentskills.io/specification)

## 5. schemas/job.schema.json：依頼の入力契約

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version", "job_id", "target",
    "desired_changes", "acceptance", "publication"
  ],
  "properties": {
    "schema_version": {"const": 1},
    "job_id": {
      "type": "string",
      "pattern": "^[a-z0-9][a-z0-9-]{2,80}$"
    },
    "target": {
      "type": "object",
      "additionalProperties": false,
      "required": ["character", "prefab_guid", "prefab_path"],
      "properties": {
        "character": {"type": "string", "minLength": 1},
        "prefab_guid": {"$ref": "#/$defs/guid"},
        "prefab_path": {"type": "string", "pattern": "^Assets/.+\\.prefab$"}
      }
    },
    "desired_changes": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["kind", "goal"],
        "properties": {
          "kind": {
            "enum": [
              "outfit_fit", "material_edit", "rig_retarget",
              "animator_repair", "reference_repair", "sdk_build"
            ]
          },
          "goal": {"type": "string", "minLength": 8}
        }
      }
    },
    "acceptance": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "type", "expected"],
        "properties": {
          "id": {"type": "string", "minLength": 2},
          "type": {
            "enum": [
              "reference_integrity", "material_integrity",
              "visual_review", "pose_review",
              "sdk_build", "property_check"
            ]
          },
          "expected": {"type": "string", "minLength": 3}
        }
      }
    },
    "publication": {"enum": ["none", "manual_only"]}
  },
  "$defs": {
    "guid": {
      "type": "string",
      "pattern": "^[a-f0-9]{32}$"
    }
  }
}
```

**入力の形を検証できることと、GUIDが本当に対象を指すことは別問題。** 後者はUnity Editorの現在の実体を読む必要がある。

## 6. schemas/result.schema.json：引き継ぎの出力契約

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version", "job_id", "pack_revision",
    "status", "checks", "changes", "next_action"
  ],
  "properties": {
    "schema_version": {"const": 1},
    "job_id": {"type": "string", "minLength": 3},
    "pack_revision": {
      "type": "string", "pattern": "^[a-f0-9]{40}$"
    },
    "status": {
      "enum": ["COMPLETE", "BLOCKED", "FAILED", "UNVERIFIED"]
    },
    "checks": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "status", "method", "evidence"],
        "properties": {
          "id": {"type": "string"},
          "status": {
            "enum": ["PASS", "FAIL", "BLOCKED", "UNVERIFIED"]
          },
          "method": {"type": "string"},
          "evidence": {
            "type": "array",
            "items": {"type": "string"}
          }
        }
      }
    },
    "changes": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["path", "operation"],
        "properties": {
          "path": {"type": "string"},
          "operation": {
            "enum": ["created", "modified", "deleted"]
          }
        }
      }
    },
    "next_action": {"type": ["string", "null"]}
  }
}
```

`PASS`には証拠へのパスを残す。`COMPLETE`は全部の必須チェックがPASSした場合だけにする。入力された`status`を信じるのではなく、validatorが整合性を確認する。

## 7. adapters/unity-mcp.yaml：ツール能力の要求

```yaml
schema_version: 1
id: unity-mcp
discovery:
  method: mcp_tools_list
  paginate: true
  inspect_input_schema: true
  prohibit_assumed_tool_names: true
capabilities:
  unity.inspect:
    required_evidence: live_scene_and_prefab_identity
    operations:
      - list_scenes
      - list_avatar_roots
      - inspect_references
  unity.modify:
    required_evidence: recorded_changes
    operations:
      - edit_prefab
      - configure_material
      - repair_reference
  unity.save_reload:
    required_evidence: fresh_object_identity
    operations:
      - save_assets
      - reload_assets
      - reread_references
  visual.review:
    optional: true
    required_evidence: timestamped_images_and_verdict
    operations:
      - capture_four_views
      - inspect_pose_deformation
  vrchat.sdk.build_test:
    optional: true
    required_evidence: current_build_log
    operations:
      - sdk_validation
      - build_and_test
on_unresolved_required_capability: BLOCKED
forbidden:
  - guess_tool_arguments
  - bypass_host_permissions
  - modify_vendor_originals
  - report_unobserved_visual_success
  - automatically_publish_avatar
```

ここにある`list_scenes`や`edit_prefab`も**抽象操作名**だ。実際のMCPツール名への対応は実行時に確認する。MCPの`tools/list`で実在する名前と`inputSchema`を取得する。[MCP Tools仕様](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)

## 8. scripts/validate.py：最小の機械検証

```python
#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def safe_path(root, rel):
    root = root.resolve()
    path = (root / rel).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"path escapes repository: {rel}")
    return path


def check_schema(path, value):
    schema = read_json(path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(
        schema, format_checker=FormatChecker()
    )
    errors = sorted(
        validator.iter_errors(value),
        key=lambda e: str(list(e.absolute_path))
    )
    if errors:
        raise ValueError("; ".join(e.message for e in errors))


def verify_pack_revision(repo, pack_rel, pack_dir):
    entries = subprocess.check_output(
        ["git", "-C", str(repo), "ls-files", "--stage", "--", pack_rel],
        text=True,
    ).splitlines()
    if len(entries) != 1:
        raise ValueError("pack must be a tracked Git submodule")
    meta, tracked_path = entries[0].split("\t", 1)
    mode, expected_sha, stage = meta.split()
    if (mode, stage, tracked_path) != ("160000", "0", pack_rel):
        raise ValueError("pack is not a Git submodule")
    actual_sha = subprocess.check_output(
        ["git", "-C", str(pack_dir), "rev-parse", "HEAD"],
        text=True,
    ).strip()
    if actual_sha != expected_sha:
        raise ValueError("pack checkout differs from indexed gitlink")
    return actual_sha


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True, type=Path)
    p.add_argument("--job", required=True)
    p.add_argument("--result")
    args = p.parse_args()
    repo = args.repo.resolve()
    install = yaml.safe_load(
        (repo / ".agent-pack.yaml").read_text(encoding="utf-8")
    )
    pack_rel = install["pack"]["path"]
    pack_dir = safe_path(repo, pack_rel)
    manifest = yaml.safe_load(
        (pack_dir / "pack.yaml").read_text(encoding="utf-8")
    )
    if manifest["id"] != install["pack"]["id"]:
        raise ValueError("pack id mismatch")
    revision = verify_pack_revision(repo, pack_rel, pack_dir)

    for key in ("entrypoint", "workflow", "knowledge"):
        if not safe_path(pack_dir, manifest[key]).is_file():
            raise ValueError(f"missing pack file: {manifest[key]}")

    knowledge_ids = set()
    for line in (pack_dir / manifest["knowledge"]).read_text(
        encoding="utf-8"
    ).splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if (
            record.get("id") in knowledge_ids
            or not record.get("id")
            or not record.get("source")
        ):
            raise ValueError("invalid/duplicate knowledge record")
        knowledge_ids.add(record["id"])

    job = read_json(safe_path(repo, args.job))
    check_schema(
        pack_dir / manifest["contracts"]["job"], job
    )
    job_ids = [x["id"] for x in job["acceptance"]]
    if len(job_ids) != len(set(job_ids)):
        raise ValueError("duplicate acceptance id")

    if args.result:
        result = read_json(safe_path(repo, args.result))
        check_schema(
            pack_dir / manifest["contracts"]["result"], result
        )
        if result["job_id"] != job["job_id"]:
            raise ValueError("wrong result job")
        if result["pack_revision"] != revision:
            raise ValueError("wrong result pack SHA")
        checks = result["checks"]
        if set(x["id"] for x in checks) != set(job_ids):
            raise ValueError("acceptance/result checks differ")
        if len(checks) != len(job_ids):
            raise ValueError("duplicate result checks")
        for check in checks:
            for item in check["evidence"]:
                if not safe_path(repo, item).is_file():
                    raise ValueError(f"missing evidence: {item}")
            if check["status"] == "PASS" and not check["evidence"]:
                raise ValueError("PASS without evidence")
        all_pass = all(x["status"] == "PASS" for x in checks)
        if (result["status"] == "COMPLETE") != all_pass:
            raise ValueError("invalid COMPLETE status")

    print(json.dumps({
        "valid": True,
        "pack_revision": revision,
        "job_id": job["job_id"],
        "result_checked": bool(args.result)
    }))


if __name__ == "__main__":
    main()
```

この検証器は入力・出力の構造、コミット固定、`PASS`と証拠ファイル存在の整合性を見る。**画像を見て正しさを判定するプログラムではない**。証拠の改ざん検出や鮮度の確認も、この短いサンプルには未実装だ。実運用では証拠のSHA-256、観測日時、対象GUIDと最後の変更後の再測定を追加する。

# 利用側リポジトリのファイル

## 9. .agent-pack.yaml

```yaml
schema_version: 1
pack:
  id: kafka.avatar-agent
  path: .agent-packs/avatar
job_dir: .agent-jobs
evidence_dir: .agent-runs
project:
  repository: https://github.com/KAFKA2306/avatars2509
  unity_project_env: AVATAR_UNITY_PROJECT
permissions:
  protect_vendor_assets: true
  publication: manual_only
```

## 10. AGENTS.md

```markdown
For Unity/VRChat avatar tasks:
1. Read .agent-pack.yaml.
2. Initialize the pinned .agent-packs/avatar Git submodule.
3. Read .agent-packs/avatar/skills/avatar-agent/SKILL.md.
4. Validate the selected .agent-jobs/*.json file.
5. Discover available tools and respect host permissions.
6. Persist evidence and verify all required acceptance checks.
7. Never infer COMPLETE from a successful tool call alone.
8. Never upload an avatar on behalf of the user.
```

既存の`AGENTS.md`を消さず、この入口だけ追加する。

## 11. CLAUDE.mdと12. GEMINI.md

各AIの入口は重複した詳細仕様ではなく、同じSkillへの参照に留める。

```markdown
Read AGENTS.md and .agent-packs/avatar/skills/avatar-agent/SKILL.md
for avatar-related work. Do not override repository rules or host permissions.
```

上記の同じ2行を、必要なエージェントの文脈ファイルに追加する。各製品の自動発見対象ディレクトリ・命名・設定の詳細は製品ごとに異なるので、上記だけで全製品への対応を保証しない。

## 13. .agent-jobs/outfit.json

対象GUIDは**動作説明用の架空値**。実行前にUnity Editorで調べた本物の値へ置き換える。

```json
{
  "schema_version": 1,
  "job_id": "rurune-outfit-reference-repair",
  "target": {
    "character": "rurune",
    "prefab_guid": "00000000000000000000000000000000",
    "prefab_path": "Assets/Example/ModifiedAvatar.prefab"
  },
  "desired_changes": [
    {
      "kind": "reference_repair",
      "goal": "Repair missing material references without changing vendor originals."
    }
  ],
  "acceptance": [
    {
      "id": "reference-audit",
      "type": "reference_integrity",
      "expected": "Every required reference resolves after reload."
    },
    {
      "id": "visual-review",
      "type": "visual_review",
      "expected": "Four views show no new material or geometry defect."
    }
  ],
  "publication": "none"
}
```

## 14. .gitignoreと.gitmodules

```gitignore
.agent-runs/
```

利用側で共有リポジトリが作成された後に実行する。

```bash
git submodule add \
  https://github.com/KAFKA2306/kafka-avatar-agent-pack.git \
  .agent-packs/avatar

# submoduleを検証済みコミットへ移動してから
# 親リポジトリへgitlinkを記録する
git add .gitmodules .agent-packs/avatar
```

`kafka-avatar-agent-pack`は未作成の名前。ここに示した`git submodule add`を現時点で実行すれば取得に失敗する。架空のコミットSHAで固定したふりをしてはいけない。

## 15. 実行結果：.agent-runs/<run-id>/result.json

次は接続できなかった**例示結果**であり、実行証拠ではない。

```json
{
  "schema_version": 1,
  "job_id": "rurune-outfit-reference-repair",
  "pack_revision": "0000000000000000000000000000000000000000",
  "status": "BLOCKED",
  "checks": [
    {
      "id": "reference-audit",
      "status": "BLOCKED",
      "method": "Unity editor connection missing",
      "evidence": []
    },
    {
      "id": "visual-review",
      "status": "UNVERIFIED",
      "method": "not executed",
      "evidence": []
    }
  ],
  "changes": [],
  "next_action": "Connect the correct Unity project, resolve the real GUID, then rerun the audit."
}
```

実際の`pack_revision`にはGit submoduleの正しいSHAを記録する。ツール呼び出し履歴と証拠への参照は同じ実行ディレクトリの`events.jsonl`へ残す。購入アセットの本体・認証情報・個人情報は公開リポジトリに入れない。

## 検証のしかた

共通リポジトリを実際に作成して固定した場合、次を利用できる。

```bash
git submodule update --init --recursive

uv run --with PyYAML --with jsonschema \
  .agent-packs/avatar/scripts/validate.py \
  --repo . \
  --job .agent-jobs/outfit.json

# 実行結果が生成された後だけ追加
uv run --with PyYAML --with jsonschema \
  .agent-packs/avatar/scripts/validate.py \
  --repo . \
  --job .agent-jobs/outfit.json \
  --result .agent-runs/example/result.json
```

`uv`、Python、Gitは利用環境に用意する。上記のコマンドは、まだ共有リポジトリが存在しない現時点での成功実績を意味しない。

## 他のプロジェクトに移せる判断規則

Unity以外でも、AIが外部の実物を変更するなら同じ形を使える。例えばデータベース移行、3D制作、記事制作、インフラ変更では、対象・変更範囲・利用可能な操作・完成の証拠を分ける。

導入判断はこの順番にする。

1. **対象を一意に特定できるか**：名前の曖昧一致だけなら実行しない。
2. **現在使える能力を確認できるか**：Skillに書いてあるだけなら実行しない。
3. **要求された差分を定義できるか**：保護対象と許容変更を先に決める。
4. **変更後の実物を読み直せるか**：ツールの成功応答だけでは完成にしない。
5. **別エージェントが同じ証拠を確認できるか**：結果を構造化して残す。
6. **共有仕様をバージョン固定できるか**：同じ依頼を後で再検証できるようにする。

実行環境が完全に閉じていてファイルを共有できない場合、Git submoduleは使えない。逆に、作業内容が数行の静的な手順にすぎず、対象と完了条件が明確なら、これだけのファイル分割は過剰だ。まず短い`AGENTS.md`と`SKILL.md`だけで十分なこともある。

**増やすべきなのは説明書ではなく、別のAIが誤った対象を変更しないために必要な情報だけだ。**

## 今回の証拠と未実証範囲

**確認できたこと**

- Agent Skillsは`SKILL.md`を標準入口として定義している。[公式仕様](https://agentskills.io/specification)
- AGENTS.mdはリポジトリにAI向け指示を置く公開形式である。[公式サイト](https://agents.md/)
- MCPは`tools/list`で現在のツール定義・入力スキーマを取得できる。[公式仕様](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
- Unityアバター改変で、低互換性と左右骨の誤対応、見た目の失敗が記録されている。[公開プロジェクト記録](https://github.com/KAFKA2306/avatars2509/blob/main/Docs/MOCHIFITTER.md)

**まだ証明していないこと**

- 上記の共通Packを作成・配布して、複数のAIで同じ成果を得られたか。
- Unity MCP接続の違いをすべて吸収できるか。
- 検証用スクリプトだけで画像・アニメーション・実機動作の正しさを保証できるか。
- 認証や実行権限を越えて異なるAI間で仕事を自動委譲できるか。

つまり、これは**実プロジェクトで見えた引き継ぎ問題から導いた、検証可能な設計案**である。仕様ファイルを作ったこと自体を実運用の成功とは数えない。

既存の[Unity MCP実用性記事](https://github.com/KAFKA2306/articles/blob/main/articles/unity-mcp-editor-boundary.md)は「AIが作ったものをどこまで監査できるか」を扱う。本記事の主題は、**その監査を含む作業契約を、別のAIやリポジトリへどう引き継ぐか**だ。