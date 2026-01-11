"""
Tests for Database Models and Operations

MVP: Test database models and CRUD operations.
"""

import pytest
import uuid
from app.models.concept import Document, Concept, Relationship
from app.database.postgres import get_db


def test_create_document(db_session):
    """Test creating a document."""
    doc = Document(
        id=uuid.uuid4(),
        filename="test.pdf",
        file_path="/tmp/test.pdf",
        file_size=1024,
        status="pending"
    )
    db_session.add(doc)
    db_session.commit()
    
    assert doc.id is not None
    assert doc.filename == "test.pdf"
    assert doc.status == "pending"


def test_create_concept(db_session, sample_concept_data):
    """Test creating a concept."""
    # Create document first
    doc = Document(
        id=uuid.uuid4(),
        filename="test.pdf",
        status="completed"
    )
    db_session.add(doc)
    db_session.commit()
    
    # Create concept
    concept = Concept(
        document_id=doc.id,
        **sample_concept_data
    )
    db_session.add(concept)
    db_session.commit()
    
    assert concept.id is not None
    assert concept.term == "GDPR"
    assert concept.document_id == doc.id
    assert concept.confidence == 0.95


def test_create_relationship(db_session, sample_concept_data):
    """Test creating a relationship between concepts."""
    # Create document
    doc = Document(
        id=uuid.uuid4(),
        filename="test.pdf",
        status="completed"
    )
    db_session.add(doc)
    db_session.commit()
    
    # Create two concepts
    concept1 = Concept(
        document_id=doc.id,
        term="GDPR",
        type="concept",
        confidence=0.95,
        **{k: v for k, v in sample_concept_data.items() if k not in ["term"]}
    )
    concept2 = Concept(
        document_id=doc.id,
        term="Data Protection",
        type="concept",
        confidence=0.90,
        **{k: v for k, v in sample_concept_data.items() if k not in ["term"]}
    )
    db_session.add(concept1)
    db_session.add(concept2)
    db_session.commit()
    
    # Create relationship
    relationship = Relationship(
        source_concept_id=concept1.id,
        target_concept_id=concept2.id,
        type="relates_to",
        confidence=0.85
    )
    db_session.add(relationship)
    db_session.commit()
    
    assert relationship.id is not None
    assert relationship.source_concept_id == concept1.id
    assert relationship.target_concept_id == concept2.id


def test_query_concepts_by_document(db_session, sample_concept_data):
    """Test querying concepts by document."""
    # Create document
    doc = Document(
        id=uuid.uuid4(),
        filename="test.pdf",
        status="completed"
    )
    db_session.add(doc)
    db_session.commit()
    
    # Create multiple concepts
    for term in ["GDPR", "Data Protection", "Privacy"]:
        concept = Concept(
            document_id=doc.id,
            term=term,
            type="concept",
            confidence=0.9,
            **{k: v for k, v in sample_concept_data.items() if k not in ["term"]}
        )
        db_session.add(concept)
    db_session.commit()
    
    # Query concepts
    concepts = db_session.query(Concept).filter(Concept.document_id == doc.id).all()
    
    assert len(concepts) == 3
    assert all(c.document_id == doc.id for c in concepts)
