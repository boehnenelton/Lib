"""
Library:     lib_bejson_html2.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Unified Entry Point for Core-Command HTML Generation.
             Unified Dashboard Architecture v4.0.
"""

import sys
import os

# Ensure local directory is in path
LIB_DIR = os.path.dirname(os.path.abspath(__file__))
if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)

# Core Imports
from lib_html2_page_templates import html_page, html_dashboard
from lib_html2_tables import html_table
from lib_html2_body import html_stats_bar, html_card, html_card_grid, html_badge, html_subtabs, html_tab_content

def bejson_html_generate_full(title, doc, nav_links=None):
    """Generates a complete dashboard from a BEJSON document."""
    return html_dashboard(title, doc, nav_links=nav_links)

def bejson_html_save(content, path):
    """Saves HTML content to file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("lib_bejson_html2 v3.0.0 — Unified Dashboard Architecture Active.")
