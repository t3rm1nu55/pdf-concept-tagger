"""
Shared data models for both experiment and demo tracks.

These models are used across both Track 1 (experimentation) and Track 2 (demo machine)
to ensure consistency in data structures.

See PROJECT_RULES.md for development guidelines.
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class Concept(BaseModel):
    """
    Concept model representing extracted entities/concepts from documents.
    
    Used by HARVESTER agent to represent extracted concepts with confidence scores
    and metadata.
    
    Attributes:
        id: Unique identifier for the concept
        term: The actual text/name of the concept
        type: "concept" or "hypernode"
        dataType: Type of entity (entity, date, location, etc.)
        category: Classification category
        explanation: Brief description of what this concept is
        confidence: Confidence score 0.0-1.0
        boundingBox: [ymin, xmin, ymax, xmax] if detectable in image
        ui_group: Grouping category for UI display
        extractedBy: Agent that extracted this concept
        timestamp: ISO timestamp of extraction
    """
    id: str
    term: str
    type: Literal["concept", "hypernode"]
    dataType: Optional[Literal["entity", "date", "location", "organization", "person", "money", "legal", "condition"]] = None
    category: str = ""
    explanation: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    boundingBox: Optional[List[float]] = None
    ui_group: str = "General"
    extractedBy: Optional[str] = None
    timestamp: Optional[str] = None

class Domain(BaseModel):
    """
    Domain model representing broad domain structures.
    
    Used by ARCHITECT agent to define domains (e.g., "Legal Framework", "Financial").
    """
    id: str
    name: str
    description: str = ""
    sensitivity: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"
    definedBy: Optional[str] = None
    timestamp: Optional[str] = None


class Relationship(BaseModel):
    """
    Relationship model representing connections between concepts or domains.
    
    Used by ARCHITECT agent to create semantic relationships.
    """
    source: str
    target: str
    predicate: str
    type: Literal["structural", "semantic", "hyperlink"] = "semantic"
    weight: Optional[float] = Field(ge=0.0, le=1.0, default=1.0)
    createdBy: Optional[str] = None
    timestamp: Optional[str] = None


class Taxonomy(BaseModel):
    """
    Taxonomy model representing hierarchical relationships.
    
    Used by CURATOR agent to organize taxonomical hierarchies.
    """
    parent: str
    child: str
    type: Literal["is_a", "part_of"] = "is_a"
    createdBy: Optional[str] = None
    timestamp: Optional[str] = None


class AgentPacket(BaseModel):
    """
    Agent Packet protocol for inter-agent communication.
    
    Standard format for messages between agents in the multi-agent system.
    Used for streaming updates, task coordination, and state management.
    
    Attributes:
        sender: Agent that sent the packet
        recipient: Target agent (or "ALL" for broadcast)
        intent: Purpose of the packet (GRAPH_UPDATE, TASK_COMPLETE, etc.)
        content: Payload data (varies by intent)
        timestamp: ISO timestamp of packet creation
        correlationId: Optional correlation ID for tracking related packets
    """
    sender: Literal["SYSTEM", "HARVESTER", "ARCHITECT", "CURATOR", "CRITIC", "ORCHESTRATOR", "OBSERVER"]
    recipient: str = "ALL"
    intent: Literal["INFO", "TASK_START", "TASK_COMPLETE", "CRITIQUE", "GRAPH_UPDATE", "ROUND_START", "HYPOTHESIS", "TOOL_USE", "EXPLAIN"] = "GRAPH_UPDATE"
    content: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    correlationId: Optional[str] = None


class Document(BaseModel):
    """
    Document model representing uploaded PDF documents.
    """
    id: str
    filename: str
    page_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None


class AnalyzeRequest(BaseModel):
    """
    Request model for PDF analysis endpoint.
    
    Used by POST /api/v1/analyze endpoint.
    """
    image_base64: str
    page_number: int
    exclude_terms: List[str] = Field(default_factory=list)
    prompt_override: Optional[str] = None
    model_override: Optional[str] = None
    domain_hints: List[str] = Field(default_factory=list)


class ExperimentRequest(BaseModel):
    """
    Request model for prompt experimentation endpoint.
    
    Used by POST /api/v1/prompts/experiment endpoint.
    """
    prompt: str
    image_base64: Optional[str] = None
    model: Optional[str] = None
    provider: Optional[Literal["openai", "anthropic", "google"]] = None
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
