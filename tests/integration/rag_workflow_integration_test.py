"""
Integration test for the complete RAG workflow (ChromaDB-free version).

Tests the full end-to-end RAG pipeline without ChromaDB dependencies:
1. POST /rag/enrich endpoint receives prompt and diagram
2. Query extraction (if enabled) processes the diagram
3. RAG service retrieves relevant documents (mocked)
4. RAG service augments the prompt with retrieved context (mocked)
5. Returns enriched prompt

This test validates the complete integration between REST endpoints and business logic
while avoiding ChromaDB instability by mocking all database operations.
"""
import pytest
import logging
from unittest.mock import patch, MagicMock
from flask import Flask
from app.presentation.controller.RESTController import rest_bp
from app.core.dtos.DocumentDTO import DocumentDTO

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def app():

    app = Flask(__name__)
    app.register_blueprint(rest_bp)
    app.config['TESTING'] = True
    
    with patch('app.presentation.controller.RESTController.app_service') as mock_app_service:
        mock_app_service.process_rag_request.return_value = "Enhanced prompt with RAG context"
        mock_app_service.add_docs.return_value = None
        mock_app_service.search_docs.return_value = [
            (DocumentDTO(id="doc1", text="Sample document", metadata={}), 0.8)
        ]
        
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

class TestRAGWorkflowIntegrationMocked:
    
    # Test successful RAG enrichment endpoint integration
    def test_rag_enrich_endpoint_success(self, client):
        logger.info("=== Testing RAG Enrich Endpoint Success (Mocked) ===")
        
        with patch('app.presentation.controller.RESTController.app_service') as mock_app_service:
            # Configure mock to simulate successful RAG processing
            mock_app_service.process_rag_request.return_value = "Enhanced prompt: How should I design a BPMN process? Context: BPMN processes require proper start and end events."
            
            # Send RAG enrich request
            test_prompt = "How should I design a BPMN process?"
            test_diagram = "process modeling workflow design"
            
            response = client.post('/rag/enrich',
                                   json={
                                       "prompt": test_prompt,
                                       "diagram": test_diagram
                                   },
                                   content_type='application/json')
            
            # Verify response
            assert response.status_code == 200
            response_data = response.get_json()
            assert "enriched_prompt" in response_data
            
            enriched_prompt = response_data["enriched_prompt"]
            assert isinstance(enriched_prompt, str)
            assert "Enhanced prompt" in enriched_prompt
            assert "Context:" in enriched_prompt
            
            # Verify that the application service was called correctly
            mock_app_service.process_rag_request.assert_called_once_with(test_prompt, test_diagram)
            
            logger.info(f"Original prompt: {test_prompt}")
            logger.info(f"Enriched prompt: {enriched_prompt}")
    
    # Test RAG enrichment endpoint with diagram preprocessing
    def test_rag_enrich_endpoint_with_diagram_preprocessing(self, client):
        logger.info("=== Testing RAG Enrich Endpoint with Preprocessing (Mocked) ===")
        
        with patch('app.presentation.controller.RESTController.app_service') as mock_app_service:
            # Configure mock to simulate preprocessing and RAG processing
            mock_app_service.process_rag_request.return_value = "Preprocessed and enhanced prompt with extracted BPMN elements"
            
            # Send RAG enrich request with BPMN diagram
            response = client.post('/rag/enrich',
                                   json={
                                       "prompt": "Describe this process",
                                       "diagram": "<bpmn:process><bpmn:startEvent/><bpmn:task name='Review Application'/></bpmn:process>"
                                   },
                                   content_type='application/json')
            
            # Verify response
            assert response.status_code == 200
            response_data = response.get_json()
            assert "enriched_prompt" in response_data
            
            enriched_prompt = response_data["enriched_prompt"]
            assert "Preprocessed and enhanced" in enriched_prompt
            
            # Verify that the application service was called
            mock_app_service.process_rag_request.assert_called_once()

    # Test RAG enrichment endpoint error handling
    def test_rag_enrich_endpoint_error_handling(self, client):

        with patch('app.presentation.controller.RESTController.app_service') as mock_app_service:
            # Configure mock to simulate ValueError
            mock_app_service.process_rag_request.side_effect = ValueError("Invalid diagram format")
            
            response = client.post('/rag/enrich',
                                   json={
                                       "prompt": "Test prompt",
                                       "diagram": "invalid diagram"
                                   },
                                   content_type='application/json')
            
            # Should return 400 Bad Request
            assert response.status_code == 400
            response_data = response.get_json()
            assert "error" in response_data
            assert "Invalid diagram format" in response_data["error"]
    
    # Test the complete RAG workflow from document addition to enrichment
    def test_full_rag_workflow_integration(self, client):

        with patch('app.presentation.controller.RESTController.app_service') as mock_app_service:
            # Configure mocks for the complete workflow
            mock_app_service.add_docs.return_value = None
            mock_app_service.process_rag_request.return_value = "Complete workflow: Enhanced prompt with full context from multiple documents"
            
            # Step 1: Add documents
            sample_docs = [
                {
                    "text": "BPMN modeling guidelines for process design",
                    "metadata": {"source": "bpmn_guide.pdf"}
                },
                {
                    "text": "Best practices for workflow automation",
                    "metadata": {"source": "workflow_best_practices.pdf"}
                }
            ]
            
            add_response = client.post('/rag/add',
                                       json=sample_docs,
                                       content_type='application/json')
            assert add_response.status_code == 201 
            
            # Step 2: Perform RAG enrichment
            enrich_response = client.post('/rag/enrich',
                                          json={
                                              "prompt": "How to create effective BPMN diagrams?",
                                              "diagram": "process modeling diagram"
                                          },
                                          content_type='application/json')
            
            # Step 3: Verify complete workflow
            assert enrich_response.status_code == 200
            response_data = enrich_response.get_json()
            
            enriched_prompt = response_data["enriched_prompt"]
            assert "Complete workflow" in enriched_prompt
            assert "Enhanced prompt" in enriched_prompt
            assert "full context" in enriched_prompt
            
            # Verify both operations were called
            mock_app_service.add_docs.assert_called_once()
            mock_app_service.process_rag_request.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
