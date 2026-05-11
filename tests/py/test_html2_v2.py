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

def test_v2_components():
    print("Generating V2 Components test...")
    
    # 1. Drawer
    drawer = body.html_drawer("config_drawer", "System Configuration", "<p>Settings and filters go here.</p>")
    drawer_btn = '<button onclick="openDrawer(\'config_drawer\')" class="subtabs__btn">OPEN CONFIG DRAWER</button>'
    
    # 2. Property List
    props = [
        {"key": "OS", "value": "Core-Command Linux"},
        {"key": "Kernel", "value": "5.15.0-v8"},
        {"key": "Uptime", "value": "12 days, 4 hours"},
        {"key": "Status", "value": "READY"}
    ]
    prop_list = body.html_property_list(props)
    
    # 3. Gauges
    gauges = body.html_gauge("CPU LOAD", 42)
    gauges += body.html_gauge("MEMORY", 78, variant="warning")
    gauges += body.html_gauge("DISK SPACE", 15, variant="success")
    
    # 4. Carousel
    carousel_items = [
        "<h3>Slide 1</h3><p>Information about Entity A</p>",
        "<h3>Slide 2</h3><p>Information about Entity B</p>",
        "<h3>Slide 3</h3><p>Information about Entity C</p>"
    ]
    carousel = widgets.html_carousel(carousel_items)
    
    # 5. Code Block
    code = """def hello_world():
    print("Hello from Core-Command!")
    return True"""
    code_block = widgets.html_code_block(code, title="Python Sample")
    
    # Assemble Content
    content = f"""
    <h1>V2 Components Test</h1>
    {drawer_btn}
    {drawer}
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 30px;">
        <div>
            <h2>Property List</h2>
            {prop_list}
        </div>
        <div>
            <h2>System Gauges</h2>
            {gauges}
        </div>
    </div>
    
    <div style="margin-top: 40px;">
        <h2>Content Carousel</h2>
        {carousel}
    </div>
    
    <div style="margin-top: 40px;">
        <h2>Code Inspector</h2>
        {code_block}
    </div>
    """
    
    nav = [{"category": "V2 Components", "items": [{"label": "V2 Components", "url": "test_v2.html"}]}]
    html = page.html_page("V2 Components Test", content, nav_links=nav, active_url="test_v2.html")
    page.html_save(html, os.path.join(OUTPUT_DIR, "test_v2.html"))

if __name__ == "__main__":
    test_v2_components()
    print(f"\nAll V2 tests generated in: {OUTPUT_DIR}/test_v2.html")
