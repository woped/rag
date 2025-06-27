from chromadb import PersistentClient
from langchain.prompts import ChatPromptTemplate

from ..infrastructure.db.DatabaseAdapter import DatabaseAdapter
from ..infrastructure.db.PDFLoader import PDFLoader
from ..infrastructure.rag.RAGAdapter import RAGAdapter
from ..infrastructure.preprocessing.BpmnQueryExtractor import BpmnQueryExtractor
from ..infrastructure.preprocessing.PnmlQueryExtractor import PnmlQueryExtractor
from ..core.services.DatabaseService import DatabaseService
from ..core.services.RAGService import RAGService
from ..core.services.PDFService import PDFService
from ..core.services.QueryExtractionService import QueryExtractionService
from ..core.ApplicationService import ApplicationService


class ServiceConfig:
    
    def __init__(self):
        # Initialize ChromaDB
        self.client = PersistentClient(path="chroma")
        self.collection = self.client.get_or_create_collection("rag_collection")
        
        # Configure RAG prompt template
        self.rag_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "{prompt}\n\n{additional_llm_instruction}\n\nKontext:\n{context}\n\nAntwort:"
            )
        ])
    
    def create_application_service(self) -> ApplicationService:
        # Infrastructure adapters
        db_adapter = DatabaseAdapter()
        rag_adapter = RAGAdapter(self.rag_prompt)
        pdf_loader = PDFLoader() 
        
        # Extractors for diagram preprocessing
        extractors = [
            BpmnQueryExtractor(),
            PnmlQueryExtractor()
        ]

        # Core services  
        db_service = DatabaseService(db_adapter)
        pdf_service = PDFService(pdf_loader)
        rag_service = RAGService(rag_adapter)
        query_extraction_service = QueryExtractionService(extractors)
        
        # Main application service
        return ApplicationService(
            db_service, 
            rag_service, 
            pdf_service,
            query_extraction_service, 
        )
