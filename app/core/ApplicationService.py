from app.core.dtos.DocumentDTO import DocumentDTO
from app.core.dtos.RagDTO import State
from typing import List, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

class ApplicationService:
    """
    Main orchestrator for PDF processing and RAG operations in the WoPeD integration system.
    
    This service coordinates complex workflows between multiple domain services and infrastructure components.
    It serves as the primary entry point for REST controllers and handles the complete lifecycle of 
    document processing - from PDF upload and indexing to intelligent document retrieval and prompt enrichment.
    
    Key responsibilities include PDF processing pipelines, RAG query orchestration, document CRUD operations,
    and system initialization. Implements application-level business logic while delegating technical concerns
    to specialized services (DatabaseService for persistence, RAGService for retrieval/augmentation).
    
    Architecture: Application layer service that acts as a facade over domain services, providing
    simplified interfaces for complex multi-step workflows and maintaining system state consistency.
    """
    
    # Singleton instance - set in main.py
    application_service = None
    
    def __init__(self, db_service, rag_service, pdf_service, query_extraction_service):
        self.db_service = db_service
        self.rag_service = rag_service
        self.pdf_service = pdf_service
        self.query_extraction_service = query_extraction_service
        logger.info("ApplicationService initialized")

    # === PDF Processing Orchestration ===
    
    def process_pdf(self, file_path: str, prefix: str) -> None:
        logger.info(f"Orchestrating PDF processing: {file_path} with prefix: {prefix}")
        
        # 1. PDF Service: Load and convert to DocumentDTOs
        documents = self.pdf_service.load_and_convert_pdf(file_path, prefix)
        
        # 2. Database Service: Clean old data with same prefix first
        logger.debug(f"Cleaning old documents with prefix: {prefix}")
        self.db_service.delete_by_prefix(prefix)
        
        # 3. Database Service: Store new documents
        self.db_service.add_docs(documents)
        
        logger.info(f"Successfully processed PDF: {file_path}, stored {len(documents)} chunks")

    def process_directory(self, pdf_directory: str) -> Dict[str, Any]:
        logger.info(f"Orchestrating PDF directory processing: {pdf_directory}")
        
        # 1. PDF Service: Get all documents from directory
        results = self.pdf_service.process_directory_to_documents(pdf_directory)
        
        # 2. Database Service: Store all documents if any were successfully processed
        if results["documents"]:
            # Group documents by prefix for efficient batch operations
            documents_by_prefix = {}
            for doc in results["documents"]:
                prefix = doc.id.rsplit('_', 1)[0]  # Extract prefix from document ID
                if prefix not in documents_by_prefix:
                    documents_by_prefix[prefix] = []
                documents_by_prefix[prefix].append(doc)
            
            # Clean and store for each prefix
            for prefix, documents in documents_by_prefix.items():
                logger.debug(f"Cleaning old documents with prefix: {prefix}")
                self.db_service.delete_by_prefix(prefix)
                self.db_service.add_docs(documents)
        
        # Return clean summary (without documents)
        return {
            "successful": results["successful"],
            "failed": results["failed"],
            "errors": results["errors"]
        }

    # Load and index all PDFs from directory at startup
    def load_startup_pdfs(self):
        pdf_directory = os.environ.get("PDF_DIRECTORY")
        logger.info(f"Starting startup PDF indexing from directory: {pdf_directory}")
        results = self.process_directory(pdf_directory)
        logger.info(f"PDF indexing complete: {results['successful']} successful, {results['failed']} failed")

    # === RAG Operations ===
    
    # Complete RAG pipeline: retrieve -> augment -> return enriched prompt
    def process_rag_request(self, prompt: str, diagram: str) -> str:
        logger.info("[RAG PIPELINE] Starting RAG workflow")
        
        # Check if diagram preprocessing is enabled
        preprocessing_enabled = os.getenv("ENABLE_DIAGRAM_PREPROCESSING").lower() == "true"
        logger.debug(f"[RAG PIPELINE] Original diagram: {diagram}")
        
        if preprocessing_enabled:
            # Preprocessing: Extract semantic content from PNML/BPMN
            logger.debug(f"[RAG PIPELINE] Diagram preprocessing enabled")
            query = self.query_extraction_service.extract_query(diagram)
            logger.debug(f"[RAG PIPELINE] RAG search query: '{query[:200]}{'...' if len(query) > 200 else ''}'")
        else:
            # Use diagram as-is for RAG search
            query = diagram
            logger.debug(f"[RAG PIPELINE] Diagram preprocessing disabled - using original diagram")
        
        # Phase 1: Retrieve
        results = self.rag_service.retrieve(query)
        context = [dto for dto, _ in results]
        
        # Phase 2: Augment
        state: State = {
            "prompt": prompt,
            "diagram": diagram,
            "context": context,
            "answer": ""  # Not used
        }
        enriched_prompt = self.rag_service.augment(state)

        logger.info("[RAG PIPELINE] Workflow completed successfully")
        return enriched_prompt

    # Search documents using RAG service
    def search_docs(self, query):
        logger.info(f"Searching documents with query: '{query}' via ApplicationService")
        return self.rag_service.retrieve(query)

    # === Document CRUD Operations ===
    
    # Add documents to database
    def add_docs(self, documents):
        logger.info(f"Adding {len(documents)} documents via ApplicationService")
        return self.db_service.add_docs(documents)

    # Get document by ID
    def get_doc_by_id(self, doc_id):
        logger.debug(f"Retrieving document with ID: {doc_id} via ApplicationService")
        return self.db_service.get_doc_by_id(doc_id)

    # Update existing document
    def update_doc(self, document):
        logger.debug(f"Updating document with ID: {document.id} via ApplicationService")
        return self.db_service.update_doc(document)

    # Delete document by ID
    def delete_doc(self, doc_id):
        logger.debug(f"Deleting document with ID: {doc_id} via ApplicationService")
        return self.db_service.delete_doc(doc_id)

    # Clear all documents
    def clear_docs(self):
        logger.warning("Clearing all documents via ApplicationService")
        return self.db_service.clear()
