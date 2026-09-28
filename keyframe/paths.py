"""Repository-relative paths used by the package, notebooks and API."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
LOCKBOX = DATA / "lockbox"
PROCESSED = DATA / "processed"
MODELS = ROOT / "models"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
RESULTS = REPORTS / "results"
