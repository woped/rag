import logging
import re
from typing import List

from ...core.ports.QueryExtractorPort import QueryExtractorPort

logger = logging.getLogger(__name__)


class PnmlQueryExtractor(QueryExtractorPort):
    
    def can_process(self, diagram: str) -> bool:
        return ("<?xml" in diagram and "<pnml>" in diagram)
    
    def get_diagram_type(self) -> str:
        return "PNML"
    
    def extract_semantic_terms(self, diagram: str) -> List[str]:
        logger.debug("[PNML EXTRACTOR] Extracting keywords from PNML diagram")
        
        # Extract text elements from XML - mainly transition and place names
        text_matches = re.findall(r'<text[^>]*>([^<]+)</text>', diagram, re.IGNORECASE)
        
        # Clean and filter text elements for search keywords
        search_keywords = self.filter_semantic_terms(text_matches)
        
        logger.debug(f"[PNML EXTRACTOR] Extracted {len(search_keywords)} search keywords")
        
        return search_keywords
    
    def filter_semantic_terms(self, text_matches: List[str]) -> List[str]:
        semantic_terms = []
        
        for text in text_matches:
            # Clean the text content only, not the XML tags
            cleaned_text = text.strip().lower()
            
            if self.is_meaningful_text(cleaned_text):
                # Clean up XML artifacts and normalize
                cleaned_text = re.sub(r'[<>-]', ' ', cleaned_text)
                cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
                
                if self.is_process_relevant(cleaned_text):
                    semantic_terms.append(cleaned_text)
        
        return semantic_terms
    
    def is_meaningful_text(self, text: str) -> bool:
        return (text and len(text) > 1 and  # Include p1, t3 etc.
                not text.isdigit() and 
                not text.startswith('<') and
                not re.match(r'^noID$', text) and
                not re.match(r'^\d+$', text) and
                not text in ['op', 'woped', 'designer', 'version'] and
                not re.match(r'^[a-z]\d+_op_\d+$', text))  # Skip t4_op_1 patterns
    
    def is_process_relevant(self, text: str) -> bool:
        return (len(text) > 1 and not text.isdigit() and
                not text in ['http', 'www', 'org', 'berlin', 'hu'] and  # Skip URLs/domains
                not re.match(r'^x\d+$', text) and  # Skip coordinates
                not re.match(r'^y\d+$', text))
    
    def is_valid_name(self, name: str) -> bool:
        return (name and len(name) > 1 and not name.isdigit())
