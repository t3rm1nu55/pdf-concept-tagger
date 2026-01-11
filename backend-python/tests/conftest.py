"""
Pytest Configuration and Fixtures

Shared fixtures for all tests.
"""

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database.postgres import Base, get_db
from app.main import app

# Use test database
TEST_DATABASE_URL = os.getenv("TEST_POSTGRES_URL", "postgresql://pdf_tagger:pdf_tagger_dev@localhost:5432/pdf_tagger_test")

# Create test engine
test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Clean up tables
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_concept_data():
    """Sample concept data for testing."""
    return {
        "term": "GDPR",
        "type": "concept",
        "node_group": "concept",
        "data_type": "legal",
        "category": "regulation",
        "explanation": "General Data Protection Regulation",
        "confidence": 0.95,
        "assessment": "usually_true",
        "extracted_by": "HARVESTER",
        "source_location": {"page": 1}
    }
