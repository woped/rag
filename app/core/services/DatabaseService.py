from app.core.ports.DatabasePort import DatabasePort
from app.core.dtos.DocumentDTO import DocumentDTO
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Service for managing document persistence and CRUD operations in the WoPeD RAG system.

    This service acts as the business logic layer for all document storage workflows. 
    It adds validation, business rules, and success logging on top of the technical DatabaseAdapter.
    Technical errors and warnings are handled and logged in the adapter layer.

    Responsibilities:
      - Validate documents and enforce business rules before persistence
      - Orchestrate all CRUD operations for documents
      - Log successful business operations
      - Provide a simple, technology-agnostic interface for the application layer
      - Act as the gateway between application logic and database infrastructure
    """
    
    def __init__(self, database_port: DatabasePort):
        self.db = database_port
        logger.info("[DatabaseService] initialized")

    # Add documents
    def add_docs(self, documents: list[DocumentDTO]):
        logger.debug(f"Adding {len(documents)} documents to database")
        valid_docs = [doc for doc in documents if doc.id and doc.text]
        if len(valid_docs) != len(documents):
            logger.warning(f"Filtered out {len(documents) - len(valid_docs)} invalid documents")
        if valid_docs:
            self.db.add_docs(valid_docs)
        logger.info(f"Successfully added {len(valid_docs)} documents to database")

    # Get document by ID
    def get_doc_by_id(self, doc_id: str):
        if not doc_id:
            logger.warning("Empty document ID provided")
            return None
        logger.debug(f"Retrieving document with ID: {doc_id} from database")
        return self.db.get_doc_by_id(doc_id)

    # Update existing document
    def update_doc(self, document: DocumentDTO):
        logger.debug(f"Updating document with ID: {document.id} in database")
        self.db.update_doc(document)
        logger.info(f"Successfully updated Document with ID: {document.id}")

    # Delete document by ID
    def delete_doc(self, doc_id: str):
        logger.debug(f"Deleting document with ID: {doc_id} from database")
        self.db.delete_doc(doc_id)
        logger.info(f"Successfully deleted Document with ID: {doc_id}")
    
    # Delete documents by prefix
    def delete_by_prefix(self, prefix: str):
        if not prefix or not prefix.strip():
            logger.warning("Empty prefix provided for deletion - this would delete all documents")
            raise ValueError("Prefix cannot be empty")
        logger.debug(f"Deleting documents with prefix: {prefix} from database")
        self.db.delete_by_prefix(prefix)
        logger.info(f"Successfully deleted documents with prefix: {prefix}")

    # Clear all documents
    def clear(self):
        logger.warning("Clearing all documents from database")
        self.db.clear()
        logger.info("Successfully cleared all documents from database")
