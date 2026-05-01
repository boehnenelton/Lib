"""
Library:     test_build_and_server.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Core-Command library component.
"""
import os
import sys
import timeSCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.dirname(SCRIPT_DIR)
BASE_DIR = os.path.dirname(LIB_DIR)

if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)

from BEJSON_CMS_Lib import CMSDatabase

MASTER_DB = os.path.join(BASE_DIR, "Data", "BEJSON_WEB_BUILDER", "site_master.json")

def test():
    print(f"--- CMS Server & Build Test ---")
    cms = CMSDatabase(MASTER_DB)
    
    # 1. Test Server Start
    print("\n[1] Starting CMS Server...")
    if cms.start_server("cms"):
        print("Waiting 3 seconds for server to spin up...")
        time.sleep(3)
        
        # 2. Test Build (while server is running)
        print("\n[2] Triggering Static Build...")
        if cms.build_and_publish():
            print("Build SUCCESS")
            
            # Check if output exists
            www_dir = os.path.join(BASE_DIR, "Processing", "BEJSON_WEB_BUILDER", "www")
            if os.path.exists(os.path.join(www_dir, "index.html")):
                print(f"Verified: index.html found in {www_dir}")
            else:
                print("Warning: index.html NOT found.")
        else:
            print("Build FAILED")
            
        # 3. Test Server Stop
        print("\n[3] Stopping CMS Server...")
        cms.stop_server("cms")
    else:
        print("Failed to start CMS server")

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    test()
