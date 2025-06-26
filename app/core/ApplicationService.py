from app.core.dtos.DocumentDTO import DocumentDTO
import logging
import glob
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
    
    def __init__(self, pdf_loader, db_service, rag_service, collection):
        self.pdf_loader = pdf_loader
        self.db_service = db_service
        self.rag_service = rag_service
        self.collection = collection
        logger.info("ApplicationService initialized")

    # === PDF Processing Operations ===
    
    # Load, split and store PDF in database
    def upload_and_index_pdf(self, pdf_path: str, prefix: str):
        self.delete_old_docs_by_prefix(prefix)
        chunks = self.pdf_loader.load_and_split(pdf_path)
        texts = [c.page_content for c in chunks]
        metadatas = [c.metadata for c in chunks]
        ids = [f"{prefix}_{i}" for i in range(len(texts))]
        self.db_service.add_docs([
            DocumentDTO(id=i, text=t, metadata=m)
            for i, t, m in zip(ids, texts, metadatas)
        ])
        logger.info(f"Indexed and stored pdf '{pdf_path}'")

    # Load and index all PDFs from directory at startup
    def load_and_index_startup_pdfs(self, pdf_directory="PDF"):
        pdf_pattern = os.path.join(pdf_directory, "*.pdf")
        pdf_files = glob.glob(pdf_pattern)
        
        results = {
            "total_found": len(pdf_files),
            "successfully_indexed": 0,
            "failed": 0,
            "errors": []
        }
        
        if not pdf_files:
            logger.info(f"No PDF files found in {pdf_directory}/ directory")
            return results
            
        logger.info(f"Found {len(pdf_files)} PDF files to index in {pdf_directory}/")
        
        for pdf_path in pdf_files:
            logger.info(f"Loading PDF: {pdf_path}")
            filename_prefix = os.path.basename(pdf_path).replace(".pdf", "")
            
            try:
                self.upload_and_index_pdf(pdf_path, filename_prefix)
                logger.info(f"Successfully indexed: {pdf_path}")
                results["successfully_indexed"] += 1
                
            except Exception as e:
                error_msg = f"Failed to index {pdf_path}: {str(e)}"
                logger.error(error_msg)
                results["failed"] += 1
                results["errors"].append(error_msg)
        
        logger.info(f"PDF indexing complete: {results['successfully_indexed']} successful, {results['failed']} failed")
        return results
    
    # Delete documents by ID prefix
    def delete_old_docs_by_prefix(self, prefix):
        results = self.collection.get()
        all_ids = results.get("ids", [])
        ids_to_delete = [id_ for id_ in all_ids if id_.startswith(prefix)]
        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)
            logger.info(f"-> Deleted {len(ids_to_delete)} old chunks with prefix '{prefix}'")
        else:
            logger.info(f"-> No old chunks with prefix '{prefix}' found")

    # === RAG Operations ===
    
    # Complete RAG pipeline: retrieve -> augment -> return enriched prompt
    def process_rag_request(self, prompt: str, question: str) -> str:
        logger.info("[RAG PIPELINE] Starting RAG workflow")
        # Phase 1: Retrieve
        results = self.rag_service.retrieve(question)
        context = [dto for dto, _ in results]
        
        # Phase 2: Augment
        state = {
            "prompt": prompt,
            "question": question,
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


