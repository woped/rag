import logging
import os
from typing import Dict, Any, List
from ..ports.PDFLoaderPort import PDFLoaderPort
from ..dtos.DocumentDTO import DocumentDTO

logger = logging.getLogger(__name__)

class PDFService:
    
    def __init__(self, pdf_loader: PDFLoaderPort):
        self.pdf_loader = pdf_loader
        logger.debug("[PDFService] Initialized with injected PDF loader port")

    def load_and_convert_pdf(self, file_path: str, prefix: str) -> List[DocumentDTO]:
        logger.info(f"Loading and converting PDF: {file_path} with prefix: {prefix}")
        
        # Business validation
        if not file_path or not file_path.strip():
            raise ValueError("File path cannot be empty")
        if not prefix or not prefix.strip():
            raise ValueError("Prefix cannot be empty")
        
        # 1. Load via infrastructure
        chunks = self.pdf_loader.load_and_split(file_path)
        
        # 2. Business validation
        if not chunks:
            raise ValueError(f"No content extracted from {file_path}")
        
        # 3. Convert to DTOs (business logic)
        documents = []
        for i, chunk in enumerate(chunks):
            doc = DocumentDTO(
                id=f"{prefix}_{i}",
                text=chunk['page_content'],
                metadata=chunk['metadata']
            )
            documents.append(doc)
        
        logger.info(f"Successfully converted PDF to {len(documents)} DocumentDTOs: {file_path}")
        return documents

    def process_directory_to_documents(self, pdf_directory: str) -> Dict[str, Any]:
        logger.info(f"Processing PDF directory to documents: {pdf_directory}")
        
        # Business validation
        if not pdf_directory or not pdf_directory.strip():
            raise ValueError("PDF directory cannot be empty")
        
        # 1. Get PDF files via infrastructure
        pdf_files = self.get_pdf_files_from_directory(pdf_directory)
        
        # 2. Business logic: Process each file and track results
        results = {"successful": 0, "failed": 0, "errors": [], "documents": []}
        
        for pdf_file in pdf_files:
            try:
                # Business logic: Extract filename as prefix
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

    def get_pdf_files_from_directory(self, directory: str) -> List[str]:
        logger.debug(f"Getting PDF files from directory: {directory}")
        
        # Business validation
        if not directory or not directory.strip():
            raise ValueError("Directory cannot be empty")
        
        # Delegate to infrastructure
        return self.pdf_loader.get_pdf_files(directory)
