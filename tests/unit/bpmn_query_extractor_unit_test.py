import pytest
from unittest.mock import patch, MagicMock
from app.infrastructure.preprocessing.BpmnQueryExtractor import BpmnQueryExtractor


class TestBpmnQueryExtractor:
    
    @pytest.fixture
    def bpmn_extractor(self):
        return BpmnQueryExtractor()
    
    # Test can_process method for BPMN diagrams
    def test_can_process_bpmn_diagram_returns_true(self, bpmn_extractor):
        bpmn_xml = '<?xml version="1.0"?><definitions><bpmn:process></bpmn:process></definitions>'
        assert bpmn_extractor.can_process(bpmn_xml) is True
    
    # Test can_process method for BPMN diagrams with pnml prefix
    def test_can_process_pnml_diagram_returns_false(self, bpmn_extractor):
        pnml_xml = '<?xml version="1.0"?><pnml></pnml>'
        assert bpmn_extractor.can_process(pnml_xml) is False
    
    # Test can_process method for invalid XML content
    def test_can_process_invalid_xml_returns_false(self, bpmn_extractor):
        invalid_xml = "not xml content"
        assert bpmn_extractor.can_process(invalid_xml) is False
    
    # Test can_process method for empty or None content
    def test_can_process_empty_content_returns_false(self, bpmn_extractor):
        assert bpmn_extractor.can_process("") is False
        assert bpmn_extractor.can_process(None) is False
    
    # Test get_diagram_type method
    def test_get_diagram_type_returns_bpmn(self, bpmn_extractor):
        assert bpmn_extractor.get_diagram_type() == "BPMN"
    
    # Test extract_semantic_terms method
    @patch.object(BpmnQueryExtractor, 'extract_participants')
    @patch.object(BpmnQueryExtractor, 'extract_lanes')
    @patch.object(BpmnQueryExtractor, 'extract_activities')
    def test_extract_semantic_terms_success(self, mock_activities, mock_lanes, mock_participants, bpmn_extractor):
        mock_participants.return_value = ["bank customer"]
        mock_lanes.return_value = ["risk management"]
        mock_activities.return_value = ["approve loan"]
        
        result = bpmn_extractor.extract_semantic_terms('<?xml version="1.0"?><definitions></definitions>')
        
        # Participants and lanes are inserted at the beginning
        assert "bank customer" in result
        assert "risk management" in result
        assert "approve loan" in result
    
    # Test extract_participants method
    @patch('app.infrastructure.preprocessing.BpmnQueryExtractor.re.findall')
    def test_extract_participants_success(self, mock_findall, bpmn_extractor):
        mock_findall.return_value = ["Bank Customer"]
        
        with patch.object(bpmn_extractor, 'is_valid_name', return_value=True):
            result = bpmn_extractor.extract_participants('<participant name="Bank Customer"/>')
        
        assert "bank customer" in result
    
    # Test extract_lanes method
    @patch('app.infrastructure.preprocessing.BpmnQueryExtractor.re.findall')
    def test_extract_lanes_success(self, mock_findall, bpmn_extractor):
        mock_findall.return_value = ["Risk Management"]
        
        with patch.object(bpmn_extractor, 'is_valid_name', return_value=True):
            result = bpmn_extractor.extract_lanes('<lane name="Risk Management"/>')
        
        assert "risk management" in result
    
    # Test extract_activities method
    @patch('app.infrastructure.preprocessing.BpmnQueryExtractor.re.findall')
    def test_extract_activities_success(self, mock_findall, bpmn_extractor):
        mock_findall.return_value = ["Review Application"]
        
        with patch.object(bpmn_extractor, 'is_valid_name', return_value=True):
            result = bpmn_extractor.extract_activities('<task name="Review Application"/>')
        
        assert "review application" in result