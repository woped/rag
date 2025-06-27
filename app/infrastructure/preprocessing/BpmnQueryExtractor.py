import logging
import re
from typing import List
from app.core.ports.QueryExtractorPort import QueryExtractorPort
from .bpmn_patterns import PARTICIPANT_PATTERNS, LANE_PATTERNS, ACTIVITY_PATTERNS


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
        
        try: 
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
        except Exception as e:
            logger.exception(f"[BPMN EXTRACTOR] Failed to extract semantic terms: {e}")
            raise
    
    # Extract participant names from the BPMN diagram using regex patterns
    def extract_participants(self, diagram: str) -> List[str]:
        try:
            participant_names = []

            for pattern in PARTICIPANT_PATTERNS:
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
        except Exception as e:
            logger.exception(f"[BPMN EXTRACTOR] Failed to extract participants: {e}")
            raise
    
    # Extract lane names from the BPMN diagram using regex patterns
    def extract_lanes(self, diagram: str) -> List[str]:
        try:
            lane_names = []
            
            for pattern in LANE_PATTERNS:
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
        except Exception as e:
            logger.exception(f"[BPMN EXTRACTOR] Failed to extract lanes: {e}")
            raise
    
    # Extract activity names from the BPMN diagram using regex patterns
    def extract_activities(self, diagram: str) -> List[str]:
        try:
            activity_names = []
            
            for pattern in ACTIVITY_PATTERNS:
                activities = re.findall(pattern, diagram, re.IGNORECASE)
                for activity in activities:
                    name = activity.strip().lower()
                    is_valid_name = (name and len(name) > 1 and not name.isdigit())
                    if is_valid_name and name not in activity_names:
                        activity_names.append(name)
            
            return activity_names
        except Exception as e:
            logger.exception(f"[BPMN EXTRACTOR] Failed to extract activities: {e}")
            raise
