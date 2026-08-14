---
title: "AIの「秘密の透かし」は誰が検出する？ 生成側の秘密と第三者検証を分けて考える"
emoji: "🔐"
type: "tech"
topics: ["watermark", "security", "llm", "ai", "provenance"]
published: false
published_at: 2026-08-13 09:00
---

「AIが生成した文章に、外からは見えない透かしが入っている」と聞くと、次の疑問が出る。

> 第三者が検出するには、生成側の秘密まで共有しないといけないのでは？

最初はClaudeを題材にこの疑問を考えていた。

しかし、2026年8月14日にAnthropicの現行一次情報を確認し直すと、記事の前提を変える必要があった。

AnthropicのTransparency Hubは、Claudeが現在text-based outputsを提供していること、watermarkingについてindustry・academiaで技術動向を追い、適用法令への準備を進めていることを説明している。一方、その公開ページは**Claudeのtext outputへ現在どのwatermark方式を実装しているか、secret/keyをどう管理するか、第三者向けtext detectorを提供しているか**までは述べていない。

- Anthropic Transparency Hub: https://www.anthropic.com/transparency/voluntary-commitments/security%26privacy

だから、Claudeに「秘密のtext watermarkが実装されている」という前提では書かない。

代わりに、現在実装を公式に説明しているGoogle DeepMindのSynthIDを実例にして、もっと一般的な問いへ戻す。

**AI生成物を第三者が検証できることと、生成側の秘密情報を第三者へ配ることは同じ要件なのか。**

## まず、現在公開されている事実を分ける

### Anthropicについて確認できること

Anthropicの現行Transparency Hubは、Claudeのoutput transparencyに関してwatermarkingの技術動向を探索・追跡していると説明している。

ここから言えるのは、watermarkingが検討対象であることまでだ。

この記事では次を推測しない。

```text
Claudeには現在text watermarkが入っている
Claudeは特定のsecret key方式を使っている
Claudeには非公開detector APIがある
ClaudeはSynthIDと同じ方式である
```

公開されていない内部設計を、別providerの技術から逆算しない。

### SynthIDについて確認できること

Google DeepMindの現行SynthIDページは、image / audio / text / videoへwatermarkを埋め込む技術を説明している。

textについては、Gemini app / web experienceで生成されたtextのwatermarking・identificationへSynthIDを拡張し、LLMのtoken probability scoreを調整してwatermarkを生成すると説明している。

- Google DeepMind SynthID: https://deepmind.google/models/synthid/

一方、同じ現行ページで一般ユーザー向けに案内されているGeminiのupload検証とSynthID Detector portalは、image / video / audioを対象として記載されている。

つまり、**watermarking技術が存在すること**と、**誰でも使える同一形式のverification interfaceが存在すること**も別問題である。

## 「watermarkがある」を1bitで扱わない

生成AIのprovenanceを評価するとき、最低限4つへ分けると整理しやすい。

```text
1. Embedding
   何を生成時に埋め込むか

2. Secret / parameters
   検出に必要な非公開情報があるか、誰が保持するか

3. Detection
   何を入力に、どの主体が判定するか

4. Verification interface
   外部利用者へ何を公開するか
```

これらは別componentである。

「watermarkあり」という説明だけでは、

- providerだけが検出できるのか
- 第三者がローカル検出できるのか
- API経由で判定だけ受け取るのか
- secretを配る必要があるのか
- provider停止後も検証できるのか

は分からない。

## 第三者検証に「secretの配布」は必須ではない

これは特定providerの現行実装を説明する話ではなく、architecture上の分離である。

例えばverification service型なら、

```text
third party
   ↓ content
verification service
   ↓
private detector / parameters
   ↓
result
```

とできる。

第三者はcontentを送って判定結果を受け取るが、detector内部のsecret materialを直接受け取らない。

一方、独立検証を優先するなら、

```text
third party
   ├─ content
   └─ independently usable verifier
```

のように、provider外でも検証できる設計が必要になる。

この2つはtrade-offが違う。

| 設計 | secret管理 | 独立性 | provider依存 |
|---|---|---|---|
| Provider verification service | provider側へ閉じやすい | 低い | 高い |
| Public / independently usable verifier | verifier設計次第 | 高めやすい | 低くできる |
| Operator-only detection | 外部共有不要 | 低い | 非常に高い |

重要なのは、**第三者検証可能性とsecret共有範囲を別の設計変数として扱うこと**だ。

## 「検出できる」の中にも複数のUXがある

利用者から見ると、どれも「watermarkを確認できる」ように見える。

しかし体験は違う。

### providerへ聞く

```text
contentを送る
→ providerが判定
→ resultを返す
```

簡単だが、provider availabilityや判定仕様へ依存する。

### 自分で検証する

```text
content + verifier
→ local / independent verification
```

再現性は高めやすいが、公開できるverification materialの設計が必要になる。

### providerだけが内部利用する

abuse monitoringや内部provenanceには使えても、一般ユーザーは直接確認できない。

「detectable」という言葉だけでは、どのUXなのか分からない。

## 実装を評価するときは5つ質問する

AI生成物のmarking機能を見るとき、私は今後次を分けて確認する。

1. **現在、本当に実装済みか**  
   research / exploration / commitmentとproduction deploymentを分ける。

2. **何をmarkしているか**  
   text token selection、media signal、metadataなど。

3. **誰がdetectできるか**  
   provider、一般ユーザー、限定partner、独立第三者。

4. **verificationに何が必要か**  
   public verifier、API access、private parametersなど。

5. **providerなしで将来も検証できるか**  
   long-term provenanceとして使うなら重要になる。

この5問を通すと、「watermarkがあるらしい」という曖昧な説明から、実際の利用可能性へ進める。

## Claudeについては「未確認」を正しいstateにする

この記事を書き直して一番大きく変わったのはここだった。

旧稿では、Claudeにsecret watermarkがあると仮定したときの設計を中心に考えていた。

現行一次情報へ戻ると、Anthropicはwatermarkingへの取り組み・準備を説明しているが、この記事で必要なClaude text watermarkの具体実装は公開確認できない。

だからstateを、

```text
implemented_secret_text_watermark
```

ではなく、

```text
vendor_publicly_discusses_watermarking
specific_claude_text_watermark_implementation = not established here
```

へ戻す。

**分からないものを、別providerの例で埋めない。**

これはwatermark技術そのものより、AI productを評価するときの重要な習慣だと思う。

## 読者が自分のsystemへ持ち帰る最小model

自社で生成物provenanceを設計するなら、最初から「watermark機能」という1boxにしない。

```yaml
provenance:
  embedding:
    mechanism: TBD

  detection:
    operator: TBD

  verification_interface:
    audience: TBD

  secret_or_parameters:
    holder: TBD

  long_term_verifiability:
    provider_independent: TBD
```

この形なら、

- secretは閉じたい
- 顧客には確認手段を提供したい
- 監査者には独立verificationを提供したい

といった要件を別々に議論できる。

## まとめ

最初の疑問は、

> 第三者へ検出させるなら、秘密鍵も渡さないといけないのでは？

だった。

今の結論はもっと分解されている。

**第三者が検証できること、誰がdetectorを持つこと、secretを誰が保持すること、providerなしで独立検証できることは別の要件である。**

そしてClaudeについては、2026年8月14日時点のAnthropic公開情報を超えて具体的なtext watermark実装を推測しない。

公開実装の具体例が必要ならSynthIDを見る。

vendor固有の事実が必要ならvendor自身の現在の一次情報へ戻る。

その境界を守る方が、もっともらしい説明を作るより役に立つ。

## 一次情報

- Anthropic Transparency Hub: https://www.anthropic.com/transparency/voluntary-commitments/security%26privacy
- Google DeepMind SynthID: https://deepmind.google/models/synthid/
