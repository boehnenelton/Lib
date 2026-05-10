import sys
import os
from pathlib import Path

# Add lib/py to path
LIB_PY = "/storage/emulated/0/dev/lib/py"
if LIB_PY not in sys.path:
    sys.path.append(LIB_PY)

import lib_html2_page_templates as page
import lib_html2_tables as tables
import lib_html2_widgets as widgets
import lib_html2_body as body
import lib_bejson_core as core

import lib_html2_animations as anim

OUTPUT_DIR = "/storage/emulated/0/dev/lib/tests/output/html2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_nav(active_url):
    return [
        {
            "category": "Component Tests",
            "items": [
                {"label": "Tables", "url": "test_tables.html"},
                {"label": "Widgets", "url": "test_widgets.html"},
                {"label": "Body Components", "url": "test_body.html"},
                {"label": "Tabs & Content", "url": "test_tabs.html"},
                {"label": "Badges & Stats", "url": "test_stats.html"},
                {"label": "Animations", "url": "test_animations.html"},
                {"label": "Full Dashboard", "url": "test_dashboard.html"}
            ]
        }
    ]

# 1. Tables Page
def test_tables():
    print("Generating Tables test...")
    bejson_data = {
        "Format": "BEJSON",
        "Format_Version": "104db",
        "Schema_Name": "TestTable",
        "Records_Type": ["User", "Log"],
        "Fields": [
            {"name": "Record_Type_Parent", "type": "string"},
            {"name": "id", "type": "integer", "Record_Type_Parent": "User"},
            {"name": "username", "type": "string", "Record_Type_Parent": "User"},
            {"name": "active", "type": "boolean", "Record_Type_Parent": "User"},
            {"name": "timestamp", "type": "string", "Record_Type_Parent": "Log"},
            {"name": "message", "type": "string", "Record_Type_Parent": "Log"}
        ],
        "Values": [
            ["User", 1, "alice", True, None, None],
            ["User", 2, "bob", False, None, None],
            ["Log", None, None, None, "2026-04-29 09:00", "Login success"],
            ["Log", None, None, None, "2026-04-29 09:05", "Update profile"]
        ]
    }
    
    table_html = tables.html_table(bejson_data)
    content = f"<h1>Table Component Test</h1>{table_html}"
    html = page.html_page("Tables Test", content, nav_links=generate_nav("test_tables.html"), active_url="test_tables.html")
    page.html_save(html, os.path.join(OUTPUT_DIR, "test_tables.html"))

# 2. Widgets Page
def test_widgets():
    print("Generating Widgets test...")
    info_box = widgets.html_info_box("System Alert", "This is a test of the info box component.", link_url="#", link_label="Learn More")
    
    videos = [
        {"title": "Sample Video 1", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
        {"title": "Sample Video 2", "url": "https://www.youtube.com/watch?v=9bZkp7q19f0"}
    ]
    video_grid = widgets.html_video_grid(videos)
    
    content = f"<h1>Widget Components Test</h1>{info_box}<h2>Video Grid</h2>{video_grid}"
    html = page.html_page("Widgets Test", content, nav_links=generate_nav("test_widgets.html"), active_url="test_widgets.html")
    page.html_save(html, os.path.join(OUTPUT_DIR, "test_widgets.html"))

# 3. Body Components (Cards)
def test_body():
    print("Generating Body test...")
    cards = body.html_card("Card 1", "This is the body of card one.")
    cards += body.html_card("Card 2", "This is the body of card two.")
    card_grid = body.html_card_grid(cards)
    
    content = f"<h1>Body Components Test</h1><h2>Card Grid</h2>{card_grid}"
    html = page.html_page("Body Test", content, nav_links=generate_nav("test_body.html"), active_url="test_body.html")
    page.html_save(html, os.path.join(OUTPUT_DIR, "test_body.html"))

# 4. Tabs Page
def test_tabs():
    print("Generating Tabs test...")
    tabs = [
        {"label": "Tab A", "id": "tab_a", "active": True},
        {"label": "Tab B", "id": "tab_b", "active": False}
    ]
    tabs_nav = body.html_subtabs(tabs)
    content_a = body.html_tab_content("tab_a", "<p>Content for Tab A</p>", active=True)
    content_b = body.html_tab_content("tab_b", "<p>Content for Tab B</p>", active=False)
    
    content = f"<h1>Tabs Test</h1>{tabs_nav}{content_a}{content_b}"
    # Note: Switching tabs requires JS 'switchSubTab' usually in skeletons or body
    html = page.html_page("Tabs Test", content, nav_links=generate_nav("test_tabs.html"), active_url="test_tabs.html")
    page.html_save(html, os.path.join(OUTPUT_DIR, "test_tabs.html"))

# 5. Stats & Badges
def test_stats():
    print("Generating Stats test...")
    stats = [
        {"label": "Users", "value": "1,240"},
        {"label": "Uptime", "value": "99.9%"},
        {"label": "Errors", "value": "0"}
    ]
    stats_bar = body.html_stats_bar(stats)
    
    badges = body.html_badge("Success", variant="success") + " "
    badges += body.html_badge("Failed", variant="fail") + " "
    badges += body.html_badge("Neutral")
    
    content = f"<h1>Stats & Badges Test</h1><h2>Stats Bar</h2>{stats_bar}<h2>Badges</h2><p>{badges}</p>"
    html = page.html_page("Stats Test", content, nav_links=generate_nav("test_stats.html"), active_url="test_stats.html")
    page.html_save(html, os.path.join(OUTPUT_DIR, "test_stats.html"))

# 6. Animations
def test_animations():
    print("Generating Animations test...")
    terminal = anim.html_intro_terminal([
        "> INITIALIZING CORE_COMMAND...",
        "> LOADING LIB_HTML2...",
        "> READY."
    ])
    
    glitch = anim.html_glitch_reveal("SYSTEM_READY", subtitle="CORE EVO ALIGNMENT")
    
    content = f"<h1>Animations Test</h1>{terminal}<h2>Glitch Reveal</h2>{glitch}"
    html = page.html_page("Animations Test", content, nav_links=generate_nav("test_animations.html"), active_url="test_animations.html")
    page.html_save(html, os.path.join(OUTPUT_DIR, "test_animations.html"))

# 7. Full Dashboard
def test_dashboard():
    print("Generating Dashboard test...")
    bejson_data = {
        "Format": "BEJSON",
        "Format_Version": "104db",
        "Schema_Name": "DashboardData",
        "Records_Type": ["Status"],
        "Fields": [
            {"name": "Record_Type_Parent", "type": "string"},
            {"name": "Service", "type": "string", "Record_Type_Parent": "Status"},
            {"name": "State", "type": "string", "Record_Type_Parent": "Status"}
        ],
        "Values": [
            ["Status", "Auth", "ONLINE"],
            ["Status", "Database", "ONLINE"],
            ["Status", "API", "MAINTENANCE"]
        ]
    }
    
    html = page.html_dashboard("System Overview", bejson_data, nav_links=generate_nav("test_dashboard.html"))
    page.html_save(html, os.path.join(OUTPUT_DIR, "test_dashboard.html"))

if __name__ == "__main__":
    test_tables()
    test_widgets()
    test_body()
    test_tabs()
    test_stats()
    test_animations()
    test_dashboard()
    print(f"\nAll tests generated in: {OUTPUT_DIR}")
