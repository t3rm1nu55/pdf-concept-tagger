"""Add Domain, Taxonomy, Hypothesis, Prior models

Revision ID: 002_add_models
Revises: 001_initial_mvp
Create Date: 2026-01-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_models'
down_revision = '001_initial_mvp'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create domains table
    op.create_table(
        'domains',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('sensitivity', sa.String(20), default='MEDIUM'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )
    
    # Create taxonomies table
    op.create_table(
        'taxonomies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('parent_concept_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('concepts.id'), nullable=False),
        sa.Column('child_concept_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('concepts.id'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),  # is_a, part_of
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Create hypotheses table
    op.create_table(
        'hypotheses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('target_concept_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('concepts.id'), nullable=False),
        sa.Column('claim', sa.Text, nullable=False),
        sa.Column('evidence', sa.Text, nullable=False),
        sa.Column('status', sa.String(20), default='PROPOSED'),  # PROPOSED, ACCEPTED, REJECTED
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )
    
    # Create priors table
    op.create_table(
        'priors',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id'), nullable=True),  # Can be global
        sa.Column('axiom', sa.Text, nullable=False),
        sa.Column('weight', sa.Float, default=1.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Create indexes
    op.create_index('idx_domains_document_id', 'domains', ['document_id'])
    op.create_index('idx_taxonomies_document_id', 'taxonomies', ['document_id'])
    op.create_index('idx_taxonomies_parent', 'taxonomies', ['parent_concept_id'])
    op.create_index('idx_taxonomies_child', 'taxonomies', ['child_concept_id'])
    op.create_index('idx_hypotheses_document_id', 'hypotheses', ['document_id'])
    op.create_index('idx_hypotheses_target', 'hypotheses', ['target_concept_id'])
    op.create_index('idx_priors_document_id', 'priors', ['document_id'])


def downgrade() -> None:
    op.drop_index('idx_priors_document_id', 'priors')
    op.drop_index('idx_hypotheses_target', 'hypotheses')
    op.drop_index('idx_hypotheses_document_id', 'hypotheses')
    op.drop_index('idx_taxonomies_child', 'taxonomies')
    op.drop_index('idx_taxonomies_parent', 'taxonomies')
    op.drop_index('idx_taxonomies_document_id', 'taxonomies')
    op.drop_index('idx_domains_document_id', 'domains')
    op.drop_table('priors')
    op.drop_table('hypotheses')
    op.drop_table('taxonomies')
    op.drop_table('domains')
