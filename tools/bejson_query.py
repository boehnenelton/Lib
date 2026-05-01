"""
Library:     bejson_query.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Interactive query builder for BEJSON 104db databases.
             Supports multi-entity queries, joins, and filtering.
"""
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path

LIB_DIR = os.path.dirname(os.path.abspath(__file__))
if LIB_DIR not in sys.path:
    sys.path.append(LIB_DIR)

from lib_bejson_core import (
    bejson_core_load_file,
    bejson_core_get_version,
    bejson_core_get_stats,
    bejson_core_get_records_by_type,
    bejson_core_get_field_index,
    bejson_core_query_records,
    bejson_core_get_field_values,
    BEJSONCoreError,
)

class C:
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    RED    = "\033[91m"
    RESET  = "\033[0m"


def stats(doc):
    """Print detailed statistics about a BEJSON document."""
    s = bejson_core_get_stats(doc)
    version = bejson_core_get_version(doc)

    print(f"\n{C.BOLD}{C.BLUE}{'='*50}{C.RESET}")
    print(f"{C.BOLD}  BEJSON Database Statistics{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}{'='*50}{C.RESET}\n")
    print(f"  Version:        {C.BOLD}{version}{C.RESET}")
    print(f"  Record Types:   {C.BOLD}{', '.join(s['records_types'])}{C.RESET}")
    print(f"  Total Fields:   {C.BOLD}{s['field_count']}{C.RESET}")
    print(f"  Total Records:  {C.BOLD}{s['record_count']}{C.RESET}")

    # Per-entity stats for 104db
    if version == "104db":
        print(f"\n  {C.BOLD}Per-Entity Record Counts:{C.RESET}")
        for etype in s["records_types"]:
            count = len(bejson_core_get_records_by_type(doc, etype))
            print(f"    {C.GREEN}{etype}{C.RESET}: {C.BOLD}{count}{C.RESET}")

    # Field detail
    print(f"\n  {C.BOLD}Schema:{C.RESET}")
    for i, f in enumerate(doc["Fields"]):
        parent = f.get("Record_Type_Parent", "")
        ps = f" ({C.CYAN}{parent}{C.RESET})" if parent else ""
        print(f"    {i:3d}. {C.GREEN}{f['name']:<30s}{C.RESET} {f['type']}{ps}")

    # Non-null value counts
    print(f"\n  {C.BOLD}Non-Null Value Counts:{C.RESET}")
    fnames = [f["name"] for f in doc["Fields"]]
    for i in range(len(doc["Fields"])):
        non_null = sum(1 for r in doc["Values"] if r[i] is not None)
        pct = f"{non_null}/{s['record_count']}"
        bar_len = int((non_null / max(s['record_count'], 1)) * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        print(f"    {C.GREEN}{fnames[i]:<30s}{C.RESET} {bar} {pct}")

    print()


def interactive_query(doc):
    """Interactive query mode."""
    version = bejson_core_get_version(doc)
    fnames = [f["name"] for f in doc["Fields"]]

    print(f"\n{C.BOLD}{C.BLUE}{'='*50}{C.RESET}")
    print(f"{C.BOLD}  Interactive Query Mode{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}{'='*50}{C.RESET}\n")

    # Show entities (for 104db)
    if version == "104db":
        print(f"{C.BOLD}Available Entities:{C.RESET}")
        for et in doc["Records_Type"]:
            count = len(bejson_core_get_records_by_type(doc, et))
            print(f"  {C.GREEN}{et}{C.RESET} ({count} records)")
        print()

    while True:
        entity = None
        if version == "104db":
            entity = input(f"{C.CYAN}Entity (or blank for all){C.RESET}: ").strip()
            if not entity:
                entity = None
            elif entity not in doc["Records_Type"]:
                print(f"{C.YELLOW}⚠ Unknown entity: {entity}{C.RESET}")
                continue

        print(f"\n{C.BOLD}Available Fields:{C.RESET}")
        for i, f in enumerate(doc["Fields"]):
            if entity and f.get("Record_Type_Parent", "") not in (entity, ""):
                continue
            print(f"  {i:3d}. {C.GREEN}{f['name']}{C.RESET} ({f['type']})")

        field = input(f"\n{C.CYAN}Field to query{C.RESET}: ").strip()
        if not field or field == "exit" or field == "quit":
            break

        if field not in fnames:
            print(f"{C.YELLOW}⚠ Unknown field: {field}{C.RESET}")
            continue

        value_str = input(f"{C.CYAN}Value (JSON-parseable){C.RESET}: ").strip()
        try:
            value = json.loads(value_str)
        except (json.JSONDecodeError, TypeError):
            value = value_str

        # Execute query
        try:
            if entity:
                recs = bejson_core_get_records_by_type(doc, entity)
                idx = bejson_core_get_field_index(doc, field)
                results = [r for r in recs if r[idx] == value]
            else:
                results = bejson_core_query_records(doc, field, value)
        except BEJSONCoreError as e:
            print(f"{C.RED}✗ Query error: {e}{C.RESET}")
            continue

        if not results:
            print(f"{C.YELLOW}⚠ No results found{C.RESET}")
            continue

        print(f"\n{C.GREEN}✓ Found {len(results)} record(s){C.RESET}\n")
        for i, rec in enumerate(results):
            print(f"  {C.BOLD}[{i}]{C.RESET}")
            for j, v in enumerate(rec):
                if v is not None:
                    print(f"    {C.GREEN}{fnames[j]}{C.RESET}: {json.dumps(v)}")
            print()


def export_csv(doc, output_path, entity_filter=None):
    """Export BEJSON to CSV."""
    records = doc["Values"]
    if entity_filter:
        idx = bejson_core_get_field_index(doc, "Record_Type_Parent")
        records = [r for r in records if r[idx] == entity_filter]

    fnames = [f["name"] for f in doc["Fields"]]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(fnames)
        for rec in records:
            writer.writerow([json.dumps(v) if isinstance(v, (list, dict)) else v for v in rec])
    print(f"{C.GREEN}✓ Exported {len(records)} records → {output_path}{C.RESET}")


def do_join(doc, join_spec):
    """
    Perform a simple join between entities.
    Format: Entity1:Entity2:join_field (e.g. User:Item:owner_user_id_fk)
    """
    parts = join_spec.split(":")
    if len(parts) != 3:
        print(f"{C.RED}✗ Join spec must be Entity1:Entity2:join_field{C.RESET}")
        return

    entity1, entity2, join_field = parts
    fnames = [f["name"] for f in doc["Fields"]]

    # Get join field indices
    try:
        jf_idx = bejson_core_get_field_index(doc, join_field)
    except BEJSONCoreError:
        print(f"{C.RED}✗ Join field not found: {join_field}{C.RESET}")
        return

    # Find the primary key field in entity2
    # (We assume it's the second field for entity2, typically *_id)
    e2_records = bejson_core_get_records_by_type(doc, entity2)
    e1_records = bejson_core_get_records_by_type(doc, entity1)

    if not e2_records:
        print(f"{C.YELLOW}⚠ No records for {entity2}{C.RESET}")
        return

    # Build lookup: entity2's join_field value → entity2 record
    e2_lookup = {}
    for r in e2_records:
        key_val = r[jf_idx]
        if key_val is not None:
            e2_lookup[key_val] = r

    # Join: find entity1 records that match
    # We need to find which field in entity1 references entity2
    # Look for fields ending in _fk in entity1
    fk_fields = []
    for i, f in enumerate(doc["Fields"]):
        if f.get("Record_Type_Parent") == entity1 and f["name"].endswith("_fk"):
            fk_fields.append((i, f["name"]))

    if not fk_fields:
        print(f"{C.YELLOW}⚠ No foreign key fields found in {entity1}{C.RESET}")
        print(f"  Convention: use field names ending in '_fk' (e.g. {entity2.lower()}_id_fk)")
        return

    # Try each FK field
    for fk_idx, fk_name in fk_fields:
        matches = []
        for r1 in e1_records:
            fk_val = r1[fk_idx]
            if fk_val in e2_lookup:
                matches.append((r1, e2_lookup[fk_val]))

        if matches:
            print(f"\n{C.BOLD}{C.BLUE}Join: {entity1} → {entity2} via {fk_name}{C.RESET}")
            print(f"{C.BOLD}{C.BLUE}{'='*50}{C.RESET}\n")
            for i, (r1, r2) in enumerate(matches):
                print(f"  {C.BOLD}Match {i+1}:{C.RESET}")
                # Print entity1 fields
                for j, v in enumerate(r1):
                    if v is not None and j > 0:  # Skip RTP
                        print(f"    {C.GREEN}{entity1}.{fnames[j]}{C.RESET}: {json.dumps(v)}")
                # Print matched entity2 fields
                for j, v in enumerate(r2):
                    if v is not None and j > 0:
                        print(f"    {C.CYAN}{entity2}.{fnames[j]}{C.RESET}: {json.dumps(v)}")
                print()
            return

    print(f"{C.YELLOW}⚠ No matches found for any FK field{C.RESET}")


def main():
    ap = argparse.ArgumentParser(description="BEJSON Query Tool")
    ap.add_argument("file", help="BEJSON file")
    ap.add_argument("-e", "--entity", help="Entity type (104db)")
    ap.add_argument("-f", "--field", help="Field to query")
    ap.add_argument("-v", "--value", help="Value to match")
    ap.add_argument("--stats", action="store_true", help="Show detailed statistics")
    ap.add_argument("--export-csv", help="Export to CSV (output path)")
    ap.add_argument("--join", help="Join spec: Entity1:Entity2:join_field")
    args = ap.parse_args()

    doc = bejson_core_load_file(args.file)

    if args.stats:
        stats(doc)
        return 0

    if args.export_csv:
        export_csv(doc, args.export_csv, entity_filter=args.entity)
        return 0

    if args.join:
        do_join(doc, args.join)
        return 0

    if args.field and args.value:
        # Non-interactive query
        try:
            value = json.loads(args.value)
        except (json.JSONDecodeError, TypeError):
            value = args.value

        if args.entity:
            recs = bejson_core_get_records_by_type(doc, args.entity)
            idx = bejson_core_get_field_index(doc, args.field)
            results = [r for r in recs if r[idx] == value]
        else:
            results = bejson_core_query_records(doc, args.field, value)

        fnames = [f["name"] for f in doc["Fields"]]
        if not results:
            print(f"{C.YELLOW}⚠ No results{C.RESET}")
            return 0

        print(f"{C.GREEN}✓ {len(results)} record(s){C.RESET}")
        for i, rec in enumerate(results):
            print(f"\n{C.BOLD}[{i}]{C.RESET}")
            for j, v in enumerate(rec):
                if v is not None:
                    print(f"  {C.GREEN}{fnames[j]}{C.RESET}: {json.dumps(v)}")
        return 0

    # Default: interactive mode
    interactive_query(doc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
