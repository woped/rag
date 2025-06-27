# Standard library imports
import os
import argparse
import logging

# Third-party imports
from flask import Flask
from dotenv import load_dotenv

# Load configuration
load_dotenv("config.env")

# Import service configuration
from app.config.ServiceConfig import ServiceConfig
from app.core.ApplicationService import ApplicationService

# Create all services via ServiceConfig
service_config = ServiceConfig()
application_service = service_config.create_application_service()

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
    application_service.load_startup_pdfs()
    
    # Start Flask application
    port = int(os.getenv("PORT"))
    host = os.getenv("HOST")
    
    logger.info(f"Starting Flask server on {host}:{port}")
    app = create_app()
    app.run(debug=True, use_reloader=False, port=port, host=host)
