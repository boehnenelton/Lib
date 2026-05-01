"""
Library:     BEJSON_Extended_Lib.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: " in line: description = line.split("Description:")[-1].strip()
            if "Version:" in line: version = line.split("Version:")[-1].strip()
            if "Author:" in line: author = line.split("Author:")[-1].strip()
            
        content = "".join(lines)
        
        body = f"<div class='meta-box' style='background:var(--bg-footer);padding:15px;border-radius:8px;margin-bottom:20px;border-left:4px solid var(--accent-color);'>"
        body += f"<p><strong>Description:</strong> {description or 'No description provided.'}</p>"
        body += f"<p><strong>Version:</strong> {version} | <strong>Author:</strong> {author}</p>"
        body += f"</div>"
We just need to wrap the body and code snippet into a page format.
Since this method generates an *HTML body*, not a full page, 
we can just use the html library's standard output structures if applicable,
but to match existing tabs:
        content_esc = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        tabs_html = f"<div class='bej-multi-file-viewer'>"
        tabs_html += f"<div class='bej-tabs'><button class='bej-tab-btn active' onclick='bejOpenTab(event, \"tab-0\")' style='padding:10px 16px;border:none;cursor:pointer;'>{fname}</button></div>"
        tabs_html += f"<div id='tab-0' class='bej-tab-content' style='display:block;background:var(--code-bg);padding:20px;color:var(--code-text);font-family:monospace;overflow-x:auto;'>"
        tabs_html += f"<pre><code>{content_esc}</code></pre></div></div>"
        tabs_html += BEJSONHtml._sort_js() + "<style>.bej-tab-btn.active{background:#DE2626!important;color:#fff!important;}</style>"
        
        return f"<div class='source-doc'><h2>Source: {fname}</h2>{body}{tabs_html}</div>"
==============================================================================
MODULE 7: AI MULTI-PAGE BUILDER (CMS INTEGRATION)
==============================================================================

class CMSAIBuilder:
    """CMS-specific wrapper for Multi-Page AI generation."""
    
    @staticmethod
    def setup_gemini(model: str = "gemini-3-flash-preview"):
        """Loads the global Gemini library and returns an engine."""
Try to find global lib
        BEC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        LIB_PY = os.path.join(BEC_ROOT, "lib", "py")
        if LIB_PY not in sys.path: sys.path.append(LIB_PY)
        
        try:
            import lib_bejson_gemini as GeminiLib
Find keys in root
            key_file = os.path.join(BEC_ROOT, "Gemini_API_Keys.bejson.json")
            if not os.path.exists(key_file):
                key_file = os.path.join(os.path.expanduser("~"), "Gemini_API_Keys.bejson.json")
                
            km = GeminiLib.GeminiKeyManager(key_file)
            engine = GeminiLib.GeminiJobEngine(km, model=model)
            return GeminiLib.GeminiBuilder(engine)
        except ImportError:
            print("[CMSAIBuilder] Error: lib_bejson_gemini not found.")
            return None
        except Exception as e:
            print(f"[CMSAIBuilder] Error setting up Gemini: {e}")
            return None
"""
import json
import os
import re
import random
import string
import base64
import sys
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List, Union

# ------------------------------------------------------------------------------
# DEPENDENCY: BEJSON Standard Library (Core IO)
# ------------------------------------------------------------------------------
try:
    import BEJSON_Standard_Lib as StdLib
except ImportError:
    print("[ExtendedLib] CRITICAL: 'BEJSON_Standard_Lib.py' not found.")
    StdLib = None

# ------------------------------------------------------------------------------
# OPTIONAL DEPENDENCY: Cryptography
# ------------------------------------------------------------------------------
HAS_CRYPTO = False
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTO = True
except ImportError:
    pass

# ==============================================================================
# MODULE 1: ROBUST JSON PARSING (AI TEXT CLEANER)
# ==============================================================================

def _clean_json_newlines(json_str: str) -> str:
    """Escapes control characters (newlines/tabs) inside JSON strings."""
    result = []
    in_string = False
    escape = False
    for char in json_str:
        if char == '"' and not escape: in_string = not in_string
        if char == '\\' and not escape:
            escape = True; result.append(char); continue
        if escape:
            escape = False; result.append(char); continue
        if in_string:
            if char == '\n': result.append('\\n')
            elif char == '\r': continue
            elif char == '\t': result.append('\\t')
            else: result.append(char)
        else: result.append(char)
    return "".join(result)

def _robust_json_extractor(text: str) -> Optional[str]:
    """Extracts JSON from Markdown or raw text."""
    match = re.search(r"```json(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match: return match.group(1).strip()
    match = re.search(r"```(.*?)```", text, re.DOTALL)
    if match: return match.group(1).strip()
    start_idx = text.find('{')
    if start_idx == -1: return None
    balance = 0; found_start = False
    for i in range(start_idx, len(text)):
        if text[i] == '{': balance += 1; found_start = True
        elif text[i] == '}': balance -= 1
        if found_start and balance == 0: return text[start_idx : i+1]
    return None

def parse_any_json(text: str) -> Optional[Dict[str, Any]]:
    """Converts raw AI text -> Python Dict."""
    raw = _robust_json_extractor(text)
    if not raw: return None
    try: return json.loads(_clean_json_newlines(raw))
    except: return None

# ==============================================================================
# MODULE 2: UNIVERSAL UNPACKER (AI + ARCHIVES)
# ==============================================================================

def extract_files_universal(input_data: Union[str, Dict], destination_root: str) -> Tuple[bool, str]:
    """Detects Schema Type (Wide AI vs Tall Archive) and extracts files."""
    data = None
    if isinstance(input_data, str):
        data = parse_any_json(input_data)
        if not data: return False, "No valid JSON found in text."
    else:
        data = input_data

    if not data or "Values" not in data or not data["Values"]:
        return False, "JSON contains no data values."

    field_names = [f['name'] for f in data.get("Fields", [])]
    is_wide = "file1_name" in field_names
    is_tall = "file_path" in field_names and ("content" in field_names or "content_base64" in field_names)

    if is_wide: return _extract_wide_schema(data, destination_root)
    elif is_tall: return _extract_tall_schema(data, destination_root)
    else: return False, "Unknown Schema: Could not detect file structure."

def _extract_wide_schema(data: Dict, root: str) -> Tuple[bool, str]:
    try:
        row = data["Values"][0]
        fields = data["Fields"]
        def get_val(n):
            for i, f in enumerate(fields):
                if f['name'] == n and i < len(row): return row[i]
            return None

        p_name = get_val("project_tree") or "AI_Gen_" + ''.join(random.choices(string.ascii_uppercase, k=4))
        p_ver = get_val("project_version") or "1.0"
        target_dir = os.path.join(root, p_name, p_ver)
        
        saved_count = 0
        for i in range(1, 21):
            fname = get_val(f"file{i}_name")
            fcontent = get_val(f"file{i}_content")
            if fname and fcontent is not None:
                if fname.startswith("/"): fname = fname[1:]
                full_path = os.path.join(target_dir, fname)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f: f.write(fcontent)
                saved_count += 1
        return True, f"Extracted {saved_count} files (Wide Mode) to: {target_dir}"
    except Exception as e: return False, f"Wide Extraction Error: {e}"

def _extract_tall_schema(data: Dict, root: str) -> Tuple[bool, str]:
    try:
        records = data["Values"]
        fields = data["Fields"]
        archive_name = data.get("Archive_Root_Name", "Restored_Archive")
        target_dir = os.path.join(root, archive_name)
        
        idx_path = next((i for i, f in enumerate(fields) if f['name'] == "file_path"), -1)
        idx_content = next((i for i, f in enumerate(fields) if f['name'] == "content"), -1)
        idx_b64 = next((i for i, f in enumerate(fields) if f['name'] == "content_base64"), -1)
        
        if idx_path == -1: return False, "Missing 'file_path'."

        saved_count = 0
        for row in records:
            rel_path = row[idx_path]
            content = None
            is_bin = False
            if idx_b64 != -1 and row[idx_b64]: content = row[idx_b64]; is_bin = True
            elif idx_content != -1: content = row[idx_content]
            
            if content is None or ".." in rel_path or rel_path.startswith("/"): continue
            full_path = os.path.join(target_dir, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            if is_bin:
                with open(full_path, 'wb') as f: f.write(base64.b64decode(content))
            else:
                with open(full_path, 'w', encoding='utf-8') as f: f.write(content)
            saved_count += 1
        return True, f"Extracted {saved_count} files (Tall Mode) to: {target_dir}"
    except Exception as e: return False, f"Tall Extraction Error: {e}"

# ==============================================================================
# MODULE 3: ARCHIVER / PACKER
# ==============================================================================

def bejson_pack_folder(folder_path: str, output_json: str) -> bool:
    """Packs a folder into a Base64-encoded BEJSON 104a file."""
    if not StdLib or not os.path.exists(folder_path): return False
    records = []
    folder_path = os.path.abspath(folder_path)
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for file in files:
            if file.startswith('.'): continue
            full = os.path.join(root, file)
            rel = os.path.relpath(full, folder_path)
            try:
                with open(full, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')
                records.append([rel, b64])
            except: pass

    headers = {
        "Archive_Root_Name": os.path.basename(folder_path),
        "Archive_Timestamp": datetime.now().isoformat(),
        "File_Count": len(records)
    }
    fields = [{"name": "file_path", "type": "string"}, {"name": "content_base64", "type": "string"}]
    
    if StdLib.bejson_create_104a(output_json, "ArchivedFile", fields, headers):
        if StdLib.bejson_load(output_json):
            for r in records: StdLib.bejson_add_record(r)
            return True
    return False

def bejson_merge_archives(archive_paths: List[str], output_json: str) -> bool:
    """Merges multiple BEJSON archives."""
    if not StdLib: return False
    merged_recs = []
    for path in archive_paths:
        if StdLib.bejson_load(path): merged_recs.extend(StdLib.bejson_get_records())
            
    fields = [{"name": "file_path", "type": "string"}, {"name": "content_base64", "type": "string"}]
    headers = {"Archive_Root_Name": "Merged_Archive", "Archive_Timestamp": datetime.now().isoformat()}
    
    if StdLib.bejson_create_104a(output_json, "ArchivedFile", fields, headers):
        if StdLib.bejson_load(output_json):
            for r in merged_recs: StdLib.bejson_add_record(r)
            return True
    return False

# ==============================================================================
# MODULE 4: ROW-LEVEL ENCRYPTION (AES-256-GCM)
# ==============================================================================

_FIELD_IS_ENC = "is_encrypted"
_FIELD_ENC_DATA = "encrypted_data"

def _derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=600000, backend=default_backend())
    return kdf.derive(password.encode('utf-8'))

def bejson_setup_encryption() -> bool:
    """Adds encryption fields to schema if missing."""
    if not StdLib or not StdLib._ensure_loaded(): return False
    changed = False
    if StdLib.bejson_add_field(_FIELD_IS_ENC, "boolean", default_val=False): changed = True
    if StdLib.bejson_add_field(_FIELD_ENC_DATA, "string", default_val=None): changed = True
    return True

def bejson_encrypt_row(row_index: int, password: str) -> bool:
    """Encrypts a single row, hiding values but keeping structure."""
    if not HAS_CRYPTO or not StdLib or not StdLib._ensure_loaded(): return False
    data = StdLib._current_data
    records = data["Values"]
    if row_index < 0 or row_index >= len(records): return False
    target_row = records[row_index]
    
    idx_is = StdLib._get_field_index(_FIELD_IS_ENC)
    idx_data = StdLib._get_field_index(_FIELD_ENC_DATA)
    if idx_is == -1 or idx_data == -1: return False
    if target_row[idx_is]: return False 

    try:
        payload = json.dumps(target_row)
        salt = os.urandom(16)
        iv = os.urandom(12)
        key = _derive_key(password, salt)
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(iv, payload.encode('utf-8'), None)
        blob = f"{base64.b64encode(salt).decode('utf-8')}:{base64.b64encode(iv).decode('utf-8')}:{base64.b64encode(ciphertext).decode('utf-8')}"
        
        masked_row = [None] * len(target_row)
        masked_row[0] = target_row[0]
        masked_row[idx_is] = True
        masked_row[idx_data] = blob
        records[row_index] = masked_row
        return StdLib.bejson_save()
    except Exception as e:
        print(f"[Security] Encrypt Error: {e}")
        return False

def bejson_decrypt_row(row_index: int, password: str) -> bool:
    """Decrypts a row and restores original values."""
    if not HAS_CRYPTO or not StdLib or not StdLib._ensure_loaded(): return False
    data = StdLib._current_data
    records = data["Values"]
    fields = data["Fields"]
    if row_index < 0 or row_index >= len(records): return False
    target_row = records[row_index]
    
    idx_is = StdLib._get_field_index(_FIELD_IS_ENC)
    idx_data = StdLib._get_field_index(_FIELD_ENC_DATA)
    if idx_is == -1 or not target_row[idx_is]: return False

    try:
        blob = target_row[idx_data]
        parts = blob.split(':')
        salt = base64.b64decode(parts[0])
        iv = base64.b64decode(parts[1])
        ct = base64.b64decode(parts[2])
        key = _derive_key(password, salt)
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(iv, ct, None)
        orig_row = json.loads(plaintext.decode('utf-8'))
        
        new_restored = [None] * len(fields)
        for i in range(min(len(orig_row), len(fields))): new_restored[i] = orig_row[i]
        new_restored[idx_is] = False
        new_restored[idx_data] = None
        records[row_index] = new_restored
        return StdLib.bejson_save()
    except Exception as e:
        print(f"[Security] Decrypt Error: {e}")
        return False

# ==============================================================================
# MODULE 5: DATABASE HELPERS
# ==============================================================================

def bejson_filter_db_records(record_type: str) -> List[Dict[str, Any]]:
    """
    Retrieves all records of a specific type from the currently loaded 104db file
    and converts them into a list of Dictionaries for easy access.
    """
    if not StdLib or not StdLib._ensure_loaded(): return []
    
    data = StdLib._current_data
    if data.get("Format_Version") != "104db":
        print("[ExtendedLib] Error: Loaded file is not 104db.")
        return []

    fields = data["Fields"]
    values = data["Values"]
    
    type_idx = -1
    for i, f in enumerate(fields):
        if f['name'] == "Record_Type_Parent":
            type_idx = i
            break
            
    if type_idx == -1: return []

    results = []
    for row in values:
        if len(row) > type_idx and row[type_idx] == record_type:
            record_dict = {}
            for i, val in enumerate(row):
                if i < len(fields):
                    field_name = fields[i]['name']
                    record_dict[field_name] = val
            results.append(record_dict)
            
    return results
# ==============================================================================
# MODULE 6: CONTENT GENERATION HELPERS (Source Documentation)
# ==============================================================================

class SourceDocGenerator:
    """Helper to generate CMS-ready HTML documentation from source files."""
    
    @staticmethod
    def generate_html_body(file_path: str) -> str:
        import os
        import sys
        
        # Load the html library
        BEC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        LIB_PY = os.path.join(BEC_ROOT, "lib", "py")
        if LIB_PY not in sys.path: sys.path.append(LIB_PY)
        
        try:
            import lib_bejson_html as BEJSONHtml
        except ImportError:
            # Fallback if not found in standard paths
            try:
                # Assuming it might be accessible via parent or another path
                sys.path.append(os.path.abspath("/storage/7B30-0E0B/Core-Command/Lib/py"))
                import lib_bejson_html as BEJSONHtml
            except ImportError:
                return "<p>Error: lib_bejson_html not found.</p>"

        if not os.path.exists(file_path):
            return "<p>File not found.</p>"
            
        fname = os.path.basename(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            return f"<p>Error reading file: {e}</p>"
            
        # Extract metadata from header comments
        description = ""
        version = "Unknown"
        author = "Unknown"
        
        for line in lines[:20]:
            if "Description:" in line: description = line.split("Description:")[-1].strip()
            if "Version:" in line: version = line.split("Version:")[-1].strip()
            if "Author:" in line: author = line.split("Author:")[-1].strip()
            
        content = "".join(lines)
        
        body = f"<div class='meta-box' style='background:var(--bg-footer);padding:15px;border-radius:8px;margin-bottom:20px;border-left:4px solid var(--accent-color);'>"
        body += f"<p><strong>Description:</strong> {description or 'No description provided.'}</p>"
        body += f"<p><strong>Version:</strong> {version} | <strong>Author:</strong> {author}</p>"
        body += f"</div>"
        
        # We just need to wrap the body and code snippet into a page format.
        # Since this method generates an *HTML body*, not a full page, 
        # we can just use the html library's standard output structures if applicable,
        # but to match existing tabs:
        content_esc = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        tabs_html = f"<div class='bej-multi-file-viewer'>"
        tabs_html += f"<div class='bej-tabs'><button class='bej-tab-btn active' onclick='bejOpenTab(event, \"tab-0\")' style='padding:10px 16px;border:none;cursor:pointer;'>{fname}</button></div>"
        tabs_html += f"<div id='tab-0' class='bej-tab-content' style='display:block;background:var(--code-bg);padding:20px;color:var(--code-text);font-family:monospace;overflow-x:auto;'>"
        tabs_html += f"<pre><code>{content_esc}</code></pre></div></div>"
        tabs_html += BEJSONHtml._sort_js() + "<style>.bej-tab-btn.active{background:#DE2626!important;color:#fff!important;}</style>"
        
        return f"<div class='source-doc'><h2>Source: {fname}</h2>{body}{tabs_html}</div>"
        
# ==============================================================================
# MODULE 7: AI MULTI-PAGE BUILDER (CMS INTEGRATION)
# ==============================================================================

class CMSAIBuilder:
    """CMS-specific wrapper for Multi-Page AI generation."""
    
    @staticmethod
    def setup_gemini(model: str = "gemini-3-flash-preview"):
        """Loads the global Gemini library and returns an engine."""
        # Try to find global lib
        BEC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        LIB_PY = os.path.join(BEC_ROOT, "lib", "py")
        if LIB_PY not in sys.path: sys.path.append(LIB_PY)
        
        try:
            import lib_bejson_gemini as GeminiLib
            # Find keys in root
            key_file = os.path.join(BEC_ROOT, "Gemini_API_Keys.bejson.json")
            if not os.path.exists(key_file):
                key_file = os.path.join(os.path.expanduser("~"), "Gemini_API_Keys.bejson.json")
                
            km = GeminiLib.GeminiKeyManager(key_file)
            engine = GeminiLib.GeminiJobEngine(km, model=model)
            return GeminiLib.GeminiBuilder(engine)
        except ImportError:
            print("[CMSAIBuilder] Error: lib_bejson_gemini not found.")
            return None
        except Exception as e:
            print(f"[CMSAIBuilder] Error setting up Gemini: {e}")
            return None
