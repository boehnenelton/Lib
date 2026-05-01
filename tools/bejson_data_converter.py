"""
Library:     bejson_data_converter.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Convert CSV, TSV, plain JSON to BEJSON format.
"""
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from io import StringIO

LIB_DIR = os.path.dirname(os.path.abspath(__file__))
if LIB_DIR not in sys.path:
    sys.path.append(LIB_DIR)

from lib_bejson_core import (
    bejson_core_create_104,
    bejson_core_create_104a,
    bejson_core_create_104db,
    bejson_core_atomic_write,
)

# ─── Type inference ─────────────────────────────────────────────────────

def infer_type(value):
    """Infer BEJSON field type from a Python value."""
    if value is None or value == "":
        return "string"  # default for empty
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    # String — try parsing
    s = str(value).strip()
    if s.lower() in ("true", "false"):
        return "boolean"
    try:
        int(s)
        return "integer"
    except ValueError:
        pass
    try:
        float(s)
        return "number"
    except ValueError:
        pass
    # Try JSON array/object
    if s.startswith("[") or s.startswith("{"):
        try:
            parsed = json.loads(s)
            return "array" if isinstance(parsed, list) else "object"
        except json.JSONDecodeError:
            pass
    return "string"


def coerce_value(value, ftype):
    """Coerce a string value to the inferred BEJSON type."""
    if value is None or str(value).strip() == "":
        return None
    s = str(value).strip()
    if ftype == "boolean":
        return s.lower() == "true"
    if ftype == "integer":
        try:
            return int(s)
        except (ValueError, TypeError):
            return None
    if ftype == "number":
        try:
            return float(s)
        except (ValueError, TypeError):
            return None
    if ftype == "array":
        try:
            parsed = json.loads(s)
            return parsed if isinstance(parsed, list) else None
        except (json.JSONDecodeError, TypeError):
            return None
    if ftype == "object":
        try:
            parsed = json.loads(s)
            return parsed if isinstance(parsed, dict) else None
        except (json.JSONDecodeError, TypeError):
            return None
    return s


# ─── Parsers ─────────────────────────────────────────────────────────────

def parse_csv(filepath, delimiter=","):
    """Parse CSV/TSV file and return list of dicts."""
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        return list(reader)


def parse_json_array(filepath):
    """Parse JSON file — supports array of objects or BEJSON document."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        # If first element is a BEJSON-style dict with Format key, extract Values
        if data and isinstance(data[0], dict) and "Format" not in data[0]:
            return data  # Plain array of objects
        # Could be list of lists (Values format) — handled by caller
        return data
    elif isinstance(data, dict) and "Format" in data:
        # It's a BEJSON document — extract Values as dicts
        fields = [f["name"] for f in data["Fields"]]
        return [dict(zip(fields, row)) for row in data["Values"]]
    else:
        return []


# ─── Conversion ──────────────────────────────────────────────────────────

def to_bejson(records, version, record_type, entity_types=None):
    """Convert list of dicts to BEJSON document."""
    if not records:
        raise ValueError("No records to convert")

    # Infer field types from first record
    fields = []
    for key, val in records[0].items():
        ftype = infer_type(val)
        field = {"name": key, "type": ftype}
        fields.append(field)

    # Build values
    values = []
    for rec in records:
        row = []
        for f in fields:
            raw = rec.get(f["name"])
            row.append(coerce_value(raw, f["type"]))
        values.append(row)

    # Create document
    if version == "104":
        return bejson_core_create_104(record_type, fields, values)
    elif version == "104a":
        return bejson_core_create_104a(record_type, fields, values,
                                        Source="Converted", Schema_Version="v1.0")
    elif version == "104db":
        if not entity_types:
            entity_types = ["Record"]
        # For 104db: add Record_Type_Parent as first field
        fields_104db = [
            {"name": "Record_Type_Parent", "type": "string"},
        ]
        for f in fields:
            f["Record_Type_Parent"] = entity_types[0]
            fields_104db.append(f)
        # Prepend entity type to each row
        values_104db = [[entity_types[0]] + row for row in values]
        return bejson_core_create_104db(entity_types, fields_104db, values_104db)


def main():
    ap = argparse.ArgumentParser(description="Convert CSV/TSV/JSON to BEJSON")
    ap.add_argument("input", help="Input file (csv, tsv, json)")
    ap.add_argument("-o", "--output", help="Output BEJSON file")
    ap.add_argument("-v", "--version", default="104", choices=["104","104a","104db"])
    ap.add_argument("-t", "--record-type", default="Record")
    ap.add_argument("-d", "--delimiter", default=None, help="CSV delimiter (auto-detected if not set)")
    args = ap.parse_args()

    # Determine format
    ext = Path(args.input).suffix.lower()
    if ext in (".csv", ".tsv"):
        delim = args.delimiter or ("\t" if ext == ".tsv" else ",")
        records = parse_csv(args.input, delimiter=delim)
    elif ext == ".json":
        records = parse_json_array(args.input)
    else:
        # Try CSV by default
        records = parse_csv(args.input, delimiter=args.delimiter or ",")

    if not records:
        print("✗ No records found in input")
        return 1

    # Determine entities for 104db
    entities = None
    if args.version == "104db":
        entities = [args.record_type]

    # Convert
    doc = to_bejson(records, args.version, args.record_type, entity_types=entities)

    # Write
    output = args.output or Path(args.input).stem + ".bejson.json"
    bejson_core_atomic_write(output, doc)
    print(f"✓ Converted {len(records)} records → {output}")
    print(f"  Version: {args.version} | Fields: {len(doc['Fields'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
