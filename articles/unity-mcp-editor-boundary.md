---
title: "AIがUnityを操作できた。それで『完成』にしていい？ MCP自動化で増える偽の成功"
emoji: "🛠️"
type: "tech"
topics: ["unity", "mcp", "codex", "vrchat", "ai"]
published: false
published_at: 2026-08-12 16:03
---

# AIがUnityを操作できた。それで「完成」にしていい？ MCP自動化で増える偽の成功

AIからUnity Editorを操作できるようになると、成功条件を間違えやすくなります。

```text
MCP tool call returned success
```

は、

```text
Unity成果物が正しい
```

ことを意味しません。

さらにVRChat向けなら、Editor上で正しく見えたことと、build後・実機runtimeで正しいことも別です。

この記事ではsetup方法ではなく、この**3段階のcompletion boundary**だけを扱います。

## 3種類の「成功」を分ける

最低限、次を別stateとして保存します。

```text
TOOL_SUCCESS
    ↓
EDITOR_VALIDATED
    ↓
RUNTIME_COMPLETED
```

### TOOL_SUCCESS

MCP clientからUnityへ命令を送り、tool responseが成功した状態です。

例えば、

```text
GameObjectを作成した
Componentを変更した
scriptを編集した
Test toolを呼んだ
```

という操作完了です。

CoplayDevのMCP for Unityは、LLMからUnity Editorへ接続し、Scene、GameObject、script、asset、test、build等を操作するbridgeとして公開されています。

一次情報:
https://github.com/CoplayDev/unity-mcp

しかし、操作可能であることは、その操作内容が目的に対して正しかった証拠ではありません。

### EDITOR_VALIDATED

Unity Editor側の状態を読み直し、意図した変更が成立したことを確認した状態です。

```text
tool response = success
AND
対象objectが存在
AND
期待componentが存在
AND
referenceが解決
AND
Unity側のvalidationを通過
```

ここでは「AIがそう報告した」だけでは足りません。Editor stateを別の観測で確認します。

### RUNTIME_COMPLETED

実際の成果物として必要な最終gateを通った状態です。

VRChatアバターなら、projectごとのcontractに応じて、例えばbuild、upload、実機確認などがここに入ります。

```text
Editor validation passed
!=
runtime completion passed
```

この境界を残すことが中心です。

## なぜMCP導入で偽の成功が増えるのか

人間がUnityを手作業で触る場合、操作後にSceneやGame Viewを自然に見直します。

AI toolでは、

```text
tool call
→ success response
```

だけで一つのtaskが完了したように見えます。

そのためagent側のcompletion contractを明示しないと、

```text
Componentを追加できた
→ 修正完了
```

という飛躍が起きます。

実際には、

```text
Componentを追加できた
→ referenceは正しいか
→ build processing後も残るか
→ runtimeで期待通りか
```

まで別々に確認する必要があります。

## `image2outfit` のPRは、ここを意図的にNOT_RUNとしている

`KAFKA2306/image2outfit` のDraft PR #212は、local Blender + Unity MCP supportを追加しています。

しかしPR本文では、2026年8月13日時点でも次を明示的に `NOT_RUN` としています。

- user Windows環境でのPowerShell setup
- live Blender MCP connection
- live Unity MCP connection / package resolution
- Blender Assistant → Codex → MCP end-to-end call

PR:
https://github.com/KAFKA2306/image2outfit/pull/212

また同PRは、MCP integrationをoptional local authoring supportとし、既存の`requiredCompletionGates`を変更しないと明記しています。

つまり、この実装から言えるのは、

```text
MCP integration code exists
static contract exists
```

までです。

**live Unity MCP E2Eが成功した、VRChat成果物が完成した、とはまだ言えません。**

この記事も、その境界に合わせて非公開のままにします。

## MCPはcompletion gateではなくauthoring adapterにする

構造は次のようにします。

```text
Codex / MCP client
        ↓
MCP for Unity
        ↓
Unity Editor
        ↓
existing validation
        ↓
existing build / runtime gates
```

MCPを入れたことで、既存のcompletion gateを短絡しません。

これはMCPが信用できないという意味ではありません。

**操作チャネルと検証チャネルの責務が違う**という話です。

## 壊れた例

```text
Agent: Materialを変更しました
Tool: success
Task: completed
```

ここではMaterial referenceが本当に変わったか、build processorが上書きしないか、VR runtimeで意図通りかが未確認です。

## 改善後

```text
1. MCP toolを実行
2. Editor stateを再取得
3. 期待値と比較
4. build / testを実行
5. runtime evidenceを取得
6. すべて通った場合だけcompleted
```

例えばtask resultを次のように構造化できます。

```json
{
  "tool_success": true,
  "editor_validated": true,
  "runtime_completed": false,
  "runtime_reason": "NOT_RUN"
}
```

この場合、task全体をsuccessとは呼びません。

## setup詳細を記事から外す

MCP serverのinstall方法、transport、port、version pin、doctor commandは変更され得る運用情報です。

MCP for Unityの現行READMEでは、Unity EditorをLLMから操作するbridgeとして、asset管理、Scene操作、script編集、test、build等が案内されています。

- https://github.com/CoplayDev/unity-mcp

具体的なsetupはupstream docsとproject側docsへ委ね、この記事では固定しません。

これにより、記事の主張をversion依存の導入手順から切り離せます。

## 再利用できるcompletion contract

GUI applicationをAI agentへ渡す場合は、次のようなcontractへできます。

```yaml
completion:
  tool_success:
    required: true
  editor_validation:
    required: true
  runtime_validation:
    required: true
```

runtime validationが実行できない環境なら、

```yaml
runtime_validation:
  status: NOT_RUN
```

としてtaskを未完了にします。

`NOT_RUN`を`PASS`へ変換しないことが重要です。

## まとめ

MCP for UnityによってAIがEditorを操作できる範囲は広がります。

しかし、自動化で本当に重要なのはtoolの数ではありません。

```text
操作できた
正しく変更できた
成果物として完成した
```

を別々に証明することです。

AIがUnityを操作できた。それは有用な中間成功です。

**でも、それだけでは「完成」ではありません。**

## 一次情報・実装証拠

- MCP for Unity: https://github.com/CoplayDev/unity-mcp
- image2outfit Draft PR #212: https://github.com/KAFKA2306/image2outfit/pull/212
