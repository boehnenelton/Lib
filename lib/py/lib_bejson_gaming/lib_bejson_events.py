"""
game1 aka the BEJSON Game Engine (#1)
Author: Elton Boehnen
MFDB Version: 1.3.1
"""
class BEJSONEvents:
    """
    Mirror of lib_bejson_events.js
    Python/Flask-compatible MFDB 1.3 L2 Event System.
    """
    def __init__(self, state_manager):
        self.state = state_manager
        self.bejson = {
            "Format": "BEJSON",
            "Format_Version": "104",
            "Format_Creator": "Elton Boehnen",
            "Schema_Name": "Events",
            "Parent_Hierarchy": "Root/System/Events",
            "Records_Type": ["Event"],
            "Fields": [
                { "name": "id", "type": "string" },
                { "name": "type", "type": "string" },
                { "name": "x", "type": "number" },
                { "name": "y", "type": "number" },
                { "name": "script", "type": "array" },
                { "name": "condition", "type": "string" }
            ],
            "Values": []
        }

    def run_event(self, event_id):
        event = next((row for row in self.bejson["Values"] if row[0] == event_id), None)
        if not event:
            return
        
        condition = event[5]
        if condition and not self._check_condition(condition):
            return
        
        script = event[4]
        for cmd in script:
            self._execute_command(cmd)

    def _check_condition(self, condition):
        if condition.startswith("flag:"):
            flag_name = condition.split(":")[1]
            return self.state.get(flag_name) == True
        return True

    def _execute_command(self, cmd):
        action = cmd[0]
        args = cmd[1:]
        if action == "SET_FLAG":
            self.state.set(args[0], args[1])

    def export_bejson(self):
        import json
        return json.dumps(self.bejson, indent=2)
