from abc import ABC, abstractmethod
from typing import List
from app.core.dtos.DocumentDTO import DocumentDTO

class DatabasePort(ABC):
    """
    Abstract interface defining the contract for document database operations in the RAG system.
    
    This port establishes the standard CRUD interface for document persistence, enabling flexible
    database implementation switching (ChromaDB, FAISS, Pinecone, etc.) without affecting the
    domain layer. Ensures consistent behavior across different vector database implementations.
    
    Key operations: bulk document insertion, individual document retrieval and management,
    and full database cleanup. Supports the complete document lifecycle required for RAG
    operations while maintaining clean separation between domain logic and persistence concerns.
    """
    
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
    def clear(self):
        pass
