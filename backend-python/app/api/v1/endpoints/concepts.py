"""
Concept Query Endpoints

MVP: Query concepts from database.
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.database.postgres import get_db
from app.models.concept import Concept, Document

router = APIRouter()


@router.get("/concepts")
async def get_concepts(
    document_id: Optional[UUID] = Query(None, description="Filter by document ID"),
    type: Optional[str] = Query(None, description="Filter by concept type"),
    confidence_min: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db)
):
    """
    Get concepts with filtering and pagination.
    
    MVP: Basic filtering and pagination.
    """
    query = db.query(Concept)
    
    # Apply filters
    if document_id:
        query = query.filter(Concept.document_id == document_id)
    if type:
        query = query.filter(Concept.type == type)
    if confidence_min is not None:
        query = query.filter(Concept.confidence >= confidence_min)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    concepts = query.offset(offset).limit(page_size).all()
    
    return {
        "concepts": [
            {
                "id": str(c.id),
                "term": c.term,
                "type": c.type,
                "node_group": c.node_group,
                "data_type": c.data_type,
                "confidence": c.confidence,
                "assessment": c.assessment,
                "explanation": c.explanation,
                "source_location": c.source_location,
                "extracted_by": c.extracted_by,
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in concepts
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }
    }


@router.get("/concepts/{concept_id}")
async def get_concept(
    concept_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific concept by ID."""
    concept = db.query(Concept).filter(Concept.id == concept_id).first()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")
    
    return {
        "id": str(concept.id),
        "term": concept.term,
        "type": concept.type,
        "node_group": concept.node_group,
        "data_type": concept.data_type,
        "category": concept.category,
        "explanation": concept.explanation,
        "confidence": concept.confidence,
        "assessment": concept.assessment,
        "source_location": concept.source_location,
        "ui_group": concept.ui_group,
        "extracted_by": concept.extracted_by,
        "metadata": concept.concept_metadata,
        "document_id": str(concept.document_id),
        "created_at": concept.created_at.isoformat() if concept.created_at else None,
        "updated_at": concept.updated_at.isoformat() if concept.updated_at else None
    }
