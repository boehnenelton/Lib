"""
Library:     rebuild.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Safety-first rebuild script for BEJSON CMS. Creates backups before building.
"""

import os
import sys
import threading
import zipfile
from datetime import datetime
Add script dir to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(LIB_DIR)

if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import Flask_CMS_Publisher as Publisher

def create_zip_backup(source_dirs, zip_name):
    try:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for s_dir in source_dirs:
                if os.path.exists(s_dir):
                    for root, dirs, files in os.walk(s_dir):
                        for file in files:
                            zipf.write(os.path.join(root, file),
                                       os.path.relpath(os.path.join(root, file), os.path.join(s_dir, '..')))
        return True
    except Exception as e:
        print(f"[Backup] Failed: {e}")
        return False

def trigger_rebuild():
    print("[Rebuilder] Starting safety-first build...")
    
    data_dir = os.path.join(SCRIPT_DIR, "Data")
    proc_dir = os.path.join(SCRIPT_DIR, "Processing")
    backup_dir = os.path.join(SCRIPT_DIR, "Backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pre_zip = os.path.join(backup_dir, f"PreBuild_Backup_{timestamp}.zip")
    
    print(f"[Backup] Creating pre-build archive: {os.path.basename(pre_zip)}")
    create_zip_backup([data_dir, proc_dir], pre_zip)
Setup state
    Publisher._state["build_running"] = True
    Publisher._state["build_log"] = []
Run the execution logic
    Publisher._execute()
    
    print("[Rebuilder] Build complete.")
    for msg in Publisher._state["build_log"]:
        print(f"  > {msg}")
Create Last Known Good
    lkg_zip = os.path.join(backup_dir, "Last_Known_Good_Build.zip")
    print(f"[Backup] Updating Last Known Good: {os.path.basename(lkg_zip)}")
    create_zip_backup([data_dir, proc_dir], lkg_zip)

if __name__ == "__main__":
    trigger_rebuild()
"""
import os
import sys
import threading
import zipfile
from datetime import datetime

# Add script dir to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(LIB_DIR)

if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import Flask_CMS_Publisher as Publisher

def create_zip_backup(source_dirs, zip_name):
    try:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for s_dir in source_dirs:
                if os.path.exists(s_dir):
                    for root, dirs, files in os.walk(s_dir):
                        for file in files:
                            zipf.write(os.path.join(root, file),
                                       os.path.relpath(os.path.join(root, file), os.path.join(s_dir, '..')))
        return True
    except Exception as e:
        print(f"[Backup] Failed: {e}")
        return False

def trigger_rebuild():
    print("[Rebuilder] Starting safety-first build...")
    
    data_dir = os.path.join(SCRIPT_DIR, "Data")
    proc_dir = os.path.join(SCRIPT_DIR, "Processing")
    backup_dir = os.path.join(SCRIPT_DIR, "Backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pre_zip = os.path.join(backup_dir, f"PreBuild_Backup_{timestamp}.zip")
    
    print(f"[Backup] Creating pre-build archive: {os.path.basename(pre_zip)}")
    create_zip_backup([data_dir, proc_dir], pre_zip)
    
    # Setup state
    Publisher._state["build_running"] = True
    Publisher._state["build_log"] = []
    
    # Run the execution logic
    Publisher._execute()
    
    print("[Rebuilder] Build complete.")
    for msg in Publisher._state["build_log"]:
        print(f"  > {msg}")
        
    # Create Last Known Good
    lkg_zip = os.path.join(backup_dir, "Last_Known_Good_Build.zip")
    print(f"[Backup] Updating Last Known Good: {os.path.basename(lkg_zip)}")
    create_zip_backup([data_dir, proc_dir], lkg_zip)

if __name__ == "__main__":
    trigger_rebuild()
