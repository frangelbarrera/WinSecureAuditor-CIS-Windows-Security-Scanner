"""Integration tests: the full load -> execute -> evaluate -> score pipeline.

These run on every platform because they rely on file-existence checks
(tmp files) and command checks rather than the Windows registry.
"""

import logging

import pytest

from scanner import Scanner


def _rewrite_rules(rules_dir, transform):
    """Rewrite the generated yml through ``transform`` and return its path."""
    import os

    path = os.path.join(rules_dir, "test_rules.yml")
    with open(path, encoding="utf-8") as fh:
        content = transform(fh.read())
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return path


class TestScannerPipeline:
    def test_run_scan_executes_portable_rules(self, rules_dir):
        scanner = Scanner(rules_dir)
        results = scanner.run_scan()

        assert len(results) == 2
        by_id = {r.rule_id: r for r in results}
        assert by_id[20001].status == "PASS"  # required file exists
        assert by_id[20002].status == "PASS"  # forbidden file missing

    def test_failing_check_when_required_file_disappears(self, rules_dir, tmp_path):
        # Remove the required helper file so check 20001 must FAIL.
        (tmp_path / "required_helper.txt").unlink()
        scanner = Scanner(rules_dir)
        results = scanner.run_scan()
        by_id = {r.rule_id: r for r in results}
        assert by_id[20001].status == "FAIL"
        assert "file not found" in by_id[20001].details

    def test_basic_summary(self, rules_dir):
        scanner = Scanner(rules_dir)
        scanner.run_scan()
        summary = scanner.get_summary()
        assert summary["passed"] == 2
        assert summary["failed"] == 0
        assert summary["total"] == 2
        assert summary["score_percent"] == 100

    def test_weighted_summary(self, rules_dir):
        scanner = Scanner(rules_dir)
        scanner.run_scan()
        summary = scanner.get_summary(weighted=True)
        assert summary["weighted"] is True
        assert summary["total"] == 2
        assert summary["score_percent"] == 100

    def test_batch_size_one_processes_everything(self, rules_dir):
        scanner = Scanner(rules_dir)
        scanner.load_rules()
        assert len(scanner.rules) == 2
        scanner.execute_and_evaluate(batch_size=1)
        assert len(scanner.results) == 2

    def test_load_rules_failure_propagates(self, tmp_path):
        scanner = Scanner(str(tmp_path / "nowhere"))
        with pytest.raises(FileNotFoundError):
            scanner.run_scan()

    def test_run_scan_logs_summary(self, rules_dir, caplog):
        scanner = Scanner(rules_dir)
        with caplog.at_level(logging.INFO):
            scanner.run_scan()
        assert any("Scan completed" in rec.message for rec in caplog.records)
