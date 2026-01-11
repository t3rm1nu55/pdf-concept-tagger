"""
Integration Example: Using LlamaIndex with Existing Agents

This module shows how to integrate LlamaIndex RAG, Knowledge Graph,
and Query Engines with your existing agent system.

Usage:
    # In your agent coordinator or service
    from llamaindex_integration_example import ConceptRAGTool, ConceptKGTool
    
    # Add as tools to your agents
    rag_tool = ConceptRAGTool()
    kg_tool = ConceptKGTool()
    
    # Use in agent workflow
    agent = FunctionAgent(tools=[rag_tool, kg_tool], ...)
"""

import os
from typing import List, Optional, Dict, Any
from llama_index.core.tools import FunctionTool
from llama_index_rag_service import RAGService
from llama_index_kg_service import KGService
from shared.models import Concept


class ConceptRAGTool:
    """
    RAG tool that can be used by agents to query concepts semantically.
    
    This wraps the RAGService and exposes it as a tool that agents can call.
    """
    
    def __init__(
        self,
        pinecone_api_key: Optional[str] = None,
        pinecone_index_name: str = "concepts",
        openai_api_key: Optional[str] = None,
    ):
        """Initialize RAG tool."""
        self.rag_service = RAGService(
            pinecone_api_key=pinecone_api_key,
            pinecone_index_name=pinecone_index_name,
            openai_api_key=openai_api_key,
        )
    
    async def query_concepts(
        self,
        query: str,
        similarity_top_k: int = 10,
        required_keywords: Optional[List[str]] = None,
    ) -> str:
        """
        Query concepts using semantic search.
        
        Args:
            query: Natural language query about concepts
            similarity_top_k: Number of results to return
            required_keywords: Optional keywords that must be present
            
        Returns:
            Formatted response with concepts and sources
        """
        result = await self.rag_service.query(
            query_text=query,
            similarity_top_k=similarity_top_k,
            required_keywords=required_keywords,
        )
        
        # Format response for agent
        response_parts = [f"Query: {query}\n\nResponse: {result['response']}\n"]
        
        if result["source_concepts"]:
            response_parts.append("\nSource Concepts:")
            for i, concept in enumerate(result["source_concepts"][:5], 1):
                response_parts.append(
                    f"{i}. {concept['term']} ({concept['type']}) - "
                    f"Confidence: {concept['confidence']:.2f}, "
                    f"Group: {concept['ui_group']}"
                )
        
        return "\n".join(response_parts)
    
    async def index_concepts_batch(
        self,
        concepts: List[Concept],
    ) -> str:
        """
        Index a batch of concepts into the vector store.
        
        Args:
            concepts: List of concepts to index
            
        Returns:
            Status message
        """
        result = await self.rag_service.index_concepts(concepts)
        
        if result["indexed"] > 0:
            return f"Successfully indexed {result['indexed']} concepts."
        else:
            return f"Failed to index concepts. Errors: {result.get('errors', [])}"
    
    def get_tools(self) -> List[FunctionTool]:
        """
        Get LlamaIndex FunctionTool instances for agent use.
        
        Returns:
            List of tools that can be added to agents
        """
        return [
            FunctionTool.from_defaults(
                fn=self.query_concepts,
                name="query_concepts_semantic",
                description=(
                    "Query concepts using semantic search. "
                    "Use this to find concepts by meaning, similarity, or description. "
                    "Returns concepts with their metadata and confidence scores."
                ),
            ),
            FunctionTool.from_defaults(
                fn=self.index_concepts_batch,
                name="index_concepts",
                description=(
                    "Index concepts into the vector store for semantic search. "
                    "Use this after extracting new concepts to make them searchable."
                ),
            ),
        ]


class ConceptKGTool:
    """
    Knowledge Graph tool that can be used by agents to query relationships.
    
    This wraps the KGService and exposes it as a tool that agents can call.
    """
    
    def __init__(
        self,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None,
        openai_api_key: Optional[str] = None,
    ):
        """Initialize KG tool."""
        self.kg_service = KGService(
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password,
            openai_api_key=openai_api_key,
        )
    
    async def query_relationships(
        self,
        query: str,
        top_k: int = 10,
    ) -> str:
        """
        Query the knowledge graph for relationships.
        
        Args:
            query: Natural language query about relationships
            top_k: Number of results to return
            
        Returns:
            Formatted response with relationships
        """
        result = await self.kg_service.query(
            query_text=query,
            top_k=top_k,
        )
        
        # Format response for agent
        response_parts = [
            f"Query: {query}\n\nResponse: {result['response']}\n"
        ]
        
        if result["source_nodes"]:
            response_parts.append("\nRelated Concepts:")
            for i, node in enumerate(result["source_nodes"][:5], 1):
                metadata = node.get("metadata", {})
                response_parts.append(
                    f"{i}. {metadata.get('term', 'Unknown')} "
                    f"({metadata.get('type', 'concept')})"
                )
        
        return "\n".join(response_parts)
    
    async def get_related_concepts(
        self,
        concept_id: str,
        max_depth: int = 2,
    ) -> str:
        """
        Get concepts related to a given concept.
        
        Args:
            concept_id: Concept ID to find relationships for
            max_depth: Maximum traversal depth
            
        Returns:
            Formatted list of related concepts
        """
        result = await self.kg_service.get_related_concepts(
            concept_id=concept_id,
            max_depth=max_depth,
        )
        
        if result.get("error"):
            return f"Error: {result['error']}"
        
        response_parts = [
            f"Concept: {concept_id}\n",
            f"Found {result['count']} related concepts:\n"
        ]
        
        for i, concept in enumerate(result["related_concepts"][:10], 1):
            response_parts.append(
                f"{i}. {concept['term']} (depth: {concept['depth']}, "
                f"predicates: {', '.join(concept['predicates'][:3])})"
            )
        
        return "\n".join(response_parts)
    
    async def add_concept_to_graph(
        self,
        concept: Concept,
    ) -> str:
        """
        Add a concept to the knowledge graph.
        
        Args:
            concept: Concept to add
            
        Returns:
            Status message
        """
        result = await self.kg_service.add_concept_node(concept)
        
        if result["success"]:
            return f"Successfully added concept {concept.term} (ID: {concept.id}) to graph."
        else:
            return f"Failed to add concept: {result.get('error', 'Unknown error')}"
    
    def get_tools(self) -> List[FunctionTool]:
        """
        Get LlamaIndex FunctionTool instances for agent use.
        
        Returns:
            List of tools that can be added to agents
        """
        return [
            FunctionTool.from_defaults(
                fn=self.query_relationships,
                name="query_concept_relationships",
                description=(
                    "Query the knowledge graph for relationships between concepts. "
                    "Use this to find how concepts are connected, what relationships exist, "
                    "or to traverse the concept graph."
                ),
            ),
            FunctionTool.from_defaults(
                fn=self.get_related_concepts,
                name="get_related_concepts",
                description=(
                    "Get concepts related to a specific concept via graph traversal. "
                    "Use this to find neighbors, related concepts, or concept clusters."
                ),
            ),
            FunctionTool.from_defaults(
                fn=self.add_concept_to_graph,
                name="add_concept_to_graph",
                description=(
                    "Add a concept to the knowledge graph. "
                    "Use this after extracting a new concept to store it in the graph."
                ),
            ),
        ]


class AgentIntegrationHelper:
    """
    Helper class to integrate LlamaIndex with existing agent system.
    
    This provides a bridge between your agent packet protocol and LlamaIndex.
    """
    
    def __init__(
        self,
        rag_tool: Optional[ConceptRAGTool] = None,
        kg_tool: Optional[ConceptKGTool] = None,
    ):
        """Initialize integration helper."""
        self.rag_tool = rag_tool
        self.kg_tool = kg_tool
    
    def get_all_tools(self) -> List[FunctionTool]:
        """
        Get all available tools for agent use.
        
        Returns:
            Combined list of RAG and KG tools
        """
        tools = []
        
        if self.rag_tool:
            tools.extend(self.rag_tool.get_tools())
        
        if self.kg_tool:
            tools.extend(self.kg_tool.get_tools())
        
        return tools
    
    async def process_agent_packet(
        self,
        packet: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Process an agent packet and trigger appropriate LlamaIndex operations.
        
        This bridges your AgentPacket protocol with LlamaIndex indexing.
        
        Args:
            packet: Agent packet with concept/relationship data
            
        Returns:
            Optional result dictionary
        """
        intent = packet.get("intent")
        content = packet.get("content", {})
        
        # Handle concept extraction (HARVESTER)
        if intent == "GRAPH_UPDATE" and "concept" in content:
            concept_data = content["concept"]
            
            # Convert to Concept model
            from shared.models import Concept
            concept = Concept(
                id=concept_data["id"],
                term=concept_data["term"],
                type=concept_data["type"],
                dataType=concept_data.get("dataType"),
                category=concept_data.get("category", ""),
                explanation=concept_data.get("explanation", ""),
                confidence=concept_data.get("confidence", 0.5),
                ui_group=concept_data.get("ui_group", "General"),
                extractedBy=packet.get("sender", "UNKNOWN"),
            )
            
            # Index in RAG if available
            if self.rag_tool:
                await self.rag_tool.rag_service.index_concepts([concept])
            
            # Add to KG if available
            if self.kg_tool:
                await self.kg_tool.kg_service.add_concept_node(concept)
            
            return {"indexed": True, "concept_id": concept.id}
        
        # Handle relationship extraction (ARCHITECT)
        elif intent == "GRAPH_UPDATE" and "relationship" in content:
            rel_data = content["relationship"]
            
            # Add to KG if available
            if self.kg_tool:
                await self.kg_tool.kg_service.add_relationship(
                    source_id=rel_data["source"],
                    target_id=rel_data["target"],
                    predicate=rel_data["predicate"],
                    relationship_type=rel_data.get("type", "semantic"),
                )
            
            return {"added": True}
        
        # Handle taxonomy (CURATOR)
        elif intent == "GRAPH_UPDATE" and "taxonomy" in content:
            tax_data = content["taxonomy"]
            
            if self.kg_tool:
                await self.kg_tool.kg_service.add_taxonomy_relationship(
                    parent_id=tax_data["parent"],
                    child_id=tax_data["child"],
                    taxonomy_type=tax_data.get("type", "is_a"),
                )
            
            return {"added": True}
        
        return None
