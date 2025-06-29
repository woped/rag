import logging
import re
import xml.etree.ElementTree as ET
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
    
    def extract_terms(self, diagram: str) -> List[str]:
        logger.debug("[PNML EXTRACTOR] Extracting text elements from PNML diagram")
        try:
            # Parse XML with ElementTree
            root = ET.fromstring(diagram)
            
            # Extract all text elements from PNML (transition and place names)
            text_elements = []
            
            # Find all name elements with text content
            # Handle both namespaced and non-namespaced XML
            for name_elem in root.iter():
                if name_elem.tag.endswith('name') or name_elem.tag == 'name':
                    for text_elem in name_elem.iter():
                        if (text_elem.tag.endswith('text') or text_elem.tag == 'text') and text_elem.text:
                            text_elements.append(text_elem.text.strip())
            
            # Also check for direct name attributes
            for elem in root.iter():
                if elem.get('name'):
                    text_elements.append(elem.get('name').strip())
            
            logger.debug(f"[PNML EXTRACTOR] Extracted {len(text_elements)} text elements: {text_elements}")
            return text_elements
        except ET.ParseError as e:
            logger.error(f"[PNML EXTRACTOR] Invalid XML format: {e}")
            return []
        except Exception as e:
            logger.exception(f"[PNML EXTRACTOR] Failed to extract semantic terms: {e}")
            raise
    
    def filter_technical_terms(self, text_matches: List[str]) -> List[str]:
        try:
            semantic_terms = []
            for text in text_matches:
                cleaned_text = text.strip().lower()

                # Check if text is valid PNML business term (filter only technical IDs)
                if (bool(cleaned_text) and len(cleaned_text) > 1 and
                    not cleaned_text.isdigit() and 
                    not cleaned_text.startswith('<') and
                    not re.match(r'^noid$', cleaned_text, re.IGNORECASE) and  # Skip noID/noid
                    not re.match(r'^\d+$', cleaned_text) and
                    not re.match(r'^[a-z]\d+$', cleaned_text) and  # Skip p1, t3, etc.
                    not re.match(r'^[a-z]\d+_op_\d+$', cleaned_text) and  # Skip t4_op_1 patterns
                    not re.match(r'^x\d+$', cleaned_text) and  # Skip coordinates
                    not re.match(r'^y\d+$', cleaned_text)):
                    
                    # Clean the text
                    cleaned_text = re.sub(r'[<>-]', ' ', cleaned_text)
                    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
                    semantic_terms.append(cleaned_text)

            return semantic_terms
        except Exception as e:
            logger.exception(f"[PNML EXTRACTOR] Failed to filter technical terms: {e}")
            raise
    
    def filter_structural_terms(self, keywords: List[str]) -> List[str]:
        try:
            optimized_keywords = []
            
            # PNML-specific structural terms to exclude
            pnml_structural_terms = ['place', 'transition', 'arc', 'token',
                                   'start', 'end', 'split', 'join', 'and', 'xor',
                                   'http', 'www', 'org', 'berlin', 'hu', 
                                   'op', 'woped', 'designer', 'version']
            
            for keyword in keywords:
                # Exclude PNML structural terms
                if not any(term in keyword.lower() for term in pnml_structural_terms):
                    optimized_keywords.append(keyword)
            
            return optimized_keywords
        except Exception as e:
            logger.exception(f"[PNML EXTRACTOR] Failed to filter structural terms: {e}")
            raise
