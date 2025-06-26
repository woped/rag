from app.infrastructure.rag.langchain.LangchainClient import LangchainClient
from app.core.ports.DatabasePort import DatabasePort
import logging

logger = logging.getLogger(__name__)

class DatabaseAdapter(DatabasePort):
    """
    Infrastructure adapter for document persistence using ChromaDB via LangchainClient.
    
    This adapter implements the technical database operations, providing a concrete implementation
    of the DatabasePort interface. Handles all CRUD operations by delegating to the LangchainClient
    which manages the actual ChromaDB vector database interactions and document storage.
    
    Key operations: document storage and retrieval, metadata management, bulk operations,
    and database cleanup. Serves as the persistence layer bridge between domain services
    and the ChromaDB vector database infrastructure.
    """
    
    def __init__(self):
        self.client = LangchainClient()
        logger.info("DatabaseAdapter initialized with LangchainClient")

    # Add multiple documents to database
    def add_docs(self, documents):
        logger.info(f"Adding {len(documents)} documents")
        try:
            texts = [doc.text for doc in documents]
            metadatas = [doc.metadata or {} for doc in documents]
            ids = [doc.id or None for doc in documents]
            self.client.add_docs(texts, metadatas, ids)
        except Exception as e:
            logger.exception("Failed to add documents")
            raise

    # Get single document by ID
    def get_doc_by_id(self, id):
        logger.debug(f"Retrieving document with ID: {id}")
        try:
            return self.client.get_doc_by_id(id)
        except Exception as e:
            logger.exception(f"Failed to retrieve document with ID: {id}")
            raise
    
    # Update existing document
    def update_doc(self, document):
        logger.info(f"Updating document with ID: {document.id}")
        try:
            self.client.update_doc(document.id, document.text, document.metadata)
        except Exception as e:
            logger.exception(f"Failed to update document with ID: {document.id}")
            raise
    
    # Delete document by ID
    def delete_doc(self, id):
        logger.warning(f"Deleting document with ID: {id}")
        try:
            self.client.delete_doc(id)
        except Exception as e:
            logger.exception(f"Failed to delete document with ID: {id}")
            raise
    
    # Clear all documents from database
    def clear(self):
        logger.critical("Clearing all documents from the database!")
        try:
            self.client.clear()
        except Exception as e:
            logger.exception("Failed to clear the database")
            raise
