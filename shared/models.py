"""
Shared data models for both experiment and demo tracks
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

# Shared Concept Model
class Concept(BaseModel):
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

# Shared Domain Model
class Domain(BaseModel):
    id: str
    name: str
    description: str = ""
    sensitivity: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"
    definedBy: Optional[str] = None
    timestamp: Optional[str] = None

# Shared Relationship Model
class Relationship(BaseModel):
    source: str
    target: str
    predicate: str
    type: Literal["structural", "semantic", "hyperlink"] = "semantic"
    weight: Optional[float] = Field(ge=0.0, le=1.0, default=1.0)
    createdBy: Optional[str] = None
    timestamp: Optional[str] = None

# Shared Taxonomy Model
class Taxonomy(BaseModel):
    parent: str
    child: str
    type: Literal["is_a", "part_of"] = "is_a"
    createdBy: Optional[str] = None
    timestamp: Optional[str] = None

# Shared Agent Packet Model
class AgentPacket(BaseModel):
    sender: Literal["SYSTEM", "HARVESTER", "ARCHITECT", "CURATOR", "CRITIC", "ORCHESTRATOR", "OBSERVER"]
    recipient: str = "ALL"
    intent: Literal["INFO", "TASK_START", "TASK_COMPLETE", "CRITIQUE", "GRAPH_UPDATE", "ROUND_START", "HYPOTHESIS", "TOOL_USE", "EXPLAIN"] = "GRAPH_UPDATE"
    content: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    correlationId: Optional[str] = None

# Shared Document Model
class Document(BaseModel):
    id: str
    filename: str
    page_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None

# Shared Analysis Request
class AnalyzeRequest(BaseModel):
    image_base64: str
    page_number: int
    exclude_terms: List[str] = Field(default_factory=list)
    prompt_override: Optional[str] = None
    model_override: Optional[str] = None
    domain_hints: List[str] = Field(default_factory=list)

# Shared Experiment Request
class ExperimentRequest(BaseModel):
    prompt: str
    image_base64: Optional[str] = None
    model: Optional[str] = None
    provider: Optional[Literal["openai", "anthropic", "google"]] = None
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
