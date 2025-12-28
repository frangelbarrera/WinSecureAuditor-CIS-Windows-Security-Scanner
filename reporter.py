# File: reporter.py

import json
import datetime
from typing import List
from evaluator import RuleResult

###################################################
# Enhanced JSON Report
###################################################

def write_enhanced_json_report(
    results: List[RuleResult],
    host: str,
    os_name: str,
    passed_count: int,
    failed_count: int,
    json_path: str,
    benchmark_name: str = ""
):
    """
    Writes a JSON report with pass/fail counts, plus the fields from each RuleResult
    (description, rationale, remediation, compliance, condition, etc.).
    The 'benchmark_name' is optional (can be empty).
    """
    total = len(results)
    score_percent = 0
    if total > 0:
        score_percent = round((passed_count / total) * 100)

    report_data = {
        "benchmark_name": benchmark_name,
        "passed": passed_count,
        "failed": failed_count,
        "score_percent": score_percent,
        "scan_time": datetime.datetime.now().isoformat(),
        "host": host,
        "os": os_name,
        "checks": []
    }

    for r in results:
        item = {
            "id": r.rule_id,
            "title": r.title,
            "status": r.status,
            "details": r.details,
            "description": r.description,
            "rationale": r.rationale,
            "remediation": r.remediation,
            "compliance": r.compliance,
            "condition": r.condition
        }
        report_data["checks"].append(item)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

###################################################
# Enhanced HTML Report (Bootstrap-based)
###################################################

def write_enhanced_html_report(
    results: List[RuleResult],
    host: str,
    os_name: str,
    passed_count: int,
    failed_count: int,
    html_path: str,
    benchmark_name: str = ""
):
    """
    Writes an HTML report with a summary and a table of checks.
    Each check has a toggle to reveal description, rationale, remediation, etc.
    The 'benchmark_name' is optional.
    """
    total = len(results)
    score_percent = 0
    if total > 0:
        score_percent = round((passed_count / total) * 100)
    date_str = datetime.datetime.now().strftime("%b %d, %Y @ %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{benchmark_name or "CIS Scan Report"}</title>
    <!-- Bootstrap CSS -->
    <link rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
    <style>
      body {{
        margin: 20px;
      }}
      .summary-box {{
        display: flex;
        flex-wrap: wrap;
        gap: 1.5rem;
        margin-bottom: 1rem;
      }}
      .summary-item {{
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        min-width: 150px;
        text-align: center;
      }}
      .pass {{
        background-color: #e0ffe0 !important;
      }}
      .fail {{
        background-color: #ffe0e0 !important;
      }}
      .details {{
        display: none;
        margin-top: 0.5rem;
      }}
      .toggle-details {{
        cursor: pointer;
        color: #0d6efd;
        text-decoration: underline;
      }}
    </style>
</head>
<body>

<div class="container">

  <h1 class="my-3">{benchmark_name or "CIS Scan Report"}</h1>
  <div class="summary-box">
    <div class="summary-item">
      <h5>Passed</h5>
      <p style="color: green; font-weight: bold;">{passed_count}</p>
    </div>
    <div class="summary-item">
      <h5>Failed</h5>
      <p style="color: red; font-weight: bold;">{failed_count}</p>
    </div>
    <div class="summary-item">
      <h5>Score</h5>
      <p style="color: #0d6efd; font-weight: bold;">{score_percent}%</p>
    </div>
    <div class="summary-item">
      <h5>Scan Date</h5>
      <p>{date_str}</p>
    </div>
    <div class="summary-item">
      <h5>Host</h5>
      <p>{host}</p>
    </div>
    <div class="summary-item">
      <h5>OS</h5>
      <p>{os_name}</p>
    </div>
  </div>

  <hr/>

  <h4>Checks ({total})</h4>
  <table class="table table-bordered table-hover mt-3">
    <thead class="table-light">
      <tr>
        <th style="width:5%">ID</th>
        <th style="width:50%">Title</th>
        <th style="width:10%">Status</th>
        <th style="width:35%">Action</th>
      </tr>
    </thead>
    <tbody>
"""

    for i, r in enumerate(results):
        row_class = "pass" if r.status == "PASS" else "fail"
        details_id = f"details-{i}"

        # Convert compliance to a readable string
        compliance_str = ""
        if r.compliance:
            comps = []
            for cdict in r.compliance:
                for key, val_list in cdict.items():
                    comps.append(f"{key}: {', '.join(val_list)}")
            compliance_str = "; ".join(comps)

        html += f"""
      <tr class="{row_class}">
        <td>{r.rule_id}</td>
        <td>{r.title}</td>
        <td>{r.status}</td>
        <td>
          <span class="toggle-details" onclick="toggleDetails('{details_id}')">View Details</span>
        </td>
      </tr>
      <tr>
        <td colspan="4">
          <div id="{details_id}" class="details">
            <p><strong>Description:</strong> {r.description}</p>
            <p><strong>Rationale:</strong> {r.rationale}</p>
            <p><strong>Remediation:</strong> {r.remediation}</p>
            <p><strong>Compliance:</strong> {compliance_str}</p>
            <p><strong>Condition:</strong> {r.condition}</p>
            <p><strong>Evaluation:</strong> {r.details}</p>
          </div>
        </td>
      </tr>
"""

    html += """
    </tbody>
  </table>
</div>

<script>
function toggleDetails(id) {
  var el = document.getElementById(id);
  if (el.style.display === "none" || el.style.display === "") {
    el.style.display = "block";
  } else {
    el.style.display = "none";
  }
}
</script>

</body>
</html>
"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
