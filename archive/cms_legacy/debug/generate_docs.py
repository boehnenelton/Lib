"""
Library:     generate_docs.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Core-Command library component.
"""
import os
import sys
import json
import uuidSCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(LIB_DIR)

if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import BEJSON_Standard_Lib as StdLib
import BEJSON_Extended_Lib as ExtLib
try:
    import lib_bejson_gemini as GeminiLib
except ImportError:
    GeminiLib = None # Might be outside project

from Flask_Page_Editor import _write_page_record, MASTER_DB

def generate_bejson_docs():
    print("--- BEJSON DOCUMENTATION GENERATOR ---")
    
    # 1. Setup Engine
    key_file = os.path.join(PROJECT_ROOT, "Gemini_API_Keys.bejson.json")
    if not GeminiLib:
        print("FAIL: lib_bejson_gemini not found. Check sys.path.")
        return
    km = GeminiLib.GeminiKeyManager(key_file)
    engine = GeminiLib.GeminiJobEngine(km, model="gemini-flash-latest")
    builder = GeminiLib.GeminiBuilder(engine)
    
    # 2. Context
    ctx_path = os.path.join(PROJECT_ROOT, "Context", "bejson_crash_course.txt")
    if not os.path.exists(ctx_path):
        print(f"FAIL: {ctx_path} not found.")
        return
    with open(ctx_path, 'r') as f:
        crash_course = f.read()
    
    context_parts = [{"text": f"[OFFICIAL REFERENCE: BEJSON CRASH COURSE]\n{crash_course}"}]
    
    # 3. Plan
    prompt = "Create a comprehensive 4-page documentation site for BEJSON based on the crash course. Include: Introduction, Version 104 vs 104a, Version 104db (Databases), and Best Practices/Validation."
    print("Generating Plan...")
    plan = builder.generate_plan(prompt, emit=lambda e: print(f"  [Plan] {e.get('message', e.get('type'))}"))
    
    if not plan:
        print("FAIL: No plan.")
        return

    # 4. Build
    print("\nBuilding Pages...")
    def writer_cb(step, content):
        page_uuid = str(uuid.uuid4())
        print(f"  [Writer] Saving: {step['title']}")
        _write_page_record(
            page_uuid=page_uuid,
            title=step['title'],
            category="BEJSON Documentation",
            author="Gemini CLI Builder",
            body_html=content,
            is_new=True
        )

    success = builder.build_pages(
        plan, "BEJSON Documentation", "Gemini CLI Builder",
        context_parts=context_parts,
        emit=lambda e: print(f"  [Build] {e.get('message', e.get('type'))}"),
        page_writer_callback=writer_cb
    )

    if success:
        print("\nSUCCESS: Documentation generated.")
        # 5. Trigger Publisher (if possible)
        # In this environment, we just run the publisher script or call its logic
        # For now, let's just confirm the records are there.
    else:
        print("\nFAIL: Generation failed.")

if __name__ == "__main__":
    generate_bejson_docs()
