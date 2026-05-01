"""
Library:     BEJSON_Standard_Lib.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Core-Command library component.
"""
import json
import os
import tempfile
from typing import List, Dict, Any, Optional, Union

# ==============================================================================
# GLOBAL STATE
# ==============================================================================

_current_file: Optional[str] = None
_current_data: Optional[Dict[str, Any]] = None
_current_fmt_ver: Optional[str] = None # "104", "104a", or "104db"

_RESERVED_KEYS = ["Format", "Format_Version", "Format_Creator", "Records_Type", "Fields", "Values"]
_ALLOWED_PRIMITIVES = ["string", "integer", "number", "boolean"]
_DB_PARENT_FIELD = "Record_Type_Parent"

# ==============================================================================
# INTERNAL UTILITIES
# ==============================================================================

def _atomic_write(file_path: str, data: Dict[str, Any]) -> bool:
    """Safely writes JSON to temp file then renames (Android safe)."""
    try:
        directory = os.path.dirname(os.path.abspath(file_path))
        if not os.path.exists(directory) and directory != '':
            os.makedirs(directory)
        with tempfile.NamedTemporaryFile('w', dir=directory, delete=False, encoding='utf-8') as tf:
            json.dump(data, tf, indent=2, ensure_ascii=False)
            temp_name = tf.name
        if os.path.exists(file_path): os.remove(file_path)
        os.rename(temp_name, file_path)
        return True
    except Exception as e:
        print(f"[System] Write Error: {e}")
        return False

def _ensure_loaded() -> bool:
    if _current_data is None:
        print("[System] Error: No file loaded.")
        return False
    return True

def _get_field_index(field_name: str) -> int:
    if not _ensure_loaded(): return -1
    for i, f in enumerate(_current_data["Fields"]):
        if f['name'] == field_name: return i
    return -1

# ==============================================================================
# CORE I/O OPERATIONS
# ==============================================================================

def bejson_load(path: str) -> bool:
    """Loads any BEJSON file and detects version."""
    global _current_file, _current_data, _current_fmt_ver
    if not os.path.exists(path):
        print(f"[System] File not found: {path}")
        return False
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        ver = data.get("Format_Version")
        if ver not in ["104", "104a", "104db"]:
            print(f"[System] Warning: Unknown or unsupported format version '{ver}'.")
        
        _current_file = path
        _current_data = data
        _current_fmt_ver = ver
        print(f"[System] Loaded {os.path.basename(path)} ({ver})")
        return True
    except Exception as e:
        print(f"[System] Load Failed: {e}")
        return False

def bejson_save() -> bool:
    """Saves current memory state to disk."""
    if not _ensure_loaded(): return False
    return _atomic_write(_current_file, _current_data)

def bejson_unload():
    """Clears memory."""
    global _current_file, _current_data, _current_fmt_ver
    _current_file = None
    _current_data = None
    _current_fmt_ver = None

# ==============================================================================
# CREATION FUNCTIONS
# ==============================================================================

def bejson_create_104(path: str, record_type: str, fields: List[Dict[str, str]]) -> bool:
    """Creates strict 104 file (Single Type, No Custom Headers)."""
    if not path.endswith('.json'): path += '.json'
    structure = {
        "Format": "BEJSON", "Format_Version": "104", "Format_Creator": "Elton Boehnen",
        "Records_Type": [record_type], "Fields": fields, "Values": []
    }
    return _atomic_write(path, structure)

def bejson_create_104a(path: str, record_type: str, fields: List[Dict[str, str]], headers: Dict = None) -> bool:
    """Creates 104a file (Primitives Only, Custom Headers Allowed)."""
    if not path.endswith('.json'): path += '.json'
    # Validate Primitives
    for f in fields:
        if f['type'] not in _ALLOWED_PRIMITIVES:
            print(f"[Error] 104a violation: Field '{f['name']}' type '{f['type']}' is not primitive.")
            return False
            
    structure = {
        "Format": "BEJSON", "Format_Version": "104a", "Format_Creator": "Elton Boehnen",
        "Records_Type": [record_type], "Fields": fields, "Values": []
    }
    if headers:
        for k, v in headers.items():
            if k not in _RESERVED_KEYS: structure[k] = v
            
    return _atomic_write(path, structure)

def bejson_create_104db(path: str, initial_types: List[str] = None) -> bool:
    """Creates 104db file (Multi-Entity, Record_Type_Parent mandatory)."""
    if not path.endswith('.json'): path += '.json'
    if not initial_types: initial_types = ["Default"]
    
    structure = {
        "Format": "BEJSON", "Format_Version": "104db", "Format_Creator": "Elton Boehnen",
        "Records_Type": initial_types,
        "Fields": [{"name": _DB_PARENT_FIELD, "type": "string"}],
        "Values": []
    }
    return _atomic_write(path, structure)

# ==============================================================================
# RECORD MANIPULATION
# ==============================================================================

def bejson_add_record(values: List[Any]) -> bool:
    """
    Standard append for 104 and 104a.
    Requires list length to match field count exactly.
    """
    if not _ensure_loaded(): return False
    if len(values) != len(_current_data["Fields"]):
        print(f"[Error] Value count mismatch. Expected {len(_current_data['Fields'])}, got {len(values)}.")
        return False
    _current_data["Values"].append(values)
    return bejson_save()

def bejson_add_record_db(type_name: str, data_dict: Dict[str, Any]) -> bool:
    """
    Smart append for 104db. 
    Handles null-padding for fields belonging to other entities automatically.
    """
    if not _ensure_loaded(): return False
    if _current_fmt_ver != "104db":
        print("[Error] Use bejson_add_record for non-db formats.")
        return False
    if type_name not in _current_data["Records_Type"]:
        print(f"[Error] Type '{type_name}' not defined in Records_Type.")
        return False

    row = []
    for f in _current_data["Fields"]:
        name = f['name']
        parent = f.get('Record_Type_Parent')
        
        if name == _DB_PARENT_FIELD:
            row.append(type_name)
        elif parent is None or parent == type_name:
            # Common field or Specific field for this type
            row.append(data_dict.get(name, None))
        else:
            # Field belongs to another type -> Must be Null
            row.append(None)
            
    _current_data["Values"].append(row)
    return bejson_save()

def bejson_get_records() -> List[List[Any]]:
    """Returns raw values list."""
    if not _ensure_loaded(): return []
    return _current_data["Values"]

# ==============================================================================
# SCHEMA MANIPULATION
# ==============================================================================

def bejson_add_field(name: str, type_str: str, default_val=None, db_parent: str=None) -> bool:
    """
    Adds a field to the schema and backfills existing records.
    db_parent: (104db only) Specify which entity owns this field.
    """
    if not _ensure_loaded(): return False
    if _get_field_index(name) != -1: return False

    field_def = {"name": name, "type": type_str}
    
    if _current_fmt_ver == "104db" and db_parent:
        if db_parent in _current_data["Records_Type"]:
            field_def["Record_Type_Parent"] = db_parent
        else:
            print(f"[Error] Parent type '{db_parent}' not found.")
            return False

    _current_data["Fields"].append(field_def)
    
    # Backfill
    for row in _current_data["Values"]:
        row.append(default_val)
        
    return bejson_save()