from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class DocumentDTO:
    """
    Data Transfer Object for document handling in the RAG system.
    
    Represents a document chunk with metadata that can be stored in vector databases
    and used for similarity search operations.
    
    Attributes:
        id: Unique identifier for the document chunk (optional)
        text: The actual text content of the document chunk
        metadata: Additional information about the document (file path, page number, etc.)
    """
    id: Optional[str]
    text: str
    metadata: Optional[Dict] = None
