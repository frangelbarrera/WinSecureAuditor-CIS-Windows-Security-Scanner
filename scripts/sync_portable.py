#!/usr/bin/env python3
"""Keep the Portable distribution rules in sync with the canonical ruleset.

``rules/windows`` is the single source of truth. The copy bundled under
``WinSecureAuditor_Portable/rules/windows`` is generated from it.

Usage:
    python scripts/sync_portable.py           # copy changed files over
    python scripts/sync_portable.py --check   # only report drift (exit 1)
"""

import argparse
import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE = REPO_ROOT / "rules" / "windows"
TARGET = REPO_ROOT / "WinSecureAuditor_Portable" / "rules" / "windows"


def snapshot(root: Path) -> dict:
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*.yml"))
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="report drift without copying; exit code 1 on drift")
    args = ap.parse_args()

    if not SOURCE.is_dir():
        print(f"error: source rules not found at {SOURCE}", file=sys.stderr)
        return 2

    src = snapshot(SOURCE)
    TARGET.mkdir(parents=True, exist_ok=True)
    tgt = snapshot(TARGET)

    changed = sorted(k for k in src if tgt.get(k) != src[k])
    removed = sorted(k for k in tgt if k not in src)

    if not changed and not removed:
        print(f"portable rules already in sync ({len(src)} files)")
        return 0

    if args.check:
        for k in changed:
            print(f"drift: {k}")
        for k in removed:
            print(f"stale: {k}")
        print("run: python scripts/sync_portable.py")
        return 1

    for rel in changed:
        (TARGET / rel).parent.mkdir(parents=True, exist_ok=True)
        (TARGET / rel).write_bytes((SOURCE / rel).read_bytes())
        print(f"synced: {rel}")
    for rel in removed:
        (TARGET / rel).unlink()
        print(f"removed stale: {rel}")
    print(f"done: {len(changed)} synced, {len(removed)} removed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
