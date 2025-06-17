from typing import cast
from app.core.dtos.RagDTO import State
from app.core.dtos.DocumentDTO import DocumentDTO

class RAGService:

    def __init__(self, db_service, llm, prompt):
        self.db = db_service
        self.llm = llm  # Not required for enrich_prompt, only for full RAG pipeline
        self.prompt = prompt

    def enrich_prompt(self, state) -> str:
        """
        Enriches the given question with context from similarity search and the RAG prompt template.
        Verwendet State-DTO mit prompt, question, context.
        """
        context_text = "\n\n".join(doc.text for doc in state["context"])
        messages = self.prompt.format_messages(
            prompt=state["prompt"],
            question=state["question"],
            context=context_text
        )
        return messages[0].content if messages else state["question"]

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
        # Falls state["context"] aus search_docs kommt, ist es eine Liste von (DocumentDTO, distance)
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