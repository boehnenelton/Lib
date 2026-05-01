"""
Library:     create_test_content.py
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

def main():
    print(f"--- CMS Test Content Creator ---")
    cms = CMSDatabase(MASTER_DB)
    
    # 1. Sync Schema first
    print("Syncing schema...")
    cms.sync_schema()
    
    # 2. Create Categories
    categories = ["Documentation", "Tutorials", "News", "Resources"]
    for cat in categories:
        if cms.create_category(cat):
            print(f"Created category: {cat}")
        else:
            print(f"Category already exists: {cat}")
            
    # 3. Create Test Pages
    test_pages = [
        {"title": "Getting Started with CMS v11", "cat": "Documentation", "author": "Gemini"},
        {"title": "How to use BEJSON 104db", "cat": "Tutorials", "author": "Elton"},
        {"title": "Project Update: March 2026", "cat": "News", "author": "Admin"},
        {"title": "Useful Development Tools", "cat": "Resources", "author": "Gemini"}
    ]
    
    for page in test_pages:
        uuid = cms.create_page(
            title=page["title"],
            category=page["cat"],
            author=page["author"]
        )
        if uuid:
            print(f"Created page: {page['title']} (UUID: {uuid})")
            
            # Add some custom content to one of them
            if page["cat"] == "Documentation":
                cms.save_page_content(
                    uuid, 
                    html=f"<h1>{page['title']}</h1><p>Welcome to the new CMS documentation.</p>",
                    markdown=f"""# {page['title']}
Welcome to the new CMS documentation."""
                )
                print(f"  -> Added custom content to {page['title']}")
        else:
            print(f"Failed to create page: {page['title']}")

    # 4. List everything to verify
    print("\n--- Final Verification ---")
    cats = cms.list_categories()
    pages = cms.list_pages()
    
    print(f"Total Categories: {len(cats)}")
    print(f"Total Pages: {len(pages)}")
    
    for p in pages[:5]: # Show last 5
        print(f" - [{p.get('category_ref')}] {p.get('page_title')} by {p.get('author_ref')}")

if __name__ == "__main__":
    main()
