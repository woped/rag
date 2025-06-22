from chromadb import PersistentClient
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import NLTKTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
import nltk
import logging

logger = logging.getLogger(__name__)

class PDFLoader:
    """
    PDF document loader and text splitter for the RAG system.
    
    This class handles the extraction and preprocessing of PDF documents:
    - Loads PDF files using PyPDFLoader
    - Splits documents into manageable chunks using NLTK text splitter
    - Configures chunk size and overlap from environment variables
    - Stores processed chunks directly in ChromaDB collection
    
    The splitting strategy uses NLTK for more intelligent sentence-aware chunking,
    ensuring that document chunks maintain semantic coherence for better
    similarity search and retrieval performance.
    """
    
    def __init__(self, collection):
        logger.debug("Initialising PDFLoader")
        for resource in ['punkt', 'punkt_tab']:
            try:
                nltk.data.find(f'tokenizers/{resource}')
                logger.debug(f"Found NLTK resource: {resource}")
            except LookupError:
                logger.info(f"Downloading NLTK resource: {resource}")
                nltk.download(resource)

        chunk_size = int(os.environ.get("CHUNK_SIZE", 150))
        chunk_overlap = int(os.environ.get("CHUNK_OVERLAP", 50))

        self.collection = collection
        self.splitter = NLTKTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def load_and_split(self, file_path):
        logger.info(f"Loading and splitting PDF: {file_path}")
        loader = PyPDFLoader(file_path)
        return self.splitter.split_documents(loader.load())

    def store_chunks(self, chunks, filename_prefix="chunk"):
        logger.info(f"Storing {len(chunks)} chunks with prefix '{filename_prefix}'")
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        ids = [f"{filename_prefix}_{i}" for i in range(len(texts))]
        
        try:
            self.collection.delete(ids=ids)
            logger.debug(f"Deleted existing IDs: {ids}")
        except Exception as e:
            logger.warning(f"Warning when deleting existing IDs: {e}")
        
        self.collection.add(documents=texts, metadatas=metadatas, ids=ids)
        logger.info(f"Chunks successfully stored in collection")



