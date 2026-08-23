"""Tests for sca_structs dataclasses."""

from sca_structs import PolicyBlock, RequirementsBlock, Rule, SCAFile


class TestPolicyBlock:
    def test_defaults(self):
        p = PolicyBlock()
        assert p.id == ""
        assert p.file == ""
        assert p.name == ""
        assert p.description == ""
        assert p.references == []

    def test_references_not_shared_between_instances(self):
        a, b = PolicyBlock(), PolicyBlock()
        a.references.append("x")
        assert b.references == []


class TestRequirementsBlock:
    def test_defaults(self):
        r = RequirementsBlock()
        assert r.title == ""
        assert r.description == ""
        assert r.condition == "all"
        assert r.rules == []

    def test_rules_not_shared_between_instances(self):
        a, b = RequirementsBlock(), RequirementsBlock()
        a.rules.append("c:echo -> r:ok")
        assert b.rules == []


class TestRule:
    def test_defaults(self):
        r = Rule()
        assert r.id == 0
        assert r.title == ""
        assert r.compliance == []
        assert r.references == []
        assert r.condition == "all"
        assert r.rules == []

    def test_mutable_lists_not_shared_between_instances(self):
        a, b = Rule(), Rule()
        a.rules.append("f:x -> exists")
        a.compliance.append({"cis": ["1.1"]})
        assert b.rules == []
        assert b.compliance == []


class TestSCAFile:
    def test_defaults(self):
        s = SCAFile()
        assert isinstance(s.policy, PolicyBlock)
        assert isinstance(s.requirements, RequirementsBlock)
        assert s.checks == []

    def test_checks_not_shared_between_instances(self):
        a, b = SCAFile(), SCAFile()
        a.checks.append(Rule(id=1))
        assert b.checks == []
