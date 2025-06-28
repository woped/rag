from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from chromadb import PersistentClient
from langchain_core.documents import Document
from app.core.dtos.DocumentDTO import DocumentDTO
import logging
import os

logger = logging.getLogger(__name__)

class LangchainClient:
    """
    Low-level client integrating LangChain VectorStore with native ChromaDB operations.
    
    This client provides a hybrid approach to vector database operations, combining LangChain's
    high-level semantic search capabilities with ChromaDB's native CRUD operations. Uses
    HuggingFace's multilingual embedding model for robust text representation and similarity
    matching across different languages.
    """

    def __init__(self, persist_directory="chroma"):
        try:
            self.persist_directory = persist_directory
            logger.info(f"[LangchainClient] initialised with Persist-directory: {self.persist_directory}")

            self.threshold = int(os.environ.get("THRESHOLD"))
            self.results_count = int(os.environ.get("RESULTS_COUNT"))
            embedding_model = os.environ.get("EMBEDDING_MODEL")

            # LangChain VectorStore for semantic search
            self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
            self.vectorstore = Chroma(
                collection_name="rag_collection",
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )

            # Native ChromaDB client for CRUD operations
            self.client = PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(name="rag_collection")
            
        except Exception as e:
            logger.exception(f"Failed to initialize LangchainClient: {e}")
            raise

    # Add multiple documents with embeddings
    def add_docs(self, texts, metadatas=None, ids=None):
        logger.debug(f"Attempting to add {len(texts)} document(s).")
        if metadatas is None:
            metadatas = [{} for _ in texts]
        if ids is None:
            ids = [str(i) for i in range(len(texts))]

        for i, (text, metadata, doc_id) in enumerate(zip(texts, metadatas, ids)):
            try:
                embedding = self.embeddings.embed_documents([text])
                self.collection.add(
                    documents=[text],
                    metadatas=[metadata],
                    ids=[doc_id],
                    embeddings=embedding
                )
                logger.debug(f"Added document ID {doc_id} successfully.")
            except Exception as e:
                logger.exception(f"Error while adding document ID {doc_id} at index {i}: {e}")
                raise

    # Get single document by ID
    def get_doc_by_id(self, id):
        logger.debug(f"Attempting to retrieve document with ID: {id}")
        try:
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
        except Exception:
            logger.exception(f"Failed to retrieve document with ID: {id}")
            raise

    # Search documents using vector similarity
    def search_docs(self, query):
        try:
            results_count = self.results_count
            threshold = self.threshold
            logger.debug(f"Searching for top {results_count} documents with query: '{query}' and threshold: {threshold}")
            results = self.vectorstore.similarity_search_with_score(query, k=results_count)

            docs = []
            for doc, distance in results:
                logger.debug(f"Distance: {distance}, ID: {getattr(doc, 'id', None)}")
                if distance < threshold:
                    id_ = getattr(doc, 'id', None) or doc.metadata.get('id', None) or "unknown"
                    text = getattr(doc, 'page_content', None) or getattr(doc, 'text', None) or doc.metadata.get('text', None) or ""
                    metadata = getattr(doc, 'metadata', None) or {}
                    docs.append((DocumentDTO(id=id_, text=text, metadata=metadata), distance))

            logger.info(f"Found {len(docs)} documents within threshold {threshold}")
            return docs
        except Exception as e:
            logger.exception(f"Failed to search documents for query '{query}': {e}")
            raise

    # Update document by delete and re-add
    def update_doc(self, id, text, metadata=None):
        logger.info(f"Updating document with ID: {id}")
        try:
            self.delete_doc(id)
            self.add_docs([text], [metadata or {}], [id])
            logger.info(f"Document with ID: {id} updated successfully")
        except Exception:
            logger.exception(f"Failed to update document with ID: {id}")
            raise

    # Delete document by ID
    def delete_doc(self, id):
        logger.info(f"Deleting document with ID: {id}")
        try:
            self.collection.delete(ids=[id])
            logger.info(f"Document with ID: {id} deleted")
        except Exception:
            logger.exception(f"Failed to delete document with ID: {id}")
            raise

    # Clear all documents from collection
    def clear(self):
        try:
            ids = self.collection.get()["ids"]
            if ids:
                logger.warning(f"Clearing all documents, total count: {len(ids)}")
                self.collection.delete(ids=ids)
                logger.warning("All documents cleared")
            else:
                logger.info("Clear called but no documents to delete")
        except Exception:
            logger.exception("Failed to clear all documents")
            raise


    # Delete documents by prefix
    def delete_by_prefix(self, prefix: str):
        try:
            # Get all document IDs from the collection
            results = self.collection.get()
            all_ids = results.get("ids", [])
            
            # Filter IDs that start with the given prefix
            ids_to_delete = [id_ for id_ in all_ids if id_.startswith(prefix)]
            
            if ids_to_delete:
                # Delete documents with matching prefix
                self.collection.delete(ids=ids_to_delete)
                logger.debug(f"Successfully deleted {len(ids_to_delete)} documents with prefix '{prefix}'")
            else:
                logger.info(f"No documents with prefix '{prefix}' found")
        except Exception as e:
            logger.exception(f"Failed to delete documents by prefix '{prefix}': {e}")
            raise
