from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class DocumentDTO:
    id: Optional[str]
    text: str
    metadata: Optional[Dict] = None
