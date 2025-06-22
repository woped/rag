from app.core.dtos.DocumentDTO import DocumentDTO
import logging

logger = logging.getLogger(__name__)

class ApplicationService:
    """
    Core application service that orchestrates PDF indexing and RAG operations.
    
    This service acts as the main coordinator between different components:
    - PDF loading and document chunking
    - Vector database operations for document storage and retrieval
    - RAG-based prompt enrichment for external LLM services
    
    The service handles the complete lifecycle from PDF ingestion to retrieving
    relevant context for prompt augmentation, supporting the RAG pipeline
    without direct LLM generation (delegated to external services like P2T).
    """
    
    def __init__(self, pdf_loader, db_service, rag_service, collection):
        self.pdf_loader = pdf_loader
        self.db_service = db_service
        self.rag_service = rag_service
        self.collection = collection

    def delete_old_docs_by_prefix(self, prefix):
        results = self.collection.get()
        all_ids = results.get("ids", [])
        ids_to_delete = [id_ for id_ in all_ids if id_.startswith(prefix)]
        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)
            logger.info(f"-> Deleted {len(ids_to_delete)} old chunks with prefix '{prefix}'")
        else:
            logger.info(f"-> No old chunks with prefix '{prefix}' found")

    def upload_and_index_pdf(self, pdf_path: str, prefix: str):
        """Loads, splits, and stores a PDF in the database."""
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

    def answer_with_rag(self, state) -> str:
        """Returns an enriched prompt or a full RAG answer using State-DTO."""
        return self.rag_service.enrich_prompt(state)