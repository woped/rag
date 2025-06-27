from app.core.ports.DatabasePort import DatabasePort
from app.core.dtos.DocumentDTO import DocumentDTO
import logging

logger = logging.getLogger(__name__)

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
        
        try:
            valid_docs = [doc for doc in documents if doc.id and doc.text]
       
            if len(valid_docs) != len(documents):
                logger.warning(f"Filtered out {len(documents) - len(valid_docs)} invalid documents")

            if valid_docs:
                self.db.add_docs(valid_docs)
                logger.info(f"Successfully added {len(valid_docs)} documents")
        except Exception:
            logger.exception("Failed to add documents")
            raise

    # Get document by ID
    def get_doc_by_id(self, doc_id: str):
        if not doc_id:
            logger.warning("Empty document ID provided")
            return None
            
        logger.debug(f"Retrieving document with ID: {id}")
        try:
            return self.db.get_doc_by_id(doc_id)
        except Exception:
            logger.exception(f"Failed to retrieve document with ID: {id}")
            raise

    # Update existing document
    def update_doc(self, document: DocumentDTO):
        logger.debug(f"Updating document with ID: {document.id}")
        try:
            self.db.update_doc(document)
        except Exception:
            logger.exception(f"Failed to update document with ID: {document.id}")
            raise

    # Delete document by ID
    def delete_doc(self, doc_id: str):
        logger.debug(f"Deleting document with ID: {id}")
        try:
            self.db.delete_doc(id)
        except Exception:
            logger.exception(f"Failed to delete document with ID: {id}")
            raise
    
    # Delete documents by prefix
    def delete_by_prefix(self, prefix: str):
        if not prefix or not prefix.strip():
            logger.warning("Empty prefix provided for deletion - this would delete all documents")
            raise ValueError("Prefix cannot be empty")
            
        logger.info(f"Deleting documents with prefix: {prefix}")
        try:
            self.db.delete_by_prefix(prefix)
            logger.info(f"Successfully deleted documents with prefix: {prefix}")
        except Exception:
            logger.exception(f"Failed to delete documents with prefix: {prefix}")
            raise

    # Clear all documents
    def clear(self):
        logger.warning("Clearing all documents from database")
        try:
            self.db.clear()
        except Exception:
            logger.exception("Failed to clear the database")
            raise
