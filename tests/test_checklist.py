"""The pre-registered part of the engineering checklist must never change.

Everything above the "Observed" heading was committed (1c75bdf, "docs: pre-register
the engineering checklist") before any fault run was compared with healthy running.
Its SHA-256 is pinned here, so the check needs no git history (CI clones shallow).
"""

import hashlib
from pathlib import Path

CHECKLIST = Path(__file__).resolve().parents[1] / "reports" / "engineering_checklist.md"
HEADING = "## Observed in the EDA"
PREREGISTERED_SHA256 = "563cef490d82cd71738f19941349f0cec4a2cc856ec608e0d0032b7cdc8ae6b6"


def test_preregistered_section_is_unchanged():
    current_head = CHECKLIST.read_text().split(HEADING)[0]
    assert hashlib.sha256(current_head.encode()).hexdigest() == PREREGISTERED_SHA256


def test_observed_section_present():
    current = CHECKLIST.read_text()
    assert HEADING in current
    observed = current.split(HEADING, 1)[1]
    assert len(observed.strip()) > 0
