from abc import ABC, abstractmethod
from typing import List


class QueryExtractorPort(ABC):
    
    @abstractmethod
    def can_process(self, diagram: str) -> bool:
        pass
    
    @abstractmethod
    def extract_semantic_terms(self, diagram: str) -> List[str]:
        pass
    
    @abstractmethod
    def get_diagram_type(self) -> str:
        pass
