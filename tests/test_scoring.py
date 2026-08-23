"""Tests for basic and weighted compliance scoring."""

from scoring import calculate_basic_score, calculate_weighted_score


class TestBasicScore:
    def test_all_passed(self, make_result):
        s = calculate_basic_score([make_result(status="PASS") for _ in range(4)])
        assert s == {"passed": 4, "failed": 0, "total": 4, "score_percent": 100}

    def test_half_passed_rounds(self, make_result):
        s = calculate_basic_score(
            [make_result(status="PASS"), make_result(status="FAIL")]
        )
        assert s == {"passed": 1, "failed": 1, "total": 2, "score_percent": 50}

    def test_all_failed(self, make_result):
        s = calculate_basic_score([make_result(status="FAIL") for _ in range(3)])
        assert s["passed"] == 0
        assert s["score_percent"] == 0

    def test_empty_results_is_zero_not_crash(self):
        s = calculate_basic_score([])
        assert s == {"passed": 0, "failed": 0, "total": 0, "score_percent": 0}

    def test_rounding_to_nearest_integer(self, make_result):
        # 2/3 -> 66.67 -> 67
        s = calculate_basic_score(
            [make_result(status="PASS"), make_result(status="PASS"), make_result(status="FAIL")]
        )
        assert s["score_percent"] == 67


class TestWeightedScore:
    def test_severity_keywords_drive_weights(self):
        results = [
            # critical (3): password
            dict(rule_id=1, title="Ensure password history size"),
            # high (2): firewall
            dict(rule_id=2, title="Ensure firewall is enabled"),
            # medium (1): screen
            dict(rule_id=3, title="Configure screen lock"),
            # low (1): anything else
            dict(rule_id=4, title="Some other check"),
        ]
        from evaluator import RuleResult

        def rr(title):
            return RuleResult(
                rule_id=1, title=title, status="FAIL", details="",
                description="", rationale="", remediation="",
                compliance=[], condition="all",
            )

        s = calculate_weighted_score([rr(r["title"]) for r in results])
        assert s["total_weight"] == 3 + 2 + 1 + 1
        assert s["passed_weight"] == 0
        assert s["score_percent"] == 0

    def test_passing_critical_counts_more_than_low(self):
        from evaluator import RuleResult

        def rr(title, status):
            return RuleResult(
                rule_id=1, title=title, status=status, details="",
                description="", rationale="", remediation="",
                compliance=[], condition="all",
            )

        # critical passes, low fails -> 3 / 4 = 75%
        s = calculate_weighted_score(
            [rr("Ensure password history size", "PASS"), rr("Misc", "FAIL")]
        )
        assert s["score_percent"] == 75

    def test_all_passed(self):
        from evaluator import RuleResult

        def rr(title):
            return RuleResult(
                rule_id=1, title=title, status="PASS", details="",
                description="", rationale="", remediation="",
                compliance=[], condition="all",
            )

        s = calculate_weighted_score([rr("Ensure audit logging"), rr("Ensure firewall domain profile")])
        assert s["score_percent"] == 100

    def test_custom_weights_override_defaults(self):
        from evaluator import RuleResult

        def rr(title, status):
            return RuleResult(
                rule_id=1, title=title, status=status, details="",
                description="", rationale="", remediation="",
                compliance=[], condition="all",
            )

        s = calculate_weighted_score(
            [rr("Ensure password history size", "PASS")],
            weights={"critical": 10, "high": 5, "medium": 2, "low": 1},
        )
        assert s["total_weight"] == 10
        assert s["passed_weight"] == 10

    def test_empty_results_is_zero_not_crash(self):
        s = calculate_weighted_score([])
        assert s == {"passed_weight": 0, "total_weight": 0, "score_percent": 0}
