from abc import ABC, abstractmethod
from typing import List
from app.core.dtos.DocumentDTO import DocumentDTO

"""
    Abstract interface for PDF loading and file operations with core functions:
    load_and_split (PDF content extraction and chunking),
    convert_chunks_to_dtos (chunk to DTO conversion),
    and get_pdf_files (directory file discovery).
"""
class PDFLoaderPort(ABC):

    @abstractmethod
    def load_and_split(self, file_path: str) -> List[dict]:
        pass
    
    @abstractmethod
    def convert_chunks_to_dtos(self, chunks: List[dict], prefix: str) -> List['DocumentDTO']:
        pass
    
    @abstractmethod
    def get_pdf_files(self, directory: str) -> List[str]:
        pass
