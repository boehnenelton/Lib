"""
Library:     test_cms_lib.py
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
    print(f"Testing with Master DB: {MASTER_DB}")
    cms = CMSDatabase(MASTER_DB)
    
    # 1. List categories
    cats = cms.list_categories()
    print(f"Categories: {[c.get('category_name') for c in cats]}")
    
    # 2. Create category
    new_cat = "Test Category"
    if cms.create_category(new_cat):
        print(f"Created category: {new_cat}")
    else:
        print(f"Failed to create or already exists: {new_cat}")
        
    # 3. Create page
    page_uuid = cms.create_page("Test Page", category=new_cat)
    if page_uuid:
        print(f"Created page with UUID: {page_uuid}")
    else:
        print("Failed to create page")
        
    # 4. Update page (Testing the 'CMS6' style update)
    if page_uuid:
        if cms.update_database("PageRecord", "page_uuid", page_uuid, {"page_title": "Updated Test Page"}):
            print("Successfully updated page title")
        else:
            print("Failed to update page title")
            
    # 5. Cleanup (optional, but good for testing)
    # if page_uuid:
    #     cms.delete_page(page_uuid)
    #     print("Deleted test page")
    # cms.delete_category(new_cat)
    # print("Deleted test category")

if __name__ == "__main__":
    test()
