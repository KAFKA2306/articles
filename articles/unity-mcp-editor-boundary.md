---
title: "AIがUnityを操作できても、VRChatアバターが完成したことにはならない"
emoji: "🛠️"
type: "tech"
topics: ["unity", "mcp", "codex", "vrchat", "ai"]
published: true
published_at: 2026-08-12 16:03
---

`KAFKA2306/image2outfit` にUnity MCP連携を入れたDraft PR #212には、setup、doctor、config、static testsがあります。

それでも2026-08-12時点で、次は **NOT_RUN** のままです。

- user Windows環境でのPowerShell setup
- live Blender MCP connection
- live Unity MCP connection / package resolution
- Blender Assistant → Codex → MCP のend-to-end call

PR: https://github.com/KAFKA2306/image2outfit/pull/212

ここで「MCP対応を実装した」と「Unity上で正しく動いた」の間に、かなり大きな空白があることに気づきました。

AIがEditorを操作できる。tool callが成功する。SceneやComponentを変更できる。

**それでも、VRChat向け成果物が完成した証拠にはなりません。**

最初は「UnityをAIから操作できれば自動化が進む」という話だと思っていました。実装を詰めるほど、必要だったのは能力の追加より、次の3つを別々に証明することでした。

1. AIがUnityを操作できる
2. その操作が正しかったと検証できる
3. VRChat向け成果物が完成した

なぜこの3つを一つの“成功”にしてはいけないのか。MCP for Unityをローカルauthoring adapterとして組み込んだ過程から追います。

## まず一次情報：MCP for Unityは何をするものか

CoplayDevの公式READMEは、MCP for Unityを、LLMとUnity EditorをModel Context Protocolで接続するbridgeと説明しています。

公式に列挙されている対象は、

- Scene / GameObjectの操作
- C# scriptの編集
- Asset管理
- Test実行
- Profile
- Build

です。

さらにREADMEでは **47 focused MCP tool entrypoints** と明記されています。

公式README:
https://github.com/CoplayDev/unity-mcp/blob/v10.1.2/README.md

`v10.1.2` のUnity package metadataも確認できます。

```json
{
  "name": "com.coplaydev.unity-mcp",
  "version": "10.1.2",
  "unity": "2021.3"
}
```

公式package metadata:
https://github.com/CoplayDev/unity-mcp/blob/v10.1.2/MCPForUnity/package.json

したがって、少なくとも公式が公開している能力の範囲では、AI側からUnityを「コードを書く対象」ではなく、**操作可能なEditor environment**として扱えます。

## 最初の仮説：Unity MCPを入れれば、デバッグもそのまま自動化できる

最初の発想は単純でした。

Unity上で表示が崩れたとき、人間が普段やっているのは、だいたい次のような巡回です。

```text
症状を見る
  ↓
Hierarchy / Prefabを見る
  ↓
Componentを見る
  ↓
Animator / Material / BlendShapeを見る
  ↓
Missing referenceやoverrideを見る
  ↓
修正する
  ↓
再生・Build・目視で確認する
```

repositoryだけを読むAIは、この途中までしか到達できません。

`.prefab` や `.controller` をテキストとして調べることはできても、現在開いているScene、Unityが解決したComponent、Package由来の状態、実際のEditor操作結果まで同じ粒度では扱えないからです。

MCP for Unityが間に入ると、構造はこう変わります。

```text
人間のprompt
   ↓
Codex / MCP client
   ↓
MCP tool call
   ↓
Unity Editor
   ├─ Scene
   ├─ GameObject / Component
   ├─ Asset
   ├─ Script
   ├─ Test
   ├─ Profiler
   └─ Build
```

ここだけを見ると、「ではUnityデバッグを全部エージェントに渡せばいい」と考えたくなります。

実際には、ここで一段問題が増えました。

## 発見1：ChatGPTのブラウザ画面と、ローカルUnity MCPは同じ接続経路ではない

これは最初に明確にしておく必要があります。

OpenAI公式のMCPドキュメントでは、Codex hostに設定したMCP serverについて、次が明記されています。

- ChatGPT desktop app
- Codex CLI
- Codex IDE extension

はMCP configurationを共有できます。

一方で、**ChatGPT webはローカルCodex設定ファイルを読みません**。

OpenAI公式:
https://developers.openai.com/codex/mcp

公式ドキュメントでは、Codex hostが扱うMCP transportとして、

- STDIO
- Streamable HTTP

が記載されています。

つまり、「ChatGPTからUnityを操作する」という言い方だけでは接続形態が曖昧です。

今回の `image2outfit` では、ローカルauthoringの正準線を **Codex + localhost MCP** として設計しました。

ブラウザ版ChatGPTが、そのままPC上のUnity Editorへ接続する設計ではありません。

## 発見2：v10.1.2ではCodex接続そのものに関係する修正が入っている

今回pinしたのは `v10.1.2` です。

公式Release Notes:
https://github.com/CoplayDev/unity-mcp/releases/tag/v10.1.2

このreleaseには、Codex利用に直接関係する変更として、少なくとも以下が記録されています。

- Codex向けHTTP transportの修復
- 34 toolsが毎回approval promptを強制していた問題の修正
- `manage_gameobject create` からcomponent propertiesへ到達できるようにする修正
- Windowsでserver launch時にstdinをNULへredirectする修正

ここで重要なのは、「MCPに対応している」という一語だけでは足りないことです。

Editor automationでは、transport、approval、component property accessのどれかが壊れるだけで、実際の操作経路が止まります。

そのため `image2outfit` 側では `#main` を追従せず、Issue #211で `v10.1.2` を明示的にpinしました。

Issue:
https://github.com/KAFKA2306/image2outfit/issues/211

## 実装：Unity MCPを「optional local authoring adapter」に限定した

実装はDraft PR #212に置いています。

https://github.com/KAFKA2306/image2outfit/pull/212

ここで最も重要な設計判断は、**MCPを製品完成条件へ入れなかったこと**です。

`image2outfit` には、衣装生成物を完成扱いにするための既存contractがあります。MCPを導入したからといって、そのcompletion boundaryを書き換えるのは危険です。

そこで、MCPはあくまで次の位置に置きました。

```text
                 ┌──────────────┐
                 │ Codex agent  │
                 └──────┬───────┘
                        │
                 localhost MCP
                        │
                 ┌──────▼───────┐
                 │ Unity Editor │
                 └──────┬───────┘
                        │ authoring / inspection
                        ▼
              existing product pipeline
                        │
                        ▼
             existing completion gates
```

MCP tool callが成功しても、既存のcompletion gateは変えません。

これは細かい実装ルールではなく、今回の中心的な発見でした。

> **「AIがEditorを操作できた」は、成果物が正しいことの証拠ではない。**

## localhostに閉じる

PR #212ではUnity側を次のURLでCodexへ登録する設計にしています。

```text
http://127.0.0.1:8080/mcp
```

Blender MCP側も `localhost:9876` に限定しています。

理由は単純です。Editorを変更できるbridgeは、通常のread-only documentation serverとは性質が違います。

MCP側にwrite capabilityがあるなら、ネットワーク境界も開発権限の一部として扱う必要があります。

そのため実装contractでは、

- `0.0.0.0` へbindしない
- API key / provider secretをcommitしない
- MCP auth materialやlocal runtime stateをcommitしない
- CIからlive Editor MCPを自動起動しない
- untrusted repository contentから自動実行しない
- Codexのapproval / sandbox controlをrepository scriptから迂回しない

という境界を置きました。

実装ドキュメント:
https://github.com/KAFKA2306/image2outfit/blob/feat/issue-211-mcp-support/docs/mcp-support.md

OpenAI公式側でも、Codex MCP設定にはserver単位・tool単位のapproval modeが用意されています。

https://developers.openai.com/codex/mcp

「EditorをAIに渡す」は、単に便利なtoolを追加する話ではありません。**誰が、どこから、どのwrite actionを呼べるか**を一緒に設計する必要があります。

## `doctor` をwrite actionより先に作った

今回、setupだけでなくread-onlyのhealth checkを用意しました。

```powershell
task mcp:doctor
```

確認対象は次です。

- `codexAvailable`
- `uvxAvailable`
- `blenderMcpRegistered`
- `unityMcpRegistered`
- `blenderPort9876Listening`
- `unityPort8080Listening`
- `blenderAddonDownloaded`
- `unityMcpPackageDetected`
- `unityProjectVersion`

狙いは、「動かない」状態を一つの巨大な失敗として扱わないことです。

例えばUnity MCPが動かないとしても、

```text
Codexがない
MCP登録がない
Packageがない
Unityが起動していない
portがlistenしていない
transportが違う
```

では修正方法が全部違います。

先に観測点を分解しておけば、AI agentにも人間にも、どのboundaryで止まっているかを渡せます。

この点はUnityに限りません。GUI applicationをagent化するとき、**write toolより先にread-only diagnosticsを作る**のはかなり重要だと感じました。

## 再現するなら、まずここまで

公式情報と今回の実装を合わせると、最小構成は次です。

Unity Package Managerからpinしたpackageを追加します。

```text
https://github.com/CoplayDev/unity-mcp.git?path=/MCPForUnity#v10.1.2
```

その後、Unity側で、

```text
Window > MCP for Unity > Configure All Detected Clients
```

を使います。

Codex側ではOpenAI公式ドキュメントにある通り、MCP serverをSTDIOまたはStreamable HTTPで設定できます。

設定後は、

```text
codex mcp list
```

またはCodex TUIの `/mcp` でactive serverを確認できます。

OpenAI公式:
https://developers.openai.com/codex/mcp

ただし、ここまで終わっても「VRChatアバター改変が完成した」ことにはしません。

## 何をまだ検証していないか

ここは意図的に残しています。

2026-08-12時点のDraft PR #212では、以下を **NOT_RUN** としています。

- user Windows環境でのPowerShell setup
- live Blender MCP connection
- live Unity MCP connection / package resolution
- Blender Assistant → Codex → MCP のend-to-end call

PR:
https://github.com/KAFKA2306/image2outfit/pull/212

つまり、この記事は「Unity MCPで実際にアバター修復まで成功した」という成功報告ではありません。

確認できているのは、

- upstream version / package metadata
- CodexのMCP transport仕様
- localhost前提のintegration設計
- setup / doctor / config / static testsの実装

までです。

live Editor validationはまだ別の証拠として必要です。

この区別を崩すと、「コードを書いた」「MCP toolが返事した」「Unity上で正しく動いた」「VRChat runtimeで正しい」が一つの“成功”に圧縮されてしまいます。

それは避けたい。

## 最初の仮説はどう変わったか

最初の仮説は、

> Unity MCPを入れれば、人間がInspectorを巡回する仕事をAIへ移せる

でした。

今は少し違います。

> Unity MCPでEditor stateをAIの調査対象にはできる。しかし、agentの操作成功と成果物の完成判定を分離しないと、むしろ自動化によって誤った「完了」が増える。

MCPで追加したかったのはwrite capabilityでした。

しかし実際に先に必要だったのは、

- version pin
- transport boundary
- localhost boundary
- approval boundary
- read-only doctor
- completion gateとの分離

でした。

## 結論

Unity MCPの面白さは、「AIがC#を書ける」ことではありません。

**Scene、GameObject、Component、Asset、Test、BuildといったUnity Editor側の状態を、AI agentが呼び出せるtoolへ変えられること**です。

一方で、そのtool callが成功したことは、アバターやゲームが正しく完成した証拠にはなりません。

今回 `image2outfit` にMCPを入れる設計で一番重要だったのは、AIにUnityを触らせることよりも、**「触れた」「正しかった」「完成した」を別々に証明する境界を残すこと**でした。

### 一次情報・実装証拠

- MCP for Unity `v10.1.2` README  
  https://github.com/CoplayDev/unity-mcp/blob/v10.1.2/README.md
- MCP for Unity `v10.1.2` release  
  https://github.com/CoplayDev/unity-mcp/releases/tag/v10.1.2
- MCP for Unity package metadata  
  https://github.com/CoplayDev/unity-mcp/blob/v10.1.2/MCPForUnity/package.json
- OpenAI Codex MCP documentation  
  https://developers.openai.com/codex/mcp
- `image2outfit` Issue #211  
  https://github.com/KAFKA2306/image2outfit/issues/211
- `image2outfit` Draft PR #212  
  https://github.com/KAFKA2306/image2outfit/pull/212
- `image2outfit` MCP integration document  
  https://github.com/KAFKA2306/image2outfit/blob/feat/issue-211-mcp-support/docs/mcp-support.md
