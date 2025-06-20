from app.core.dtos.DocumentDTO import DocumentDTO
from typing_extensions import List, TypedDict

class State(TypedDict):
    prompt: str
    question: str
    context: List[DocumentDTO]
    answer: str