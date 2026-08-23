"""Tests for the YAML rule parser."""

import os

import pytest

from parser import load_all_rules, load_sca_file

VALID_YML = """\
policy:
  id: "cis_test"
  file: "cis_test.yml"
  name: "CIS Test Benchmark"
  description: "Benchmark for tests."
  references:
    - https://www.cisecurity.org/cis-benchmarks/
requirements:
  title: "Check the platform"
  description: "Only Windows."
  condition: all
  rules:
    - 'r:HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion -> ProductName -> r:^Windows 10'
checks:
  - id: 15500
    title: "Ensure password history is configured"
    description: "Password history description."
    rationale: "Password history rationale."
    remediation: "Password history remediation."
    compliance:
      - cis: ["1.1.1"]
      - pci_dss: ["8.2"]
    references:
      - https://example.com/1.1.1
    condition: all
    rules:
      - 'r:HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\PasswordHistory -> Size -> r:^\\d+$'
  - id: 15501
    title: "Minimal check using defaults"
    rules:
      - 'c:echo hello -> r:^hello$'
"""


@pytest.fixture()
def valid_file(tmp_path):
    path = tmp_path / "cis_test.yml"
    path.write_text(VALID_YML, encoding="utf-8")
    return str(path)


class TestLoadScaFile:
    def test_parses_policy_block(self, valid_file):
        sca = load_sca_file(valid_file)
        assert sca.policy.id == "cis_test"
        assert sca.policy.file == "cis_test.yml"
        assert sca.policy.name == "CIS Test Benchmark"
        assert sca.policy.description == "Benchmark for tests."
        assert sca.policy.references == ["https://www.cisecurity.org/cis-benchmarks/"]

    def test_parses_requirements_block(self, valid_file):
        sca = load_sca_file(valid_file)
        assert sca.requirements.title == "Check the platform"
        assert sca.requirements.condition == "all"
        assert len(sca.requirements.rules) == 1
        assert "ProductName" in sca.requirements.rules[0]

    def test_parses_checks(self, valid_file):
        sca = load_sca_file(valid_file)
        assert len(sca.checks) == 2

        first = sca.checks[0]
        assert first.id == 15500
        assert first.title == "Ensure password history is configured"
        assert first.compliance == [{"cis": ["1.1.1"]}, {"pci_dss": ["8.2"]}]
        assert first.condition == "all"
        assert len(first.rules) == 1

    def test_missing_optional_fields_fall_back_to_defaults(self, valid_file):
        sca = load_sca_file(valid_file)
        minimal = sca.checks[1]
        assert minimal.id == 15501
        assert minimal.description == ""
        assert minimal.rationale == ""
        assert minimal.remediation == ""
        assert minimal.compliance == []
        assert minimal.references == []
        assert minimal.condition == "all"

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_sca_file("does/not/exist.yml")


class TestLoadAllRules:
    def test_merges_checks_from_every_yml(self, tmp_path):
        (tmp_path / "a.yml").write_text(VALID_YML, encoding="utf-8")
        (tmp_path / "b.yml").write_text(VALID_YML, encoding="utf-8")
        rules = load_all_rules(str(tmp_path))
        assert len(rules) == 4  # 2 checks per file
        assert {r.id for r in rules} == {15500, 15501}

    def test_empty_directory_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_all_rules(str(tmp_path))

    def test_directory_with_only_non_yml_raises(self, tmp_path):
        (tmp_path / "notes.txt").write_text("no rules here", encoding="utf-8")
        with pytest.raises(FileNotFoundError):
            load_all_rules(str(tmp_path))

    def test_loads_the_real_bundled_ruleset(self):
        """The shipped CIS rules must parse cleanly on every platform."""
        repo_rules = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "rules", "windows",
        )
        if not os.path.isdir(repo_rules):  # pragma: no cover
            pytest.skip("bundled rules directory not present")
        rules = load_all_rules(repo_rules)
        assert len(rules) > 100, "expected a substantial CIS ruleset"
        assert all(r.rules for r in rules), "every check should define sub-rules"
        assert all(r.title for r in rules)
