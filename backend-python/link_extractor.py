"""
Link Extractor - OpenIE + LLM-Based Relationship Extraction

Extracts knowledge graph edges using two approaches:
1. OpenIE - extract (subject, relation, object) triples (fast, high recall, noisy)
2. LLM-based - prompt LLM to extract entities/relations into target schema

Key requirements:
- Evidence spans (exact quoted text offsets)
- Schema constraints
- Confidence scores
- Contradiction checks
- Duplicate edge resolution
"""

from typing import List, Optional, Dict, Any, Set, Tuple
from structured_extraction_pipeline import (
    DocumentTreeNode,
    ConceptRegistry,
    KnowledgeGraphEdge,
    EvidenceSpan,
)
from llama_index.llms.openai import OpenAI
import os
import re


class LinkExtractor:
    """
    Link extractor using OpenIE and LLM-based extraction.
    
    Implements discipline to prevent LLM hallucination:
    - Require evidence spans
    - Constrain relation types (schema)
    - Run contradiction checks
    - Resolve duplicate edges
    - Keep confidence scores and provenance
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        llm_model: str = "gpt-4o-mini",
        relation_schema: Optional[Dict[str, List[str]]] = None,
    ):
        """
        Initialize link extractor.
        
        Args:
            openai_api_key: OpenAI API key
            llm_model: LLM model for extraction
            relation_schema: Schema of allowed relation types
        """
        openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.llm = OpenAI(model=llm_model, api_key=openai_api_key)
        
        # Default relation schema for regulatory/legal domain
        self.relation_schema = relation_schema or {
            "dependency": ["depends_on", "requires", "triggers"],
            "mitigation": ["mitigates", "controls", "reduces"],
            "supersession": ["supersedes", "replaces", "updates"],
            "definition": ["defines", "specifies", "describes"],
            "mapping": ["maps_to", "corresponds_to", "relates_to"],
            "semantic": ["related_to", "associated_with", "similar_to"],
        }
    
    def extract_openie_triples(
        self,
        text: str,
        concept_registry: List[ConceptRegistry],
    ) -> List[Tuple[str, str, str, int, int]]:
        """
        Extract OpenIE triples from text.
        
        Returns: List of (subject, relation, object, start_char, end_char)
        
        Args:
            text: Text to extract from
            concept_registry: Concept registry for filtering
            
        Returns:
            List of triples with character positions
        """
        # TODO: Integrate actual OpenIE system
        # Options:
        # - Stanford OpenIE
        # - AllenNLP OpenIE
        # - Custom pattern-based extraction
        
        # Placeholder: Simple pattern-based extraction
        triples = []
        
        # Extract simple patterns like "X depends on Y"
        patterns = [
            (r"(\w+)\s+depends\s+on\s+(\w+)", "depends_on"),
            (r"(\w+)\s+mitigates\s+(\w+)", "mitigates"),
            (r"(\w+)\s+defines\s+(\w+)", "defines"),
        ]
        
        for pattern, relation in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                subject = match.group(1)
                obj = match.group(2)
                start_char = match.start()
                end_char = match.end()
                
                # Check if subject/object are in concept registry
                concept_ids = {c.canonical_id: c for c in concept_registry}
                concept_terms = {c.canonical_term.lower(): c.canonical_id for c in concept_registry}
                
                # Map to concept IDs if possible
                subject_id = concept_terms.get(subject.lower(), subject)
                obj_id = concept_terms.get(obj.lower(), obj)
                
                triples.append((subject_id, relation, obj_id, start_char, end_char))
        
        return triples
    
    async def extract_llm_relations(
        self,
        document_nodes: List[DocumentTreeNode],
        concept_registry: List[ConceptRegistry],
    ) -> List[KnowledgeGraphEdge]:
        """
        Extract relations using LLM with schema constraints.
        
        Args:
            document_nodes: Document tree nodes
            concept_registry: Concept registry
            
        Returns:
            List of KG edges with evidence
        """
        kg_edges = []
        
        # Build concept lookup
        concept_lookup = {c.canonical_id: c for c in concept_registry}
        concept_terms = {c.canonical_term: c.canonical_id for c in concept_registry}
        
        # Process nodes in batches
        batch_size = 5
        for i in range(0, len(document_nodes), batch_size):
            batch = document_nodes[i:i + batch_size]
            
            # Build prompt with schema constraints
            prompt = self._build_relation_extraction_prompt(batch, concept_registry)
            
            # Call LLM
            response = await self.llm.acomplete(prompt)
            
            # Parse response
            edges = self._parse_relation_response(
                response.text,
                batch,
                concept_lookup,
            )
            kg_edges.extend(edges)
        
        # Post-process: contradiction checks, duplicate resolution
        kg_edges = self._resolve_contradictions(kg_edges)
        kg_edges = self._resolve_duplicates(kg_edges)
        
        return kg_edges
    
    def _build_relation_extraction_prompt(
        self,
        document_nodes: List[DocumentTreeNode],
        concept_registry: List[ConceptRegistry],
    ) -> str:
        """Build prompt for LLM relation extraction."""
        # Build text context
        texts = []
        for node in document_nodes:
            texts.append(f"[Page {node.page_number}, chars {node.start_char}-{node.end_char}]\n{node.text}")
        
        # Build concept list
        concept_list = "\n".join([
            f"- {c.canonical_term} ({c.canonical_id})" for c in concept_registry[:50]
        ])
        
        # Build relation schema
        schema_text = []
        for category, relations in self.relation_schema.items():
            schema_text.append(f"{category}: {', '.join(relations)}")
        
        prompt = f"""Extract relationships between concepts from this text.

Text:
{chr(10).join(texts)}

Concepts to consider:
{concept_list}

Allowed relation types (by category):
{chr(10).join(schema_text)}

Requirements:
1. Extract only relationships explicitly stated in the text
2. For each relationship, provide exact quoted evidence text
3. Include character offsets (start_char, end_char) for evidence
4. Assign confidence score (0.0-1.0)
5. Use concept IDs, not terms

Output JSON array with:
- source_id (concept ID)
- target_id (concept ID)
- predicate (relation type)
- relationship_type (category)
- evidence_text (exact quote)
- evidence_start_char
- evidence_end_char
- evidence_page_number
- confidence

Do not invent relationships. Only extract what is explicitly stated.
"""
        return prompt
    
    def _parse_relation_response(
        self,
        response_text: str,
        document_nodes: List[DocumentTreeNode],
        concept_lookup: Dict[str, ConceptRegistry],
    ) -> List[KnowledgeGraphEdge]:
        """Parse LLM response into KnowledgeGraphEdge objects."""
        edges = []
        
        # TODO: Parse JSON response
        # Extract edges with evidence spans
        
        return edges
    
    def _resolve_contradictions(
        self,
        edges: List[KnowledgeGraphEdge],
    ) -> List[KnowledgeGraphEdge]:
        """
        Resolve contradictory edges.
        
        Contradictions: Same source/target with incompatible predicates.
        
        Args:
            edges: List of edges
            
        Returns:
            Filtered list without contradictions
        """
        # Group edges by source/target pair
        edge_groups = {}
        for edge in edges:
            key = (edge.source_id, edge.target_id)
            if key not in edge_groups:
                edge_groups[key] = []
            edge_groups[key].append(edge)
        
        resolved_edges = []
        
        # For each pair, keep highest confidence edge
        for (source_id, target_id), group_edges in edge_groups.items():
            # Check for contradictions
            predicates = [e.predicate for e in group_edges]
            
            # If multiple different predicates, keep highest confidence
            if len(set(predicates)) > 1:
                # Contradiction detected - keep highest confidence
                best_edge = max(group_edges, key=lambda e: e.confidence)
                resolved_edges.append(best_edge)
            else:
                # No contradiction - keep all
                resolved_edges.extend(group_edges)
        
        return resolved_edges
    
    def _resolve_duplicates(
        self,
        edges: List[KnowledgeGraphEdge],
    ) -> List[KnowledgeGraphEdge]:
        """
        Resolve duplicate edges (same source/target/predicate).
        
        Args:
            edges: List of edges
            
        Returns:
            Deduplicated list (keep highest confidence)
        """
        seen = {}
        
        for edge in edges:
            key = (edge.source_id, edge.target_id, edge.predicate)
            
            if key not in seen:
                seen[key] = edge
            else:
                # Duplicate - keep highest confidence
                if edge.confidence > seen[key].confidence:
                    seen[key] = edge
        
        return list(seen.values())
    
    async def extract_links(
        self,
        document_tree: List[DocumentTreeNode],
        concept_registry: List[ConceptRegistry],
        use_openie: bool = True,
        use_llm: bool = True,
    ) -> List[KnowledgeGraphEdge]:
        """
        Extract knowledge graph links.
        
        Args:
            document_tree: Document tree nodes
            concept_registry: Concept registry
            use_openie: Use OpenIE extraction
            use_llm: Use LLM-based extraction
            
        Returns:
            List of KG edges with evidence spans
        """
        all_edges = []
        
        # OpenIE extraction (fast, noisy)
        if use_openie:
            for node in document_tree:
                triples = self.extract_openie_triples(node.text, concept_registry)
                
                for subject_id, predicate, obj_id, start_char, end_char in triples:
                    # Create evidence span
                    evidence = EvidenceSpan(
                        text=node.text[start_char:end_char],
                        start_char=start_char + node.start_char,
                        end_char=end_char + node.start_char,
                        page_number=node.page_number,
                        section_id=node.id,
                        confidence=0.6,  # Lower confidence for OpenIE
                    )
                    
                    edge = KnowledgeGraphEdge(
                        source_id=subject_id,
                        target_id=obj_id,
                        predicate=predicate,
                        relationship_type="semantic",
                        evidence_spans=[evidence],
                        confidence=0.6,
                        extracted_by="openie",
                    )
                    all_edges.append(edge)
        
        # LLM-based extraction (slower, more accurate)
        if use_llm:
            llm_edges = await self.extract_llm_relations(document_tree, concept_registry)
            all_edges.extend(llm_edges)
        
        # Post-process
        all_edges = self._resolve_contradictions(all_edges)
        all_edges = self._resolve_duplicates(all_edges)
        
        return all_edges
