"""
Library:     test_scaffolding.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Core-Command library component.
"""
import os
import sysSCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.dirname(SCRIPT_DIR)
BASE_DIR = os.path.dirname(LIB_DIR)

if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)

from BEJSON_CMS_Lib import CMSDatabase

MASTER_DB = os.path.join(BASE_DIR, "Data", "BEJSON_WEB_BUILDER", "site_master.json")

def test():
    print("--- Page Scaffolding Test ---")
    cms = CMSDatabase(MASTER_DB)
    
    # 1. Test Video Gallery Scaffolding
    print("\n[1] Scaffolding Video Gallery...")
    videos = [
        {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "label": "Never Gonna Give You Up"},
        {"url": "https://youtu.be/9bZkp7q19f0", "label": "PSY - GANGNAM STYLE"}
    ]
    vid_id = cms.scaffold_video_gallery("My Music Collection", videos, intro="A collection of classic hits.", category="Tutorials")
    if vid_id:
        print(f"Success: Video Gallery created (UUID: {vid_id})")
        
    # 2. Test GitHub Project Scaffolding
    print("\n[2] Scaffolding GitHub Project...")
    features = [
        "Positionally strictly tabular data",
        "Fast index-based access",
        "Embedded schema validation"
    ]
    proj_id = cms.scaffold_github_project(
        "BEJSON Core Library", 
        "https://github.com/boehnenelton/bejson-core", 
        features, 
        desc="A powerful library for handling BEJSON files.",
        category="Documentation"
    )
    if proj_id:
        print(f"Success: Project Page created (UUID: {proj_id})")

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    test()
