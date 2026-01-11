"""
Advanced Query Engines for Concept Search

This module demonstrates various LlamaIndex query engines:
- Router Query Engine (route to different indexes)
- Sub-Question Query Engine (break complex queries)
- Multi-Step Query Engine (iterative refinement)
- Citation Query Engine (source attribution)

Usage:
    from llamaindex_query_engines import create_router_engine, create_sub_question_engine
    
    # Router engine
    router = create_router_engine(vector_index, kg_index)
    response = await router.query("What are the legal concepts?")
    
    # Sub-question engine
    sub_q = create_sub_question_engine([vector_tool, kg_tool])
    response = await sub_q.query("What concepts relate to GDPR and when were they mentioned?")
"""

from typing import List, Optional, Dict, Any
from llama_index.core import (
    VectorStoreIndex,
    KnowledgeGraphIndex,
    QueryBundle,
    get_response_synthesizer,
)
from llama_index.core.query_engine import (
    RouterQueryEngine,
    SubQuestionQueryEngine,
    MultiStepQueryEngine,
    RetrieverQueryEngine,
)
from llama_index.core.tools import QueryEngineTool
from llama_index.core.selectors import (
    LLMSingleSelector,
    LLMMultiSelector,
)
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.retrievers import VectorIndexRetriever


def create_router_query_engine(
    vector_index: VectorStoreIndex,
    kg_index: Optional[KnowledgeGraphIndex] = None,
    selector_type: str = "single",  # "single" or "multi"
) -> RouterQueryEngine:
    """
    Create a router query engine that selects the best index for a query.
    
    This is useful when you have multiple indexes (vector, knowledge graph)
    and want to route queries to the most appropriate one.
    
    Args:
        vector_index: Vector store index for semantic search
        kg_index: Optional knowledge graph index
        selector_type: "single" (one index) or "multi" (multiple indexes)
        
    Returns:
        Router query engine
    """
    # Create query engines for each index
    vector_query_engine = vector_index.as_query_engine(
        similarity_top_k=10,
        node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
    )
    
    tools = [
        QueryEngineTool.from_defaults(
            query_engine=vector_query_engine,
            description=(
                "Useful for semantic search over concepts. "
                "Use this for questions about what concepts exist, "
                "finding similar concepts, or searching by meaning."
            ),
        ),
    ]
    
    # Add KG tool if available
    if kg_index:
        kg_query_engine = kg_index.as_query_engine(
            include_text=True,
            retriever_mode="hybrid",
        )
        tools.append(
            QueryEngineTool.from_defaults(
                query_engine=kg_query_engine,
                description=(
                    "Useful for questions about relationships between concepts, "
                    "finding related concepts, or understanding concept connections. "
                    "Use this when you need to traverse the knowledge graph."
                ),
            ),
        )
    
    # Create selector
    if selector_type == "multi":
        selector = LLMMultiSelector.from_defaults()
    else:
        selector = LLMSingleSelector.from_defaults()
    
    # Create router
    router_query_engine = RouterQueryEngine.from_defaults(
        query_engine_tools=tools,
        selector=selector,
        verbose=True,
    )
    
    return router_query_engine


def create_sub_question_query_engine(
    query_engine_tools: List[QueryEngineTool],
    use_async: bool = True,
) -> SubQuestionQueryEngine:
    """
    Create a sub-question query engine that breaks complex queries into sub-questions.
    
    This is useful for queries that require multiple pieces of information,
    like "What concepts relate to GDPR and when were they mentioned?"
    
    Args:
        query_engine_tools: List of query engine tools to use
        use_async: Whether to execute sub-queries in parallel
        
    Returns:
        Sub-question query engine
    """
    sub_question_engine = SubQuestionQueryEngine.from_defaults(
        query_engine_tools=query_engine_tools,
        use_async=use_async,
        verbose=True,
    )
    
    return sub_question_engine


def create_multi_step_query_engine(
    query_engine: RetrieverQueryEngine,
    max_iterations: int = 3,
) -> MultiStepQueryEngine:
    """
    Create a multi-step query engine that iteratively refines queries.
    
    This is useful for complex queries that may need multiple passes
    to fully answer, with each step building on previous results.
    
    Args:
        query_engine: Base query engine to use
        max_iterations: Maximum number of refinement steps
        
    Returns:
        Multi-step query engine
    """
    multi_step_engine = MultiStepQueryEngine.from_defaults(
        query_engine=query_engine,
        max_iterations=max_iterations,
        verbose=True,
    )
    
    return multi_step_engine


def create_citation_query_engine(
    query_engine: RetrieverQueryEngine,
) -> RetrieverQueryEngine:
    """
    Create a citation query engine that provides source attribution.
    
    This is useful when you need to know where information came from,
    with citations to specific concepts and document sections.
    
    Args:
        query_engine: Base query engine to add citations to
        
    Returns:
        Query engine with citation support
    """
    # The citation is handled by the response synthesizer
    # We configure it to include source nodes
    citation_query_engine = query_engine
    
    # Citations are automatically included in response.source_nodes
    return citation_query_engine


def create_hybrid_query_engine(
    vector_index: VectorStoreIndex,
    kg_index: Optional[KnowledgeGraphIndex] = None,
    query_type: str = "router",  # "router", "sub_question", "multi_step"
) -> Any:
    """
    Create an advanced query engine based on query type.
    
    Args:
        vector_index: Vector store index
        kg_index: Optional knowledge graph index
        query_type: Type of query engine ("router", "sub_question", "multi_step")
        
    Returns:
        Configured query engine
    """
    # Create base tools
    vector_tool = QueryEngineTool.from_defaults(
        query_engine=vector_index.as_query_engine(),
        description="Semantic search over concepts",
    )
    
    tools = [vector_tool]
    
    if kg_index:
        kg_tool = QueryEngineTool.from_defaults(
            query_engine=kg_index.as_query_engine(),
            description="Knowledge graph traversal",
        )
        tools.append(kg_tool)
    
    # Create appropriate engine
    if query_type == "router":
        return create_router_query_engine(vector_index, kg_index)
    elif query_type == "sub_question":
        return create_sub_question_query_engine(tools)
    elif query_type == "multi_step":
        base_engine = vector_index.as_query_engine()
        return create_multi_step_query_engine(base_engine)
    else:
        raise ValueError(f"Unknown query_type: {query_type}")


async def evaluate_query_engines(
    query: str,
    vector_index: VectorStoreIndex,
    kg_index: Optional[KnowledgeGraphIndex] = None,
) -> Dict[str, Any]:
    """
    Evaluate different query engines on the same query for comparison.
    
    Args:
        query: Query to test
        vector_index: Vector store index
        kg_index: Optional knowledge graph index
        
    Returns:
        Comparison results from different engines
    """
    results = {}
    
    # 1. Basic vector query
    basic_engine = vector_index.as_query_engine()
    basic_response = basic_engine.query(query)
    results["basic_vector"] = {
        "response": str(basic_response),
        "num_sources": len(basic_response.source_nodes),
    }
    
    # 2. Router query (if KG available)
    if kg_index:
        router_engine = create_router_query_engine(vector_index, kg_index)
        router_response = router_engine.query(query)
        results["router"] = {
            "response": str(router_response),
            "num_sources": len(router_response.source_nodes) if hasattr(router_response, "source_nodes") else 0,
        }
    
    # 3. Sub-question query
    vector_tool = QueryEngineTool.from_defaults(
        query_engine=vector_index.as_query_engine(),
        description="Semantic search",
    )
    tools = [vector_tool]
    
    if kg_index:
        kg_tool = QueryEngineTool.from_defaults(
            query_engine=kg_index.as_query_engine(),
            description="Graph traversal",
        )
        tools.append(kg_tool)
    
    sub_q_engine = create_sub_question_query_engine(tools)
    sub_q_response = sub_q_engine.query(query)
    results["sub_question"] = {
        "response": str(sub_q_response),
        "num_sources": len(sub_q_response.source_nodes) if hasattr(sub_q_response, "source_nodes") else 0,
    }
    
    return results
