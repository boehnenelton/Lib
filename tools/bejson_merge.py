"""
Library:     bejson_merge.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Merge multiple BEJSON files into one.
             Supports concatenation, deduplication, and entity merging for 104db.
"""
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

LIB_DIR = os.path.dirname(os.path.abspath(__file__))
if LIB_DIR not in sys.path:
    sys.path.append(LIB_DIR)

from lib_bejson_core import (
    bejson_core_load_file,
    bejson_core_atomic_write,
    bejson_core_create_104,
    bejson_core_create_104a,
    bejson_core_create_104db,
    bejson_core_get_version,
    bejson_core_get_stats,
)
from lib_bejson_validator import bejson_validator_validate_file, BEJSONValidationError


class C:
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"


def record_hash(record):
    """Create a hash of a record for deduplication."""
    return hashlib.md5(json.dumps(record, sort_keys=True).encode()).hexdigest()


def merge_fields(fields_list, version):
    """Merge field definitions from multiple files.
    Returns combined fields with union of all field names.
    """
    seen = {}
    for fields in fields_list:
        for f in fields:
            name = f["name"]
            if name not in seen:
                seen[name] = f
            # If type differs, prefer the more permissive type
            elif seen[name]["type"] != f["type"]:
                # Upgrade integer→number, string stays
                if seen[name]["type"] == "integer" and f["type"] == "number":
                    seen[name]["type"] = "number"
    return list(seen.values())


def align_record(record, fields, doc_fields):
    """Align a record to new field positions.
    Returns a new list with values in the order of `fields`.
    """
    old_indices = {}
    for i, f in enumerate(doc_fields):
        old_indices[f["name"]] = i

    new_record = [None] * len(fields)
    for i, f in enumerate(fields):
        name = f["name"]
        if name in old_indices and old_indices[name] < len(record):
            new_record[i] = record[old_indices[name]]
    return new_record


def merge_104(files, dedup=False, entity_filter=None):
    """Merge BEJSON 104 files (single record type)."""
    docs = []
    all_records = []
    all_fields = []

    for fp in files:
        doc = bejson_core_load_file(fp)
        docs.append(doc)
        all_fields.append(doc["Fields"])
        all_records.extend(doc["Values"])

    if not docs:
        return None

    # Merge fields
    merged_fields = merge_fields(all_fields, "104")

    # Align all records to merged schema
    aligned = []
    for doc, records in [(d, d["Values"]) for d in docs]:
        for rec in records:
            aligned.append(align_record(rec, merged_fields, doc["Fields"]))

    # Deduplicate
    if dedup:
        seen = set()
        unique = []
        for rec in aligned:
            h = record_hash(rec)
            if h not in seen:
                seen.add(h)
                unique.append(rec)
        aligned = unique

    # Filter by entity if specified (104db files merged)
    if entity_filter:
        type_idx = -1
        for i, f in enumerate(merged_fields):
            if f["name"] == "Record_Type_Parent":
                type_idx = i
                break
        if type_idx >= 0:
            aligned = [r for r in aligned if r[type_idx] == entity_filter]

    # Determine record type name
    rt_name = docs[0]["Records_Type"][0]
    if version := docs[0]["Format_Version"] == "104a":
        # Collect custom headers from all files
        custom = {}
        mandatory = {"Format", "Format_Version", "Format_Creator", "Records_Type", "Fields", "Values"}
        for d in docs:
            for k, v in d.items():
                if k not in mandatory:
                    custom[k] = v
        doc = bejson_core_create_104a(rt_name, merged_fields, aligned, **custom)
    else:
        doc = bejson_core_create_104(rt_name, merged_fields, aligned)

    return doc


def merge_104db(files, dedup=False, entity_filter=None):
    """Merge BEJSON 104db files (multi-entity)."""
    docs = []
    all_entities = set()
    all_fields = []
    all_records = []

    for fp in files:
        doc = bejson_core_load_file(fp)
        if bejson_core_get_version(doc) != "104db":
            print(f"{C.YELLOW}⚠ Skipping non-104db file: {fp}{C.RESET}")
            continue
        docs.append(doc)
        all_entities.update(doc["Records_Type"])
        all_fields.append(doc["Fields"])
        all_records.extend(doc["Values"])

    if not docs:
        return None

    entities = sorted(all_entities)

    # Merge all field definitions
    merged_fields = merge_fields(all_fields, "104db")

    # Ensure Record_Type_Parent is first
    merged_fields.sort(key=lambda f: (0 if f["name"] == "Record_Type_Parent" else 1))

    # Align records
    aligned = []
    for doc in docs:
        for rec in doc["Values"]:
            aligned.append(align_record(rec, merged_fields, doc["Fields"]))

    # Deduplicate
    if dedup:
        seen = set()
        unique = []
        for rec in aligned:
            h = record_hash(rec)
            if h not in seen:
                seen.add(h)
                unique.append(rec)
        aligned = unique

    # Filter by entity
    if entity_filter:
        aligned = [r for r in aligned if r[0] == entity_filter]

    return bejson_core_create_104db(entities, merged_fields, aligned)


def main():
    ap = argparse.ArgumentParser(description="Merge BEJSON files")
    ap.add_argument("files", nargs="+", help="BEJSON files to merge")
    ap.add_argument("-o", "--output", required=True, help="Output merged file")
    ap.add_argument("--dedup", action="store_true", help="Remove duplicate records")
    ap.add_argument("--entity", help="Filter to specific entity type (104db)")
    args = ap.parse_args()

    # Validate inputs
    valid_files = []
    for fp in args.files:
        if not os.path.isfile(fp):
            print(f"{C.YELLOW}⚠ File not found: {fp}{C.RESET}")
            continue
        try:
            bejson_validator_validate_file(fp)
            valid_files.append(fp)
        except BEJSONValidationError as e:
            print(f"{C.YELLOW}⚠ Invalid BEJSON, skipping: {fp} ({e}){C.RESET}")

    if not valid_files:
        print(f"{C.YELLOW}✗ No valid BEJSON files to merge{C.RESET}")
        return 1

    # Detect version
    first_doc = bejson_core_load_file(valid_files[0])
    version = bejson_core_get_version(first_doc)

    print(f"{C.BOLD}Merging {len(valid_files)} files (version {version}){C.RESET}")

    if version == "104db":
        doc = merge_104db(valid_files, dedup=args.dedup, entity_filter=args.entity)
    else:
        doc = merge_104(valid_files, dedup=args.dedup, entity_filter=args.entity)

    if not doc:
        print(f"{C.YELLOW}✗ Merge produced no records{C.RESET}")
        return 1

    bejson_core_atomic_write(args.output, doc)
    stats = bejson_core_get_stats(doc)
    print(f"{C.GREEN}✓ Merged → {args.output}{C.RESET}")
    print(f"  Fields: {stats['field_count']}, Records: {stats['record_count']}")
    if version == "104db":
        print(f"  Entities: {', '.join(stats['records_types'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
