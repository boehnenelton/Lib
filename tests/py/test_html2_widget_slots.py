import sys
import os
from pathlib import Path

# Add lib/py to path
LIB_PY = "/storage/emulated/0/dev/lib/py"
if LIB_PY not in sys.path:
    sys.path.append(LIB_PY)

import lib_html2_page_templates as page
import lib_html2_widgets as widgets
import lib_html2_body as body

OUTPUT_DIR = "/storage/emulated/0/dev/lib/tests/output/html2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def test_widget_slots():
    print("Generating Widget Slots test...")
    
    # 1. Create a Sidebar Widget (Small)
    sidebar_content = body.html_badge("System OK", variant="success")
    sidebar_content += "<p style='font-size:12px;margin-top:10px;'>All core services are operating within normal parameters.</p>"
    sw = widgets.html_widget(sidebar_content, title="STATUS", size="small")
    
    # 2. Create Content Widgets (Medium & Large)
    # Medium: System Stats
    stats_content = body.html_gauge("CPU", 12)
    stats_content += body.html_gauge("MEM", 45)
    stats_content += body.html_gauge("NET", 8)
    mw = widgets.html_widget(stats_content, title="RESOURCE MONITOR", size="medium")
    
    # Large: Activity Log
    log_content = body.html_property_list([
        {"key": "09:00", "value": "User Admin logged in"},
        {"key": "09:15", "value": "Backup completed"},
        {"key": "09:30", "value": "System scan started"}
    ])
    lw = widgets.html_widget(log_content, title="GLOBAL ACTIVITY LOG", size="large")
    
    # Assemble Bottom Widgets
    bottom_ws = mw + lw
    
    # Main Content
    main_content = "<h1>Standardized Widget System</h1><p>This page demonstrates the new 104db Widget Standard with fixed dimensions and dedicated slots.</p>"
    
    nav = [{"category": "Widget Tests", "items": [{"label": "Widget Slots", "url": "test_slots.html"}]}]
    
    html = page.html_page(
        "Widget Slots Test", 
        main_content, 
        nav_links=nav, 
        active_url="test_slots.html",
        sidebar_widgets=sw,
        bottom_widgets=bottom_ws
    )
    
    page.html_save(html, os.path.join(OUTPUT_DIR, "test_slots.html"))

if __name__ == "__main__":
    test_widget_slots()
    print(f"\nWidget standards test generated in: {OUTPUT_DIR}/test_slots.html")
