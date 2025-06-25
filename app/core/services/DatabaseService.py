"""
    DatabaseService provides high-level access to vector database operations
    for the application core. It delegates all data-related functionality
    to an implementation of the DatabasePort interface.

    This service acts as the application's main entry point for storing,
    retrieving, updating, deleting, and searching documents.
"""
from app.core.ports.DatabasePort import DatabasePort
from app.core.dtos.DocumentDTO import DocumentDTO
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, database_port: DatabasePort):
        self.db = database_port

    def add_docs(self, documents: list[DocumentDTO]):
        logger.debug(f"Adding {len(documents)} documents")
        try:
            self.db.add_docs(documents)
        except Exception:
            logger.exception("Failed to add documents")
            raise

    def get_doc_by_id(self, id: str):
        logger.debug(f"Retrieving document with ID: {id}")
        try:
            return self.db.get_doc_by_id(id)
        except Exception:
            logger.exception(f"Failed to retrieve document with ID: {id}")
            raise

    def search_docs(self, query: str, k: int):
        logger.debug(f"Searching documents with query: '{query}', top {k}")
        try:
            return self.db.search_docs(query, k)
        except Exception:
            logger.exception(f"Failed to search documents with query: '{query}'")
            raise

    def update_doc(self, document: DocumentDTO):
        logger.debug(f"Updating document with ID: {document.id}")
        try:
            self.db.update_doc(document)
        except Exception:
            logger.exception(f"Failed to update document with ID: {document.id}")
            raise

    def delete_doc(self, id: str):
        logger.debug(f"Deleting document with ID: {id}")
        try:
            self.db.delete_doc(id)
        except Exception:
            logger.exception(f"Failed to delete document with ID: {id}")
            raise

    def clear(self):
        logger.warning("Clearing all documents from database")
        try:
            self.db.clear()
        except Exception:
            logger.exception("Failed to clear the database")
            raise
