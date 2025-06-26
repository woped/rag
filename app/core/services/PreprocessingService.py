import logging
import os
import re

logger = logging.getLogger(__name__)

class PreprocessingService:
    """
    Service for preprocessing PNML/BPMN XML diagrams for better RAG search.
    
    Extracts semantic content from process diagrams by:
    - Parsing XML text elements 
    - Filtering out technical IDs and structural keywords
    - Weighting meaningful terms for improved similarity search
    - Providing fallback for non-processable content
    
    This service focuses solely on diagram preprocessing logic,
    following single responsibility principle for better maintainability and testability.
    """
    
    def __init__(self):
        logger.debug("PreprocessingService initialized")
    
    def preprocess(self, diagram: str) -> str:
        """Main preprocessing entry point"""
        if self.is_xml_process_diagram(diagram):
            logger.debug("[DIAGRAM PREPROCESSING] Detected XML process model")
            return self.process_xml_diagram(diagram)
        
        # For non-XML diagrams, return as-is
        logger.debug("[DIAGRAM PREPROCESSING] Non-XML diagram, using original")
        return diagram
    
    def is_xml_process_diagram(self, diagram: str) -> bool:
        return ("<?xml" in diagram and 
                ("<pnml>" in diagram or "<bpmn:" in diagram or "<definitions" in diagram))
    
    def process_xml_diagram(self, diagram: str) -> str:
        # Extract text elements from XML
        text_matches = re.findall(r'<text>(.*?)</text>', diagram, re.IGNORECASE | re.DOTALL)
        
        # Clean and filter text elements 
        semantic_terms = self.extract_semantic_terms(text_matches)
        
        # Apply weighting and final filtering
        filtered_terms, excluded_structural = self.apply_term_weighting(semantic_terms)
        
        # Generate final query
        processed_query = " ".join(filtered_terms)
        if not processed_query.strip():
            processed_query = "business process workflow"
        
        # Log processing results
        self.log_processing_results(semantic_terms, excluded_structural, processed_query)
        
        return processed_query
    
    def extract_semantic_terms(self, text_matches: list) -> list:
        semantic_terms = []
        
        for text in text_matches:
            text = text.strip().lower()
            
            if self.is_meaningful_text(text):
                # Clean up XML artifacts and normalize
                text = re.sub(r'[<>-]', ' ', text)
                text = re.sub(r'\s+', ' ', text).strip()
                
                if self.is_process_relevant(text):
                    semantic_terms.append(text)
        
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
    
    def apply_term_weighting(self, semantic_terms: list) -> tuple:
        filtered_terms = []
        excluded_structural = []
        
        structural_keywords = ['and', 'xor', 'split', 'join', 'start', 'end', 
                              'gateway', 'transition', 'place', 'fork', 'merge']
        
        for text in semantic_terms:
            # Skip structural BPMN/Petri net keywords completely
            if any(keyword in text for keyword in structural_keywords):
                excluded_structural.append(text)
                continue
            
            # Weight terms: normal words get higher weight than technical IDs
            if re.match(r'^[pt]\d+$', text):
                # Technical IDs: low weight (appear 1x) 
                filtered_terms.append(text)
            else:
                # Normal words: higher weight (appear 3x)
                filtered_terms.extend([text, text, text])
        
        return filtered_terms, excluded_structural
    
    def log_processing_results(self, semantic_terms: list, excluded_structural: list, processed_query: str):
        structural_keywords = ['and', 'xor', 'split', 'join', 'start', 'end', 
                              'gateway', 'transition', 'place', 'fork', 'merge']
        
        normal_words_count = len([t for t in semantic_terms 
                                 if not re.match(r'^[pt]\d+$', t) and 
                                 not any(keyword in t for keyword in structural_keywords)])
        technical_count = len([t for t in semantic_terms if re.match(r'^[pt]\d+$', t)])
        excluded_count = len(excluded_structural)
        
        logger.debug(f"[DIAGRAM PREPROCESSING] Term breakdown - Normal words: {normal_words_count}, "
                    f"Technical IDs: {technical_count}, Excluded structural: {excluded_count}")
        logger.debug(f"[DIAGRAM PREPROCESSING] Excluded structural terms: {excluded_structural}")
        
        query_preview = processed_query[:200] + ('...' if len(processed_query) > 200 else '')
        logger.debug(f"[DIAGRAM PREPROCESSING] Final filtered RAG search prompt: '{query_preview}'")
