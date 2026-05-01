"""
Library:     bejson_schema_builder.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Interactive BEJSON schema builder. Creates BEJSON files
             from guided prompts or specification files.
"""
"""

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
    bejson_core_atomic_write,
)

class C:
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"

def prompt(text, default_val="", choices=None):
    if choices:
        opts = "/".join(choices)
        while True:
            ans = input(f"{C.CYAN}{text} [{opts}]{C.RESET} [{default_val}]: ").strip()
            if not ans:
                ans = default_val
            if ans in choices:
                return ans
            print(f"{C.YELLOW}Choose one of: {opts}{C.RESET}")
    else:
        ans = input(f"{C.CYAN}{text}{C.RESET} [{default_val}]: ").strip()
        return ans if ans else default_val


def interactive_field_builder(version, entity_name=""):
    """Interactively build field definitions."""
    fields = []
    print(f"\n{C.BOLD}{C.BLUE}--- Field Builder ---{C.RESET}")
    print(f"{C.YELLOW}Enter fields one at a time. Leave name blank to finish.{C.RESET}\n")

    if version == "104db" and entity_name:
        # First field must be Record_Type_Parent
        fields.append({"name": "Record_Type_Parent", "type": "string"})
        print(f"  + Record_Type_Parent (string) — auto-added for 104db\n")

    while True:
        name = input(f"{C.CYAN}  Field name{C.RESET}: ").strip()
        if not name:
            break
        ftype = prompt("  Type", default_val="string",
                       choices=["string","integer","number","boolean","array","object"])
        # Version 104a: only primitives
        if version == "104a" and ftype in ("array", "object"):
            print(f"{C.YELLOW}  ⚠ 104a only allows primitive types. Using 'string' instead.{C.RESET}")
            ftype = "string"

        field = {"name": name, "type": ftype}
        if version == "104db" and entity_name and name != "Record_Type_Parent":
            field["Record_Type_Parent"] = entity_name
        fields.append(field)
        print(f"  {C.GREEN}+ Added: {name} ({ftype}){C.RESET}\n")

    return fields


def interactive_104db_builder():
    """Multi-entity 104db builder."""
    print(f"\n{C.BOLD}{C.BLUE}--- 104db Multi-Entity Schema Builder ---{C.RESET}")
    raw = input(f"{C.CYAN}Entity names (comma-separated){C.RESET}: ").strip()
    entities = [e.strip() for e in raw.split(",") if e.strip()]
    if len(entities) < 2:
        print(f"{C.YELLOW}⚠ 104db requires at least 2 entities. Adding 'Record' as second entity.{C.RESET}")
        entities = entities + ["Record"] if entities else ["Record", "Record"]

    all_fields = []
    for ent in entities:
        fields = interactive_field_builder("104db", entity_name=ent)
        all_fields.extend(fields)

    # Remove duplicate field definitions (keep unique by name)
    seen = set()
    unique_fields = []
    for f in all_fields:
        if f["name"] not in seen:
            seen.add(f["name"])
            unique_fields.append(f)

    # Ensure Record_Type_Parent is first
    unique_fields.sort(key=lambda f: (0 if f["name"] == "Record_Type_Parent" else 1))

    return entities, unique_fields


def main():
    print(f"{C.BOLD}{C.BLUE}")
    print("╔══════════════════════════════════════════════╗")
    print("║       BEJSON Schema Builder v1.0.0           ║")
    print("╚══════════════════════════════════════════════╝")
    print(f"{C.RESET}")

    version = prompt("BEJSON Version", default_val="104db",
                     choices=["104", "104a", "104db"])

    # Record type
    if version == "104db":
        entities, fields = interactive_104db_builder()
        record_type = entities  # list for 104db
    else:
        record_type = prompt("Record type name", default_val="Record")
        fields = interactive_field_builder(version)

    if not fields or (version == "104db" and len(fields) < 2):
        print(f"\n{C.YELLOW}⚠ No fields defined — creating with minimal schema{C.RESET}")
        if version == "104db":
            fields = [
                {"name": "Record_Type_Parent", "type": "string"},
                {"name": "data", "type": "string", "Record_Type_Parent": entities[0]},
            ]
        else:
            fields = [{"name": "data", "type": "string"}]

    # Custom headers for 104a
    custom = {}
    if version == "104a":
        print(f"\n{C.YELLOW}Optional custom headers (PascalCase, file-level metadata only){C.RESET}")
        while True:
            hname = input(f"{C.CYAN}  Header name (blank to finish){C.RESET}: ").strip()
            if not hname:
                break
            hval = input(f"{C.CYAN}  Header value{C.RESET}: ").strip()
            if hname and hval:
                custom[hname] = hval

    # Output
    output = input(f"{C.CYAN}Output file{C.RESET} [output.bejson.json]: ").strip()
    if not output:
        output = "output.bejson.json"

    # Create document
    if version == "104":
        doc = bejson_core_create_104(record_type, fields, [])
    elif version == "104a":
        doc = bejson_core_create_104a(record_type, fields, [], **custom)
    elif version == "104db":
        doc = bejson_core_create_104db(entities, fields, [])

    bejson_core_atomic_write(output, doc)
    print(f"\n{C.GREEN}✓ Schema created: {output}{C.RESET}")
    print(f"  {len(fields)} fields, 0 records")
    if version == "104db":
        print(f"  Entities: {', '.join(entities)}")
    print(f"\n{C.YELLOW}Add records with: python3 bejson_cli.py add {output} '[\"val1\", \"val2\", ...]'{C.RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
