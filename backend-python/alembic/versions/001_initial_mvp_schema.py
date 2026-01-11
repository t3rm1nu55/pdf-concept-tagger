"""Initial MVP schema

Revision ID: 001_initial_mvp
Revises: 
Create Date: 2026-01-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_mvp'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('file_path', sa.Text),
        sa.Column('file_size', sa.Integer),
        sa.Column('page_count', sa.Integer),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )
    
    # Create concepts table
    op.create_table(
        'concepts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('term', sa.String(500), nullable=False),
        sa.Column('type', sa.String(100), nullable=False),
        sa.Column('node_group', sa.String(50), default='concept'),
        sa.Column('data_type', sa.String(50)),
        sa.Column('category', sa.String(200)),
        sa.Column('explanation', sa.Text),
        sa.Column('confidence', sa.Float, nullable=False),
        sa.Column('assessment', sa.String(20), default='usually_true'),
        sa.Column('source_location', postgresql.JSON),
        sa.Column('ui_group', sa.String(100)),
        sa.Column('extracted_by', sa.String(100)),
        sa.Column('concept_metadata', postgresql.JSON),  # Renamed from 'metadata' (reserved in SQLAlchemy)
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )
    
    # Create relationships table
    op.create_table(
        'relationships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('source_concept_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('concepts.id'), nullable=False),
        sa.Column('target_concept_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('concepts.id'), nullable=False),
        sa.Column('type', sa.String(100), nullable=False),
        sa.Column('predicate', sa.String(200)),
        sa.Column('confidence', sa.Float),
        sa.Column('strength', sa.Float),
        sa.Column('relationship_metadata', postgresql.JSON),  # Renamed from 'metadata' (reserved in SQLAlchemy)
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Create indexes
    op.create_index('idx_concepts_document_id', 'concepts', ['document_id'])
    op.create_index('idx_concepts_term', 'concepts', ['term'])
    op.create_index('idx_concepts_type', 'concepts', ['type'])
    op.create_index('idx_concepts_confidence', 'concepts', ['confidence'])
    op.create_index('idx_relationships_source', 'relationships', ['source_concept_id'])
    op.create_index('idx_relationships_target', 'relationships', ['target_concept_id'])


def downgrade() -> None:
    op.drop_index('idx_relationships_target', 'relationships')
    op.drop_index('idx_relationships_source', 'relationships')
    op.drop_index('idx_concepts_confidence', 'concepts')
    op.drop_index('idx_concepts_type', 'concepts')
    op.drop_index('idx_concepts_term', 'concepts')
    op.drop_index('idx_concepts_document_id', 'concepts')
    op.drop_table('relationships')
    op.drop_table('concepts')
    op.drop_table('documents')
