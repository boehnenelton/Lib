"""
Library:     test_final_features.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: {data['meta_description']}")
        print(f"Verified Author: {data['meta_author']}")
2. Test Latest/Related Queries
    print("\n[2] Testing Query Helpers...")
    latest = cms.get_latest_pages(limit=2)
    print(f"Latest 2 Pages: {[p.get('page_title') for p in latest]}")
    
    related = cms.get_related_pages(pid)
    print(f"Related Pages (same category): {[p.get('page_title') for p in related]}")
3. Test Exports
    print("\n[3] Testing ZIP Exports...")
    print(f"CMS Dir: {cms.cms_dir}")
    www_path = os.path.join(cms.cms_dir, "Processing", "BEJSON_WEB_BUILDER", "www")
    print(f"Checking WWW path: {www_path} (Exists: {os.path.exists(www_path)})")
    
    cms.build_and_publish()
    
    site_zip = cms.export_site_zip()
    if site_zip and os.path.exists(site_zip):
        print(f"Site Export SUCCESS: {os.path.basename(site_zip)}")
    else:
        print("Site Export Failed (or no build exists)")
        
    data_zip = cms.export_data_zip()
    if data_zip and os.path.exists(data_zip):
        print(f"Data Backup SUCCESS: {os.path.basename(data_zip)}")
    else:
        print("Data Backup Failed")

    print("\n--- Final Verification Complete ---")

if __name__ == "__main__":
    test()
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
    print("--- Final Features Verification ---")
    cms = CMSDatabase(MASTER_DB)
    
    # 1. Test Metadata and Advanced Save
    print("\n[1] Testing Advanced Page Metadata...")
    pid = cms.create_page("Final Library Test", author="Senior Engineer")
    if pid:
        cms.save_page_content(
            pid, 
            meta_description="A high-level CMS management library for BEJSON.",
            markdown="# Final Test\nVerified all components."
        )
        data = cms.get_page_content(pid)
        print(f"Verified Description: {data['meta_description']}")
        print(f"Verified Author: {data['meta_author']}")
    
    # 2. Test Latest/Related Queries
    print("\n[2] Testing Query Helpers...")
    latest = cms.get_latest_pages(limit=2)
    print(f"Latest 2 Pages: {[p.get('page_title') for p in latest]}")
    
    related = cms.get_related_pages(pid)
    print(f"Related Pages (same category): {[p.get('page_title') for p in related]}")
    
    # 3. Test Exports
    print("\n[3] Testing ZIP Exports...")
    print(f"CMS Dir: {cms.cms_dir}")
    www_path = os.path.join(cms.cms_dir, "Processing", "BEJSON_WEB_BUILDER", "www")
    print(f"Checking WWW path: {www_path} (Exists: {os.path.exists(www_path)})")
    
    cms.build_and_publish()
    
    site_zip = cms.export_site_zip()
    if site_zip and os.path.exists(site_zip):
        print(f"Site Export SUCCESS: {os.path.basename(site_zip)}")
    else:
        print("Site Export Failed (or no build exists)")
        
    data_zip = cms.export_data_zip()
    if data_zip and os.path.exists(data_zip):
        print(f"Data Backup SUCCESS: {os.path.basename(data_zip)}")
    else:
        print("Data Backup Failed")

    print("\n--- Final Verification Complete ---")

if __name__ == "__main__":
    test()
