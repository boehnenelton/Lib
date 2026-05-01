"""
Library:     reset_cms.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Factory reset utility for BEJSON CMS. Clears data and re-initializes schema.
"""

import sys
import os
Add Lib to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(LIB_DIR)

if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from BEJSON_CMS_Lib import CMSDatabase

MASTER_DB = os.path.join(PROJECT_ROOT, "Data", "BEJSON_WEB_BUILDER", "site_master.json")

def main():
    print("Initializing CMS Database for Factory Reset...")
    cms = CMSDatabase(MASTER_DB)
    print("Performing Factory Reset...")
    if cms.factory_reset(confirm=True):
        print("SUCCESS: CMS Database has been factory reset.")
    else:
        print("FAILURE: CMS Database reset failed.")

if __name__ == "__main__":
    main()
"""
import sys
import os

# Add Lib to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(LIB_DIR)

if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from BEJSON_CMS_Lib import CMSDatabase

MASTER_DB = os.path.join(PROJECT_ROOT, "Data", "BEJSON_WEB_BUILDER", "site_master.json")

def main():
    print("Initializing CMS Database for Factory Reset...")
    cms = CMSDatabase(MASTER_DB)
    print("Performing Factory Reset...")
    if cms.factory_reset(confirm=True):
        print("SUCCESS: CMS Database has been factory reset.")
    else:
        print("FAILURE: CMS Database reset failed.")

if __name__ == "__main__":
    main()
