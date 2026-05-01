"""
Library:     Lib_Doc_Architect.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: \s*(.*)", content)
            ver_match = re.search(r"Version:\s*(.*)", content)
            auth_match = re.search(r"Author:\s*(.*)", content)
            
            if desc_match: meta["description"] = desc_match.group(1).strip()
            if ver_match: meta["version"] = ver_match.group(1).strip()
            if auth_match: meta["author"] = auth_match.group(1).strip()
    except:
        pass
    return meta

def get_exports(file_path):
    """Extracts function/class definitions or exports."""
import os
import sys
import re
import json
from datetime import datetime

# Setup paths for library access
CORE_ROOT = "/storage/7B30-0E0B/Core-Command"
LIB_DIR = os.path.join(CORE_ROOT, "Lib")
LIB_PY = os.path.join(LIB_DIR, "py")
REPORT_DIR = os.path.join(LIB_DIR, "REPORTS")

if LIB_PY not in sys.path:
    sys.path.insert(0, LIB_PY)

try:
    import lib_bejson_html2 as HTML2
except ImportError:
    print("CRITICAL: lib_bejson_html2 not found.")
    sys.exit(1)

def parse_header(file_path):
    """Extracts metadata from script headers."""
    meta = {"name": os.path.basename(file_path), "description": "No description provided.", "version": "1.0.0", "author": "Unknown"}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(2000) # Read first 2k chars
            
            # Look for common header patterns
            desc_match = re.search(r"Description:\s*(.*)", content)
            ver_match = re.search(r"Version:\s*(.*)", content)
            auth_match = re.search(r"Author:\s*(.*)", content)
            
            if desc_match: meta["description"] = desc_match.group(1).strip()
            if ver_match: meta["version"] = ver_match.group(1).strip()
            if auth_match: meta["author"] = auth_match.group(1).strip()
    except:
        pass
    return meta

def get_exports(file_path):
    """Extracts function/class definitions or exports."""
    exports = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                # Python/JS/TS functions
                if line.strip().startswith(("def ", "export function ", "export const ", "class ")):
                    exports.append(line.strip())
                # Bash functions
                elif "() {" in line and not line.startswith(" "):
                    exports.append(line.split("()")[0].strip() + "()")
    except:
        pass
    return exports[:20] # Limit to top 20

def generate_docs():
    print("--- [START] Library Documentation Architecture ---")
    os.makedirs(REPORT_DIR, exist_ok=True)
    
    # Collect all library files
    lib_files = []
    for root, _, files in os.walk(LIB_DIR):
        if "REPORTS" in root or "__pycache__" in root: continue
        for f in files:
            if f.endswith((".py", ".sh", ".ts")):
                lib_files.append(os.path.join(root, f))
    
    print(f"Found {len(lib_files)} libraries.")
    
    sections = []
    
    # 1. Summary Table
    table_data = {
        "Format": "BEJSON", "Format_Version": "104", "Records_Type": ["Lib_Inventory"],
        "Fields": [{"name": "Type", "type": "string"}, {"name": "File", "type": "string"}, {"name": "Description", "type": "string"}],
        "Values": []
    }
    
    for lp in sorted(lib_files):
        meta = parse_header(lp)
        ext = os.path.splitext(lp)[1][1:].upper()
        rel_path = os.path.relpath(lp, LIB_DIR)
        table_data["Values"].append([ext, rel_path, meta["description"]])
        
        # 2. Detailed Cards (using Info Boxes)
        exp_list = "<br>".join([f"<code>{e}</code>" for e in get_exports(lp)])
        content = f"<p><strong>Author:</strong> {meta['author']} | <strong>Version:</strong> {meta['version']}</p>"
        content += f"<p>{meta['description']}</p>"
        content += f"<div style='margin-top:10px; font-size:0.75rem;'><strong>EXPORTS:</strong><br>{exp_list or 'None detected'}</div>"
        
        sections.append(HTML2.html_info_box(
            title=f"LIB: {rel_path}",
            content=content,
            link_url="#", # Future: individual doc pages
            link_label="VIEW SOURCE"
        ))

    # Build the final report
    full_html = "<h1>Core-Command Library Manifest</h1>"
    full_html += "<p style='color:var(--muted);'>Unified Documentation v2.0.0 (Auto-Generated)</p>"
    full_html += "<h2>1. Quick Reference</h2>"
    full_html += HTML2.html_table(table_data)
    full_html += "<h2>2. Component Details</h2>"
    full_html += "<div style='display:grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap:1rem;'>" + "\n".join(sections) + "</div>"
    
    out_path = os.path.join(REPORT_DIR, "INDEX.html")
    HTML2.bejson_html_save_to_file(
        full_html, 
        out_path, 
        title="Lib Documentation Index",
        meta=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    # 3. Replace Legacy Docs
    legacy_files = [
        os.path.join(LIB_DIR, "BEJSON_LIBRARY_DOCS.md"),
        os.path.join(LIB_DIR, "INDEX.md")
    ]
    for lf in legacy_files:
        if os.path.exists(lf):
            # Instead of deleting, we overwrite with a link to the new HTML
            with open(lf, 'w') as f:
                f.write(f"# Legacy Documentation Retired\n\nThis documentation has been superseded by the componentized HTML documentation system.\n\n**NEW DOCS:** [Lib/REPORTS/INDEX.html](./REPORTS/INDEX.html)\n")

    print(f"SUCCESS | Documentation suite ready at: {out_path}")
    return out_path

if __name__ == "__main__":
    p = generate_docs()
    print(f"OPEN_URL:file://{p}")
