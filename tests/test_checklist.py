"""The pre-registered part of the engineering checklist must never change."""
import subprocess
from pathlib import Path

CHECKLIST = Path(__file__).resolve().parents[1] / "reports" / "engineering_checklist.md"
HEADING = "## Observed in the EDA"
PREREGISTERED_COMMIT = "57ecbea"


def test_preregistered_section_is_unchanged():
    current = CHECKLIST.read_text()
    current_head = current.split(HEADING)[0]

    original = subprocess.run(
        ["git", "show", f"{PREREGISTERED_COMMIT}:reports/engineering_checklist.md"],
        cwd=CHECKLIST.parents[1],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    original_head = original.split(HEADING)[0]

    assert current_head == original_head


def test_observed_section_present():
    current = CHECKLIST.read_text()
    assert HEADING in current
    observed = current.split(HEADING, 1)[1]
    assert len(observed.strip()) > 0
