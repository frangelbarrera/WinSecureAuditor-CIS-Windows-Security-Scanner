# Contributing to WinSecureAuditor

Thanks for your interest in improving WinSecureAuditor. This document covers
the essential workflow so your changes land quickly.

## Development setup

```bash
git clone https://github.com/frangelbarrera/WinSecureAuditor.git
cd WinSecureAuditor
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

Python 3.10+ is required. The runtime dependency footprint is intentionally
tiny (`PyYAML` only); everything else is standard library.

## Running the tests

```bash
pytest
```

The suite runs on Linux, macOS and Windows. Registry-dependent code paths are
exercised through fakes on non-Windows platforms, so you do not need Windows
to develop — but please smoke-test registry-heavy changes on a real Windows
machine before submitting.

The test suite includes a drift guard: the rules bundled under
`WinSecureAuditor_Portable/` must stay identical to `rules/windows/`. If you
edit any rule, refresh the portable copy with:

```bash
python scripts/sync_portable.py
```

## Linting

```bash
ruff check .
```

CI runs the same command; fix warnings locally before pushing.

## Project layout

| Path | Purpose |
|---|---|
| `main.py` | CLI entry point |
| `gui.py` | Tkinter graphical interface |
| `scanner.py` | Orchestrates load → execute → evaluate |
| `parser.py` | Parses Wazuh-style SCA YAML rule files |
| `sca_structs.py` | Dataclasses for the rule format |
| `executor.py` | Runs sub-rules (registry / file / command) |
| `evaluator.py` | Decides PASS/FAIL per rule and sub-rule |
| `scoring.py` | Basic and weighted compliance scores |
| `reporter.py` | JSON and HTML report generation |
| `rules/windows/` | Canonical CIS benchmark rules (source of truth) |
| `WinSecureAuditor_Portable/` | Generated portable distribution copy |
| `scripts/sync_portable.py` | Regenerates the portable rules copy |

## Rule file format

Rules follow the Wazuh SCA YAML dialect:

```yaml
checks:
  - id: 15500
    title: "Ensure 'Enforce password history' is set to 24 or greater"
    condition: all            # all | any | none
    rules:
      - 'r:HKLM\...\Netlogon -> PasswordHistory -> r:^\d+$'
```

Sub-rule prefixes: `r:` registry, `f:` file, `c:`/`cmd:` command. Comparison
suffixes: `-> exists`, `-> missing`, `-> r:<regex>` (case-insensitive).

## Pull requests

1. Fork, create a feature branch (`fix/...` or `feat/...`).
2. Add or update tests for the behaviour you are changing.
3. Make sure `pytest` and `ruff check .` pass locally.
4. Keep diffs focused — one logical change per PR.
5. Describe the motivation, not just the implementation.

## Security

See [SECURITY.md](SECURITY.md). Do not open issues with sensitive scan
output; use the private contact channel listed there instead.
