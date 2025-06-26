from app.infrastructure.rag.langchain.LangchainClient import LangchainClient
from app.core.ports.DatabasePort import DatabasePort
import logging

logger = logging.getLogger(__name__)

"""
    DatabaseAdapter connects the application core (via the DatabasePort interface)
    to the LangchainClient, which provides access to both semantic search and
    full CRUD operations using ChromaDB.

    It acts as the bridge between your core logic and the infrastructure layer.
"""

class DatabaseAdapter(DatabasePort):
    
    def __init__(self):
        self.client = LangchainClient()
        logger.info("DatabaseAdapter initialized with LangchainClient")

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

    def get_doc_by_id(self, id):
        logger.debug(f"Retrieving document with ID: {id}")
        try:
            return self.client.get_doc_by_id(id)
        except Exception as e:
            logger.exception(f"Failed to retrieve document with ID: {id}")
            raise

    def search_docs(self, query, k):
        logger.debug(f"Searching for top {k} documents matching query: '{query}'")
        try:
            results = self.client.search_docs(query, k)
            logger.debug(f"Search returned {len(results)} results")
            return results
        except Exception as e:
            logger.exception(f"Search failed for query: '{query}'")
            raise
    
    def update_doc(self, document):
        logger.info(f"Updating document with ID: {document.id}")
        try:
            self.client.update_doc(document.id, document.text, document.metadata)
        except Exception as e:
            logger.exception(f"Failed to update document with ID: {document.id}")
            raise
    
    def delete_doc(self, id):
        logger.warning(f"Deleting document with ID: {id}")
        try:
            self.client.delete_doc(id)
        except Exception as e:
            logger.exception(f"Failed to delete document with ID: {id}")
            raise
    
    def clear(self):
        logger.critical("Clearing all documents from the database!")
        try:
            self.client.clear()
        except Exception as e:
            logger.exception("Failed to clear the database")
            raise
