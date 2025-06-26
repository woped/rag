from abc import ABC, abstractmethod
from typing import List
from app.core.dtos.DocumentDTO import DocumentDTO

"""
    DatabasePort defines the abstract interface for data access operations
    used by the application core.

    It decouples the core logic from any specific database implementation,
    allowing for flexibility and easy substitution (e.g. ChromaDB, FAISS, etc.).
"""

class DatabasePort(ABC):
    @abstractmethod
    def add_docs(self, documents: List[DocumentDTO]):
        pass

    @abstractmethod
    def delete_doc(self, id: str):
        pass

    @abstractmethod
    def get_doc_by_id(self, id: str):
        pass

    @abstractmethod
    def update_doc(self, document: DocumentDTO):
        pass

    @abstractmethod
    def search_docs(self, query: str, k: int):
        pass
