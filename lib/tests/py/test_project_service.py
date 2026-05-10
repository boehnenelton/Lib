"""
Library:     test_project_service.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.5)
Author:      Elton Boehnen
Version:     1.5 OFFICIAL
Date:        2026-05-01
Description: Core-Command library component.
"""
import os
import sys
import unittest
import json
from pathlib import PathLIB_DIR = "/storage/7B30-0E0B/Core-Command/Lib/py"
if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)

from lib_be_project_service import ProjectService

class TestProjectService(unittest.TestCase):
    def test_list_projects(self):
        projects = ProjectService.get_projects()
        self.assertIsInstance(projects, list)
        print(f"Verified: Found {len(projects)} projects.")

    def test_get_paths(self):
        projects = ProjectService.get_projects()
        if projects:
            p_name = projects[0][2]
            path = ProjectService.get_project_path(p_name)
            self.assertIsNotNone(path)
            self.assertTrue(os.path.exists(path))

    def test_sync_dry_run(self):
        try:
            ProjectService.scan_and_sync()
            success = True
        except Exception as e:
            print(f"Sync failed: {e}")
            success = False
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main()
