from abc import ABC, abstractmethod
from typing import List, Tuple
from app.core.dtos.DocumentDTO import DocumentDTO
from app.core.dtos.RagDTO import State

"""
    Abstract interface for Retrieval-Augmented Generation operations with three core phases:
    retrieve (semantic document search), augment (prompt enhancement with context),
    and generate (response creation - delegated to external P2T service).
"""

class RAGPort(ABC):

    @abstractmethod
    def retrieve(self, query: str) -> List[Tuple[DocumentDTO, float]]:
        pass

    @abstractmethod
    def augment(self, state: State) -> str:
        pass

    @abstractmethod
    def generate(self, prompt: str, context: List[DocumentDTO]) -> str:
        pass