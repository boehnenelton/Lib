"""
Library:     apply_redesign.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Core-Command library component.
"""
import os
import sys
from BEJSON_CMS_Lib import CMSDatabase
...
# Paths
CMS_DIR = "/storage/7B30-0E0B/CoreGem/PPM/scripts/BEJSON-CMS-v11"
MASTER_DB = os.path.join(CMS_DIR, "Data", "BEJSON_WEB_BUILDER", "site_master.json")
LIB_DIR = "/storage/7B30-0E0B/CoreGem/PPM/data/lib"
CMS_LIB_PATH = os.path.join(CMS_DIR, "Lib", "BEJSON_CMS_Lib.py")

def main():
    print("--- Redesigning Site: boehnenelton2024 ---")
    cms = CMSDatabase(MASTER_DB)
    
    # 1. Update Site Config
    cms._load()
    cms.set_config("title", "boehnenelton2024")
    cms.set_config("creator", "boehnenelton2024")
    cms.set_config("description", "Professional Documentation & Library Source for CoreGem")
    cms._unload()
    
    # 2. Clear and Re-document
    print("Re-generating documentation...")
    # We won't factory reset to keep categories, just overwrite records
    
    # CMS Lib
    with open(CMS_LIB_PATH, 'r') as f: cms_code = f.read()
    cms.scaffold_code_project(
        "BEJSON CMS Library",
        {"BEJSON_CMS_Lib.py": cms_code},
        description="Core management library for boehnenelton2024 ecosystem.",
        category="Library Source"
    )
    
    # PPM Libs
    libs = [f for f in os.listdir(LIB_DIR) if f.endswith(('.py', '.js', '.sh'))]
    for lib_name in libs:
        path = os.path.join(LIB_DIR, lib_name)
        try:
            with open(path, 'r') as f: code = f.read()
            cms.scaffold_code_project(
                f"Library: {lib_name}",
                {lib_name: code},
                description=f"Source code for {lib_name} component.",
                category="Library Source"
            )
        except: pass

    # 3. Build with Dark Theme
    print("\nTriggering Dark Professional Build...")
    if cms.build_and_publish(stylesheet="dark.css"):
        print("--- boehnenelton2024 Dark Redesign SUCCESS ---")
        print(f"URL: file://{os.path.join(CMS_DIR, 'Processing', 'BEJSON_WEB_BUILDER', 'www', 'index.html')}")
    else:
        print("Build Failed.")

if __name__ == "__main__":
    main()
