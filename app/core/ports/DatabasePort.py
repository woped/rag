from abc import ABC, abstractmethod
from typing import List
from app.core.dtos.DocumentDTO import DocumentDTO

"""
    Abstract interface for document database operations with CRUD and bulk capabilities:
    add_docs (bulk insertion), get_doc_by_id (retrieval), update_doc (modification),
    delete_doc (removal), delete_by_prefix (batch deletion), and clear (full cleanup).
    
    Enables flexible database implementation switching (ChromaDB, FAISS, Pinecone, etc.).
"""

class DatabasePort(ABC):
    
    @abstractmethod
    def add_docs(self, documents: List[DocumentDTO]):
        pass

    @abstractmethod
    def get_doc_by_id(self, id: str):
        pass

    @abstractmethod
    def update_doc(self, document: DocumentDTO):
        pass

    @abstractmethod
    def delete_doc(self, id: str):
        pass

    @abstractmethod
    def delete_by_prefix(self, prefix: str):
        pass

    @abstractmethod
    def clear(self):
        pass