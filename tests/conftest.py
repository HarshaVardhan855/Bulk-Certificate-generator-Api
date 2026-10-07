import os
import sys
import shutil
import tempfile
from pathlib import Path
from typing import Generator

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Prepare temporary paths for test isolation
TEST_DIR = Path(tempfile.mkdtemp(prefix="cert_test_"))
TEST_DB_PATH = TEST_DIR / "test.db"
TEST_GENERATED_DIR = TEST_DIR / "generated"
TEST_GENERATED_DIR.mkdir(parents=True, exist_ok=True)

# Point environment variables before importing app modules
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ["GENERATED_DIR"] = str(TEST_GENERATED_DIR)

from app.core.database import Base, get_db  # noqa: E402
import app.core.database as core_db  # noqa: E402
import app.workers.tasks as worker_tasks  # noqa: E402
import app.services.certificate_service as cert_svc  # noqa: E402
from app.main import app  # noqa: E402

test_engine = create_engine(
    f"sqlite:///{TEST_DB_PATH}",
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Patch SessionLocal across modules so background tasks use the test DB
core_db.SessionLocal = TestingSessionLocal
worker_tasks.SessionLocal = TestingSessionLocal
cert_svc.GENERATED_DIR = TEST_GENERATED_DIR


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    # Clear generated files in temp dir between tests
    for f in TEST_GENERATED_DIR.glob("*.pdf"):
        try:
            f.unlink()
        except OSError:
            pass


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def cleanup_temp_dir():
    yield
    try:
        shutil.rmtree(TEST_DIR, ignore_errors=True)
    except Exception:
        pass
