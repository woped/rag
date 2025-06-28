import logging
import re
from typing import List, Tuple
from app.core.ports.QueryExtractorPort import QueryExtractorPort

logger = logging.getLogger(__name__)


class QueryExtractionService:
    """
    Service for extracting and optimizing search queries from process diagrams (BPMN, PNML)
    to improve RAG similarity search in a hexagonal architecture.

    This service uses extractor adapters (e.g., BpmnQueryExtractor, PnmlQueryExtractor) that implement
    the QueryExtractorPort interface. It selects the appropriate adapter based on the diagram format,
    extracts relevant keywords, and optimizes them for retrieval. This avoids using the entire diagram,
    which would distort search results.

    Responsibilities:
      - Detect diagram type and delegate extraction to the correct adapter (port)
      - Extract and optimize semantic keywords for similarity search
      - Log extraction details for traceability
    """

    def __init__(self, extractors: List[QueryExtractorPort]):
        self.extractors = extractors
        logger.info(f"[QueryExtractionService] initialized")
    
    # Entry point for optimizing rag similiarity search query from a diagram
    def extract_query(self, diagram: str) -> str:
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
            logger.error("[QUERY EXTRACTION] Non-XML diagram, using original")
            return diagram
    
    # Find the extractor that can process the given diagram
    def find_extractor(self, diagram: str) -> QueryExtractorPort:
        for extractor in self.extractors:
            if extractor.can_process(diagram):
                return extractor
        return None
    
    # Optimize extracted keywords by filtering structural terms
    def optimize_keywords(self, keywords: List[str]) -> Tuple[List[str], List[str]]:
        optimized_keywords = []
        excluded_terms = []
        
        # Terms to exclude from search queries
        structural_terms = ['and', 'xor', 'split', 'join', 'start', 'end', 
                        'gateway', 'transition', 'place', 'fork', 'merge']
        for keyword in keywords:
            # Exclude structural terms from the rag similarity search query
            if keyword in structural_terms:
                excluded_terms.append(keyword)
                continue
            # Kein Gewichtungsmechanismus mehr, einfach übernehmen
            optimized_keywords.append(keyword)
        
        return optimized_keywords, excluded_terms
    
    # Log the results of the query extraction process
    # Includes counts of business terms, technical IDs, and excluded structural terms
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
