import pytest
from unittest.mock import MagicMock
from app.core.services.QueryExtractionService import QueryExtractionService


class TestQueryExtractionService:
    
    @pytest.fixture
    def mock_pnml_extractor(self):
        return MagicMock()
    
    @pytest.fixture
    def mock_bpmn_extractor(self):
        return MagicMock()
    
    @pytest.fixture
    def query_service(self, mock_pnml_extractor, mock_bpmn_extractor):
        return QueryExtractionService([mock_pnml_extractor, mock_bpmn_extractor])
    
    # Test that extract_query processes PNML diagrams correctly
    def test_extract_query_pnml_diagram(self, query_service, mock_pnml_extractor, mock_bpmn_extractor):
        pnml_xml = '<?xml version="1.0"?><pnml><text>loan application</text></pnml>'
        
        mock_pnml_extractor.can_process.return_value = True
        mock_bpmn_extractor.can_process.return_value = False
        mock_pnml_extractor.get_diagram_type.return_value = "PNML"
        mock_pnml_extractor.extract_semantic_terms.return_value = ["loan application process"]
        
        result = query_service.extract_query(pnml_xml)
        
        assert result == "loan application process"
        mock_pnml_extractor.can_process.assert_called_once_with(pnml_xml)
        mock_pnml_extractor.extract_semantic_terms.assert_called_once_with(pnml_xml)
        mock_bpmn_extractor.extract_query.assert_not_called()
    
    # Test that extract_query processes BPMN diagrams correctly
    def test_extract_query_bpmn_diagram(self, query_service, mock_pnml_extractor, mock_bpmn_extractor):
        bpmn_xml = '<?xml version="1.0"?><definitions><process><task name="approve loan"/></process></definitions>'
        
        mock_pnml_extractor.can_process.return_value = False
        mock_bpmn_extractor.can_process.return_value = True
        mock_bpmn_extractor.get_diagram_type.return_value = "BPMN"
        mock_bpmn_extractor.extract_semantic_terms.return_value = ["approve loan workflow"]
        
        result = query_service.extract_query(bpmn_xml)
        
        assert result == "approve loan workflow"
        mock_bpmn_extractor.can_process.assert_called_once_with(bpmn_xml)
        mock_bpmn_extractor.extract_semantic_terms.assert_called_once_with(bpmn_xml)
        mock_pnml_extractor.extract_query.assert_not_called()
    
    # Test that extract_query returns original input for non-XML diagrams
    def test_extract_query_unknown_format_returns_original(self, query_service, mock_pnml_extractor, mock_bpmn_extractor):
        unknown_xml = "<unknown>not a valid diagram</unknown>"
        
        mock_pnml_extractor.can_process.return_value = False
        mock_bpmn_extractor.can_process.return_value = False
        
        result = query_service.extract_query(unknown_xml)
        
        assert result == unknown_xml
        mock_pnml_extractor.extract_query.assert_not_called()
        mock_bpmn_extractor.extract_query.assert_not_called()
    
    # Test that extract_query returns original input for empty input
    def test_extract_query_empty_input(self, query_service):
        result = query_service.extract_query("")
        assert result == ""
    
    # Test that find_extractor returns the correct extractor based on diagram type
    def test_find_extractor_returns_correct_extractor(self, query_service, mock_pnml_extractor, mock_bpmn_extractor):
        diagram = "test diagram"
        
        mock_pnml_extractor.can_process.return_value = True
        mock_bpmn_extractor.can_process.return_value = False
        
        result = query_service.find_extractor(diagram)
        
        assert result == mock_pnml_extractor
        mock_pnml_extractor.can_process.assert_called_once_with(diagram)
    
    # Test that find_extractor returns None when no extractor can process the diagram
    def test_find_extractor_returns_none_when_no_match(self, query_service, mock_pnml_extractor, mock_bpmn_extractor):
        diagram = "unknown format"
        
        mock_pnml_extractor.can_process.return_value = False
        mock_bpmn_extractor.can_process.return_value = False
        
        result = query_service.find_extractor(diagram)
        
        assert result is None
