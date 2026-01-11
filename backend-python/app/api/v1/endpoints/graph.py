"""
Graph Query Endpoints

MVP: Return graph data for visualization (nodes and edges).
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.database.postgres import get_db
from app.models.concept import Concept, Relationship

router = APIRouter()


@router.get("/graph")
async def get_graph(
    document_id: Optional[UUID] = Query(None, description="Filter by document ID"),
    node_ids: Optional[List[UUID]] = Query(None, description="Filter by specific node IDs"),
    relationship_types: Optional[List[str]] = Query(None, description="Filter by relationship types"),
    depth: int = Query(2, ge=1, le=5, description="Traversal depth"),
    db: Session = Depends(get_db)
):
    """
    Get graph data for visualization.
    
    MVP: Returns nodes (concepts) and edges (relationships) from PostgreSQL.
    Future: Will use Neo4j for graph queries.
    """
    # Get nodes (concepts)
    query = db.query(Concept)
    if document_id:
        query = query.filter(Concept.document_id == document_id)
    if node_ids:
        query = query.filter(Concept.id.in_(node_ids))
    
    concepts = query.all()
    
    # Get edges (relationships)
    rel_query = db.query(Relationship)
    if document_id:
        # Filter relationships by concepts in this document
        concept_ids = [c.id for c in concepts]
        rel_query = rel_query.filter(
            Relationship.source_concept_id.in_(concept_ids) |
            Relationship.target_concept_id.in_(concept_ids)
        )
    if relationship_types:
        rel_query = rel_query.filter(Relationship.type.in_(relationship_types))
    
    relationships = rel_query.all()
    
    # Format nodes
    nodes = [
        {
            "id": str(c.id),
            "label": c.term,
            "type": c.type,
            "node_group": c.node_group,
            "properties": {
                "confidence": c.confidence,
                "assessment": c.assessment,
                "data_type": c.data_type,
                "category": c.category
            }
        }
        for c in concepts
    ]
    
    # Format edges
    edges = [
        {
            "id": str(r.id),
            "source": str(r.source_concept_id),
            "target": str(r.target_concept_id),
            "type": r.type,
            "properties": {
                "predicate": r.predicate,
                "confidence": r.confidence,
                "strength": r.strength
            }
        }
        for r in relationships
    ]
    
    return {
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "document_id": str(document_id) if document_id else None
        }
    }


@router.get("/graph/paths")
async def get_paths(
    source: UUID = Query(..., description="Source node ID"),
    target: UUID = Query(..., description="Target node ID"),
    max_length: int = Query(5, ge=1, le=10, description="Maximum path length"),
    relationship_types: Optional[List[str]] = Query(None, description="Allowed relationship types"),
    db: Session = Depends(get_db)
):
    """
    Find paths between two nodes.
    
    MVP: Simple path finding using PostgreSQL.
    Future: Will use Neo4j for efficient path finding.
    """
    # MVP: Simple implementation - find direct relationships
    # Future: Use Neo4j for multi-hop path finding
    
    direct_rel = db.query(Relationship).filter(
        Relationship.source_concept_id == source,
        Relationship.target_concept_id == target
    ).first()
    
    if direct_rel:
        return {
            "paths": [
                {
                    "nodes": [str(source), str(target)],
                    "edges": [str(direct_rel.id)],
                    "length": 1,
                    "confidence": direct_rel.confidence or 0.5
                }
            ],
            "shortest_path": {
                "nodes": [str(source), str(target)],
                "length": 1
            }
        }
    
    # No direct path found
    return {
        "paths": [],
        "shortest_path": None
    }
