# File: sca_structs.py

from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class PolicyBlock:
    """Represents the 'policy:' section of a Wazuh-style SCA YAML file."""
    id: str = ""
    file: str = ""
    name: str = ""
    description: str = ""
    references: List[str] = field(default_factory=list)

@dataclass
class RequirementsBlock:
    """Represents the 'requirements:' section of a Wazuh-style SCA YAML file."""
    title: str = ""
    description: str = ""
    condition: str = "all"
    rules: List[str] = field(default_factory=list)

@dataclass
class Rule:
    """Represents each item in the 'checks:' array of a Wazuh-style SCA YAML file."""
    id: int = 0
    title: str = ""
    description: str = ""
    rationale: str = ""
    remediation: str = ""
    # compliance is typically a list of maps, e.g. [{cis: ["2.3.1.2"]}, {pci_dss: ["8.1"]}]
    compliance: List[Dict[str, List[str]]] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    condition: str = "all"
    # sub-rules (registry/file/command checks) go here
    rules: List[str] = field(default_factory=list)

@dataclass
class SCAFile:
    """Top-level structure matching Wazuh SCA format: policy, requirements, checks."""
    policy: PolicyBlock = field(default_factory=PolicyBlock)
    requirements: RequirementsBlock = field(default_factory=RequirementsBlock)
    checks: List[Rule] = field(default_factory=list)
