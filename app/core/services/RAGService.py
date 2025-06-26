from typing import cast
from app.core.dtos.RagDTO import State
from app.core.dtos.DocumentDTO import DocumentDTO
import logging

logger = logging.getLogger(__name__)

class RAGService:

    def __init__(self, db_service, llm, prompt):
        self.db = db_service
        self.llm = llm
        self.prompt = prompt

    def enrich_prompt(self, question: str, k: int) -> str:
        logger.info(f"Enriching prompt for question: '{question}' with top {k} documents")

        try:
            results = self.db.search_docs(question, k)
        except Exception as e:
            logger.error(f"Similarity search failed for question '{question}': {e}")
            return question

        docs = [dto for dto, _ in results]
        logger.debug(f"Found {len(docs)} documents for context enrichment")

        context_text = "\n\n".join(doc.text for doc in docs if doc.text.strip())

        if not context_text:
            logger.warning(f"No usable context found for question: '{question}'")

        try:
            messages = self.prompt.format_messages(question=question, context=context_text)
            logger.debug("Prompt formatted successfully")
        except Exception as e:
            logger.error(f"Prompt formatting failed: {e}")
            return question

        enriched = messages[0].content if messages else question
        logger.debug(f"Enriched prompt length: {len(enriched)} characters")
        return enriched

    # --- The following methods are not required for the P2T integration ---
    # --- They are only kept for standalone/full RAG pipeline tests ---

    def retrieve(self, state: State) -> dict:
        """
        [Not used in P2T integration] Retrieves context documents for a question.
        Returns DocumentDTOs in the context.
        """
        query = state["question"]
        results = self.db.search_docs(query, k=3)
        return {"context": results}

    def generate(self, state: State) -> dict:
        """
        [Not used in P2T integration] Generates an answer using the LLM and context.
        Expects context as a list of DocumentDTOs.
        """
        docs = [dto for dto, _ in state["context"]] if state["context"] and isinstance(state["context"][0], tuple) else state["context"]
        context_text = "\n\n".join(doc.text for doc in docs)
        messages = self.prompt.format_messages(question=state["question"], context=context_text)
        response = self.llm.invoke(messages)
        return {"answer": response.content}

    def invoke(self, state_dict: dict) -> State:
        """
        [Not used in P2T integration] Full RAG pipeline: retrieve context and generate answer.
        """
        state = cast(State, state_dict)
        state.update(self.retrieve(state))
        state.update(self.generate(state))
        return state