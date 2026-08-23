"""Tests for rule and sub-rule evaluation logic."""

from executor import ExecResult
from evaluator import RuleResult, evaluate_rule, evaluate_subrule


def exec_result(sub_rule, value="", error=""):
    return ExecResult(sub_rule=sub_rule, value=value, error=error)


class TestEvaluateSubrule:
    def test_error_fails_with_reason(self):
        ok, reason = evaluate_subrule(exec_result("r:HKLM\\X", error="Registry error: boom"))
        assert ok is False
        assert reason == "Registry error: boom"

    def test_exists_passes_when_file_found(self):
        ok, reason = evaluate_subrule(exec_result("f:C:\\x\\a.dll -> exists", value="exists"))
        assert ok is True
        assert reason == "file found"

    def test_exists_fails_when_file_missing(self):
        ok, reason = evaluate_subrule(exec_result("f:C:\\x\\a.dll -> exists", value="missing"))
        assert ok is False
        assert reason == "file not found (missing)"

    def test_missing_passes_when_file_absent(self):
        ok, reason = evaluate_subrule(exec_result("f:C:\\x\\a.dll -> missing", value="missing"))
        assert ok is True
        assert reason == "file is missing"

    def test_missing_fails_when_file_present(self):
        ok, reason = evaluate_subrule(exec_result("f:C:\\x\\a.dll -> missing", value="exists"))
        assert ok is False
        assert reason == "file is present (exists)"

    def test_longform_regex_prefix_matches(self):
        ok, reason = evaluate_subrule(exec_result("c:ver -> regex:^Windows", value="Windows 10 Pro"))
        assert ok is True
        assert reason == "regex matched"

    def test_longform_regex_prefix_no_match(self):
        ok, reason = evaluate_subrule(exec_result("c:ver -> regex:^Windows", value="Linux"))
        assert ok is False
        assert "did not match" in reason

    def test_unrecognized_condition_passes_by_default(self):
        ok, reason = evaluate_subrule(exec_result("c:ver", value="anything"))
        assert ok is True
        assert reason == "no condition recognized"


class TestEvaluateRuleConditions:
    def test_condition_all_passes_when_every_subrule_passes(self, make_rule):
        results = [
            exec_result("f:a -> exists", value="exists"),
            exec_result("f:b -> missing", value="missing"),
        ]
        rr = evaluate_rule(make_rule(condition="all"), results)
        assert rr.status == "PASS"
        assert rr.details == "2/2 sub-rules passed"

    def test_condition_all_fails_when_one_subrule_fails(self, make_rule):
        results = [
            exec_result("f:a -> exists", value="exists"),
            exec_result("f:b -> exists", value="missing"),
        ]
        rr = evaluate_rule(make_rule(condition="all"), results)
        assert rr.status == "FAIL"
        assert "[f:b -> exists] file not found (missing)" in rr.details

    def test_condition_any_passes_with_single_success(self, make_rule):
        results = [
            exec_result("f:a -> exists", value="missing"),
            exec_result("f:b -> exists", value="exists"),
        ]
        rr = evaluate_rule(make_rule(condition="any"), results)
        assert rr.status == "PASS"

    def test_condition_any_fails_when_nothing_passes(self, make_rule):
        results = [exec_result("f:a -> exists", value="missing")]
        rr = evaluate_rule(make_rule(condition="any"), results)
        assert rr.status == "FAIL"

    def test_condition_none_passes_when_nothing_passes(self, make_rule):
        results = [exec_result("f:a -> exists", value="missing")]
        rr = evaluate_rule(make_rule(condition="none"), results)
        assert rr.status == "PASS"

    def test_condition_none_fails_when_something_passes(self, make_rule):
        results = [exec_result("f:a -> exists", value="exists")]
        rr = evaluate_rule(make_rule(condition="none"), results)
        assert rr.status == "FAIL"

    def test_unknown_condition_behaves_like_all(self, make_rule):
        results = [
            exec_result("f:a -> exists", value="exists"),
            exec_result("f:b -> exists", value="missing"),
        ]
        rr = evaluate_rule(make_rule(condition="sometimes"), results)
        assert rr.status == "FAIL"

    def test_empty_condition_defaults_to_all(self, make_rule):
        results = [exec_result("f:a -> exists", value="exists")]
        rr = evaluate_rule(make_rule(condition=""), results)
        assert rr.status == "PASS"

    def test_no_subrules_documents_current_behaviour(self, make_rule):
        """An 'all' rule with zero sub-rules currently evaluates as PASS."""
        rr = evaluate_rule(make_rule(condition="all"), [])
        assert rr.status == "PASS"
        assert rr.details == "0/0 sub-rules passed"

    def test_error_subrule_marks_rule_failed(self, make_rule):
        results = [exec_result("r:HKLM\\X", error="Registry check not supported")]
        rr = evaluate_rule(make_rule(), results)
        assert rr.status == "FAIL"
        assert "Registry check not supported" in rr.details


class TestRuleResultConstruction:
    def test_fields_carry_the_original_rule(self, make_rule):
        rule = make_rule()
        rr = evaluate_rule(rule, [exec_result(rule.rules[0], value="exists")])
        assert isinstance(rr, RuleResult)
        assert rr.rule_id == rule.id
        assert rr.title == rule.title
        assert rr.description == rule.description
        assert rr.rationale == rule.rationale
        assert rr.remediation == rule.remediation
        assert rr.compliance == rule.compliance
        assert rr.condition == rule.condition
