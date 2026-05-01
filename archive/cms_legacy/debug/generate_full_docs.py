"""
Library:     generate_full_docs.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: " in code:
                for line in code.split('\n'):
                    if "Description:" in line:
                        desc = line.split("Description:")[1].strip()
                        break
            
            cms.scaffold_code_project(
                f"Library: {lib_name}",
                {lib_name: code},
                description=desc,
                category="Library Source"
            )
Create a simplified overview page in Documentation category
            cms.create_page(
                f"Overview: {lib_name}",
                category="Documentation",
                author="System Docs"
            )
Add basic content to overview
(In a real scenario, we'd use AI to write this, but here we'll place a placeholder)
        except Exception as e:
            print(f"Error processing {lib_name}: {e}")
5. Build the Site
    print("\nTriggering Site Build...")
    if cms.build_and_publish():
        print("--- Documentation Site Build SUCCESS ---")
        print(f"Location: {os.path.join(CMS_DIR, 'Processing', 'BEJSON_WEB_BUILDER', 'www')}")
    else:
        print("Build Failed.")

if __name__ == "__main__":
    main()
"""
import os
import sysSCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(LIB_DIR)

if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from BEJSON_CMS_Lib import CMSDatabase

MASTER_DB = os.path.join(PROJECT_ROOT, "Data", "BEJSON_WEB_BUILDER", "site_master.json")
# For the purpose of this script, we'll look for other libs in the project Lib dir
CORE_LIB_DIR = LIB_DIR 
CMS_LIB_PATH = os.path.join(LIB_DIR, "BEJSON_CMS_Lib.py")

def main():
    print("--- CoreGem Full Documentation Generator ---")
    cms = CMSDatabase(MASTER_DB)
    
    # 1. Sync & Clear (Starting documentation build fresh)
    cms.sync_schema()
    
    # 2. Create Categories
    cms.create_category("Documentation")
    cms.create_category("Library Source")
    
    # 3. Document the new CMS Library itself
    print("Documenting BEJSON_CMS_Lib.py...")
    if not os.path.exists(CMS_LIB_PATH):
        print(f"Error: {CMS_LIB_PATH} not found.")
    else:
        with open(CMS_LIB_PATH, 'r') as f:
            cms_code = f.read()
        
        cms.scaffold_code_project(
            "BEJSON CMS Library (v1.1.0)",
            {"BEJSON_CMS_Lib.py": cms_code},
            description="The primary high-level interface for managing BEJSON-based CMS projects. Handles database logic, scaffolding, and server control.",
            category="Library Source"
        )
    
    # 4. Scan and document all libraries in CORE_LIB_DIR
    if os.path.exists(CORE_LIB_DIR):
        libs = [f for f in os.listdir(CORE_LIB_DIR) if f.endswith('.py') or f.endswith('.js') or f.endswith('.sh')]
        for lib_name in libs:
            path = os.path.join(CORE_LIB_DIR, lib_name)
            print(f"Documenting {lib_name}...")
            try:
                with open(path, 'r') as f:
                    code = f.read()
            
            # Simple description extraction (first few lines)
            desc = "Core system library component."
            if "Description:" in code:
                for line in code.split('\n'):
                    if "Description:" in line:
                        desc = line.split("Description:")[1].strip()
                        break
            
            cms.scaffold_code_project(
                f"Library: {lib_name}",
                {lib_name: code},
                description=desc,
                category="Library Source"
            )
            
            # Create a simplified overview page in Documentation category
            cms.create_page(
                f"Overview: {lib_name}",
                category="Documentation",
                author="System Docs"
            )
            # Add basic content to overview
            # (In a real scenario, we'd use AI to write this, but here we'll place a placeholder)
        except Exception as e:
            print(f"Error processing {lib_name}: {e}")

    # 5. Build the Site
    print("\nTriggering Site Build...")
    if cms.build_and_publish():
        print("--- Documentation Site Build SUCCESS ---")
        print(f"Location: {os.path.join(CMS_DIR, 'Processing', 'BEJSON_WEB_BUILDER', 'www')}")
    else:
        print("Build Failed.")

if __name__ == "__main__":
    main()
