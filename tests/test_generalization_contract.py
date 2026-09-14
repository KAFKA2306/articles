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
            "generalizable_insight": "手順ではなく、判断を成立させる条件と失敗境界を再利用単位にする",
            "transfer_conditions": "同じ目的で入力・観測可能性・失敗コストを比較できる案件",
            "non_transfer_conditions": "安全性や外部制約が異なり、同じ失敗を許容できない案件",
        }

    def test_story_ready_requires_all_generalization_fields(self) -> None:
        self.assertTrue(editorial.story_ready(self.topic()))
        for field in (
            "generalizable_insight",
            "transfer_conditions",
            "non_transfer_conditions",
        ):
            candidate = self.topic()
            candidate[field] = ""
            with self.subTest(field=field):
                self.assertFalse(editorial.story_ready(candidate))

    def test_single_case_can_pass_when_transfer_boundary_is_explicit(self) -> None:
        candidate = self.topic()
        candidate["generalizable_insight"] = (
            "単一事例でも、観測したmechanismと適用境界を分離すれば限定的な判断規則として再利用できる"
        )
        candidate["transfer_conditions"] = "同じmechanismを観測できる場合に限る"
        candidate["non_transfer_conditions"] = "未観測のpopulationや異なるfailure modeへは拡張しない"
        self.assertTrue(editorial.story_ready(candidate))

    def test_generalization_blockers_are_publication_blockers(self) -> None:
        passing = {
            "logic": 5.0,
            "utility": 5.0,
            "readability": 5.0,
            "originality": 5.0,
            "clarity": 5.0,
            "overall": 5.0,
            "interest": 5.0,
            "discovery": 5.0,
            "narrative": 5.0,
            "context": 5.0,
            "story_overall": 5.0,
        }
        for issue in editorial.GENERALIZATION_BLOCKING_ISSUES:
            review = dict(passing)
            review["blocking_issues"] = [issue]
            with self.subTest(issue=issue):
                self.assertFalse(editorial.passes_quality(review, sources_ok=True))

    def test_prompt_and_review_contract_name_required_fields_and_blockers(self) -> None:
        source = (editorial.core.ROOT / "pipeline" / "editorial.py").read_text(
            encoding="utf-8"
        )
        for field in (
            "generalizable_insight",
            "transfer_conditions",
            "non_transfer_conditions",
        ):
            self.assertIn(field, source)
        for issue in (
            "case_specific_without_transfer",
            "unclear_transfer_conditions",
            "overgeneralized_from_narrow_evidence",
        ):
            self.assertIn(issue, source)
        self.assertIn("decision rule", source)
        self.assertIn("comparison lens", source)
        self.assertIn("experiment protocol", source)


if __name__ == "__main__":
    unittest.main()
