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
        texts = [doc.text for doc in documents]
        metadatas = [doc.metadata or {} for doc in documents]
        ids = [doc.id or None for doc in documents]
        self.client.add_docs(texts, metadatas, ids)

    def get_doc_by_id(self, id):
        logger.debug(f"Retrieving document with ID: {id}")
        return self.client.get_doc_by_id(id)

    def search_docs(self, query, k):
        logger.info(f"Delegating search to LangchainClient: k={k}")
        return self.client.search_docs(query, k)
    
    def update_doc(self, document):
        logger.info(f"Updating document with ID: {document.id}")
        self.client.update_doc(document.id, document.text, document.metadata)
    
    def delete_doc(self, id):
        logger.warning(f"Deleting document with ID: {id}")
        self.client.delete_doc(id)
    
    def clear(self):
        logger.critical("Clearing all documents from the database!")
        self.client.clear()
