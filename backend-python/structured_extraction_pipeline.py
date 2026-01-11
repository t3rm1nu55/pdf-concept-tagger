"""
Structured Extraction Pipeline

Implements the "pipeline of specialized extractors" approach:
1. Document Tree Extractor (Docling) → Document hierarchy
2. Concept Inventory Builder → Concept candidates
3. Taxonomy Builder (LLM + clustering) → Draft hierarchy
4. Link Extractor (OpenIE + LLM) → Edges with evidence

Based on: "There's no single 'press button, get ontology' model"
Instead: Compose specialized extractors into a pipeline.

Key principles:
- Evidence spans (exact text offsets)
- Schema constraints
- Confidence scores
- Provenance tracking
"""

from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import json


class EvidenceSpan(BaseModel):
    """
    Evidence span - exact text location supporting an extraction.
    
    Required for all relationships and taxonomy edges to ensure
    traceability and prevent LLM hallucination.
    """
    text: str = Field(..., description="Exact quoted text from document")
    start_char: int = Field(..., description="Character offset start")
    end_char: int = Field(..., description="Character offset end")
    page_number: int = Field(..., description="Page number where span appears")
    section_id: Optional[str] = Field(None, description="Section ID if available")
    confidence: float = Field(0.5, ge=0.0, le=1.0, description="Confidence in span accuracy")


class DocumentTreeNode(BaseModel):
    """
    Document tree node - hierarchical structure.
    
    Output from Docling-class tooling: Document → Section → Clause → Block → Table
    """
    id: str = Field(..., description="Stable ID for this node")
    type: str = Field(..., description="Node type: document, section, clause, block, table, cell")
    level: int = Field(..., description="Hierarchy level (0=document, 1=section, etc.)")
    title: Optional[str] = Field(None, description="Title/heading text")
    text: str = Field(..., description="Full text content")
    start_char: int = Field(..., description="Character offset start")
    end_char: int = Field(..., description="Character offset end")
    page_number: int = Field(..., description="Page number")
    parent_id: Optional[str] = Field(None, description="Parent node ID")
    children_ids: List[str] = Field(default_factory=list, description="Child node IDs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ConceptRegistry(BaseModel):
    """
    Concept registry - canonical concept with synonyms, definitions, examples.
    
    This is the "concept inventory" output from the pipeline.
    """
    canonical_id: str = Field(..., description="Canonical concept ID")
    canonical_term: str = Field(..., description="Primary term")
    synonyms: List[str] = Field(default_factory=list, description="Alternative terms/variants")
    definition_spans: List[EvidenceSpan] = Field(default_factory=list, description="Definition evidence")
    example_spans: List[EvidenceSpan] = Field(default_factory=list, description="Example evidence")
    category: str = Field(..., description="Category/domain")
    confidence: float = Field(0.5, ge=0.0, le=1.0, description="Overall confidence")
    extracted_by: str = Field(..., description="Which extractor found this")
    timestamp: datetime = Field(default_factory=datetime.now)


class TaxonomyEdge(BaseModel):
    """
    Taxonomy edge - hierarchical relationship with evidence.
    
    Types: parent_of, part_of, applies_to, etc.
    Each edge MUST have evidence spans.
    """
    parent_id: str = Field(..., description="Parent concept ID")
    child_id: str = Field(..., description="Child concept ID")
    relationship_type: str = Field(..., description="Type: is_a, part_of, applies_to, etc.")
    evidence_spans: List[EvidenceSpan] = Field(..., description="Evidence supporting this relationship")
    confidence: float = Field(0.5, ge=0.0, le=1.0, description="Confidence in relationship")
    extracted_by: str = Field(..., description="Which extractor found this")
    timestamp: datetime = Field(default_factory=datetime.now)


class KnowledgeGraphEdge(BaseModel):
    """
    Knowledge graph edge - relationship aligned to operating model.
    
    Examples:
    - "Obligation A depends on Condition B"
    - "Control C mitigates Risk R"
    - "Doc D supersedes Doc E"
    - "Field F maps to Schema element S"
    
    All edges require evidence spans.
    """
    source_id: str = Field(..., description="Source concept/node ID")
    target_id: str = Field(..., description="Target concept/node ID")
    predicate: str = Field(..., description="Relationship predicate")
    relationship_type: str = Field(..., description="Type: semantic, structural, dependency, etc.")
    evidence_spans: List[EvidenceSpan] = Field(..., description="Evidence supporting this relationship")
    confidence: float = Field(0.5, ge=0.0, le=1.0, description="Confidence in relationship")
    schema_aligned: bool = Field(False, description="Whether this aligns to a known schema")
    extracted_by: str = Field(..., description="Which extractor found this")
    timestamp: datetime = Field(default_factory=datetime.now)


class ExtractionPipelineOutput(BaseModel):
    """
    Complete pipeline output - all four structure types.
    
    This is what the pipeline produces:
    1. DocTree JSON
    2. Concept registry
    3. Taxonomy edges
    4. Knowledge graph edges
    """
    document_id: str = Field(..., description="Source document ID")
    document_metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    
    # 1. Document tree
    document_tree: List[DocumentTreeNode] = Field(default_factory=list, description="Document hierarchy")
    
    # 2. Concept registry
    concept_registry: List[ConceptRegistry] = Field(default_factory=list, description="Canonical concepts")
    
    # 3. Taxonomy edges
    taxonomy_edges: List[TaxonomyEdge] = Field(default_factory=list, description="Hierarchical relationships")
    
    # 4. Knowledge graph edges
    kg_edges: List[KnowledgeGraphEdge] = Field(default_factory=list, description="Concept relationships")
    
    # Validation results
    validation_errors: List[str] = Field(default_factory=list, description="Validation issues found")
    confidence_summary: Dict[str, float] = Field(default_factory=dict, description="Confidence statistics")
    
    timestamp: datetime = Field(default_factory=datetime.now)


class ExtractorType(str, Enum):
    """Types of extractors in the pipeline."""
    DOCUMENT_TREE = "document_tree"
    CONCEPT_INVENTORY = "concept_inventory"
    TAXONOMY_BUILDER = "taxonomy_builder"
    LINK_EXTRACTOR = "link_extractor"


class StructuredExtractionPipeline:
    """
    Structured extraction pipeline - composes specialized extractors.
    
    This implements the "pipeline of extractors" approach rather than
    a single "press button, get ontology" model.
    """
    
    def __init__(
        self,
        require_evidence: bool = True,
        min_confidence: float = 0.3,
        validate_schema: bool = True,
    ):
        """
        Initialize pipeline.
        
        Args:
            require_evidence: Require evidence spans for all relationships
            min_confidence: Minimum confidence threshold
            validate_schema: Validate against schema constraints
        """
        self.require_evidence = require_evidence
        self.min_confidence = min_confidence
        self.validate_schema = validate_schema
        self.extractors = {}
    
    def register_extractor(
        self,
        extractor_type: ExtractorType,
        extractor_func: callable,
    ):
        """Register an extractor function."""
        self.extractors[extractor_type] = extractor_func
    
    async def extract_document_tree(
        self,
        document_path: str,
        use_docling: bool = True,
    ) -> List[DocumentTreeNode]:
        """
        Extract document tree structure.
        
        This is the "most solved" part - use Docling or similar.
        
        Args:
            document_path: Path to PDF/DOCX
            use_docling: Use Docling if available, otherwise fallback
            
        Returns:
            List of document tree nodes
        """
        # TODO: Integrate Docling here
        # For now, return placeholder structure
        # In production, this would call Docling API or library
        
        if use_docling:
            # Docling integration would go here
            # docling_result = docling.convert(document_path)
            # return self._parse_docling_tree(docling_result)
            pass
        
        # Fallback: Basic structure extraction
        return []
    
    async def extract_concept_inventory(
        self,
        document_tree: List[DocumentTreeNode],
        existing_concepts: Optional[List[str]] = None,
    ) -> List[ConceptRegistry]:
        """
        Extract concept inventory - candidate terms/entities.
        
        This uses:
        - Entity extraction (NER)
        - Keyphrase extraction
        - LLM-assisted concept identification
        
        Args:
            document_tree: Document tree nodes
            existing_concepts: Existing concept IDs to avoid duplicates
            
        Returns:
            List of concept registries
        """
        concepts = []
        
        # Extract from each document node
        for node in document_tree:
            # Extract entities/keyphrases from node text
            # This would use NER, keyphrase extraction, or LLM
            
            # For now, placeholder
            # In production, this would:
            # 1. Extract candidate terms
            # 2. Cluster by embedding similarity
            # 3. Have LLM propose canonical forms
            # 4. Extract definition/example spans
            
            pass
        
        return concepts
    
    async def build_taxonomy(
        self,
        concept_registry: List[ConceptRegistry],
        seed_taxonomy: Optional[Dict[str, Any]] = None,
    ) -> List[TaxonomyEdge]:
        """
        Build taxonomy - hierarchical relationships.
        
        Uses LLM-assisted taxonomy building:
        - Extract candidate terms
        - Cluster by embedding similarity
        - Have LLM propose parent/child relations under constraints
        - Validate each edge with evidence and scoring
        
        Args:
            concept_registry: Concept inventory
            seed_taxonomy: Optional seed taxonomy to expand
            
        Returns:
            List of taxonomy edges with evidence
        """
        taxonomy_edges = []
        
        # If seed taxonomy exists, use TaxoExpan-style expansion
        if seed_taxonomy:
            # Expand existing taxonomy
            pass
        else:
            # Build from scratch using LLM + clustering
            # 1. Cluster concepts by embedding similarity
            # 2. LLM proposes parent/child relations
            # 3. Extract evidence spans for each relation
            # 4. Validate and score
            
            pass
        
        return taxonomy_edges
    
    async def extract_links(
        self,
        document_tree: List[DocumentTreeNode],
        concept_registry: List[ConceptRegistry],
        use_openie: bool = True,
        use_llm: bool = True,
    ) -> List[KnowledgeGraphEdge]:
        """
        Extract knowledge graph links.
        
        Uses two approaches:
        1. OpenIE - extract (subject, relation, object) triples (fast, high recall, noisy)
        2. LLM-based - prompt LLM to extract entities/relations into target schema
        
        Args:
            document_tree: Document tree nodes
            concept_registry: Concept inventory
            use_openie: Use OpenIE extraction
            use_llm: Use LLM-based extraction
            
        Returns:
            List of KG edges with evidence spans
        """
        kg_edges = []
        
        # OpenIE extraction (fast, noisy)
        if use_openie:
            # Extract triples from text
            # Filter by concept registry
            # Extract evidence spans
            pass
        
        # LLM-based extraction (slower, more accurate)
        if use_llm:
            # Prompt LLM with schema constraints
            # Extract entities/relations
            # Require evidence spans
            # Run contradiction checks
            # Resolve duplicate edges
            pass
        
        return kg_edges
    
    def validate_output(
        self,
        output: ExtractionPipelineOutput,
    ) -> List[str]:
        """
        Validate pipeline output.
        
        Checks:
        - All relationships have evidence spans (if required)
        - Confidence scores are within range
        - Schema constraints are met
        - No contradictions
        
        Args:
            output: Pipeline output to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check evidence spans
        if self.require_evidence:
            for edge in output.taxonomy_edges:
                if not edge.evidence_spans:
                    errors.append(f"Taxonomy edge {edge.parent_id}->{edge.child_id} missing evidence")
            
            for edge in output.kg_edges:
                if not edge.evidence_spans:
                    errors.append(f"KG edge {edge.source_id}->{edge.target_id} missing evidence")
        
        # Check confidence thresholds
        for edge in output.taxonomy_edges:
            if edge.confidence < self.min_confidence:
                errors.append(f"Taxonomy edge {edge.parent_id}->{edge.child_id} below confidence threshold")
        
        for edge in output.kg_edges:
            if edge.confidence < self.min_confidence:
                errors.append(f"KG edge {edge.source_id}->{edge.target_id} below confidence threshold")
        
        # Check for contradictions (same source/target with different predicates)
        # TODO: Implement contradiction detection
        
        return errors
    
    async def run_pipeline(
        self,
        document_path: str,
        document_id: str,
        document_metadata: Optional[Dict[str, Any]] = None,
        seed_taxonomy: Optional[Dict[str, Any]] = None,
    ) -> ExtractionPipelineOutput:
        """
        Run the complete extraction pipeline.
        
        Pipeline stages:
        1. Extract document tree (Docling)
        2. Extract concept inventory (NER + LLM)
        3. Build taxonomy (LLM + clustering)
        4. Extract links (OpenIE + LLM)
        5. Validate output
        
        Args:
            document_path: Path to document
            document_id: Unique document ID
            document_metadata: Document metadata
            seed_taxonomy: Optional seed taxonomy
            
        Returns:
            Complete pipeline output
        """
        # Stage 1: Document tree
        document_tree = await self.extract_document_tree(document_path)
        
        # Stage 2: Concept inventory
        concept_registry = await self.extract_concept_inventory(document_tree)
        
        # Stage 3: Taxonomy
        taxonomy_edges = await self.build_taxonomy(concept_registry, seed_taxonomy)
        
        # Stage 4: Links
        kg_edges = await self.extract_links(document_tree, concept_registry)
        
        # Create output
        output = ExtractionPipelineOutput(
            document_id=document_id,
            document_metadata=document_metadata or {},
            document_tree=document_tree,
            concept_registry=concept_registry,
            taxonomy_edges=taxonomy_edges,
            kg_edges=kg_edges,
        )
        
        # Validate
        if self.validate_schema:
            output.validation_errors = self.validate_output(output)
        
        # Calculate confidence summary
        if output.taxonomy_edges:
            output.confidence_summary["taxonomy_avg"] = sum(
                e.confidence for e in output.taxonomy_edges
            ) / len(output.taxonomy_edges)
        
        if output.kg_edges:
            output.confidence_summary["kg_avg"] = sum(
                e.confidence for e in output.kg_edges
            ) / len(output.kg_edges)
        
        return output
