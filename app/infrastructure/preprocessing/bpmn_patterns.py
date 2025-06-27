PARTICIPANT_PATTERNS = [
    r'<bpmn:participant[^>]*name="([^"]*)"',
    r'<participant[^>]*name="([^"]*)"',
    r'name="([^"]*)"[^>]*participant',
]

LANE_PATTERNS = [
    r'<bpmn:lane[^>]*name="([^"]*)"',
    r'<lane[^>]*name="([^"]*)"',
    r'name="([^"]*)"[^>]*lane',
]

ACTIVITY_PATTERNS = [
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