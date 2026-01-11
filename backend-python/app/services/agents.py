"""
Agent Services

Basic agent implementations for MVP.
These are minimal stubs that can be expanded later.
"""

from typing import List, Dict, Optional
from app.models.agent_packet import AgentPacket, AgentPacketContent, DomainContent, TaxonomyContent, HypothesisContent
from app.core.logging import logger


class ArchitectAgent:
    """ARCHITECT agent - Creates domains (hub nodes)."""
    
    def __init__(self):
        self.name = "ARCHITECT"
    
    async def analyze_domains(self, concepts: List[Dict]) -> List[AgentPacket]:
        """
        Analyze concepts and identify domains.
        
        MVP: Returns empty list (stub).
        Future: Use LLM to identify domain structures.
        """
        logger.debug(f"ARCHITECT: Analyzing {len(concepts)} concepts for domains")
        # MVP: No domain detection yet
        return []
    
    def create_domain_packet(self, domain_id: str, name: str, description: str, sensitivity: str = "MEDIUM") -> AgentPacket:
        """Create an AgentPacket for a domain."""
        return AgentPacket(
            sender="ARCHITECT",
            recipient="",
            intent="GRAPH_UPDATE",
            content=AgentPacketContent(
                domain=DomainContent(
                    id=domain_id,
                    name=name,
                    description=description,
                    sensitivity=sensitivity
                ),
                log=f"ARCHITECT defined domain: {name}"
            )
        )


class CuratorAgent:
    """CURATOR agent - Builds taxonomies (hierarchical links)."""
    
    def __init__(self):
        self.name = "CURATOR"
    
    async def build_taxonomies(self, concepts: List[Dict]) -> List[AgentPacket]:
        """
        Build taxonomies from concepts.
        
        MVP: Returns empty list (stub).
        Future: Use LLM to identify hierarchical relationships.
        """
        logger.debug(f"CURATOR: Building taxonomies from {len(concepts)} concepts")
        # MVP: No taxonomy building yet
        return []
    
    def create_taxonomy_packet(self, parent_id: str, child_id: str, taxonomy_type: str = "is_a") -> AgentPacket:
        """Create an AgentPacket for a taxonomy."""
        return AgentPacket(
            sender="CURATOR",
            recipient="",
            intent="GRAPH_UPDATE",
            content=AgentPacketContent(
                taxonomy=TaxonomyContent(
                    parent=parent_id,
                    child=child_id,
                    type=taxonomy_type
                ),
                log=f"CURATOR created taxonomy: {child_id} {taxonomy_type} {parent_id}"
            )
        )


class CriticAgent:
    """CRITIC agent - Generates hypotheses and optimizations."""
    
    def __init__(self):
        self.name = "CRITIC"
    
    async def analyze_concepts(self, concepts: List[Dict]) -> List[AgentPacket]:
        """
        Analyze concepts and generate hypotheses.
        
        MVP: Returns empty list (stub).
        Future: Use LLM to generate hypotheses and critiques.
        """
        logger.debug(f"CRITIC: Analyzing {len(concepts)} concepts for hypotheses")
        # MVP: No hypothesis generation yet
        return []
    
    def create_hypothesis_packet(
        self,
        hypothesis_id: str,
        target_concept_id: str,
        claim: str,
        evidence: str,
        status: str = "PROPOSED"
    ) -> AgentPacket:
        """Create an AgentPacket for a hypothesis."""
        return AgentPacket(
            sender="CRITIC",
            recipient="",
            intent="HYPOTHESIS",
            content=AgentPacketContent(
                hypothesis=HypothesisContent(
                    id=hypothesis_id,
                    target_concept_id=target_concept_id,
                    claim=claim,
                    evidence=evidence,
                    status=status
                ),
                log=f"CRITIC proposed hypothesis: {claim}"
            )
        )


class ObserverAgent:
    """OBSERVER agent - Monitors system state."""
    
    def __init__(self):
        self.name = "OBSERVER"
    
    def create_info_packet(self, message: str) -> AgentPacket:
        """Create an INFO packet for system monitoring."""
        return AgentPacket(
            sender="OBSERVER",
            recipient="",
            intent="INFO",
            content=AgentPacketContent(
                log=message
            )
        )
