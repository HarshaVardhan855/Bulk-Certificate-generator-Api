import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'certificates.db'}")
GENERATED_DIR = Path(os.getenv("GENERATED_DIR", str(BASE_DIR / "generated")))
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

PROJECT_NAME = "Bulk Certificate Generator API"
API_V1_STR = "/api/v1"
