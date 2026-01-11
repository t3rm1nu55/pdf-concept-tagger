"""
PDF Analysis Endpoint

MVP: Upload PDF and extract concepts using HARVESTER agent.
Returns AgentPacket format for frontend compatibility.
"""

import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import json
from app.core.logging import logger

from app.database.postgres import get_db
from app.models.concept import Document, Concept
from app.models.agent_packet import AgentPacket, AgentPacketContent, ConceptContent
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
    
    Returns AgentPacket format (streaming) for frontend compatibility.
    MVP: Processes single page, extracts concepts using HARVESTER agent.
    """
    document_id = uuid.uuid4()
    document = None
    
    async def generate_agent_packets():
        nonlocal document_id, document
        
        try:
            logger.info(f"Processing PDF: {file.filename}, page {page_number}")
            
            # 1. Save uploaded file
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
            
            # 3. Send ROUND_START packet
            round_start_packet = AgentPacket(
                sender="SYSTEM",
                recipient="",
                intent="ROUND_START",
                content=AgentPacketContent(
                    round_id=1,
                    round_name="Auto-Harvest",
                    log=f"Starting analysis of {file.filename}, page {page_number}"
                )
            )
            yield json.dumps(round_start_packet.model_dump()) + "\n"
            
            # 4. Process PDF page
            processor = PDFProcessor()
            page_text = await processor.extract_page_text(file_path, page_number)
            
            if not page_text:
                error_packet = AgentPacket(
                    sender="SYSTEM",
                    recipient="",
                    intent="INFO",
                    content=AgentPacketContent(
                        log=f"Error: Could not extract text from page {page_number}"
                    )
                )
                yield json.dumps(error_packet.model_dump()) + "\n"
                return
            
            # 5. Extract concepts using HARVESTER agent
            try:
                llm = CognizantProxyLLM()
                concepts_data = await llm.extract_concepts(page_text)
            except Exception as e:
                logger.error(f"Error extracting concepts: {e}", exc_info=True)
                error_packet = AgentPacket(
                    sender="SYSTEM",
                    recipient="",
                    intent="INFO",
                    content=AgentPacketContent(
                        log=f"Error extracting concepts: {str(e)}"
                    )
                )
                yield json.dumps(error_packet.model_dump()) + "\n"
                return
            
            # 6. Store concepts and send AgentPacket updates
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
                    source_location={"page": page_number},
                    ui_group=concept_data.get("ui_group", "General")
                )
                db.add(concept)
                db.flush()  # Flush to get concept ID
                stored_concepts.append(concept)
                
                # Create AgentPacket for concept
                concept_packet = AgentPacket(
                    sender="HARVESTER",
                    recipient="",
                    intent="GRAPH_UPDATE",
                    content=AgentPacketContent(
                        concept=ConceptContent(
                            id=str(concept.id),
                            term=concept.term,
                            type=concept.type,
                            dataType=concept.data_type,
                            category=concept.category or "",
                            explanation=concept.explanation or "",
                            confidence=concept.confidence,
                            boundingBox=concept.source_location.get("boundingBox") if concept.source_location else None,
                            ui_group=concept.ui_group or "General"
                        ),
                        log=f"Extracted concept: {concept.term}"
                    )
                )
                
                # Send via streaming response
                yield json.dumps(concept_packet.model_dump()) + "\n"
                
                # Also send via WebSocket
                await send_concept_update(document_id, concept)
            
            db.commit()
            
            # 7. Update document status
            document.status = "completed"
            document.page_count = 1  # MVP: Single page
            db.commit()
            
            # 8. Send TASK_COMPLETE packet
            complete_packet = AgentPacket(
                sender="SYSTEM",
                recipient="",
                intent="TASK_COMPLETE",
                content=AgentPacketContent(
                    log=f"Analysis complete. Extracted {len(stored_concepts)} concepts."
                )
            )
            yield json.dumps(complete_packet.model_dump()) + "\n"
            
        except Exception as e:
            logger.error(f"Error processing PDF {file.filename}: {e}", exc_info=True)
            if document:
                try:
                    document.status = "error"
                    db.commit()
                except Exception:
                    pass
            
            error_packet = AgentPacket(
                sender="SYSTEM",
                recipient="",
                intent="INFO",
                content=AgentPacketContent(
                    log=f"Error processing PDF: {str(e)}"
                )
            )
            yield json.dumps(error_packet.model_dump()) + "\n"
    
    return StreamingResponse(
        generate_agent_packets(),
        media_type="application/json"
    )


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
