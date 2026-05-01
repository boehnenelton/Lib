import os
import sys
import re
import json
from datetime import datetime

# Set PYTHONPATH to include the local library directory
LIB_DIR = "/storage/emulated/0/dev/lib/py"
if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)

try:
    from lib_html2_page_templates import html_page, html_save, BEJSONWiki
except ImportError:
    print("Error: Could not import lib_html2_page_templates. Ensure it exists in /storage/emulated/0/dev/lib/py")
    sys.exit(1)

ROOT_DIR = "/storage/emulated/0/dev/lib"
OUTPUT_DIR = os.path.join(ROOT_DIR, "DOCS_WIKI")

def parse_metadata(content):
    meta = {
        "description": "No description.",
        "version": "Unknown",
        "author": "Unknown",
        "jurisdiction": "Unknown"
    }
    desc_m = re.search(r"Description:\s*(.*)", content, re.IGNORECASE)
    ver_m = re.search(r"Version:\s*(.*)", content, re.IGNORECASE)
    auth_m = re.search(r"Author:\s*(.*)", content, re.IGNORECASE)
    jur_m = re.search(r"Jurisdiction:\s*(.*)", content, re.IGNORECASE)
    
    if desc_m: meta["description"] = desc_m.group(1).strip()
    if ver_m: meta["version"] = ver_m.group(1).strip()
    if auth_m: meta["author"] = auth_m.group(1).strip()
    if jur_m: meta["jurisdiction"] = jur_m.group(1).strip()
    
    return meta

def extract_functions(content, ext):
    functions = []
    if ext == ".py":
        matches = re.finditer(r"^def\s+([a-zA-Z0-9_]+)\s*\((.*?)\)\s*:", content, re.MULTILINE)
        for m in matches:
            functions.append({"name": m.group(1), "args": m.group(2)})
    elif ext in [".js", ".ts"]:
        matches = re.finditer(r"(?:export\s+)?function\s+([a-zA-Z0-9_]+)\s*\((.*?)\)", content)
        for m in matches:
            functions.append({"name": m.group(1), "args": m.group(2)})
    elif ext == ".sh":
        matches = re.finditer(r"^([a-zA-Z0-9_]+)\s*\(\)\s*\{", content, re.MULTILINE)
        for m in matches:
            functions.append({"name": m.group(1), "args": ""})
    elif ext == ".rs":
        matches = re.finditer(r"(?:pub\s+)?fn\s+([a-zA-Z0-9_]+)\s*\((.*?)\)", content)
        for m in matches:
            functions.append({"name": m.group(1), "args": m.group(2)})
    return functions

def main():
    print("--- [DOC-ARCHITECT] Starting Categorized Rebuild ---")
    wiki = BEJSONWiki(title="BEJSON/MFDB Official Docs", output_dir=OUTPUT_DIR, root_dir=ROOT_DIR)
    
    targets = {
        "PYTHON": os.path.join(ROOT_DIR, "py"),
        "JAVASCRIPT": os.path.join(ROOT_DIR, "js"),
        "TYPESCRIPT": os.path.join(ROOT_DIR, "ts"),
        "SHELL": os.path.join(ROOT_DIR, "sh"),
        "RUST": os.path.join(ROOT_DIR, "rs")
    }

    for lang, path in targets.items():
        if not os.path.exists(path): continue
        print(f"Processing {lang}...")
        
        # ADD MANUAL ENTRY FOR ENV: KEYS
        if lang == "PYTHON":
            wiki.pages.append({
                "name": "ENV: Keys",
                "url": "env_bejson_py.html",
                "category": "PYTHON",
                "tags": ["SYSTEM", "ENV"],
                "content": """
                <div class="glass-stats" style="margin-bottom:20px;">
                    <div class="glass-stats__item">
                        <span class="glass-stats__label">PROTOCOL</span>
                        <span class="glass-stats__value">BEJSON 104a</span>
                    </div>
                    <div class="glass-stats__item">
                        <span class="glass-stats__label">STATUS</span>
                        <span class="glass-stats__value">CENTRALIZED</span>
                    </div>
                </div>
                <div class="page-header">
                    <h1>Environment & Key Management</h1>
                    <p>Standardized BEJSON-based API key rotation and storage.</p>
                </div>
                <section style="margin-bottom:40px;">
                    <h2>Overview</h2>
                    <p>The system has migrated from hardcoded keys and flat <code>.env</code> files to a centralized **BEJSON 104a** registry. This ensures type safety, schema validation, and seamless key rotation across all libraries.</p>
                </section>
                <section style="margin-bottom:40px;">
                    <h2>Registry Path</h2>
                    <p>The primary key registry is located at:</p>
                    <pre>/data/data/com.termux/files/home/.env/api_keys_v2_decrypted.104a.bejson</pre>
                </section>
                <section style="margin-bottom:40px;">
                    <h2>BEJSON 104a Template</h2>
                    <p>The registry must follow the <code>ApiKeyRegistry</code> schema:</p>
                    <pre>{
  "Format": "BEJSON",
  "Format_Version": "104a",
  "Format_Creator": "Elton Boehnen",
  "Schema_Name": "ApiKeyRegistry",
  "Records_Type": ["ApiKey"],
  "Fields": [
    { "name": "key_slot", "type": "integer" },
    { "name": "key", "type": "string" }
  ],
  "Values": [
    [1, "AIzaSy..."],
    [2, "AIzaSy..."]
  ]
}</pre>
                </section>
                """,
                "source_rel_path": "README_ENV.md"
            })
        
        for root, _, files in os.walk(path):
            if "__pycache__" in root or "target" in root: continue
            for f in files:
                ext = os.path.splitext(f)[1]
                if ext not in [".py", ".sh", ".ts", ".js", ".rs"]: continue
                
                f_path = os.path.join(root, f)
                with open(f_path, "r", encoding="utf-8", errors="ignore") as file:
                    content = file.read()
                
                meta = parse_metadata(content)
                funcs = extract_functions(content, ext)
                
                rel_path = os.path.relpath(f_path, ROOT_DIR)
                
                # Build Detail Content
                detail_html = f"""
                <div class="glass-stats" style="margin-bottom:20px;">
                    <div class="glass-stats__item">
                        <span class="glass-stats__label">LANGUAGE</span>
                        <span class="glass-stats__value">{lang}</span>
                    </div>
                    <div class="glass-stats__item">
                        <span class="glass-stats__label">VERSION</span>
                        <span class="glass-stats__value">{meta['version']}</span>
                    </div>
                    <div class="glass-stats__item">
                        <span class="glass-stats__label">JURISDICTION</span>
                        <span class="glass-stats__value">{meta['jurisdiction']}</span>
                    </div>
                </div>
                <div class="card" style="margin-bottom:30px;">
                    <p>{meta['description']}</p>
                </div>
                <h3>Exported Functions</h3>
                <div class="table-container">
                <table class="data-table">
                    <thead><tr><th>Function Name</th><th>Arguments</th></tr></thead>
                    <tbody>
                """
                for fn in funcs:
                    detail_html += f"<tr><td><code>{fn['name']}</code></td><td><code>{fn['args']}</code></td></tr>"
                
                if not funcs:
                    detail_html += "<tr><td colspan='2' style='text-align:center;'>No functions detected.</td></tr>"
                
                detail_html += "</tbody></table></div>"
                
                wiki.pages.append({
                    "name": f,
                    "url": f.replace(".", "_") + ".html",
                    "category": lang,
                    "tags": [lang, "LIB"],
                    "content": detail_html,
                    "source_rel_path": rel_path
                })

    # Render all pages
    wiki.render_all()
    print(f"--- [SUCCESS] Documentation suite generated at {ROOT_DIR}/library_docs.html ---")

if __name__ == "__main__":
    main()
