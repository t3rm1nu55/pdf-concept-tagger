"""
Concept Model

MVP: Basic concept model for PostgreSQL storage.
"""

from sqlalchemy import Column, String, Float, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database.postgres import Base


class Document(Base):
    """Document model."""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    file_path = Column(Text)
    file_size = Column(Integer)
    page_count = Column(Integer)
    status = Column(String(50), default="pending")  # pending, processing, completed, error
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Concept(Base):
    """Concept model."""
    __tablename__ = "concepts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    term = Column(String(500), nullable=False)
    type = Column(String(100), nullable=False)  # concept, hypernode
    node_group = Column(String(50), default="concept")  # concept, hypernode, domain, prior
    data_type = Column(String(50))  # entity, date, location, etc.
    category = Column(String(200))
    explanation = Column(Text)
    confidence = Column(Float, nullable=False)
    assessment = Column(String(20), default="usually_true")  # always_true, usually_true, sometimes_true
    source_location = Column(JSON)  # {page, section, x, y}
    ui_group = Column(String(100))
    extracted_by = Column(String(100))  # HARVESTER, ARCHITECT, etc.
    concept_metadata = Column(JSON)  # Renamed from 'metadata' (reserved in SQLAlchemy)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Relationship(Base):
    """Relationship model."""
    __tablename__ = "relationships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id"), nullable=False)
    target_concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id"), nullable=False)
    type = Column(String(100), nullable=False)  # relates_to, part_of, is_a, etc.
    predicate = Column(String(200))
    confidence = Column(Float)
    strength = Column(Float)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
