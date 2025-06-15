from typing import cast
from langchain_core.documents import Document
from app.core.dtos.RagDTO import State

class RAGService:

    def __init__(self, db_service, llm, prompt):
        self.db = db_service
        self.llm = llm
        self.prompt = prompt

    def retrieve(self, state: State) -> dict:
        query = state["question"]
        results = self.db.search_docs(query, k=3)
        documents = [Document(page_content=doc) for doc in results]
        return {"context": documents}

    def generate(self, state: State) -> dict:
        context_text = "\n\n".join(doc.page_content for doc in state["context"])
        messages = self.prompt.format_messages(question=state["question"], context=context_text)
        response = self.llm.invoke(messages)
        return {"answer": response.content}

    def invoke(self, state_dict: dict) -> State:
        state = cast(State, state_dict)
        state.update(self.retrieve(state))
        state.update(self.generate(state))
        return state
