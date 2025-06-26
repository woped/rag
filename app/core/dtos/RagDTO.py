from app.core.dtos.DocumentDTO import DocumentDTO
from typing_extensions import List, TypedDict

class State(TypedDict):
    """
    RAG pipeline state for prompt enrichment operations.
    
    Attributes:
        prompt: Original user prompt for text generation
        question: Query for context document retrieval
        context: Retrieved document chunks for context
        answer: Generated response (reserved for future use)
    """
    prompt: str
    question: str
    context: List[DocumentDTO]
    answer: str