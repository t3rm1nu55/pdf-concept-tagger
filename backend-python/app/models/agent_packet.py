"""
AgentPacket Protocol Models

Matches the prototype's AgentPacket interface for frontend compatibility.
"""

from typing import Optional, Literal, List
from pydantic import BaseModel


# AgentPacket Content Models
class ConceptContent(BaseModel):
    """Concept content in AgentPacket."""
    id: str
    term: str
    type: Literal["concept", "hypernode"]
    dataType: Optional[Literal["entity", "date", "location", "organization", "person", "money", "legal", "condition"]] = None
    category: str = ""
    explanation: str = ""
    confidence: float
    boundingBox: Optional[List[float]] = None
    ui_group: Optional[str] = None


class DomainContent(BaseModel):
    """Domain content in AgentPacket."""
    id: str
    name: str
    description: str = ""
    sensitivity: Optional[Literal["LOW", "MEDIUM", "HIGH"]] = "MEDIUM"


class TaxonomyContent(BaseModel):
    """Taxonomy content in AgentPacket."""
    parent: str
    child: str
    type: Literal["is_a", "part_of"]


class PriorContent(BaseModel):
    """Prior (reality prior/axiom) content in AgentPacket."""
    id: str
    axiom: str
    weight: float = 1.0


class RelationshipContent(BaseModel):
    """Relationship content in AgentPacket."""
    source: str
    target: str
    predicate: str
    type: Optional[Literal["structural", "semantic", "hyperlink"]] = "semantic"


class HypothesisContent(BaseModel):
    """Hypothesis content in AgentPacket."""
    id: str
    target_concept_id: str
    claim: str
    evidence: str
    status: Literal["PROPOSED", "ACCEPTED", "REJECTED"] = "PROPOSED"


class OptimizationContent(BaseModel):
    """Optimization content in AgentPacket."""
    score: float
    suggestion: str
    focus_nodes: List[str] = []


class AgentPacketContent(BaseModel):
    """Content of an AgentPacket."""
    log: Optional[str] = None
    round_id: Optional[int] = None
    round_name: Optional[str] = None
    
    # Graph update content
    concept: Optional[ConceptContent] = None
    domain: Optional[DomainContent] = None
    taxonomy: Optional[TaxonomyContent] = None
    prior: Optional[PriorContent] = None
    relationship: Optional[RelationshipContent] = None
    hypothesis: Optional[HypothesisContent] = None
    optimization: Optional[OptimizationContent] = None


class AgentPacket(BaseModel):
    """AgentPacket protocol - matches prototype interface."""
    sender: Literal["SYSTEM", "HARVESTER", "ARCHITECT", "CRITIC", "ORCHESTRATOR", "OBSERVER", "CURATOR"]
    recipient: str = ""
    intent: Literal["INFO", "TASK_START", "TASK_COMPLETE", "CRITIQUE", "GRAPH_UPDATE", "ROUND_START", "HYPOTHESIS", "TOOL_USE", "EXPLAIN"]
    content: AgentPacketContent
