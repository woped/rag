"""
    DatabaseService provides high-level access to vector database operations
    for the application core. It delegates all data-related functionality
    to an implementation of the DatabasePort interface.

    This service acts as the application's main entry point for storing,
    retrieving, updating, deleting, and searching documents.
"""
from app.core.ports.DatabasePort import DatabasePort
from app.core.dtos.DocumentDTO import DocumentDTO

class DatabaseService:
    def __init__(self, database_port: DatabasePort):
        self.db = database_port

    def add_docs(self, documents: list[DocumentDTO]):
        self.db.add_docs(documents)

    def get_doc_by_id(self, id: str):
        return self.db.get_doc_by_id(id)

    def search_docs(self, query: str, k: int):
        return self.db.search_docs(query, k)

    def update_doc(self, document: DocumentDTO):
        self.db.update_doc(document)

    def delete_doc(self, id: str):
        self.db.delete_doc(id)
    
    def clear(self):
        self.db.clear()

