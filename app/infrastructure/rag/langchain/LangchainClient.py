from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from chromadb import PersistentClient
from langchain_core.documents import Document
from app.core.dtos.DocumentDTO import DocumentDTO

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

    def search_docs(self, query, k, threshold=25):
        # Perform semantic search using LangChain's similarity_search_with_score
        # This returns (document, distance) tuples where lower distance means higher similarity
        results = self.vectorstore.similarity_search_with_score(query, k=k)

        docs = []
        for doc, distance in results:
            print(f"Distance: {distance}, ID: {getattr(doc, 'id', None)}")
            if distance <= threshold:
                id_ = getattr(doc, 'id', None) or doc.metadata.get('id', None) or "unknown"
                text = getattr(doc, 'page_content', None) or getattr(doc, 'text', None) or doc.metadata.get('text', None) or ""
                metadata = getattr(doc, 'metadata', None) or {}
                docs.append((DocumentDTO(id=id_, text=text, metadata=metadata), distance))
        return docs

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

