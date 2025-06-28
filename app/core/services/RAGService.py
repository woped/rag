from typing import List, Tuple
from app.core.dtos.RagDTO import State
from app.core.dtos.DocumentDTO import DocumentDTO
from app.core.ports.RAGPort import RAGPort
import logging

logger = logging.getLogger(__name__)

class RAGService:
    """
    Service for Retrieval-Augmented Generation operations in the WoPeD system.
    
    This service orchestrates the core RAG operations: document retrieval using semantic similarity
    search and prompt augmentation with retrieved context. Acts as a domain layer service that
    handles business validation and error handling while delegating technical operations to the
    RAGAdapter infrastructure component. Provides a clean abstraction for complex RAG workflows.
    
    Key operations: semantic document retrieval, context-aware prompt augmentation, and business
    rule validation. Integrates with the database service for document management and ensures
    proper error handling throughout the RAG pipeline.
    """

    def __init__(self, rag_adapter: RAGPort):
        self.rag_adapter = rag_adapter
        logger.info("[RAGService] initialized")

    # Retrieve documents using similarity search
    def retrieve(self, query: str) -> List[Tuple[DocumentDTO, float]]:
        logger.debug("[RAGService] delegating search to adapter")
        
        if not query.strip():
            logger.warning("Empty query provided")
            return []
        
        return self.rag_adapter.retrieve(query)

    # Augment prompt with context documents
    def augment(self, state: State) -> str:
        logger.debug("[RAGService] delegating augmentation to adapter")
        
        if not state.get("prompt"):
            raise ValueError("Prompt is required")
        
        if not state.get("context"):
            logger.warning("No context provided, returning original prompt")
            return state["prompt"]
        
        return self.rag_adapter.augment(state)

    # Generate response (placeholder - not used)
    def generate(self, prompt: str, context: List[DocumentDTO]) -> str:
        logger.info("Generate called - handled by external P2T service")
        return prompt
