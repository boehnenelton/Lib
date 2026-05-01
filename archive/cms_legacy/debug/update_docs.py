"""
Library:     update_docs.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Automated documentation updater. Syncs source code into CMS pages.
"""

import os
import json
import sys
from datetime import datetime
Add script dir to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(LIB_DIR)

if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import BEJSON_Standard_Lib as StdLib
import BEJSON_Extended_Lib as ExtLib

DATA_ROOT = os.path.join(PROJECT_ROOT, "Data", "BEJSON_WEB_BUILDER")
MASTER_DB = os.path.join(DATA_ROOT, "site_master.json")
PAGES_DB_DIR = os.path.join(DATA_ROOT, "pages_db")
Paths to source files (mapped to their page titles in CMS)
Hardcoded absolute paths are kept as fallback, but relative project paths are added.
SOURCE_MAP = {
    "Source: BEJSON_Standard_Lib.py": os.path.join(PROJECT_ROOT, "BEJSON_Standard_Lib.py"),
    "Source: BEJSON_Extended_Lib.py": os.path.join(PROJECT_ROOT, "BEJSON_Extended_Lib.py"),
    "Source: BEJSON_CMS_Lib.py": os.path.join(LIB_DIR, "BEJSON_CMS_Lib.py"),
    "Source: BEJSON_CMS_Gen_Lib.py": os.path.join(LIB_DIR, "BEJSON_CMS_Gen_Lib.py"),
}

def update_all_docs():
    print("[DocsUpdater] Loading Master DB...")
    if not StdLib.bejson_load(MASTER_DB):
        print("[DocsUpdater] Failed to load Master DB.")
        return

    pages = ExtLib.bejson_filter_db_records("PageRecord")
    updated_count = 0

    for page in pages:
        title = page.get("page_title")
        uuid = page.get("page_uuid")
        
        if title in SOURCE_MAP:
            src_path = SOURCE_MAP[title]
            if not os.path.exists(src_path):
                print(f"[DocsUpdater] Skip: {src_path} not found.")
                continue
                
            print(f"[DocsUpdater] Updating: {title} ({uuid})")
            new_html = ExtLib.SourceDocGenerator.generate_html_body(src_path)
Load the specific page DB
            page_db_path = os.path.join(PAGES_DB_DIR, f"{uuid}.json")
            if os.path.exists(page_db_path):
                with open(page_db_path, 'r', encoding='utf-8') as f:
                    js = json.load(f)
                
                fields = js.get("Fields", [])
                idx_html = next((i for i, f in enumerate(fields) if f['name'] == "html_body"), -1)
                idx_parent = next((i for i, f in enumerate(fields) if f['name'] == "Record_Type_Parent"), 0)
Update the Content record
                for row in js["Values"]:
                    if row[idx_parent] == "Content":
                        row[idx_html] = new_html
                        break
Save back
                with open(page_db_path, 'w', encoding='utf-8') as f:
                    json.dump(js, f, indent=2)
                
                updated_count += 1
            else:
                print(f"[DocsUpdater] Error: Page DB {uuid}.json missing.")

    print(f"[DocsUpdater] Completed. {updated_count} pages updated.")

if __name__ == "__main__":
    update_all_docs()
"""
import os
import json
import sys
from datetime import datetime

# Add script dir to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(LIB_DIR)

if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import BEJSON_Standard_Lib as StdLib
import BEJSON_Extended_Lib as ExtLib

DATA_ROOT = os.path.join(PROJECT_ROOT, "Data", "BEJSON_WEB_BUILDER")
MASTER_DB = os.path.join(DATA_ROOT, "site_master.json")
PAGES_DB_DIR = os.path.join(DATA_ROOT, "pages_db")

# Paths to source files (mapped to their page titles in CMS)
# Hardcoded absolute paths are kept as fallback, but relative project paths are added.
SOURCE_MAP = {
    "Source: BEJSON_Standard_Lib.py": os.path.join(PROJECT_ROOT, "BEJSON_Standard_Lib.py"),
    "Source: BEJSON_Extended_Lib.py": os.path.join(PROJECT_ROOT, "BEJSON_Extended_Lib.py"),
    "Source: BEJSON_CMS_Lib.py": os.path.join(LIB_DIR, "BEJSON_CMS_Lib.py"),
    "Source: BEJSON_CMS_Gen_Lib.py": os.path.join(LIB_DIR, "BEJSON_CMS_Gen_Lib.py"),
}

def update_all_docs():
    print("[DocsUpdater] Loading Master DB...")
    if not StdLib.bejson_load(MASTER_DB):
        print("[DocsUpdater] Failed to load Master DB.")
        return

    pages = ExtLib.bejson_filter_db_records("PageRecord")
    updated_count = 0

    for page in pages:
        title = page.get("page_title")
        uuid = page.get("page_uuid")
        
        if title in SOURCE_MAP:
            src_path = SOURCE_MAP[title]
            if not os.path.exists(src_path):
                print(f"[DocsUpdater] Skip: {src_path} not found.")
                continue
                
            print(f"[DocsUpdater] Updating: {title} ({uuid})")
            new_html = ExtLib.SourceDocGenerator.generate_html_body(src_path)
            
            # Load the specific page DB
            page_db_path = os.path.join(PAGES_DB_DIR, f"{uuid}.json")
            if os.path.exists(page_db_path):
                with open(page_db_path, 'r', encoding='utf-8') as f:
                    js = json.load(f)
                
                fields = js.get("Fields", [])
                idx_html = next((i for i, f in enumerate(fields) if f['name'] == "html_body"), -1)
                idx_parent = next((i for i, f in enumerate(fields) if f['name'] == "Record_Type_Parent"), 0)
                
                # Update the Content record
                for row in js["Values"]:
                    if row[idx_parent] == "Content":
                        row[idx_html] = new_html
                        break
                
                # Save back
                with open(page_db_path, 'w', encoding='utf-8') as f:
                    json.dump(js, f, indent=2)
                
                updated_count += 1
            else:
                print(f"[DocsUpdater] Error: Page DB {uuid}.json missing.")

    print(f"[DocsUpdater] Completed. {updated_count} pages updated.")

if __name__ == "__main__":
    update_all_docs()
