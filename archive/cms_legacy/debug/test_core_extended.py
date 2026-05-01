"""
Library:     test_core_extended.py
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
    print("--- Extended Core Functionality Test ---")
    cms = CMSDatabase(MASTER_DB)
    
    # 1. Test Assets Listing
    print("\n[1] Assets:")
    assets = cms.list_assets()
    print(f"Files in assets/: {assets}")
    
    # 2. Test Specialized Query
    print("\n[2] Filtering Pages (Documentation):")
    docs = cms.query_entities("PageRecord", {"category_ref": "Documentation"})
    for d in docs:
        print(f" - {d.get('page_title')}")
        
    # 3. Test Ad Toggling
    print("\n[3] Ad Management:")
    ad_id = cms.create_ad("Test Sidebar Ad", "ad.jpg", "https://example.com")
    if ad_id:
        print(f"Created Ad: {ad_id}")
        ads = cms.list_ads()
        status = next((a for a in ads if a['ad_uuid'] == ad_id), {}).get('ad_active')
        print(f"Current Status: {status}")
        
        cms.toggle_ad_status(ad_id)
        ads = cms.list_ads()
        status = next((a for a in ads if a['ad_uuid'] == ad_id), {}).get('ad_active')
        print(f"Status after toggle: {status}")

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    test()
