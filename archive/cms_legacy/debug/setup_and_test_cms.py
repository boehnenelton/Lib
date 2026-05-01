"""
Library:     setup_and_test_cms.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Automated setup and testing script for BEJSON CMS. 
                Initializes schema, categories, assets, and sample pages.
"""

import os
import sys
import shutil
from datetime import datetime
Add Lib to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(LIB_DIR)

if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
"""
import os
import sys
import shutil
from datetime import datetime

# Add Lib to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(LIB_DIR)

if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from BEJSON_CMS_Lib import CMSDatabase
except ImportError:
    print("[TestScript] Error: Could not import BEJSON_CMS_Lib")
    sys.exit(1)

# Paths
CMS_ROOT = PROJECT_ROOT
DATA_ROOT = os.path.join(CMS_ROOT, "Data", "BEJSON_WEB_BUILDER")
MASTER_DB = os.path.join(DATA_ROOT, "site_master.json")
# CORE_GEM_ROOT remains relative if possible, but adjust to point outside project if needed.
# Original was 3 levels up from Lib (which was CMS_ROOT before)
CORE_GEM_ROOT = os.path.dirname(os.path.dirname(PROJECT_ROOT))
IMAGES_DIR = os.path.join(CORE_GEM_ROOT, "images")
DRAWING_APP_HTML = os.path.join(CMS_ROOT, "drawing_app.html")

def main():
    print("=== CMS Setup & Test Script ===")
    cms = CMSDatabase(MASTER_DB)
    
    # 1. Sync Schema
    print("[1] Syncing schema...")
    cms.sync_schema()
    
    # 2. Create Categories
    print("[2] Creating categories...")
    categories = ["Apps", "Documentation", "gemdocs", "Resources"]
    for cat in categories:
        cms.create_category(cat)
    
    # 3. Handle Images
    print("[3] Sourcing images...")
    test_img = "BEJSON_BASH.png"
    src_img = os.path.join(IMAGES_DIR, "BEJSON BASH.png")
    saved_img = None
    if os.path.exists(src_img):
        saved_img = cms.save_asset(src_img, test_img)
        print(f"  -> Saved asset: {saved_img}")
    else:
        print(f"  -> Warning: Source image not found at {src_img}")

    # 4. Create Pages
    print("[4] Creating pages...")
    
    # BEJSON Info Page
    info_pid = cms.create_page(
        title="Understanding BEJSON Positional Integrity",
        category="Documentation",
        author="Gemini CLI",
        featured_img=saved_img or ""
    )
    if info_pid:
        cms.save_page_content(
            info_pid,
            html=f"<h1>Positional Integrity</h1><p>BEJSON relies on the order of fields matching the order of values. This makes it lightning fast!</p><img src='/assets/{saved_img}' style='max-width:100%;'>",
            markdown="""# Positional Integrity
BEJSON relies on the order of fields matching the order of values."""
        )
    
    # gemdocs Change Log
    changelog_pid = cms.create_page(
        title="CMS v12 Change Log",
        category="gemdocs",
        author="Gemini CLI"
    )
    if changelog_pid:
        cms.save_page_content(
            changelog_pid,
            html="""<h2>Version 12.1.0 (2026-03-27)</h2>
            <ul>
                <li>Refactored core to use unified BEJSON Standard & Extended Libraries.</li>
                <li>Added Relation IDs to all core files and maintenance scripts.</li>
                <li>Standardized versioning to 12.1.0 across the entire project.</li>
                <li>Cleaned up and optimized database initialization logic.</li>
            </ul>""",
            markdown="""## Version 12.1.0
- Refactored core to use unified BEJSON Standard & Extended Libraries.
- Added Relation IDs to all core files and maintenance scripts.
- Standardized versioning to 12.1.0 across the entire project.
- Cleaned up and optimized database initialization logic."""
        )

    # 5. Import Standalone App
    print("[5] Importing Standalone App...")
    app_uuid = cms.import_standalone_app(
        name="BEJSON Drawing Pad",
        source_path=DRAWING_APP_HTML,
        description="A silly drawing program that generates Base64 images.",
        entry_file="index.html",
        app_image=saved_img or ""
    )
    if app_uuid:
        print(f"  -> Imported app: {app_uuid}")
    else:
        print("  -> Failed to import app.")

    # 6. Build the site
    print("[6] Building site...")
    # Mocking the publisher execute to ensure output_dir is set correctly
    cms.build_and_publish(stylesheet="dark.css")
    
    # 7. Create literal gemdocs folder (as requested)
    print("[7] Creating literal gemdocs folder...")
    literal_gemdocs = os.path.join(CMS_ROOT, "gemdocs")
    os.makedirs(literal_gemdocs, exist_ok=True)
    with open(os.path.join(literal_gemdocs, "changelog.txt"), "w") as f:
        f.write("""CMS v12 Change Log
==================
2026-03-27: Initialized gemdocs and test content for v12.1.0.""")

    print("\n=== CMS Setup Complete ===")

if __name__ == "__main__":
    main()
