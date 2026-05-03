"""
Library:     lib_state_bejson_management.py
Family:      Core
Jurisdiction: ["PYTHON", "SWITCH_CORE"]
Status:      OFFICIAL — BEJSON-Core/Lib (v1.4)
Author:      Elton Boehnen
Version:     1.4 OFFICIAL
Date:        2026-05-03
Description: Mirror of lib_state_bejson_management.js
    Python/Flask-compatible state management using BEJSON 104db.
"""
import json
from datetime import datetime

class BEJSONState:
    
    def __init__(self, schema_name="AppState", initial_state=None):
        self.bejson = {
            "Format": "BEJSON",
            "Format_Version": "104db",
            "Schema_Name": schema_name,
            "Records_Type": ["StateNode", "History"],
            "Fields": [
                { "name": "Record_Type_Parent", "type": "string" },
                { "name": "key", "type": "string", "Record_Type_Parent": "StateNode" },
                { "name": "value", "type": "string", "Record_Type_Parent": "StateNode" },
                { "name": "timestamp", "type": "string", "Record_Type_Parent": "History" },
                { "name": "snapshot", "type": "string", "Record_Type_Parent": "History" }
            ],
            "Values": []
        }
        self._state = initial_state or {}
        self._history_index = -1
        self._sync_to_bejson()
        self._save_history()

    @property
    def state(self):
        return self._state

    def set(self, key, value):
        self._state[key] = value
        self._sync_to_bejson()
        self._save_history()

    def get(self, key, default=None):
        return self._state.get(key, default)

    def _sync_to_bejson(self):
        # Clear current StateNodes
        self.bejson["Values"] = [r for r in self.bejson["Values"] if r[0] != "StateNode"]
        # Inject from current state
        for key, value in self._state.items():
            self.bejson["Values"].append(["StateNode", key, json.dumps(value), None, None])

    def _save_history(self):
        snapshot = json.dumps(self._state)
        timestamp = datetime.now().isoformat()
        self.bejson["Values"].append(["History", None, None, timestamp, snapshot])
        history_rows = [r for r in self.bejson["Values"] if r[0] == "History"]
        self._history_index = len(history_rows) - 1

    def undo(self):
        history_rows = [r for r in self.bejson["Values"] if r[0] == "History"]
        if self._history_index <= 0:
            return False
        self._history_index -= 1
        self._state = json.loads(history_rows[self._history_index][4])
        self._sync_to_bejson()
        return True

    def export_bejson(self):
        return json.dumps(self.bejson, indent=2)
