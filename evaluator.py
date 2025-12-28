# File: evaluator.py

import re
from typing import List
from executor import ExecResult
from sca_structs import Rule

class RuleResult:
    """
    Holds the final pass/fail status plus the original rule data
    so we can display it in reports without hardcoding.
    """
    def __init__(
        self,
        rule_id: int,
        title: str,
        status: str,
        details: str,
        description: str,
        rationale: str,
        remediation: str,
        compliance,
        condition: str
    ):
        self.rule_id = rule_id
        self.title = title
        self.status = status       # "PASS" or "FAIL"
        self.details = details     # e.g. "2/2 sub-rules passed"
        self.description = description
        self.rationale = rationale
        self.remediation = remediation
        self.compliance = compliance
        self.condition = condition

def evaluate_rule(rule: Rule, exec_results: List[ExecResult]) -> RuleResult:
    """
    Evaluate pass/fail for the given 'rule' based on the sub-rule results in exec_results.
    Then create a RuleResult that includes all relevant fields from the original Rule.
    """
    passed_subrules = 0
    fail_reasons = []
    total = len(exec_results)

    # Evaluate each sub-rule
    for r in exec_results:
        sub_pass, reason = evaluate_subrule(r)
        if sub_pass:
            passed_subrules += 1
        else:
            fail_reasons.append(f"[{r.sub_rule}] {reason}")

    # Condition logic
    cond = rule.condition.lower() if rule.condition else "all"
    if cond == "all":
        passed = (passed_subrules == total)
    elif cond == "any":
        passed = (passed_subrules > 0)
    elif cond == "none":
        passed = (passed_subrules == 0)
    else:
        passed = (passed_subrules == total)

    status = "PASS" if passed else "FAIL"
    if not passed and fail_reasons:
        details = "; ".join(fail_reasons)
    else:
        details = f"{passed_subrules}/{total} sub-rules passed"

    # Build a RuleResult with original fields from 'rule'
    return RuleResult(
        rule_id=rule.id,
        title=rule.title,
        status=status,
        details=details,
        description=rule.description,
        rationale=rule.rationale,
        remediation=rule.remediation,
        compliance=rule.compliance,
        condition=rule.condition
    )

def evaluate_subrule(exec_result: ExecResult) -> (bool, str):
    """
    Compare the ExecResult value with any expected pattern in the sub_rule
    (like -> exists, -> missing, -> regex:^...).
    Return (passOrFail, reason).
    """
    if exec_result.error:
        return False, exec_result.error  # e.g. registry or command error

    sub_rule = exec_result.sub_rule.lower()
    val = exec_result.value

    # Example checks
    if "-> exists" in sub_rule:
        if val == "exists":
            return True, "file found"
        return False, f"file not found ({val})"

    if "-> missing" in sub_rule:
        if val == "missing":
            return True, "file is missing"
        return False, f"file is present ({val})"

    # Regex check: e.g. -> regex:^Windows 10
    match = re.search(r"->\s*regex:(.+)$", sub_rule)
    if match:
        pattern = match.group(1).strip()
        if re.match(pattern, val):
            return True, "regex matched"
        else:
            return False, f"regex '{pattern}' did not match '{val}'"

    # Default: pass if no specific logic recognized
    return True, "no condition recognized"
