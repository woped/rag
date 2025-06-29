import pytest
from unittest.mock import MagicMock
from app.core.services.PDFService import PDFService
from app.core.dtos.DocumentDTO import DocumentDTO


class TestPDFService:
    
    @pytest.fixture
    def mock_pdf_loader(self):
        return MagicMock()
    
    @pytest.fixture
    def pdf_service(self, mock_pdf_loader):
        return PDFService(mock_pdf_loader)
    
    # Test process_directory method with a valid directory
    def test_process_directory_success(self, pdf_service, mock_pdf_loader):
        documents = [
            DocumentDTO(id="doc1_0", text="Chunk 1", metadata={"source": "doc1.pdf"}),
            DocumentDTO(id="doc1_1", text="Chunk 2", metadata={"source": "doc1.pdf"}),
            DocumentDTO(id="doc2_0", text="Chunk 1", metadata={"source": "doc2.pdf"})
        ]
        
        # Mock the load_directory method (which delegates to pdf_loader)
        pdf_service.load_directory = MagicMock(return_value={
            "successful": 2, "failed": 0, "errors": [], "documents": documents
        })
        
        result = pdf_service.process_directory("/test/dir")
        
        assert len(result) == 2
        assert "doc1" in result and "doc2" in result
        assert len(result["doc1"]) == 2
        assert len(result["doc2"]) == 1
    
    # Test process_directory with an empty directory
    def test_process_directory_no_documents_raises_error(self, pdf_service):
        pdf_service.load_directory = MagicMock(return_value={
            "successful": 0, "failed": 0, "errors": [], "documents": []
        })
        
        with pytest.raises(RuntimeError, match="No documents could be processed"):
            pdf_service.process_directory("/empty/dir")
    
    # Test load_directory with a valid directory
    def test_load_and_convert_pdf_success(self, pdf_service, mock_pdf_loader):
        mock_pdf_loader.load_pdf.return_value = "PDF content"
        mock_pdf_loader.split_document.return_value = ["chunk1", "chunk2"]
        mock_pdf_loader.convert_chunks_to_dtos.return_value = [
            DocumentDTO(id="test_0", text="chunk1", metadata={}),
            DocumentDTO(id="test_1", text="chunk2", metadata={})
        ]
        
        result = pdf_service.load_and_convert_pdf("/test.pdf", "test")
        
        assert len(result) == 2
        assert result[0].id == "test_0"
        assert result[1].id == "test_1"
        mock_pdf_loader.load_pdf.assert_called_once_with("/test.pdf")
        mock_pdf_loader.split_document.assert_called_once_with("PDF content")
        mock_pdf_loader.convert_chunks_to_dtos.assert_called_once_with(["chunk1", "chunk2"], "test")
    
    # Test load_and_convert_pdf raises ValueError for empty file path
    def test_load_and_convert_pdf_empty_file_path(self, pdf_service):
        with pytest.raises(ValueError, match="File path cannot be empty"):
            pdf_service.load_and_convert_pdf("", "test")
    
    # Test load_and_convert_pdf raises ValueError for empty prefix
    def test_load_and_convert_pdf_empty_prefix(self, pdf_service):
        with pytest.raises(ValueError, match="Prefix cannot be empty"):
            pdf_service.load_and_convert_pdf("/test.pdf", "")
    
    # Test group_by_prefix with normal documents
    def test_group_by_prefix_normal_documents(self, pdf_service):
        documents = [
            DocumentDTO(id="loan_application_process_0", text="Content 1", metadata={}),
            DocumentDTO(id="loan_application_process_1", text="Content 2", metadata={}),
            DocumentDTO(id="credit_check_workflow_0", text="Content 3", metadata={})
        ]
        
        result = pdf_service.group_by_prefix(documents)
        
        assert len(result) == 2
        assert "loan_application_process" in result
        assert "credit_check_workflow" in result
        assert len(result["loan_application_process"]) == 2
        assert len(result["credit_check_workflow"]) == 1
    
    # Test group_by_prefix with empty list
    def test_group_by_prefix_empty_list(self, pdf_service):
        result = pdf_service.group_by_prefix([])
        assert result == {}