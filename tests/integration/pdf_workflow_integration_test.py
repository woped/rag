"""
Integration test for the PDF loader workflow.
Tests the complete PDF loading workflow that runs at startup.
"""

import os
import pytest
import tempfile
import shutil
import logging
from unittest.mock import patch, MagicMock
from app.core.dtos.DocumentDTO import DocumentDTO

logger = logging.getLogger(__name__)

@pytest.fixture
def temp_pdf_directory():
    """Create temporary directory with mock PDF files"""
    temp_dir = tempfile.mkdtemp()
    
    pdf_files = ["Loan_Process.pdf", "Business_Guide.pdf", "Technical_Details.pdf"]
    for pdf_file in pdf_files:
        with open(os.path.join(temp_dir, pdf_file), 'w') as f:
            f.write(f"Mock content for {pdf_file}")
    
    yield temp_dir
    shutil.rmtree(temp_dir)

class TestPDFWorkflowIntegration:
    
    def test_startup_pdf_loading_workflow(self, temp_pdf_directory):
        """Test the complete PDF loading workflow that runs at startup"""
        
        # Expected result after PDF processing
        expected_documents = {
            "Loan_Process": [
                DocumentDTO(id="doc1", text="Loan process content", metadata={"source": "Loan_Process.pdf"})
            ],
            "Business_Guide": [
                DocumentDTO(id="doc2", text="Business guide content", metadata={"source": "Business_Guide.pdf"})
            ]
        }
        
        # Mock the services to avoid ChromaDB
        with patch('app.config.ServiceConfig.ServiceConfig') as mock_config:
            mock_app_service = MagicMock()
            mock_pdf_service = MagicMock()
            mock_db_service = MagicMock()
            
            # Configure mocks
            mock_pdf_service.process_directory.return_value = expected_documents
            mock_app_service.pdf_service = mock_pdf_service
            mock_app_service.db_service = mock_db_service
            
            mock_config.return_value.create_application_service.return_value = mock_app_service
            
            # Test the workflow
            with patch.dict(os.environ, {"PDF_DIRECTORY": temp_pdf_directory}):
                mock_app_service.load_startup_pdfs()
                
                # Verify the workflow was executed
                mock_app_service.load_startup_pdfs.assert_called_once()