"""
Library:     bejson_template_gen.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Generate BEJSON template files for common use cases.
"""
"""

import argparse
import json
import os
import sys
from pathlib import Path

LIB_DIR = os.path.dirname(os.path.abspath(__file__))
if LIB_DIR not in sys.path:
    sys.path.append(LIB_DIR)

from lib_bejson_core import (
    bejson_core_create_104,
    bejson_core_create_104a,
    bejson_core_create_104db,
    bejson_core_atomic_write,
)

class C:
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"

# ─── Template definitions ────────────────────────────────────────────────

TEMPLATES = {}

def register(name, desc, builder):
    TEMPLATES[name] = {"desc": desc, "build": builder}


def register_all():
    # Project Manager (104db: Project, Task)
    def build_projects(**kwargs):
        return bejson_core_create_104db(
            ["Project", "Task"],
            [
                {"name": "Record_Type_Parent", "type": "string"},
                {"name": "project_id", "type": "string", "Record_Type_Parent": "Project"},
                {"name": "project_name", "type": "string", "Record_Type_Parent": "Project"},
                {"name": "project_status", "type": "string", "Record_Type_Parent": "Project"},
                {"name": "project_priority", "type": "string", "Record_Type_Parent": "Project"},
                {"name": "project_description", "type": "string", "Record_Type_Parent": "Project"},
                {"name": "project_created", "type": "string", "Record_Type_Parent": "Project"},
                {"name": "task_id", "type": "string", "Record_Type_Parent": "Task"},
                {"name": "task_name", "type": "string", "Record_Type_Parent": "Task"},
                {"name": "task_status", "type": "string", "Record_Type_Parent": "Task"},
                {"name": "task_priority", "type": "string", "Record_Type_Parent": "Task"},
                {"name": "project_id_fk", "type": "string", "Record_Type_Parent": "Task"},
                {"name": "assigned_to", "type": "string", "Record_Type_Parent": "Task"},
                {"name": "task_due_date", "type": "string", "Record_Type_Parent": "Task"},
            ],
            []
        )

    register("projects", "Project & Task tracker (104db: Project, Task)", build_projects)

    # Contacts (104)
    def build_contacts(**kwargs):
        return bejson_core_create_104("Contact", [
            {"name": "contact_id", "type": "string"},
            {"name": "first_name", "type": "string"},
            {"name": "last_name", "type": "string"},
            {"name": "email", "type": "string"},
            {"name": "phone", "type": "string"},
            {"name": "company", "type": "string"},
            {"name": "tags", "type": "array"},
            {"name": "notes", "type": "string"},
            {"name": "created_at", "type": "string"},
        ], [])

    register("contacts", "Contact address book", build_contacts)

    # Inventory (104a with custom headers)
    def build_inventory(**kwargs):
        return bejson_core_create_104a("InventoryItem", [
            {"name": "item_id", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "category", "type": "string"},
            {"name": "quantity", "type": "integer"},
            {"name": "price", "type": "number"},
            {"name": "location", "type": "string"},
            {"name": "is_active", "type": "boolean"},
            {"name": "last_updated", "type": "string"},
        ], [],
        Database_Name="Inventory",
        Schema_Version="v1.0",
        Owner="User"
        )

    register("inventory", "Inventory management (104a)", build_inventory)

    # Tasks (104)
    def build_tasks(**kwargs):
        return bejson_core_create_104("Task", [
            {"name": "task_id", "type": "string"},
            {"name": "title", "type": "string"},
            {"name": "description", "type": "string"},
            {"name": "status", "type": "string"},
            {"name": "priority", "type": "string"},
            {"name": "tags", "type": "array"},
            {"name": "due_date", "type": "string"},
            {"name": "completed", "type": "boolean"},
            {"name": "completed_at", "type": "string"},
        ], [])

    register("tasks", "Task / to-do list", build_tasks)

    # Finance (104db: Account, Transaction)
    def build_finance(**kwargs):
        return bejson_core_create_104db(
            ["Account", "Transaction"],
            [
                {"name": "Record_Type_Parent", "type": "string"},
                {"name": "account_id", "type": "string", "Record_Type_Parent": "Account"},
                {"name": "account_name", "type": "string", "Record_Type_Parent": "Account"},
                {"name": "account_type", "type": "string", "Record_Type_Parent": "Account"},
                {"name": "account_balance", "type": "number", "Record_Type_Parent": "Account"},
                {"name": "account_currency", "type": "string", "Record_Type_Parent": "Account"},
                {"name": "transaction_id", "type": "string", "Record_Type_Parent": "Transaction"},
                {"name": "transaction_amount", "type": "number", "Record_Type_Parent": "Transaction"},
                {"name": "transaction_category", "type": "string", "Record_Type_Parent": "Transaction"},
                {"name": "transaction_description", "type": "string", "Record_Type_Parent": "Transaction"},
                {"name": "transaction_date", "type": "string", "Record_Type_Parent": "Transaction"},
                {"name": "account_id_fk", "type": "string", "Record_Type_Parent": "Transaction"},
                {"name": "transaction_recurring", "type": "boolean", "Record_Type_Parent": "Transaction"},
            ],
            []
        )

    register("finance", "Finance tracker (104db: Account, Transaction)", build_finance)

    # Wiki / Knowledge Base (104)
    def build_wiki(**kwargs):
        return bejson_core_create_104("Article", [
            {"name": "article_id", "type": "string"},
            {"name": "title", "type": "string"},
            {"name": "category", "type": "string"},
            {"name": "tags", "type": "array"},
            {"name": "content", "type": "string"},
            {"name": "author", "type": "string"},
            {"name": "created_at", "type": "string"},
            {"name": "updated_at", "type": "string"},
            {"name": "is_published", "type": "boolean"},
        ], [])

    register("wiki", "Wiki / knowledge base", build_wiki)

    # CRM (104db: Contact, Company, Deal)
    def build_crm(**kwargs):
        return bejson_core_create_104db(
            ["Contact", "Company", "Deal"],
            [
                {"name": "Record_Type_Parent", "type": "string"},
                {"name": "contact_id", "type": "string", "Record_Type_Parent": "Contact"},
                {"name": "contact_first_name", "type": "string", "Record_Type_Parent": "Contact"},
                {"name": "contact_last_name", "type": "string", "Record_Type_Parent": "Contact"},
                {"name": "contact_email", "type": "string", "Record_Type_Parent": "Contact"},
                {"name": "contact_phone", "type": "string", "Record_Type_Parent": "Contact"},
                {"name": "contact_company_fk", "type": "string", "Record_Type_Parent": "Contact"},
                {"name": "company_id", "type": "string", "Record_Type_Parent": "Company"},
                {"name": "company_name", "type": "string", "Record_Type_Parent": "Company"},
                {"name": "company_industry", "type": "string", "Record_Type_Parent": "Company"},
                {"name": "company_website", "type": "string", "Record_Type_Parent": "Company"},
                {"name": "deal_id", "type": "string", "Record_Type_Parent": "Deal"},
                {"name": "deal_name", "type": "string", "Record_Type_Parent": "Deal"},
                {"name": "deal_value", "type": "number", "Record_Type_Parent": "Deal"},
                {"name": "deal_stage", "type": "string", "Record_Type_Parent": "Deal"},
                {"name": "deal_contact_fk", "type": "string", "Record_Type_Parent": "Deal"},
                {"name": "deal_company_fk", "type": "string", "Record_Type_Parent": "Deal"},
                {"name": "deal_won", "type": "boolean", "Record_Type_Parent": "Deal"},
            ],
            []
        )

    register("crm", "CRM system (104db: Contact, Company, Deal)", build_crm)

    # Simple key-value store (104a)
    def build_kv(**kwargs):
        return bejson_core_create_104a("ConfigEntry", [
            {"name": "key", "type": "string"},
            {"name": "value", "type": "string"},
            {"name": "type", "type": "string"},
            {"name": "is_secret", "type": "boolean"},
            {"name": "updated_at", "type": "string"},
        ], [],
        Database_Name="ConfigStore",
        Schema_Version="v1.0"
        )

    register("kv", "Key-value config store (104a)", build_kv)

    # Note-taking (104)
    def build_notes(**kwargs):
        return bejson_core_create_104("Note", [
            {"name": "note_id", "type": "string"},
            {"name": "title", "type": "string"},
            {"name": "content", "type": "string"},
            {"name": "tags", "type": "array"},
            {"name": "pinned", "type": "boolean"},
            {"name": "created_at", "type": "string"},
            {"name": "updated_at", "type": "string"},
        ], [])

    register("notes", "Note-taking app", build_notes)

    # Event log / audit trail (104)
    def build_events(**kwargs):
        return bejson_core_create_104("Event", [
            {"name": "event_id", "type": "string"},
            {"name": "timestamp", "type": "string"},
            {"name": "level", "type": "string"},
            {"name": "source", "type": "string"},
            {"name": "message", "type": "string"},
            {"name": "details", "type": "object"},
        ], [])

    register("events", "Event / audit log", build_events)


# ─── Main ─────────────────────────────────────────────────────────────────

def main():
    register_all()

    ap = argparse.ArgumentParser(description="BEJSON Template Generator")
    ap.add_argument("template", nargs="?", help="Template name (use 'list' to see all)")
    ap.add_argument("-o", "--output", help="Output file path")
    args = ap.parse_args()

    if not args.template or args.template == "list":
        print(f"\n{C.BOLD}{C.BLUE}Available BEJSON Templates:{C.RESET}\n")
        max_name = max(len(n) for n in TEMPLATES)
        for name, info in sorted(TEMPLATES.items()):
            print(f"  {C.GREEN}{name:<{max_name}}{C.RESET}  {info['desc']}")
        print(f"\n{C.YELLOW}Usage: python3 bejson_template_gen.py <template_name> -o output.bejson.json{C.RESET}\n")
        return 0

    if args.template not in TEMPLATES:
        print(f"{C.RED}✗ Unknown template: {args.template}{C.RESET}")
        print(f"{C.YELLOW}Run 'list' to see available templates{C.RESET}")
        return 1

    doc = TEMPLATES[args.template]["build"]()
    output = args.output or f"{args.template}.bejson.json"
    bejson_core_atomic_write(output, doc)
    print(f"{C.GREEN}✓ Template '{args.template}' → {output}{C.RESET}")
    stats = {
        "version": doc["Format_Version"],
        "fields": len(doc["Fields"]),
        "records": len(doc["Values"]),
        "types": ", ".join(doc["Records_Type"]),
    }
    print(f"  Version: {stats['version']} | Fields: {stats['fields']} | Types: {stats['types']}")
    print(f"\n{C.YELLOW}Add records with: python3 bejson_cli.py add {output} '[\"val1\", \"val2\", ...]'{C.RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
