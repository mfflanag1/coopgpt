"""Package-local paths for fresh verification output."""
from pathlib import Path
RESULTS = Path(__file__).resolve().parent / "results"
RESULTS.mkdir(exist_ok=True)
