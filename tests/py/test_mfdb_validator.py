"""
Library:     test_mfdb_validator.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.3 OFFICIAL
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

from lib_mfdb_core import mfdb_core_create_database
from lib_mfdb_validator import (
    mfdb_validator_validate_manifest,
    mfdb_validator_validate_entity_file,
    mfdb_validator_validate_database,
    MFDBValidationError
)

class TestMFDBValidator(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.entities = [
            {
                "name": "User",
                "fields": [{"name": "id", "type": "string"}, {"name": "name", "type": "string"}],
                "primary_key": "id"
            }
        ]
        self.manifest_path = mfdb_core_create_database(
            self.test_dir, "TestDB", self.entities, "A test database"
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_manifest_validation(self):
        # Should not raise
        self.assertTrue(mfdb_validator_validate_manifest(self.manifest_path))

    def test_entity_validation(self):
        user_path = os.path.join(self.test_dir, "data", "user.bejson")
        # Should not raise
        self.assertTrue(mfdb_validator_validate_entity_file(user_path, self.manifest_path))

    def test_database_validation(self):
        # Should not raise
        self.assertTrue(mfdb_validator_validate_database(self.manifest_path))

if __name__ == "__main__":
    unittest.main()
