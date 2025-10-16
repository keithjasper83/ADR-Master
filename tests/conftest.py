"""Pytest configuration and fixtures."""
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings, get_settings
from app.db.database import Base, get_db
from app.main import app


@pytest.fixture(scope="function")
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(scope="function")
def test_settings(temp_dir: Path) -> Settings:
    """Create test settings."""
    return Settings(
        workdir=temp_dir,
        adr_dir=temp_dir / "ADR",
        adr_draft_dir=temp_dir / "ADR" / "Draft",
        log_dir=temp_dir / "_logs",
        database_url=f"sqlite:///{temp_dir}/test.db",
        mcp_base_url=None,
        github_token=None,
    )


@pytest.fixture(scope="function")
def test_db(test_settings: Settings) -> Generator[Session, None, None]:
    """Create test database."""
    engine = create_engine(
        test_settings.database_url, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_settings: Settings, test_db: Session) -> TestClient:
    """Create test client."""
    
    def override_get_settings():
        return test_settings
    
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_settings] = override_get_settings
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()
