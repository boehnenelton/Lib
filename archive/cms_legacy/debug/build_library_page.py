"""
Library:     build_library_page.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Core-Command library component.
"""
import sys
import osPROJECT_ROOT = "/storage/emulated/0/updateme/BEJSON-CMS-v153"
LIB_DIR = os.path.join(PROJECT_ROOT, "Lib")
MASTER_DB = os.path.join(PROJECT_ROOT, "Data", "BEJSON_WEB_BUILDER", "site_master.json")

sys.path.append(LIB_DIR)

from BEJSON_CMS_Lib import CMSDatabase

def build_library_page():
    cms = CMSDatabase(MASTER_DB)
    
    # Define the files to showcase
    source_paths = {
        "lib_bejson_core.sh": "/storage/7B30-0E0B/Core-Command/Lib/sh/lib_bejson_core.sh",
        "lib_bejson_core.py": "/storage/7B30-0E0B/Core-Command/Lib/py/lib_bejson_core.py",
        "lib_bejson_core.js": "/storage/7B30-0E0B/Core-Command/Lib/js/lib_bejson_core.js"
    }
    
    files_content = {}
    for name, path in source_paths.items():
        if os.path.exists(path):
            with open(path, 'r') as f:
                files_content[name] = f.read()
        else:
            print(f"Warning: {path} not found.")

    if not files_content:
        print("Error: No source files found to showcase.")
        return

    # Description and Version Details
    description_html = """

    # Generate the multi-file viewer HTML
    # We use the internal generate_multi_file_code_block from CMSDatabase
    viewer_html = cms.generate_multi_file_code_block(files_content)
    
    full_html = description_html + viewer_html

    # Create the page
    title = "BEJSON Universal Libraries"
    category = "BEJSON Libraries"
    author = "boehnenelton2024"
    
    print(f"Creating page: {title}...")
    page_uuid = cms.create_page(title, category=category, author=author)
    
    if page_uuid:
        print(f"Page created with UUID: {page_uuid}")
        if cms.save_page_content(page_uuid, html=full_html):
            print("Successfully saved page content.")
            
            # Trigger build
            print("Triggering site build...")
            if cms.build_and_publish():
                print("Site build successful.")
            else:
                print("Site build failed.")
        else:
            print("Failed to save page content.")
    else:
        print("Failed to create page record.")

if __name__ == "__main__":
    build_library_page()
