import os
from pathlib import Path

QUERIES_DIR = Path(os.environ.get("QUERIES_DIR", Path(__file__).parent / "queries"))
