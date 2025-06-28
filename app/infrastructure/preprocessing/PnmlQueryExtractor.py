import logging
import re
from typing import List
from ...core.ports.QueryExtractorPort import QueryExtractorPort

logger = logging.getLogger(__name__)

class PnmlQueryExtractor(QueryExtractorPort):
    
    def can_process(self, diagram: str) -> bool:
        if not diagram:
            return False
        return ("<?xml" in diagram and "<pnml" in diagram)
    
    def get_diagram_type(self) -> str:
        return "PNML"
    
    def extract_semantic_terms(self, diagram: str) -> List[str]:
        logger.debug("[PNML EXTRACTOR] Extracting keywords from PNML diagram")
        try:
            # Extract all <text> elements from the PNML XML (usually transition and place names)
            text_matches = re.findall(r'<text[^>]*>([^<]+)</text>', diagram, re.IGNORECASE)
            
            # Clean and filter text elements to obtain relevant search keywords
            search_keywords = self.filter_semantic_terms(text_matches)
            
            logger.debug(f"[PNML EXTRACTOR] Extracted {len(search_keywords)} search keywords")
            return search_keywords
        except Exception as e:
            logger.exception(f"[PNML EXTRACTOR] Failed to extract semantic terms: {e}")
            raise
    
    # Filter and clean the extracted text elements to keep only meaningful process terms
    def filter_semantic_terms(self, text_matches: List[str]) -> List[str]:
        try:
            semantic_terms = []
            for text in text_matches:
                cleaned_text = text.strip().lower()

                if self.is_meaningful_text(cleaned_text):
                    cleaned_text = re.sub(r'[<>-]', ' ', cleaned_text)
                    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

                    if self.is_process_relevant(cleaned_text):
                        semantic_terms.append(cleaned_text)

            return semantic_terms
        except Exception as e:
            logger.exception(f"[PNML EXTRACTOR] Failed to filter semantic terms: {e}")
            raise
    
    # Check if the text is a meaningful candidate for a process keyword
    def is_meaningful_text(self, text: str) -> bool:
        try:
            return (bool(text) and len(text) > 1 and  # Include p1, t3 etc.
                    not text.isdigit() and 
                    not text.startswith('<') and
                    not re.match(r'^noID$', text) and
                    not re.match(r'^\d+$', text) and
                    not text in ['op', 'woped', 'designer', 'version'] and
                    not re.match(r'^[a-z]\d+_op_\d+$', text))  # Skip t4_op_1 patterns
        except Exception as e:
            logger.exception(f"[PNML EXTRACTOR] Failed to check if text is meaningful: {e}")
            raise   
    
    # Further filter to exclude technical, coordinate, or irrelevant terms
    def is_process_relevant(self, text: str) -> bool:
        try:
            return (len(text) > 1 and not text.isdigit() and
                    not text in ['http', 'www', 'org', 'berlin', 'hu'] and  # Skip URLs/domains
                    not re.match(r'^x\d+$', text) and  # Skip coordinates
                    not re.match(r'^y\d+$', text))
        except Exception as e:
            logger.exception(f"[PNML EXTRACTOR] Failed to check if text is process relevant: {e}")
            raise
