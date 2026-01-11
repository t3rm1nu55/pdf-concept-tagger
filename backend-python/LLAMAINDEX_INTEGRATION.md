# LlamaIndex Integration Guide

This guide explains how to use LlamaIndex services for RAG, Knowledge Graph, and advanced querying in your PDF Concept Tagger system.

## Overview

LlamaIndex provides:
1. **RAG Service** - Semantic search over extracted concepts using Pinecone
2. **Knowledge Graph Service** - Graph storage and traversal using Neo4j
3. **Advanced Query Engines** - Router, sub-question, multi-step querying
4. **Agent Integration** - Tools that work with your existing agents

## Installation

Add to `requirements.txt`:
```bash
llama-index-core==0.10.0
llama-index-vector-stores-pinecone==0.1.0
llama-index-graph-stores-neo4j==0.1.0
llama-index-embeddings-openai==0.1.0
llama-index-llms-openai==0.1.0
```

Install:
```bash
pip install -r requirements.txt
```

## Environment Variables

Set these environment variables:

```bash
# Required
export OPENAI_API_KEY=your_openai_key
export PINECONE_API_KEY=your_pinecone_key
export PINECONE_ENV=us-east-1-aws  # Your Pinecone environment

# Optional (for Knowledge Graph)
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=your_password
```

## 1. RAG Service (Semantic Search)

### Basic Usage

```python
from llamaindex_rag_service import RAGService
from shared.models import Concept

# Initialize service
rag = RAGService(
    pinecone_api_key="your-key",
    pinecone_index_name="concepts",
    openai_api_key="your-key",
)

# Index concepts
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
    # ... more concepts
]

result = await rag.index_concepts(concepts)
print(f"Indexed {result['indexed']} concepts")

# Query concepts
response = await rag.query("What are the legal concepts?")
print(response['response'])
print(f"Found {response['num_sources']} source concepts")
```

### Advanced Features

**Keyword Filtering:**
```python
response = await rag.query(
    "What regulations apply?",
    required_keywords=["GDPR", "legal"],
    exclude_keywords=["financial"],
)
```

**Streaming Responses:**
```python
async for chunk in rag.query_streaming("What are the concepts?"):
    print(chunk, end="")
```

## 2. Knowledge Graph Service

### Basic Usage

```python
from llamaindex_kg_service import KGService
from shared.models import Concept

# Initialize service
kg = KGService(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    openai_api_key="your-key",
)

# Build graph from concepts and relationships
concepts = [/* your concepts */]
relationships = [
    {
        "source": "c1",
        "target": "c2",
        "predicate": "governs",
        "type": "semantic",
    }
]

result = await kg.build_graph(concepts, relationships)

# Query graph
response = await kg.query("What concepts relate to GDPR?")
print(response['response'])

# Get related concepts
related = await kg.get_related_concepts("c1", max_depth=2)
for concept in related['related_concepts']:
    print(f"{concept['term']} (depth: {concept['depth']})")
```

### Adding Relationships

```python
# Add semantic relationship
await kg.add_relationship(
    source_id="c1",
    target_id="c2",
    predicate="governs",
    relationship_type="semantic",
)

# Add taxonomy relationship
await kg.add_taxonomy_relationship(
    parent_id="domain_legal",
    child_id="c1",
    taxonomy_type="is_a",
)
```

## 3. Advanced Query Engines

### Router Query Engine

Routes queries to the best index (vector vs graph):

```python
from llamaindex_query_engines import create_router_query_engine

router = create_router_query_engine(
    vector_index=vector_index,
    kg_index=kg_index,
    selector_type="single",  # or "multi"
)

response = router.query("What are the legal concepts?")
# Automatically routes to best index
```

### Sub-Question Query Engine

Breaks complex queries into sub-questions:

```python
from llamaindex_query_engines import create_sub_question_query_engine
from llama_index.core.tools import QueryEngineTool

# Create tools
vector_tool = QueryEngineTool.from_defaults(
    query_engine=vector_index.as_query_engine(),
    description="Semantic search",
)
kg_tool = QueryEngineTool.from_defaults(
    query_engine=kg_index.as_query_engine(),
    description="Graph traversal",
)

# Create sub-question engine
sub_q_engine = create_sub_question_query_engine(
    query_engine_tools=[vector_tool, kg_tool],
    use_async=True,
)

# Complex query gets broken down
response = sub_q_engine.query(
    "What concepts relate to GDPR and when were they mentioned?"
)
# → "What concepts relate to GDPR?"
# → "When were GDPR concepts mentioned?"
```

### Multi-Step Query Engine

Iteratively refines queries:

```python
from llamaindex_query_engines import create_multi_step_query_engine

multi_step = create_multi_step_query_engine(
    query_engine=base_query_engine,
    max_iterations=3,
)

response = multi_step.query("What are the most important legal concepts?")
# Iteratively refines the query
```

## 4. Agent Integration

### Using with Your Agents

```python
from llamaindex_integration_example import (
    ConceptRAGTool,
    ConceptKGTool,
    AgentIntegrationHelper,
)

# Create tools
rag_tool = ConceptRAGTool(
    pinecone_api_key=os.getenv("PINECONE_API_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)

kg_tool = ConceptKGTool(
    neo4j_uri=os.getenv("NEO4J_URI"),
    neo4j_user=os.getenv("NEO4J_USER"),
    neo4j_password=os.getenv("NEO4J_PASSWORD"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)

# Get tools for agents (LangChain, LlamaIndex agents, etc.)
tools = rag_tool.get_tools() + kg_tool.get_tools()

# Use with LangChain agent
from langchain.agents import create_openai_tools_agent
agent = create_openai_tools_agent(llm, tools, prompt)
```

### Processing Agent Packets

Automatically index concepts when agents extract them:

```python
helper = AgentIntegrationHelper(rag_tool=rag_tool, kg_tool=kg_tool)

# Process agent packet (from your HARVESTER, ARCHITECT, etc.)
packet = {
    "sender": "HARVESTER",
    "intent": "GRAPH_UPDATE",
    "content": {
        "concept": {
            "id": "c1",
            "term": "GDPR",
            "type": "concept",
            # ... rest of concept data
        }
    }
}

result = await helper.process_agent_packet(packet)
# Automatically indexes in RAG and adds to KG
```

## Integration with Existing System

### In Your Agent Coordinator

```python
# backend/src/coordinator.py or similar

from llamaindex_integration_example import AgentIntegrationHelper

class Coordinator:
    def __init__(self):
        # ... existing initialization
        
        # Add LlamaIndex integration
        self.llamaindex_helper = AgentIntegrationHelper(
            rag_tool=ConceptRAGTool(...),
            kg_tool=ConceptKGTool(...),
        )
    
    async def handle_agent_packet(self, packet):
        # ... existing packet handling
        
        # Auto-index with LlamaIndex
        await self.llamaindex_helper.process_agent_packet(packet)
        
        # ... rest of handling
```

### Adding RAG Query Endpoint

```python
# FastAPI endpoint
from fastapi import APIRouter
from llamaindex_rag_service import RAGService

router = APIRouter()
rag_service = RAGService(...)

@router.post("/api/v1/query/concepts")
async def query_concepts(query: str):
    """Query concepts using semantic search."""
    result = await rag_service.query(query)
    return result
```

## Comparison: LlamaIndex vs LangChain

| Feature | LangChain | LlamaIndex | Recommendation |
|---------|-----------|------------|----------------|
| RAG Pipeline | Good | **Excellent** | Use LlamaIndex |
| Query Engines | Basic | **Advanced** | Use LlamaIndex |
| Knowledge Graph | Basic | **Excellent** | Use LlamaIndex |
| Agent Framework | **Excellent** | Good | Keep LangChain |
| Workflows | LangGraph (DAG) | Workflows (events) | Evaluate both |

## Best Practices

1. **Index Concepts Incrementally**: Index concepts as they're extracted, not in batches
2. **Use Hybrid Search**: Combine vector + keyword + graph for best results
3. **Post-Process Results**: Use similarity cutoff and keyword filters to improve quality
4. **Monitor Performance**: Track query latency and result quality
5. **Cache Common Queries**: Cache frequent queries to reduce API costs

## Examples

See `llamaindex_example_usage.py` for complete examples:

```bash
python llamaindex_example_usage.py
```

## Troubleshooting

**Pinecone Connection Issues:**
- Verify API key and environment
- Check index name exists
- Ensure index has correct dimensions (1536 for text-embedding-3-small)

**Neo4j Connection Issues:**
- Verify URI format: `bolt://host:port`
- Check credentials
- Ensure Neo4j is running

**OpenAI API Issues:**
- Verify API key is set
- Check rate limits
- Use appropriate model (gpt-4o-mini for cost, gpt-4 for quality)

## Next Steps

1. **Prototype**: Start with RAG service for concept search
2. **Add KG**: Integrate knowledge graph for relationships
3. **Advanced Queries**: Add router/sub-question engines for complex queries
4. **Agent Tools**: Integrate tools with your agents
5. **Evaluate**: Compare performance with LangChain implementation

## Resources

- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [Neo4j Documentation](https://neo4j.com/docs/)
