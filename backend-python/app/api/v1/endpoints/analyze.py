"""
PDF Analysis Endpoint

MVP: Upload PDF and extract concepts using HARVESTER agent.
"""

import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import json

from app.database.postgres import get_db
from app.models.concept import Document, Concept
from app.services.cognizant_proxy import CognizantProxyLLM
from app.services.pdf_processor import PDFProcessor
from app.api.v1.endpoints.websocket import send_concept_update

router = APIRouter()


@router.post("/analyze")
async def analyze_pdf(
    file: UploadFile = File(...),
    page_number: int = 1,
    db: Session = Depends(get_db)
):
    """
    Analyze PDF page and extract concepts.
    
    MVP: Processes single page, extracts concepts using HARVESTER agent.
    """
    try:
        # 1. Save uploaded file
        document_id = uuid.uuid4()
        file_path = f"/tmp/{document_id}_{file.filename}"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 2. Create document record
        document = Document(
            id=document_id,
            filename=file.filename,
            file_path=file_path,
            file_size=len(content),
            status="processing"
        )
        db.add(document)
        db.commit()
        
        # 3. Process PDF page
        processor = PDFProcessor()
        page_text = await processor.extract_page_text(file_path, page_number)
        
        if not page_text:
            raise HTTPException(status_code=400, detail=f"Could not extract text from page {page_number}")
        
        # 4. Extract concepts using HARVESTER agent
        llm = CognizantProxyLLM()
        concepts_data = await llm.extract_concepts(page_text)
        
        # 5. Store concepts and send WebSocket updates
        stored_concepts = []
        for concept_data in concepts_data:
            concept = Concept(
                document_id=document_id,
                term=concept_data.get("term", ""),
                type=concept_data.get("type", "concept"),
                node_group="concept",
                data_type=concept_data.get("dataType"),
                category=concept_data.get("category", ""),
                explanation=concept_data.get("explanation", ""),
                confidence=float(concept_data.get("confidence", 0.5)),
                assessment="usually_true",  # MVP: Default assessment
                extracted_by="HARVESTER",
                source_location={"page": page_number}
            )
            db.add(concept)
            db.flush()  # Flush to get concept ID
            stored_concepts.append(concept)
            
            # Send WebSocket update
            await send_concept_update(document_id, concept)
        
        db.commit()
        
        # 6. Update document status
        document.status = "completed"
        document.page_count = 1  # MVP: Single page
        db.commit()
        
        # 7. Return results
        return {
            "document_id": str(document_id),
            "concepts": [
                {
                    "id": str(c.id),
                    "term": c.term,
                    "type": c.type,
                    "confidence": c.confidence,
                    "assessment": c.assessment
                }
                for c in stored_concepts
            ],
            "total_concepts": len(stored_concepts)
        }
        
    except Exception as e:
        # Update document status on error
        if 'document' in locals():
            document.status = "error"
            db.commit()
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@router.get("/analyze/{document_id}/status")
async def get_analysis_status(
    document_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get analysis status for a document."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    concept_count = db.query(Concept).filter(Concept.document_id == document_id).count()
    
    return {
        "document_id": str(document_id),
        "status": document.status,
        "concepts_extracted": concept_count,
        "created_at": document.created_at.isoformat() if document.created_at else None
    }
