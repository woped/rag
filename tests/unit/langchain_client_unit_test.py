import pytest
from unittest.mock import MagicMock, patch
import os
from app.infrastructure.rag.langchain.LangchainClient import LangchainClient
from app.core.dtos.DocumentDTO import DocumentDTO


class TestLangchainClient:
    
    @pytest.fixture
    def mock_embeddings(self):
        embeddings = MagicMock()
        embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3]]
        return embeddings
    
    @pytest.fixture
    def mock_vectorstore(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_collection(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        return client
    
    @pytest.fixture
    def langchain_client(self, mock_embeddings, mock_vectorstore, mock_collection, mock_client):
        with patch.dict(os.environ, {
            "THRESHOLD": "2",
            "RESULTS_COUNT": "5", 
            "EMBEDDING_MODEL": "test-model"
        }):
            with patch('app.infrastructure.rag.langchain.LangchainClient.HuggingFaceEmbeddings') as mock_hf:
                with patch('app.infrastructure.rag.langchain.LangchainClient.Chroma') as mock_chroma:
                    with patch('app.infrastructure.rag.langchain.LangchainClient.PersistentClient') as mock_persistent:
                        mock_hf.return_value = mock_embeddings
                        mock_chroma.return_value = mock_vectorstore
                        mock_persistent.return_value = mock_client
                        mock_client.get_or_create_collection.return_value = mock_collection
                        
                        client = LangchainClient("test_chroma")
                        client.embeddings = mock_embeddings
                        client.vectorstore = mock_vectorstore
                        client.collection = mock_collection
                        client.client = mock_client
                        return client
    
    # === Add Documents Tests ===
    
    # Test successful document addition with embeddings
    def test_add_docs_success(self, langchain_client, mock_collection, mock_embeddings):
        texts = ["Document 1", "Document 2"]
        metadatas = [{"source": "test1"}, {"source": "test2"}]
        ids = ["doc1", "doc2"]
        
        langchain_client.add_docs(texts, metadatas, ids)
        
        # Verify embeddings were called for each document
        assert mock_embeddings.embed_documents.call_count == 2
        # Verify collection.add was called for each document
        assert mock_collection.add.call_count == 2
    
    # Test document addition with default metadata and IDs
    def test_add_docs_default_metadata_and_ids(self, langchain_client, mock_collection):
        texts = ["Document 1", "Document 2"]
        
        langchain_client.add_docs(texts)
        
        # Should generate default metadata and IDs
        assert mock_collection.add.call_count == 2
        
        # Check first call args
        first_call = mock_collection.add.call_args_list[0]
        assert first_call[1]["metadatas"] == [{"source": "unknown"}]
        assert first_call[1]["ids"] == ["0"]
    
    # Test that empty metadata gets replaced with default
    def test_add_docs_empty_metadata_gets_default(self, langchain_client, mock_collection):
        texts = ["Document 1"]
        metadatas = [{}]  # Empty metadata
        
        langchain_client.add_docs(texts, metadatas)
        
        call_args = mock_collection.add.call_args[1]
        assert call_args["metadatas"] == [{"source": "default"}] 
    
    # === Get Document by ID Tests ===
    
    # Test successful document retrieval by ID
    def test_get_doc_by_id_success(self, langchain_client, mock_collection):
        """Test successful document retrieval by ID"""
        mock_collection.get.return_value = {
            "ids": ["doc1"],
            "documents": ["Test content"],
            "metadatas": [{"source": "test"}]
        }
        
        result = langchain_client.get_doc_by_id("doc1")
        
        assert isinstance(result, DocumentDTO)
        assert result.id == "doc1"
        assert result.text == "Test content"
        assert result.metadata == {"source": "test"}
        mock_collection.get.assert_called_once_with(ids=["doc1"])
   
    # Test document retrieval when ID not found
    def test_get_doc_by_id_not_found(self, langchain_client, mock_collection):
        mock_collection.get.return_value = {
            "ids": [],
            "documents": [],
            "metadatas": []
        }
        
        result = langchain_client.get_doc_by_id("nonexistent")
        
        assert result is None
    
    # === Search Documents Tests ===
    
    # Test successful document search
    def test_search_docs_success(self, langchain_client, mock_vectorstore):
        # Mock document objects with necessary attributes
        doc1 = MagicMock()
        doc1.id = "doc1"
        doc1.page_content = "Content 1"
        doc1.metadata = {"source": "test1"}
        
        doc2 = MagicMock()
        doc2.id = "doc2" 
        doc2.page_content = "Content 2"
        doc2.metadata = {"source": "test2"}
        
        mock_vectorstore.similarity_search_with_score.return_value = [
            (doc1, 0.3),  # Below threshold
            (doc2, 2.5)   # Above threshold
        ]
        
        results = langchain_client.search_docs("test query")
        
        # Should only return documents below threshold
        assert len(results) == 1
        doc_dto, distance = results[0]
        assert isinstance(doc_dto, DocumentDTO)
        assert doc_dto.id == "doc1"
        assert doc_dto.text == "Content 1"
        assert distance == 0.3
    
    # Test search with no results below threshold
    def test_search_docs_no_results_below_threshold(self, langchain_client, mock_vectorstore):
        doc1 = MagicMock()
        doc1.id = "doc1"
        doc1.page_content = "Content 1"
        doc1.metadata = {"source": "test1"}
        
        mock_vectorstore.similarity_search_with_score.return_value = [
            (doc1, 2.5) 
        ]
        
        results = langchain_client.search_docs("test query")
        
        assert len(results) == 0
    
    # Test search with documents missing some attributes
    def test_search_docs_handles_missing_attributes(self, langchain_client, mock_vectorstore):
        doc1 = MagicMock()
        # Missing id attribute
        doc1.page_content = "Content 1"
        doc1.metadata = {"source": "test1"}
        delattr(doc1, 'id')  # Ensure id attribute doesn't exist
        
        mock_vectorstore.similarity_search_with_score.return_value = [
            (doc1, 0.3)
        ]
        
        results = langchain_client.search_docs("test query")
        
        assert len(results) == 1
        doc_dto, distance = results[0]
        assert doc_dto.id == "unknown"  # Default fallback
    
    # === Update Document Tests ===
    
    # Test successful document update
    def test_update_doc_success(self, langchain_client, mock_collection):
        langchain_client.update_doc("doc1", "Updated content", {"source": "updated"})
        
        # Should delete then add
        mock_collection.delete.assert_called_once_with(ids=["doc1"])
        mock_collection.add.assert_called_once()
    
    # Test update with default metadata when none provided
    def test_update_doc_no_metadata_uses_default(self, langchain_client, mock_collection):
        langchain_client.update_doc("doc1", "Updated content")
        
        # Check that default metadata was used
        call_args = mock_collection.add.call_args[1]
        assert call_args["metadatas"] == [{"source": "updated"}]
    
    # === Delete Document Tests ===
    
    # Test successful document deletion
    def test_delete_doc_success(self, langchain_client, mock_collection):
        langchain_client.delete_doc("doc1")
        
        mock_collection.delete.assert_called_once_with(ids=["doc1"])
    
    # === Clear All Tests ===
    
    # Test successful clear operation
    def test_clear_success(self, langchain_client, mock_collection):
        mock_collection.get.return_value = {"ids": ["doc1", "doc2", "doc3"]}
        
        langchain_client.clear()
        
        mock_collection.delete.assert_called_once_with(ids=["doc1", "doc2", "doc3"])
    
    # Test clear when no documents exist
    def test_clear_no_documents(self, langchain_client, mock_collection):
        mock_collection.get.return_value = {"ids": []}
        
        langchain_client.clear()
        
        # Should not call delete if no documents
        mock_collection.delete.assert_not_called()
    
    # === Delete by Prefix Tests ===
    
    # Test delete by prefix with successful matches
    def test_delete_by_prefix_success(self, langchain_client, mock_collection):
        mock_collection.get.return_value = {
            "ids": ["test_doc1", "test_doc2", "other_doc1", "test_doc3"]
        }
        
        langchain_client.delete_by_prefix("test_")
        
        # Should delete only documents with matching prefix
        mock_collection.delete.assert_called_once_with(ids=["test_doc1", "test_doc2", "test_doc3"])
    
    # Test delete by prefix with no matches
    def test_delete_by_prefix_no_matches(self, langchain_client, mock_collection):
        mock_collection.get.return_value = {
            "ids": ["other_doc1", "another_doc2"]
        }
        
        langchain_client.delete_by_prefix("test_")
        
        # Should not call delete if no matches
        mock_collection.delete.assert_not_called()
    