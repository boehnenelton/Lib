"""
Library:     lib_brain_helper.py
Family:      AI
Jurisdiction: ["PYTHON", "BEJSON_LIBRARIES"]
Status:      OFFICIAL
Author:      Elton Boehnen
Version:     1.5 OFFICIAL
MFDB Version: 1.3.1
Format_Creator: Elton Boehnen
Date:        2026-05-01
Description: High-level helper library for querying and managing the Workspace Brain MFDB.
             Wraps foundational MFDB core libraries and utilizes the Mount-Commit pattern.
"""

import os
import sys
from typing import Any, Callable, Optional, List, Dict

# Resolve paths
HOME = "/Data/Data/com.termux/files/home"
CORE_DIR = "{SC_ROOT}/Core"
if CORE_DIR not in sys.path:
    sys.path.append(CORE_DIR)

import env
env.setup_python_path()

import switchboard
from lib_mfdb_core import (
    mfdb_core_load_entity,
    mfdb_core_add_entity_record,
    mfdb_core_update_entity_record,
    mfdb_core_remove_entity_record
)

def brain_load_entity(entity_name: str) -> List[Dict[str, Any]]:
    """Loads all records for a specific entity from the Brain MFDB."""
    return switchboard.handle_operation(mfdb_core_load_entity, entity_name) or []

def brain_query_entity(entity_name: str, predicate: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]:
    """Returns a list of records matching a specific filter function."""
    records = brain_load_entity(entity_name)
    return [r for r in records if predicate(r)]

def brain_get_record(entity_name: str, field: str, value: Any) -> Optional[Dict[str, Any]]:
    """Finds and returns a single record dict based on a field match."""
    records = brain_load_entity(entity_name)
    return next((r for r in records if r.get(field) == value), None)

def brain_add_record(entity_name: str, values: List[Any]) -> bool:
    """Adds a new record to an entity with automated manifest synchronization."""
    result = switchboard.handle_operation(mfdb_core_add_entity_record, entity_name, values)
    return result is not None

def brain_update_record(entity_name: str, search_field: str, search_value: Any, update_field: str, new_value: Any) -> bool:
    """Updates a specific field in a record found by a search criterion."""
    def _update(manifest, **kwargs):
        records = mfdb_core_load_entity(manifest, entity_name)
        idx = next((i for i, r in enumerate(records) if r.get(search_field) == search_value), -1)
        if idx == -1:
            return False
        mfdb_core_update_entity_record(manifest, entity_name, idx, update_field, new_value)
        return True
    
    result = switchboard.handle_operation(_update, force_commit=True)
    return bool(result)

def brain_remove_record(entity_name: str, search_field: str, search_value: Any) -> bool:
    """Removes a record from an entity found by a search criterion."""
    def _remove(manifest, **kwargs):
        records = mfdb_core_load_entity(manifest, entity_name)
        idx = next((i for i, r in enumerate(records) if r.get(search_field) == search_value), -1)
        if idx == -1:
            return False
        mfdb_core_remove_entity_record(manifest, entity_name, idx)
        return True
    
    result = switchboard.handle_operation(_remove, force_commit=True)
    return bool(result)

# --- Specialized Helpers ---

def brain_get_node(path: str) -> Optional[Dict[str, Any]]:
    """Specialized helper to retrieve a WorkspaceNode by its path."""
    return brain_get_record("WorkspaceNode", "path", path)

def brain_get_policy(title: str) -> Optional[Dict[str, Any]]:
    """Specialized helper to retrieve a Policy by its title."""
    return brain_get_record("Policy", "title", title)

def brain_get_switch(key: str) -> Optional[Dict[str, Any]]:
    """Specialized helper to retrieve a SwitchBoard entry by its key."""
    return brain_get_record("SwitchBoard", "key", key)

if __name__ == "__main__":
    # Quick sanity check: list policies
    policies = brain_load_entity("Policy")
    print(f"Loaded {len(policies)} policies from Brain.")
    for p in policies:
        print(f"- {p.get('title')}")
