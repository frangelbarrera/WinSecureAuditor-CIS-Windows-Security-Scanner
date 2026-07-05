# Security Policy

## WinSecureAuditor — CIS Windows Security Scanner

This document explains how to responsibly report security issues in
the WinSecureAuditor codebase (Python scanner + bundled CIS rule
files). It does **not** describe how to use the tool — for that, see
`README.md`.

## Supported Versions

| Version   | Branch | Supported             |
|-----------|--------|-----------------------|
| Latest    | `main` | Security fixes only   |
| < Latest  | any    | Not supported         |

WinSecureAuditor is in **maintenance mode**. A single critical-fix
pass is queued (fail-closed evaluator, attribution update,
`shell=True` hardening). After that pass the repository will be
**archived**. New features will not be developed. Reports against
forks or pre-`main` commits will not be triaged.

## Reporting a Vulnerability

**Do not open a public GitHub issue for security reports.**

Email the maintainer privately at:

`frangelrcbarrera@gmail.com`

Please include:

1. **Description** of the issue and its security impact.
2. **Affected file(s) and line(s)** (e.g. `executor.py:119`).
3. **Reproduction steps** — minimal YAML rule, command, and the
   observed vs. expected behavior.
4. **Git commit hash** of the version you tested.
5. **Suggested fix** (optional, but appreciated).

You should receive an acknowledgement within **7 days**. If the
issue is confirmed, a fix will be developed and released as a public
commit. You will be credited in the commit message unless you
request otherwise.

## Response Timeline

| Severity                        | Ack   | Fix target                |
|---------------------------------|-------|---------------------------|
| Critical (RCE, supply-chain)    | 7 days| 30 days                   |
| High (XSS, auth bypass)         | 7 days| 60 days                   |
| Medium / Low                    | 7 days| Best-effort before archival|

The maintainer is an individual contributor; timelines may slip if
connectivity or infrastructure is interrupted. Any slip will be
communicated by email to the reporter.

## Scope

**In scope:**

- Vulnerabilities in the Python scanner code (`parser.py`,
  `executor.py`, `evaluator.py`, `scanner.py`, `scoring.py`,
  `reporter.py`, `gui.py`, `main.py`, `sca_structs.py`).
- Code execution, path traversal, or injection issues triggered by
  loading a YAML rule file.
- Stored XSS in the generated HTML report (`reporter.py`).
- Supply-chain issues in declared dependencies.
- License/attribution inconsistencies that affect redistribution.

**Out of scope:**

- *"The scanner reports PASS but the control is not actually met."*
  This is a **known functional limitation** of the evaluator — see
  *Known Security Considerations* below. It is tracked as a
  maintenance item, not a new vulnerability.
- *"The bundled CIS rules are outdated."* The rule files are
  third-party content (see *Attribution*); report upstream to Wazuh.
- *"The tool requires administrator privileges."* Intended behavior
  for registry checks.
- *"The referenced `WinSecureAuditor_Installer.exe` is missing."*
  Known documentation defect, not a security issue.

## Safe Harbor

Good-faith security research on systems you own or are explicitly
authorized to test is welcomed and will not be the subject of legal
action by the maintainer, provided that:

- You do not degrade availability (no DoS, no resource exhaustion).
- You do not access, exfiltrate, or destroy third-party data.
- You do not test the tool against production systems without
  written authorization from their owner.
- You give the maintainer reasonable time to remediate before any
  public disclosure.

## Legal Framework

This policy is aligned with international responsible disclosure
frameworks:

- **USA** — Computer Fraud and Abuse Act (CFAA), 18 U.S.C. § 1030.
  Good-faith security research should not be prosecuted. See DOJ
  Guidance (2022).
- **European Union** — Directive 2013/40/EU on attacks against
  information systems. Member States should not criminalize good-faith
  research.
- **Council of Europe** — Convention on Cybercrime (Budapest, 2001).
  Article 6 (misuse of devices) exceptions for research.
- **United Kingdom** — Computer Misuse Act 1990 (CMA). See Crown
  Prosecution Service guidance on legitimate researchers.

Reporters are responsible for complying with the laws of their own
jurisdiction. If you are unsure whether your research falls under
"good faith," contact the maintainer **before** testing.

## Known Security Considerations

These are documented so that reporters do not waste effort on items
already tracked:

1. **Latent RCE via `cmd:` rules** — `executor.py:119`
   (`run_command`) calls
   `subprocess.check_output(cmd_str, shell=True, universal_newlines=True)`
   on the raw string of any YAML rule prefixed with `cmd:`. None of
   the bundled rules use `cmd:`, so the issue is latent. Loading an
   **untrusted** YAML rule pack that contains `cmd:` rules results in
   arbitrary command execution. **Mitigation:** only load rule packs
   from trusted sources. The maintenance pass will either remove
   `cmd:` support or replace `shell=True` with a tokenized argv list
   and an explicit allow-list.

2. **Destructive `.lower()` on sub-rule** — `executor.py:24`
   lowercases the entire rule string before parsing, including
   registry paths and file paths. This corrupts lookups on
   case-sensitive paths. Functional bug, not strictly a security
   bug, but it weakens the integrity of registry results.

3. **Evaluator returns false PASS (known functional bug)** —
   `evaluator.py:evaluate_subrule()` only recognizes `-> exists`,
   `-> missing`, and `-> regex:` matchers. The bundled CIS rules
   use Wazuh SCA syntax (`-> 1`, `-> n:`, `-> r:^...$`). The
   default branch returns `True` ("no condition recognized"), so
   most rules PASS without actually being evaluated. **Do not rely
   on WinSecureAuditor PASS output for compliance decisions** until
   the queued fail-closed fix (default `return False`) is merged.
   Until then, treat every PASS as "unverified".

4. **Stored XSS in HTML report** — `reporter.py` (f-string
   interpolation, lines 185–206) interpolates rule `title`,
   `description`, `rationale`, `remediation`, and `compliance`
   strings into the HTML template without escaping. A malicious
   YAML rule pack can therefore inject `<script>` into the generated
   report, which executes when the report is opened in a browser.
   **Mitigation:** only load trusted rule packs.

5. **License conflict on bundled rule files** — the YAML files in
   `rules/windows/` and `WinSecureAuditor_Portable/rules/windows/`
   carry a GPL-v2 header (Wazuh SCA upstream), while the repository
   `LICENSE` is GPL-v3. The maintenance pass will add explicit
   attribution to Wazuh and reconcile the licensing notice.

6. **README references non-existent binaries** —
   `WinSecureAuditor_Installer.exe` and `WinSecureAuditor_GUI.exe`
   are mentioned in `README.md` but not shipped. Only the Inno Setup
   source `installer.iss` is present. Listed here only because it
   can mislead users into running untrusted binaries downloaded
   from third parties under the same name.

## Attribution

The repository bundles **6 YAML files** in `rules/windows/`
(duplicated 100% in `WinSecureAuditor_Portable/rules/windows/`)
containing **1148 CIS checks** with a total of **1323 sub-rules**.
These files are derived from the **Wazuh SCA** policy set
(<https://github.com/wazuh/wazuh-ruleset>), licensed under GPL-v2.
The `sca_structs.py` data classes follow the Wazuh SCA file schema.
The maintenance pass will add a `THIRD_PARTY_NOTICES.md` and an
explicit attribution section to `README.md`.

If you are a Wazuh contributor and find that attribution is missing
or incorrect, please email the maintainer — this will be treated as
a priority issue.

## Acknowledgments

Security researchers who report confirmed issues will be credited by
name (or handle) in the fixing commit message and in this section,
unless they request otherwise. No reports have been received yet.

## Contact

- **Maintainer:** Frangel Raúl Crespo Barrera
- **Email:** `frangelrcbarrera@gmail.com`
- **GitHub:** [frangelbarrera](https://github.com/frangelbarrera)

Responsible disclosure is appreciated. Irresponsible disclosure
(public post before the fix lands, or testing on systems you do not
own) voids the safe harbor above.
