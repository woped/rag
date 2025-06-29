import os
import logging
import argparse
from chromadb import PersistentClient
from langchain.prompts import ChatPromptTemplate

from app.infrastructure.db.DatabaseAdapter import DatabaseAdapter
from app.infrastructure.db.PDFLoader import PDFLoader
from app.infrastructure.rag.RAGAdapter import RAGAdapter
from app.infrastructure.preprocessing.BpmnQueryExtractor import BpmnQueryExtractor
from app.infrastructure.preprocessing.PnmlQueryExtractor import PnmlQueryExtractor
from app.core.services.DatabaseService import DatabaseService
from app.core.services.RAGService import RAGService
from app.core.services.PDFService import PDFService
from app.core.services.QueryExtractionService import QueryExtractionService
from app.core.ApplicationService import ApplicationService

class ServiceConfig:
    
    def __init__(self):
        # Configure ChromaDB telemetry first (before any ChromaDB imports)
        os.environ["ANONYMIZED_TELEMETRY"] = "false"
        os.environ["CHROMA_CLIENT_AUTH_PROVIDER"] = ""
        
        # Configure logging
        self.configure_logging()
        
        # Get database path from environment variable
        self.db_path = os.getenv("DB_PATH", "chroma")

        # Configure RAG prompt template
        self.rag_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "{prompt}\n\n{additional_llm_instruction}\n\nKontext:\n{context}\n\nAntwort:"
            )
        ])
    
    # Configure logging based on environment variable and command line arguments
    def configure_logging(self):
        
        # Parse command line arguments for logging level
        parser = argparse.ArgumentParser(description="RAG API Server")
        parser.add_argument(
            "--loglevel",
            default=None,
            choices=["debug", "info", "warning", "error", "critical"],
            help="Set the logging level (overrides LOG_LEVEL env variable)"
        )
        args, _ = parser.parse_known_args()
        
        # Determine logging level: CLI argument > ENV variable > default
        if args.loglevel:
            log_level = args.loglevel
        else:
            log_level = os.getenv("LOG_LEVEL", "warning").lower()
        
        numeric_level = getattr(logging, log_level.upper())
        logging.basicConfig(
            level=numeric_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        logger = logging.getLogger(__name__)
        logger.info("RAG API Server starting up...")
        logger.info(f"Logging level set to: {log_level.upper()} (from {'CLI' if args.loglevel else 'ENV' if os.getenv('LOG_LEVEL') else 'default'})")
        
        # Suppress ChromaDB telemetry logging
        logging.getLogger("chromadb.telemetry").setLevel(logging.CRITICAL)
        logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)
        
        return logger
    
    def create_application_service(self) -> ApplicationService:
        # Infrastructure adapters with database path
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
