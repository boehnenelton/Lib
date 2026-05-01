"""
Library:     test_ai_generation.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: {data['meta_description']}")
        print(f"HTML Length: {len(data['html'])} bytes")
Build to see results
        cms.build_and_publish(stylesheet="dark.css")
    else:
        print("\n[FAILED] AI Generation failed.")

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
from BEJSON_CMS_Gen_Lib import ContentGenerator

MASTER_DB = os.path.join(BASE_DIR, "Data", "BEJSON_WEB_BUILDER", "site_master.json")

def test():
    print("--- AI Content Generation Test ---")
    cms = CMSDatabase(MASTER_DB)
    gen = ContentGenerator()
    
    # 1. Generate and Save a full page
    topic = "The Future of BEJSON and Tabular Data Integrity"
    pid = gen.generate_and_save_page(cms, topic, category="Documentation", persona="Lead Data Scientist")
    
    if pid:
        print("\n[SUCCESS] AI Page Created!")
        data = cms.get_page_content(pid)
        print(f"Title: {data['meta_title']}")
        print(f"Description: {data['meta_description']}")
        print(f"HTML Length: {len(data['html'])} bytes")
        
        # Build to see results
        cms.build_and_publish(stylesheet="dark.css")
    else:
        print("\n[FAILED] AI Generation failed.")

if __name__ == "__main__":
    test()
