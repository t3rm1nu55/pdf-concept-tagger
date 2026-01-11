"""
LlamaIndex Knowledge Graph Service with Neo4j Integration

This service provides knowledge graph capabilities for storing and querying
concept relationships using LlamaIndex's KnowledgeGraphIndex and Neo4j.

Usage:
    from llamaindex_kg_service import KGService
    
    kg = KGService(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password",
        openai_api_key="your-key"
    )
    
    # Build graph from concepts and relationships
    await kg.build_graph(concepts, relationships)
    
    # Query with hybrid graph + vector search
    response = await kg.query("What concepts relate to GDPR?")
"""

import os
from typing import List, Optional, Dict, Any, Tuple
from llama_index.core import (
    Document,
    KnowledgeGraphIndex,
    Settings,
    get_response_synthesizer,
)
from llama_index.core.graph_stores import SimpleGraphStore
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import NodeWithScore
import neo4j
from shared.models import Concept


class KGService:
    """
    Knowledge Graph service for storing and querying concept relationships.
    
    Features:
    - Knowledge graph construction from concepts and relationships
    - Hybrid querying (graph traversal + vector search)
    - Automatic relationship extraction
    - Neo4j integration
    """
    
    def __init__(
        self,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None,
        neo4j_database: str = "neo4j",
        openai_api_key: Optional[str] = None,
        embedding_model: str = "text-embedding-3-small",
        llm_model: str = "gpt-4o-mini",
        kg_triplet_extract_mode: str = "hybrid",  # "basic", "llm", "hybrid"
    ):
        """
        Initialize Knowledge Graph service.
        
        Args:
            neo4j_uri: Neo4j connection URI (or set NEO4J_URI env var)
            neo4j_user: Neo4j username (or set NEO4J_USER env var)
            neo4j_password: Neo4j password (or set NEO4J_PASSWORD env var)
            neo4j_database: Neo4j database name
            openai_api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            embedding_model: OpenAI embedding model name
            llm_model: LLM model for relationship extraction
            kg_triplet_extract_mode: How to extract triplets ("basic", "llm", "hybrid")
        """
        # Initialize Neo4j
        neo4j_uri = neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = neo4j_user or os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = neo4j_password or os.getenv("NEO4J_PASSWORD")
        
        if not neo4j_password:
            raise ValueError("Neo4j password required")
        
        # Create Neo4j driver
        self.neo4j_driver = neo4j.GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password),
        )
        
        # Initialize OpenAI
        openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OpenAI API key required")
        
        # Configure LlamaIndex settings
        Settings.llm = OpenAI(model=llm_model, api_key=openai_api_key)
        Settings.embed_model = OpenAIEmbedding(
            model=embedding_model,
            api_key=openai_api_key
        )
        Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
        
        # Initialize Neo4j graph store
        self.graph_store = Neo4jGraphStore(
            username=neo4j_user,
            password=neo4j_password,
            url=neo4j_uri,
            database=neo4j_database,
        )
        
        # Store settings
        self.kg_triplet_extract_mode = kg_triplet_extract_mode
        
        # Lazy initialization of index
        self._index: Optional[KnowledgeGraphIndex] = None
    
    def _get_index(self) -> KnowledgeGraphIndex:
        """Get or create the knowledge graph index."""
        if self._index is None:
            # Try to load existing index, or create new one
            try:
                # Check if graph store has data
                # For now, we'll create a new index - in production you'd check first
                self._index = KnowledgeGraphIndex.from_documents(
                    documents=[],  # Empty, we'll add nodes manually
                    graph_store=self.graph_store,
                    kg_triplet_extract_mode=self.kg_triplet_extract_mode,
                    max_triplets_per_chunk=10,
                    include_embeddings=True,
                )
            except Exception:
                # Create new index
                self._index = KnowledgeGraphIndex.from_documents(
                    documents=[],
                    graph_store=self.graph_store,
                    kg_triplet_extract_mode=self.kg_triplet_extract_mode,
                    max_triplets_per_chunk=10,
                    include_embeddings=True,
                )
        return self._index
    
    def concept_to_document(self, concept: Concept) -> Document:
        """
        Convert a Concept to a LlamaIndex Document.
        
        Args:
            concept: Concept model from shared.models
            
        Returns:
            Document with concept information
        """
        text_parts = [
            f"Concept: {concept.term}",
        ]
        
        if concept.explanation:
            text_parts.append(f"Description: {concept.explanation}")
        
        if concept.category:
            text_parts.append(f"Category: {concept.category}")
        
        text = "\n".join(text_parts)
        
        metadata = {
            "concept_id": concept.id,
            "term": concept.term,
            "type": concept.type,
            "dataType": concept.dataType or "",
            "ui_group": concept.ui_group,
            "confidence": concept.confidence,
        }
        
        return Document(
            text=text,
            metadata=metadata,
            id_=concept.id,
        )
    
    async def add_concept_node(
        self,
        concept: Concept,
    ) -> Dict[str, Any]:
        """
        Add a concept as a node in the knowledge graph.
        
        Args:
            concept: Concept to add
            
        Returns:
            Result dictionary
        """
        try:
            # Create node in Neo4j
            with self.neo4j_driver.session() as session:
                # Create or update concept node
                query = """
                MERGE (c:Concept {id: $id})
                SET c.term = $term,
                    c.type = $type,
                    c.dataType = $dataType,
                    c.category = $category,
                    c.ui_group = $ui_group,
                    c.confidence = $confidence,
                    c.explanation = $explanation
                RETURN c
                """
                
                result = session.run(
                    query,
                    id=concept.id,
                    term=concept.term,
                    type=concept.type,
                    dataType=concept.dataType or "",
                    category=concept.category,
                    ui_group=concept.ui_group,
                    confidence=concept.confidence,
                    explanation=concept.explanation or "",
                )
                
                node = result.single()
                
                return {
                    "success": True,
                    "concept_id": concept.id,
                    "node_id": node["c"].id if node else None,
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "concept_id": concept.id,
            }
    
    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        predicate: str,
        relationship_type: str = "semantic",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add a relationship between two concepts.
        
        Args:
            source_id: Source concept ID
            target_id: Target concept ID
            predicate: Relationship predicate/type
            relationship_type: Type of relationship (semantic, structural, etc.)
            metadata: Optional relationship metadata
            
        Returns:
            Result dictionary
        """
        try:
            with self.neo4j_driver.session() as session:
                # Create relationship
                query = """
                MATCH (source:Concept {id: $source_id})
                MATCH (target:Concept {id: $target_id})
                MERGE (source)-[r:RELATES_TO {
                    predicate: $predicate,
                    type: $relationship_type
                }]->(target)
                SET r.created_at = datetime()
                RETURN r
                """
                
                result = session.run(
                    query,
                    source_id=source_id,
                    target_id=target_id,
                    predicate=predicate,
                    relationship_type=relationship_type,
                )
                
                rel = result.single()
                
                return {
                    "success": True,
                    "source_id": source_id,
                    "target_id": target_id,
                    "predicate": predicate,
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source_id": source_id,
                "target_id": target_id,
            }
    
    async def add_taxonomy_relationship(
        self,
        parent_id: str,
        child_id: str,
        taxonomy_type: str = "is_a",
    ) -> Dict[str, Any]:
        """
        Add a taxonomy (hierarchical) relationship.
        
        Args:
            parent_id: Parent concept ID
            child_id: Child concept ID
            taxonomy_type: Type of taxonomy ("is_a", "part_of")
            
        Returns:
            Result dictionary
        """
        return await self.add_relationship(
            source_id=parent_id,
            target_id=child_id,
            predicate=taxonomy_type,
            relationship_type="taxonomy",
        )
    
    async def build_graph(
        self,
        concepts: List[Concept],
        relationships: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Build knowledge graph from concepts and relationships.
        
        Args:
            concepts: List of concepts to add as nodes
            relationships: Optional list of relationship dicts with:
                source, target, predicate, type
        
        Returns:
            Build results
        """
        results = {
            "concepts_added": 0,
            "relationships_added": 0,
            "errors": [],
        }
        
        # Add all concepts as nodes
        for concept in concepts:
            result = await self.add_concept_node(concept)
            if result["success"]:
                results["concepts_added"] += 1
            else:
                results["errors"].append(result)
        
        # Add relationships if provided
        if relationships:
            for rel in relationships:
                result = await self.add_relationship(
                    source_id=rel["source"],
                    target_id=rel["target"],
                    predicate=rel["predicate"],
                    relationship_type=rel.get("type", "semantic"),
                )
                if result["success"]:
                    results["relationships_added"] += 1
                else:
                    results["errors"].append(result)
        
        return results
    
    async def query(
        self,
        query_text: str,
        include_text: bool = True,
        retriever_mode: str = "hybrid",  # "keyword", "embedding", "hybrid"
        top_k: int = 10,
    ) -> Dict[str, Any]:
        """
        Query the knowledge graph with hybrid search.
        
        Args:
            query_text: Natural language query
            include_text: Whether to include text in response
            retriever_mode: Retrieval mode ("keyword", "embedding", "hybrid")
            top_k: Number of results to return
            
        Returns:
            Query results with concepts and relationships
        """
        index = self._get_index()
        
        # Create query engine with hybrid retrieval
        query_engine = index.as_query_engine(
            include_text=include_text,
            retriever_mode=retriever_mode,
            similarity_top_k=top_k,
        )
        
        # Execute query
        response = query_engine.query(query_text)
        
        # Extract source nodes
        source_nodes = []
        for node_with_score in response.source_nodes:
            source_nodes.append({
                "text": str(node_with_score.node.text),
                "score": node_with_score.score,
                "metadata": node_with_score.node.metadata,
            })
        
        return {
            "response": str(response),
            "source_nodes": source_nodes,
            "num_sources": len(source_nodes),
            "query": query_text,
        }
    
    async def get_related_concepts(
        self,
        concept_id: str,
        max_depth: int = 2,
        relationship_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get concepts related to a given concept via graph traversal.
        
        Args:
            concept_id: Concept ID to find relationships for
            max_depth: Maximum traversal depth
            relationship_types: Optional filter by relationship types
            
        Returns:
            Related concepts and paths
        """
        try:
            with self.neo4j_driver.session() as session:
                # Build query based on filters
                if relationship_types:
                    rel_filter = f"r.type IN {relationship_types}"
                else:
                    rel_filter = "true"
                
                query = f"""
                MATCH path = (start:Concept {{id: $concept_id}})-[r:RELATES_TO*1..{max_depth}]-(related:Concept)
                WHERE {rel_filter}
                RETURN DISTINCT related, length(path) as depth, 
                       [rel IN relationships(path) | rel.predicate] as predicates
                ORDER BY depth
                LIMIT 50
                """
                
                result = session.run(query, concept_id=concept_id)
                
                related_concepts = []
                for record in result:
                    node = record["related"]
                    related_concepts.append({
                        "concept_id": node["id"],
                        "term": node["term"],
                        "type": node.get("type"),
                        "depth": record["depth"],
                        "predicates": record["predicates"],
                    })
                
                return {
                    "concept_id": concept_id,
                    "related_concepts": related_concepts,
                    "count": len(related_concepts),
                }
        except Exception as e:
            return {
                "concept_id": concept_id,
                "error": str(e),
                "related_concepts": [],
            }
    
    def close(self):
        """Close Neo4j driver connection."""
        if self.neo4j_driver:
            self.neo4j_driver.close()
