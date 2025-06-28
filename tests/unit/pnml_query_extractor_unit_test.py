import pytest
from unittest.mock import patch, MagicMock
from app.infrastructure.preprocessing.PnmlQueryExtractor import PnmlQueryExtractor


class TestPnmlQueryExtractor:
    
    @pytest.fixture
    def pnml_extractor(self):
        return PnmlQueryExtractor()
    
    # Test can_process method for PNML diagrams
    def test_can_process_pnml_diagram_returns_true(self, pnml_extractor):
        pnml_xml = '<?xml version="1.0"?><pnml><net></net></pnml>'
        assert pnml_extractor.can_process(pnml_xml) is True
    
    # Test can_process method for BPMN diagrams
    def test_can_process_bpmn_diagram_returns_false(self, pnml_extractor):
        bpmn_xml = '<?xml version="1.0"?><definitions><bpmn:process></bpmn:process></definitions>'
        assert pnml_extractor.can_process(bpmn_xml) is False
    
    # Test can_process method for non-PNML content
    def test_can_process_invalid_xml_returns_false(self, pnml_extractor):
        invalid_xml = "not xml content"
        assert pnml_extractor.can_process(invalid_xml) is False
    
    # Test can_process method for empty or None content
    def test_can_process_empty_content_returns_false(self, pnml_extractor):
        assert pnml_extractor.can_process("") is False
        assert pnml_extractor.can_process(None) is False
    
    # Test get_diagram_type method
    def test_get_diagram_type_returns_pnml(self, pnml_extractor):
        assert pnml_extractor.get_diagram_type() == "PNML"
    
    # Test extract_semantic_terms method
    @patch('app.infrastructure.preprocessing.PnmlQueryExtractor.re.findall')
    def test_extract_semantic_terms_success(self, mock_findall, pnml_extractor):
        mock_findall.return_value = ["loan application received", "verify identity", "start", "123"]
        
        with patch.object(pnml_extractor, 'filter_semantic_terms') as mock_filter:
            mock_filter.return_value = ["loan application received", "verify identity"]
            
            result = pnml_extractor.extract_semantic_terms('<?xml version="1.0"?><pnml></pnml>')
        
        assert "loan application received" in result
        assert "verify identity" in result
        assert "start" not in result  # Should be filtered out
        assert "123" not in result    # Should be filtered out
    
    # Test filter_semantic_terms method
    def test_filter_semantic_terms_success(self, pnml_extractor):
        text_matches = ["loan application received", "verify identity", "start", "123"]
        
        with patch.object(pnml_extractor, 'is_meaningful_text') as mock_meaningful:
            with patch.object(pnml_extractor, 'is_process_relevant') as mock_relevant:
                mock_meaningful.side_effect = [True, True, False, False]
                mock_relevant.side_effect = [True, True]
                
                result = pnml_extractor.filter_semantic_terms(text_matches)
        
        assert len(result) == 2
        assert "loan application received" in result
        assert "verify identity" in result