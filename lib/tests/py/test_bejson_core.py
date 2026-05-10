"""
Library:     test_bejson_core.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
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

# Add lib/py to path
LIB_PY_DIR = "/storage/7B30-0E0B/Core-Command/Lib/py"
if LIB_PY_DIR not in sys.path:
    sys.path.insert(0, LIB_PY_DIR)

from lib_bejson_core import (
    __bejson_core_atomic_backup as atomic_backup,
    __bejson_core_restore_backup as restore_backup,
    bejson_core_atomic_write,
    bejson_core_create_104,
    bejson_core_create_104a,
    bejson_core_create_104db,
    bejson_core_load_file,
    bejson_core_load_string,
    bejson_core_get_version,
    bejson_core_get_records_types,
    bejson_core_get_fields,
    bejson_core_get_field_index,
    bejson_core_get_field_def,
    bejson_core_get_field_count,
    bejson_core_get_record_count,
    bejson_core_get_value_at,
    bejson_core_get_record,
    bejson_core_get_field_values,
    bejson_core_query_records,
    bejson_core_query_records_advanced,
    bejson_core_get_records_by_type,
    bejson_core_has_record_type,
    bejson_core_get_field_applicability,
    bejson_core_set_value_at,
    bejson_core_add_record,
    bejson_core_remove_record,
    bejson_core_update_field,
    bejson_core_add_column,
    bejson_core_remove_column,
    bejson_core_rename_column,
    bejson_core_get_column,
    bejson_core_set_column,
    bejson_core_filter_rows,
    bejson_core_sort_by_field,
    bejson_core_pretty_print,
    bejson_core_compact_print,
    bejson_core_is_valid,
    bejson_core_get_stats,
    BEJSONCoreError
)

class TestBEJSONCore(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.sample_104 = bejson_core_create_104(
            "Test",
            [{"name": "id", "type": "string"}, {"name": "val", "type": "integer"}],
            [["a", 1], ["b", 2]]
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_document_creation(self):
        doc104 = bejson_core_create_104("MyType", [{"name":"f1","type":"string"}], [["v1"]])
        self.assertEqual(doc104["Format_Version"], "104")
        
        doc104a = bejson_core_create_104a("MyType", [], [], App_Name="TestApp")
        self.assertEqual(doc104a["Format_Version"], "104a")
        self.assertEqual(doc104a["App_Name"], "TestApp")
        
        doc104db = bejson_core_create_104db(["T1", "T2"], [{"name":"Record_Type_Parent","type":"string"}], [])
        self.assertEqual(doc104db["Format_Version"], "104db")

    def test_file_io_and_backup(self):
        path = os.path.join(self.test_dir, "test.bejson")
        bejson_core_atomic_write(path, self.sample_104)
        self.assertTrue(os.path.exists(path))
        
        # Test explicit backup function
        backup_path = atomic_backup(path)
        self.assertTrue(os.path.exists(backup_path))
        self.assertIn(".backup.", backup_path)
        
        # Test restore backup
        os.remove(path)
        self.assertFalse(os.path.exists(path))
        restore_backup(path, backup_path)
        self.assertTrue(os.path.exists(path))
        self.assertFalse(os.path.exists(backup_path))

        loaded = bejson_core_load_file(path)
        self.assertEqual(loaded["Values"], self.sample_104["Values"])

    def test_accessors(self):
        doc = self.sample_104
        self.assertEqual(bejson_core_get_version(doc), "104")
        self.assertEqual(bejson_core_get_records_types(doc), ["Test"])
        self.assertEqual(bejson_core_get_field_count(doc), 2)
        self.assertEqual(bejson_core_get_record_count(doc), 2)
        self.assertEqual(bejson_core_get_field_index(doc, "val"), 1)
        self.assertEqual(bejson_core_get_value_at(doc, 0, 1), 1)
        self.assertEqual(bejson_core_get_record(doc, 1), ["b", 2])
        self.assertEqual(bejson_core_get_field_values(doc, "id"), ["a", "b"])

    def test_querying(self):
        doc = self.sample_104
        self.assertEqual(bejson_core_query_records(doc, "id", "a"), [["a", 1]])
        self.assertEqual(bejson_core_query_records_advanced(doc, id="b", val=2), [["b", 2]])

    def test_mutation(self):
        doc = self.sample_104
        # Set value
        doc2 = bejson_core_set_value_at(doc, 0, 1, 10)
        self.assertEqual(bejson_core_get_value_at(doc2, 0, 1), 10)
        # Add record
        doc3 = bejson_core_add_record(doc, ["c", 3])
        self.assertEqual(bejson_core_get_record_count(doc3), 3)
        # Remove record
        doc4 = bejson_core_remove_record(doc, 0)
        self.assertEqual(bejson_core_get_record_count(doc4), 1)
        # Update field
        doc5 = bejson_core_update_field(doc, 1, "val", 20)
        self.assertEqual(bejson_core_get_value_at(doc5, 1, 1), 20)

    def test_table_ops(self):
        doc = self.sample_104
        # Add column
        doc2 = bejson_core_add_column(doc, "new", "string", "def")
        self.assertEqual(bejson_core_get_field_count(doc2), 3)
        self.assertEqual(bejson_core_get_value_at(doc2, 0, 2), "def")
        # Remove column
        doc3 = bejson_core_remove_column(doc, "val")
        self.assertEqual(bejson_core_get_field_count(doc3), 1)
        # Rename column
        doc4 = bejson_core_rename_column(doc, "id", "key")
        self.assertEqual(doc4["Fields"][0]["name"], "key")
        # Set column
        doc5 = bejson_core_set_column(doc, "val", [100, 200])
        self.assertEqual(bejson_core_get_field_values(doc5, "val"), [100, 200])
        # Sort
        doc6 = bejson_core_sort_by_field(doc, "val", ascending=False)
        self.assertEqual(bejson_core_get_record(doc6, 0), ["b", 2])

    def test_utility(self):
        doc = self.sample_104
        self.assertTrue(bejson_core_is_valid(doc))
        self.assertIn('"Format": "BEJSON"', bejson_core_pretty_print(doc))
        self.assertNotIn("\n", bejson_core_compact_print(doc))
        stats = bejson_core_get_stats(doc)
        self.assertEqual(stats["record_count"], 2)

if __name__ == "__main__":
    unittest.main()
