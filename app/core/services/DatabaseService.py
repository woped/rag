from app.core.ports.DatabasePort import DatabasePort
from app.core.dtos.DocumentDTO import DocumentDTO
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Manages document persistence and CRUD operations for the WoPeD RAG system.
    
    This service provides the domain layer interface for document storage operations, adding
    business validation and error handling on top of the DatabaseAdapter infrastructure.
    Ensures data integrity through validation rules and maintains clean separation between
    business logic and persistence concerns.
    
    Key responsibilities: document validation, CRUD operation orchestration, error handling,
    and business rule enforcement. Acts as a gateway between the application layer and the
    database infrastructure, providing a simplified interface for document management.
    """
    
    def __init__(self, database_port: DatabasePort):
        self.db = database_port
        logger.info("DatabaseService initialized")

    # Add documents with validation
    def add_docs(self, documents: list[DocumentDTO]):
        logger.info(f"Adding {len(documents)} documents")
        
        valid_docs = [doc for doc in documents if doc.id and doc.text]
        
        if len(valid_docs) != len(documents):
            logger.warning(f"Filtered out {len(documents) - len(valid_docs)} invalid documents")
        
        if valid_docs:
            self.db.add_docs(valid_docs)
            logger.info(f"Successfully added {len(valid_docs)} documents")

    # Get document by ID
    def get_doc_by_id(self, doc_id: str):
        if not doc_id:
            logger.warning("Empty document ID provided")
            return None
            
        return self.db.get_doc_by_id(doc_id)

    # Update existing document
    def update_doc(self, document: DocumentDTO):
        if not document.id or not document.text:
            raise ValueError("Document must have ID and text")
            
        self.db.update_doc(document)
        logger.info(f"Updated document: {document.id}")

    # Delete document by ID
    def delete_doc(self, doc_id: str):
        if not doc_id:
            raise ValueError("Document ID required")
            
        self.db.delete_doc(doc_id)
        logger.info(f"Deleted document: {doc_id}")
    
    # Clear all documents
    def clear(self):
        logger.warning("Clearing ALL documents")
        self.db.clear()
