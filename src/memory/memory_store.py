import json
from pathlib import Path
from typing import List, Dict


MEM_PATH = Path(".data") / "memory.json"
MEM_PATH.parent.mkdir(parents=True, exist_ok=True)


class MemoryStore:
    def __init__(self, path=MEM_PATH):
            self.path = Path(path)
            if not self.path.exists():
                self.path.write_text(json.dumps({"sessions": []}))


    def save_session(self, session: Dict):
        data = json.loads(self.path.read_text())
        data["sessions"].append(session)
        self.path.write_text(json.dumps(data, indent=2))


    def list_sessions(self) -> List[Dict]:
        return json.loads(self.path.read_text()).get("sessions", [])