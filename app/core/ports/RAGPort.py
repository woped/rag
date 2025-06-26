from abc import ABC, abstractmethod

class RAGPort(ABC):
    """
    Abstract port for RAG (Retrieval-Augmented Generation) operations.
    
    NOTE: This interface is currently not used in the active implementation.
    The current architecture delegates LLM generation to external services (P2T).
    
    This port is reserved for potential future implementations where the RAG service
    would handle both retrieval AND generation internally, making direct LLM calls
    instead of returning enriched prompts to external services.
    
    Current flow: RAG service → enriched prompt → P2T service → LLM generation
    """

    @abstractmethod
    def retrieve(self):
        """Retrieve relevant documents based on query."""
        pass

    @abstractmethod
    def generate(self):
        """Generate answer using retrieved context and LLM."""
        pass