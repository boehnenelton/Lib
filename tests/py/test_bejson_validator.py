"""
Library:     test_bejson_validator.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.5)
Author:      Elton Boehnen
Version:     1.5 OFFICIAL
Date:        2026-05-01
Description: Core-Command library component.
"""
import os
import sys
import json
import unittest
import tempfile
from pathlib import Path

# Add lib/py to path
LIB_PY_DIR = "/storage/7B30-0E0B/Core-Command/Lib/py"
if LIB_PY_DIR not in sys.path:
    sys.path.insert(0, LIB_PY_DIR)

from lib_bejson_validator import (
    bejson_validator_reset_state,
    bejson_validator_get_errors,
    bejson_validator_get_warnings,
    bejson_validator_has_errors,
    bejson_validator_has_warnings,
    bejson_validator_error_count,
    bejson_validator_warning_count,
    bejson_validator_check_dependencies,
    bejson_validator_check_json_syntax,
    bejson_validator_check_mandatory_keys,
    bejson_validator_check_fields_structure,
    bejson_validator_check_records_type,
    bejson_validator_check_record_type_parent,
    bejson_validator_check_values,
    bejson_validator_check_custom_headers,
    bejson_validator_validate_string,
    bejson_validator_validate_file,
    bejson_validator_get_report,
    BEJSONValidationError
)

class TestBEJSONValidator(unittest.TestCase):
    def setUp(self):
        bejson_validator_reset_state()
        self.valid_104 = {
            "Format": "BEJSON",
            "Format_Version": "104",
            "Format_Creator": "Elton Boehnen",
            "Records_Type": ["Test"],
            "Fields": [{"name": "id", "type": "string"}, {"name": "val", "type": "integer"}],
            "Values": [["a", 1], ["b", 2]]
        }
        self.valid_104a = {
            "Format": "BEJSON",
            "Format_Version": "104a",
            "Format_Creator": "Elton Boehnen",
            "Custom_Header": "Hello",
            "Records_Type": ["Config"],
            "Fields": [{"name": "key", "type": "string"}],
            "Values": [["opt1"]]
        }
        self.valid_104db = {
            "Format": "BEJSON",
            "Format_Version": "104db",
            "Format_Creator": "Elton Boehnen",
            "Records_Type": ["User", "Order"],
            "Fields": [
                {"name": "Record_Type_Parent", "type": "string"},
                {"name": "id", "type": "string", "Record_Type_Parent": "common"},
                {"name": "name", "type": "string", "Record_Type_Parent": "User"},
                {"name": "amount", "type": "number", "Record_Type_Parent": "Order"}
            ],
            "Values": [
                ["User", "u1", "Alice", None],
                ["Order", "o1", None, 99.99]
            ]
        }

    def test_state_management(self):
        self.assertFalse(bejson_validator_has_errors())
        try:
            bejson_validator_validate_string("invalid json")
        except BEJSONValidationError:
            pass
        self.assertTrue(bejson_validator_has_errors())
        bejson_validator_reset_state()
        self.assertFalse(bejson_validator_has_errors())
        self.assertEqual(bejson_validator_error_count(), 0)

    def test_json_syntax(self):
        self.assertIsInstance(bejson_validator_check_json_syntax('{"a":1}'), dict)
        with self.assertRaises(BEJSONValidationError):
            bejson_validator_check_json_syntax('{"a":1')

    def test_mandatory_keys(self):
        data = self.valid_104.copy()
        self.assertEqual(bejson_validator_check_mandatory_keys(data), "104")
        del data["Format"]
        with self.assertRaises(BEJSONValidationError):
            bejson_validator_check_mandatory_keys(data)

    def test_fields_structure(self):
        self.assertEqual(bejson_validator_check_fields_structure(self.valid_104, "104"), 2)
        bad_fields = self.valid_104.copy()
        bad_fields["Fields"] = [{"no_name": "x"}]
        with self.assertRaises(BEJSONValidationError):
            bejson_validator_check_fields_structure(bad_fields, "104")

    def test_records_type(self):
        # Should not raise
        bejson_validator_check_records_type(self.valid_104, "104")
        bad = self.valid_104.copy()
        bad["Records_Type"] = []
        with self.assertRaises(BEJSONValidationError):
            bejson_validator_check_records_type(bad, "104")

    def test_104db_constraints(self):
        # Should not raise
        bejson_validator_check_record_type_parent(self.valid_104db)
        # 104db must have Record_Type_Parent as first field
        bad = self.valid_104db.copy()
        bad["Fields"] = bad["Fields"][1:] 
        with self.assertRaises(BEJSONValidationError):
            bejson_validator_check_record_type_parent(bad)

    def test_values_validation(self):
        # Should not raise
        bejson_validator_check_values(self.valid_104, "104", 2)
        # Type mismatch
        bad = self.valid_104.copy()
        bad["Values"] = [["a", "not an int"]]
        with self.assertRaises(BEJSONValidationError):
            bejson_validator_check_values(bad, "104", 2)
        # Length mismatch
        bad["Values"] = [["a"]]
        with self.assertRaises(BEJSONValidationError):
            bejson_validator_check_values(bad, "104", 2)

    def test_custom_headers(self):
        # Should not raise
        bejson_validator_check_custom_headers(self.valid_104a, "104a")
        # 104 cannot have custom headers
        bad = self.valid_104.copy()
        bad["Illegal"] = 1
        with self.assertRaises(BEJSONValidationError):
            bejson_validator_check_custom_headers(bad, "104")

    def test_validate_string(self):
        self.assertTrue(bejson_validator_validate_string(json.dumps(self.valid_104)))
        with self.assertRaises(BEJSONValidationError):
            bejson_validator_validate_string('{"bad": "json"}')

    def test_validate_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bejson', delete=False) as tf:
            json.dump(self.valid_104, tf)
            temp_name = tf.name
        try:
            self.assertTrue(bejson_validator_validate_file(temp_name))
        finally:
            if os.path.exists(temp_name):
                os.remove(temp_name)

    def test_get_report(self):
        json_str = json.dumps(self.valid_104)
        report = bejson_validator_get_report(json_str)
        self.assertIn("BEJSON Validation Report", report)
        self.assertIn("Status: VALID", report)
        
        bad_str = '{"bad": "json"}'
        report_bad = bejson_validator_get_report(bad_str)
        self.assertIn("Status: INVALID", report_bad)

if __name__ == "__main__":
    unittest.main()
