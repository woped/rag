# Standard library imports
import os
import logging

# Third-party imports
from flask import Flask
from dotenv import load_dotenv

# Load configuration
load_dotenv("app/config/config.env")

# Import service configuration
from app.config.ServiceConfig import ServiceConfig
from app.core.ApplicationService import ApplicationService

# Create all services via ServiceConfig (includes logging setup)
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

    # Load and index existing PDF files at startup
    application_service.load_startup_pdfs()
    
    # Start Flask application
    port = int(os.getenv("PORT"))
    host = os.getenv("HOST")
    
    # Create the Flask app and run it
    app = create_app()
    app.run(debug=True, use_reloader=False, port=port, host=host)
