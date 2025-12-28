# File: parser.py

import os
import glob
import yaml
from typing import List
from sca_structs import SCAFile, Rule, PolicyBlock, RequirementsBlock

def load_sca_file(file_path: str) -> SCAFile:
    """Parse a single .yml file into an SCAFile object."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    sca = SCAFile()

    # Fill 'policy' block
    policy_data = data.get("policy", {})
    sca.policy.id = policy_data.get("id", "")
    sca.policy.file = policy_data.get("file", "")
    sca.policy.name = policy_data.get("name", "")
    sca.policy.description = policy_data.get("description", "")
    sca.policy.references = policy_data.get("references", [])

    # Fill 'requirements' block
    req_data = data.get("requirements", {})
    sca.requirements.title = req_data.get("title", "")
    sca.requirements.description = req_data.get("description", "")
    sca.requirements.condition = req_data.get("condition", "all")
    sca.requirements.rules = req_data.get("rules", [])

    # Fill 'checks' array
    checks_data = data.get("checks", [])
    sca.checks = []
    for item in checks_data:
        rule_obj = Rule(
            id=item.get("id", 0),
            title=item.get("title", ""),
            description=item.get("description", ""),
            rationale=item.get("rationale", ""),
            remediation=item.get("remediation", ""),
            compliance=item.get("compliance", []),
            references=item.get("references", []),
            condition=item.get("condition", "all"),
            rules=item.get("rules", [])
        )
        sca.checks.append(rule_obj)

    return sca

def load_all_rules(rules_dir: str) -> List[Rule]:
    """
    Finds all .yml files in rules_dir, parses each into SCAFile,
    and merges the checks into a single list of Rule objects.
    """
    pattern = os.path.join(rules_dir, "*.yml")
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f"No .yml files found in {rules_dir}")

    all_rules = []
    for file_path in files:
        sca_file = load_sca_file(file_path)
        # We only append the "checks" from each file, ignoring policy/requirements
        all_rules.extend(sca_file.checks)

    return all_rules
