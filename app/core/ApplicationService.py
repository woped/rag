from app.core.dtos.DocumentDTO import DocumentDTO

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
            print(f"-> Deleted {len(ids_to_delete)} old chunks with prefix '{prefix}'")
        else:
            print(f"-> No old chunks with prefix '{prefix}' found")

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

    def answer_with_rag(self, state) -> str:
        """Returns an enriched prompt or a full RAG answer using State-DTO."""
        return self.rag_service.enrich_prompt(state)