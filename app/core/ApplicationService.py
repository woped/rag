from app.core.dtos.DocumentDTO import DocumentDTO
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
    
    def __init__(self, db_service, rag_service, pdf_service, preprocessing_service, collection):
        self.db_service = db_service
        self.rag_service = rag_service
        self.pdf_service = pdf_service
        self.preprocessing_service = preprocessing_service
        self.collection = collection
        logger.info("ApplicationService initialized")

    # === PDF Processing Operations ===
    
    # Load and index all PDFs from directory at startup
    def load_startup_pdfs(self, pdf_directory="PDF"):
        logger.info(f"Starting startup PDF indexing from directory: {pdf_directory}")
        return self.pdf_service.load_and_index_startup_pdfs(pdf_directory, self.collection)

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
            query = self.preprocessing_service.preprocess(diagram)
            logger.debug(f"[RAG PIPELINE] RAG search prompt: '{query}'")
        else:
            # Use diagram as-is for RAG search
            query = diagram
            logger.debug(f"[RAG PIPELINE] Diagram preprocessing disabled - using original diagram")
        
        # Phase 1: Retrieve
        results = self.rag_service.retrieve(query)
        context = [dto for dto, _ in results]
        
        # Phase 2: Augment
        state = {
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
