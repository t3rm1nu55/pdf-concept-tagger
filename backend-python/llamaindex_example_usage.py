"""
Example Usage: LlamaIndex Integration

This script demonstrates how to use the LlamaIndex services
with your existing concept extraction system.

Run with:
    python llamaindex_example_usage.py
"""

import asyncio
import os
from typing import List
from shared.models import Concept
from llamaindex_rag_service import RAGService
from llamaindex_kg_service import KGService
from llamaindex_query_engines import (
    create_router_query_engine,
    create_sub_question_query_engine,
    evaluate_query_engines,
)
from llamaindex_integration_example import (
    ConceptRAGTool,
    ConceptKGTool,
    AgentIntegrationHelper,
)


async def example_rag_usage():
    """Example: Using RAG service for semantic concept search."""
    print("\n=== RAG Service Example ===\n")
    
    # Initialize RAG service
    rag = RAGService(
        pinecone_api_key=os.getenv("PINECONE_API_KEY"),
        pinecone_index_name="concepts",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
    
    # Create sample concepts
    concepts = [
        Concept(
            id="c1",
            term="GDPR",
            type="concept",
            dataType="legal",
            category="Regulation",
            explanation="General Data Protection Regulation - EU privacy law",
            confidence=0.9,
            ui_group="Legal",
        ),
        Concept(
            id="c2",
            term="Data Processing Agreement",
            type="concept",
            dataType="legal",
            category="Contract",
            explanation="Agreement governing how data is processed",
            confidence=0.85,
            ui_group="Legal",
        ),
        Concept(
            id="c3",
            term="2024-06-30",
            type="concept",
            dataType="date",
            category="Deadline",
            explanation="Completion date for project",
            confidence=0.8,
            ui_group="Timeline",
        ),
    ]
    
    # Index concepts
    print("Indexing concepts...")
    result = await rag.index_concepts(concepts)
    print(f"Indexed: {result['indexed']} concepts\n")
    
    # Query concepts
    print("Querying: 'What are the legal concepts?'")
    response = await rag.query("What are the legal concepts?")
    print(f"Response: {response['response']}\n")
    print(f"Found {response['num_sources']} source concepts:")
    for concept in response["source_concepts"]:
        print(f"  - {concept['term']} (confidence: {concept['confidence']:.2f})")
    
    # Query with keyword filter
    print("\nQuerying with keyword filter: 'GDPR'")
    response = await rag.query(
        "What regulations apply?",
        required_keywords=["GDPR", "legal"],
    )
    print(f"Response: {response['response']}\n")


async def example_kg_usage():
    """Example: Using Knowledge Graph service."""
    print("\n=== Knowledge Graph Service Example ===\n")
    
    # Initialize KG service
    kg = KGService(
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
    
    # Create sample concepts
    concepts = [
        Concept(
            id="c1",
            term="GDPR",
            type="concept",
            dataType="legal",
            explanation="General Data Protection Regulation",
            confidence=0.9,
            ui_group="Legal",
        ),
        Concept(
            id="c2",
            term="Data Processing",
            type="concept",
            dataType="entity",
            explanation="Processing of personal data",
            confidence=0.85,
            ui_group="Legal",
        ),
    ]
    
    # Build graph
    print("Building knowledge graph...")
    relationships = [
        {
            "source": "c1",
            "target": "c2",
            "predicate": "governs",
            "type": "semantic",
        }
    ]
    
    result = await kg.build_graph(concepts, relationships)
    print(f"Added {result['concepts_added']} concepts, {result['relationships_added']} relationships\n")
    
    # Query graph
    print("Querying: 'What concepts relate to GDPR?'")
    response = await kg.query("What concepts relate to GDPR?")
    print(f"Response: {response['response']}\n")
    
    # Get related concepts
    print("Getting related concepts for 'c1'...")
    related = await kg.get_related_concepts("c1", max_depth=2)
    print(f"Found {related['count']} related concepts:")
    for concept in related["related_concepts"][:5]:
        print(f"  - {concept['term']} (depth: {concept['depth']})")
    
    kg.close()


async def example_query_engines():
    """Example: Using advanced query engines."""
    print("\n=== Advanced Query Engines Example ===\n")
    
    # This would require initialized indexes
    # For demo purposes, we'll show the API
    
    print("Router Query Engine:")
    print("  - Routes queries to best index (vector vs graph)")
    print("  - Use when you have multiple indexes\n")
    
    print("Sub-Question Query Engine:")
    print("  - Breaks complex queries into sub-questions")
    print("  - Example: 'What concepts relate to GDPR and when mentioned?'")
    print("    → 'What concepts relate to GDPR?'")
    print("    → 'When were GDPR concepts mentioned?'\n")
    
    print("Multi-Step Query Engine:")
    print("  - Iteratively refines queries")
    print("  - Each step builds on previous results\n")


async def example_agent_integration():
    """Example: Integrating with agents."""
    print("\n=== Agent Integration Example ===\n")
    
    # Create tools
    rag_tool = ConceptRAGTool(
        pinecone_api_key=os.getenv("PINECONE_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
    
    kg_tool = ConceptKGTool(
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
    
    # Create integration helper
    helper = AgentIntegrationHelper(rag_tool=rag_tool, kg_tool=kg_tool)
    
    # Get tools for agents
    tools = helper.get_all_tools()
    print(f"Available tools for agents: {len(tools)}")
    for tool in tools:
        print(f"  - {tool.metadata.name}: {tool.metadata.description[:60]}...")
    
    # Process agent packet
    print("\nProcessing agent packet...")
    packet = {
        "sender": "HARVESTER",
        "intent": "GRAPH_UPDATE",
        "content": {
            "concept": {
                "id": "c_new",
                "term": "CCPA",
                "type": "concept",
                "dataType": "legal",
                "category": "Regulation",
                "explanation": "California Consumer Privacy Act",
                "confidence": 0.9,
                "ui_group": "Legal",
            }
        }
    }
    
    result = await helper.process_agent_packet(packet)
    if result:
        print(f"Processed: {result}")
    
    # Example agent query
    print("\nAgent querying concepts...")
    response = await rag_tool.query_concepts("What are privacy regulations?")
    print(response[:200] + "...")


async def main():
    """Run all examples."""
    print("LlamaIndex Integration Examples")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ["OPENAI_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing)}")
        print("Set these to run the examples:\n")
        for var in missing:
            print(f"  export {var}=your_value")
        return
    
    try:
        # Run examples (comment out ones that need services)
        await example_rag_usage()
        # await example_kg_usage()  # Requires Neo4j
        await example_query_engines()
        await example_agent_integration()
        
        print("\n" + "=" * 50)
        print("Examples completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: Some examples require:")
        print("  - Pinecone API key and index")
        print("  - Neo4j running and configured")
        print("  - OpenAI API key")


if __name__ == "__main__":
    asyncio.run(main())
