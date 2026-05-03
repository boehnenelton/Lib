"""
Library:     lib_bejson_game1_ui_screens.py
Family:      Game1
Jurisdiction: ["PYTHON", "SWITCH_CORE"]
Status:      OFFICIAL — BEJSON-Core/Lib (v1.4)
Author:      Elton Boehnen
Version:     1.4 OFFICIAL
Date:        2026-05-03
Description: Mirror of lib_bejson_ui_screens.js
    Python-compatible BEJSON-Native UI Screen Manager.
"""
import json

class BEJSONUIScreens:
    
    def __init__(self):
        self.bejson = {
            "Format": "BEJSON",
            "Format_Version": "104",
            "Schema_Name": "UIScreens",
            "Records_Type": ["Screen"],
            "Fields": [
                { "name": "id", "type": "string" },
                { "name": "title", "type": "string" },
                { "name": "options", "type": "array" }
            ],
            "Values": [
                ["START_SCREEN", "SWITCH RPG", ["Start Game", "Load Game", "Options", "Exit"]],
                ["SAVE_MENU", "SAVE GAME", ["Slot 1", "Slot 2", "Slot 3", "Back"]]
            ]
        }

    def get_screen(self, screen_id):
        """Retrieves a screen record by ID."""
        return next((row for row in self.bejson["Values"] if row[0] == screen_id), None)

    def add_screen(self, screen_id, title, options):
        """Adds a new screen to the registry."""
        idx = next((i for i, v in enumerate(self.bejson["Values"]) if v[0] == screen_id), -1)
        if idx != -1:
            self.bejson["Values"][idx] = [screen_id, title, options]
        else:
            self.bejson["Values"].append([screen_id, title, options])

    def export_bejson(self):
        return json.dumps(self.bejson, indent=2)
