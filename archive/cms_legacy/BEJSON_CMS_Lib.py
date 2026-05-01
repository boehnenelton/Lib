"""
Library:     BEJSON_CMS_Lib.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: str = "", entry_file: str = "index.html", app_image: str = "") -> Optional[str]:
        if not os.path.exists(source_path): return None
        new_uuid = str(uuid.uuid4())
        slug = re.sub(r'[^a-z0-9]', '-', name.lower()).strip('-')
        
        apps_storage = os.path.join(os.path.dirname(self.master_db), "standalone_apps")
        target_dir = os.path.join(apps_storage, new_uuid)
        os.makedirs(target_dir, exist_ok=True)
        
        if os.path.isdir(source_path):
            for item in os.listdir(source_path):
                s = os.path.join(source_path, item)
                d = os.path.join(target_dir, item)
                if os.path.isdir(s): shutil.copytree(s, d, dirs_exist_ok=True)
                else: shutil.copy2(s, d)
        elif source_path.endswith(".zip"):
            with zipfile.ZipFile(source_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
        else: # Single file import (e.g. .html)
            shutil.copy2(source_path, os.path.join(target_dir, entry_file))

        if not self._load(): return None
        success = StdLib.bejson_add_record_db("StandaloneApp", {
            "app_uuid": new_uuid, 
            "app_name": name, 
            "app_slug": slug, 
            "app_desc": description, 
            "entry_file": entry_file, 
            "app_image": app_image,
            "created_at": datetime.now().strftime("%Y-%m-%d")
        })
        self._save(); self._unload()
        return new_uuid if success else None

    def delete_standalone_app(self, app_uuid: str) -> bool:
        if not self._load(): return False
        idx_p = StdLib._get_field_index("Record_Type_Parent")
        idx_uuid = StdLib._get_field_index("app_uuid")
        idx_slug = StdLib._get_field_index("app_slug")
        
        data = StdLib._current_data
        slug_to_delete = None
        for row in data["Values"]:
            if row[idx_p] == "StandaloneApp" and row[idx_uuid] == app_uuid:
                slug_to_delete = row[idx_slug]
                break
        
        data["Values"] = [row for row in data["Values"] if not (row[idx_p] == "StandaloneApp" and row[idx_uuid] == app_uuid)]
        success = self._save(); self._unload()
        
        if success and slug_to_delete:
            apps_storage = os.path.join(os.path.dirname(self.master_db), "standalone_apps")
            target_dir = os.path.join(apps_storage, slug_to_delete)
            if os.path.exists(target_dir): shutil.rmtree(target_dir)
            
        return success
--------------------------------------------------------------------------
CONFIGURATION & LINKS
--------------------------------------------------------------------------

    def get_config(self, key: str) -> Optional[str]:
        if not self._load(): return None
        from BEJSON_Extended_Lib import bejson_filter_db_records
        configs = bejson_filter_db_records("SiteConfig"); self._unload()
        for c in configs:
            if c.get('config_key') == key: return c.get('config_value')
        return None

    def set_config(self, key: str, value: str) -> bool:
        if not self._load(): return False
        idx_p = StdLib._get_field_index("Record_Type_Parent"); idx_k = StdLib._get_field_index("config_key")
        data = StdLib._current_data
        data["Values"] = [row for row in data["Values"] if not (row[idx_p] == "SiteConfig" and row[idx_k] == key)]
        success = StdLib.bejson_add_record_db("SiteConfig", {"config_key": key, "config_value": value})
        self._unload(); return success

    def add_nav_link(self, label: str, url: str) -> bool:
        if not self._load(): return False
        success = StdLib.bejson_add_record_db("NavLink", {"nav_label": label, "nav_url": url})
        self._unload(); return success

    def add_social_link(self, platform: str, url: str) -> bool:
        if not self._load(): return False
        success = StdLib.bejson_add_record_db("SocialLink", {"social_platform": platform, "social_url": url})
        self._unload(); return success
--------------------------------------------------------------------------
ASSETS, SEARCH & QUERY
--------------------------------------------------------------------------

    def list_assets(self) -> List[str]:
        asset_dir = os.path.join(os.path.dirname(self.master_db), "assets")
        if not os.path.exists(asset_dir): return []
        return sorted([f for f in os.listdir(asset_dir) if os.path.isfile(os.path.join(asset_dir, f))])

    def delete_asset(self, filename: str) -> bool:
        asset_path = os.path.join(os.path.dirname(self.master_db), "assets", filename)
        if os.path.exists(asset_path): os.remove(asset_path); return True
        return False

    def save_asset(self, src_path: str, filename: str = None) -> Optional[str]:
        if not os.path.exists(src_path): return None
        asset_dir = os.path.join(os.path.dirname(self.master_db), "assets")
        os.makedirs(asset_dir, exist_ok=True)
        fname = re.sub(r'[^A-Za-z0-9\._-]', '_', filename or os.path.basename(src_path))
        shutil.copy2(src_path, os.path.join(asset_dir, fname))
        return fname

    def query_entities(self, entity_type: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if not self._load(): return []
        from BEJSON_Extended_Lib import bejson_filter_db_records
        results = bejson_filter_db_records(entity_type); self._unload()
        if not filters: return results
        return [res for res in results if all(res.get(k) == v for k, v in filters.items())]

    def get_latest_pages(self, limit: int = 5) -> List[Dict[str, Any]]:
        return self.list_pages(sort_by_date=True)[:limit]

    def get_related_pages(self, page_uuid: str, limit: int = 3) -> List[Dict[str, Any]]:
        pages = self.list_pages()
        curr = next((p for p in pages if p['page_uuid'] == page_uuid), None)
        if not curr: return []
        return [p for p in pages if p.get('category_ref') == curr.get('category_ref') and p['page_uuid'] != page_uuid][:limit]
--------------------------------------------------------------------------
IMPORT & EXPORT
--------------------------------------------------------------------------

    def import_html_file(self, html_path: str, category: str = "Uncategorized", author: str = "") -> Optional[str]:
        if not os.path.exists(html_path): return None
        with open(html_path, 'rb') as f: raw = f.read()
        title, body, _ = self.extract_from_html(raw)
        pid = self.create_page(title, category=category, author=author)
        if pid: self.save_page_content(pid, html=body)
        return pid

    def extract_from_html(self, html_bytes: bytes):
        if not _BS4_OK:
            raw = html_bytes.decode('utf-8', errors='replace')
            title = re.search(r'<title[^>]*>(.*?)</title>', raw, re.I | re.S)
            return title.group(1).strip() if title else 'Imported', f'<p>{raw[:50000]}</p>', raw[:200]
        soup = BeautifulSoup(html_bytes, 'html.parser')
        title = (soup.find('title') or soup.find('h1') or type('T',(),{'get_text':lambda s,**k:'Imported'})()).get_text(strip=True)
        body = soup.find('body') or soup
        for t in body.find_all(['script', 'style', 'noscript', 'link', 'meta']): t.decompose()
        body = self._strip_word_html(body)
        return title, body.decode_contents().strip(), re.sub(r'\s+', ' ', body.get_text(separator=' ', strip=True))[:200]

    def _strip_word_html(self, soup):
        for t in soup.find_all('o:p'): t.decompose()
        for t in soup.find_all(True):
            if any('Mso' in c for c in t.get('class', [])): t.unwrap()
        for t in soup.find_all(True, style=True):
            style = t.get('style', '')
            if 'mso-' in style:
                cleaned = '; '.join(p for p in style.split(';') if 'mso-' not in p.lower()).strip().strip(';')
                if cleaned: t['style'] = cleaned
                else: del t['style']
        for t in soup.find_all(['footer', 'div', 'p', 'span']):
            text = t.get_text(strip=True)
            if text and len(text) < 200 and re.search(r'(microsoft\s+word|generated\s+by|created\s+with|renderer:|claude\s+ai|gemini\s+ai|openai|chatgpt|copilot)', text, re.I):
                if not t.find(['h1', 'h2', 'h3', 'ul', 'ol', 'table']): t.decompose()
        return soup

    def export_site_zip(self) -> Optional[str]:
        www = os.path.join(self.cms_dir, "Processing", "BEJSON_WEB_BUILDER", "www")
        out = os.path.join(self.cms_dir, "Exports", f"site_build_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        if not os.path.exists(www): return None
        return shutil.make_archive(out, 'zip', www) + ".zip"

    def export_data_zip(self) -> Optional[str]:
        data = os.path.dirname(self.master_db)
        out = os.path.join(self.cms_dir, "Exports", f"cms_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        return shutil.make_archive(out, 'zip', data) + ".zip"

    def sync_to_external_storage(self, target_path: str = "/storage/emulated/0/www"):
        """Copies the entire built site to an external storage path (e.g. for Pydroid/External access)."""
        www_dir = os.path.join(self.cms_dir, "Processing", "BEJSON_WEB_BUILDER", "www")
        if not os.path.exists(www_dir):
            print("[CMSLib] Sync Failed: Build directory not found.")
            return False
            
        try:
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            shutil.copytree(www_dir, target_path)
            print(f"[CMSLib] Sync Successful: {target_path}")
            return True
        except Exception as e:
            print(f"[CMSLib] Sync Error: {e}")
            return False

    def factory_reset(self, confirm: bool = False) -> bool:
        if not confirm: return False
        for p in [os.path.dirname(self.master_db), os.path.join(self.cms_dir, "Processing", "BEJSON_WEB_BUILDER", "www"), os.path.join(self.cms_dir, "Exports")]:
            if os.path.exists(p): shutil.rmtree(p)
        for d in ["assets", "pages_db", "standalone_apps"]: os.makedirs(os.path.join(os.path.dirname(self.master_db), d), exist_ok=True)
        os.makedirs(os.path.join(self.cms_dir, "Exports"), exist_ok=True)
        return self.sync_schema()
--------------------------------------------------------------------------
SCAFFOLDING
--------------------------------------------------------------------------

    def scaffold_video_gallery(self, title: str, videos: List[Dict[str, str]], intro: str = "", category: str = "Uncategorized") -> Optional[str]:
        items = ""
        for v in videos:
            vid = re.search(r'(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})', v.get("url", ""))
            if not vid: continue
            items += f'<div class="bej-video-item"><div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:4px;"><iframe src="https://www.youtube.com/embed/{vid.group(1)}" frameborder="0" allowfullscreen style="position:absolute;top:0;left:0;width:100%;height:100%;"></iframe></div><h3 style="margin-top:14px;font-size:1.05rem;">{v.get("label", "Video")}</h3></div>'
        pid = self.create_page(title, category=category)
        if pid: self.save_page_content(pid, html=f"<p>{intro}</p><div style='display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:32px;margin:30px 0;'>{items}</div>")
        return pid

    def scaffold_github_project(self, title: str, repo_url: str, features: List[str], desc: str = "", category: str = "Uncategorized") -> Optional[str]:
        repo_name = repo_url.rstrip("/").split("/")[-1]
        feat_html = "".join([f'<li style="padding:8px 0;border-bottom:1px solid #eee;"><span style="color:#DE2626;">→</span> {f}</li>' for f in features])
        html = f"<p>{desc}</p><div style='background:#f8f8f8;border:1px solid #e5e5e5;padding:24px;margin:24px 0;'><div style='font-size:1.4rem;font-weight:900;'>{repo_name}</div><a href='{repo_url}' style='display:inline-block;margin-top:10px;padding:8px 16px;background:#24292e;color:#fff;border-radius:4px;'>🐙 View on GitHub</a></div><h2>Features</h2><ul style='list-style:none;padding:0;'>{feat_html}</ul>"
        pid = self.create_page(title, category=category)
        if pid: self.save_page_content(pid, html=html)
        return pid

    def generate_multi_file_code_block(self, files: Dict[str, str]) -> str:
        tabs = ""; content = ""
        for i, (name, code) in enumerate(files.items()):
            active = "active" if i == 0 else ""; display = "block" if i == 0 else "none"
            safe_code = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            tabs += f'<button class="bej-tab-btn {active}" onclick="bejOpenTab(event, \'tab-{i}\')">{name}</button>'
            content += f'<div id="tab-{i}" class="bej-tab-content" style="display:{display};"><pre class="code-box" style="background:var(--code-bg);color:var(--code-text);padding:20px;margin:0;overflow:auto;max-height:700px;font-family:\'Source Code Pro\',monospace;font-size:13px;line-height:1.5;white-space:pre-wrap;word-wrap:break-word;word-break:break-all;"><code>{safe_code}</code></pre></div>'
        
        return f"""
        <div class="bej-multi-file-viewer">
            <div class="bej-tabs">{tabs}</div>
            {content}
        </div>
        <script>
        function bejOpenTab(e, t) {{
            var i, c, b;
            var viewer = e.currentTarget.closest('.bej-multi-file-viewer');
            c = viewer.getElementsByClassName('bej-tab-content');
            for (i = 0; i < c.length; i++) c[i].style.display = 'none';
            b = viewer.getElementsByClassName('bej-tab-btn');
            for (i = 0; i < b.length; i++) b[i].className = b[i].className.replace(' active', '');
            document.getElementById(t).style.display = 'block';
            e.currentTarget.className += ' active';
        }}
        </script>
        <style>
        .bej-multi-file-viewer {{ background: var(--bg-card); border-radius: 8px; overflow: hidden; margin: 30px 0; border: 1px solid var(--border-color); box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
        .bej-tabs {{ background: var(--border-color); display: flex; overflow-x: auto; border-bottom: 1px solid var(--border-color); }}
        .bej-tab-btn {{ background: var(--border-color); color: var(--text-muted); border: none; padding: 14px 22px; cursor: pointer; font-family: inherit; font-size: 13px; font-weight: 600; transition: 0.2s; white-space: nowrap; border-right: 1px solid var(--bg-body); }}
        .bej-tab-btn:hover {{ background: var(--bg-body); color: var(--text-main); }}
        .bej-tab-btn.active {{ background: var(--accent-color); color: #fff; }}
        .bej-tab-content {{ padding: 0; }}
        .code-box::-webkit-scrollbar {{ width: 10px; height: 10px; }}
        .code-box::-webkit-scrollbar-track {{ background: var(--code-bg); }}
        .code-box::-webkit-scrollbar-thumb {{ background: var(--text-muted); border-radius: 5px; border: 2px solid var(--code-bg); }}
        .code-box::-webkit-scrollbar-thumb:hover {{ background: var(--accent-color); }}
        </style>
        """

    def scaffold_code_project(self, title: str, files: Dict[str, str], description: str = "", category: str = "Uncategorized") -> Optional[str]:
        pid = self.create_page(title, category=category)
        if pid: self.save_page_content(pid, html=f"<p>{description}</p>{self.generate_multi_file_code_block(files)}")
        return pid
"""
import os
import json
import uuid
import re
import subprocess
import signal
import time
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional

# ------------------------------------------------------------------------------
# DEPENDENCY: BEJSON Standard Library (Core IO)
# ------------------------------------------------------------------------------
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    import BEJSON_Standard_Lib as StdLib
except ImportError:
    try:
        import BEJSON_Standard_Lib as StdLib
    except ImportError:
        print("[CMSLib] CRITICAL: 'BEJSON_Standard_Lib.py' not found.")
        StdLib = None

try:
    from bs4 import BeautifulSoup
    _BS4_OK = True
except ImportError:
    _BS4_OK = False

# ==============================================================================
# CMS DATABASE MANAGER
# ==============================================================================

class CMSDatabase:
    def __init__(self, master_db_path: str):
        self.master_db = master_db_path
        self.cms_dir = os.path.dirname(os.path.dirname(os.path.dirname(master_db_path)))
        self.pages_db_dir = os.path.join(os.path.dirname(master_db_path), "pages_db")
        if not os.path.exists(self.pages_db_dir):
            os.makedirs(self.pages_db_dir, exist_ok=True)
            
        self.pids = {"cms": None, "publisher": None, "editor": None}

    def _load(self):
        if not StdLib: return False
        return StdLib.bejson_load(self.master_db)

    def _save(self):
        if not StdLib: return False
        return StdLib.bejson_save()

    def _unload(self):
        if not StdLib: return
        StdLib.bejson_unload()

    # --------------------------------------------------------------------------
    # SERVER MANAGEMENT
    # --------------------------------------------------------------------------

    def start_server(self, service: str = "cms"):
        scripts = {"cms": "Flask_CMS.py", "publisher": "Flask_CMS_Publisher.py", "editor": "Flask_Page_Editor.py"}
        if service not in scripts: return False
        script_path = os.path.join(self.cms_dir, scripts[service])
        if not os.path.exists(script_path): return False
        proc = subprocess.Popen([sys.executable, script_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setpgrp)
        self.pids[service] = proc.pid
        return True

    def stop_server(self, service: str = "cms"):
        if service not in self.pids or not self.pids[service]: return self._kill_by_name(service)
        try:
            os.killpg(os.getpgid(self.pids[service]), signal.SIGTERM)
            self.pids[service] = None
            return True
        except: return False

    def _kill_by_name(self, service: str):
        scripts = {"cms": "Flask_CMS.py", "publisher": "Flask_CMS_Publisher.py", "editor": "Flask_Page_Editor.py"}
        os.system(f"pkill -f {scripts[service]}")
        return True

    # --------------------------------------------------------------------------
    # BUILD & PUBLISH
    # --------------------------------------------------------------------------

    def build_and_publish(self, stylesheet: str = "light.css"):
        sys.path.append(self.cms_dir)
        try:
            import Flask_CMS_Publisher as Publisher
            Publisher._state["output_dir"] = os.path.join(self.cms_dir, "Processing", "BEJSON_WEB_BUILDER", "www")
            Publisher._state["stylesheet"] = stylesheet
            Publisher._execute()
            return True
        except Exception as e:
            print(f"[CMSLib] Build Failed: {e}")
            return False

    # --------------------------------------------------------------------------
    # SCHEMA SYNCHRONIZATION
    # --------------------------------------------------------------------------

    def sync_schema(self):
        expected_types = ["SiteConfig", "Category", "PageRecord", "NavLink", "SocialLink", "AuthorProfile", "AdUnit", "StandaloneApp", "PageTemplate"]
        if not os.path.exists(self.master_db): StdLib.bejson_create_104db(self.master_db, expected_types)
        if not self._load(): return False
        data = StdLib._current_data
        for t in expected_types:
            if t not in data["Records_Type"]: data["Records_Type"].append(t)
        fields = [
            ("config_key", "string", "SiteConfig"), ("config_value", "string", "SiteConfig"),
            ("category_name", "string", "Category"), ("category_slug", "string", "Category"),
            ("page_uuid", "string", "PageRecord"), ("page_title", "string", "PageRecord"),
            ("page_slug", "string", "PageRecord"), ("category_ref", "string", "PageRecord"),
            ("item_type", "string", "PageRecord"), ("external_url", "string", "PageRecord"),
            ("created_at", "string", "PageRecord"), ("author_ref", "string", "PageRecord"),
            ("featured_img", "string", "PageRecord"), ("nav_label", "string", "NavLink"),
            ("nav_url", "string", "NavLink"), ("social_platform", "string", "SocialLink"),
            ("social_url", "string", "SocialLink"), ("auth_name", "string", "AuthorProfile"),
            ("auth_bio", "string", "AuthorProfile"), ("auth_img", "string", "AuthorProfile"),
            ("ad_uuid", "string", "AdUnit"), ("ad_name", "string", "AdUnit"),
            ("ad_image", "string", "AdUnit"), ("ad_link", "string", "AdUnit"),
            ("ad_zone", "string", "AdUnit"), ("ad_active", "boolean", "AdUnit"),
            ("app_uuid", "string", "StandaloneApp"), ("app_name", "string", "StandaloneApp"),
            ("app_slug", "string", "StandaloneApp"), ("app_desc", "string", "StandaloneApp"),
            ("entry_file", "string", "StandaloneApp"), ("app_image", "string", "StandaloneApp"),
            ("created_at", "string", "StandaloneApp"),
            ("tpl_key", "string", "PageTemplate"), ("tpl_label", "string", "PageTemplate"),
            ("tpl_icon", "string", "PageTemplate"), ("tpl_desc", "string", "PageTemplate"),
            ("tpl_body", "string", "PageTemplate")
        ]
        for name, ftype, parent in fields: StdLib.bejson_add_field(name, ftype, db_parent=parent)
        self._save()
        self._unload()
        return True

    # --------------------------------------------------------------------------
    # CATEGORY OPERATIONS
    # --------------------------------------------------------------------------
    
    def list_categories(self) -> List[Dict[str, Any]]:
        if not self._load(): return []
        from BEJSON_Extended_Lib import bejson_filter_db_records
        results = bejson_filter_db_records("Category")
        self._unload()
        return results

    def create_category(self, name: str) -> bool:
        if not name: return False
        slug = re.sub(r'[^a-z0-9]', '-', name.lower()).strip('-')
        if not self._load(): return False
        from BEJSON_Extended_Lib import bejson_filter_db_records
        if any(c.get('category_name') == name for c in bejson_filter_db_records("Category")):
            self._unload(); return False
        success = StdLib.bejson_add_record_db("Category", {"category_name": name, "category_slug": slug})
        self._unload(); return success

    def delete_category(self, name: str, fallback_category: str = "Uncategorized") -> bool:
        if name == fallback_category: return False
        if not self._load(): return False
        idx_p = StdLib._get_field_index("Record_Type_Parent")
        idx_name = StdLib._get_field_index("category_name")
        data = StdLib._current_data
        data["Values"] = [row for row in data["Values"] if not (row[idx_p] == "Category" and row[idx_name] == name)]
        idx_cat_ref = StdLib._get_field_index("category_ref")
        for row in data["Values"]:
            if row[idx_p] == "PageRecord" and row[idx_cat_ref] == name: row[idx_cat_ref] = fallback_category
        success = self._save()
        self._unload(); return success

    # --------------------------------------------------------------------------
    # TEMPLATE OPERATIONS
    # --------------------------------------------------------------------------

    def list_templates(self) -> List[Dict[str, Any]]:
        if not self._load(): return []
        from BEJSON_Extended_Lib import bejson_filter_db_records
        results = bejson_filter_db_records("PageTemplate")
        self._unload()
        return results

    def create_template(self, key: str, label: str, icon: str, desc: str, body: str) -> bool:
        if not key or not label: return False
        if not self._load(): return False
        from BEJSON_Extended_Lib import bejson_filter_db_records
        if any(t.get('tpl_key') == key for t in bejson_filter_db_records("PageTemplate")):
            self._unload(); return False
        success = StdLib.bejson_add_record_db("PageTemplate", {
            "tpl_key": key, "tpl_label": label, "tpl_icon": icon, "tpl_desc": desc, "tpl_body": body
        })
        self._unload(); return success

    # --------------------------------------------------------------------------
    # PAGE OPERATIONS
    # --------------------------------------------------------------------------

    def list_pages(self, sort_by_date: bool = True) -> List[Dict[str, Any]]:
        if not self._load(): return []
        from BEJSON_Extended_Lib import bejson_filter_db_records
        pages = bejson_filter_db_records("PageRecord")
        self._unload()
        if sort_by_date: pages.sort(key=lambda p: p.get('created_at', ''), reverse=True)
        return pages

    def get_page_content(self, page_uuid: str) -> Dict[str, str]:
        pfile = os.path.join(self.pages_db_dir, f"{page_uuid}.json")
        result = {"html": "", "markdown": "", "source": "", "meta_title": "", "meta_description": "", "meta_author": "", "meta_image": ""}
        if not os.path.exists(pfile) or not StdLib.bejson_load(pfile): return result
        from BEJSON_Extended_Lib import bejson_filter_db_records
        content_recs = bejson_filter_db_records("Content")
        meta_recs = bejson_filter_db_records("PageMeta")
        StdLib.bejson_unload()
        if content_recs:
            c = content_recs[0]
            result["html"] = c.get("html_body", ""); result["markdown"] = c.get("markdown_body", ""); result["source"] = c.get("source_code", "")
        if meta_recs:
            m = meta_recs[0]
            result["meta_title"] = m.get("meta_title", ""); result["meta_description"] = m.get("meta_description", ""); result["meta_author"] = m.get("meta_author", ""); result["meta_image"] = m.get("meta_image", "")
        return result

    def save_page_content(self, page_uuid: str, **kwargs) -> bool:
        pfile = os.path.join(self.pages_db_dir, f"{page_uuid}.json")
        if not os.path.exists(pfile) or not StdLib.bejson_load(pfile): return False
        idx_p = StdLib._get_field_index("Record_Type_Parent")
        for row in StdLib._current_data["Values"]:
            if row[idx_p] == "Content":
                for key in ["html", "markdown", "source"]:
                    if key in kwargs and kwargs[key] is not None:
                        field = "html_body" if key == "html" else f"{key}_body" if key == "markdown" else "source_code"
                        fidx = StdLib._get_field_index(field)
                        if fidx != -1: row[fidx] = kwargs[key]
            elif row[idx_p] == "PageMeta":
                for key in ["meta_title", "meta_description", "meta_author", "meta_image"]:
                    if key in kwargs and kwargs[key] is not None:
                        fidx = StdLib._get_field_index(key)
                        if fidx != -1: row[fidx] = kwargs[key]
        success = StdLib.bejson_save()
        StdLib.bejson_unload(); return success

    def create_page(self, title: str, category: str = "Uncategorized", author: str = "", featured_img: str = "") -> Optional[str]:
        if not title: return None
        if not self._load(): return None
        
        from BEJSON_Extended_Lib import bejson_filter_db_records
        existing_pages = bejson_filter_db_records("PageRecord")
        existing_page = next((p for p in existing_pages if p.get('page_title') == title), None)
        
        if existing_page:
            new_uuid = existing_page['page_uuid']
            # Preserve existing image if the new one is empty
            if not featured_img and existing_page.get('featured_img'):
                featured_img = existing_page['featured_img']
            
            # Update existing record
            idx_p = StdLib._get_field_index("Record_Type_Parent")
            idx_uuid = StdLib._get_field_index("page_uuid")
            idx_title = StdLib._get_field_index("page_title")
            idx_cat = StdLib._get_field_index("category_ref")
            idx_auth = StdLib._get_field_index("author_ref")
            idx_feat = StdLib._get_field_index("featured_img")
            
            for row in StdLib._current_data["Values"]:
                if row[idx_p] == "PageRecord" and row[idx_uuid] == new_uuid:
                    if idx_title != -1: row[idx_title] = title
                    if idx_cat != -1: row[idx_cat] = category
                    if idx_auth != -1: row[idx_auth] = author
                    if idx_feat != -1 and featured_img: row[idx_feat] = featured_img
                    break
            success = StdLib.bejson_save()
        else:
            new_uuid = str(uuid.uuid4())
            slug = re.sub(r'[^a-z0-9]', '-', title.lower()).strip('-')
            success = StdLib.bejson_add_record_db("PageRecord", {
                "page_uuid": new_uuid, 
                "page_title": title, 
                "page_slug": slug, 
                "category_ref": category, 
                "item_type": "page", 
                "created_at": datetime.now().strftime("%Y-%m-%d"), 
                "author_ref": author, 
                "featured_img": featured_img
            })
            
        self._unload()
        if not success: return None
        
        pfile = os.path.join(self.pages_db_dir, f"{new_uuid}.json")
        is_update = os.path.exists(pfile)
        
        if not is_update:
            StdLib.bejson_create_104db(pfile, ["PageMeta", "Content"])
            StdLib.bejson_load(pfile)
            for f in [("meta_title", "string", "PageMeta"), ("meta_description", "string", "PageMeta"), ("meta_author", "string", "PageMeta"), ("meta_image", "string", "PageMeta"), ("html_body", "string", "Content"), ("markdown_body", "string", "Content"), ("source_code", "string", "Content")]:
                StdLib.bejson_add_field(f[0], f[1], db_parent=f[2])
            StdLib.bejson_add_record_db("PageMeta", {"meta_title": title, "meta_author": author, "meta_image": featured_img})
            StdLib.bejson_add_record_db("Content", {"html_body": f"<h2>{title}</h2><p>Start writing...</p>", "markdown_body": "", "source_code": ""})
            StdLib.bejson_save()
            StdLib.bejson_unload()
        else:
            # Update existing meta if it's an update
            self.save_page_content(new_uuid, meta_title=title, meta_author=author, meta_image=featured_img)
            
        return new_uuid

    def delete_page(self, page_uuid: str) -> bool:
        if not self._load(): return False
        idx_p = StdLib._get_field_index("Record_Type_Parent"); idx_uuid = StdLib._get_field_index("page_uuid")
        data = StdLib._current_data
        data["Values"] = [row for row in data["Values"] if not (row[idx_p] == "PageRecord" and row[idx_uuid] == page_uuid)]
        success = self._save(); self._unload()
        if success:
            pfile = os.path.join(self.pages_db_dir, f"{page_uuid}.json")
            if os.path.exists(pfile): os.remove(pfile)
        return success

    # --------------------------------------------------------------------------
    # STANDALONE APP OPERATIONS
    # --------------------------------------------------------------------------

    def list_standalone_apps(self) -> List[Dict[str, Any]]:
        if not self._load(): return []
        from BEJSON_Extended_Lib import bejson_filter_db_records
        results = bejson_filter_db_records("StandaloneApp")
        self._unload()
        return results

    def import_standalone_app(self, name: str, source_path: str, description: str = "", entry_file: str = "index.html", app_image: str = "") -> Optional[str]:
        if not os.path.exists(source_path): return None
        new_uuid = str(uuid.uuid4())
        slug = re.sub(r'[^a-z0-9]', '-', name.lower()).strip('-')
        
        apps_storage = os.path.join(os.path.dirname(self.master_db), "standalone_apps")
        target_dir = os.path.join(apps_storage, new_uuid)
        os.makedirs(target_dir, exist_ok=True)
        
        if os.path.isdir(source_path):
            for item in os.listdir(source_path):
                s = os.path.join(source_path, item)
                d = os.path.join(target_dir, item)
                if os.path.isdir(s): shutil.copytree(s, d, dirs_exist_ok=True)
                else: shutil.copy2(s, d)
        elif source_path.endswith(".zip"):
            with zipfile.ZipFile(source_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
        else: # Single file import (e.g. .html)
            shutil.copy2(source_path, os.path.join(target_dir, entry_file))

        if not self._load(): return None
        success = StdLib.bejson_add_record_db("StandaloneApp", {
            "app_uuid": new_uuid, 
            "app_name": name, 
            "app_slug": slug, 
            "app_desc": description, 
            "entry_file": entry_file, 
            "app_image": app_image,
            "created_at": datetime.now().strftime("%Y-%m-%d")
        })
        self._save(); self._unload()
        return new_uuid if success else None

    def delete_standalone_app(self, app_uuid: str) -> bool:
        if not self._load(): return False
        idx_p = StdLib._get_field_index("Record_Type_Parent")
        idx_uuid = StdLib._get_field_index("app_uuid")
        idx_slug = StdLib._get_field_index("app_slug")
        
        data = StdLib._current_data
        slug_to_delete = None
        for row in data["Values"]:
            if row[idx_p] == "StandaloneApp" and row[idx_uuid] == app_uuid:
                slug_to_delete = row[idx_slug]
                break
        
        data["Values"] = [row for row in data["Values"] if not (row[idx_p] == "StandaloneApp" and row[idx_uuid] == app_uuid)]
        success = self._save(); self._unload()
        
        if success and slug_to_delete:
            apps_storage = os.path.join(os.path.dirname(self.master_db), "standalone_apps")
            target_dir = os.path.join(apps_storage, slug_to_delete)
            if os.path.exists(target_dir): shutil.rmtree(target_dir)
            
        return success

    # --------------------------------------------------------------------------
    # CONFIGURATION & LINKS
    # --------------------------------------------------------------------------

    def get_config(self, key: str) -> Optional[str]:
        if not self._load(): return None
        from BEJSON_Extended_Lib import bejson_filter_db_records
        configs = bejson_filter_db_records("SiteConfig"); self._unload()
        for c in configs:
            if c.get('config_key') == key: return c.get('config_value')
        return None

    def set_config(self, key: str, value: str) -> bool:
        if not self._load(): return False
        idx_p = StdLib._get_field_index("Record_Type_Parent"); idx_k = StdLib._get_field_index("config_key")
        data = StdLib._current_data
        data["Values"] = [row for row in data["Values"] if not (row[idx_p] == "SiteConfig" and row[idx_k] == key)]
        success = StdLib.bejson_add_record_db("SiteConfig", {"config_key": key, "config_value": value})
        self._unload(); return success

    def add_nav_link(self, label: str, url: str) -> bool:
        if not self._load(): return False
        success = StdLib.bejson_add_record_db("NavLink", {"nav_label": label, "nav_url": url})
        self._unload(); return success

    def add_social_link(self, platform: str, url: str) -> bool:
        if not self._load(): return False
        success = StdLib.bejson_add_record_db("SocialLink", {"social_platform": platform, "social_url": url})
        self._unload(); return success

    # --------------------------------------------------------------------------
    # ASSETS, SEARCH & QUERY
    # --------------------------------------------------------------------------

    def list_assets(self) -> List[str]:
        asset_dir = os.path.join(os.path.dirname(self.master_db), "assets")
        if not os.path.exists(asset_dir): return []
        return sorted([f for f in os.listdir(asset_dir) if os.path.isfile(os.path.join(asset_dir, f))])

    def delete_asset(self, filename: str) -> bool:
        asset_path = os.path.join(os.path.dirname(self.master_db), "assets", filename)
        if os.path.exists(asset_path): os.remove(asset_path); return True
        return False

    def save_asset(self, src_path: str, filename: str = None) -> Optional[str]:
        if not os.path.exists(src_path): return None
        asset_dir = os.path.join(os.path.dirname(self.master_db), "assets")
        os.makedirs(asset_dir, exist_ok=True)
        fname = re.sub(r'[^A-Za-z0-9\._-]', '_', filename or os.path.basename(src_path))
        shutil.copy2(src_path, os.path.join(asset_dir, fname))
        return fname

    def query_entities(self, entity_type: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if not self._load(): return []
        from BEJSON_Extended_Lib import bejson_filter_db_records
        results = bejson_filter_db_records(entity_type); self._unload()
        if not filters: return results
        return [res for res in results if all(res.get(k) == v for k, v in filters.items())]

    def get_latest_pages(self, limit: int = 5) -> List[Dict[str, Any]]:
        return self.list_pages(sort_by_date=True)[:limit]

    def get_related_pages(self, page_uuid: str, limit: int = 3) -> List[Dict[str, Any]]:
        pages = self.list_pages()
        curr = next((p for p in pages if p['page_uuid'] == page_uuid), None)
        if not curr: return []
        return [p for p in pages if p.get('category_ref') == curr.get('category_ref') and p['page_uuid'] != page_uuid][:limit]

    # --------------------------------------------------------------------------
    # IMPORT & EXPORT
    # --------------------------------------------------------------------------

    def import_html_file(self, html_path: str, category: str = "Uncategorized", author: str = "") -> Optional[str]:
        if not os.path.exists(html_path): return None
        with open(html_path, 'rb') as f: raw = f.read()
        title, body, _ = self.extract_from_html(raw)
        pid = self.create_page(title, category=category, author=author)
        if pid: self.save_page_content(pid, html=body)
        return pid

    def extract_from_html(self, html_bytes: bytes):
        if not _BS4_OK:
            raw = html_bytes.decode('utf-8', errors='replace')
            title = re.search(r'<title[^>]*>(.*?)</title>', raw, re.I | re.S)
            return title.group(1).strip() if title else 'Imported', f'<p>{raw[:50000]}</p>', raw[:200]
        soup = BeautifulSoup(html_bytes, 'html.parser')
        title = (soup.find('title') or soup.find('h1') or type('T',(),{'get_text':lambda s,**k:'Imported'})()).get_text(strip=True)
        body = soup.find('body') or soup
        for t in body.find_all(['script', 'style', 'noscript', 'link', 'meta']): t.decompose()
        body = self._strip_word_html(body)
        return title, body.decode_contents().strip(), re.sub(r'\s+', ' ', body.get_text(separator=' ', strip=True))[:200]

    def _strip_word_html(self, soup):
        for t in soup.find_all('o:p'): t.decompose()
        for t in soup.find_all(True):
            if any('Mso' in c for c in t.get('class', [])): t.unwrap()
        for t in soup.find_all(True, style=True):
            style = t.get('style', '')
            if 'mso-' in style:
                cleaned = '; '.join(p for p in style.split(';') if 'mso-' not in p.lower()).strip().strip(';')
                if cleaned: t['style'] = cleaned
                else: del t['style']
        for t in soup.find_all(['footer', 'div', 'p', 'span']):
            text = t.get_text(strip=True)
            if text and len(text) < 200 and re.search(r'(microsoft\s+word|generated\s+by|created\s+with|renderer:|claude\s+ai|gemini\s+ai|openai|chatgpt|copilot)', text, re.I):
                if not t.find(['h1', 'h2', 'h3', 'ul', 'ol', 'table']): t.decompose()
        return soup

    def export_site_zip(self) -> Optional[str]:
        www = os.path.join(self.cms_dir, "Processing", "BEJSON_WEB_BUILDER", "www")
        out = os.path.join(self.cms_dir, "Exports", f"site_build_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        if not os.path.exists(www): return None
        return shutil.make_archive(out, 'zip', www) + ".zip"

    def export_data_zip(self) -> Optional[str]:
        data = os.path.dirname(self.master_db)
        out = os.path.join(self.cms_dir, "Exports", f"cms_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        return shutil.make_archive(out, 'zip', data) + ".zip"

    def sync_to_external_storage(self, target_path: str = "/storage/emulated/0/www"):
        """Copies the entire built site to an external storage path (e.g. for Pydroid/External access)."""
        www_dir = os.path.join(self.cms_dir, "Processing", "BEJSON_WEB_BUILDER", "www")
        if not os.path.exists(www_dir):
            print("[CMSLib] Sync Failed: Build directory not found.")
            return False
            
        try:
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            shutil.copytree(www_dir, target_path)
            print(f"[CMSLib] Sync Successful: {target_path}")
            return True
        except Exception as e:
            print(f"[CMSLib] Sync Error: {e}")
            return False

    def factory_reset(self, confirm: bool = False) -> bool:
        if not confirm: return False
        for p in [os.path.dirname(self.master_db), os.path.join(self.cms_dir, "Processing", "BEJSON_WEB_BUILDER", "www"), os.path.join(self.cms_dir, "Exports")]:
            if os.path.exists(p): shutil.rmtree(p)
        for d in ["assets", "pages_db", "standalone_apps"]: os.makedirs(os.path.join(os.path.dirname(self.master_db), d), exist_ok=True)
        os.makedirs(os.path.join(self.cms_dir, "Exports"), exist_ok=True)
        return self.sync_schema()

    # --------------------------------------------------------------------------
    # SCAFFOLDING
    # --------------------------------------------------------------------------

    def scaffold_video_gallery(self, title: str, videos: List[Dict[str, str]], intro: str = "", category: str = "Uncategorized") -> Optional[str]:
        items = ""
        for v in videos:
            vid = re.search(r'(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})', v.get("url", ""))
            if not vid: continue
            items += f'<div class="bej-video-item"><div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:4px;"><iframe src="https://www.youtube.com/embed/{vid.group(1)}" frameborder="0" allowfullscreen style="position:absolute;top:0;left:0;width:100%;height:100%;"></iframe></div><h3 style="margin-top:14px;font-size:1.05rem;">{v.get("label", "Video")}</h3></div>'
        pid = self.create_page(title, category=category)
        if pid: self.save_page_content(pid, html=f"<p>{intro}</p><div style='display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:32px;margin:30px 0;'>{items}</div>")
        return pid

    def scaffold_github_project(self, title: str, repo_url: str, features: List[str], desc: str = "", category: str = "Uncategorized") -> Optional[str]:
        repo_name = repo_url.rstrip("/").split("/")[-1]
        feat_html = "".join([f'<li style="padding:8px 0;border-bottom:1px solid #eee;"><span style="color:#DE2626;">→</span> {f}</li>' for f in features])
        html = f"<p>{desc}</p><div style='background:#f8f8f8;border:1px solid #e5e5e5;padding:24px;margin:24px 0;'><div style='font-size:1.4rem;font-weight:900;'>{repo_name}</div><a href='{repo_url}' style='display:inline-block;margin-top:10px;padding:8px 16px;background:#24292e;color:#fff;border-radius:4px;'>🐙 View on GitHub</a></div><h2>Features</h2><ul style='list-style:none;padding:0;'>{feat_html}</ul>"
        pid = self.create_page(title, category=category)
        if pid: self.save_page_content(pid, html=html)
        return pid

    def generate_multi_file_code_block(self, files: Dict[str, str]) -> str:
        tabs = ""; content = ""
        for i, (name, code) in enumerate(files.items()):
            active = "active" if i == 0 else ""; display = "block" if i == 0 else "none"
            safe_code = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            tabs += f'<button class="bej-tab-btn {active}" onclick="bejOpenTab(event, \'tab-{i}\')">{name}</button>'
            content += f'<div id="tab-{i}" class="bej-tab-content" style="display:{display};"><pre class="code-box" style="background:var(--code-bg);color:var(--code-text);padding:20px;margin:0;overflow:auto;max-height:700px;font-family:\'Source Code Pro\',monospace;font-size:13px;line-height:1.5;white-space:pre-wrap;word-wrap:break-word;word-break:break-all;"><code>{safe_code}</code></pre></div>'
        
        return f"""
        <div class="bej-multi-file-viewer">
            <div class="bej-tabs">{tabs}</div>
            {content}
        </div>
        <script>
        function bejOpenTab(e, t) {{
            var i, c, b;
            var viewer = e.currentTarget.closest('.bej-multi-file-viewer');
            c = viewer.getElementsByClassName('bej-tab-content');
            for (i = 0; i < c.length; i++) c[i].style.display = 'none';
            b = viewer.getElementsByClassName('bej-tab-btn');
            for (i = 0; i < b.length; i++) b[i].className = b[i].className.replace(' active', '');
            document.getElementById(t).style.display = 'block';
            e.currentTarget.className += ' active';
        }}
        </script>
        <style>
        .bej-multi-file-viewer {{ background: var(--bg-card); border-radius: 8px; overflow: hidden; margin: 30px 0; border: 1px solid var(--border-color); box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
        .bej-tabs {{ background: var(--border-color); display: flex; overflow-x: auto; border-bottom: 1px solid var(--border-color); }}
        .bej-tab-btn {{ background: var(--border-color); color: var(--text-muted); border: none; padding: 14px 22px; cursor: pointer; font-family: inherit; font-size: 13px; font-weight: 600; transition: 0.2s; white-space: nowrap; border-right: 1px solid var(--bg-body); }}
        .bej-tab-btn:hover {{ background: var(--bg-body); color: var(--text-main); }}
        .bej-tab-btn.active {{ background: var(--accent-color); color: #fff; }}
        .bej-tab-content {{ padding: 0; }}
        .code-box::-webkit-scrollbar {{ width: 10px; height: 10px; }}
        .code-box::-webkit-scrollbar-track {{ background: var(--code-bg); }}
        .code-box::-webkit-scrollbar-thumb {{ background: var(--text-muted); border-radius: 5px; border: 2px solid var(--code-bg); }}
        .code-box::-webkit-scrollbar-thumb:hover {{ background: var(--accent-color); }}
        </style>
        """

    def scaffold_code_project(self, title: str, files: Dict[str, str], description: str = "", category: str = "Uncategorized") -> Optional[str]:
        pid = self.create_page(title, category=category)
        if pid: self.save_page_content(pid, html=f"<p>{description}</p>{self.generate_multi_file_code_block(files)}")
        return pid
