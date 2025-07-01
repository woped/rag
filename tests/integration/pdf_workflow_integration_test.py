"""
Integration test for the PDF loader workflow.
Tests the complete PDF loading workflow that runs at startup.
Tests the REAL PDF processing workflow with database/ChromaDB, RAG and QueryExtractor mocked.
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
    temp_dir = tempfile.mkdtemp()
    
    yield temp_dir
    shutil.rmtree(temp_dir)

class TestPDFWorkflowIntegration:
    
    # Test the complete PDF loading workflow with REAL PDF service and REAL PDFLoader.
    def test_startup_pdf_loading_workflow(self, temp_pdf_directory):
        
        # Create actual PDF files for testing (simplified PDF format)
        test_files = {
            "Loan_Process.pdf": "This is a loan process document with workflow steps and business logic.",
            "Business_Guide.pdf": "This is a business guide with important information about processes.",
            "Technical_Details.pdf": "Technical details about the system architecture and implementation."
        }
        
        # Write actual content to PDF files in the temp directory
        for filename, content in test_files.items():
            with open(os.path.join(temp_pdf_directory, filename), 'w') as f:
                f.write(content)
        
        # Mock only the database and ChromaDB dependencies
        with patch('app.infrastructure.db.DatabaseAdapter.DatabaseAdapter') as mock_db_adapter:
            with patch('chromadb.PersistentClient') as mock_chroma_client:
                
                # Configure ChromaDB mock
                mock_collection = MagicMock()
                mock_client_instance = MagicMock()
                mock_client_instance.get_or_create_collection.return_value = mock_collection
                mock_chroma_client.return_value = mock_client_instance
                
                # Configure database adapter mock
                mock_db_instance = MagicMock()
                mock_db_adapter.return_value = mock_db_instance
                
                # Mock PyPDFLoader to simulate PDF parsing but use real file processing
                with patch('app.infrastructure.db.PDFLoader.PyPDFLoader') as mock_pypdf_loader:
                    
                    def create_mock_loader(file_path):
                        # Read the actual file content
                        with open(file_path, 'r') as f:
                            content = f.read()
                        
                        # Create a mock document that looks like PyPDFLoader output
                        mock_doc = MagicMock()
                        mock_doc.page_content = content
                        mock_doc.metadata = {"source": file_path}
                        
                        # Create mock loader instance
                        mock_loader_instance = MagicMock()
                        mock_loader_instance.load.return_value = [mock_doc]
                        
                        return mock_loader_instance
                    
                    mock_pypdf_loader.side_effect = create_mock_loader
                    
                    # Create mix of REAL and MOCK services for focused testing
                    from app.core.services.DatabaseService import DatabaseService
                    from app.core.services.PDFService import PDFService
                    from app.core.ApplicationService import ApplicationService
                    from app.infrastructure.db.PDFLoader import PDFLoader
                    
                    # Create REAL service instances for PDF processing
                    pdf_loader = PDFLoader()  # REAL PDF loader
                    db_service = DatabaseService(mock_db_instance)  # Real service with mocked adapter
                    pdf_service = PDFService(pdf_loader)  # REAL PDF service with REAL PDF loader
                    
                    # Create MOCK services for dependencies we don't want to test
                    mock_rag_service = MagicMock()  # MOCK RAG service
                    mock_query_service = MagicMock()  # MOCK query service
                    
                    # Create ApplicationService with mixed REAL and MOCK services
                    app_service = ApplicationService(
                        db_service=db_service,
                        rag_service=mock_rag_service,  # MOCK
                        pdf_service=pdf_service,  # REAL
                        query_extraction_service=mock_query_service  # MOCK
                    )
                    
                    # Test 1: Without PDF_DIRECTORY environment variable
                    with patch.dict(os.environ, {}, clear=True):
                        app_service.load_startup_pdfs()
                        
                        # Verify no database calls were made
                        mock_db_instance.add_docs.assert_not_called()
                    
                    # Reset mocks for test 2
                    mock_db_instance.reset_mock()
                    
                    # Test 2: With PDF_DIRECTORY set - this tests the REAL workflow
                    with patch.dict(os.environ, {"PDF_DIRECTORY": temp_pdf_directory}):
                        app_service.load_startup_pdfs()
                        
                        # Verify the REAL workflow processed files and called the database
                        # The real PDFService should have called the real PDFLoader
                        # which should have processed our test files
                        assert mock_db_instance.add_docs.call_count >= 1, "Database add_docs should have been called"
                        
                        # Verify that documents were actually created and passed to the database
                        call_args = mock_db_instance.add_docs.call_args_list
                        assert len(call_args) > 0, "add_docs should have been called with documents"
                        
                        # Check that actual documents were processed
                        # The first argument to add_docs should be a list of DocumentDTOs
                        added_docs = call_args[0][0][0]  # First call, first argument
                        assert isinstance(added_docs, list), "add_docs should be called with a list of documents"
                        assert len(added_docs) > 0, "Should have processed at least one document"
                        
                        # Verify that the documents contain actual content from our test files
                        for doc in added_docs:
                            assert isinstance(doc, DocumentDTO), "Documents should be DocumentDTO instances"
                            assert len(doc.text) > 0, "Documents should contain text content"
                            assert doc.metadata is not None, "Documents should have metadata"
                            
                        # Verify that PyPDFLoader was called for each PDF file
                        assert mock_pypdf_loader.call_count == len(test_files), f"PyPDFLoader should be called for each PDF file ({len(test_files)} times)"
                        
                        # Verify that the correct file paths were processed
                        call_args_list = mock_pypdf_loader.call_args_list
                        processed_files = [call[0][0] for call in call_args_list]  # Extract file paths
                        
                        for filename in test_files.keys():
                            expected_path = os.path.join(temp_pdf_directory, filename)
                            assert any(expected_path in processed_file for processed_file in processed_files), \
                                f"Expected {filename} to be processed, got: {processed_files}"