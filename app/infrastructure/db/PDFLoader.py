import os
import glob
import nltk
import logging
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import NLTKTextSplitter
from app.core.ports.PDFLoaderPort import PDFLoaderPort
from app.core.dtos.DocumentDTO import DocumentDTO

logger = logging.getLogger(__name__)

class PDFLoader(PDFLoaderPort):
    def __init__(self):
        try:
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
            logger.debug(f"[PDFLoader] initialized with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
        except Exception as e:
            logger.exception(f"Failed to initialize PDFLoader: {e}")
            raise
    
    # Load a PDF file and split its content into chunks.
    def load_and_split(self, file_path: str) -> List[dict]:
        try:
            logger.info(f"Loading and splitting PDF: {file_path}")
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            if not documents:
                logger.warning(f"No content loaded from PDF: {file_path}")
                return []
            chunks = self.splitter.split_documents(documents)
            logger.debug(f"Split into {len(chunks)} chunks")
            result = []
            for chunk in chunks:
                result.append({
                    'page_content': chunk.page_content,
                    'metadata': chunk.metadata or {}
                })
            return result
        except FileNotFoundError:
            logger.error(f"PDF file not found: {file_path}")
            raise
        except Exception as e:
            logger.exception(f"Failed to load and split PDF {file_path}: {e}")
            raise
    
    # Find all PDF files in the specified directory.
    def get_pdf_files(self, directory: str) -> List[str]:
        try:
            if not os.path.exists(directory):
                logger.warning(f"Directory does not exist: {directory}")
                return []
            pdf_pattern = os.path.join(directory, "*.pdf")
            pdf_files = glob.glob(pdf_pattern)
            logger.debug(f"Found {len(pdf_files)} PDF files in directory: {directory}")
            return pdf_files
        except Exception as e:
            logger.exception(f"Failed to get PDF files from directory {directory}: {e}")
            raise

    # Convert chunk dictionaries to DocumentDTO objects with a given prefix.
    def convert_chunks_to_dtos(self, chunks: List[dict], prefix: str) -> List['DocumentDTO']:
        try:
            logger.debug(f"Converting {len(chunks)} chunks to DTOs with prefix: {prefix}")
            documents = []
            for i, chunk in enumerate(chunks):
                doc = DocumentDTO(
                    id=f"{prefix}_{i}",
                    text=chunk['page_content'],
                    metadata=chunk['metadata']
                )
                documents.append(doc)
            logger.debug(f"Successfully converted {len(documents)} chunks to DocumentDTOs")
            return documents
        except Exception as e:
            logger.exception(f"Failed to convert chunks to DTOs with prefix {prefix}: {e}")
            raise
