# Standard library imports
import os
import glob

# imports for logging
import argparse
import logging

# Third-party imports
from flask import Flask
from dotenv import load_dotenv
from chromadb import PersistentClient
from langchain import hub

# Project-specific imports
from app.presentation.controller.RESTController import rest_bp
from app.infrastructure.db.PDFLoader import PDFLoader
from app.core.services.RAGService import RAGService
from app.core.ApplicationService import ApplicationService
from app.core.services.DatabaseService import DatabaseService
from app.infrastructure.db.DatabaseAdapter import DatabaseAdapter
import app.core.services.RAGService 
import app.core.services.DatabaseService

# Initialize ChromaDB and PDF loader
client = PersistentClient(path="chroma")
collection = client.get_or_create_collection("rag_collection")
pdf_loader = PDFLoader(collection)
db_service = DatabaseService(DatabaseAdapter())

# Load environment variables from .env file
load_dotenv()

# Load RAG prompt from LangChain Hub
rag_prompt = hub.pull("rlm/rag-prompt")

# Initialize RAGService (llm=None for prompt enrichment only)
rag_service = RAGService(db_service, None, rag_prompt)
application_service = ApplicationService(pdf_loader, db_service, rag_service, collection)

# Provide singletons for use in RESTController and other modules
app.core.services.RAGService.rag_service = rag_service
app.core.ApplicationService.application_service = application_service
app.core.services.DatabaseService.db_service = db_service

def create_app():
    app = Flask(__name__)
    app.register_blueprint(rest_bp)
    return app

if __name__ == "__main__":
    # ---------------------------------------
    # Set up argument parser for log level
    # ---------------------------------------
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--loglevel",
        default="warning",
        help="Set the logging level (debug, info, warning, error, critical)"
    )
    args = parser.parse_args()

    numeric_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"invalid loglevel: {args.loglevel}, valid input: debug, info, warning, error or critical")

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logging.info("Logging successfully initialised")

    # ---------------------------------------
    # load pdf files
    # ---------------------------------------
    for pdf_path in glob.glob("PDF/*.pdf"):
        logging.info(f"--> Loading: {pdf_path}")
        filename_prefix = os.path.basename(pdf_path).replace(".pdf", "")
        application_service.upload_and_index_pdf(pdf_path, filename_prefix)

    # ---------------------------------------
    # start FLASK App
    # ---------------------------------------
    port = int(os.getenv("PORT", 5000))
    app = create_app()
    app.run(debug=True, use_reloader=False, port=port)
