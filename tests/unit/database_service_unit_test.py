import pytest
from unittest.mock import MagicMock
from app.core.services.DatabaseService import DatabaseService
from app.core.dtos.DocumentDTO import DocumentDTO


class TestDatabaseService:

    @pytest.fixture
    def mock_database_port(self):
        return MagicMock()
    
    @pytest.fixture
    def database_service(self, mock_database_port):
        return DatabaseService(mock_database_port)

    # === Add Documents Tests ===
    
    # Test successful document addition
    def test_add_docs_success(self, database_service, mock_database_port):
        """Test successful document addition"""
        documents = [
            DocumentDTO(id="doc1", text="Test content 1", metadata={}),
            DocumentDTO(id="doc2", text="Test content 2", metadata={})
        ]
        
        database_service.add_docs(documents)
        
        mock_database_port.add_docs.assert_called_once_with(documents)
    
    # Test that invalid documents are filtered out
    def test_add_docs_filters_invalid_documents(self, database_service, mock_database_port):
        documents = [
            DocumentDTO(id="doc1", text="Valid content", metadata={}),
            DocumentDTO(id="", text="No ID", metadata={}),  # Invalid: no ID
            DocumentDTO(id="doc3", text="", metadata={}),   # Invalid: no text
            DocumentDTO(id=None, text="No ID", metadata={}),  # Invalid: None ID
            DocumentDTO(id="doc4", text="Valid content 2", metadata={})
        ]
        
        database_service.add_docs(documents)
        
        # Should only add valid documents
        call_args = mock_database_port.add_docs.call_args[0][0]
        assert len(call_args) == 2
        assert call_args[0].id == "doc1"
        assert call_args[1].id == "doc4"
    
    # Test adding empty list of documents
    def test_add_docs_empty_list(self, database_service, mock_database_port):
        database_service.add_docs([])
        
        mock_database_port.add_docs.assert_not_called()
    
    # Test adding documents with all invalid entries
    def test_add_docs_all_invalid(self, database_service, mock_database_port):
        documents = [
            DocumentDTO(id="", text="", metadata={}),
            DocumentDTO(id=None, text=None, metadata={})
        ]
        
        database_service.add_docs(documents)
        
        mock_database_port.add_docs.assert_not_called()
    
    # === Get Document Tests ===
    
    # Test successful document retrieval by ID
    def test_get_doc_by_id_success(self, database_service, mock_database_port):
        expected_doc = DocumentDTO(id="doc1", text="Test content", metadata={})
        mock_database_port.get_doc_by_id.return_value = expected_doc
        
        result = database_service.get_doc_by_id("doc1")
        
        assert result == expected_doc
        mock_database_port.get_doc_by_id.assert_called_once_with("doc1")
    
    # Test retrieval with empty ID returns None
    def test_get_doc_by_id_empty_id(self, database_service, mock_database_port):
        result = database_service.get_doc_by_id("")
        
        assert result is None
        mock_database_port.get_doc_by_id.assert_not_called()
    
    # Test retrieval with None ID returns None
    def test_get_doc_by_id_none_id(self, database_service, mock_database_port):
        result = database_service.get_doc_by_id(None)
        
        assert result is None
        mock_database_port.get_doc_by_id.assert_not_called()
    
    # Test retrieval when document ID does not exist
    def test_get_doc_by_id_not_found(self, database_service, mock_database_port):
        mock_database_port.get_doc_by_id.return_value = None
        
        result = database_service.get_doc_by_id("nonexistent")
        
        assert result is None
        mock_database_port.get_doc_by_id.assert_called_once_with("nonexistent")
    
    # === Update Document Tests ===
    
    # Test successful document update
    def test_update_doc_success(self, database_service, mock_database_port):
        document = DocumentDTO(id="doc1", text="Updated content", metadata={})
        
        database_service.update_doc(document)
        
        mock_database_port.update_doc.assert_called_once_with(document)
    
    # === Delete Document Tests ===
    
    # Test successful document deletion
    def test_delete_doc_success(self, database_service, mock_database_port):
        database_service.delete_doc("doc1")
        
        mock_database_port.delete_doc.assert_called_once_with("doc1")
    
    # === Delete by Prefix Tests ===
    
    # Test successful deletion by prefix
    def test_delete_by_prefix_success(self, database_service, mock_database_port):
        database_service.delete_by_prefix("test_prefix")
        
        mock_database_port.delete_by_prefix.assert_called_once_with("test_prefix")
    
    # Test that empty prefix raises ValueError
    def test_delete_by_prefix_empty_raises_error(self, database_service, mock_database_port):
        with pytest.raises(ValueError, match="Prefix cannot be empty"):
            database_service.delete_by_prefix("")
        
        mock_database_port.delete_by_prefix.assert_not_called()
    
    # Test that None prefix raises ValueError
    def test_delete_by_prefix_none_raises_error(self, database_service, mock_database_port):
        with pytest.raises(ValueError, match="Prefix cannot be empty"):
            database_service.delete_by_prefix(None)
        
        mock_database_port.delete_by_prefix.assert_not_called()
    
    # === Clear All Tests ===
    
    # Test successful clear operation
    def test_clear_success(self, database_service, mock_database_port):
        database_service.clear()
        
        mock_database_port.clear.assert_called_once()
