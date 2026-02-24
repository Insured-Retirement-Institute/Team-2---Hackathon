import os
from pathlib import Path

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://")
QUERIES_DIR = Path(os.environ.get("QUERIES_DIR", Path(__file__).parent / "queries"))
