"""Drift guard: the Portable rules must mirror the canonical ruleset.

``rules/windows`` is the single source of truth. If the bundled copy under
``WinSecureAuditor_Portable/rules/windows`` diverges, this test fails and
tells you to run ``python scripts/sync_portable.py``.
"""

import hashlib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE = REPO_ROOT / "rules" / "windows"
TARGET = REPO_ROOT / "WinSecureAuditor_Portable" / "rules" / "windows"


def snapshot(root: Path) -> dict:
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*.yml"))
    }


@pytest.mark.skipif(
    not (SOURCE.is_dir() and TARGET.is_dir()),
    reason="portable rules directory not present in this checkout",
)
def test_portable_rules_are_in_sync_with_canonical_ruleset():
    src = snapshot(SOURCE)
    tgt = snapshot(TARGET)

    drift = sorted(k for k in src if tgt.get(k) != src[k])
    stale = sorted(k for k in tgt if k not in src)

    assert not drift and not stale, (
        "WinSecureAuditor_Portable rules are out of sync with rules/windows.\n"
        f"  drifted: {drift}\n"
        f"  stale:   {stale}\n"
        "Fix with: python scripts/sync_portable.py"
    )
