import pytest
from unittest.mock import MagicMock, patch
import os
from app.infrastructure.rag.RAGAdapter import RAGAdapter
from app.core.dtos.DocumentDTO import DocumentDTO
from app.core.dtos.RagDTO import State


class TestRAGAdapter:
    
    @pytest.fixture
    def mock_langchain_client(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_prompt_template(self):
        template = MagicMock()
        template.format.return_value = "Formatted prompt with context"
        return template
    
    @pytest.fixture
    def rag_adapter(self, mock_prompt_template):
        with patch('app.infrastructure.rag.RAGAdapter.LangchainClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            adapter = RAGAdapter(mock_prompt_template)
            adapter.langchain_client = mock_client
            return adapter
    
    # === Retrieve Tests ===
    
    # Test successful document retrieval
    def test_retrieve_success(self, rag_adapter):
        expected_results = [
            (DocumentDTO(id="doc1", text="Test content", metadata={}), 0.8),
            (DocumentDTO(id="doc2", text="Another doc", metadata={}), 0.6)
        ]
        rag_adapter.langchain_client.search_docs.return_value = expected_results
        
        result = rag_adapter.retrieve("test query")
        
        assert result == expected_results
        rag_adapter.langchain_client.search_docs.assert_called_once_with("test query")
    
    # Test that empty query returns empty list
    def test_retrieve_empty_result(self, rag_adapter):
        """Test retrieval when no documents are found"""
        rag_adapter.langchain_client.search_docs.return_value = []
        
        result = rag_adapter.retrieve("test query")
        
        assert result == []
        rag_adapter.langchain_client.search_docs.assert_called_once_with("test query")
    
    # Test that LangChain exceptions are propagated
    def test_retrieve_langchain_exception(self, rag_adapter):
        rag_adapter.langchain_client.search_docs.side_effect = Exception("Vector DB error")
        
        with pytest.raises(Exception, match="Vector DB error"):
            rag_adapter.retrieve("test query")
    
    # === Augment Tests ===
    
    # Test successful prompt augmentation using template
    def test_augment_with_template_success(self, rag_adapter):
        state = State({
            "prompt": "Test prompt",
            "context": [
                DocumentDTO(id="doc1", text="Context 1", metadata={}),
                DocumentDTO(id="doc2", text="Context 2", metadata={})
            ]
        })
        
        with patch.dict(os.environ, {"ADDITIONAL_LLM_INSTRUCTION": "Be precise"}):
            result = rag_adapter.augment(state)
        
        assert result == "Formatted prompt with context"
        rag_adapter.prompt_template.format.assert_called_once()
        call_args = rag_adapter.prompt_template.format.call_args[1]
        assert call_args["prompt"] == "Test prompt"
        assert call_args["additional_llm_instruction"] == "Be precise"
        assert "[Document 1]" in call_args["context"]
        assert "Context 1" in call_args["context"]
        assert "[Document 2]" in call_args["context"]
        assert "Context 2" in call_args["context"]
    
    # Test augmentation with empty context
    def test_augment_without_context(self, rag_adapter):
        state = State({
            "prompt": "Test prompt"
        })
        
        with patch.dict(os.environ, {"ADDITIONAL_LLM_INSTRUCTION": "Be precise"}):
            rag_adapter.augment(state)
        
        rag_adapter.prompt_template.format.assert_called_once()
        call_args = rag_adapter.prompt_template.format.call_args[1]
        assert call_args["context"] == ""
    
    # Test fallback when template formatting fails
    def test_augment_template_failure_fallback(self, rag_adapter):
        state = State({
            "prompt": "Test prompt",
            "context": [DocumentDTO(id="doc1", text="Context", metadata={})]
        })
        
        rag_adapter.prompt_template.format.side_effect = Exception("Template error")
        
        with patch.dict(os.environ, {"ADDITIONAL_LLM_INSTRUCTION": "Be precise"}):
            result = rag_adapter.augment(state)
        
        assert "Test prompt" in result
        assert "Be precise" in result
        assert "Context" in result
        assert "Context:" in result
    
    # Test augmentation with no template
    def test_augment_no_template(self):
        with patch('app.infrastructure.rag.RAGAdapter.LangchainClient'):
            adapter = RAGAdapter(None)  # No template
            
        state = State({
            "prompt": "Test prompt",
            "context": [DocumentDTO(id="doc1", text="Context", metadata={})]
        })
        
        with patch.dict(os.environ, {"ADDITIONAL_LLM_INSTRUCTION": "Be precise"}):
            result = adapter.augment(state)
        
        assert "Test prompt" in result
        assert "Be precise" in result
        assert "Context" in result
    
    # Test augmentation with additional LLM instruction from environment
    def test_augment_no_additional_instruction(self, rag_adapter):
        state = State({
            "prompt": "Test prompt",
            "context": [DocumentDTO(id="doc1", text="Context", metadata={})]
        })
        
        with patch.dict(os.environ, {}, clear=True):  # Clear env vars
            rag_adapter.augment(state)
        
        call_args = rag_adapter.prompt_template.format.call_args[1]
        assert call_args["additional_llm_instruction"] is None
    
    # Test augmentation with empty context list
    def test_augment_empty_context_list(self, rag_adapter):
        """Test augmentation with empty context list"""
        state = State({
            "prompt": "Test prompt",
            "context": []
        })
        
        result = rag_adapter.augment(state)
        
        call_args = rag_adapter.prompt_template.format.call_args[1]
        assert call_args["context"] == ""
    
    # Test that multiple documents are formatted correctly
    def test_augment_multiple_documents_formatting(self, rag_adapter):
        state = State({
            "prompt": "Test prompt",
            "context": [
                DocumentDTO(id="doc1", text="First document", metadata={}),
                DocumentDTO(id="doc2", text="Second document", metadata={}),
                DocumentDTO(id="doc3", text="Third document", metadata={})
            ]
        })
        
        rag_adapter.augment(state)
        
        call_args = rag_adapter.prompt_template.format.call_args[1]
        context_text = call_args["context"]
        
        # Check document numbering and formatting
        assert "[Document 1]" in context_text
        assert "[Document 2]" in context_text
        assert "[Document 3]" in context_text
        assert "First document" in context_text
        assert "Second document" in context_text
        assert "Third document" in context_text
        
        # Check documents are separated
        lines = context_text.split("\n\n")
        assert len(lines) == 3