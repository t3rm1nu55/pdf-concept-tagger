"""
Integration Tests

MVP: Test API endpoints with database.
Requires PostgreSQL running.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, AsyncMock
from app.main import app
from app.database.postgres import Base, get_db
import os

# Test database URL
TEST_DATABASE_URL = os.getenv("TEST_POSTGRES_URL", "postgresql://pdf_tagger:pdf_tagger_dev@localhost:5432/pdf_tagger_mvp_test")

# Create test engine
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_concepts_empty(client):
    """Test getting concepts when none exist."""
    response = client.get("/api/v1/concepts")
    assert response.status_code == 200
    data = response.json()
    assert data["concepts"] == []
    assert data["pagination"]["total"] == 0


@pytest.mark.asyncio
@patch("app.api.v1.endpoints.analyze.CognizantProxyLLM")
@patch("app.api.v1.endpoints.analyze.PDFProcessor")
async def test_analyze_pdf_integration(mock_processor_class, mock_llm_class, client, db_session):
    """Test PDF analysis end-to-end."""
    # Mock PDF processor
    mock_processor = AsyncMock()
    mock_processor.extract_page_text = AsyncMock(return_value="Sample PDF text with GDPR and data protection")
    mock_processor_class.return_value = mock_processor
    
    # Mock LLM
    mock_llm = AsyncMock()
    mock_llm.extract_concepts = AsyncMock(return_value=[
        {
            "id": "c1",
            "term": "GDPR",
            "type": "concept",
            "dataType": "legal",
            "confidence": 0.95,
            "explanation": "General Data Protection Regulation"
        },
        {
            "id": "c2",
            "term": "data protection",
            "type": "concept",
            "dataType": "legal",
            "confidence": 0.85,
            "explanation": "Data protection requirements"
        }
    ])
    mock_llm_class.return_value = mock_llm
    
    # Create test file
    test_file = ("test.pdf", b"fake pdf content", "application/pdf")
    
    response = client.post(
        "/api/v1/analyze",
        files={"file": test_file},
        data={"page_number": 1}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert len(data["concepts"]) == 2
    assert data["concepts"][0]["term"] == "GDPR"
    
    # Verify concepts stored in database
    concepts_response = client.get("/api/v1/concepts")
    assert concepts_response.status_code == 200
    concepts_data = concepts_response.json()
    assert concepts_data["pagination"]["total"] == 2
