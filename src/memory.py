# src/memory.py
import json
from pathlib import Path

MEM_PATH = Path(".data") / "memory.json"
MEM_PATH.parent.mkdir(parents=True, exist_ok=True)

class MemoryStore:
    def __init__(self, path: Path = MEM_PATH):
        self.path = Path(path)
        if not self.path.exists():
            self.path.write_text(json.dumps({"sessions": []}, indent=2))

    def save_session(self, session: dict):
        data = json.loads(self.path.read_text())
        data["sessions"].append(session)
        self.path.write_text(json.dumps(data, indent=2))

    def list_sessions(self):
        return json.loads(self.path.read_text()).get("sessions", [])

# Singleton instance
memory_store = MemoryStore()
