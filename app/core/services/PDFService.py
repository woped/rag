import logging
import os
from typing import Dict, Any, List
from app.core.ports.PDFLoaderPort import PDFLoaderPort
from app.core.dtos.DocumentDTO import DocumentDTO

logger = logging.getLogger(__name__)

class PDFService:
    """
    Domain service for orchestrating PDF processing in the WoPeD RAG system.

    This service represents the business logic layer for all PDF-related workflows. 
    It delegates technical operations (such as file access and parsing) to an injected PDFLoader (adapter), 
    ensuring a clean separation between business logic and infrastructure. 
    Responsibilities include:
      - Coordinating the loading and conversion of all PDFs from a directory into DocumentDTOs
      - Performing business-level validation and logging of successful operations
      - Grouping documents by prefix for downstream indexing
      - Providing a technology-agnostic API for PDF ingestion and conversion

    Note: 
      - Success logs and business-relevant events are handled in this service.
      - Technical errors and warnings are logged in the adapter layer.
    """

    def __init__(self, pdf_loader: PDFLoaderPort):
        self.pdf_loader = pdf_loader
        logger.info("[PDFService] initialized")

    # Entry point for processing a directory of PDFs
    def process_directory(self, pdf_directory: str) -> Dict[str, List[DocumentDTO]]:
        results = self.load_directory(pdf_directory)
        if not results["documents"]:
            logger.error(f"No documents found in directory: {pdf_directory}. Errors: {results.get('errors', [])}")
            raise RuntimeError(f"No documents could be processed from directory: {pdf_directory}")
        return self.group_by_prefix(results["documents"])
    
    # Load and convert all PDF files from a directory
    # Returns a dictionary with counts of successful and failed conversions, along with errors and the list of successfully converted DocumentDTOs
    def load_directory(self, pdf_directory: str) -> Dict[str, Any]:
        if not pdf_directory or not pdf_directory.strip():
            raise ValueError("PDF directory cannot be empty")
        if not os.path.exists(pdf_directory):
            logger.warning(f"Directory does not exist: {pdf_directory}")
            return {"successful": 0, "failed": 0, "errors": [f"Directory does not exist: {pdf_directory}"], "documents": []}
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
    
    # Load a single PDF, split into chunks, and convert to DocumentDTOs
    def load_and_convert_pdf(self, file_path: str, prefix: str) -> List[DocumentDTO]:
        logger.debug(f"Loading and converting PDF: {file_path}")
        if not file_path or not file_path.strip():
            raise ValueError("File path cannot be empty")
        if not prefix or not prefix.strip():
            raise ValueError("Prefix cannot be empty")
        document = self.pdf_loader.load_pdf(file_path)
        chunks = self.pdf_loader.split_document(document)
        if not chunks:
            raise ValueError(f"No content extracted from {file_path}")
        dtos = self.pdf_loader.convert_chunks_to_dtos(chunks, prefix)
        logger.info(f"Successfully loaded & converted PDF: {file_path} to {len(dtos)} DocumentDTOs")
        return dtos
    
    # Group DocumentDTOs by their prefix (everything before the last underscore in the ID)
    def group_by_prefix(self, documents: List[DocumentDTO]) -> Dict[str, List[DocumentDTO]]:
        logger.debug(f"Grouping {len(documents)} documents by prefix")
        documents_by_prefix = {}
        for doc in documents:
            prefix = doc.id.rsplit('_', 1)[0]
            if prefix not in documents_by_prefix:
                documents_by_prefix[prefix] = []
            documents_by_prefix[prefix].append(doc)
        logger.debug(f"Grouped documents into {len(documents_by_prefix)} prefixes: {list(documents_by_prefix.keys())}")
        return documents_by_prefix
