# scanner.py - Module to handle loading, execution and evaluation of SCA rules

import os
import logging
from typing import List
from parser import load_all_rules
from executor import execute_subrule
from evaluator import evaluate_rule, RuleResult
from scoring import calculate_basic_score, calculate_weighted_score

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Scanner:
    def __init__(self, rules_dir: str):
        self.rules_dir = rules_dir
        self.rules = []
        self.results = []

    def load_rules(self) -> None:
        """Load all rules from the specified directory."""
        try:
            self.rules = load_all_rules(self.rules_dir)
            logging.info(f"Loaded {len(self.rules)} rules from {self.rules_dir}")
        except Exception as e:
            logging.error(f"Error loading rules: {e}")
            raise

    def execute_and_evaluate(self, batch_size: int = 50) -> None:
        """Execute and evaluate all loaded rules in batches to optimize memory."""
        self.results = []
        for i in range(0, len(self.rules), batch_size):
            batch = self.rules[i:i + batch_size]
            logging.info(f"Processing batch {i//batch_size + 1} of {len(batch)} rules")
            for rule in batch:
                exec_results = []
                for sub_rule in rule.rules:
                    r_exec = execute_subrule(sub_rule)
                    exec_results.append(r_exec)

                r_result = evaluate_rule(rule, exec_results)
                self.results.append(r_result)
                logging.debug(f"Evaluated rule {rule.id}: {r_result.status}")
            # Free memory of processed batch
            del batch

    def get_summary(self, weighted: bool = False) -> dict:
        """Return a summary of the results. If weighted=True, use weighted score."""
        if weighted:
            weighted_summary = calculate_weighted_score(self.results)
            return {
                "passed": sum(1 for r in self.results if r.status == "PASS"),
                "failed": len(self.results) - sum(1 for r in self.results if r.status == "PASS"),
                "total": len(self.results),
                "score_percent": weighted_summary["score_percent"],
                "weighted": True
            }
        else:
            basic_summary = calculate_basic_score(self.results)
            return basic_summary

    def run_scan(self) -> List[RuleResult]:
        """Execute the complete scan and return the results."""
        self.load_rules()
        self.execute_and_evaluate()
        summary = self.get_summary()
        logging.info(f"Scan completed: {summary['passed']} passed, {summary['failed']} failed, Score: {summary['score_percent']}%")
        return self.results