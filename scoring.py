# scoring.py - Module to calculate compliance scores

from typing import List
from evaluator import RuleResult

def calculate_basic_score(results: List[RuleResult]) -> dict:
    """Calculate the basic score: percentage of passed rules."""
    passed_count = sum(1 for r in results if r.status == "PASS")
    failed_count = len(results) - passed_count
    total = len(results)
    score_percent = round((passed_count / total) * 100) if total > 0 else 0
    return {
        "passed": passed_count,
        "failed": failed_count,
        "total": total,
        "score_percent": score_percent
    }

def calculate_weighted_score(results: List[RuleResult], weights: dict = None) -> dict:
    """
    Calculate weighted score based on severity inferred from title or compliance.
    By default, weights: critical=3, high=2, medium=1, low=1.
    Infers severity by keywords in title (e.g., 'password' -> critical).
    """
    if weights is None:
        weights = {'critical': 3, 'high': 2, 'medium': 1, 'low': 1}

    def infer_severity(rule: RuleResult) -> str:
        title_lower = rule.title.lower()
        if any(word in title_lower for word in ['password', 'encryption', 'audit', 'privilege', 'admin']):
            return 'critical'
        elif any(word in title_lower for word in ['firewall', 'network', 'service', 'registry']):
            return 'high'
        elif any(word in title_lower for word in ['logon', 'screen', 'update']):
            return 'medium'
        else:
            return 'low'

    total_weight = 0
    passed_weight = 0
    for r in results:
        severity = infer_severity(r)
        weight = weights.get(severity, 1)
        total_weight += weight
        if r.status == "PASS":
            passed_weight += weight

    score_percent = round((passed_weight / total_weight) * 100) if total_weight > 0 else 0
    return {
        "passed_weight": passed_weight,
        "total_weight": total_weight,
        "score_percent": score_percent
    }