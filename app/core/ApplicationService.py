from app.core.dtos.DocumentDTO import DocumentDTO
import logging

logger = logging.getLogger(__name__)

class ApplicationService:
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
        logger.info(f"Starting upload and indexing of '{pdf_path}' with prefix '{prefix}'")
    
        self.delete_old_docs_by_prefix(prefix)
    
        try:
            chunks = self.pdf_loader.load_and_split(pdf_path)
            logger.debug(f"Loaded {len(chunks)} chunks from PDF")
        except Exception as e:
            logger.error(f"Error while loading PDF '{pdf_path}': {e}")
            raise

        texts = [c.page_content for c in chunks]
        metadatas = [c.metadata for c in chunks]
        ids = [f"{prefix}_{i}" for i in range(len(texts))]
    
        try:
            self.db_service.add_docs([
            DocumentDTO(id=i, text=t, metadata=m)
            for i, t, m in zip(ids, texts, metadatas)
            ])
            logger.info(f"Successfully stored {len(texts)} chunks from '{pdf_path}'")
        except Exception as e:
            logger.error(f"Error while storing chunks for '{pdf_path}': {e}")
            raise

    def answer_with_rag(self, question: str, k: int) -> str:
        """Returns an enriched prompt or a full RAG answer."""
        logger.info(f"Enrich prompt for question '{question}'")
        return self.rag_service.enrich_prompt(question, k)
    
    