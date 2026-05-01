"""
Library:     test_bejson_parse.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Core-Command library component.
"""
import os
import sys
import unittest
import tempfile
import shutil
import json

LIB_PY_DIR = "/storage/7B30-0E0B/Core-Command/Lib/py"
if LIB_PY_DIR not in sys.path:
    sys.path.insert(0, LIB_PY_DIR)

from lib_bejson_parse import parse_json, extract_data, save_files

class TestBEJSONParse(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.sample_104 = {
            "Format": "BEJSON",
            "Format_Version": "104",
            "Format_Creator": "Elton",
            "Records_Type": ["File"],
            "Fields": [
                {"name": "file1name", "type": "string"},
                {"name": "file1content", "type": "string"}
            ],
            "Values": [
                ["test.txt", "Hello World"]
            ]
        }

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_parse_json(self):
        res = parse_json(json.dumps(self.sample_104))
        self.assertEqual(res["Format"], "BEJSON")

    def test_extract_data(self):
        proj, files = extract_data(self.sample_104)
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["content"], "Hello World")

    def test_save_files(self):
        data = parse_json(json.dumps(self.sample_104))
        proj, files = extract_data(data)
        out_path = os.path.join(self.test_dir, "output")
        save_res = save_files(proj, files, {"output_path": out_path, "overwrite_enabled": True})
        self.assertTrue(save_res["success"])
        # save_files creates a subdir for the project name
        self.assertTrue(os.path.exists(os.path.join(out_path, proj, "test.txt")))

if __name__ == "__main__":
    unittest.main()
