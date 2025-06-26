from typing import List, Tuple
from app.core.ports.RAGPort import RAGPort
from app.core.dtos.RagDTO import State
from app.core.dtos.DocumentDTO import DocumentDTO
from app.infrastructure.rag.langchain.LangchainClient import LangchainClient
import logging
import os

logger = logging.getLogger(__name__)

class RAGAdapter(RAGPort):
    """
    Infrastructure adapter implementing RAG operations using LangChain and ChromaDB.
    
    This adapter provides the technical implementation of RAG functionality, integrating with
    vector databases and embedding models through the LangchainClient. Handles the low-level
    operations of similarity search, document retrieval, and prompt template formatting.
    
    Key technical operations: vector similarity search via ChromaDB, document embedding and
    retrieval, prompt template processing, and context injection. Serves as the bridge between
    the domain layer's RAG abstractions and the actual vector database infrastructure.
    """
    
    def __init__(self, prompt_template=None):
        self.langchain_client = LangchainClient()
        self.prompt_template = prompt_template
        logger.info("RAGAdapter initialized")

    # Search documents using vector similarity
    def retrieve(self, query: str) -> List[Tuple[DocumentDTO, float]]:
        logger.info(f"Searching documents for: {query[:50]}...")
        results = self.langchain_client.search_docs(query)
        logger.info(f"Found {len(results)} documents")
        return results

    # Add context documents to prompt
    def augment(self, state: State) -> str:
        logger.info("Adding context to prompt")
        
        # Format context documents
        context_text = ""
        if state.get("context"):
            context_blocks = []
            for i, doc in enumerate(state["context"], 1):
                context_blocks.append(f"[Document {i}]\n{doc.text}")
            context_text = "\n\n".join(context_blocks)
        
         # Get additional instruction from environment
        additional_llm_instruction = os.getenv("ADDITIONAL_LLM_INSTRUCTION")
        
        # Use template or simple format
        if self.prompt_template:
            try:
                enriched_prompt = self.prompt_template.format(
                    prompt=state["prompt"],
                    additional_llm_instruction=additional_llm_instruction,
                    context=context_text
                )
            except Exception as e:
                logger.warning(f"Template failed: {e}")
                enriched_prompt = f"{state['prompt']}\n\n{additional_llm_instruction}\n\nContext:\n{context_text}"
        else:
            enriched_prompt = f"{state['prompt']}\n\n{additional_llm_instruction}\n\nContext:\n{context_text}"

        logger.info("Prompt augmentation completed")
        return enriched_prompt

    # Generate response (placeholder - not used)
    def generate(self, prompt: str, context: List[DocumentDTO]) -> str:
        logger.info("Generate called - handled by external P2T service")
        return prompt
