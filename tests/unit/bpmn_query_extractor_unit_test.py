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
    
    # Test extract_terms method
    def test_extract_terms_success(self, bpmn_extractor):
        bpmn_xml = """<?xml version="1.0"?>
        <definitions>
            <participant name="Bank Customer"/>
            <task name="Review Application"/>
            <userTask name="Approve Loan"/>
        </definitions>"""
        
        result = bpmn_extractor.extract_terms(bpmn_xml)
        
        assert "Bank Customer" in result
        assert "Review Application" in result
        assert "Approve Loan" in result
    
    # Test filter_technical_terms method
    def test_filter_technical_terms_success(self, bpmn_extractor):
        text_matches = ["Bank Customer", "task_123abc", "Review Application", "sequenceflow_xyz", "designer"]

        result = bpmn_extractor.filter_technical_terms(text_matches)

        assert "bank customer" in result
        assert "review application" in result
        assert "designer" in result  # Tool terms are filtered in structural filter, not technical
        assert "task_123abc" not in result  # Technical ID filtered
        assert "sequenceflow_xyz" not in result  # SequenceFlow filtered
    
    # Test filter_structural_terms method
    def test_filter_structural_terms_success(self, bpmn_extractor):
        keywords = ["bank customer", "start", "end", "gateway", "review application", "sequence"]
        
        result = bpmn_extractor.filter_structural_terms(keywords)
        
        assert "bank customer" in result
        assert "review application" in result
        assert "start" not in result  # Structural term filtered
        assert "end" not in result  # Structural term filtered
        assert "gateway" not in result  # Structural term filtered
        assert "sequence" not in result  # Structural term filtered