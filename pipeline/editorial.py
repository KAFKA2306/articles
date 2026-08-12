from __future__ import annotations

import json
from typing import Callable

from . import core

TECHNICAL_AXES = [
    "logic",
    "utility",
    "readability",
    "originality",
    "clarity",
]
EDITORIAL_AXES = [
    "interest",
    "discovery",
    "narrative",
    "context",
]
STORY_FIELDS = [
    "central_question",
    "surprising_finding",
    "initial_hypothesis",
    "hypothesis_update",
    "stakes",
    "story_type",
    "evidence_urls",
    "why_interesting",
]
PREMATURE_CONCLUSION_MARKERS = (
    "結論はこれです",
    "結論は単純です",
    "この記事で伝えたい結論は一つです",
    "この記事で伝えたい結論は1つです",
)


def _score(value: object) -> float:
    try:
        return max(0.0, min(5.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def opening_has_premature_conclusion(
    article: str,
    *,
    char_limit: int = 800,
) -> bool:
    opening = article[:char_limit]
    return any(marker in opening for marker in PREMATURE_CONCLUSION_MARKERS)


def story_ready(topic: dict[str, object]) -> bool:
    if any(not topic.get(key) for key in STORY_FIELDS):
        return False
    if str(topic.get("story_type")) not in set(core.CONFIG["story_types"]):
        return False
    urls = topic.get("evidence_urls")
    return isinstance(urls, list) and len(urls) >= 2


def choose_topic(signals: list[dict[str, object]]) -> dict[str, object]:
    user = f"""
公開GitHubシグナルから記事候補を{core.CONFIG['candidate_count']}件作り、
最も強い1件を選んでください。

記事は技術用語の解説から始めません。各候補は、実装やデータを追った結果として
見つかる一つの現象を主役にしてください。候補の種類は次のいずれかです。
{json.dumps(core.CONFIG['story_types'], ensure_ascii=False)}

必須条件:
- 一つの候補につき、一つの問いと一つの発見だけを置く。
- `surprising_finding` はPUBLIC_GITHUB_SIGNALSから検証できる事実だけにする。
- 単なる生成ミス、URL間違い、設定漏れだけで終わる題材は選ばない。
- 専門用語そのものではなく、数値、挙動、失敗、矛盾、桁差、予想外の接続を主役にする。
- 既存記事の焼き直しは禁止する。
- 証拠が弱い候補は捨てる。面白そうという理由で事実を補わない。
- 既知のベストプラクティスを別の技術へ適用しただけの `gap spotting` は選ばない。
- 読者の自然な予想または既存前提が、一次証拠によってどう崩れるかを明示できない候補は落とす。
- `why_interesting` が「役に立つ」「安全になる」「理解しやすい」の言い換えだけなら落とす。
- 文章を上手く書けば面白くなりそう、ではなく、事実そのものに読む理由がある候補だけを残す。

既存タイトル:
{json.dumps(core.existing_titles(), ensure_ascii=False)}

PUBLIC_GITHUB_SIGNALS:
{json.dumps(signals, ensure_ascii=False, indent=2)}

各候補を次の形にしてください。
{{
  "title": "技術名ではなく現象または問いを中心にした仮タイトル",
  "central_question": "一文の問い",
  "surprising_finding": "一文の発見",
  "initial_hypothesis": "調査前に自然だった予想",
  "hypothesis_update": "何を見て予想が変わるか",
  "stakes": "なぜ確かめる価値があるか",
  "story_type": "anomaly|contradiction|failure|unexpected-connection|counterintuitive-result|magnitude",
  "evidence_urls": ["https://github.com/KAFKA2306/...", "https://github.com/KAFKA2306/..."],
  "why_interesting": "この題材固有の面白さ。どの前提がどう裏切られるかまで書く",
  "technical_payoff": "最後に一般化できる技術知見"
}}

JSONのみ返してください。
{{"selected": {{...}}, "alternatives": [{{...}}]}}
"""
    result = json.loads(
        core.model_call(
            "あなたは事実検証を優先する技術編集者です。弱い問いを文章力で救済せず、前提を更新する強い問いと一つの発見で記事を選びます。文体模倣はしません。",
            user,
            temperature=0.0,
            json_mode=True,
        )
    )
    selected = result.get("selected")
    if not isinstance(selected, dict) or not story_ready(selected):
        raise RuntimeError("topic selection did not produce a story-ready candidate")
    return result


def enrich_topic(
    topic: dict[str, object],
    signals: list[dict[str, object]],
) -> dict[str, object]:
    if story_ready(topic):
        return topic

    user = f"""
既に選ばれた技術テーマを、そのまま説明記事にせず、
公開証拠で検証できる一つの発見へ絞り直してください。

重要:
- 元テーマにない事実を創作しない。
- PUBLIC_GITHUB_SIGNALSで支えられない発見は採用しない。
- 単なる生成ミス、URL間違い、設定漏れだけの話にはしない。
- 既知の原則を別技術へ適用しただけなら `publishable` を false にする。
- 読者の自然な予想・既存前提を何も更新しない場合は `publishable` を false にする。
- 十分な発見を作れない場合は `publishable` を false にする。

元テーマ:
{json.dumps(topic, ensure_ascii=False, indent=2)}

PUBLIC_GITHUB_SIGNALS:
{json.dumps(signals, ensure_ascii=False, indent=2)}

JSONのみ返してください。
{{
  "publishable": true,
  "title": "...",
  "central_question": "...",
  "surprising_finding": "...",
  "initial_hypothesis": "...",
  "hypothesis_update": "...",
  "stakes": "...",
  "story_type": "anomaly|contradiction|failure|unexpected-connection|counterintuitive-result|magnitude",
  "evidence_urls": ["...", "..."],
  "why_interesting": "...",
  "technical_payoff": "..."
}}
"""
    result = json.loads(
        core.model_call(
            "あなたは技術テーマを一つの検証可能な発見へ絞る編集者です。問いが弱ければ公開不可にします。",
            user,
            temperature=0.0,
            json_mode=True,
        )
    )
    if result.get("publishable") is not True or not story_ready(result):
        raise RuntimeError("topic could not be converted into a story-ready candidate")
    return result


def draft_article(
    topic: dict[str, object],
    signals: list[dict[str, object]],
) -> str:
    shaped = enrich_topic(topic, signals)
    user = f"""
以下の契約に従って日本語の完成記事を書いてください。
Markdown本文のみ。front matterは不要です。

{core.PROMPT}

記事の核:
{json.dumps(shaped, ensure_ascii=False, indent=2)}

利用可能な公開一次証拠:
{json.dumps(signals, ensure_ascii=False, indent=2)}

必須:
- 最初の具体物を、一般論・用語定義・アーキテクチャ説明より前に置く。
- 冒頭はscene、実測値、失敗ログ、差分、予想外の挙動のいずれかから始める。
- `central_question` を冒頭500文字以内で自然に成立させる。
- 冒頭500文字では最終結論を完全に閉じない。読者に一つの未解決状態を残す。
- `結論はこれです`、`結論は単純です`、`この記事で伝えたい結論は一つです` のような結論先出し定型句を使わない。
- `initial_hypothesis` を置き、観測や実験で `hypothesis_update` へ進む。
- `surprising_finding` 以外の論点を主役にしない。
- 公開URLを冒頭で一覧化しない。証拠は、その事実を使う位置へ置く。
- 技術用語は必要になった位置で短く説明する。
- 固有名詞は役割が分かる一文を添える。
- GitHub上で確認できない実装事実を創作しない。
- 外部仕様を断定する場合は公式一次情報URLを直後に付ける。
- URLを確信できない場合、その外部仕様自体を削除する。
- 中心の問いを前進させない正しい節は削る。網羅性を目的にしない。
- 最後に一文の持ち帰りを置く。
- 最後に「一次情報・再現証拠」節を設け、本文で実際に使ったURLだけを列挙する。
- 最低でもKAFKA2306 GitHub URLを2件、外部の公式一次情報を1件含める。
"""
    return core.model_call(
        "あなたは調査の過程を読者が追体験できる技術ライターです。正確さと面白さを両立し、具体的なsceneから始め、文体模倣はしません。",
        user,
    )


def evaluate(article: str) -> dict[str, object]:
    user = f"""
この記事を厳格に評価してください。0.0〜5.0です。

技術品質:
- logic
- utility
- readability
- originality
- clarity

編集品質:
- interest: 冒頭から続きを知りたくなる未解決の問い・意外性・具体性があるか
- discovery: 一つの検証可能な発見へ記事全体が収束しているか
- narrative: scene→自然な予想→観測/実験→仮説更新→結論の因果が通るか
- context: 本文だけで固有名詞・数値・技術の意味を追えるか

甘く採点しないでください。
LAPRAS相当の技術品質は「他のエンジニアに役立つか」の品質床であり、面白さの代理ではありません。
技術的に正しくても、次の場合は `interest` を3.5以下にしてください。
- 用語説明や一般論がsceneより先行する。
- 冒頭で記事全体の最終結論を閉じ、続きを読む必要をなくしている。
- タイトル相当の主張を予想通り説明するだけで、前提更新がない。
- 既知のベストプラクティスを別技術へ適用しただけのgap spottingである。
- repository / PR / URLの列挙が具体的事件より先に来る。
- 説明書としては有用だが、この著者の実測・失敗・判断変更がなくても成立する。

具体物が遅い、論点が散る、結論が予想通り、導入を読んでも続きを知りたくならない場合は編集品質を下げてください。
クリックを誘うだけで本文が回収しない場合も `interest` を下げてください。
100+人気記事の文体を模倣したかではなく、scene before concept、具体的結果、実測、著者固有の経験、制約開示という編集原理が素材に根ざしているかを見てください。

{core.PROMPT}

ARTICLE:
{article}

JSONのみ返してください。
{{
  "logic": 0.0,
  "utility": 0.0,
  "readability": 0.0,
  "originality": 0.0,
  "clarity": 0.0,
  "interest": 0.0,
  "discovery": 0.0,
  "narrative": 0.0,
  "context": 0.0,
  "blocking_issues": [],
  "revision_actions": []
}}
"""
    result = json.loads(
        core.model_call(
            "あなたは独立した技術記事の編集査読者です。正確さ・有用性と、実際に読み進めたくなる構造を別々に採点します。",
            user,
            temperature=0.0,
            json_mode=True,
        )
    )
    for key in TECHNICAL_AXES + EDITORIAL_AXES:
        result[key] = _score(result.get(key, 0.0))

    if opening_has_premature_conclusion(article):
        result["interest"] = min(_score(result.get("interest")), 3.4)
        blocking = result.get("blocking_issues")
        if not isinstance(blocking, list):
            blocking = []
        if "premature_conclusion_in_opening" not in blocking:
            blocking.append("premature_conclusion_in_opening")
        result["blocking_issues"] = blocking

    result["overall"] = round(
        sum(result[key] for key in TECHNICAL_AXES) / len(TECHNICAL_AXES),
        3,
    )
    result["story_overall"] = round(
        sum(result[key] for key in EDITORIAL_AXES) / len(EDITORIAL_AXES),
        3,
    )
    result["evaluation_kind"] = str(
        core.CONFIG.get("evaluation_kind", "internal_lapras_rubric_proxy")
    )
    result["editorial_evaluation_kind"] = str(
        core.CONFIG.get("editorial_evaluation_kind", "story_interest_proxy")
    )
    return result


def aggregate_evaluations(
    article: str,
    *,
    rounds: int = 3,
) -> dict[str, object]:
    reviews = [evaluate(article) for _ in range(rounds)]
    keys = TECHNICAL_AXES + EDITORIAL_AXES + ["overall", "story_overall"]
    aggregate: dict[str, object] = {
        "reviews": reviews,
        "evaluation_kind": str(
            core.CONFIG.get("evaluation_kind", "internal_lapras_rubric_proxy")
        ),
        "editorial_evaluation_kind": str(
            core.CONFIG.get("editorial_evaluation_kind", "story_interest_proxy")
        ),
    }
    for key in keys:
        values = sorted(_score(review.get(key, 0.0)) for review in reviews)
        aggregate[key] = values[len(values) // 2]
    aggregate["blocking_issues"] = list(
        dict.fromkeys(
            issue
            for review in reviews
            for issue in review.get("blocking_issues", [])
            if isinstance(issue, str)
        )
    )
    aggregate["revision_actions"] = list(
        dict.fromkeys(
            action
            for review in reviews
            for action in review.get("revision_actions", [])
            if isinstance(action, str)
        )
    )
    return aggregate


def passes_quality(review: dict[str, object], sources_ok: bool) -> bool:
    gate = core.CONFIG["quality_gate"]
    blocking = review.get("blocking_issues", [])
    if isinstance(blocking, list) and "premature_conclusion_in_opening" in blocking:
        return False
    return bool(
        sources_ok
        and _score(review.get("overall")) >= float(gate["minimum_overall"])
        and all(
            _score(review.get(key)) >= float(gate["minimum_axis"])
            for key in TECHNICAL_AXES
        )
        and _score(review.get("story_overall"))
        >= float(gate["minimum_story_overall"])
        and all(
            _score(review.get(key)) >= float(gate["minimum_story_axis"])
            for key in EDITORIAL_AXES
        )
        and _score(review.get("interest")) >= float(gate["minimum_interest"])
    )


def revise(
    article: str,
    review: dict[str, object],
    source_report: dict[str, object],
) -> str:
    user = f"""
以下の記事を全面改稿してください。
文章量を増やすことではなく、問い・発見・因果を強くすることが目的です。
Markdown本文のみ返してください。

品質契約:
{core.PROMPT}

査読結果:
{json.dumps(review, ensure_ascii=False, indent=2)}

一次情報検証:
{json.dumps(source_report, ensure_ascii=False, indent=2)}

ARTICLE:
{article}

改稿規則:
- `interest` が弱い場合、抽象的な導入を削り、具体的なscene・数値・失敗から始める。
- 冒頭に最終結論がある場合、それを削り、自然な予想と予想外の観測の差へ置き換える。
- `discovery` が弱い場合、最も強い一つ以外の論点を削る。
- `narrative` が弱い場合、scene→予想→観測→更新→結論の因果順に組み直す。
- `context` が弱い場合、必要な固有名詞だけをその場で一文説明する。
- URL一覧がsceneより先にある場合、URLを事実の使用箇所へ移す。
- 中心の問いを前進させない正しい節を削る。網羅性を増やさない。
- 既知のベストプラクティス適用だけで問いが弱い場合、無理に文章で救済せずblocking issueを残す。
- 存在確認できないURL・断定・数値は削除する。
- 面白さのために新しい事実を作らない。
- 最後を一文の持ち帰りで閉じる。
"""
    return core.model_call(
        "あなたは記事の論点を削って強くするリビジョン担当です。冒頭の答えを消してsceneと問いを前に出します。",
        user,
        temperature=0.0,
    )


def install_editorial_pipeline() -> None:
    replacements: dict[str, Callable[..., object]] = {
        "choose_topic": choose_topic,
        "draft_article": draft_article,
        "evaluate": evaluate,
        "aggregate_evaluations": aggregate_evaluations,
        "passes_quality": passes_quality,
        "revise": revise,
    }
    for name, func in replacements.items():
        setattr(core, name, func)
