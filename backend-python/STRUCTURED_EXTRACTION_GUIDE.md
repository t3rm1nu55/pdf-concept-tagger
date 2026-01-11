# Structured Extraction Pipeline Guide

This guide explains the **"pipeline of specialized extractors"** approach, which replaces the "press button, get ontology" model.

## Philosophy

**There is no single "press button, get ontology" model.**

Instead, we compose specialized extractors into a pipeline that produces:
1. **Document Tree** (Docling) → Document hierarchy
2. **Concept Inventory** → Concept candidates
3. **Taxonomy Draft** (LLM + clustering) → Hierarchical relationships
4. **Link Graph** (OpenIE + LLM) → Edges with evidence

## Pipeline Architecture

```
PDF/DOCX Input
    ↓
[1] Document Tree Extractor (Docling)
    → Document → Section → Clause → Block → Table
    ↓
[2] Concept Inventory Builder
    → Extract entities/keyphrases
    → Cluster by embedding similarity
    → LLM proposes canonical forms
    ↓
[3] Taxonomy Builder (LLM + Clustering)
    → Propose parent/child relations
    → Validate with evidence spans
    → Score confidence
    ↓
[4] Link Extractor (OpenIE + LLM)
    → Extract (subject, relation, object) triples
    → Require evidence spans
    → Run contradiction checks
    ↓
Complete Ontology Output
```

## Key Principles

### 1. Evidence Spans (Required)

**Every relationship MUST have evidence spans** - exact quoted text with character offsets.

```python
evidence = EvidenceSpan(
    text="GDPR requires data processing agreements",
    start_char=1234,
    end_char=1280,
    page_number=5,
    section_id="sec_3_2",
    confidence=0.9,
)
```

**Why?** Prevents LLM hallucination. If you can't quote the text, the relationship doesn't exist.

### 2. Schema Constraints

**Constrain relation types** to your operating model:

```python
relation_schema = {
    "dependency": ["depends_on", "requires", "triggers"],
    "mitigation": ["mitigates", "controls", "reduces"],
    "supersession": ["supersedes", "replaces", "updates"],
    "definition": ["defines", "specifies", "describes"],
}
```

**Why?** Prevents arbitrary relationships. Forces alignment to your domain model.

### 3. Confidence Scores

**Every extraction has a confidence score** (0.0-1.0):

- **1.0**: Explicit statement, high confidence
- **0.7**: Likely but inferred
- **0.5**: Uncertain, needs review
- **0.3**: Low confidence, probably skip

**Why?** Enables filtering and governance. Low-confidence extractions can be flagged for review.

### 4. Validation & Contradiction Checks

**Run validation** to catch:
- Missing evidence spans
- Contradictory relationships
- Duplicate edges
- Low confidence scores

**Why?** Ensures quality and consistency.

## Implementation

### Stage 1: Document Tree (Most Solved)

Use **Docling** for document structure extraction:

```python
from docling_integration import DoclingIntegration

docling = DoclingIntegration()
tree_nodes = await docling.extract_document_tree("document.pdf")
```

**Output**: Document → Section → Clause → Block → Table hierarchy with stable IDs.

### Stage 2: Concept Inventory (Partially Solved)

Extract concepts using:
- NER (Named Entity Recognition)
- Keyphrase extraction
- LLM-assisted concept identification

```python
from structured_extraction_pipeline import StructuredExtractionPipeline

pipeline = StructuredExtractionPipeline()
concepts = await pipeline.extract_concept_inventory(tree_nodes)
```

**Output**: Concept registry with canonical terms, synonyms, definitions, examples.

### Stage 3: Taxonomy Builder (Partially Solved)

Build taxonomy using:
- **If seed taxonomy exists**: TaxoExpan-style expansion
- **If no seed**: LLM + clustering from scratch

```python
from taxonomy_builder import TaxonomyBuilder

builder = TaxonomyBuilder()
taxonomy_edges = await builder.build_taxonomy(
    concept_registry=concepts,
    seed_taxonomy=existing_taxonomy,  # Optional
)
```

**Output**: Taxonomy edges (parent_of, part_of, etc.) with evidence spans.

### Stage 4: Link Extractor (GraphRAG)

Extract relationships using:
- **OpenIE**: Fast, high recall, noisy
- **LLM-based**: Slower, more accurate, schema-constrained

```python
from link_extractor import LinkExtractor

extractor = LinkExtractor(relation_schema=my_schema)
kg_edges = await extractor.extract_links(
    document_tree=tree_nodes,
    concept_registry=concepts,
    use_openie=True,
    use_llm=True,
)
```

**Output**: Knowledge graph edges with evidence spans, validated and deduplicated.

## Output Schema

The pipeline produces structured output:

```python
output = ExtractionPipelineOutput(
    document_id="doc_123",
    document_tree=[...],  # DocumentTreeNode[]
    concept_registry=[...],  # ConceptRegistry[]
    taxonomy_edges=[...],  # TaxonomyEdge[]
    kg_edges=[...],  # KnowledgeGraphEdge[]
    validation_errors=[...],
    confidence_summary={...},
)
```

## Integration with Existing System

### With Your Agents

Your existing agents map to pipeline stages:

- **HARVESTER** → Concept Inventory Builder
- **ARCHITECT** → Link Extractor (KG edges)
- **CURATOR** → Taxonomy Builder
- **SYSTEM** → Document Tree Extractor (or use Docling directly)

### Migration Path

1. **Add Docling** for document structure (Stage 1)
2. **Enhance HARVESTER** with evidence spans (Stage 2)
3. **Enhance CURATOR** with LLM + clustering (Stage 3)
4. **Enhance ARCHITECT** with OpenIE + schema constraints (Stage 4)

## Best Practices

1. **Always require evidence spans** for relationships
2. **Use schema constraints** to prevent arbitrary relations
3. **Run validation** after each stage
4. **Track confidence scores** throughout
5. **Iterate and refine** - taxonomy building is iterative
6. **Govern the output** - review low-confidence extractions

## Reality Checks

### Document Tree
✅ **Most solved** - Docling provides reliable structure

### Taxonomy
⚠️ **Partially solved** - Works well with seed taxonomy, needs iteration without seed

### Domains/Classification
✅ **Operationally solved** - Embedding + LLM zero-shot works

### Linkages
⚠️ **Requires discipline** - LLMs will invent edges unless constrained:
- Require evidence spans ✅
- Constrain relation types ✅
- Run contradiction checks ✅
- Keep confidence scores ✅

## Next Steps

1. **Integrate Docling** for document structure extraction
2. **Add evidence spans** to existing relationship extraction
3. **Implement taxonomy builder** with LLM + clustering
4. **Add validation** and contradiction checks
5. **Track confidence scores** throughout pipeline

## Resources

- [Docling Documentation](https://docling.readthedocs.io/)
- [TaxoExpan Research](https://arxiv.org/abs/2004.04935)
- [OpenIE Systems](https://nlp.stanford.edu/software/openie.html)
- [LlamaIndex Knowledge Graph](https://docs.llamaindex.ai/en/stable/module_guides/indexing/knowledge_graph/)
