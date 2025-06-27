from abc import ABC, abstractmethod
from typing import List


class PDFLoaderPort(ABC):
    
    @abstractmethod
    def load_and_split(self, file_path: str) -> List[dict]:
        pass
    
    @abstractmethod
    def get_pdf_files(self, directory: str) -> List[str]:
        pass
