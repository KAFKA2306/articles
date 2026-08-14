---
title: "Claudeの「秘密の透かし」は誰のため？ 検出と秘密鍵共有を分けて考える"
emoji: "🔐"
type: "tech"
topics: ["claude", "watermark", "security", "llm", "ai"]
published: false
published_at: 2026-08-13 09:00
---

# Claudeの「秘密の透かし」は誰のため？ 検出と秘密鍵共有を分けて考える

Claudeの生成テキストに機械検出可能なmarkingを入れるとしたら、誰がそれを判定できるのでしょうか。

この問いを考えると、すぐに「秘密鍵を第三者へ渡さなければ検出できないのでは？」という疑問が出ます。

しかし、公開されているtext watermark研究を見ると、**検出できること**と**watermark keyを第三者へ配ること**は同じ問題ではありません。

この記事では、この1点だけを整理します。

なお、2026年8月13日時点で、AnthropicがClaudeのtext watermarkについて、sampling方式、key管理、detector APIの内部仕様を公開している一次情報は確認できませんでした。したがって、ClaudeがGoogle SynthID-Textや特定論文と同じ方式を使っているとは扱いません。

## まず、公開研究では何が起きているか

Google DeepMindのSynthIDは、AI生成textへwatermarkを埋め込み、後から識別する技術を公開しています。

公式説明では、LLMが次tokenを選ぶときの確率分布へ追加情報を入れ、watermark patternを作ります。

- Google DeepMind SynthID: https://deepmind.google/models/synthid/
- 公式技術解説: https://deepmind.google/blog/watermarking-ai-generated-text-and-video-with-synthid/

重要なのは、watermarkが文章の末尾へ固定文字列を付ける方式ではないことです。生成時のtoken選択へ統計的な偏りを入れ、その偏りを後からscoreとして検出します。

概念的には次のように分けられます。

```text
生成
LLM token distribution
        ↓
watermarking rule
        ↓
選択分布をわずかに変える
        ↓
text

検出
text
  ↓
同じwatermarking ruleに基づきscoreを計算
  ↓
watermarked / not watermarked を統計判定
```

この構造から分かるのは、**検出処理と文章生成処理は別に実装できる**ということです。

## 「第三者が検出する」には2通りある

ここで鍵管理を考えます。

### 方式A: detectorを第三者へ配る

第三者が必要な情報を持ち、自分でwatermark scoreを計算します。

```text
third party
  ├─ text
  ├─ detector
  └─ detectorに必要なkey / parameter
       ↓
     score
```

この方式は検出主体が独立できますが、秘密にしたい情報まで配布する設計なら、漏えい・解析・偽装への対策が必要になります。

### 方式B: keyはprovider内部に置き、判定APIだけ公開する

```text
third party
  ↓ text
provider detector API
  ↓
provider内部のkey / detector
  ↓
score / 判定だけ返す
```

この構成なら、第三者はwatermarkを確認できますが、keyそのものを受け取る必要はありません。

したがって、

> 第三者にも検出可能にしたい

という要求から、

> 秘密鍵を第三者全員へ配る必要がある

とは導けません。

## なぜ「鍵を公開しない検出」に意味があるのか

watermarkに秘密情報を使う設計では、その情報が攻撃者へ渡ると、watermark除去や偽watermark生成を容易にする可能性があります。

一方で、判定結果だけを返すAPIなら、key materialをprovider側に閉じたまま外部検証を提供できます。

もちろん、API化すれば別の問題が生まれます。

- provider停止時に検証できない
- rate limitや料金に依存する
- providerが判定ロジックを変更できる
- 第三者がdetector自体を監査しにくい

つまり設計問題は「秘密鍵を共有するかどうか」だけではありません。

**検出可能性・独立監査性・攻撃耐性・運用依存性をどこで分けるか**です。

## SynthIDからClaudeの内部実装を逆算しない

ここがこの記事で最も重要な境界です。

SynthIDがtoken probabilityへwatermarkを入れているからといって、Claudeも同じ方式とは言えません。

同様に、公開研究にkeyed watermarkがあるからといって、Claudeにも同じ意味の秘密鍵があるとは断定できません。

この記事で確実に言えるのは次だけです。

```text
公開研究では
「検出」と「key配布」を分離できる設計が存在する
```

Claude固有の内部仕様については、Anthropicの一次情報が公開されるまで未確定として扱います。

## EU AI Actが要求しているのは「秘密鍵共有」ではない

EU AI Act Regulation (EU) 2024/1689 Article 50(2) は、synthetic audio / image / video / textを生成するAI system providerに対し、出力をmachine-readable formatでmarkし、人工生成・操作されたことをdetectableにするよう求めています。

一次情報:
https://eur-lex.europa.eu/eli/reg/2024/1689/oj?locale=en

ここでも条文が要求しているのは、**machine-readable markingとdetectability**です。

「watermark secretを一般公開すること」までは書かれていません。

したがって制度面でも、

```text
detectableである
!=
secret keyを公開する
```

と分けて考える必要があります。

## 検出器を評価するときの4つの質問

text watermarkを採用するサービスを見るときは、次の4点を分けて確認すると混乱しにくくなります。

1. **何をmarkしているか**  
   token selectionなのか、metadataなのか、別の信号なのか。

2. **誰がdetectできるか**  
   providerだけか、一般ユーザーか、限定された第三者か。

3. **何を共有する必要があるか**  
   full detector、public parameter、secret key、API accessのどれか。

4. **判定を独立検証できるか**  
   provider停止後も検証できるのか、provider APIへの依存が残るのか。

「watermarkがある」という1bitの説明だけでは、この4つは分かりません。

## 読者が再利用できる最小モデル

生成AIのprovenance機能を設計するときは、次のように役割を分けると整理しやすくなります。

```text
Generator
  └─ watermark embedding

Key / secret service
  └─ detectorに必要な秘密情報を保持

Detector
  └─ textからscoreを計算

Verification interface
  └─ 第三者へ結果を返す
```

この4つを1つの「watermark機能」に潰さないことが重要です。

GeneratorとDetectorを別サービスにしてもよいし、keyをDetector内部だけに閉じてもよい。第三者へはverification interfaceだけを公開することもできます。

## まとめ

最初の疑問は「秘密鍵を第三者へ渡さないとwatermarkを検出できないのでは？」でした。

公開研究から分かる答えは、もっと設計自由度があります。

**第三者が検出できることと、第三者が秘密鍵を保持することは別です。**

providerがkeyを保持したままdetector APIだけを公開する設計も成立します。一方、独立監査性を重視するなら、別の公開検証方式が必要になります。

Claudeについては内部仕様を推測しません。Anthropicが公開していない部分を、SynthIDや他研究から埋めないこと自体が、この記事の証拠境界です。

## 一次情報

- Google DeepMind — SynthID: https://deepmind.google/models/synthid/
- Google DeepMind — Watermarking AI-generated text and video with SynthID: https://deepmind.google/blog/watermarking-ai-generated-text-and-video-with-synthid/
- Regulation (EU) 2024/1689 Article 50: https://eur-lex.europa.eu/eli/reg/2024/1689/oj?locale=en
