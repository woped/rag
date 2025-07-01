from abc import ABC, abstractmethod
from typing import List

"""
    Abstract interface for extracting semantic terms from BPMN/PNML diagram formats:
    can_process (format detection), extract_semantic_terms (term extraction),
    and get_diagram_type (type identification).
"""

class QueryExtractorPort(ABC):
    
    @abstractmethod
    def can_process(self, diagram: str) -> bool:
        pass
    
    @abstractmethod
    def get_diagram_type(self) -> str:
        pass

    @abstractmethod
    def extract_terms(self, diagram: str) -> List[str]:
        pass
    @abstractmethod
    def filter_technical_terms(self, text_matches: List[str]) -> List[str]:
        pass

    @abstractmethod
    def filter_structural_terms(self, keywords: List[str]) -> List[str]:
        pass

