from app.core.dtos.DocumentDTO import DocumentDTO
from app.core.dtos.RagDTO import State
from typing import List, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

class ApplicationService:
    """
    Central application service in a hexagonal architecture for the WoPeD RAG system.

    Delegates business workflows to domain services, which in turn interact with infrastructure adapters.
    Main responsibilities:
      - Coordinates PDF ingestion, conversion, and indexing (single and batch)
      - Executes the Retrieval-Augmented Generation (RAG) pipeline
      - Provides document CRUD operations
      - Handles system startup routines

    This service is technology-agnostic and contains no direct adapter logic.
    """

    # Singleton instance - set in main.py
    application_service = None
    
    def __init__(self, db_service, rag_service, pdf_service, query_extraction_service):
        self.db_service = db_service
        self.rag_service = rag_service
        self.pdf_service = pdf_service
        self.query_extraction_service = query_extraction_service
        logger.info("ApplicationService initialized")

    # === RAG Operations ===
    
    # Complete RAG pipeline: (preprocess) -> retrieve -> augment -> return enriched prompt
    def process_rag_request(self, prompt: str, diagram: str) -> str:
        logger.info("[RAG PIPELINE] Starting RAG workflow")
        
        try:
            # Check if diagram preprocessing is enabled
            preprocessing_enabled = os.getenv("ENABLE_DIAGRAM_PREPROCESSING", "false").lower() == "true"
            logger.debug(f"[RAG PIPELINE] Original diagram: {diagram}")
            
            # Phase 1: Preprocessing
            if preprocessing_enabled:
                logger.debug(f"[RAG PIPELINE] Diagram preprocessing enabled")
                try:
                    query = self.query_extraction_service.extract_query(diagram)
                    logger.debug(f"[RAG PIPELINE] RAG search query: '{query[:200]}{'...' if len(query) > 200 else ''}'")
                except Exception as e:
                    logger.error(f"[RAG PIPELINE] Query extraction failed, using original diagram: {e}")
                    query = diagram
            else:
                query = diagram
                logger.debug(f"[RAG PIPELINE] Diagram preprocessing disabled - using original diagram")
            
            # Phase 2: Retrieve
            results = self.rag_service.retrieve(query)
            context = [dto for dto, _ in results] if results else []
            
            # Phase 3: Augment
            state: State = {
                "prompt": prompt,
                "diagram": diagram,
                "context": context,
                "answer": ""  # Answer will be generated through P2T service, not used here
            }
            enriched_prompt = self.rag_service.augment(state)

            logger.info("[RAG PIPELINE] Workflow completed successfully")
            return enriched_prompt
            
        except Exception as e:
            logger.exception(f"[RAG PIPELINE] Pipeline failed: {e}")

    # Search documents using RAG service
    def search_docs(self, query):
        return self.rag_service.retrieve(query)
    
    # === PDF Processing Orchestration ===

    # Load and index all PDFs from directory at startup
    def load_startup_pdfs(self):
        pdf_directory = os.environ.get("PDF_DIRECTORY")
        if not pdf_directory:
            logger.warning("PDF_DIRECTORY environment variable not set - skipping startup PDF indexing")
            return
        
        try:
            logger.info(f"Starting startup PDF indexing from directory: {pdf_directory} via PDFService")
            documents_by_prefix = self.pdf_service.process_directory(pdf_directory)
            
            successful = 0
            failed = 0
            errors = []

            for prefix, documents in documents_by_prefix.items():
                logger.debug(f"Cleaning old documents with prefix: {prefix} via DBService")
                self.db_service.delete_by_prefix(prefix)
                try:
                    logger.debug(f"Adding new documents via DBService")
                    self.db_service.add_docs(documents)
                    successful += 1
                except Exception as e:
                    logger.error(f"Error while adding documents for prefix {prefix}: {e}")
                    failed += 1
                    errors.append(f"{prefix}: {str(e)}")

            logger.info(f"PDF indexing complete: {successful} successful, {failed} failed")
            if errors:
                logger.warning(f"PDF indexing completed with errors: {errors}")
        except Exception as e:
            logger.exception(f"Startup PDF indexing failed: {e}")
    
    # Upload and index a single PDF file with a specific prefix
    def upload_and_index_pdf(self, file_path: str, prefix: str):
        logger.info(f"Uploading and indexing PDF: {file_path} with prefix: {prefix}")
        try:
            documents = self.pdf_service.load_and_convert_pdf(file_path, prefix)
            self.db_service.delete_by_prefix(prefix)
            self.db_service.add_docs(documents)
            logger.info(f"PDF {file_path} indexed successfully with prefix {prefix}")
        except Exception as e:
            logger.exception(f"Failed to upload and index PDF {file_path}: {e}")

    # === Document CRUD Operations ===
    
    def add_docs(self, documents):
        return self.db_service.add_docs(documents)

    def get_doc_by_id(self, doc_id):
        return self.db_service.get_doc_by_id(doc_id)

    def update_doc(self, document):
        return self.db_service.update_doc(document)

    def delete_doc(self, doc_id):
        return self.db_service.delete_doc(doc_id)

    def clear_docs(self):
        return self.db_service.clear()