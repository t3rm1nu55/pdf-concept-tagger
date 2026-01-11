"""
Taxonomy Builder - LLM-Assisted Taxonomy Construction

Implements the "LLM + evidence + iterative refinement" approach:
1. Extract candidate terms (entities/keyphrases)
2. Cluster by embedding similarity
3. Have LLM propose parent/child relations under constraints
4. Validate each edge with evidence (quotes/spans) and scoring

This is "partially solved" - works well with seed taxonomy,
or can build from scratch with iteration.
"""

from typing import List, Optional, Dict, Any, Tuple
from structured_extraction_pipeline import (
    ConceptRegistry,
    TaxonomyEdge,
    EvidenceSpan,
)
from llama_index.core import Document
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
import numpy as np
from sklearn.cluster import DBSCAN
import os


class TaxonomyBuilder:
    """
    Taxonomy builder using LLM + clustering + evidence validation.
    
    Approach:
    - If seed taxonomy exists: Use TaxoExpan-style expansion
    - If no seed: Build from scratch using LLM + clustering
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        embedding_model: str = "text-embedding-3-small",
        llm_model: str = "gpt-4o-mini",
    ):
        """
        Initialize taxonomy builder.
        
        Args:
            openai_api_key: OpenAI API key
            embedding_model: Embedding model name
            llm_model: LLM model for taxonomy construction
        """
        openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        self.embed_model = OpenAIEmbedding(
            model=embedding_model,
            api_key=openai_api_key,
        )
        self.llm = OpenAI(model=llm_model, api_key=openai_api_key)
    
    async def cluster_concepts(
        self,
        concepts: List[ConceptRegistry],
        eps: float = 0.3,
        min_samples: int = 2,
    ) -> Dict[int, List[str]]:
        """
        Cluster concepts by embedding similarity.
        
        Args:
            concepts: Concept registry
            eps: DBSCAN eps parameter
            min_samples: DBSCAN min_samples parameter
            
        Returns:
            Dictionary mapping cluster ID to concept IDs
        """
        if not concepts:
            return {}
        
        # Generate embeddings
        texts = [c.canonical_term for c in concepts]
        embeddings = await self.embed_model.aget_text_embedding_batch(texts)
        
        # Cluster using DBSCAN
        embeddings_array = np.array(embeddings)
        clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
        cluster_labels = clustering.fit_predict(embeddings_array)
        
        # Group by cluster
        clusters = {}
        for idx, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(concepts[idx].canonical_id)
        
        return clusters
    
    async def propose_taxonomy_relations(
        self,
        concept_pairs: List[Tuple[str, str]],
        concept_registry: List[ConceptRegistry],
        relationship_types: List[str] = None,
    ) -> List[TaxonomyEdge]:
        """
        Use LLM to propose taxonomy relations with constraints.
        
        Args:
            concept_pairs: Pairs of concept IDs to evaluate
            concept_registry: Concept registry for context
            relationship_types: Allowed relationship types
            
        Returns:
            List of proposed taxonomy edges with evidence
        """
        if relationship_types is None:
            relationship_types = ["is_a", "part_of", "applies_to", "instance_of"]
        
        taxonomy_edges = []
        
        # Build concept lookup
        concept_lookup = {c.canonical_id: c for c in concept_registry}
        
        # Process pairs in batches
        batch_size = 10
        for i in range(0, len(concept_pairs), batch_size):
            batch = concept_pairs[i:i + batch_size]
            
            # Build prompt for LLM
            prompt = self._build_taxonomy_prompt(batch, concept_lookup, relationship_types)
            
            # Call LLM
            response = await self.llm.acomplete(prompt)
            
            # Parse response and extract edges
            edges = self._parse_taxonomy_response(response.text, concept_lookup)
            taxonomy_edges.extend(edges)
        
        return taxonomy_edges
    
    def _build_taxonomy_prompt(
        self,
        concept_pairs: List[Tuple[str, str]],
        concept_lookup: Dict[str, ConceptRegistry],
        relationship_types: List[str],
    ) -> str:
        """Build prompt for LLM taxonomy proposal."""
        pairs_text = []
        for parent_id, child_id in concept_pairs:
            parent = concept_lookup.get(parent_id)
            child = concept_lookup.get(child_id)
            if parent and child:
                pairs_text.append(
                    f"- Parent: {parent.canonical_term} ({parent_id})\n"
                    f"  Child: {child.canonical_term} ({child_id})"
                )
        
        prompt = f"""Analyze these concept pairs and propose taxonomy relationships.

Concept Pairs:
{chr(10).join(pairs_text)}

Allowed relationship types: {', '.join(relationship_types)}

For each pair:
1. Determine if a taxonomy relationship exists
2. Identify the relationship type
3. Find evidence spans (exact quoted text) supporting the relationship
4. Assign confidence score (0.0-1.0)

Output JSON array with:
- parent_id
- child_id
- relationship_type
- evidence_text (exact quote)
- evidence_start_char
- evidence_end_char
- evidence_page_number
- confidence

Only propose relationships with strong evidence. If uncertain, skip the pair.
"""
        return prompt
    
    def _parse_taxonomy_response(
        self,
        response_text: str,
        concept_lookup: Dict[str, ConceptRegistry],
    ) -> List[TaxonomyEdge]:
        """Parse LLM response into TaxonomyEdge objects."""
        edges = []
        
        # TODO: Parse JSON response
        # Extract edges with evidence spans
        
        return edges
    
    async def expand_seed_taxonomy(
        self,
        seed_taxonomy: Dict[str, Any],
        new_concepts: List[ConceptRegistry],
    ) -> List[TaxonomyEdge]:
        """
        Expand existing taxonomy with new concepts (TaxoExpan-style).
        
        Args:
            seed_taxonomy: Existing taxonomy structure
            new_concepts: New concepts to add
            
        Returns:
            List of new taxonomy edges
        """
        # TODO: Implement TaxoExpan-style expansion
        # This would:
        # 1. Find similar concepts in seed taxonomy
        # 2. Propose parent/child relations
        # 3. Validate with evidence
        
        return []
    
    async def build_taxonomy(
        self,
        concept_registry: List[ConceptRegistry],
        seed_taxonomy: Optional[Dict[str, Any]] = None,
        require_evidence: bool = True,
    ) -> List[TaxonomyEdge]:
        """
        Build taxonomy from concepts.
        
        Args:
            concept_registry: Concept inventory
            seed_taxonomy: Optional seed taxonomy
            require_evidence: Require evidence spans
            
        Returns:
            List of taxonomy edges with evidence
        """
        if seed_taxonomy:
            # Expand existing taxonomy
            return await self.expand_seed_taxonomy(seed_taxonomy, concept_registry)
        else:
            # Build from scratch
            # 1. Cluster concepts
            clusters = await self.cluster_concepts(concept_registry)
            
            # 2. Generate candidate pairs within clusters
            concept_pairs = []
            for cluster_concept_ids in clusters.values():
                if len(cluster_concept_ids) > 1:
                    # Generate pairs within cluster
                    for i in range(len(cluster_concept_ids)):
                        for j in range(i + 1, len(cluster_concept_ids)):
                            concept_pairs.append((cluster_concept_ids[i], cluster_concept_ids[j]))
            
            # 3. Propose relations
            taxonomy_edges = await self.propose_taxonomy_relations(
                concept_pairs,
                concept_registry,
            )
            
            # 4. Filter by evidence requirement
            if require_evidence:
                taxonomy_edges = [
                    e for e in taxonomy_edges if e.evidence_spans
                ]
            
            return taxonomy_edges
