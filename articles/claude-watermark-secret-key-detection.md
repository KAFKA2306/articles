---
title: "AIの文章に「透かし」があると言われたら、誰がそれを証明できるのか"
emoji: "🔐"
type: "tech"
topics: ["watermark", "security", "llm", "ai", "provenance"]
published: true
published_at: 2026-08-13 09:00
---

採用課題、レポート、ニュース原稿、社内文書。

ある文章を見て、誰かがこう言ったとする。

> 「これはAI生成です。透かしで分かります」

ここで本当に知りたいのは、透かしの仕組みそのものではない。

**誰が、その判定を証明できるのか。**

生成AIの会社だけが判定できるのか。第三者も検証できるのか。第三者が検証するなら、生成側の秘密鍵まで渡す必要があるのか。

私は最初、Claudeを題材に「秘密のtext watermarkを第三者がどう検出するか」を考えていた。

ところが2026年8月15日にAnthropicの一次情報へ戻ると、その出発点を捨てる必要があった。

AnthropicのTransparency Hubは、Claudeが現在text-based outputsを提供していること、watermarkingについてindustry・academiaで技術動向を追っていることを説明している。しかし、その公開ページは**Claudeのtext outputへ現在どのwatermark方式を実装しているか、secret/keyをどう管理するか、第三者向けtext detectorを提供しているか**までは述べていない。

- Anthropic Transparency Hub: https://www.anthropic.com/transparency/voluntary-commitments/security%26privacy

つまり、ここで「Claudeには秘密のtext watermarkがある」と話を進めると、記事の一番大事な部分を推測で埋めることになる。

そこで問いを変えた。

**AI生成物を第三者が検証できることと、生成側の秘密情報を第三者へ配ることは、本当に同じ要件なのか。**

## 実装済みの例を見ると、問いが具体化する

現在、text watermarkの具体例として一次情報を追えるのがGoogle DeepMindのSynthID-Textだ。

Google DeepMindはSynthIDをimage / audio / text / videoへ適用する技術として公開しており、textではGemini app / web experienceで生成される文章へwatermarkingとidentificationを拡張したと説明している。

- Google DeepMind SynthID: https://deepmind.google/models/synthid/

2024年にNatureへ掲載されたSynthID-Text論文では、生成時にtokenの選択へwatermark signalを入れ、検出側はその偏りをscoreする方式が説明されている。論文のMethodsでは、scoring functionがtokenized text、watermarking key、random seed generatorを使い、**underlying LLMへアクセスせずに検出できる**と記載されている。

- Dathathri et al., *Scalable watermarking for identifying large language model outputs*: https://www.nature.com/articles/s41586-024-08025-4

Google DeepMindはreference implementationも公開している。そこではwatermark configurationに`keys`があり、Mean / Weighted Mean / Bayesian detectorの実装も確認できる。ただしREADME自身が、このrepositoryをreference implementationでありproduction用ではないと明記している。

- google-deepmind/synthid-text: https://github.com/google-deepmind/synthid-text

ここで最初の疑問が少し変わる。

「keyが必要なdetectorがある」ことと、**そのkeyを検証したい全員へ配布しなければならない**ことは同じではない。

## 「watermarkがある」を1bitで扱わない

生成AIのprovenanceを評価するとき、少なくとも次の4つを分けた方がいい。

```text
1. Embedding
   生成時に何を埋め込むか

2. Secret / parameters
   検出に必要な非公開情報は何か、誰が保持するか

3. Detection
   何を入力に、誰が判定するか

4. Verification interface
   外部利用者へ何を公開するか
```

これらは別componentである。

「watermarkあり」という一言だけでは、

- providerだけが検出できるのか
- 第三者がローカル検出できるのか
- API経由で判定だけ受け取るのか
- secretを配る必要があるのか
- provider停止後も検証できるのか

は分からない。

この区別をしないと、「検出可能」と「独立検証可能」が同じ言葉に潰れてしまう。

## 第三者検証にsecretの配布は必須ではない

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

第三者はcontentを送り、判定結果だけを受け取る。detector内部のsecret materialはprovider側に残せる。

ただし、この設計では第三者はproviderのservice availability、判定仕様、運用継続性を信頼する必要がある。

一方、独立検証を優先するなら、

```text
third party
   ├─ content
   └─ independently usable verifier
```

のように、provider外でも再現可能なverification materialが必要になる。

| 設計 | secret管理 | 独立性 | provider依存 |
|---|---|---|---|
| Provider verification service | provider側へ閉じやすい | 低い | 高い |
| Public / independently usable verifier | verifier設計次第 | 高めやすい | 低くできる |
| Operator-only detection | 外部共有不要 | 低い | 非常に高い |

重要なのは、**第三者検証可能性とsecret共有範囲を別の設計変数として扱うこと**だ。

## 「検出できた」は「証明できた」とも限らない

ここはwatermarkを議論するときに最も落としたくない境界だ。

SynthID-Text論文は、watermarkがAI text detectionの完全な解ではないと明記している。生成側がwatermarkingを実装しなければ当然検出できず、textへのeditやLLM paraphrasingでwatermarkが弱くなること、stealing / spoofing / scrubbing attackが研究課題であることもlimitationsとして挙げている。

だから、detectorの出力をそのまま、

```text
AI生成であることの絶対的証明
```

とは扱わない方がいい。

実運用で知りたいのは、少なくとも次だ。

```text
何を検出しているのか
どのthresholdで判定するのか
false positive / false negativeをどう扱うのか
編集・翻訳・要約後にどこまで残るのか
誰がverifierを運用しているのか
```

これは「watermarkがあるか」より一段実務的な問いになる。

## 実は、provenanceにはwatermark以外の設計もある

ここで一度、watermarkから離れると整理しやすい。

C2PAのContent Credentialsは、provenance情報をmanifestとして持ち、claimをdigital signatureで署名し、trust modelに基づいて検証するarchitectureを定義している。

- C2PA Specifications 2.2: https://spec.c2pa.org/specifications/specifications/2.2/index.html
- C2PA Content Credentials specification: https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html

これはtext watermarkと同じ仕組みではない。

しかし、「第三者が検証するなら秘密を共有しなければならない」という直感が一般には成り立たないことを理解するにはよい対照になる。署名者側の秘密と、検証者が使うverification materialは分離できる。

つまり、本当に設計したいのは「秘密をどう隠すか」だけではない。

**誰が、何を根拠に、どこまで独立して検証できるか**である。

## Claudeについては「未確認」を正しいstateにする

この記事を書き直して一番大きく変わったのはここだった。

旧稿では、Claudeにsecret watermarkがあると仮定したときの設計を中心に考えていた。

しかし現行一次情報へ戻ると、Anthropicはwatermarkingへの取り組みを説明しているものの、この記事で必要なClaude text watermarkの具体実装は公開確認できない。

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

これはwatermarkに限らない。AI productを比較するとき、公開されていない内部設計を「たぶん同じだろう」で補うと、もっともらしい説明ほど危険になる。

## 読者が持ち帰る5つの質問

今後、AI生成物のmarkingやprovenance機能を見るときは、私は次の5つを先に確認する。

1. **現在、本当に実装済みか**  
   research / exploration / commitmentとproduction deploymentを分ける。

2. **何をmarkしているか**  
   text token selection、media signal、metadata、署名などを分ける。

3. **誰がdetect / verifyできるか**  
   provider、一般ユーザー、限定partner、独立第三者を分ける。

4. **verificationに何が必要か**  
   public verifier、API access、key / parameters、credentialなどを確認する。

5. **providerなしで将来も検証できるか**  
   long-term provenanceとして使うなら、ここが効いてくる。

この5問を通すだけで、「watermarkがあるらしい」という曖昧な説明から、実際に使えるverification designへ進める。

## 最後に

最初の疑問は単純だった。

> 第三者へ検出させるなら、秘密鍵も渡さないといけないのでは？

今は、問いそのものが変わっている。

**第三者が検証できること、誰がdetectorを持つこと、secretを誰が保持すること、providerなしで独立検証できることは、すべて別の要件である。**

そして、watermarkの検出結果そのものにも限界がある。

だからAI生成物を見るとき、「透かしは入っていますか？」で止まらない方がいい。

**「その主張を、誰が、何を使って、どこまで独立して確かめられるのか？」**

この問いに変えるだけで、vendorの説明を読むときも、自社systemを設計するときも、判断の解像度が一段上がる。

## 一次情報

- Anthropic Transparency Hub: https://www.anthropic.com/transparency/voluntary-commitments/security%26privacy
- Google DeepMind SynthID: https://deepmind.google/models/synthid/
- Dathathri et al., *Scalable watermarking for identifying large language model outputs*: https://www.nature.com/articles/s41586-024-08025-4
- google-deepmind/synthid-text: https://github.com/google-deepmind/synthid-text
- C2PA Specifications 2.2: https://spec.c2pa.org/specifications/specifications/2.2/index.html
- C2PA Content Credentials specification: https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html
