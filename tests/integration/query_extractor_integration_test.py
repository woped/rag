import pytest
from app.core.services.QueryExtractionService import QueryExtractionService
from app.infrastructure.preprocessing.PnmlQueryExtractor import PnmlQueryExtractor
from app.infrastructure.preprocessing.BpmnQueryExtractor import BpmnQueryExtractor


class TestQueryExtractionServiceIntegration:
    
    @pytest.fixture
    def mock_pnml_diagram(self):
        return """<?xml version="1.0" encoding="UTF-8"?>
<pnml xmlns="http://www.pnml.org/version-2009/grammar/pnml">
    <net id="net1" type="http://www.pnml.org/version-2009/grammar/ptnet">
        <place id="p1">
            <name>
                <text>loan application received</text>
            </name>
        </place>
        <place id="p2">
            <name>
                <text>credit check complete</text>
            </name>
        </place>
        <transition id="t1">
            <name>
                <text>verify applicant identity</text>
            </name>
        </transition>
        <transition id="t2">
            <name>
                <text>perform credit assessment</text>
            </name>
        </transition>
        <transition id="t3">
            <name>
                <text>noID</text>
            </name>
        </transition>
        <place id="p3">
            <name>
                <text>123</text>
            </name>
        </place>
    </net>
</pnml>"""
    
    @pytest.fixture
    def mock_bpmn_diagram(self):
        return """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
             xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL">
    <collaboration id="collaboration">
        <participant id="participant1" name="Bank Customer" processRef="process1"/>
        <participant id="participant2" name="Loan Officer" processRef="process2"/>
    </collaboration>
    <process id="process1">
        <lane id="lane1" name="Customer Service">
            <flowNodeRef>startEvent1</flowNodeRef>
            <flowNodeRef>task1</flowNodeRef>
        </lane>
        <lane id="lane2" name="Risk Management">
            <flowNodeRef>task2</flowNodeRef>
            <flowNodeRef>endEvent1</flowNodeRef>
        </lane>
        <startEvent id="startEvent1" name="Application Submitted"/>
        <userTask id="task1" name="Review Application Documents"/>
        <serviceTask id="task2" name="Calculate Risk Score"/>
        <endEvent id="endEvent1" name="Decision Made"/>
    </process>
</definitions>"""
    
    @pytest.fixture
    def query_extraction_service(self):
        extractors = [PnmlQueryExtractor(), BpmnQueryExtractor()]
        return QueryExtractionService(extractors)

    # Test that PnmlQueryExtractor correctly identifies PNML diagrams and extracts keywords
    def test_pnml_diagram_detection_and_extraction(self, query_extraction_service, mock_pnml_diagram):
        extracted_query = query_extraction_service.extract_query(mock_pnml_diagram)
        
        # Assert: Check that meaningful business terms are extracted
        assert "loan application received" in extracted_query
        assert "credit check complete" in extracted_query
        assert "verify applicant identity" in extracted_query
        assert "perform credit assessment" in extracted_query
        
        # Assert: Check that filtered content is excluded
        assert "noID" not in extracted_query  # Should be filtered out
        assert "123" not in extracted_query   # Pure numbers should be filtered out
        
        # Assert: Check that the query is not empty
        assert len(extracted_query.strip()) > 0
    
    # Test that BpmnQueryExtractor correctly identifies BPMN diagrams and extracts keywords
    def test_bpmn_diagram_detection_and_extraction(self, query_extraction_service, mock_bpmn_diagram):
        extracted_query = query_extraction_service.extract_query(mock_bpmn_diagram)
        
        # Assert: Check that participants are extracted (high priority)
        assert "bank customer" in extracted_query
        assert "loan officer" in extracted_query
        
        # Assert: Check that lanes are extracted (high priority)
        assert "customer service" in extracted_query
        assert "risk management" in extracted_query
        
        # Assert: Check that activities are extracted
        assert "review application documents" in extracted_query
        assert "calculate risk score" in extracted_query
        
        # Assert: Check that events are extracted
        assert "application submitted" in extracted_query
        assert "decision made" in extracted_query
        
        # Assert: Check that the query is not empty
        assert len(extracted_query.strip()) > 0
    
    # Test that structural terms are filtered out from the final query
    def test_keyword_optimization_filtering(self, query_extraction_service):
        # Create a realistic PNML diagram that includes both business and structural terms
        mock_diagram = '''<?xml version="1.0"?>
        <pnml xmlns="http://www.pnml.org/version-2009/grammar/pnml">
            <net>
                <place id="p1"><name><text>loan application</text></name></place>
                <place id="p2"><name><text>start</text></name></place>
                <transition id="t1"><name><text>gateway</text></name></transition>
                <transition id="t2"><name><text>end</text></name></transition>
            </net>
        </pnml>'''
        
        # Act: Extract query using real extractors
        extracted_query = query_extraction_service.extract_query(mock_diagram)
        
        # Assert: Business terms should be included
        assert "loan application" in extracted_query
        
        # Assert: Structural terms should be excluded by the optimization
        assert "start" not in extracted_query
        assert "gateway" not in extracted_query
        assert "end" not in extracted_query
    
    # Test that unknown diagram types return the original content as fallback
    def test_unknown_diagram_type_fallback(self, query_extraction_service):
        # Act: Try to extract from non-XML content
        unknown_content = "This is plain text, not a diagram"
        result = query_extraction_service.extract_query(unknown_content)
        
        # Assert: Should return the original content as fallback
        assert result == unknown_content
    
    # Test handling of empty or minimal diagrams
    def test_empty_diagram_handling(self, query_extraction_service):
        # Empty PNML diagram
        empty_pnml = '<?xml version="1.0"?><pnml></pnml>'
        result = query_extraction_service.extract_query(empty_pnml)
        
        # Should not crash and should return an empty or minimal query
        assert isinstance(result, str)
        
        # Empty BPMN diagram
        empty_bpmn = '<?xml version="1.0"?><definitions></definitions>'
        result = query_extraction_service.extract_query(empty_bpmn)
        
        # Should not crash and should return an empty or minimal query
        assert isinstance(result, str)
