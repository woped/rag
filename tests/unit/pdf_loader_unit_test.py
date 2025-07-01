import pytest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from app.infrastructure.db.PDFLoader import PDFLoader
from app.core.dtos.DocumentDTO import DocumentDTO


class TestPDFLoader:
    
    @pytest.fixture(autouse=True)
    def setup_env(self):
        load_dotenv("app/config/config.env")
    
    @pytest.fixture
    def pdf_loader(self):
        with patch('nltk.download'), patch('nltk.data.find'):
            return PDFLoader()
    
    # Test getting PDF files from a directory
    @patch('os.path.exists')
    @patch('glob.glob')
    def test_get_pdf_files_success(self, mock_glob, mock_exists, pdf_loader):
        mock_exists.return_value = True
        mock_glob.return_value = ["/test/doc1.pdf", "/test/doc2.pdf"]
        
        result = pdf_loader.get_pdf_files("/test")
        
        assert len(result) == 2
        assert "/test/doc1.pdf" in result
        assert "/test/doc2.pdf" in result
        mock_glob.assert_called_once_with("/test/*.pdf")
    
    # Test get_pdf_files with a non-existent directory
    @patch('os.path.exists')
    def test_get_pdf_files_directory_not_exists(self, mock_exists, pdf_loader):
        mock_exists.return_value = False
        
        result = pdf_loader.get_pdf_files("/nonexistent")
        
        assert result == []
    
    # Test successful loading of a PDF file
    @patch('app.infrastructure.db.PDFLoader.PyPDFLoader')
    def test_load_pdf_success(self, mock_pypdf_loader, pdf_loader):
        mock_loader_instance = MagicMock()
        mock_pypdf_loader.return_value = mock_loader_instance
        mock_loader_instance.load.return_value = [
            MagicMock(page_content="Test content", metadata={"source": "test.pdf"})
        ]
        
        result = pdf_loader.load_pdf("/test.pdf")
        
        assert len(result) == 1
        mock_pypdf_loader.assert_called_once_with("/test.pdf")
        mock_loader_instance.load.assert_called_once()
    
    # Test splitting a document into chunks
    def test_split_document_success(self, pdf_loader):
        document = [MagicMock(page_content="Test content", metadata={"source": "test.pdf"})]
        
        with patch.object(pdf_loader.splitter, 'split_documents') as mock_split:
            mock_split.return_value = [
                MagicMock(page_content="Chunk 1", metadata={"source": "test.pdf"}),
                MagicMock(page_content="Chunk 2", metadata={"source": "test.pdf"})
            ]
            
            result = pdf_loader.split_document(document)
            
            assert len(result) == 2
            mock_split.assert_called_once_with(document)
    
    # Test converting chunks to DocumentDTOs
    def test_convert_chunks_to_dtos_success(self, pdf_loader):
        chunks = [
            {'page_content': "Chunk 1", 'metadata': {"source": "test.pdf"}},
            {'page_content': "Chunk 2", 'metadata': {"source": "test.pdf"}}
        ]
        
        result = pdf_loader.convert_chunks_to_dtos(chunks, "test")
        
        assert len(result) == 2
        assert all(isinstance(doc, DocumentDTO) for doc in result)
        assert result[0].id == "test_0"
        assert result[1].id == "test_1"
        assert result[0].text == "Chunk 1"
        assert result[1].text == "Chunk 2"
