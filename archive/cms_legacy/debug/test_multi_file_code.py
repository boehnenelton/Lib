"""
Library:     test_multi_file_code.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Core-Command library component.
"""
import os
import sysSCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.dirname(SCRIPT_DIR)
BASE_DIR = os.path.dirname(LIB_DIR)

if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)

from BEJSON_CMS_Lib import CMSDatabase

MASTER_DB = os.path.join(BASE_DIR, "Data", "BEJSON_WEB_BUILDER", "site_master.json")

def test():
    print("--- Multi-File Code Scaffolding Test ---")
    cms = CMSDatabase(MASTER_DB)
    
    files = {
        "main.py": "def hello():\n    print('Hello World')\n\nif __name__ == '__main__':\n    hello()",
        "utils.py": "def add(a, b):\n    return a + b",
        "README.md": "# My Project\nThis is a test of the multi-file code viewer."
    }
    
    pid = cms.scaffold_code_project(
        "Multi-File Library Demo",
        files,
        description="This page demonstrates the new multi-file source code viewer with tabs.",
        category="Tutorials"
    )
    
    if pid:
        print(f"Success: Multi-file project page created (UUID: {pid})")
        # Trigger build to see it in action
        cms.build_and_publish()
        print(f"Site built. Check the Tutorials category for 'Multi-File Library Demo'")
    else:
        print("Failed to create multi-file project page")

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    test()
