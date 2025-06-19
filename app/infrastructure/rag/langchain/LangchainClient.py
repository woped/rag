from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from chromadb import PersistentClient
from langchain_core.documents import Document
from app.core.dtos.DocumentDTO import DocumentDTO
import logging

logger = logging.getLogger(__name__)

class LangchainClient:
    """
    LangchainClient is a hybrid wrapper that combines LangChain's Chroma VectorStore
    for semantic search with direct access to ChromaDB for CRUD operations.

    - Uses LangChain for similarity search via sentence embeddings
    - Uses ChromaDB native client for add, get, delete, update
    - Stores all data persistently in the given directory

    """
    def __init__(self, persist_directory="chroma"):
        self.persist_directory = persist_directory
        logger.info(f"LangchainClient initialised with Persist-directory: {self.persist_directory}")

        # LangChain-compatible VectorStore using HuggingFace embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        self.vectorstore = Chroma(
            collection_name="rag_collection",
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

        # Native ChromaDB client for direct CRUD access
        self.client = PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(name="rag_collection")


    def add_docs(self, texts, metadatas=None, ids=None):
        logger.debug(f"add_docs called with {len(texts)} document(s).")
        # Add one or more documents directly to ChromaDB using manually computed embeddings
        if metadatas is None:
            metadatas = [{} for _ in texts]
        if ids is None:
            ids = [str(i) for i in range(len(texts))]

        for i, (text, metadata, doc_id) in enumerate(zip(texts, metadatas, ids)):
            try:
                # Compute embeddings from plain texts
                embedding = self.embeddings.embed_documents([text])
                self.collection.add(
                    documents=[text],
                    metadatas=[metadata],
                    ids=[doc_id],
                    embeddings=embedding
                )
                logger.debug(f"Added document ID {doc_id} successfully.")
            except Exception as e:
                logger.error(f"Error while adding document ID {doc_id} at index {i}: {e}", exc_info=True)
                raise

    def get_doc_by_id(self, id):
        logger.debug(f"Attempting to retrieve document with ID: {id}")
        result = self.collection.get(ids=[id])
        if not result["documents"]:
            logger.warning(f"No document found with ID: {id}")
            return None
        logger.info(f"Document with ID: {id} retrieved successfully")
        return {
            "id": result["ids"][0],
            "text": result["documents"][0],
            "metadata": result["metadatas"][0]
        }

    def search_docs(self, query, k, threshold=25):
        logger.debug(f"Searching for top {k} documents with query: '{query}' and threshold: {threshold}")
        results = self.vectorstore.similarity_search_with_score(query, k=k)

        docs = []
        for doc, distance in results:
            logger.debug(f"Distance: {distance}, ID: {getattr(doc, 'id', None)}")
            if distance <= threshold:
                id_ = getattr(doc, 'id', None) or doc.metadata.get('id', None) or "unknown"
                text = getattr(doc, 'page_content', None) or getattr(doc, 'text', None) or doc.metadata.get('text', None) or ""
                metadata = getattr(doc, 'metadata', None) or {}
                docs.append((DocumentDTO(id=id_, text=text, metadata=metadata), distance))

        logger.info(f"Found {len(docs)} documents within threshold {threshold}")
        return docs

    def update_doc(self, id, text, metadata=None):
        #Update a document by deleting and re-adding it with the same ID.
        logger.info(f"Updating document with ID: {id}")
        self.delete_doc(id)
        self.add_docs([text], [metadata or {}], [id])
        logger.info(f"Document with ID: {id} updated successfully")

    def delete_doc(self, id):
        #Delete a document by its ID.
        logger.info(f"Deleting document with ID: {id}")
        self.collection.delete(ids=[id])
        logger.info(f"Document with ID: {id} deleted")

    def clear(self):
        ids = self.collection.get()["ids"]
        if ids:
            logger.warning(f"Clearing all documents, total count: {len(ids)}")
            self.collection.delete(ids=ids)
            logger.warning("All documents cleared")
        else:
            logger.info("Clear called but no documents to delete")

