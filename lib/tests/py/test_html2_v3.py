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

def test_v3_components():
    print("Generating V3 Components test...")
    
    # 1. Dialog (Modal)
    dialog_content = "<p>This is a critical system warning. Please confirm your action.</p>"
    dialog_actions = '<button onclick="closeDialog(\'test_dialog\')" class="form__button form__button--outline">CANCEL</button>'
    dialog_actions += '<button onclick="alert(\'Action Confirmed\');closeDialog(\'test_dialog\')" class="form__button">CONFIRM</button>'
    dialog = widgets.html_dialog("test_dialog", "Security Alert", dialog_content, actions_html=dialog_actions)
    dialog_btn = '<button onclick="openDialog(\'test_dialog\')" class="form__button">TRIGGER DIALOG</button>'
    
    # 2. Action List
    actions = [
        {"label": "Reboot Server", "action_label": "RUN", "onclick": "alert('Rebooting...')"},
        {"label": "Clear Cache", "action_label": "WIPE", "onclick": "alert('Wiping...')"},
        {"label": "Update Libs", "action_label": "SYNC", "onclick": "alert('Syncing...')"}
    ]
    action_list = body.html_action_list(actions)
    
    # 3. Description List
    descriptions = [
        {"term": "Runtime", "description": "Python 3.13.0"},
        {"term": "Database", "description": "BEJSON 104db (Local)"},
        {"term": "Security", "description": "Level 4 - Enforced"}
    ]
    desc_list = body.html_description_list(descriptions)
    
    # 4. Status Panel
    panel_content = "<p>All encryption modules are loaded and verified.</p>"
    status_panel = body.html_status_panel("Encryption Core", panel_content, status="ONLINE")
    
    # Assemble Content
    content = f"""
    <h1>V3 Components Test</h1>
    <div style="margin-bottom: 30px;">
        {dialog_btn}
        {dialog}
    </div>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
        <div>
            <h2>Status Panel</h2>
            {status_panel}
        </div>
        <div>
            <h2>Action List</h2>
            {action_list}
        </div>
    </div>
    
    <div style="margin-top: 40px; padding: 20px; background: #fafafa; border: 1px solid #eee;">
        <h2>Description List</h2>
        {desc_list}
    </div>
    """
    
    nav = [{"category": "V3 Components", "items": [{"label": "V3 Components", "url": "test_v3.html"}]}]
    html = page.html_page("V3 Components Test", content, nav_links=nav, active_url="test_v3.html")
    page.html_save(html, os.path.join(OUTPUT_DIR, "test_v3.html"))

if __name__ == "__main__":
    test_v3_components()
    print(f"\nAll V3 tests generated in: {OUTPUT_DIR}/test_v3.html")
