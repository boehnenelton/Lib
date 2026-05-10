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
from lib_bejson_html2_skeletons import THEMES

OUTPUT_DIR = "/storage/emulated/0/dev/lib/tests/output/html2/themes"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def test_themes():
    print("Generating Theme tests...")
    
    main_content = """
    <h1>Theme Showcase</h1>
    <p>This page demonstrates the 104db Multi-Theme Engine.</p>
    <div style='display:grid; grid-template-columns: 1fr 1fr; gap: 20px;'>
        <div>
            <h2>Components</h2>
            <div class='badge' style='margin-bottom:10px;'>VERSION 4.2</div>
            <p>UI components automatically inherit theme colors.</p>
        </div>
        <div>
            <h2>Health</h2>
            <div class='gauge-container'>
                <div class='gauge__track'><div class='gauge__bar' style='width:75%; background:var(--primary-red);'></div></div>
            </div>
        </div>
    </div>
    """
    
    # Sidebar Widget
    sw = widgets.html_widget("<p>Theme specific status.</p>", title="CORE_STATE", size="small")
    
    for theme_name in THEMES.keys():
        print(f"  [+] {theme_name}")
        html = page.html_page(
            f"Theme: {theme_name}",
            main_content,
            nav_links=[{"category": "Themes", "items": [{"label": t, "url": f"test_{t}.html"} for t in THEMES.keys()]}],
            active_url=f"test_{theme_name}.html",
            sidebar_widgets=sw,
            theme=theme_name
        )
        page.html_save(html, os.path.join(OUTPUT_DIR, f"test_{theme_name}.html"))

if __name__ == "__main__":
    test_themes()
    print(f"\nTheme tests generated in: {OUTPUT_DIR}")
