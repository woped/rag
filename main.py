# Standard library imports
import os
import argparse
import logging

# Third-party imports
from flask import Flask
from dotenv import load_dotenv
from chromadb import PersistentClient
from langchain.prompts import ChatPromptTemplate

# Load configuration
load_dotenv("config.env")

# Import application components
from app.infrastructure.db.DatabaseAdapter import DatabaseAdapter
from app.infrastructure.rag.RAGAdapter import RAGAdapter
from app.core.services.DatabaseService import DatabaseService
from app.core.services.RAGService import RAGService
from app.core.services.PDFService import PDFService
from app.core.services.PreprocessingService import PreprocessingService
from app.core.ApplicationService import ApplicationService

# Initialize ChromaDB client and collection
client = PersistentClient(path="chroma")
collection = client.get_or_create_collection("rag_collection")

# Configure RAG prompt template
rag_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "{prompt}\n\n{additional_llm_instruction}\n\nKontext:\n{context}\n\nAntwort:"
    )
])

# Initialize services
db_adapter = DatabaseAdapter()
db_service = DatabaseService(db_adapter)
pdf_service = PDFService()
rag_adapter = RAGAdapter(rag_prompt)
rag_service = RAGService(rag_adapter, db_service)
preprocessing_service = PreprocessingService()
application_service = ApplicationService(db_service, rag_service, pdf_service, preprocessing_service, collection)

# Set singleton for REST controller access
ApplicationService.application_service = application_service

# Import REST controller after singletons are initialized
from app.presentation.controller.RESTController import rest_bp

# Create and configure Flask application with REST endpoints
def create_app():
    app = Flask(__name__)
    app.register_blueprint(rest_bp)
    return app

if __name__ == "__main__":
    # Configure logging
    parser = argparse.ArgumentParser(description="RAG API Server")
    parser.add_argument(
        "--loglevel",
        default="debug",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Set the logging level"
    )
    args = parser.parse_args()

    numeric_level = getattr(logging, args.loglevel.upper())
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("RAG API Server starting up...")
    logger.info(f"Logging level set to: {args.loglevel.upper()}")

    # Load and index existing PDF files at startup
    indexing_results = application_service.load_startup_pdfs()
    
    # Start Flask application
    port = int(os.getenv("PORT"))
    host = os.getenv("HOST")
    
    logger.info(f"Starting Flask server on {host}:{port}")
    app = create_app()
    app.run(debug=True, use_reloader=False, port=port, host=host)
