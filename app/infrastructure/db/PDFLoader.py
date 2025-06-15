from chromadb import PersistentClient
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

class PDFLoader:
    def __init__(self, collection):
        self.collection = collection
        #Hier die Chunk Size je nachdem anpassen. Je höher die Chunk Size desto mehr Einträge in Chroma. 
        #Wenn die Chunk Size zu hoch gesetzt wird, gibt es Probleme bei der Similarity Search. 
        # Wenn in der Suche nur wenige Begriffe verwendet werden und die Einträge große Textblöcke enthalten, kann der vorliegende Treshold 0.9 nicht eingehalten werden und es gibt keine Ausgabe. 
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=50,separators=["\n\n", "\n", ".", " ", ""])

    def load_and_split(self, file_path):
        loader = PyPDFLoader(file_path)
        return self.splitter.split_documents(loader.load())

    def store_chunks(self, chunks, filename_prefix="chunk"):
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        ids = [f"{filename_prefix}_{i}" for i in range(len(texts))]
        
        try:
            self.collection.delete(ids=ids)
        except Exception as e:
            print(f"Warnung beim Löschen vorhandener IDs: {e}")
        
        self.collection.add(documents=texts, metadatas=metadatas, ids=ids)
        


