"""from chromadb import PersistentClient


    ChromaDatabase provides direct access to ChromaDB for storing,
    retrieving, updating, deleting, and querying documents using embeddings.

    This class manages a persistent ChromaDB collection and offers
    simple CRUD and similarity search operations.

    Intended for use without LangChain.


class ChromaDatabase:
    def __init__(self, persist_directory="chroma"):
        self.client = PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name="rag_collection")

    def add_docs(self, texts, metadatas=None, ids=None):
        if metadatas is None:
            metadatas = [{} for _ in texts]
        if ids is None:
            ids = [str(i) for i in range(len(texts))]
        self.collection.add(documents=texts, metadatas=metadatas, ids=ids)

    def delete_doc(self, id):
        self.collection.delete(ids=[id])

    def get_doc_by_id(self, id):
        return self.collection.get(ids=[id])

    def update_doc(self, id, new_text, new_metadata=None):
        self.delete_doc(id)
        self.add_docs(new_text, metadata=new_metadata, id=id)
"""