"""
Library:     build_final_docs.py
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
PROJECT_ROOT = os.path.dirname(LIB_DIR)

if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from BEJSON_CMS_Lib import CMSDatabase
from BEJSON_CMS_Gen_Lib import ContentGenerator

MASTER_DB = os.path.join(PROJECT_ROOT, "Data", "BEJSON_WEB_BUILDER", "site_master.json")
CORE_LIB_DIR = LIB_DIR
CMS_LIB_PATH = os.path.join(LIB_DIR, "BEJSON_CMS_Lib.py")
GEN_LIB_PATH = os.path.join(LIB_DIR, "BEJSON_CMS_Gen_Lib.py")

def main():
    print("--- [boehnenelton2024] Final AI Documentation Build ---")
    cms = CMSDatabase(MASTER_DB)
    gen = ContentGenerator()
    
    # 1. Fresh Reset for Production Build
    cms.factory_reset(confirm=True)
    
    # 2. Config
    cms._load()
    cms.set_config("title", "boehnenelton2024")
    cms.set_config("creator", "boehnenelton2024")
    cms._unload()
    
    cms.create_category("Docs")
    cms.create_category("Source")
    
    # 3. Process All Libraries
    # Combine Lib paths
    target_files = [CMS_LIB_PATH, GEN_LIB_PATH]
    if os.path.exists(CORE_LIB_DIR):
        for f in os.listdir(CORE_LIB_DIR):
            if f.endswith(('.py', '.sh', '.js')):
                target_files.append(os.path.join(CORE_LIB_DIR, f))
            
    for file_path in target_files:
        if not os.path.exists(file_path): continue
        name = os.path.basename(file_path)
        print(f"\nProcessing: {name}...")
        
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            # A. Generate AI Documentation Page
            topic = f"Documentation for the '{name}' library in the CoreGem ecosystem. Explain its purpose, key functions, and usage examples."
            gen.generate_and_save_page(
                cms, 
                topic, 
                category="Docs", 
                persona="Senior Software Architect",
                title=name # Explicitly use filename as title
            )
            
            # B. Create Source Code Page
            cms.scaffold_code_project(
                f"Source: {name}",
                {name: code},
                description=f"Raw source code for {name}.",
                category="Source"
            )
            
        except Exception as e:
            print(f"Error documenting {name}: {e}")

    # 4. Final Build
    print("\n[FINISHING] Building Site with Dark Overlay Theme...")
    if cms.build_and_publish(stylesheet="dark.css"):
        print("\n[SYNC] Copying build to external storage...")
        cms.sync_to_external_storage("/storage/emulated/0/www")
        
        print("\n" + "="*60)
        print(" PRODUCTION SITE BUILT SUCCESSFULLY ")
        print(" Name: boehnenelton2024")
        print(f" Local Path: {os.path.join(CMS_DIR, 'Processing', 'BEJSON_WEB_BUILDER', 'www', 'index.html')}")
        print(f" External Path: /storage/emulated/0/www/index.html")
        print("="*60)
    else:
        print("Build Failed.")

if __name__ == "__main__":
    main()
