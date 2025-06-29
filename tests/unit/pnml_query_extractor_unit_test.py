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
    
    # Test extract_terms method
    def test_extract_terms_success(self, pnml_extractor):
        pnml_xml = """<?xml version="1.0"?>
        <pnml>
            <net>
                <place id="p1"><name><text>Loan Application</text></name></place>
                <transition id="t1"><name><text>Verify Identity</text></name></transition>
            </net>
        </pnml>"""
        
        result = pnml_extractor.extract_terms(pnml_xml)
        
        assert "Loan Application" in result
        assert "Verify Identity" in result
    
    # Test filter_technical_terms method
    def test_filter_technical_terms_success(self, pnml_extractor):
        text_matches = ["Loan Application", "p1", "t2", "verify identity", "123", "noID"]
        
        result = pnml_extractor.filter_technical_terms(text_matches)
        
        assert "loan application" in result
        assert "verify identity" in result
        assert "p1" not in result  # Technical ID filtered
        assert "t2" not in result  # Technical ID filtered
        assert "123" not in result  # Number filtered
        assert "noID" not in result  # Special case filtered
    
    # Test filter_structural_terms method
    def test_filter_structural_terms_success(self, pnml_extractor):
        keywords = ["loan application", "start", "end", "place", "transition", "verify identity"]
        
        result = pnml_extractor.filter_structural_terms(keywords)
        
        assert "loan application" in result
        assert "verify identity" in result
        assert "start" not in result  # Structural term filtered
        assert "end" not in result  # Structural term filtered
        assert "place" not in result  # Structural term filtered
        assert "transition" not in result  # Structural term filtered