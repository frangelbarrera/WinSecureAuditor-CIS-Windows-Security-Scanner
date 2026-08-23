"""Regression tests: Wazuh short-form '-> r:' regex sub-rules.

The bundled CIS rule files use the short ``-> r:<pattern>`` suffix for regex
comparisons (69 sub-rules across the shipped benchmarks), while the evaluator
only recognised the long ``-> regex:`` form. Unrecognised comparisons fell
through to the default branch and reported PASS without evaluating anything.

These tests pin the corrected behaviour and must never regress.
"""

from executor import ExecResult
from evaluator import evaluate_subrule


def exec_result(sub_rule, value="", error=""):
    return ExecResult(sub_rule=sub_rule, value=value, error=error)


class TestShortRegexPrefix:
    def test_short_r_prefix_matches(self):
        ok, reason = evaluate_subrule(
            exec_result("c:ver -> r:^Windows 10", value="Windows 10 Pro")
        )
        assert ok is True
        assert reason == "regex matched"

    def test_short_r_prefix_no_match(self):
        ok, reason = evaluate_subrule(
            exec_result("c:ver -> r:^Windows 10", value="Linux")
        )
        assert ok is False
        assert "did not match" in reason

    def test_short_r_prefix_on_registry_style_rule(self):
        # Real shape taken from cis_win10_enterprise.yml requirements.
        ok, _ = evaluate_subrule(
            exec_result(
                "r:HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion"
                " -> ProductName -> r:^Windows 10",
                value="Windows 10 Enterprise",
            )
        )
        assert ok is True

    def test_mixed_case_value_matches_case_insensitively(self):
        # The sub-rule is lowercased internally, so the pattern loses its
        # original case; matching must stay case-insensitive both ways.
        ok, _ = evaluate_subrule(
            exec_result("c:ver -> r:^Windows 10", value="windows 10 enterprise")
        )
        assert ok is True

    def test_numeric_registry_value_does_not_crash(self):
        # DWORD registry values arrive as ints; they must be compared as str.
        ok, _ = evaluate_subrule(
            exec_result("r:HKLM\\...\\PasswordHistory -> Size -> r:^24$", value=24)
        )
        assert ok is True

    def test_short_r_prefix_in_the_middle_of_chain(self):
        # The first '->' segment is a value name, not the regex marker.
        ok, _ = evaluate_subrule(
            exec_result("r:HKLM\\... -> ProductName -> r:^Windows", value="Windows 10")
        )
        assert ok is True
