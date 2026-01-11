"""
API Endpoint Tests

MVP: Test API endpoints.
"""

import pytest
import uuid
from unittest.mock import patch, AsyncMock, MagicMock
from app.models.concept import Document, Concept


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
@patch("app.api.v1.endpoints.analyze.CognizantProxyLLM")
@patch("app.api.v1.endpoints.analyze.PDFProcessor")
async def test_analyze_endpoint(mock_processor_class, mock_llm_class, client, db_session):
    """Test PDF analysis endpoint."""
    # Mock PDF processor
    mock_processor = AsyncMock()
    mock_processor.extract_page_text = AsyncMock(return_value="Sample PDF text with GDPR requirements")
    mock_processor_class.return_value = mock_processor
    
    # Mock LLM
    mock_llm = AsyncMock()
    mock_llm.extract_concepts = AsyncMock(return_value=[
        {
            "term": "GDPR",
            "type": "concept",
            "dataType": "legal",
            "category": "regulation",
            "confidence": 0.95,
            "explanation": "General Data Protection Regulation"
        }
    ])
    mock_llm_class.return_value = mock_llm
    
    # Create test file
    test_file = ("test.pdf", b"fake pdf content", "application/pdf")
    
    # Test endpoint
    response = client.post(
        "/api/v1/analyze",
        files={"file": test_file},
        params={"page_number": 1}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert "concepts" in data
    assert len(data["concepts"]) > 0
    assert data["concepts"][0]["term"] == "GDPR"


def test_get_concepts_endpoint(client, db_session, sample_concept_data):
    """Test concepts endpoint."""
    # Create a test document and concept
    doc = Document(
        id=uuid.uuid4(),
        filename="test.pdf",
        status="completed"
    )
    db_session.add(doc)
    db_session.commit()
    
    concept = Concept(
        document_id=doc.id,
        **sample_concept_data
    )
    db_session.add(concept)
    db_session.commit()
    
    # Test endpoint
    response = client.get("/api/v1/concepts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["term"] == "GDPR"


def test_get_concept_by_id(client, db_session, sample_concept_data):
    """Test getting a single concept by ID."""
    # Create a test document and concept
    doc = Document(
        id=uuid.uuid4(),
        filename="test.pdf",
        status="completed"
    )
    db_session.add(doc)
    db_session.commit()
    
    concept = Concept(
        document_id=doc.id,
        **sample_concept_data
    )
    db_session.add(concept)
    db_session.commit()
    
    # Test endpoint
    response = client.get(f"/api/v1/concepts/{concept.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["term"] == "GDPR"
    assert data["id"] == str(concept.id)
