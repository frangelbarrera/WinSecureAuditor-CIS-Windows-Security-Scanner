"""Tests for the JSON and HTML reporters."""

import json

from reporter import write_enhanced_html_report, write_enhanced_json_report


class TestJsonReport:
    def test_report_structure(self, tmp_path, make_result):
        results = [
            make_result(rule_id=1, status="PASS", title="Check A"),
            make_result(rule_id=2, status="FAIL", title="Check B"),
        ]
        out = tmp_path / "scan.json"
        write_enhanced_json_report(
            results=results, host="HOST01", os_name="Windows 10",
            passed_count=1, failed_count=1, json_path=str(out),
            benchmark_name="CIS Windows 10",
        )
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["benchmark_name"] == "CIS Windows 10"
        assert data["host"] == "HOST01"
        assert data["os"] == "Windows 10"
        assert data["passed"] == 1
        assert data["failed"] == 1
        assert data["score_percent"] == 50
        assert "scan_time" in data
        assert len(data["checks"]) == 2

    def test_check_entries_carry_rule_fields(self, tmp_path, make_result):
        out = tmp_path / "scan.json"
        write_enhanced_json_report(
            results=[make_result()], host="H", os_name="OS",
            passed_count=1, failed_count=0, json_path=str(out),
        )
        entry = json.loads(out.read_text(encoding="utf-8"))["checks"][0]
        for key in ("id", "title", "status", "details", "description",
                    "rationale", "remediation", "compliance", "condition"):
            assert key in entry

    def test_benchmark_name_defaults_to_empty(self, tmp_path, make_result):
        out = tmp_path / "scan.json"
        write_enhanced_json_report(
            results=[], host="H", os_name="OS",
            passed_count=0, failed_count=0, json_path=str(out),
        )
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["benchmark_name"] == ""
        assert data["score_percent"] == 0  # zero results must not divide by zero

    def test_uses_utf8_encoding(self, tmp_path, make_result):
        out = tmp_path / "scan.json"
        write_enhanced_json_report(
            results=[make_result(title="Añadir contraseña — ñ ok")],
            host="H", os_name="OS", passed_count=1, failed_count=0,
            json_path=str(out),
        )
        data = json.loads(out.read_text(encoding="utf-8"))
        assert "ñ" in data["checks"][0]["title"]


class TestHtmlReport:
    def test_contains_summary_and_rows(self, tmp_path, make_result):
        results = [
            make_result(rule_id=1, status="PASS", title="Passing check"),
            make_result(rule_id=2, status="FAIL", title="Failing check"),
        ]
        out = tmp_path / "report.html"
        write_enhanced_html_report(
            results=results, host="HOST01", os_name="Windows 10",
            passed_count=1, failed_count=1, html_path=str(out),
            benchmark_name="CIS Windows 10",
        )
        html = out.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in html
        assert "CIS Windows 10" in html
        assert 'class="pass"' in html
        assert 'class="fail"' in html
        assert "Passing check" in html
        assert "Failing check" in html
        assert "HOST01" in html
        assert "toggleDetails" in html

    def test_fallback_title_when_no_benchmark(self, tmp_path, make_result):
        out = tmp_path / "report.html"
        write_enhanced_html_report(
            results=[make_result()], host="H", os_name="OS",
            passed_count=1, failed_count=0, html_path=str(out),
        )
        html = out.read_text(encoding="utf-8")
        assert "CIS Scan Report" in html

    def test_compliance_rendered_readable(self, tmp_path, make_result):
        out = tmp_path / "report.html"
        write_enhanced_html_report(
            results=[make_result(compliance=[{"cis": ["1.1.1", "1.1.2"], "pci_dss": ["8.2"]}])],
            host="H", os_name="OS", passed_count=1, failed_count=0,
            html_path=str(out),
        )
        html = out.read_text(encoding="utf-8")
        assert "cis: 1.1.1, 1.1.2" in html
        assert "pci_dss: 8.2" in html

    def test_zero_results_renders_without_crash(self, tmp_path):
        out = tmp_path / "report.html"
        write_enhanced_html_report(
            results=[], host="H", os_name="OS",
            passed_count=0, failed_count=0, html_path=str(out),
        )
        assert "Checks (0)" in out.read_text(encoding="utf-8")
