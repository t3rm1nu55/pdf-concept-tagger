"""
LlamaIndex RAG Service with Pinecone Integration

This service provides RAG capabilities for querying extracted concepts
using LlamaIndex's advanced query engines and Pinecone vector store.

Usage:
    from llamaindex_rag_service import RAGService
    
    rag = RAGService(
        pinecone_api_key="your-key",
        pinecone_index_name="concepts",
        openai_api_key="your-key"
    )
    
    # Index concepts
    await rag.index_concepts(concepts)
    
    # Query concepts
    response = await rag.query("What are the legal concepts?")
"""

import os
from typing import List, Optional, Dict, Any
from llama_index.core import (
    Document,
    VectorStoreIndex,
    Settings,
    get_response_synthesizer,
    QueryBundle,
)
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import (
    SimilarityPostprocessor,
    KeywordNodePostprocessor,
)
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import NodeWithScore, MetadataMode
import pinecone
from shared.models import Concept


class RAGService:
    """
    RAG service for semantic search over extracted concepts.
    
    Features:
    - Vector indexing with Pinecone
    - Advanced query engines (router, sub-question, multi-step)
    - Post-processing (reranking, filtering)
    - Hybrid search (vector + keyword)
    """
    
    def __init__(
        self,
        pinecone_api_key: Optional[str] = None,
        pinecone_index_name: str = "concepts",
        openai_api_key: Optional[str] = None,
        embedding_model: str = "text-embedding-3-small",
        llm_model: str = "gpt-4o-mini",
        similarity_top_k: int = 10,
        similarity_cutoff: float = 0.7,
    ):
        """
        Initialize RAG service.
        
        Args:
            pinecone_api_key: Pinecone API key (or set PINECONE_API_KEY env var)
            pinecone_index_name: Name of Pinecone index
            openai_api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            embedding_model: OpenAI embedding model name
            llm_model: LLM model for query synthesis
            similarity_top_k: Number of top results to retrieve
            similarity_cutoff: Minimum similarity score threshold
        """
        # Initialize Pinecone
        pinecone_api_key = pinecone_api_key or os.getenv("PINECONE_API_KEY")
        if not pinecone_api_key:
            raise ValueError("Pinecone API key required")
        
        pinecone.init(api_key=pinecone_api_key, environment=os.getenv("PINECONE_ENV", "us-east-1-aws"))
        
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
        
        # Initialize Pinecone vector store
        self.pinecone_index = pinecone.Index(pinecone_index_name)
        self.vector_store = PineconeVectorStore(
            pinecone_index=self.pinecone_index,
            namespace="concepts"
        )
        
        # Store settings
        self.similarity_top_k = similarity_top_k
        self.similarity_cutoff = similarity_cutoff
        self.index_name = pinecone_index_name
        
        # Lazy initialization of index
        self._index: Optional[VectorStoreIndex] = None
    
    def _get_index(self) -> VectorStoreIndex:
        """Get or create the vector index."""
        if self._index is None:
            self._index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store
            )
        return self._index
    
    def concept_to_document(self, concept: Concept) -> Document:
        """
        Convert a Concept to a LlamaIndex Document.
        
        Args:
            concept: Concept model from shared.models
            
        Returns:
            Document with concept information and metadata
        """
        # Build text content from concept
        text_parts = [
            f"Concept: {concept.term}",
            f"Type: {concept.type}",
        ]
        
        if concept.explanation:
            text_parts.append(f"Description: {concept.explanation}")
        
        if concept.category:
            text_parts.append(f"Category: {concept.category}")
        
        if concept.dataType:
            text_parts.append(f"Data Type: {concept.dataType}")
        
        text = "\n".join(text_parts)
        
        # Build metadata
        metadata = {
            "concept_id": concept.id,
            "term": concept.term,
            "type": concept.type,
            "dataType": concept.dataType or "",
            "category": concept.category,
            "ui_group": concept.ui_group,
            "confidence": concept.confidence,
            "extractedBy": concept.extractedBy or "",
            "timestamp": concept.timestamp or "",
        }
        
        return Document(
            text=text,
            metadata=metadata,
            id_=concept.id,
        )
    
    async def index_concepts(self, concepts: List[Concept]) -> Dict[str, Any]:
        """
        Index a list of concepts into Pinecone.
        
        Args:
            concepts: List of Concept objects to index
            
        Returns:
            Dictionary with indexing results
        """
        if not concepts:
            return {"indexed": 0, "errors": []}
        
        # Convert concepts to documents
        documents = [self.concept_to_document(concept) for concept in concepts]
        
        # Get or create index
        index = self._get_index()
        
        # Insert documents
        try:
            # Use async insert if available, otherwise sync
            index.insert(documents)
            
            return {
                "indexed": len(documents),
                "errors": [],
                "index_name": self.index_name,
            }
        except Exception as e:
            return {
                "indexed": 0,
                "errors": [str(e)],
            }
    
    def create_basic_query_engine(
        self,
        similarity_top_k: Optional[int] = None,
        similarity_cutoff: Optional[float] = None,
    ) -> RetrieverQueryEngine:
        """
        Create a basic query engine with post-processing.
        
        Args:
            similarity_top_k: Override default top_k
            similarity_cutoff: Override default cutoff
            
        Returns:
            Configured query engine
        """
        index = self._get_index()
        
        # Configure retriever
        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=similarity_top_k or self.similarity_top_k,
        )
        
        # Configure post-processors
        node_postprocessors = [
            SimilarityPostprocessor(
                similarity_cutoff=similarity_cutoff or self.similarity_cutoff
            ),
        ]
        
        # Configure response synthesizer
        response_synthesizer = get_response_synthesizer(
            response_mode="compact"  # Compact mode for efficiency
        )
        
        # Create query engine
        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
            node_postprocessors=node_postprocessors,
        )
        
        return query_engine
    
    def create_keyword_filtered_engine(
        self,
        required_keywords: List[str],
        exclude_keywords: Optional[List[str]] = None,
    ) -> RetrieverQueryEngine:
        """
        Create a query engine with keyword filtering.
        
        Args:
            required_keywords: Keywords that must be present
            exclude_keywords: Keywords to exclude
            
        Returns:
            Query engine with keyword post-processing
        """
        index = self._get_index()
        
        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=self.similarity_top_k,
        )
        
        # Add keyword post-processor
        node_postprocessors = [
            SimilarityPostprocessor(similarity_cutoff=self.similarity_cutoff),
            KeywordNodePostprocessor(
                required_keywords=required_keywords,
                exclude_keywords=exclude_keywords or [],
            ),
        ]
        
        response_synthesizer = get_response_synthesizer(response_mode="compact")
        
        return RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
            node_postprocessors=node_postprocessors,
        )
    
    async def query(
        self,
        query_text: str,
        similarity_top_k: Optional[int] = None,
        similarity_cutoff: Optional[float] = None,
        required_keywords: Optional[List[str]] = None,
        exclude_keywords: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Query concepts using semantic search.
        
        Args:
            query_text: Natural language query
            similarity_top_k: Override default top_k
            similarity_cutoff: Override default cutoff
            required_keywords: Optional keyword filter
            exclude_keywords: Optional exclusion keywords
            
        Returns:
            Dictionary with query results and metadata
        """
        # Choose query engine based on filters
        if required_keywords or exclude_keywords:
            query_engine = self.create_keyword_filtered_engine(
                required_keywords=required_keywords or [],
                exclude_keywords=exclude_keywords,
            )
        else:
            query_engine = self.create_basic_query_engine(
                similarity_top_k=similarity_top_k,
                similarity_cutoff=similarity_cutoff,
            )
        
        # Execute query
        response = query_engine.query(query_text)
        
        # Extract source nodes with metadata
        source_concepts = []
        for node_with_score in response.source_nodes:
            metadata = node_with_score.node.metadata
            source_concepts.append({
                "concept_id": metadata.get("concept_id"),
                "term": metadata.get("term"),
                "type": metadata.get("type"),
                "ui_group": metadata.get("ui_group"),
                "confidence": metadata.get("confidence"),
                "similarity_score": node_with_score.score,
                "text": node_with_score.node.get_content(metadata_mode=MetadataMode.NONE),
            })
        
        return {
            "response": str(response),
            "source_concepts": source_concepts,
            "num_sources": len(source_concepts),
            "query": query_text,
        }
    
    async def query_streaming(
        self,
        query_text: str,
        similarity_top_k: Optional[int] = None,
    ):
        """
        Stream query results as they're generated.
        
        Args:
            query_text: Natural language query
            similarity_top_k: Override default top_k
            
        Yields:
            Chunks of the response as they're generated
        """
        query_engine = self.create_basic_query_engine(similarity_top_k=similarity_top_k)
        
        streaming_response = query_engine.query(query_text)
        
        for token in streaming_response.response_gen:
            yield token
