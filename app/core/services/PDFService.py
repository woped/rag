from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import NLTKTextSplitter
from app.core.dtos.DocumentDTO import DocumentDTO
import nltk
import os
import glob
import logging

logger = logging.getLogger(__name__)

class PDFService:
    """
    Service for PDF document processing in the RAG system.
    
    Handles the complete PDF processing pipeline:
    - Loads PDF files using PyPDFLoader
    - Splits documents into manageable chunks using NLTK text splitter
    - Configures chunk size and overlap from environment variables
    - Downloads required NLTK resources automatically
    
    The splitting strategy uses NLTK for more intelligent sentence-aware chunking,
    ensuring that document chunks maintain semantic coherence for better
    similarity search and retrieval performance.
    
    This service focuses solely on PDF processing logic, following single 
    responsibility principle for better maintainability and testability.
    """
    
    def __init__(self):
        logger.debug("Initializing PDFService")
        
        # Download required NLTK resources
        for resource in ['punkt', 'punkt_tab']:
            try:
                nltk.data.find(f'tokenizers/{resource}')
                logger.debug(f"Found NLTK resource: {resource}")
            except LookupError:
                logger.info(f"Downloading NLTK resource: {resource}")
                nltk.download(resource)

        # Configure text splitter from environment
        chunk_size = int(os.environ.get("CHUNK_SIZE", 150))
        chunk_overlap = int(os.environ.get("CHUNK_OVERLAP", 50))
        
        self.splitter = NLTKTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        logger.debug(f"PDFService initialized with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")

    def load_and_split(self, file_path: str):
        logger.info(f"Loading and splitting PDF: {file_path}")
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            if not documents:
                logger.warning(f"No content loaded from PDF: {file_path}")
                return []
                
            chunks = self.splitter.split_documents(documents)
            logger.debug(f"Split into {len(chunks)} chunks")
            return chunks
            
        except FileNotFoundError:
            logger.error(f"PDF file not found: {file_path}")
            raise
        except Exception as e:
            logger.exception(f"Failed to load and split PDF: {file_path}")
            raise

    def get_startup_pdfs(self, pdf_directory="PDF"):
        """Get list of PDF files for startup indexing"""
        pdf_pattern = os.path.join(pdf_directory, "*.pdf")
        pdf_files = glob.glob(pdf_pattern)
        return pdf_files
    
    def store_chunks(self, chunks, filename_prefix, collection):
        """Store PDF chunks in collection with proper IDs"""
        logger.info(f"Storing {len(chunks)} chunks with prefix '{filename_prefix}'")
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        ids = [f"{filename_prefix}_{i}" for i in range(len(texts))]

        try:
            collection.delete(ids=ids)
            logger.debug(f"Deleted existing IDs: {ids}")
        except Exception as e:
            logger.warning(f"Warning when deleting existing IDs: {e}")

        collection.add(documents=texts, metadatas=metadatas, ids=ids)
        logger.info(f"Chunks successfully stored in collection")
    
    def upload_and_index_pdf(self, pdf_path: str, prefix: str, collection):
        """Complete PDF upload and indexing workflow"""
        logger.info(f"PDFService: Starting upload and indexing of '{pdf_path}' with prefix '{prefix}'")
        try:
            # Delete old documents with same prefix
            self.delete_old_docs_by_prefix(prefix, collection)
            
            # Load and split PDF
            chunks = self.load_and_split(pdf_path)
            
            # Store chunks
            self.store_chunks(chunks, prefix, collection)
            
            logger.info(f"PDFService: Successfully completed upload and indexing of '{pdf_path}'")
        except Exception as e:
            logger.error(f"PDFService: Error during upload and indexing of '{pdf_path}': {e}")
            raise
    
    def load_and_index_startup_pdfs(self, pdf_directory, collection):
        """Load and index all PDFs from directory at startup"""
        logger.info(f"PDFService: Starting startup PDF indexing from directory: {pdf_directory}")
        
        pdf_files = self.get_startup_pdfs(pdf_directory)
        successfully_indexed = 0
        failed = 0
        
        for pdf_file in pdf_files:
            try:
                filename = os.path.splitext(os.path.basename(pdf_file))[0]
                self.upload_and_index_pdf(pdf_file, filename, collection)
                successfully_indexed += 1
            except Exception as e:
                logger.error(f"PDFService: Failed to index PDF '{pdf_file}': {e}")
                failed += 1
        
        results = {"successfully_indexed": successfully_indexed, "failed": failed}
        logger.info(f"PDFService: PDF indexing complete: {results['successfully_indexed']} successful, {results['failed']} failed")
        return results

    def delete_old_docs_by_prefix(self, prefix, collection):
        """Delete documents with specific prefix from collection"""
        results = collection.get()
        all_ids = results.get("ids", [])
        ids_to_delete = [id_ for id_ in all_ids if id_.startswith(prefix)]
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            logger.info(f"-> Deleted {len(ids_to_delete)} old chunks with prefix '{prefix}'")
        else:
            logger.info(f"-> No old chunks with prefix '{prefix}' found")
