# File: main.py

import argparse
import sys
import os
import logging

from scanner import Scanner
from scoring import calculate_basic_score
from reporter import (
    write_enhanced_json_report,
    write_enhanced_html_report
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    parser = argparse.ArgumentParser(description="Windows CIS Scanner Audit")
    parser.add_argument("--rules", default="./rules/windows",
                        help="Directory containing .yml rule files")
    parser.add_argument("--json", default="./output/scan.json",
                        help="Path to JSON output file")
    parser.add_argument("--html", default="./output/report.html",
                        help="Path to HTML output file")
    parser.add_argument("--host", default="MyHost", help="Hostname override")
    parser.add_argument("--os", default="Windows 11", help="OS name override")
    parser.add_argument("--benchmark", default="",
                        help="(Optional) Benchmark name to display in reports")
    parser.add_argument("--weighted", action="store_true",
                        help="Use weighted scoring based on severity")
    args = parser.parse_args()

    # Use the refactored Scanner
    scanner = Scanner(args.rules)
    try:
        all_results = scanner.run_scan()
    except Exception as e:
        logging.error(f"Error during scan: {e}")
        sys.exit(1)

    # Calculate score using scanner
    summary = scanner.get_summary(weighted=args.weighted)
    score_type = "weighted" if args.weighted else "basic"
    logging.info(f"Summary ({score_type}): Passed: {summary['passed']}, Failed: {summary['failed']}, Score: {summary['score_percent']}%")

    # 4. Ensure output folders exist
    os.makedirs(os.path.dirname(args.json), exist_ok=True)
    os.makedirs(os.path.dirname(args.html), exist_ok=True)

    # 5. Generate Enhanced JSON & HTML
    write_enhanced_json_report(
        results=all_results,
        host=args.host,
        os_name=args.os,
        passed_count=summary['passed'],
        failed_count=summary['failed'],
        json_path=args.json,
        benchmark_name=args.benchmark
    )

    write_enhanced_html_report(
        results=all_results,
        host=args.host,
        os_name=args.os,
        passed_count=summary['passed'],
        failed_count=summary['failed'],
        html_path=args.html,
        benchmark_name=args.benchmark
    )

    print(f"JSON report saved to: {args.json}")
    print(f"HTML report saved to: {args.html}")

    # 6. Exit code 1 if any checks fail
    if summary['failed'] > 0:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
