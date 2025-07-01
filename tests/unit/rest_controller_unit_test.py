import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
import tempfile
import os
from app.presentation.controller.RESTController import rest_bp
from app.core.dtos.DocumentDTO import DocumentDTO


class TestRESTController:
    
    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        app.register_blueprint(rest_bp)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    # === Search Endpoint Tests ===
    
    # Test successful document search
    @patch('app.presentation.controller.RESTController.app_service')
    def test_search_docs_success(self, mock_app_service, client):
        mock_app_service.search_docs.return_value = [
            (DocumentDTO(id="doc1", text="Test content", metadata={"source": "test"}), 0.5),
            (DocumentDTO(id="doc2", text="Another test", metadata={}), 0.7)
        ]
        
        response = client.get('/rag/search?query=test')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['results']) == 2
        assert data['results'][0]['id'] == 'doc1'
        assert data['results'][0]['text'] == 'Test content'
        assert data['results'][0]['distance'] == 0.5
        assert data['results'][0]['metadata'] == {"source": "test"}
        mock_app_service.search_docs.assert_called_once_with('test')
    
    # Test search without query parameter
    @patch('app.presentation.controller.RESTController.app_service')
    def test_search_docs_no_query(self, mock_app_service, client):
        response = client.get('/rag/search')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'No query provided' in data['error']
        mock_app_service.search_docs.assert_not_called()
    
    # Test search with empty query
    @patch('app.presentation.controller.RESTController.app_service')
    def test_search_docs_empty_query(self, mock_app_service, client):
        response = client.get('/rag/search?query=')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'No query provided' in data['error']
    
    # Test search returning no results
    @patch('app.presentation.controller.RESTController.app_service')
    def test_search_docs_no_results(self, mock_app_service, client):
        mock_app_service.search_docs.return_value = []
        
        response = client.get('/rag/search?query=nonexistent')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['results'] == []
    
    # Test search with service raising ValueError
    @patch('app.presentation.controller.RESTController.app_service')
    def test_search_docs_internal_error(self, mock_app_service, client):
        """Test search with service raising internal error"""
        mock_app_service.search_docs.side_effect = Exception("Database error")
        
        response = client.get('/rag/search?query=test')
        
        assert response.status_code == 500
        data = response.get_json()
        assert 'Internal server error' in data['error']
    
    # === Enrich Prompt Endpoint Tests ===
    
    # Test successful prompt enrichment
    @patch('app.presentation.controller.RESTController.app_service')
    def test_enrich_prompt_success(self, mock_app_service, client):
        mock_app_service.process_rag_request.return_value = "Enriched prompt with context"
        
        response = client.post('/rag/enrich', 
                              json={'prompt': 'test prompt', 'diagram': 'xml content'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['enriched_prompt'] == 'Enriched prompt with context'
        mock_app_service.process_rag_request.assert_called_once_with('test prompt', 'xml content')
    
    # Test prompt enrichment with missing fields (should use defaults)
    @patch('app.presentation.controller.RESTController.app_service')
    def test_enrich_prompt_missing_fields(self, mock_app_service, client):
        mock_app_service.process_rag_request.return_value = "Enriched prompt"
        
        response = client.post('/rag/enrich', json={})
        
        assert response.status_code == 200
        mock_app_service.process_rag_request.assert_called_once_with('', '')
    
    # === Add Documents Endpoint Tests ===
    
    # Test successful document addition
    @patch('app.presentation.controller.RESTController.app_service')
    def test_add_docs_success(self, mock_app_service, client):
        docs = [
            {'text': 'Test content 1', 'id': 'test1', 'metadata': {'source': 'test'}},
            {'text': 'Test content 2', 'id': 'test2'}
        ]
        
        response = client.post('/rag/add', json=docs)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['status'] == 'ok'
        mock_app_service.add_docs.assert_called_once()
        
        # Verify the DocumentDTOs were created correctly
        call_args = mock_app_service.add_docs.call_args[0][0]
        assert len(call_args) == 2
        assert call_args[0].id == 'test1'
        assert call_args[0].text == 'Test content 1'
        assert call_args[1].id == 'test2'
        assert call_args[1].text == 'Test content 2'
    
    # Test document addition with invalid format (not a list)
    @patch('app.presentation.controller.RESTController.app_service')
    def test_add_docs_invalid_format(self, mock_app_service, client):
        response = client.post('/rag/add', json={'not': 'a list'})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Expected a list' in data['error']
        mock_app_service.add_docs.assert_not_called()
    
    # Test document addition with missing text field
    @patch('app.presentation.controller.RESTController.app_service')
    def test_add_docs_missing_text(self, mock_app_service, client):
        docs = [{'id': 'test1'}]  # Missing text
        
        response = client.post('/rag/add', json=docs)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Missing text' in data['error']
        mock_app_service.add_docs.assert_not_called()
    
    # === Get Document by ID Endpoint Tests ===
    
    # Test successful document retrieval by ID
    @patch('app.presentation.controller.RESTController.app_service')
    def test_get_doc_by_id_success(self, mock_app_service, client):
        mock_result = {"id": "doc1", "text": "Test content", "metadata": {"source": "test"}}
        mock_app_service.get_doc_by_id.return_value = mock_result
        
        response = client.get('/rag/doc1')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == 'doc1'
        assert data['text'] == 'Test content'
        mock_app_service.get_doc_by_id.assert_called_once_with('doc1')
    
    # Test document retrieval when document not found
    @patch('app.presentation.controller.RESTController.app_service')
    def test_get_doc_by_id_not_found(self, mock_app_service, client):
        mock_app_service.get_doc_by_id.return_value = None
        
        response = client.get('/rag/nonexistent')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data is None
    
    # === Update Document Endpoint Tests ===
    
    # Test successful document update
    @patch('app.presentation.controller.RESTController.app_service')
    def test_update_doc_success(self, mock_app_service, client):
        response = client.put('/rag/doc1', 
                             json={'text': 'Updated content', 'metadata': {'updated': True}})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'updated'
        mock_app_service.update_doc.assert_called_once()
        
        # Verify the DocumentDTO was created correctly
        call_args = mock_app_service.update_doc.call_args[0][0]
        assert call_args.id == 'doc1'
        assert call_args.text == 'Updated content'
        assert call_args.metadata == {'updated': True}
    
    # Test document update with missing text field
    @patch('app.presentation.controller.RESTController.app_service')
    def test_update_doc_no_text(self, mock_app_service, client):
        response = client.put('/rag/doc1', json={'metadata': {'test': True}})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'No text provided' in data['error']
        mock_app_service.update_doc.assert_not_called()
    
    # Test document update with empty text
    @patch('app.presentation.controller.RESTController.app_service')
    def test_update_doc_empty_text(self, mock_app_service, client):
        """Test document update with empty text"""
        response = client.put('/rag/doc1', json={'text': ''})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'No text provided' in data['error']
    
    # === Delete Document Endpoint Tests ===
    
    # Test successful document deletion
    @patch('app.presentation.controller.RESTController.app_service')
    def test_delete_doc_success(self, mock_app_service, client):
        response = client.delete('/rag/doc1')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'deleted'
        mock_app_service.delete_doc.assert_called_once_with('doc1')
    
    # Test document deletion with non-existent ID
    @patch('app.presentation.controller.RESTController.app_service')
    def test_delete_doc_value_error(self, mock_app_service, client):
        mock_app_service.delete_doc.side_effect = ValueError("Invalid ID")
        
        response = client.delete('/rag/invalid')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid ID' in data['error']
    
    # Test document deletion with internal error
    @patch('app.presentation.controller.RESTController.app_service')
    def test_delete_doc_internal_error(self, mock_app_service, client):
        """Test document deletion with internal error"""
        mock_app_service.delete_doc.side_effect = Exception("Database error")
        
        response = client.delete('/rag/doc1')
        
        assert response.status_code == 500
        data = response.get_json()
        assert 'Internal server error' in data['error']
    
    # === Clear Database Endpoint Tests ===
    
    # Test successful database clear
    @patch('app.presentation.controller.RESTController.app_service')
    def test_clear_collection_success(self, mock_app_service, client):
        response = client.post('/rag/clear')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'cleared'
        mock_app_service.clear_docs.assert_called_once()
    
    # Test database clear with internal error
    @patch('app.presentation.controller.RESTController.app_service')
    def test_clear_collection_internal_error(self, mock_app_service, client):
        mock_app_service.clear_docs.side_effect = Exception("Database error")
        
        response = client.post('/rag/clear')
        
        assert response.status_code == 500
        data = response.get_json()
        assert 'Internal server error' in data['error']
    
    # === Upload PDF Endpoint Tests ===
    
    # Test successful PDF upload
    @patch('app.presentation.controller.RESTController.app_service')
    def test_upload_pdf_success(self, mock_app_service, client):
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'%PDF-1.4 fake pdf content')
            tmp_path = tmp.name
        
        try:
            with open(tmp_path, 'rb') as f:
                response = client.post('/rag/upload_pdf', 
                                     data={'file': (f, 'test.pdf')},
                                     content_type='multipart/form-data')
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['status'] == 'PDF processed and added'
            mock_app_service.upload_and_index_pdf.assert_called_once()
        finally:
            os.unlink(tmp_path)
    
    # Test PDF upload without file
    @patch('app.presentation.controller.RESTController.app_service')
    def test_upload_pdf_no_file(self, mock_app_service, client):
        response = client.post('/rag/upload_pdf')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'No file uploaded' in data['error']
        mock_app_service.upload_and_index_pdf.assert_not_called()
    
    # Test PDF upload with invalid file type
    @patch('app.presentation.controller.RESTController.app_service')
    def test_upload_pdf_value_error(self, mock_app_service, client):
        mock_app_service.upload_and_index_pdf.side_effect = ValueError("Invalid PDF")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'fake pdf')
            tmp_path = tmp.name
        
        try:
            with open(tmp_path, 'rb') as f:
                response = client.post('/rag/upload_pdf', 
                                     data={'file': (f, 'test.pdf')},
                                     content_type='multipart/form-data')
            
            assert response.status_code == 400
            data = response.get_json()
            assert 'Invalid PDF' in data['error']
        finally:
            os.unlink(tmp_path)
    
    # Test PDF upload with internal error
    @patch('app.presentation.controller.RESTController.app_service')
    def test_upload_pdf_internal_error(self, mock_app_service, client):
        mock_app_service.upload_and_index_pdf.side_effect = Exception("Processing failed")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'fake pdf')
            tmp_path = tmp.name
        
        try:
            with open(tmp_path, 'rb') as f:
                response = client.post('/rag/upload_pdf', 
                                     data={'file': (f, 'test.pdf')},
                                     content_type='multipart/form-data')
            
            assert response.status_code == 500
            data = response.get_json()
            assert 'Internal server error' in data['error']
        finally:
            os.unlink(tmp_path)
    
    # === Debug Dump Endpoint Tests ===
    
    # Test successful debug dump
    @patch('app.presentation.controller.RESTController.app_service')
    def test_debug_dump_success(self, mock_app_service, client):
        # Mock the nested structure: app_service.db_service.db.client.collection.get()
        mock_collection = MagicMock()
        mock_collection.get.return_value = {"ids": ["doc1", "doc2", "doc3"]}
        mock_client = MagicMock()
        mock_client.collection = mock_collection
        mock_db = MagicMock()
        mock_db.client = mock_client
        mock_app_service.db_service.db = mock_db
        
        response = client.get('/rag/debug_dump')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 3
        assert data['ids'] == ["doc1", "doc2", "doc3"]
