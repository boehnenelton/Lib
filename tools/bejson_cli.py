"""
Library:     bejson_cli.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Unified CLI interface for all BEJSON operations.
             Create, validate, query, modify, and inspect BEJSON files.
"""
"""

import argparse
import json
import os
import sys
from pathlib import Path

LIB_DIR = os.path.dirname(os.path.abspath(__file__))
if LIB_DIR not in sys.path:
    sys.path.append(LIB_DIR)

from lib_bejson_core import (
    bejson_core_create_104,
    bejson_core_create_104a,
    bejson_core_create_104db,
    bejson_core_load_file,
    bejson_core_atomic_write,
    bejson_core_get_stats,
    bejson_core_get_field_index,
    bejson_core_get_field_values,
    bejson_core_query_records,
    bejson_core_query_records_advanced,
    bejson_core_add_record,
    bejson_core_remove_record,
    bejson_core_update_field,
    bejson_core_add_column,
    bejson_core_remove_column,
    bejson_core_rename_column,
    bejson_core_sort_by_field,
    bejson_core_get_records_by_type,
    bejson_core_pretty_print,
    bejson_core_is_valid,
    BEJSONCoreError,
)
from lib_bejson_validator import (
    bejson_validator_validate_file,
    bejson_validator_validate_string,
    bejson_validator_get_report,
    BEJSONValidationError,
)
from lib_bejson_parse import parse_json, extract_data, save_files

# ─── Color helpers ───────────────────────────────────────────────────────

class C:
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"

def ok(m):     print(f"{C.GREEN}✓ {m}{C.RESET}")
def warn(m):   print(f"{C.YELLOW}⚠ {m}{C.RESET}")
def err(m):    print(f"{C.RED}✗ {m}{C.RESET}")
def info(m):   print(f"{C.CYAN}ℹ {m}{C.RESET}")
def hdr(m):
    print(f"\n{C.BOLD}{C.BLUE}{'='*60}{C.RESET}")
    print(f"{C.BOLD}{m}{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}{'='*60}{C.RESET}\n")

# ─── Commands ────────────────────────────────────────────────────────────

def cmd_validate(args):
    all_ok = True
    for fp in args.files:
        if not os.path.isfile(fp):
            err(f"File not found: {fp}")
            all_ok = False
            continue
        try:
            bejson_validator_validate_file(fp)
            ok(f"VALID: {fp}")
        except BEJSONValidationError as e:
            err(f"INVALID: {fp} — {e}")
            try:
                report = bejson_validator_get_report(Path(fp).read_text(), is_file=True)
                print(report)
            except Exception:
                pass
            all_ok = False
    return 0 if all_ok else 1

def cmd_create(args):
    fields_src = args.fields
    if os.path.isfile(fields_src):
        fields = json.loads(Path(fields_src).read_text())
    else:
        fields = json.loads(fields_src)

    v = args.version
    if v == "104":
        doc = bejson_core_create_104(args.records_type, fields, [])
    elif v == "104a":
        custom = {}
        if args.custom_headers:
            for kv in args.custom_headers:
                k, val = kv.split("=", 1)
                custom[k] = val
        doc = bejson_core_create_104a(args.records_type, fields, [], **custom)
    elif v == "104db":
        types = [t.strip() for t in args.records_type.split(",")]
        doc = bejson_core_create_104db(types, fields, [])
    else:
        err(f"Unknown version: {v}")
        return 1

    bejson_core_atomic_write(args.output, doc)
    ok(f"Created {v} BEJSON: {args.output}")
    info(f"Fields: {len(fields)}, Records: 0")
    return 0

def cmd_info(args):
    doc = bejson_core_load_file(args.file)
    s = bejson_core_get_stats(doc)
    hdr("BEJSON File Info")
    print(f"  Version:       {C.BOLD}{s['version']}{C.RESET}")
    print(f"  Record Types:  {C.BOLD}{', '.join(s['records_types'])}{C.RESET}")
    print(f"  Fields:        {C.BOLD}{s['field_count']}{C.RESET}")
    print(f"  Records:       {C.BOLD}{s['record_count']}{C.RESET}")

    if args.verbose:
        print(f"\n{C.BOLD}Fields:{C.RESET}")
        for i, f in enumerate(doc["Fields"]):
            p = f.get("Record_Type_Parent", "")
            ps = f" ({C.CYAN}{p}{C.RESET})" if p else ""
            print(f"  {i}. {C.GREEN}{f['name']}{C.RESET} ({f['type']}){ps}")
        if 0 < s["record_count"] <= 5:
            print(f"\n{C.BOLD}Records (preview):{C.RESET}")
            fnames = [f["name"] for f in doc["Fields"]]
            for i, rec in enumerate(doc["Values"]):
                print(f"\n  [{i}]")
                for j, val in enumerate(rec):
                    if val is not None:
                        print(f"    {fnames[j]}: {json.dumps(val)}")
    return 0

def cmd_query(args):
    doc = bejson_core_load_file(args.file)
    val = args.value
    try:
        val = json.loads(val)
    except (json.JSONDecodeError, TypeError):
        pass

    if args.entity:
        recs = bejson_core_get_records_by_type(doc, args.entity)
        if not recs:
            warn(f"No records for entity: {args.entity}")
            return 0
        idx = bejson_core_get_field_index(doc, args.field)
        results = [r for r in recs if r[idx] == val]
    else:
        results = bejson_core_query_records(doc, args.field, val)

    if not results:
        warn(f"No records where {args.field} == {val}")
        return 0

    hdr(f"Query Results ({len(results)} records)")
    fnames = [f["name"] for f in doc["Fields"]]
    for i, rec in enumerate(results):
        print(f"\n{C.BOLD}Record {i}:{C.RESET}")
        for j, v in enumerate(rec):
            if v is not None:
                print(f"  {C.GREEN}{fnames[j]}{C.RESET}: {json.dumps(v)}")
    return 0

def cmd_add(args):
    doc = bejson_core_load_file(args.file)
    try:
        values = json.loads(args.record)
    except json.JSONDecodeError:
        err("Record must be valid JSON array, e.g. ['val1', 'val2', null]")
        return 1
    if not isinstance(values, list):
        err("Record must be a JSON array")
        return 1
    if len(values) != len(doc["Fields"]):
        err(f"Need {len(doc['Fields'])} values (one per field), got {len(values)}")
        return 1
    doc = bejson_core_add_record(doc, values)
    bejson_core_atomic_write(args.file, doc)
    ok(f"Record added. Total: {len(doc['Values'])}")
    return 0

def cmd_delete(args):
    doc = bejson_core_load_file(args.file)
    idx = args.index
    if idx < 0 or idx >= len(doc["Values"]):
        err(f"Index {idx} out of bounds (0-{len(doc['Values'])-1})")
        return 1
    doc = bejson_core_remove_record(doc, idx)
    bejson_core_atomic_write(args.file, doc)
    ok(f"Record {idx} deleted. Total: {len(doc['Values'])}")
    return 0

def cmd_sort(args):
    doc = bejson_core_load_file(args.file)
    doc = bejson_core_sort_by_field(doc, args.field, ascending=not args.desc)
    bejson_core_atomic_write(args.file, doc)
    order = "DESC" if args.desc else "ASC"
    ok(f"Sorted by {args.field} ({order})")
    return 0

def cmd_export(args):
    doc = bejson_core_load_file(args.file)
    fnames = [f["name"] for f in doc["Fields"]]
    records = [dict(zip(fnames, rec)) for rec in doc["Values"]]
    out = args.output or args.file.replace(".bejson", ".json").replace(".bejson.json", ".json")
    Path(out).write_text(json.dumps(records, indent=2), encoding="utf-8")
    ok(f"Exported {len(records)} records → {out}")
    return 0

def cmd_import(args):
    data = json.loads(Path(args.file).read_text())
    if not isinstance(data, list) or not data:
        err("Input must be a non-empty JSON array of objects")
        return 1
    fields = []
    for key, val in data[0].items():
        if isinstance(val, bool):       ft = "boolean"
        elif isinstance(val, int):      ft = "integer"
        elif isinstance(val, float):    ft = "number"
        elif isinstance(val, list):     ft = "array"
        elif isinstance(val, dict):     ft = "object"
        else:                           ft = "string"
        fields.append({"name": key, "type": ft})
    values = [[obj.get(f["name"]) for f in fields] for obj in data]
    doc = bejson_core_create_104(args.records_type or "Imported", fields, values)
    out = args.output or args.file.replace(".json", ".bejson.json")
    bejson_core_atomic_write(out, doc)
    ok(f"Imported {len(values)} records → {out}")
    return 0

def cmd_diff(args):
    d1 = bejson_core_load_file(args.file1)
    d2 = bejson_core_load_file(args.file2)
    hdr("BEJSON Diff")

    v1, v2 = d1["Format_Version"], d2["Format_Version"]
    if v1 != v2: warn(f"Version: {v1} vs {v2}")
    else:        ok(f"Version: {v1}")

    f1 = {f["name"]: f for f in d1["Fields"]}
    f2 = {f["name"]: f for f in d2["Fields"]}
    only1 = set(f1) - set(f2)
    only2 = set(f2) - set(f1)
    common = set(f1) & set(f2)
    if only1: warn(f"Only in file1: {', '.join(sorted(only1))}")
    if only2: warn(f"Only in file2: {', '.join(sorted(only2))}")
    type_changes = [n for n in common if f1[n]["type"] != f2[n]["type"]]
    if type_changes: warn(f"Type changes: {', '.join(sorted(type_changes))}")

    r1, r2 = len(d1["Values"]), len(d2["Values"])
    print(f"\n  Records: {C.BOLD}{r1}{C.RESET} → {C.BOLD}{r2}{C.RESET} ({r2-r1:+d})")
    return 0

def cmd_pretty(args):
    doc = bejson_core_load_file(args.file)
    print(bejson_core_pretty_print(doc))
    return 0

def cmd_parse(args):
    text = Path(args.file).read_text()
    try:
        data = parse_json(text)
    except json.JSONDecodeError as e:
        err(f"JSON parse failed: {e}")
        return 1
    proj, files = extract_data(data)
    info(f"Project: {proj} | Files: {len(files)}")
    cfg = {"output_path": args.output or "./output", "overwrite_enabled": args.overwrite}
    result = save_files(proj, files, cfg)
    if result["success"]:
        ok(f"Saved to {result['path']} ({result['file_count']} files)")
    else:
        err(f"Failed: {result['message']}")
        return 1
    return 0

# ─── Main ────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(prog="bejson", description="BEJSON CLI")
    sub = p.add_subparsers(dest="cmd")

    # validate
    a = sub.add_parser("validate", help="Validate BEJSON file(s)")
    a.add_argument("files", nargs="+")

    # create
    a = sub.add_parser("create", help="Create new BEJSON")
    a.add_argument("-v", "--version", required=True, choices=["104","104a","104db"])
    a.add_argument("-t", "--records-type", required=True)
    a.add_argument("-f", "--fields", required=True)
    a.add_argument("-o", "--output", required=True)
    a.add_argument("-c", "--custom-headers", nargs="*")

    # info
    a = sub.add_parser("info", help="Show file stats")
    a.add_argument("file")
    a.add_argument("-v", "--verbose", action="store_true")

    # query
    a = sub.add_parser("query", help="Query records")
    a.add_argument("file")
    a.add_argument("field")
    a.add_argument("value")
    a.add_argument("-e", "--entity")

    # add
    a = sub.add_parser("add", help="Add a record")
    a.add_argument("file")
    a.add_argument("record")

    # delete
    a = sub.add_parser("delete", help="Delete record by index")
    a.add_argument("file")
    a.add_argument("index", type=int)

    # sort
    a = sub.add_parser("sort", help="Sort by field")
    a.add_argument("file")
    a.add_argument("field")
    a.add_argument("-d", "--desc", action="store_true")

    # export
    a = sub.add_parser("export", help="Export to plain JSON")
    a.add_argument("file")
    a.add_argument("-o", "--output")

    # import
    a = sub.add_parser("import", help="Import JSON array")
    a.add_argument("file")
    a.add_argument("-o", "--output")
    a.add_argument("-t", "--records-type", default="Imported")

    # diff
    a = sub.add_parser("diff", help="Compare two BEJSON files")
    a.add_argument("file1")
    a.add_argument("file2")

    # pretty
    a = sub.add_parser("pretty", help="Pretty-print BEJSON")
    a.add_argument("file")

    # parse
    a = sub.add_parser("parse", help="Extract files from structured BEJSON")
    a.add_argument("file")
    a.add_argument("-o", "--output")
    a.add_argument("--overwrite", action="store_true")

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        return 1

    cmds = {
        "validate": cmd_validate, "create": cmd_create, "info": cmd_info,
        "query": cmd_query, "add": cmd_add, "delete": cmd_delete,
        "sort": cmd_sort, "export": cmd_export, "import": cmd_import,
        "diff": cmd_diff, "pretty": cmd_pretty, "parse": cmd_parse,
    }
    return cmds[args.cmd](args)

if __name__ == "__main__":
    sys.exit(main())
