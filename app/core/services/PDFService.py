import logging
import os
from typing import Dict, Any, List
from app.core.ports.PDFLoaderPort import PDFLoaderPort
from app.core.dtos.DocumentDTO import DocumentDTO

logger = logging.getLogger(__name__)

class PDFService:
    """
    Service for orchestrating PDF processing in the WoPeD RAG system.

    This service acts as the domain layer for all PDF-related workflows. It delegates
    technical operations to an injected PDFLoader (adapter), ensuring a clean separation
    between business logic and infrastructure. Responsibilities include:
      - Loading and converting all PDFs from a directory into DocumentDTOs
      - Handling errors and logging during batch and single PDF processing
      - Grouping documents by prefix for downstream indexing
      - Providing a technology-agnostic API for PDF ingestion and conversion
    """

    def __init__(self, pdf_loader: PDFLoaderPort):
        self.pdf_loader = pdf_loader
        logger.info("[PDFService] initialized")

    # Entry point for processing a directory of PDFs
    def process_directory(self, pdf_directory: str) -> Dict[str, List[DocumentDTO]]:
        try:
            results = self.load_directory(pdf_directory)
            if not results["documents"]:
                logger.error(f"No documents found in directory: {pdf_directory}. Errors: {results.get('errors', [])}")
                raise RuntimeError(f"No documents could be processed from directory: {pdf_directory}")
            return self.group_by_prefix(results["documents"])
        except Exception as e:
            logger.exception(f"Failed to process directory {pdf_directory}: {e}")
            raise
    
    # Load and convert all PDF files from a directory
    # Returns a dictionary with counts of successful and failed conversions, along with errors and the list of successfully converted DocumentDTOs
    def load_directory(self, pdf_directory: str) -> Dict[str, Any]:
        logger.info(f"Processing PDF directory to documents: {pdf_directory}")
        
        if not pdf_directory or not pdf_directory.strip():
            raise ValueError("PDF directory cannot be empty")
        
        try:
            pdf_files = self.pdf_loader.get_pdf_files(pdf_directory)

            results = {"successful": 0, "failed": 0, "errors": [], "documents": []}
            
            for pdf_file in pdf_files:
                try:
                    filename = os.path.splitext(os.path.basename(pdf_file))[0]
                    documents = self.load_and_convert_pdf(pdf_file, filename)
                    results["documents"].extend(documents)
                    results["successful"] += 1
                except Exception as e:
                    logger.error(f"Failed to process PDF '{pdf_file}': {e}")
                    results["failed"] += 1
                    results["errors"].append({"file": pdf_file, "error": str(e)})
            
            logger.info(f"Directory processing complete: {results['successful']} successful, {results['failed']} failed")
            return results
        except Exception as e:
            logger.exception(f"Failed to load directory {pdf_directory}: {e}")
            raise
    
    # Load a single PDF, split into chunks, and convert to DocumentDTOs
    def load_and_convert_pdf(self, file_path: str, prefix: str) -> List[DocumentDTO]:
        logger.info(f"Loading and converting PDF: {file_path} with prefix: {prefix}")
        
        if not file_path or not file_path.strip():
            raise ValueError("File path cannot be empty")
        if not prefix or not prefix.strip():
            raise ValueError("Prefix cannot be empty")
        
        try:  
            chunks = self.pdf_loader.load_and_split(file_path)
            
            if not chunks:
                raise ValueError(f"No content extracted from {file_path}")
            
            documents = self.pdf_loader.convert_chunks_to_dtos(chunks, prefix)
            
            logger.info(f"Successfully converted PDF to {len(documents)} DocumentDTOs: {file_path}")
            return documents
        except Exception as e:
            logger.error(f"Failed to load and convert PDF {file_path}: {e}")
            raise
    
    # Group DocumentDTOs by their prefix (everything before the last underscore in the ID)
    def group_by_prefix(self, documents: List[DocumentDTO]) -> Dict[str, List[DocumentDTO]]:
        logger.debug(f"Grouping {len(documents)} documents by prefix")
        
        try:
            documents_by_prefix = {}
            for doc in documents:
                prefix = doc.id.rsplit('_', 1)[0]
                if prefix not in documents_by_prefix:
                    documents_by_prefix[prefix] = []
                documents_by_prefix[prefix].append(doc)
            logger.debug(f"Grouped documents into {len(documents_by_prefix)} prefixes: {list(documents_by_prefix.keys())}")
            return documents_by_prefix
        except Exception as e:
            logger.exception(f"Failed to group documents by prefix: {e}")
            raise
