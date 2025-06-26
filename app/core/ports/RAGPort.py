from abc import ABC, abstractmethod
from typing import List, Tuple
from app.core.dtos.DocumentDTO import DocumentDTO
from app.core.dtos.RagDTO import State

class RAGPort(ABC):
    """
    Abstract interface defining the contract for Retrieval-Augmented Generation operations.
    
    This port establishes the standard interface for RAG pipeline implementations, ensuring
    consistent behavior across different RAG service implementations. Defines the three core
    RAG phases: retrieve (semantic document search), augment (prompt enhancement with context),
    and generate (response creation - delegated to external P2T service in WoPeD architecture).
    
    Implementations must provide concrete behavior for document retrieval using similarity search
    and prompt augmentation with retrieved context, enabling pluggable RAG strategies.
    """

    @abstractmethod
    def retrieve(self, query: str) -> List[Tuple[DocumentDTO, float]]:
        pass

    @abstractmethod
    def augment(self, state: State) -> str:
        pass

    @abstractmethod
    def generate(self, prompt: str, context: List[DocumentDTO]) -> str:
        pass