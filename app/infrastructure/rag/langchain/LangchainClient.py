from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from chromadb import PersistentClient
from langchain_core.documents import Document

class LangchainClient:
    """
    LangchainClient is a hybrid wrapper that combines LangChain's Chroma VectorStore
    for semantic search with direct access to ChromaDB for CRUD operations.

    - Uses LangChain for similarity search via sentence embeddings
    - Uses ChromaDB native client for add, get, delete, update
    - Stores all data persistently in the given directory

    """

    # Änderung vom Collection Namen: Es muss ein einheitlicher Name verwendet werden (vorher stand hier als Name "rag_collection_langchain")
    def __init__(self, persist_directory="chroma"):
        self.persist_directory = persist_directory

        # LangChain-compatible VectorStore using HuggingFace embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vectorstore = Chroma(
            collection_name="rag_collection",
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

        # Native ChromaDB client for direct CRUD access
        self.client = PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(name="rag_collection")


    def add_docs(self, texts, metadatas=None, ids=None):
        # Add one or more documents directly to ChromaDB using manually computed embeddings
        if metadatas is None:
            metadatas = [{} for _ in texts]
        if ids is None:
            ids = [str(i) for i in range(len(texts))]

        # Compute embeddings from plain texts
        embeddings = self.embeddings.embed_documents(texts)

        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )

    def get_doc_by_id(self, id):
        #Retrieve a document by its ID using the native ChromaDB client.
        result = self.collection.get(ids=[id])
        if not result["documents"]:
            return None
        return {
            "id": result["ids"][0],
            "text": result["documents"][0],
            "metadata": result["metadatas"][0]
        }

    def search_docs(self, query, k=10, threshold=0.9):
        # Perform semantic search using LangChain's similarity_search_with_score
        # This returns (document, distance) tuples where lower distance means higher similarity
        results = self.vectorstore.similarity_search_with_score(query, k=k)

        # Filter documents based on similarity threshold (lower distance = better match)
        filtered = [
            {
                "content": doc.page_content,
                "score": score  # Note: this is a distance, not a similarity score
            }
            for doc, score in results
            if score <= threshold
        ]

        return filtered

    def update_doc(self, id, text, metadata=None):
        #Update a document by deleting and re-adding it with the same ID.
        self.delete_doc(id)
        self.add_docs([text], [metadata or {}], [id])

    def delete_doc(self, id):
        #Delete a document by its ID.
        self.collection.delete(ids=[id])

    def clear(self):
        ids = self.collection.get()["ids"]
        if ids:
            self.collection.delete(ids=ids)

