"""
Library:     test_mfdb_core.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
MFDB Version: 1.3.1
Author:      Elton Boehnen
Version:     1.3 OFFICIAL
Date:        2026-05-01
Description: Core-Command library component.
"""
import os
import sys
import json
import unittest
import tempfile
import shutil
from pathlib import Path

LIB_PY_DIR = "/storage/7B30-0E0B/Core-Command/Lib/py"
if LIB_PY_DIR not in sys.path:
    sys.path.insert(0, LIB_PY_DIR)

from lib_mfdb_core import (
    mfdb_core_create_database,
    mfdb_core_load_manifest,
    mfdb_core_load_entity,
    mfdb_core_add_entity_record,
    mfdb_core_discover,
    MFDBCoreError
)

class TestMFDBCore(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.entities = [
            {
                "name": "User",
                "fields": [{"name": "id", "type": "string"}, {"name": "name", "type": "string"}],
                "primary_key": "id"
            },
            {
                "name": "Order",
                "fields": [{"name": "id", "type": "string"}, {"name": "user_id", "type": "string"}],
                "primary_key": "id"
            }
        ]
        self.manifest_path = mfdb_core_create_database(
            self.test_dir, "TestDB", self.entities, "A test database"
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_database_creation(self):
        self.assertTrue(os.path.exists(self.manifest_path))
        manifest = mfdb_core_load_manifest(self.manifest_path)
        self.assertEqual(len(manifest), 2)
        self.assertEqual(manifest[0]["entity_name"], "User")

    def test_discovery(self):
        self.assertEqual(mfdb_core_discover(self.manifest_path), "manifest")
        user_path = os.path.join(self.test_dir, "data", "user.bejson")
        self.assertEqual(mfdb_core_discover(user_path), "entity")

    def test_entity_ops(self):
        # Add record
        mfdb_core_add_entity_record(self.manifest_path, "User", ["u1", "Alice"])
        users = mfdb_core_load_entity(self.manifest_path, "User")
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["name"], "Alice")
        
        # Verify manifest count sync
        manifest = mfdb_core_load_manifest(self.manifest_path)
        user_entry = next(e for e in manifest if e["entity_name"] == "User")
        self.assertEqual(user_entry["record_count"], 1)

if __name__ == "__main__":
    unittest.main()
