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
    """

    def __init__(self, extractors: List[QueryExtractorPort]):
        self.extractors = extractors
        logger.info(f"[QueryExtractionService] initialized")
    
    # Entry point for optimizing rag similiarity search query from a diagram
    def extract_query(self, diagram: str) -> str:
        extractor = self.find_extractor(diagram)
        if extractor:
            logger.debug(f"[QUERY EXTRACTION] Detected {extractor.get_diagram_type()} diagram")
            
            # Extract raw text elements from diagram
            text_elements = extractor.extract_terms(diagram)
            
            # Filter and clean the text elements from technical terms (ids etc.)
            filtered_keywords = extractor.filter_technical_terms(text_elements)
            
            # Apply structural term filtering (filter out terms that are not relevant for search)
            optimized_keywords = extractor.filter_structural_terms(filtered_keywords)
            search_query = " ".join(optimized_keywords)
            
            # Log results
            self.log_extraction_results(extractor.get_diagram_type(), filtered_keywords, optimized_keywords)
            
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
    
    # Log the results of the query extraction process
    def log_extraction_results(self, diagram_type: str, filtered_keywords: List[str], optimized_keywords: List[str]) -> None:
        excluded_count = len(filtered_keywords) - len(optimized_keywords)
        
        logger.debug(f"[QUERY EXTRACTION] {diagram_type} breakdown - "
                    f"Filtered terms: {len(filtered_keywords)}, Final terms: {len(optimized_keywords)}, "
                    f"Excluded structural: {excluded_count}")
        logger.debug(f"[QUERY EXTRACTION] Final keywords: {optimized_keywords}")
