"""
PDF Analysis Endpoint

MVP: Upload PDF and extract concepts using HARVESTER agent.
Returns AgentPacket format for frontend compatibility.

Supports both:
- PDF file upload (multipart/form-data)
- Image base64 (JSON) - for prototype compatibility
"""

import uuid
import base64
import io
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from pydantic import BaseModel
from app.core.logging import logger

from app.database.postgres import get_db
from app.models.concept import Document, Concept
from app.models.agent_packet import AgentPacket, AgentPacketContent, ConceptContent
from app.services.cognizant_proxy import CognizantProxyLLM
from app.services.pdf_processor import PDFProcessor
from app.api.v1.endpoints.websocket import send_concept_update

router = APIRouter()


class AnalyzeImageRequest(BaseModel):
    """Request model for image-based analysis (prototype compatibility)."""
    image: str  # Base64 encoded image
    pageNumber: int = 1
    excludeTerms: List[str] = []


async def process_text_extraction(
    text: str,
    document_id: uuid.UUID,
    page_number: int,
    db: Session,
    exclude_terms: List[str] = None
):
    """
    Extract concepts from text and yield AgentPackets.
    
    Shared logic for both PDF and image-based analysis.
    """
    if exclude_terms is None:
        exclude_terms = []
    
    # Extract concepts using HARVESTER agent
    try:
        llm = CognizantProxyLLM()
        concepts_data = await llm.extract_concepts(text)
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
    
    # Filter out excluded terms
    filtered_concepts = [
        c for c in concepts_data
        if c.get("term", "").lower() not in [t.lower() for t in exclude_terms]
    ]
    
    # Store concepts and send AgentPacket updates
    for concept_data in filtered_concepts:
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


@router.post("/analyze")
async def analyze_pdf(
    file: Optional[UploadFile] = File(None),
    page_number: int = 1,
    request: Optional[AnalyzeImageRequest] = Body(None),
    db: Session = Depends(get_db)
):
    """
    Analyze PDF page or image and extract concepts.
    
    Supports two modes:
    1. PDF file upload (multipart/form-data): file + page_number
    2. Image base64 (JSON): request body with image + pageNumber
    
    Returns streaming AgentPacket format for frontend compatibility.
    """
    document_id = uuid.uuid4()
    document = None
    
    async def generate_agent_packets():
        nonlocal document_id, document
        
        try:
            # Determine input type
            if request and request.image:
                # Image-based analysis (prototype compatibility)
                logger.info(f"Processing image analysis, page {request.pageNumber}")
                
                # Decode base64 image
                try:
                    # Remove data URL prefix if present
                    image_data = request.image
                    if "," in image_data:
                        image_data = image_data.split(",", 1)[1]
                    
                    image_bytes = base64.b64decode(image_data)
                    
                    # For MVP, we'll extract text from image using OCR
                    # For now, create a placeholder document
                    document = Document(
                        id=document_id,
                        filename=f"image_page_{request.pageNumber}.png",
                        file_path=None,
                        file_size=len(image_bytes),
                        status="processing"
                    )
                    db.add(document)
                    db.commit()
                    
                    # Send ROUND_START packet
                    round_start_packet = AgentPacket(
                        sender="SYSTEM",
                        recipient="",
                        intent="ROUND_START",
                        content=AgentPacketContent(
                            round_id=1,
                            round_name="Auto-Harvest",
                            log=f"Starting image analysis, page {request.pageNumber}"
                        )
                    )
                    yield json.dumps(round_start_packet.model_dump()) + "\n"
                    
                    # MVP: For image-based, we'd need OCR
                    # For now, return a placeholder concept
                    # TODO: Integrate OCR (Tesseract, Google Vision, etc.)
                    text = ""  # Placeholder - would be OCR result
                    
                    if not text:
                        # For MVP, skip image processing
                        complete_packet = AgentPacket(
                            sender="SYSTEM",
                            recipient="",
                            intent="TASK_COMPLETE",
                            content=AgentPacketContent(
                                log="Image analysis requires OCR (not implemented in MVP). Use PDF upload instead."
                            )
                        )
                        yield json.dumps(complete_packet.model_dump()) + "\n"
                        return
                    
                    # Process text extraction
                    async for packet in process_text_extraction(
                        text,
                        document_id,
                        request.pageNumber,
                        db,
                        request.excludeTerms
                    ):
                        yield packet
                    
                except Exception as e:
                    logger.error(f"Error processing image: {e}", exc_info=True)
                    error_packet = AgentPacket(
                        sender="SYSTEM",
                        recipient="",
                        intent="INFO",
                        content=AgentPacketContent(
                            log=f"Error processing image: {str(e)}"
                        )
                    )
                    yield json.dumps(error_packet.model_dump()) + "\n"
                    return
                    
            elif file:
                # PDF file upload
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
                
                # 5. Process text extraction
                async for packet in process_text_extraction(
                    page_text,
                    document_id,
                    page_number,
                    db
                ):
                    yield packet
                
                # 6. Update document status
                document.status = "completed"
                document.page_count = 1  # MVP: Single page
                db.commit()
                
            else:
                # No input provided
                error_packet = AgentPacket(
                    sender="SYSTEM",
                    recipient="",
                    intent="INFO",
                    content=AgentPacketContent(
                        log="Error: No file or image provided"
                    )
                )
                yield json.dumps(error_packet.model_dump()) + "\n"
                return
            
            # 7. Send TASK_COMPLETE packet
            complete_packet = AgentPacket(
                sender="SYSTEM",
                recipient="",
                intent="TASK_COMPLETE",
                content=AgentPacketContent(
                    log="Analysis complete."
                )
            )
            yield json.dumps(complete_packet.model_dump()) + "\n"
            
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
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
                    log=f"Error processing request: {str(e)}"
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
