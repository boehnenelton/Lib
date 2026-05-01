"""
Library:     bejson_stats.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Dashboard for BEJSON file analysis — scan directories,
             generate statistics, find duplicates, track schema changes.
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
    bejson_core_get_version,
    bejson_core_get_stats,
    bejson_core_get_field_values,
    bejson_core_pretty_print,
    BEJSONCoreError,
)
from lib_bejson_validator import (
    bejson_validator_validate_file,
    BEJSONValidationError,
)

class C:
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    RESET  = "\033[0m"


def file_hash(path):
    return hashlib.md5(Path(path).read_bytes()).hexdigest()


def cmd_scan(args):
    """Scan a directory for BEJSON files and show statistics."""
    dirpath = Path(args.directory)
    if not dirpath.is_dir():
        print(f"{C.RED}✗ Not a directory: {args.directory}{C.RESET}")
        return 1

    # Find all .json and .bejson files
    candidates = list(dirpath.rglob("*.json"))
    if not candidates:
        print(f"{C.YELLOW}⚠ No .json files found in {args.directory}{C.RESET}")
        return 0

    # Validate and collect stats
    valid_files = []
    invalid_files = []
    total_size = 0
    version_counts = {}
    entity_counts = {}
    field_names = {}
    total_records = 0

    for fp in candidates:
        fp_str = str(fp)
        try:
            bejson_validator_validate_file(fp_str)
        except (BEJSONValidationError, Exception):
            invalid_files.append(fp_str)
            continue

        try:
            doc = bejson_core_load_file(fp_str)
        except Exception:
            invalid_files.append(fp_str)
            continue

        valid_files.append(fp)
        size = fp.stat().st_size
        total_size += size
        stats = bejson_core_get_stats(doc)
        version = stats["version"]
        version_counts[version] = version_counts.get(version, 0) + 1
        total_records += stats["record_count"]

        for et in stats["records_types"]:
            entity_counts[et] = entity_counts.get(et, 0) + 1

        for f in doc["Fields"]:
            name = f["name"]
            field_names[name] = field_names.get(name, 0) + 1

    # Display
    print(f"\n{C.BOLD}{C.BLUE}{'='*60}{C.RESET}")
    print(f"{C.BOLD}  BEJSON Directory Scan: {dirpath}{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}{'='*60}{C.RESET}\n")

    print(f"  {C.BOLD}Files scanned:{C.RESET} {len(candidates)}")
    print(f"  {C.GREEN}Valid BEJSON:{C.RESET} {len(valid_files)}")
    print(f"  {C.YELLOW}Invalid/Non-BEJSON:{C.RESET} {len(invalid_files)}")
    print(f"  {C.BOLD}Total size:{C.RESET} {total_size:,} bytes ({total_size/1024:.1f} KB)")
    print(f"  {C.BOLD}Total records:{C.RESET} {total_records:,}")

    if version_counts:
        print(f"\n  {C.BOLD}Version Distribution:{C.RESET}")
        for v, c in sorted(version_counts.items()):
            print(f"    {C.GREEN}{v}{C.RESET}: {c} file(s)")

    if entity_counts:
        print(f"\n  {C.BOLD}Entity Types (across all files):{C.RESET}")
        for et, c in sorted(entity_counts.items(), key=lambda x: -x[1]):
            print(f"    {C.GREEN}{et}{C.RESET}: {c} occurrence(s)")

    if field_names and args.top:
        print(f"\n  {C.BOLD}Top {args.top} Field Names:{C.RESET}")
        for name, count in sorted(field_names.items(), key=lambda x: -x[1])[:args.top]:
            pct = f"{count/len(valid_files)*100:.0f}%"
            bar_len = int(count / len(valid_files) * 30)
            bar = "█" * bar_len + "░" * (30 - bar_len)
            print(f"    {C.GREEN}{name:<35s}{C.RESET} {bar} {pct}")

    if invalid_files and args.show_invalid:
        print(f"\n  {C.BOLD}Invalid Files:{C.RESET}")
        for fp in invalid_files:
            print(f"    {C.RED}✗ {fp}{C.RESET}")

    print()
    return 0


def cmd_duplicates(args):
    """Find duplicate BEJSON files in a directory."""
    dirpath = Path(args.directory)
    if not dirpath.is_dir():
        print(f"{C.RED}✗ Not a directory: {args.directory}{C.RESET}")
        return 1

    hashes = {}
    for fp in dirpath.rglob("*.json"):
        try:
            bejson_validator_validate_file(str(fp))
        except Exception:
            continue
        h = file_hash(fp)
        if h not in hashes:
            hashes[h] = []
        hashes[h].append(str(fp))

    dupes = {h: files for h, files in hashes.items() if len(files) > 1}

    if not dupes:
        print(f"\n{C.GREEN}✓ No duplicate BEJSON files found{C.RESET}\n")
        return 0

    print(f"\n{C.BOLD}{C.BLUE}{'='*60}{C.RESET}")
    print(f"{C.BOLD}  Duplicate BEJSON Files ({len(dupes)} groups){C.RESET}")
    print(f"{C.BOLD}{C.BLUE}{'='*60}{C.RESET}\n")

    for h, files in sorted(dupes.items(), key=lambda x: -len(x[1])):
        print(f"  {C.YELLOW}Group ({len(files)} copies, hash: {h[:8]}...){C.RESET}")
        for fp in files:
            size = Path(fp).stat().st_size
            print(f"    {C.CYAN}{fp}{C.RESET} ({size:,} bytes)")
        print()

    # Calculate wasted space
    wasted = sum((len(files) - 1) * Path(files[0]).stat().st_size for files in dupes.values())
    print(f"  {C.BOLD}Wasted space: {wasted:,} bytes ({wasted/1024:.1f} KB){C.RESET}\n")
    return 0


def cmd_compare(args):
    """Compare two BEJSON files side by side."""
    try:
        d1 = bejson_core_load_file(args.file1)
        d2 = bejson_core_load_file(args.file2)
    except BEJSONCoreError as e:
        print(f"{C.RED}✗ {e}{C.RESET}")
        return 1

    s1 = bejson_core_get_stats(d1)
    s2 = bejson_core_get_stats(d2)

    print(f"\n{C.BOLD}{C.BLUE}{'='*60}{C.RESET}")
    print(f"{C.BOLD}  BEJSON Comparison{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}{'='*60}{C.RESET}\n")

    # Header
    name1 = Path(args.file1).name
    name2 = Path(args.file2).name
    print(f"  {'':20s} {C.GREEN}{name1:<25s}{C.RESET} {C.CYAN}{name2:<25s}{C.RESET}")
    print(f"  {'─'*20} {'─'*25} {'─'*25}")

    comparisons = [
        ("Version", s1["version"], s2["version"]),
        ("Record Types", ", ".join(s1["records_types"]), ", ".join(s2["records_types"])),
        ("Fields", str(s1["field_count"]), str(s2["field_count"])),
        ("Records", str(s1["record_count"]), str(s2["record_count"])),
    ]

    for label, v1, v2 in comparisons:
        match = "✓" if v1 == v2 else f"{C.RED}✗{C.RESET}"
        print(f"  {label:<20s} {v1:<25s} {v2:<25s} {match}")

    # Field comparison
    fields1 = {f["name"]: f["type"] for f in d1["Fields"]}
    fields2 = {f["name"]: f["type"] for f in d2["Fields"]}

    only1 = sorted(set(fields1) - set(fields2))
    only2 = sorted(set(fields2) - set(fields1))
    type_changes = sorted(n for n in set(fields1) & set(fields2) if fields1[n] != fields2[n])

    if only1:
        print(f"\n  {C.RED}Only in {name1}:{C.RESET} {', '.join(only1)}")
    if only2:
        print(f"\n  {C.RED}Only in {name2}:{C.RESET} {', '.join(only2)}")
    if type_changes:
        print(f"\n  {C.YELLOW}Type differences:{C.RESET}")
        for n in type_changes:
            print(f"    {n}: {fields1[n]} → {fields2[n]}")

    # Size comparison
    size1 = Path(args.file1).stat().st_size
    size2 = Path(args.file2).stat().st_size
    diff = size2 - size1
    sign = "+" if diff >= 0 else ""
    print(f"\n  {C.BOLD}Size:{C.RESET} {size1:,} → {size2:,} bytes ({sign}{diff:,})")
    print()
    return 0


def cmd_summary(args):
    """Print summary of multiple BEJSON files."""
    print(f"\n{C.BOLD}{C.BLUE}{'='*70}{C.RESET}")
    print(f"{C.BOLD}  BEJSON File Summary{C.RESET}")
    print(f"{C.BOLD}{C.BLUE}{'='*70}{C.RESET}\n")

    # Header
    print(f"  {C.BOLD}{'File':<35s} {'Ver':<8s} {'Types':<20s} {'Fields':>7s} {'Records':>8s} {'Size':>10s}{C.RESET}")
    print(f"  {'─'*35} {'─'*8} {'─'*20} {'─'*7} {'─'*8} {'─'*10}")

    total_records = 0
    total_size = 0

    for fp in args.files:
        try:
            doc = bejson_core_load_file(fp)
        except Exception as e:
            print(f"  {C.RED}✗ {fp}: {e}{C.RESET}")
            continue

        s = bejson_core_get_stats(doc)
        size = Path(fp).stat().st_size
        total_records += s["record_count"]
        total_size += size

        types = ", ".join(s["records_types"])
        if len(types) > 20:
            types = types[:17] + "..."

        print(f"  {C.GREEN}{Path(fp).name:<35s}{C.RESET} {s['version']:<8s} {types:<20s} {s['field_count']:>7d} {s['record_count']:>8d} {size:>10,}")

    print(f"\n  {C.BOLD}Total: {len(args.files)} files, {total_records:,} records, {total_size:,} bytes ({total_size/1024:.1f} KB){C.RESET}\n")
    return 0


def main():
    ap = argparse.ArgumentParser(description="BEJSON Stats Dashboard")
    sub = ap.add_subparsers(dest="cmd")

    # scan
    a = sub.add_parser("scan", help="Scan directory for BEJSON files")
    a.add_argument("directory", help="Directory to scan")
    a.add_argument("--top", type=int, default=15, help="Show top N field names")
    a.add_argument("--show-invalid", action="store_true")

    # duplicates
    a = sub.add_parser("duplicates", help="Find duplicate BEJSON files")
    a.add_argument("directory", help="Directory to scan")

    # compare
    a = sub.add_parser("compare", help="Compare two BEJSON files")
    a.add_argument("file1")
    a.add_argument("file2")

    # summary
    a = sub.add_parser("summary", help="Summary of multiple BEJSON files")
    a.add_argument("files", nargs="+")

    args = ap.parse_args()
    if not args.cmd:
        ap.print_help()
        return 1

    cmds = {
        "scan": cmd_scan,
        "duplicates": cmd_duplicates,
        "compare": cmd_compare,
        "summary": cmd_summary,
    }
    return cmds[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
