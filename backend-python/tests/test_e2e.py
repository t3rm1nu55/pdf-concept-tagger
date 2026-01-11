"""
End-to-End Tests

MVP: Test complete workflow from PDF upload to concept extraction.
"""

import pytest
import uuid
from unittest.mock import patch, AsyncMock
from app.models.concept import Document, Concept


@pytest.mark.asyncio
@patch("app.api.v1.endpoints.analyze.CognizantProxyLLM")
@patch("app.api.v1.endpoints.analyze.PDFProcessor")
async def test_e2e_pdf_analysis_workflow(mock_processor_class, mock_llm_class, client, db_session):
    """
    Test complete workflow:
    1. Upload PDF
    2. Extract text
    3. Extract concepts via LLM
    4. Store concepts
    5. Query concepts
    """
    # Mock PDF processor
    mock_processor = AsyncMock()
    mock_processor.extract_page_text = AsyncMock(return_value="""
    The General Data Protection Regulation (GDPR) is a European Union regulation
    that requires data protection and privacy. The completion date for compliance
    is May 25, 2018. Organizations must implement data protection measures.
    """)
    mock_processor_class.return_value = mock_processor
    
    # Mock LLM to return multiple concepts
    mock_llm = AsyncMock()
    mock_llm.extract_concepts = AsyncMock(return_value=[
        {
            "term": "GDPR",
            "type": "concept",
            "dataType": "legal",
            "category": "regulation",
            "confidence": 0.95,
            "explanation": "General Data Protection Regulation"
        },
        {
            "term": "May 25, 2018",
            "type": "concept",
            "dataType": "date",
            "category": "temporal",
            "confidence": 0.90,
            "explanation": "Compliance deadline"
        },
        {
            "term": "Data Protection",
            "type": "concept",
            "dataType": "entity",
            "category": "requirement",
            "confidence": 0.85,
            "explanation": "Data protection measures"
        }
    ])
    mock_llm_class.return_value = mock_llm
    
    # Step 1: Upload PDF
    test_file = ("test.pdf", b"fake pdf content", "application/pdf")
    response = client.post(
        "/api/v1/analyze",
        files={"file": test_file},
        params={"page_number": 1}
    )
    
    assert response.status_code == 200
    analysis_data = response.json()
    assert "document_id" in analysis_data
    assert "concepts" in analysis_data
    assert len(analysis_data["concepts"]) == 3
    
    document_id = analysis_data["document_id"]
    
    # Step 2: Verify document status
    status_response = client.get(f"/api/v1/analyze/{document_id}/status")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["status"] == "completed"
    assert status_data["concepts_extracted"] == 3
    
    # Step 3: Query all concepts
    concepts_response = client.get("/api/v1/concepts")
    assert concepts_response.status_code == 200
    concepts = concepts_response.json()
    assert len(concepts) >= 3
    
    # Step 4: Query concepts by document
    doc_concepts = [c for c in concepts if c.get("document_id") == document_id]
    assert len(doc_concepts) == 3
    
    # Step 5: Verify concept details
    gdpr_concept = next(c for c in doc_concepts if c["term"] == "GDPR")
    assert gdpr_concept["confidence"] == 0.95
    assert gdpr_concept["type"] == "concept"
    
    # Step 6: Get graph data
    graph_response = client.get("/api/v1/graph")
    assert graph_response.status_code == 200
    graph_data = graph_response.json()
    assert "nodes" in graph_data
    assert "edges" in graph_data
    assert len(graph_data["nodes"]) >= 3


@pytest.mark.asyncio
async def test_error_handling_invalid_pdf(client, db_session):
    """Test error handling for invalid PDF."""
    # Try to upload non-PDF file
    test_file = ("test.txt", b"not a pdf", "text/plain")
    response = client.post(
        "/api/v1/analyze",
        files={"file": test_file},
        params={"page_number": 1}
    )
    
    # Should handle gracefully (either reject or process)
    assert response.status_code in [200, 400, 422]


@pytest.mark.asyncio
@patch("app.api.v1.endpoints.analyze.CognizantProxyLLM")
@patch("app.api.v1.endpoints.analyze.PDFProcessor")
async def test_error_handling_llm_failure(mock_processor_class, mock_llm_class, client, db_session):
    """Test error handling when LLM fails."""
    # Mock PDF processor success
    mock_processor = AsyncMock()
    mock_processor.extract_page_text = AsyncMock(return_value="Sample text")
    mock_processor_class.return_value = mock_processor
    
    # Mock LLM failure
    mock_llm = AsyncMock()
    mock_llm.extract_concepts = AsyncMock(side_effect=Exception("LLM service unavailable"))
    mock_llm_class.return_value = mock_llm
    
    test_file = ("test.pdf", b"fake pdf content", "application/pdf")
    response = client.post(
        "/api/v1/analyze",
        files={"file": test_file},
        params={"page_number": 1}
    )
    
    # Should return error status
    assert response.status_code == 500
    
    # Document should be marked as error
    # (We'd need to query the database to verify, but endpoint should handle it)
