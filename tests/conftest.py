"""Shared fixtures for the WinSecureAuditor test suite.

Puts the repository root on sys.path so the flat module layout
(parser, evaluator, executor, ...) imports cleanly under pytest.
"""

import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from evaluator import RuleResult  # noqa: E402
from sca_structs import Rule  # noqa: E402


@pytest.fixture()
def make_rule():
    """Factory building a minimal Rule with sensible defaults."""

    def _make(**overrides):
        defaults = dict(
            id=10001,
            title="Ensure hypothetical setting is configured",
            description="Long description of the check.",
            rationale="Why this matters.",
            remediation="How to fix it.",
            compliance=[{"cis": ["1.1.1"]}],
            references=["https://example.com/benchmark"],
            condition="all",
            rules=["f:C:\\some\\file.dll -> exists"],
        )
        defaults.update(overrides)
        return Rule(**defaults)

    return _make


@pytest.fixture()
def make_result():
    """Factory building a RuleResult with sensible defaults."""

    def _make(**overrides):
        defaults = dict(
            rule_id=10001,
            title="Ensure hypothetical setting is configured",
            status="PASS",
            details="1/1 sub-rules passed",
            description="Long description of the check.",
            rationale="Why this matters.",
            remediation="How to fix it.",
            compliance=[{"cis": ["1.1.1"]}],
            condition="all",
        )
        defaults.update(overrides)
        return RuleResult(**defaults)

    return _make


MINIMAL_YML = """\
policy:
  id: "test_policy"
  file: "test.yml"
  name: "Test Policy"
  description: "Policy used by the automated test suite."
  references:
    - https://example.com/policy
requirements:
  title: "Test requirements"
  description: "Only runs on test machines."
  condition: all
  rules:
    - 'c:echo test -> r:ok'
checks:
  - id: 20001
    title: "Ensure required helper file is present"
    description: "Helper file must exist."
    rationale: "The helper is required."
    remediation: "Restore the helper file."
    compliance:
      - cis: ["2.3.1.2"]
    references:
      - https://example.com/check
    condition: all
    rules:
      - 'f:{required_file} -> exists'
  - id: 20002
    title: "Ensure legacy binary is absent"
    description: "Legacy binary must not exist."
    rationale: "The binary is deprecated."
    remediation: "Delete the binary."
    compliance: []
    references: []
    condition: all
    rules:
      - 'f:{forbidden_file} -> missing'
"""


@pytest.fixture()
def rules_dir(tmp_path):
    """A rules directory with two portable checks backed by tmp files.

    * check 20001 PASSES (required file exists)
    * check 20002 PASSES (forbidden file is missing)
    """
    required_file = tmp_path / "required_helper.txt"
    required_file.write_text("helper", encoding="utf-8")
    forbidden_file = tmp_path / "legacy_binary.dll"

    sub = str(tmp_path / "rules")
    os.makedirs(sub, exist_ok=True)
    content = MINIMAL_YML.format(
        required_file=str(required_file).replace("\\", "\\\\"),
        forbidden_file=str(forbidden_file).replace("\\", "\\\\"),
    )
    with open(os.path.join(sub, "test_rules.yml"), "w", encoding="utf-8") as fh:
        fh.write(content)
    return sub
