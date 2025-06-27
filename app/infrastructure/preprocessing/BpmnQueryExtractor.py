import logging
import re
from typing import List

from ...core.ports.QueryExtractorPort import QueryExtractorPort

logger = logging.getLogger(__name__)


class BpmnQueryExtractor(QueryExtractorPort):
    
    def can_process(self, diagram: str) -> bool:
        return ("<?xml" in diagram and 
                ("<bpmn:" in diagram or "<definitions" in diagram))
    
    def get_diagram_type(self) -> str:
        return "BPMN"
    
    def extract_semantic_terms(self, diagram: str) -> List[str]:
        logger.debug("[BPMN EXTRACTOR] Extracting keywords from BPMN diagram")
        
        search_keywords = []
        
        # Extract BPMN-specific business context for search
        participants = self.extract_participants(diagram)
        lanes = self.extract_lanes(diagram)
        activities = self.extract_activities(diagram)
        
        # Add participants with high priority (at beginning)
        for participant in participants:
            search_keywords.insert(0, participant)
            logger.debug(f"[BPMN EXTRACTOR] Added participant keyword: '{participant}'")
            
        # Add lanes with high priority (at beginning)
        for lane in lanes:
            search_keywords.insert(0, lane)
            logger.debug(f"[BPMN EXTRACTOR] Added lane keyword: '{lane}'")
            
        # Add activities
        for activity in activities:
            search_keywords.append(activity)
            logger.debug(f"[BPMN EXTRACTOR] Added activity keyword: '{activity}'")
        
        logger.debug(f"[BPMN EXTRACTOR] Extracted {len(participants)} participants, "
                    f"{len(lanes)} lanes, {len(activities)} activities")
        
        return search_keywords
    
    def extract_participants(self, diagram: str) -> List[str]:
        participant_names = []
        
        patterns = [
            r'<bpmn:participant[^>]*name="([^"]*)"',
            r'<participant[^>]*name="([^"]*)"',
            r'name="([^"]*)"[^>]*participant',
        ]
        
        for pattern in patterns:
            participants = re.findall(pattern, diagram, re.IGNORECASE)
            if participants:
                logger.debug(f"[BPMN PROCESSOR] Pattern '{pattern}' found {len(participants)} participants")
                break
        else:
            logger.debug("[BPMN PROCESSOR] No participants found")
            return []
        
        for participant in participants:
            name = participant.strip().lower()
            if self.is_valid_name(name):
                participant_names.append(name)
                
        return participant_names
    
    def extract_lanes(self, diagram: str) -> List[str]:
        lane_names = []
        
        patterns = [
            r'<bpmn:lane[^>]*name="([^"]*)"',
            r'<lane[^>]*name="([^"]*)"',
            r'name="([^"]*)"[^>]*lane',
        ]
        
        for pattern in patterns:
            lanes = re.findall(pattern, diagram, re.IGNORECASE)
            if lanes:
                logger.debug(f"[BPMN PROCESSOR] Pattern '{pattern}' found {len(lanes)} lanes")
                break
        else:
            logger.debug("[BPMN PROCESSOR] No lanes found")
            return []
        
        for lane in lanes:
            name = lane.strip().lower()
            if self.is_valid_name(name):
                lane_names.append(name)
                
        return lane_names
    
    def extract_activities(self, diagram: str) -> List[str]:
        activity_names = []
        
        patterns = [
            r'<bpmn:task[^>]*name="([^"]*)"',
            r'<bpmn:userTask[^>]*name="([^"]*)"',
            r'<bpmn:serviceTask[^>]*name="([^"]*)"',
            r'<bpmn:scriptTask[^>]*name="([^"]*)"',
            r'<bpmn:manualTask[^>]*name="([^"]*)"',
            r'<bpmn:businessRuleTask[^>]*name="([^"]*)"',
            r'<bpmn:sendTask[^>]*name="([^"]*)"',
            r'<bpmn:receiveTask[^>]*name="([^"]*)"',
            r'<bpmn:startEvent[^>]*name="([^"]*)"',
            r'<bpmn:endEvent[^>]*name="([^"]*)"',
            r'<bpmn:intermediateThrowEvent[^>]*name="([^"]*)"',
            r'<bpmn:intermediateCatchEvent[^>]*name="([^"]*)"',
            r'<bpmn:subProcess[^>]*name="([^"]*)"',
            r'<task[^>]*name="([^"]*)"',
            r'<userTask[^>]*name="([^"]*)"',
            r'<serviceTask[^>]*name="([^"]*)"',
            r'<startEvent[^>]*name="([^"]*)"',
            r'<endEvent[^>]*name="([^"]*)"',
        ]
        
        for pattern in patterns:
            activities = re.findall(pattern, diagram, re.IGNORECASE)
            for activity in activities:
                name = activity.strip().lower()
                if self.is_valid_name(name) and name not in activity_names:
                    activity_names.append(name)
        
        return activity_names
    
    def is_valid_name(self, name: str) -> bool:
        return (name and len(name) > 1 and not name.isdigit())
