#!/usr/bin/env python3
"""
CLI Tool:    cli_bejson_validator.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Author:      Gemini CLI / Elton Boehnen
Version:     1.0.0
Description: Command-line validator for BEJSON files (104, 104a, 104db).
Usage:       python3 cli_bejson_validator.py <file_path> [--json]
"""
import sys
import os
import json
import argparse
from pathlib import Path

# Add lib/py to sys.path to import the validator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'py')))

try:
    import lib_bejson_validator as validator
except ImportError:
    print("Error: Could not find 'lib_bejson_validator.py' in lib/py/")
    sys.exit(1)

def validate_file(file_path, json_output=False):
    path = Path(file_path)
    if not path.exists():
        res = {"status": "ERROR", "file": str(file_path), "message": "File not found"}
        if json_output: print(json.dumps(res))
        else: print(f"FAIL: {file_path} (File not found)")
        return False

    try:
        is_valid = validator.bejson_validator_validate_file(str(path))
        res = {
            "status": "VALID" if is_valid else "INVALID",
            "file": str(file_path),
            "version": None # Logic to extract version could be added
        }
        
        # Read the file to get version for reporting
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                res["version"] = data.get("Format_Version")
        except: pass

        if json_output:
            print(json.dumps(res))
        else:
            v_str = f" [v{res['version']}]" if res["version"] else ""
            print(f"PASS: {file_path}{v_str}")
        return True

    except validator.BEJSONValidationError as e:
        res = {
            "status": "INVALID",
            "file": str(file_path),
            "error": str(e),
            "code": e.code
        }
        if json_output:
            print(json.dumps(res))
        else:
            print(f"FAIL: {file_path}")
            print(f"      Error: {e}")
        return False
    except Exception as e:
        res = {
            "status": "ERROR",
            "file": str(file_path),
            "message": str(e)
        }
        if json_output:
            print(json.dumps(res))
        else:
            print(f"CRITICAL ERROR: {file_path}")
            print(f"               {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="BEJSON CLI Validator")
    parser.add_argument("files", nargs="+", help="One or more BEJSON files to validate")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    
    args = parser.parse_args()

    overall_success = True
    for f in args.files:
        if not validate_file(f, args.json):
            overall_success = False

    sys.exit(0 if overall_success else 1)

if __name__ == "__main__":
    main()
