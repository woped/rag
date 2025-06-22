from app.core.dtos.DocumentDTO import DocumentDTO
from typing_extensions import List, TypedDict

class State(TypedDict):
    """
    Typed dictionary that represents the state of a RAG (Retrieval-Augmented Generation) operation.
    
    This state object flows through the RAG pipeline for prompt enrichment:
    1. Initial prompt and question are provided
    2. Context documents are retrieved via similarity search
    3. Enriched prompt is returned (generation happens in P2T)
    
    Attributes:
        prompt: The original user prompt/instruction for text generation
        question: The query used for retrieving relevant context documents
        context: List of relevant document chunks found via similarity search
        answer: The final generated response (not used in this service - handled by P2T)
                Reserved for potential future implementation of LLM generation within this service
    """
    prompt: str
    question: str
    context: List[DocumentDTO]
    answer: str