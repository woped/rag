import logging
import re
from typing import List, Tuple

from ..ports.QueryExtractorPort import QueryExtractorPort

logger = logging.getLogger(__name__)


class QueryExtractionService:
    """
    Service for extracting search keywords from PNML/BPMN XML diagrams for RAG queries.
    
    Uses pluggable extractors for different diagram types following hexagonal architecture.
    Orchestrates keyword extraction and query optimization using dependency injection.
    """
    
    def __init__(self, extractors: List[QueryExtractorPort]):
        self.extractors = extractors
        logger.debug(f"QueryExtractionService initialized with {len(extractors)} extractors")
    
    def extract_query(self, diagram: str) -> str:
        # Find appropriate extractor
        extractor = self.find_extractor(diagram)
        
        if extractor:
            logger.debug(f"[QUERY EXTRACTION] Detected {extractor.get_diagram_type()} diagram")
            search_keywords = extractor.extract_semantic_terms(diagram)
            
            # Apply keyword weighting and optimization
            optimized_keywords, excluded_terms = self.optimize_keywords(search_keywords)
            search_query = " ".join(optimized_keywords)
            
            # Log results
            self.log_extraction_results(extractor.get_diagram_type(), search_keywords, excluded_terms)
            
            query_preview = search_query[:200] + ('...' if len(search_query) > 200 else '')
            logger.debug(f"[QUERY EXTRACTION] Final {extractor.get_diagram_type()} query: '{query_preview}'")
            
            return search_query
        else:
            # For non-XML diagrams, return as-is
            logger.debug("[QUERY EXTRACTION] Non-XML diagram, using original")
            return diagram
    
    def find_extractor(self, diagram: str) -> QueryExtractorPort:
        for extractor in self.extractors:
            if extractor.can_process(diagram):
                return extractor
        return None
    
    def optimize_keywords(self, keywords: List[str]) -> Tuple[List[str], List[str]]:
        optimized_keywords = []
        excluded_terms = []
        
        # Terms to exclude from search queries
        structural_terms = ['and', 'xor', 'split', 'join', 'start', 'end', 
                           'gateway', 'transition', 'place', 'fork', 'merge']
        
        for keyword in keywords:
            # Skip structural terms that don't help with search
            if keyword in structural_terms:
                excluded_terms.append(keyword)
                continue
            
            # Weight keywords based on search relevance
            if re.match(r'^[pt]\d+$', keyword):
                # Technical IDs: low weight (appear 1x) 
                optimized_keywords.append(keyword)
            else:
                # Business terms: high weight (appear 3x for better search ranking)
                optimized_keywords.extend([keyword, keyword, keyword])
        
        return optimized_keywords, excluded_terms
    
    def log_extraction_results(self, diagram_type: str, keywords: List[str], excluded_terms: List[str]) -> None:
        structural_terms = ['and', 'xor', 'split', 'join', 'start', 'end', 
                           'gateway', 'transition', 'place', 'fork', 'merge']
        
        business_terms_count = len([k for k in keywords 
                                   if not re.match(r'^[pt]\d+$', k) and 
                                   not any(term in k for term in structural_terms)])
        technical_count = len([k for k in keywords if re.match(r'^[pt]\d+$', k)])
        excluded_count = len(excluded_terms)
        
        logger.debug(f"[QUERY EXTRACTION] {diagram_type} breakdown - "
                    f"Business terms: {business_terms_count}, Technical IDs: {technical_count}, "
                    f"Excluded structural: {excluded_count}")
        logger.debug(f"[QUERY EXTRACTION] Excluded terms: {excluded_terms}")
