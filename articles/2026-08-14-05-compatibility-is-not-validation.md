---
title: "動いたから使える、ではない。未知言語の互換性を3段階で止める"
emoji: "🧪"
type: "tech"
topics: ["python", "machinelearning", "nlp", "testing"]
published: false
published_at: 2026-08-14 16:00
---

英語向けに見えるNLPライブラリへ日本語を渡したとき、例外が出なければ「日本語でも使える」と判断してよいのか。

答えは、少なくとも実務の品質ゲートでは **No** だと思う。

今回 `KAFKA2306/detective` で公開OSS `explain_ai_generated_text` 0.1.1.1.7を調べたところ、日本語を実際に評価する以前に、import時点でspaCyの `en_core_web_sm` が無く停止した。ここで面白いのは、失敗そのものよりも、**「依存関係が揃う」「未知言語で実行できる」「その言語で意味的に妥当である」を別の状態として記録しないと、検証結果を簡単に過大解釈できる**ことだった。

この記事では、未知の言語・データ形式・実行環境へML/NLPライブラリを持ち込むときに、互換性確認を3段階へ分離する方法を整理する。

一次情報:

- https://github.com/KAFKA2306/detective/commit/554cec387761da2e292e1d8800b86c97eddbc268
- https://github.com/KAFKA2306/detective/commit/0d2f2da1d064c45fe8c5554cb314b712d102976d
- https://github.com/ShushantaTUD/Explain_AI_Generated_Text/blob/78b7d674e03cd2b4fdde065bfef493854f43c2f1/src/explain_ai_generated_text/utils.py
- https://github.com/ShushantaTUD/Explain_AI_Generated_Text/blob/78b7d674e03cd2b4fdde065bfef493854f43c2f1/pyproject.toml
- https://github.com/explosion/spacy-models

## 1. 問題: 「実行できた」と「使ってよい」が混ざる

例えば、AI生成文検出ライブラリに日本語を渡したいとする。

```python
result = detector("これは日本語のテキストです")
print(result)
```

ここで値が返れば、技術的には嬉しい。しかし、分かったことは最大でも「その入力で関数呼び出しが完走した」までである。

まだ次は分からない。

- 必要なモデルや辞書が正しく入っているか
- 日本語を想定した特徴抽出になっているか
- 学習時と同じ意味を特徴量が持つか
- 日本語で分類性能が検証されているか
- 返された予測を業務判断へ使ってよいか

`detective` で作った互換性probeでは、あえて `english_control` と `japanese_probe` の2入力を用意し、最初から次の解釈を禁止した。

```json
{
  "use_for_ai_authorship": false,
  "use_for_year_inference": false,
  "reason": "Compatibility probe only; upstream generalization to Japanese is not assumed."
}
```

この禁止を先に置くのが重要だった。テストが成功してから「どこまで言ってよいか」を考えると、成功という結果に引っ張られて評価範囲を広げやすい。

## 2. 実際には日本語入力まで到達しなかった

probeは次の順序だった。

```python
try:
    from explain_ai_generated_text import shap_explainer
except Exception as exc:
    report["import_error"] = f"{type(exc).__name__}: {exc}"
else:
    for name, text in SAMPLES.items():
        value = shap_explainer(text)
```

結果は `blocked` だった。

記録されたエラーはこれである。

```text
OSError: [E050] Can't find model 'en_core_web_sm'.
It doesn't seem to be a Python package or a valid path to a data directory.
```

つまり、このrunで確認できたのは **日本語非対応ではない**。逆に **日本語対応でもない**。

確認できたのは、対象環境では必要なspaCyモデルが不足し、ターゲット入力を評価する段階へ到達しなかった、という事実だけである。

この区別をしないと、CIでよくある次の誤判定が起こる。

```python
try:
    run_probe()
except Exception:
    print("Japanese unsupported")
```

これは壊れた失敗例である。依存関係不足、ネットワーク失敗、モデル破損、入力非対応を全部「日本語非対応」へ潰してしまう。

## 3. 原因: 互換性をbooleanで持っていた

`compatible = true / false` の2値は、ML/NLPの外部ライブラリ評価には粗すぎる。

少なくとも次の3段階は分けた方がよい。

### Gate A: Environment Ready

依存パッケージ、追加モデル、辞書、モデルファイルを読み込めるか。

今回の実runはここで停止した。

上流実装を見ると、`utils.py` はimport時に次を実行している。

```python
nlp = spacy.load("en_core_web_sm")
tool = language_tool_python.LanguageTool("en-US")
stop_words = set(stopwords.words("english"))
```

さらに特徴量には英語のdiscourse marker、modal、personal pronoun、hedge、transitionなどが明示的に定義されている。

例えば次のような集合である。

```python
personal_pronouns = {"i", "me", "my", "mine", "we", "us", "our", "ours"}
hedge_words = {"maybe", "perhaps", "probably", "possibly", ...}
```

したがって、`en_core_web_sm` を追加インストールしてimportが通ったとしても、それだけでは日本語向けの意味妥当性は確認できない。

### Gate B: Executes on Target Input

未知言語・未知形式の入力を渡し、例外なく特徴抽出と推論が完走するか。

これは **実行互換性** の確認である。

成功時の状態名も、例えば次のように限定すると誤読しにくい。

```text
executes_on_japanese_not_validated
```

`japanese_supported` と書かないことがポイントである。

### Gate C: Validated for Intended Use

対象言語・対象ドメインについて、正解付きデータと評価指標を使って用途上十分な性能を検証したか。

ここまで通って初めて、用途に応じて `validated` を名乗れる。

例えばAI生成文判定へ使うなら、日本語のhuman/AIラベル付き評価集合、評価手順、指標、閾値、エラー分析が必要になる。今回のprobeにはその検証は無いため、このGateを通ったとは扱わない。

## 4. 設計判断: 状態を「失敗理由」ではなく「到達段階」で持つ

実装では、例外メッセージだけを保存するより、到達段階をmachine-readableにした方が扱いやすい。

例えば次のようにする。

```python
from dataclasses import dataclass
from enum import StrEnum

class Stage(StrEnum):
    ENVIRONMENT_BLOCKED = "environment_blocked"
    EXECUTION_BLOCKED = "execution_blocked"
    EXECUTES_NOT_VALIDATED = "executes_not_validated"
    VALIDATED = "validated"

@dataclass
class CompatibilityResult:
    stage: Stage
    error: str | None = None
    can_use_for_decision: bool = False
```

重要なのは `can_use_for_decision` のdefaultを `False` にすることだ。

互換性probeは「使える証明」ではなく、**次の検証段階へ進めるかを判定する前処理**として扱う。

改善後の例はこうなる。

```python
try:
    detector = import_detector()
except Exception as exc:
    result = CompatibilityResult(
        stage=Stage.ENVIRONMENT_BLOCKED,
        error=f"{type(exc).__name__}: {exc}",
    )
else:
    try:
        detector(JAPANESE_PROBE)
    except Exception as exc:
        result = CompatibilityResult(
            stage=Stage.EXECUTION_BLOCKED,
            error=f"{type(exc).__name__}: {exc}",
        )
    else:
        result = CompatibilityResult(
            stage=Stage.EXECUTES_NOT_VALIDATED,
        )
```

この時点では、予測が `AI` でも `Human` でも、その値自体を評価結果として採用しない。

## 5. 代替案と、なぜ採らなかったか

### 代替案A: 依存を全部入れてから一気に判定する

一見速い。しかし、どの条件を満たしたことで成功したのかが分かりにくい。

依存解決と対象言語評価を1つのテストへ入れると、失敗位置も混ざる。

### 代替案B: 関数が値を返せば互換とする

最も危険である。

特徴量計算が英語前提でも、文字列処理だけなら日本語で数値を返す関数はあり得る。数値が返ることと、その数値が学習時と同じ意味を持つことは別である。

### 代替案C: package metadataだけで対象言語を推定する

上流 `pyproject.toml` では、パッケージはPython 3.8以上、SHAP、XGBoost、spaCy、LanguageTool、TextBlob、NLTKなどへの依存を宣言している。一方、ここから日本語での検証済み性能を読み取ることはできない。

metadataは依存関係確認には使えても、未知言語へのgeneralization証明にはならない。

## 6. 実装: probe自体に解釈上限を埋め込む

今回のprobeで再利用しやすかったのは、テストコードの外に説明を書くのではなく、report自体へinterpretation gateを埋め込んだ点だった。

```python
report = {
    "status": "blocked",
    "samples": {},
    "interpretation_gate": {
        "use_for_ai_authorship": False,
        "use_for_year_inference": False,
        "reason": (
            "Compatibility probe only; "
            "upstream generalization to Japanese is not assumed."
        ),
    },
}
```

この形式なら、後段のdashboardやCIが `status` だけを見て勝手に「検証済み」へ昇格させることを防ぎやすい。

さらに実務では、次も一緒に保存するとよい。

```json
{
  "package": "explain-ai-generated-text",
  "version": "0.1.1.1.7",
  "stage": "environment_blocked",
  "target_input": "japanese",
  "decision_allowed": false,
  "evidence": [
    "probe source URL",
    "result artifact URL",
    "upstream source URL"
  ]
}
```

結果を人間向け文章だけにしないことで、別の利用箇所が誤って意味を拡張しにくくなる。

## 7. 検証: 何をPASSと呼ぶかを先に決める

互換性テストの完了条件を、次のように固定できる。

| 段階 | PASS条件 | 言ってよいこと |
|---|---|---|
| Environment | importと必要モデルload成功 | 実行準備が整った |
| Execution | target inputで処理完走 | その入力で実行できた |
| Validation | 対象用途の評価集合で基準達成 | その用途で検証済み |

ここで、前段のPASSから後段のPASSを推論しない。

今回の実runはEnvironment段階で `blocked` だったため、ExecutionもValidationも **未評価** とするのが正確である。

`false` と `not evaluated` も分ける。

```json
{
  "environment_ready": false,
  "executes_on_japanese": null,
  "validated_on_japanese": null
}
```

`null` は弱さではない。まだ観測していないことを正しく残している。

## 8. 失敗から学んだこと

当初の関心は「この2026年のOSSを日本語にも使えるか」だった。

しかし実runで最初に得た成果は、日本語に関する性能値ではなく、`en_core_web_sm` という前提が実行環境に存在しないことだった。

ここでモデルを入れて即座に再実行し、値が返ったら「日本語対応」と書くのは簡単だった。しかし上流の特徴抽出を見ると、英語stopwords、`en-US` LanguageTool、英語のpronounやhedge語彙などが含まれている。

つまり、依存を直すことと、日本語適合性を証明することは別作業である。

**修復可能な実行失敗を直した直後ほど、意味的な検証を飛ばしやすい。**

ここを状態機械で分離しておくと、修復後も `executes_not_validated` で止められる。

## 9. 再現方法

読者側では、対象ライブラリを自分の用途へ持ち込む前に、まず小さなprobeを作ればよい。

```python
import json

report = {
    "environment_ready": False,
    "executes_on_target": None,
    "validated_for_task": None,
    "decision_allowed": False,
}

try:
    from your_library import analyze
except Exception as exc:
    report["error"] = f"{type(exc).__name__}: {exc}"
else:
    report["environment_ready"] = True
    try:
        analyze("対象言語の短いprobe")
    except Exception as exc:
        report["executes_on_target"] = False
        report["error"] = f"{type(exc).__name__}: {exc}"
    else:
        report["executes_on_target"] = True

print(json.dumps(report, ensure_ascii=False, indent=2))
```

ここでは `validated_for_task` を自動で `True` にしない。

別の評価工程で正解付きデータを検証したときだけ更新する。

この小さな制約だけで、次の誤推論を防げる。

```text
importできた
  != 対象入力で動く
  != 対象ドメインに適合する
  != 意思決定に使ってよい
```

## 10. まとめ

外部のML/NLPライブラリを未知言語へ持ち込むとき、一番欲しいのは最初から精度値ではない。

まず必要なのは、**どこまで確認できたかを壊さず残す検証契約**である。

1. 依存関係とモデルが読み込める
2. 対象入力で実行できる
3. 対象用途で意味的に検証されている

この3つを分離し、前段の成功を後段の成功へ昇格させない。

今回の実runは1段目で止まった。そのため日本語対応・非対応については結論を出していない。この「結論を出さない」を機械可読なstatusとして残せること自体が、互換性probeの重要な成果だと思う。
