"""
Library:     test_be_core.py
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
import tempfile
import shutil

LIB_PY_DIR = "/storage/7B30-0E0B/Core-Command/Lib/py"
if LIB_PY_DIR not in sys.path:
    sys.path.insert(0, LIB_PY_DIR)

from lib_be_core import get_bec_root, save_state, load_state

class TestBECoreSystem(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        os.environ["BEC_ROOT"] = self.test_dir

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        if "BEC_ROOT" in os.environ:
            del os.environ["BEC_ROOT"]

    def test_get_root(self):
        root = get_bec_root()
        self.assertEqual(root, self.test_dir)

    def test_state_management(self):
        save_state("test", "key", "value")
        save_state("test", "num", "123")
        
        val = load_state("test", "key")
        self.assertEqual(val, "value")
        
        num = load_state("test", "num")
        self.assertEqual(num, "123")

if __name__ == "__main__":
    unittest.main()
