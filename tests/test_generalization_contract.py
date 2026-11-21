from __future__ import annotations

import unittest

from pipeline import editorial


class GeneralizationContractTests(unittest.TestCase):
    def topic(self) -> dict[str, object]:
        return {
            "title": "同じ成功例を別案件へ移す前に、何を確認すべきか？",
            "title_options": {
                "general_problem": "同じ成功例を別案件へ移す前に、何を確認すべきか？",
                "concrete_anomaly": "1件では成功した。でも別案件へそのまま移せない理由が3つあった",
                "searchable": "成功例を別案件へ移す前に確認する：transfer conditionsの書き方",
            },
            "central_question": "一つの成功例から、どこまで別案件へ判断を移せるのか？",
            "surprising_finding": "成功した手順より、成功条件と不適用条件を残す方が再利用に効いた",
            "initial_hypothesis": "同じtoolなら同じ手順を再利用できる",
            "hypothesis_update": "入力境界と失敗条件が異なると同じ手順でも判断が変わると分かった",
            "stakes": "成功例の過剰一般化による手戻りを減らせる",
            "story_type": "counterintuitive-result",
            "evidence_urls": [
                "https://github.com/KAFKA2306/articles/issues/161",
                "https://github.com/KAFKA2306/articles/blob/main/pipeline/contracts/article.md",
            ],
            "why_interesting": "手順の再利用より適用境界の再利用が重要だった",
            "reader_before": "成功例を見つけても自分の案件へそのまま適用してよいか判断できない",
            "reader_after": "条件を比較し、適用・追加検証・不適用を判断できる",
            "design_philosophy": "一般化の広さより証拠境界を優先する",
            "why_this_article": "単一事例を一般化するときの失敗境界を実装契約として検証する",
            "proof_of_value": "candidate gateとpublication blockerを同じcontractで検証する",
            "desired_reader_action": "自分の事例をdecision ruleと適用条件の表へ変換して比較する",
            "non_goal": "単一事例から普遍的なbest practiceを証明しない",
            "generalizable_insight": "同じ手順をコピーするな。適用条件と失敗境界を先に確認せよ",
            "mechanism": "成功時の入力境界を省略すると、別の失敗条件で同じ処理を誤用してしまう",
            "falsification_condition": "同条件の再試験で無条件の手順コピーの方が失敗を減らすと確認したら撤回する",
            "transfer_conditions": "同じ目的で入力・観測可能性・失敗コストを比較できる案件",
            "non_transfer_conditions": "安全性や外部制約が異なり、同じ失敗を許容できない案件",
            "alternatives": [
                {"kind": kind, "name": kind, "reader_job": "same reader task",
                 "primary_urls": ["https://github.com/KAFKA2306/articles"], "tradeoff": "time versus accuracy"}
                for kind in ("incumbent", "direct", "adjacent")
            ],
            "unsearched_scope": "unexamined alternatives",
            "alternative_decision": {"verdict": "unresolved"},
        }

    def test_story_ready_requires_all_generalization_fields(self) -> None:
        self.assertTrue(editorial.story_ready(self.topic()))
        for field in (
            "generalizable_insight",
            "mechanism",
            "falsification_condition",
            "transfer_conditions",
            "non_transfer_conditions",
        ):
            candidate = self.topic()
            candidate[field] = ""
            with self.subTest(field=field):
                self.assertFalse(editorial.story_ready(candidate))


if __name__ == "__main__":
    unittest.main()
