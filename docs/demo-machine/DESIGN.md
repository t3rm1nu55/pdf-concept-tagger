# Demo Machine Design Specification

> **Status**: Design Phase  
> **Version**: 1.0.0  
> **Date**: 2026-01-11  
> **Purpose**: Comprehensive design addressing all design hooks from REQUIREMENTS.md

## Design Overview

This document provides detailed design specifications for the PDF Concept Tagger demo machine, addressing all design hooks identified in REQUIREMENTS.md and DESIGN_HOOKS.md. This design follows the Requirements → Design → Tasks pipeline and implements pragmatic decisions based on best-in-class tools.

## Table of Contents

1. [API Design](#api-design)
2. [Data Model Design](#data-model-design)
3. [UX Design](#ux-design)
4. [Component Design](#component-design)
5. [Agent Architecture Design](#agent-architecture-design)
6. [RAG Pipeline Design](#rag-pipeline-design)
7. [Domain Model Integration Design](#domain-model-integration-design)
8. [Hook System Design](#hook-system-design)
9. [Assessment Indicator Design](#assessment-indicator-design)
10. [Performance & Scalability Design](#performance--scalability-design)

---

## API Design

### 1. REST API Endpoints

#### Base URL
```
http://localhost:8000/api/v1
```

#### Authentication
- **Method**: API Key (header: `X-API-Key`)
- **Scope**: Per-endpoint (some public, some authenticated)
- **Future**: JWT tokens for multi-user support

#### Core Endpoints

##### 1.1 PDF Analysis Endpoint
**POST** `/analyze`

**Request**:
```json
{
  "document_id": "uuid",
  "file": "base64_encoded_pdf",
  "options": {
    "extract_structure": true,
    "extract_entities": true,
    "extract_concepts": true,
    "confidence_threshold": 0.7,
    "domain_models": ["microsoft_cdm", "accounting"],
    "stream": true
  }
}
```

**Response** (Streaming):
```json
{
  "status": "processing|completed|error",
  "progress": 0.0-1.0,
  "document_id": "uuid",
  "results": {
    "structure": {...},
    "entities": [...],
    "concepts": [...],
    "relationships": [...]
  },
  "metadata": {
    "processing_time": 45.2,
    "pages_processed": 10,
    "total_pages": 10
  }
}
```

**Error Handling**:
- `400 Bad Request`: Invalid PDF, missing required fields
- `413 Payload Too Large`: PDF exceeds size limit (50MB)
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Processing failure

**Design Decisions**:
- ✅ Streaming response for real-time updates (WebSocket fallback)
- ✅ Base64 encoding for simplicity (can switch to multipart/form-data)
- ✅ Options object for extensibility
- ✅ Progress tracking for UX

---

##### 1.2 Concept Query Endpoints

**GET** `/concepts`

**Query Parameters**:
- `q`: Search query (string)
- `type`: Entity type filter (string[])
- `confidence_min`: Minimum confidence (float, 0.0-1.0)
- `domain`: Domain model filter (string[])
- `page`: Page number (int, default: 1)
- `page_size`: Results per page (int, default: 20)
- `sort`: Sort field (string, default: "confidence")
- `order`: Sort order ("asc" | "desc", default: "desc")

**Response**:
```json
{
  "concepts": [
    {
      "id": "uuid",
      "term": "Completion Date",
      "type": "date",
      "confidence": 0.95,
      "assessment": "always_true",
      "source": {
        "document_id": "uuid",
        "page": 3,
        "section": "3.2",
        "location": {"x": 100, "y": 200}
      },
      "relationships": [
        {"type": "relates_to", "target": "uuid", "confidence": 0.8}
      ]
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 150,
    "total_pages": 8
  },
  "facets": {
    "types": {"date": 45, "entity": 60, "concept": 45},
    "domains": {"microsoft_cdm": 30, "accounting": 25}
  }
}
```

**GET** `/concepts/{id}`

**Response**:
```json
{
  "id": "uuid",
  "term": "Completion Date",
  "type": "date",
  "confidence": 0.95,
  "assessment": "always_true",
  "source": {...},
  "relationships": [...],
  "metadata": {
    "created_at": "2026-01-11T10:00:00Z",
    "updated_at": "2026-01-11T10:05:00Z",
    "extracted_by": "harvester_agent"
  },
  "domain_mapping": {
    "domain": "microsoft_cdm",
    "schema": "Project",
    "field": "CompletionDate",
    "confidence": 0.9
  }
}
```

**Design Decisions**:
- ✅ RESTful design with clear resource hierarchy
- ✅ Pagination for large result sets
- ✅ Faceted search for filtering
- ✅ Confidence and assessment indicators included

---

##### 1.3 Graph Query Endpoints

**GET** `/graph`

**Query Parameters**:
- `node_ids`: Filter by node IDs (string[])
- `relationship_types`: Filter by relationship types (string[])
- `depth`: Traversal depth (int, default: 2, max: 5)
- `layout`: Graph layout ("force" | "hierarchical" | "circular", default: "force")

**Response**:
```json
{
  "nodes": [
    {
      "id": "uuid",
      "label": "Completion Date",
      "type": "concept",
      "properties": {
        "confidence": 0.95,
        "assessment": "always_true"
      },
      "position": {"x": 100, "y": 200}
    }
  ],
  "edges": [
    {
      "id": "uuid",
      "source": "uuid",
      "target": "uuid",
      "type": "relates_to",
      "properties": {
        "confidence": 0.8,
        "strength": 0.75
      }
    }
  ],
  "metadata": {
    "total_nodes": 150,
    "total_edges": 300,
    "layout": "force"
  }
}
```

**GET** `/graph/paths`

**Query Parameters**:
- `source`: Source node ID (string, required)
- `target`: Target node ID (string, required)
- `max_length`: Maximum path length (int, default: 5)
- `relationship_types`: Allowed relationship types (string[])

**Response**:
```json
{
  "paths": [
    {
      "nodes": ["uuid1", "uuid2", "uuid3"],
      "edges": ["uuid4", "uuid5"],
      "length": 2,
      "confidence": 0.85,
      "weight": 1.5
    }
  ],
  "shortest_path": {
    "nodes": ["uuid1", "uuid2"],
    "length": 1,
    "confidence": 0.9
  }
}
```

**Design Decisions**:
- ✅ Graph representation optimized for visualization
- ✅ Path finding for relationship discovery
- ✅ Configurable layouts for different use cases

---

##### 1.4 Prompt Experimentation Endpoint

**POST** `/prompts/experiment`

**Request**:
```json
{
  "agent": "harvester|architect|curator",
  "prompt_template": "Custom prompt template...",
  "test_document_id": "uuid",
  "options": {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

**Response**:
```json
{
  "experiment_id": "uuid",
  "results": {
    "extracted_concepts": 25,
    "confidence_avg": 0.87,
    "processing_time": 12.5,
    "tokens_used": 1500
  },
  "comparison": {
    "baseline": {
      "extracted_concepts": 20,
      "confidence_avg": 0.82
    },
    "improvement": {
      "concepts": "+25%",
      "confidence": "+6%"
    }
  }
}
```

**GET** `/prompts`

**Response**:
```json
{
  "prompts": [
    {
      "id": "uuid",
      "agent": "harvester",
      "version": "1.2.0",
      "template": "...",
      "metrics": {
        "usage_count": 150,
        "avg_confidence": 0.85,
        "success_rate": 0.92
      },
      "created_at": "2026-01-11T10:00:00Z"
    }
  ]
}
```

**Design Decisions**:
- ✅ Version control for prompts
- ✅ A/B testing support
- ✅ Performance metrics tracking
- ✅ Easy prompt swapping

---

##### 1.5 WebSocket API

**Endpoint**: `ws://localhost:8001/ws`

**Connection**:
```json
{
  "type": "connect",
  "document_id": "uuid",
  "subscriptions": ["concepts", "relationships", "progress"]
}
```

**Messages** (Server → Client):
```json
{
  "type": "concept_extracted",
  "timestamp": "2026-01-11T10:00:00Z",
  "data": {
    "concept_id": "uuid",
    "term": "Completion Date",
    "confidence": 0.95
  }
}
```

**Message Types**:
- `concept_extracted`: New concept discovered
- `relationship_created`: New relationship found
- `progress_update`: Processing progress
- `error`: Error occurred
- `completed`: Processing finished

**Design Decisions**:
- ✅ Real-time updates for better UX
- ✅ Subscription-based filtering
- ✅ Automatic reconnection
- ✅ Message queuing for reliability

---

### 2. Query API Design

#### 2.1 Unified Query Syntax

**Design Goal**: Single query interface that works across all data representations (relational, graph, vector).

**Query Format**:
```json
{
  "query": "Find all dates related to project completion",
  "filters": {
    "type": ["date"],
    "confidence_min": 0.8,
    "domain": ["microsoft_cdm"]
  },
  "representations": ["relational", "graph", "vector"],
  "limit": 20
}
```

**Query Routing Algorithm**:
1. Parse query into components
2. Identify optimal representation(s) based on query type
3. Route to appropriate database(s)
4. Merge results from multiple representations
5. Rank and return unified results

**Query Types**:
- **Keyword Search**: Elasticsearch (full-text)
- **Semantic Search**: Pinecone (vector)
- **Relationship Queries**: Neo4j (graph)
- **Structured Queries**: PostgreSQL (relational)
- **Hybrid Queries**: Multiple databases, merge results

**Design Decisions**:
- ✅ Single query interface for simplicity
- ✅ Automatic routing based on query type
- ✅ Hybrid search for best results
- ✅ Performance optimization through smart routing

---

#### 2.2 Concept Variation Detection

**Algorithm**:
1. **Exact Match**: Check for identical terms
2. **Normalization**: Normalize terms (lowercase, remove punctuation)
3. **Synonym Detection**: Use domain models and knowledge bases
4. **Abbreviation Matching**: Map abbreviations to full terms
5. **Semantic Similarity**: Use embeddings for fuzzy matching

**API Endpoint**: **POST** `/concepts/match`

**Request**:
```json
{
  "term": "Completion Date",
  "document_id": "uuid",
  "threshold": 0.8
}
```

**Response**:
```json
{
  "matches": [
    {
      "concept_id": "uuid",
      "term": "completion date",
      "similarity": 0.95,
      "match_type": "normalized"
    },
    {
      "concept_id": "uuid",
      "term": "finish date",
      "similarity": 0.87,
      "match_type": "synonym"
    }
  ]
}
```

**Design Decisions**:
- ✅ Multi-stage matching for accuracy
- ✅ Configurable similarity threshold
- ✅ Match type explanation for transparency

---

### 3. Error Handling & Status Codes

**Standard Error Response**:
```json
{
  "error": {
    "code": "INVALID_PDF",
    "message": "PDF file is corrupted or invalid",
    "details": {
      "file_size": 1024,
      "file_type": "application/pdf"
    },
    "timestamp": "2026-01-11T10:00:00Z",
    "request_id": "uuid"
  }
}
```

**Error Codes**:
- `INVALID_PDF`: PDF file is invalid
- `PROCESSING_FAILED`: Analysis failed
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `DATABASE_ERROR`: Database operation failed
- `AGENT_ERROR`: Agent processing failed
- `VALIDATION_ERROR`: Request validation failed

**Design Decisions**:
- ✅ Consistent error format
- ✅ Request ID for debugging
- ✅ Detailed error messages
- ✅ Appropriate HTTP status codes

---

## Data Model Design

### 1. PostgreSQL Schema (Relational Data)

#### 1.1 Documents Table
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    page_count INTEGER,
    structure JSONB,  -- Document structure (sections, pages)
    metadata JSONB,   -- Creation date, author, version
    status VARCHAR(50) DEFAULT 'pending',  -- pending, processing, completed, error
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_created_at ON documents(created_at);
CREATE INDEX idx_documents_structure ON documents USING GIN(structure);
```

#### 1.2 Concepts Table
```sql
CREATE TABLE concepts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    term VARCHAR(500) NOT NULL,
    type VARCHAR(100) NOT NULL,  -- concept, hypernode, entity, date, etc.
    node_group VARCHAR(50) NOT NULL,  -- concept, hypernode, domain, prior
    data_type VARCHAR(50),  -- entity, date, location, organization, person, money, legal, condition
    category VARCHAR(200),
    explanation TEXT,
    confidence DECIMAL(3,2) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    assessment VARCHAR(20) NOT NULL,  -- always_true, usually_true, sometimes_true
    source_location JSONB,  -- {page, section, x, y, boundingBox}
    ui_group VARCHAR(100),  -- Grouping for UI display (e.g., "Regulations", "Reality Priors")
    extracted_by VARCHAR(100),  -- Agent name (HARVESTER, ARCHITECT, etc.)
    domain_mapping JSONB,  -- Domain model mapping
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_concepts_document_id ON concepts(document_id);
CREATE INDEX idx_concepts_term ON concepts(term);
CREATE INDEX idx_concepts_type ON concepts(type);
CREATE INDEX idx_concepts_confidence ON concepts(confidence);
CREATE INDEX idx_concepts_assessment ON concepts(assessment);
CREATE INDEX idx_concepts_search ON concepts USING GIN(to_tsvector('english', term));
```

#### 1.3 Relationships Table
```sql
CREATE TABLE relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_concept_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
    target_concept_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL,  -- relates_to, part_of, depends_on, etc.
    confidence DECIMAL(3,2) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    strength DECIMAL(3,2),  -- Relationship strength (0-1)
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_relationships_source ON relationships(source_concept_id);
CREATE INDEX idx_relationships_target ON relationships(target_concept_id);
CREATE INDEX idx_relationships_type ON relationships(type);
```

#### 1.4 Domain Models Table
```sql
CREATE TABLE domain_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,  -- microsoft_cdm, accounting, etc.
    version VARCHAR(50),
    description TEXT,
    sensitivity VARCHAR(20),  -- LOW, MEDIUM, HIGH
    schema JSONB NOT NULL,  -- Full domain model schema
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_domain_models_name ON domain_models(name);
```

#### 1.5 Reality Priors Table
```sql
CREATE TABLE reality_priors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    axiom TEXT NOT NULL,  -- The reality prior statement (e.g., "All data centers must comply with GDPR")
    weight DECIMAL(3,2) DEFAULT 0.9 CHECK (weight >= 0 AND weight <= 1),  -- Confidence/importance weight
    source VARCHAR(100),  -- Where this prior came from (agent, user, domain model)
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reality_priors_document_id ON reality_priors(document_id);
```

#### 1.6 Hypotheses/Claims Table
```sql
CREATE TABLE hypotheses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    target_concept_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
    claim TEXT NOT NULL,  -- The hypothesis/claim statement
    evidence TEXT NOT NULL,  -- Supporting evidence for the claim
    status VARCHAR(20) NOT NULL DEFAULT 'PROPOSED',  -- PROPOSED, ACCEPTED, REJECTED
    alternative_to UUID REFERENCES hypotheses(id),  -- If this is an alternative hypothesis
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_hypotheses_document_id ON hypotheses(document_id);
CREATE INDEX idx_hypotheses_concept_id ON hypotheses(target_concept_id);
CREATE INDEX idx_hypotheses_status ON hypotheses(status);
```

#### 1.7 Taxonomies Table
```sql
CREATE TABLE taxonomies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES concepts(id) ON DELETE CASCADE,  -- Parent concept (e.g., domain)
    child_id UUID REFERENCES concepts(id) ON DELETE CASCADE,  -- Child concept
    type VARCHAR(20) NOT NULL,  -- is_a, part_of
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_taxonomies_parent ON taxonomies(parent_id);
CREATE INDEX idx_taxonomies_child ON taxonomies(child_id);
CREATE INDEX idx_taxonomies_type ON taxonomies(type);
```

#### 1.8 Hooks Table
```sql
CREATE TABLE hooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trigger_type VARCHAR(100) NOT NULL,  -- date_discovered, legal_concept_discovered, etc.
    action_type VARCHAR(100) NOT NULL,  -- activate_task, import_domain, etc.
    configuration JSONB NOT NULL,  -- Hook-specific configuration
    enabled BOOLEAN DEFAULT TRUE,
    effectiveness_metrics JSONB,  -- Success rate, false positives, etc.
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_hooks_trigger_type ON hooks(trigger_type);
CREATE INDEX idx_hooks_enabled ON hooks(enabled);
```

#### 1.9 Questions Table
```json
{
  "id": "uuid",
  "document_id": "uuid",
  "question": "What does the date in Section 3.2 relate to?",
  "type": "temporal|entity|concept",
  "priority": "high|medium|low",
  "status": "unanswered|answered|auto_answered",
  "answer": {
    "text": "The date relates to document creation",
    "confidence": 0.95,
    "source": {
      "concept_id": "uuid",
      "location": "Section 3.2"
    }
  },
  "tags": ["date", "temporal", "section_3.2"],
  "created_at": "2026-01-11T10:00:00Z",
  "answered_at": "2026-01-11T10:05:00Z"
}
```

**Design Decisions**:
- ✅ JSONB for flexible schema (document structure, metadata)
- ✅ Proper indexes for performance
- ✅ Foreign keys for data integrity
- ✅ Timestamps for auditing
- ✅ Assessment indicators as first-class fields

---

### 2. Neo4j Schema (Graph Data)

#### 2.1 Node Labels
- `Concept`: Extracted concepts (type: "concept")
- `Hypernode`: Context groupings/clusters (type: "hypernode")
- `Domain`: Domain models (e.g., "Legal Framework", "Financial")
- `RealityPrior`: Axioms/reality priors (e.g., "All data centers must comply with GDPR")
- `Document`: Documents
- `Entity`: Named entities (people, organizations, locations, etc.)
- `Hypothesis`: Claims/hypotheses about concepts

#### 2.2 Relationship Types
- `RELATES_TO`: General relationship between concepts
- `PART_OF`: Hierarchical relationship (part-whole)
- `IS_A`: Taxonomic relationship (is-a hierarchy)
- `DEPENDS_ON`: Dependency relationship
- `SIMILAR_TO`: Similarity relationship
- `REFERENCES`: Document reference
- `MATCHES_DOMAIN`: Domain model match
- `HAS_HYPOTHESIS`: Concept has hypothesis/claim
- `EVIDENCES`: Hypothesis evidences concept
- `CONTRADICTS`: Contradictory relationship
- `STRUCTURAL`: Structural relationship (document structure)
- `SEMANTIC`: Semantic relationship (meaning-based)
- `HYPERLINK`: Hyperlink relationship (cross-reference)

#### 2.3 Example Cypher Queries

**Create Concept Node**:
```cypher
CREATE (c:Concept {
  id: $id,
  term: $term,
  type: $type,
  confidence: $confidence,
  assessment: $assessment
})
RETURN c
```

**Create Relationship**:
```cypher
MATCH (a:Concept {id: $source_id})
MATCH (b:Concept {id: $target_id})
CREATE (a)-[r:RELATES_TO {
  type: $rel_type,
  confidence: $confidence,
  strength: $strength
}]->(b)
RETURN r
```

**Find Paths**:
```cypher
MATCH path = (a:Concept {id: $source_id})-[*1..5]-(b:Concept {id: $target_id})
RETURN path
ORDER BY length(path)
LIMIT 10
```

**Design Decisions**:
- ✅ Neo4j for relationship queries
- ✅ Flexible property schema
- ✅ Efficient path finding
- ✅ Graph algorithms support

---

### 3. Pinecone Schema (Vector Data)

#### 3.1 Index Configuration
```python
{
    "name": "pdf-concept-tagger",
    "dimension": 1536,  # OpenAI ada-002
    "metric": "cosine",
    "pods": 1,
    "replicas": 1,
    "pod_type": "p1.x1"
}
```

#### 3.2 Vector Metadata
```json
{
  "id": "concept_uuid",
  "values": [0.123, 0.456, ...],  // 1536 dimensions
  "metadata": {
    "concept_id": "uuid",
    "document_id": "uuid",
    "term": "Completion Date",
    "type": "date",
    "confidence": 0.95
  }
}
```

**Design Decisions**:
- ✅ OpenAI embeddings (1536 dimensions)
- ✅ Metadata for filtering
- ✅ Cosine similarity for semantic search
- ✅ Managed service for reliability

---

### 4. Elasticsearch Schema (Full-Text Search)

#### 4.1 Index Mapping
```json
{
  "mappings": {
    "properties": {
      "term": {
        "type": "text",
        "analyzer": "english",
        "fields": {
          "keyword": {"type": "keyword"}
        }
      },
      "type": {"type": "keyword"},
      "confidence": {"type": "float"},
      "assessment": {"type": "keyword"},
      "document_id": {"type": "keyword"},
      "created_at": {"type": "date"}
    }
  }
}
```

**Design Decisions**:
- ✅ Full-text search for keyword queries
- ✅ Faceted search support
- ✅ English analyzer for better results

---

## UX Design

### 1. User Journey Maps

#### 1.1 Document Analysis Journey
1. **Upload**: User uploads PDF
2. **Processing**: Real-time progress updates
3. **Results**: Concepts displayed in graph
4. **Exploration**: User explores relationships
5. **Insights**: System highlights important discoveries

#### 1.2 Concept Discovery Journey
1. **Search**: User searches for concept
2. **Results**: Filtered concept list
3. **Detail**: User clicks concept
4. **Relationships**: View related concepts
5. **Context**: See source location in document

### 2. Graph Visualization (D3.js)

#### 2.1 Live Modeling Visualization

**Component**: `GraphView.tsx` (D3.js Force-Directed Graph)

**Features** (matching prototype):
- ✅ **Real-time updates**: Live graph updates via WebSocket as agents discover concepts
- ✅ **Force-directed layout**: D3 force simulation with collision detection
- ✅ **Interactive nodes**: Drag nodes, click to inspect, hover for details
- ✅ **Complete node types** (matching prototype):
  - **Concepts** (circles, indigo) - extracted entities/concepts (type: "concept")
  - **Hypernodes** (squares, orange) - context groupings/clusters (type: "hypernode")
  - **Domains** (diamonds, pink) - domain models (e.g., "Legal Framework")
  - **Reality Priors** (diamonds, pink) - axioms/reality priors (e.g., "All data centers must comply with GDPR")
- ✅ **Relationship types**:
  - Structural relationships (dashed lines)
  - Semantic relationships (solid lines)
  - Hyperlink relationships (pink lines)
  - Link labels showing predicates
- ✅ **Visual effects**: Glow on selection, arrows on edges, link labels
- ✅ **Live streaming**: Graph updates as agents process documents in real-time
- ✅ **Node highlighting**: Highlight related nodes on selection
- ✅ **Hypotheses/Claims**: Display hypotheses linked to concepts
- ✅ **Responsive**: Auto-resize with container, maintains node positions

**Implementation**:
```typescript
// src/components/graph/GraphView.tsx
import * as d3 from 'd3';
import { useEffect, useRef } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface GraphViewProps {
  documentId?: string;
  onNodeClick?: (node: GraphNode) => void;
}

export function GraphView({ documentId, onNodeClick }: GraphViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const simulationRef = useRef<d3.Simulation<GraphNode, GraphLink> | null>(null);
  
  // WebSocket for live updates
  const { data: graphUpdate } = useWebSocket(`/ws?document_id=${documentId}`);
  
  useEffect(() => {
    if (!containerRef.current) return;
    
    // Initialize D3 force simulation (same as prototype)
    const simulation = d3.forceSimulation<GraphNode, GraphLink>()
      .force('link', d3.forceLink().id(d => d.id).distance(150))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter())
      .force('collide', d3.forceCollide(30));
    
    simulationRef.current = simulation;
    
    // Render graph...
  }, []);
  
  // Update graph on WebSocket messages
  useEffect(() => {
    if (graphUpdate?.type === 'concept_extracted' || graphUpdate?.type === 'relationship_created') {
      updateGraph(graphUpdate.data);
    }
  }, [graphUpdate]);
  
  return <div ref={containerRef} className="w-full h-full" />;
}
```

**WebSocket Integration**:
- Subscribe to document-specific updates: `ws://localhost:8001/ws?document_id={id}`
- Receive real-time events (matching prototype AgentPacket protocol):
  - `concept_extracted` → Add/update concept node (circle, indigo)
  - `hypernode_created` → Add/update hypernode (square, orange)
  - `domain_created` → Add/update domain node (diamond, pink)
  - `prior_created` → Add/update reality prior node (diamond, pink)
  - `relationship_created` → Add/update edge (with type: structural/semantic/hyperlink)
  - `taxonomy_created` → Add/update taxonomy relationship (is_a/part_of)
  - `hypothesis_created` → Add/update hypothesis/claim
  - `progress_update` → Show processing status
- Graph updates smoothly without full re-render (preserves node positions)

**Design Decisions**:
- ✅ Keep D3.js (same as prototype) for maximum control and performance
- ✅ Real-time updates via WebSocket (not polling)
- ✅ Preserve node positions during updates (smooth transitions)
- ✅ Same visual style as prototype (dark theme, node types, colors)
- ✅ Interactive features match prototype (drag, click, highlight)

---

### 3. Component Library

#### 3.1 Common Components

**Filter Component** (`FilterBar.tsx`):
```typescript
interface FilterBarProps {
  filters: {
    type?: string[];
    confidence_min?: number;
    domain?: string[];
    assessment?: string[];
  };
  onFilterChange: (filters: FilterState) => void;
  facets: FacetData;
}
```

**Assessment Indicator Component** (`AssessmentBadge.tsx`):
```typescript
interface AssessmentBadgeProps {
  assessment: "always_true" | "usually_true" | "sometimes_true";
  confidence: number;
  showTooltip?: boolean;
}
```

**Citation Component** (`Citation.tsx`):
```typescript
interface CitationProps {
  source: {
    document_id: string;
    page: number;
    section: string;
    location?: { x: number; y: number };
  };
  onClick?: () => void;
}
```

**Graph Visualization** (`GraphView.tsx`):
```typescript
interface GraphViewProps {
  documentId?: string;
  nodes?: GraphNode[];
  edges?: GraphEdge[];
  layout?: "force" | "hierarchical" | "circular";
  onNodeClick?: (node: GraphNode) => void;
  onNodeDrag?: (node: GraphNode) => void;
  realTime?: boolean;  // Enable WebSocket live updates
}
```

**Timeline Visualization** (`TimelineView.tsx`):
```typescript
interface TimelineViewProps {
  events: TemporalEvent[];
  onEventClick?: (event: TemporalEvent) => void;
  layout?: "horizontal" | "vertical";
}
```

**Progress Indicator** (`ProgressBar.tsx`):
```typescript
interface ProgressBarProps {
  progress: number;  // 0-1
  status: "processing" | "completed" | "error";
  message?: string;
}
```

**Design Decisions**:
- ✅ Reusable components for consistency
- ✅ TypeScript for type safety
- ✅ Accessible design (ARIA labels)
- ✅ Responsive layouts

---

### 3. Screen Designs

#### 3.1 Main Dashboard
- **Layout**: 3-column (Document List | Graph View | Concept Inspector)
- **Components**: Document upload, graph visualization, concept list
- **Interactions**: Drag-and-drop upload, graph navigation, concept selection

#### 3.2 Concept Detail View
- **Layout**: 2-column (Concept Info | Relationships)
- **Components**: Concept card, relationship graph, source citation
- **Interactions**: Expand relationships, navigate to source

#### 3.3 Graph Visualization View (Live Modeling)
- **Layout**: Full-screen or panel view
- **Components**: D3.js force-directed graph, legend, controls
- **Features**:
  - **Live updates**: Graph updates in real-time as agents process documents
  - **Complete node types** (matching prototype):
    - Concepts (circles, indigo) - extracted entities/concepts
    - Hypernodes (squares, orange) - context groupings
    - Domains (diamonds, pink) - domain models
    - Reality Priors (diamonds, pink) - axioms/reality priors
  - **Relationship types**:
    - Structural (dashed lines) - document structure relationships
    - Semantic (solid lines) - meaning-based relationships
    - Hyperlink (pink lines) - cross-references
    - Taxonomy (is_a/part_of) - hierarchical relationships
  - **Hypotheses/Claims**: Display linked to concepts
  - **Interactions**: Drag nodes, click to inspect, zoom/pan, filter by type
  - **Visual effects**: Glow on selection, animated edges, link labels
- **Real-time**: WebSocket connection for live concept/relationship discovery
- **Interactions**: 
  - Click node → Show concept details in side panel (including hypotheses)
  - Drag node → Reposition in graph
  - Hover → Show tooltip with concept info
  - Filter → Show/hide node types (concepts, hypernodes, domains, priors)

#### 3.3 Document Structure View
- **Layout**: Tree navigation + content view
- **Components**: Document tree, section viewer, concept highlights
- **Interactions**: Expand/collapse sections, click to navigate

**Design Decisions**:
- ✅ Multi-panel layouts for information density
- ✅ Consistent navigation patterns
- ✅ Clear visual hierarchy

---

## Component Design

### 1. Frontend Component Architecture

```
src/
├── components/
│   ├── ui/              # Base UI components (Button, Card, Modal)
│   ├── common/          # Common components (FilterBar, AssessmentBadge)
│   ├── graph/           # Graph visualization (GraphView, Node, Edge)
│   ├── concepts/        # Concept components (ConceptList, ConceptInspector)
│   ├── documents/       # Document components (PDFViewer, DocumentTree)
│   └── prompts/         # Prompt experimentation (PromptEditor, PromptTester)
├── hooks/               # React hooks (useGraph, useConcepts, useWebSocket)
├── services/           # API clients (api.ts, websocket.ts)
├── stores/             # Zustand stores (graphStore, uiStore)
└── App.tsx             # Main app component
```

### 2. Component Specifications

See [COMPONENT_SPECS.md](COMPONENT_SPECS.md) for detailed component specifications.

**Design Decisions**:
- ✅ Modular component structure
- ✅ Separation of concerns (UI, logic, state)
- ✅ Reusable hooks and services
- ✅ Type-safe with TypeScript

---

## Agent Architecture Design

### 1. LangChain Agent Structure

#### 1.1 Base Agent Class
```python
class BaseAgent:
    """Base class for all agents"""
    def __init__(self, llm, tools, memory):
        self.llm = llm
        self.tools = tools
        self.memory = memory
        self.agent = self._create_agent()
    
    def _create_agent(self):
        """Create LangChain agent"""
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True
        )
    
    async def process(self, input_data: dict) -> dict:
        """Process input and return results"""
        result = await self.agent.arun(input_data)
        return self._format_result(result)
```

#### 1.2 HARVESTER Agent
**Purpose**: Extract entities and concepts from documents

**Tools**:
- `extract_text`: Extract text from PDF
- `extract_structure`: Extract document structure
- `identify_entities`: Identify named entities
- `extract_concepts`: Extract abstract concepts
- `calculate_confidence`: Calculate confidence scores

**Prompt Template**: `prompts/harvester_prompt.txt`

**Output**: List of extracted concepts with confidence scores

#### 1.3 ARCHITECT Agent
**Purpose**: Define domain structures and relationships

**Tools**:
- `create_relationship`: Create concept relationships
- `match_domain_model`: Match to domain models
- `build_graph`: Build graph structure
- `validate_structure`: Validate domain structure

**Prompt Template**: `prompts/architect_prompt.txt`

**Output**: Graph structure with relationships

#### 1.4 CURATOR Agent
**Purpose**: Organize concepts into taxonomies

**Tools**:
- `create_taxonomy`: Create taxonomy hierarchy
- `categorize_concept`: Categorize concepts
- `validate_taxonomy`: Validate taxonomy structure
- `merge_taxonomies`: Merge related taxonomies

**Prompt Template**: `prompts/curator_prompt.txt`

**Output**: Taxonomy structure

#### 1.5 CRITIC Agent
**Purpose**: Evaluate quality and validate extractions

**Tools**:
- `evaluate_quality`: Evaluate extraction quality
- `detect_conflicts`: Detect contradictions
- `validate_confidence`: Validate confidence scores
- `suggest_improvements`: Suggest improvements

**Prompt Template**: `prompts/critic_prompt.txt`

**Output**: Quality scores and validation results

#### 1.6 OBSERVER Agent
**Purpose**: Monitor and explain agent actions

**Tools**:
- `log_action`: Log agent actions
- `explain_decision`: Explain agent decisions
- `generate_insights`: Generate insights
- `track_metrics`: Track performance metrics

**Prompt Template**: `prompts/observer_prompt.txt`

**Output**: Insights and explanations

**Design Decisions**:
- ✅ LangChain agents for industry-standard approach
- ✅ Tool-based architecture for extensibility
- ✅ Prompt templates for easy experimentation
- ✅ Async processing for performance

---

### 2. LangGraph Workflow

#### 2.1 State Schema
```python
class AgentState(TypedDict):
    document_id: str
    document_content: str
    concepts: List[Concept]
    relationships: List[Relationship]
    domain_models: List[DomainModel]
    quality_scores: Dict[str, float]
    current_agent: str
    step: int
    errors: List[str]
```

#### 2.2 Workflow Graph
```
START
  ↓
HARVESTER (extract concepts)
  ↓
ARCHITECT (create relationships)
  ↓
CURATOR (organize taxonomies)
  ↓
CRITIC (validate quality)
  ↓
OBSERVER (generate insights)
  ↓
END
```

#### 2.3 Conditional Edges
- **If quality low**: Loop back to HARVESTER
- **If conflicts detected**: Route to CRITIC
- **If domain match found**: Route to ARCHITECT

**Design Decisions**:
- ✅ State machine for workflow control
- ✅ Conditional routing for flexibility
- ✅ Error handling and retry logic
- ✅ State persistence for recovery

---

## RAG Pipeline Design

### 1. Document Processing

#### 1.1 Document Loader
```python
class PDFDocumentLoader:
    """Load and parse PDF documents"""
    def load(self, file_path: str) -> List[Document]:
        # Use Docling or pdfplumber
        # Extract text, structure, metadata
        pass
    
    def chunk(self, document: Document, chunk_size: int = 1000) -> List[Chunk]:
        # Chunk by sections or fixed size
        # Preserve metadata
        pass
```

#### 1.2 Embedding Generation
```python
class EmbeddingService:
    """Generate embeddings for documents"""
    def __init__(self, model: str = "text-embedding-ada-002"):
        self.model = OpenAIEmbeddings(model=model)
    
    async def embed(self, texts: List[str]) -> List[List[float]]:
        # Batch embedding generation
        # Store in Pinecone
        pass
```

#### 1.3 Retrieval Chain
```python
class HybridRetriever:
    """Hybrid retrieval (vector + keyword)"""
    def __init__(self):
        self.vector_retriever = PineconeRetriever()
        self.keyword_retriever = ElasticsearchRetriever()
    
    async def retrieve(self, query: str, k: int = 10) -> List[Document]:
        # Retrieve from both sources
        # Rerank and merge results
        pass
```

**Design Decisions**:
- ✅ LangChain RAG components
- ✅ Hybrid search for best results
- ✅ Chunking strategy for optimal retrieval
- ✅ Metadata preservation

---

## Domain Model Integration Design

### 1. Domain Model Loader

```python
class DomainModelLoader:
    """Load domain models from JSON"""
    def load(self, model_name: str) -> DomainModel:
        # Load from domain_models/{model_name}.json
        # Parse schema, tables, relationships
        pass
    
    def match(self, document_content: str) -> List[DomainMatch]:
        # Use RAG to match document to domain models
        # Score matches
        pass
```

### 2. Schema Mapping

```python
class SchemaMapper:
    """Map extracted data to domain schemas"""
    def map(self, concept: Concept, domain: DomainModel) -> SchemaMapping:
        # Map concept to domain schema field
        # Validate against schema
        # Return mapping with confidence
        pass
```

**Design Decisions**:
- ✅ JSON-based domain models for flexibility
- ✅ Automatic domain detection
- ✅ Schema validation
- ✅ Mapping confidence scores

---

## Hook System Design

### 1. Hook Architecture

```python
class HookSystem:
    """Hook system for automatic task activation"""
    def __init__(self):
        self.hooks: Dict[str, List[Hook]] = {}
        self.load_hooks()
    
    def register(self, trigger: str, action: Callable, config: dict):
        """Register a hook"""
        hook = Hook(trigger=trigger, action=action, config=config)
        self.hooks[trigger].append(hook)
    
    async def trigger(self, trigger: str, context: dict):
        """Trigger hooks for a given event"""
        for hook in self.hooks.get(trigger, []):
            if hook.enabled:
                await hook.execute(context)
```

### 2. Hook Types

**Date Discovery Hook**:
```python
@hook_system.register("date_discovered")
async def activate_date_store(context):
    # Activate date normalization
    # Create temporal model
    # Analyze date relationships
    pass
```

**Domain Model Hook**:
```python
@hook_system.register("domain_match_found")
async def import_domain_model(context):
    # Import domain model schema
    # Activate domain-specific extraction
    # Map concepts to schema
    pass
```

**Design Decisions**:
- ✅ Event-driven architecture
- ✅ Configurable hooks
- ✅ Hook effectiveness tracking
- ✅ Easy to extend

---

## Assessment Indicator Design

### 1. Assessment Levels

**Always True**:
- Explicit statements
- High confidence (≥0.9)
- Clear source
- Example: "Document created: 2024-01-15"

**Usually True**:
- Likely but not certain
- Medium confidence (0.7-0.9)
- Some uncertainty
- Example: "Proposed completion: 2024-06-30"

**Sometimes True**:
- Conditional/uncertain
- Low confidence (<0.7)
- Tentative language
- Example: "May complete by 2024-06-30"

### 2. Component Activation Rules

```python
def activate_component(assessment: str, component: str):
    if assessment == "always_true":
        # Full activation, no validation needed
        activate_fully(component)
    elif assessment == "usually_true":
        # Activation with validation
        activate_with_validation(component)
    elif assessment == "sometimes_true":
        # Conditional activation or user confirmation
        activate_conditionally(component)
```

**Design Decisions**:
- ✅ Three-level assessment system
- ✅ Conditional component activation
- ✅ Resource optimization
- ✅ User transparency

---

## Performance & Scalability Design

### 1. Caching Strategy

**Redis Caching**:
- Concept queries (TTL: 1 hour)
- Graph queries (TTL: 30 minutes)
- Domain model matches (TTL: 24 hours)

### 2. Database Optimization

**PostgreSQL**:
- Indexes on frequently queried fields
- Full-text search indexes
- Partitioning for large tables

**Neo4j**:
- Indexes on node properties
- Relationship type indexes
- Query optimization

**Pinecone**:
- Index configuration for performance
- Batch operations
- Metadata filtering

### 3. API Performance

- **Rate Limiting**: 100 requests/minute per API key
- **Pagination**: Default 20 items per page
- **Streaming**: For long-running operations
- **Async Processing**: Background tasks for heavy operations

**Design Decisions**:
- ✅ Multi-level caching
- ✅ Database optimization
- ✅ Rate limiting for fairness
- ✅ Async processing for scalability

---

## Design Decisions Summary

### Technology Choices
- ✅ **LangChain/LangGraph**: Industry standard, best ecosystem
- ✅ **PostgreSQL**: Best open-source RDBMS
- ✅ **Neo4j**: Best graph database, managed service
- ✅ **Pinecone**: Best managed vector DB
- ✅ **FastAPI**: Best async Python framework
- ✅ **React + Vite**: Fastest development

### Architecture Choices
- ✅ **Multi-agent system**: Separation of concerns
- ✅ **State machine**: Workflow control
- ✅ **Hook system**: Automatic task activation
- ✅ **Hybrid search**: Best retrieval results
- ✅ **Multi-representation storage**: Optimal for each data type

### Design Principles
- ✅ **Pragmatic**: Use proven tools, don't reinvent
- ✅ **Incremental**: Build incrementally, test early
- ✅ **Transparent**: Document decisions, show alternatives
- ✅ **Scalable**: Design for growth
- ✅ **Maintainable**: Clear structure, good documentation

---

## Next Steps

1. **Review Design**: Stakeholder review of design document
2. **Create Tasks**: Break down design into actionable tasks
3. **Prototype**: Build key components to validate design
4. **Iterate**: Refine based on prototype learnings
5. **Implement**: Follow TASKS.md for implementation

---

**Last Updated**: 2026-01-11  
**Status**: Ready for Review  
**Next**: Create detailed implementation tasks
