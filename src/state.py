from pydantic import BaseModel
from typing import List, Dict, Optional

class EntrepreneurState(BaseModel):
    session_id: str
    user_name: Optional[str] = None
    consent: bool = True
    messages: List[str] = []
    ideas: List[str] = []
    current_idea: Optional[str] = None
    ideas_data: Dict[str, Dict] = {}
