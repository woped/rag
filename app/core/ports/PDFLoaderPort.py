from abc import ABC, abstractmethod
from typing import List
from app.core.dtos.DocumentDTO import DocumentDTO

"""
    Abstract interface for PDF loading and file operations with core functions:
    get_pdf_files (directory file discovery),
    load_pdf (PDF content extraction),
    split_documents (chunking),
    and convert_chunks_to_dtos (chunk to DTO conversion).
"""
class PDFLoaderPort(ABC):

    @abstractmethod
    def get_pdf_files(self, directory: str) -> List[str]:
        pass

    @abstractmethod
    def load_pdf(self, file_path: str):
        pass

    @abstractmethod
    def split_document(self, document) -> List[dict]:
        pass
    
    @abstractmethod
    def convert_chunks_to_dtos(self, chunks: List[dict], prefix: str) -> List['DocumentDTO']:
        pass
