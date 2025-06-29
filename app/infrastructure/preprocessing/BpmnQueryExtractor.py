import logging
import re
import xml.etree.ElementTree as ET
from typing import List
from app.core.ports.QueryExtractorPort import QueryExtractorPort

logger = logging.getLogger(__name__)

class BpmnQueryExtractor(QueryExtractorPort):
    
    def can_process(self, diagram: str) -> bool:
        if not diagram:
            return False
        return ("<?xml" in diagram and 
                ("<bpmn:" in diagram or "<definitions" in diagram))
    
    def get_diagram_type(self) -> str:
        return "BPMN"
    
    def extract_terms(self, diagram: str) -> List[str]:
        logger.debug("[BPMN EXTRACTOR] Extracting text elements from BPMN diagram")
        try:
            # Parse XML with ElementTree
            root = ET.fromstring(diagram)
            
            # Extract all text elements from BPMN
            text_elements = []
            
            # Find all elements with name attributes
            for elem in root.iter():
                name = elem.get('name', '').strip()
                if name:
                    text_elements.append(name)
            
            logger.debug(f"[BPMN EXTRACTOR] Extracted {len(text_elements)} text elements")
            return text_elements
            
        except ET.ParseError as e:
            logger.error(f"[BPMN EXTRACTOR] Invalid XML format: {e}")
            return []
        except Exception as e:
            logger.exception(f"[BPMN EXTRACTOR] Failed to extract semantic terms: {e}")
            raise
    
    # Filter out technical terms that are not relevant for search (e.g., IDs, sequence flows)
    def filter_technical_terms(self, text_matches: List[str]) -> List[str]:
        try:
            semantic_terms = []
            for text in text_matches:
                cleaned_text = text.strip().lower()

                # Check if text is valid BPMN business term (filter only technical IDs)
                if (bool(cleaned_text) and len(cleaned_text) > 1 and
                    not cleaned_text.isdigit() and 
                    not cleaned_text.startswith('<') and
                    not re.match(r'^[a-z]+_[a-z0-9]+$', cleaned_text) and  # Skip task_12j0pib
                    not 'sequenceflow' in cleaned_text):
                    
                    # Clean the text
                    cleaned_text = re.sub(r'[<>-]', ' ', cleaned_text)
                    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
                    semantic_terms.append(cleaned_text)

            return semantic_terms
        except Exception as e:
            logger.exception(f"[BPMN EXTRACTOR] Failed to filter technical terms: {e}")
            raise
    
    # Filter out structural terms that are not relevant for search
    # These are terms that describe the structure of the BPMN diagram rather than its business logic
    def filter_structural_terms(self, keywords: List[str]) -> List[str]:
        try:
            optimized_keywords = []
            
            # BPMN-specific structural terms to exclude
            bpmn_structural_terms = ['start', 'end', 'gateway', 'sequence', 'flow',
                                   'startevent', 'endevent', 'fork', 'merge',
                                   'http', 'www', 'org', 'berlin', 'hu',
                                   'op', 'woped', 'designer', 'version']
            
            for keyword in keywords:
                if not any(term in keyword.lower() for term in bpmn_structural_terms):
                    optimized_keywords.append(keyword)
            
            return optimized_keywords
        except Exception as e:
            logger.exception(f"[BPMN EXTRACTOR] Failed to filter structural terms: {e}")
            raise