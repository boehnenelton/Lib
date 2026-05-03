"""
Library:     lib_html2_page_templates.py
Family:      Core
Jurisdiction: ["PYTHON", "SWITCH_CORE"]
Status:      OFFICIAL — BEJSON-Core/Lib (v1.4)
Author:      Elton Boehnen
Version:     1.4 OFFICIAL
Date:        2026-05-03
Description: Full HTML Dashboard templates for BEJSON data.
"""
import html as html_mod
import os
import json
import re
from datetime import datetime

# Import skeletons
from lib_bejson_html2_skeletons import (
    COLOR, CSS_CORE, HTML_SKELETON
)

# ═══════════════════════════════════════════════════════
# 1. CORE PAGE GENERATION
# ═══════════════════════════════════════════════════════

def _is_active(url, active_url):
    """Strictly matches relative URLs for active highlighting."""
    if not active_url: return False
    # Normalize by removing leading ./ but preserving ../
    u = url.strip().rstrip("/")
    a = active_url.strip().rstrip("/")
    if u.startswith("./"): u = u[2:]
    if a.startswith("./"): a = a[2:]
    return u == a

def html_page(title, content, nav_links=None, status_extra="", active_url="", breadcrumbs_html=""): 
    """
    Generate a full Core-Command Dashboard page.
    :param title: Page Title
    :param content: Inner HTML content for the main area
    :param nav_links: List of {"category": "...", "items": [{"label": "...", "url": "..."}]}
    :param status_extra: Extra text for the status footer
    """
    
    # 1. CSS Injection
    css = CSS_CORE.format(**COLOR)
    
    # 2. Sidebar Tree-view Generation
    nav_html = ""
    if nav_links:
        any_active = False
        
        # Pre-check for active links to handle auto-expansion
        for cat in nav_links:
            for item in cat.get("items", []):
                if _is_active(item.get("url", "#"), active_url):
                    any_active = True
                    break
            if any_active: break

        for i, cat in enumerate(nav_links):
            cat_name = cat.get("category", "General")
            
            # Check if this category should be open
            is_active_cat = False
            for item in cat.get("items", []):
                if _is_active(item.get("url", "#"), active_url):
                    is_active_cat = True
                    break
            
            # Auto-open logic
            is_open = is_active_cat or (not any_active and i == 0)
            cat_open_class = " sidebar__category-items--open" if is_open else ""
            arrow = "▼" if is_open else "▶"

            nav_html += '<li>\n'
            nav_html += f'  <div class="sidebar__category">{html_mod.escape(cat_name)} <span class="cat-arrow">{arrow}</span></div>\n'
            nav_html += f'  <ul class="sidebar__category-items{cat_open_class}">\n'
            for item in cat.get("items", []):
                label = html_mod.escape(item.get("label", "Link"))
                url = item.get("url", "#")
                active_class = " sidebar__link--active" if _is_active(url, active_url) else ""
                nav_html += f'    <li><a href="{url}" class="sidebar__link{active_class}">> {label}</a></li>\n'
            nav_html += '  </ul>\n'
            nav_html += '</li>\n'
    else:
        nav_html = '<li><div class="sidebar__category">Navigation <span class="cat-arrow">▶</span></div>'
        nav_html += '<ul class="sidebar__category-items"><li><a href="#" class="sidebar__link">> No Links</a></li></ul></li>'

    # 3. Final Assembly
    return HTML_SKELETON.replace("{{title}}", html_mod.escape(title)) \
                       .replace("{{css}}", css) \
                       .replace("{{nav_items}}", nav_html) \
                       .replace("{{content}}", content).replace("{{breadcrumbs}}", breadcrumbs_html or "") \
                       .replace("{{status_extra}}", html_mod.escape(status_extra))

def html_dashboard(title, bejson_doc, nav_links=None):
    """
    Convenience function: Builds a dashboard around a BEJSON Table.
    """
    from lib_html2_tables import html_table
    table_content = html_table(bejson_doc)
    
    # Add a header for the content area
    content = f'<h1 style="margin-bottom:24px;">{html_mod.escape(title)}</h1>'
    content += table_content
    
    return html_page(title, content, nav_links=nav_links, status_extra=f"DATA: {bejson_doc.get('Format_Version', 'UNK')}")

def html_save(content, path):
    """Unified save function for generated HTML."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# ═══════════════════════════════════════════════════════
# 2. STATIC WIKI ENGINE
# ═══════════════════════════════════════════════════════

class BEJSONWiki:
    def __init__(self, title="System Wiki", output_dir=None, root_dir=None):
        self.title = title
        self.output_dir = output_dir # Where pages go (e.g. lib/DOCS_WIKI)
        self.root_dir = root_dir     # Where index goes (e.g. lib/)
        self.pages = [] # List of {name, url, category, tags, source_rel_path}

    def _extract_tags(self, first_line):
        if not first_line: return []
        return re.findall(r'#(\w+)', first_line)

    def _simple_md_to_html(self, text):
        lines = text.split('\n')
        html_lines = []
        in_code = False
        for line in lines:
            if line.strip().startswith('```'):
                if not in_code:
                    html_lines.append('<pre class="code-block"><code>')
                    in_code = True
                else:
                    html_lines.append('</code></pre>')
                    in_code = False
                continue
            if in_code:
                html_lines.append(html_mod.escape(line))
                continue
            if line.startswith('### '): html_lines.append(f'<h3>{line[4:]}</h3>')
            elif line.startswith('## '): html_lines.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('# '): html_lines.append(f'<h1>{line[2:]}</h1>')
            elif line.startswith('- '): html_lines.append(f'<li>{line[2:]}</li>')
            else:
                line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
                html_lines.append(f'<p>{line}</p>')
        return '\n'.join(html_lines)

    def render_all(self):
        # Build Navigation Tree (relative to WIKI root)
        nav_tree = {}
        for p in self.pages:
            cat = p.get('category', 'General')
            if cat not in nav_tree: nav_tree[cat] = []
            nav_tree[cat].append({
                "label": p['name'], 
                "url": f"../{cat}/{p['url']}"
            })
            
        nav_links = []
        nav_links.append({"category": "Home", "items": [{"label": "Hub Index", "url": "../../index.html"}]})
        for cat, items in nav_tree.items():
            nav_links.append({"category": cat, "items": items})
            
        for p in self.pages:
            cat = p.get('category', 'General')
            tag_html = "".join([f'<span class="badge" style="margin-right:5px;">{t}</span>' for t in p['tags']])
            
            action_bar = f"""
            <div style="margin: 20px 0; display: flex; gap: 10px;">
                <a href="../../{p['source_rel_path']}" class="form__button" download>DOWNLOAD SOURCE</a>
                <a href="../../{p['source_rel_path']}" class="form__button--outline" target="_blank">VIEW RAW</a>
            </div>
            """
            
            full_content = f'<div style="margin-bottom:20px;">{tag_html}</div>{action_bar}{p["content"]}'
            
            bc = f'<a href="../../index.html">HUB</a> <span class="breadcrumbs__separator">/</span> '
            bc += f'<a href="../index.html">WIKI</a> <span class="breadcrumbs__separator">/</span> '
            bc += f'<span class="breadcrumbs__current">{p["name"]}</span>'
            
            # For pages in wiki/Cat/page.html, current_url matches nav_tree url
            current_url = f"../{cat}/{p['url']}"
            final_html = html_page(
                title=f"{self.title} | {p['name']}",
                content=full_content,
                nav_links=nav_links,
                status_extra=f"WIKI | {cat}",
                active_url=current_url,
                breadcrumbs_html=bc
            )
            
            page_path = os.path.join(self.output_dir, cat, p['url'])
            html_save(final_html, page_path)

        self._build_index(nav_tree)

    def _build_index(self, nav_tree):
        # Master index in wiki/index.html (depth 1)
        index_nav = []
        index_nav.append({"category": "Home", "items": [{"label": "Hub Index", "url": "../index.html"}]})
        for cat, items in nav_tree.items():
            cat_items = []
            for item in items:
                # Items were relative to Cat subfolder, make relative to Wiki root
                cat_items.append({"label": item['label'], "url": f"{cat}/{os.path.basename(item['url'])}"})
            index_nav.append({"category": cat, "items": cat_items})

        content = f'<div class="page-header"><h1>{self.title}</h1><p>System Knowledge Hub</p></div>'
        content += '<div class="card-grid">'

        for cat, items in nav_tree.items():
            content += f'''
            <div class="card">
                <h2 style="color:var(--primary-red); border-bottom:1px solid var(--border); padding-bottom:8px; margin-bottom:15px;">{cat}</h2>
                <ul style="list-style:none;">'''
            for item in items:
                link = f"{cat}/{os.path.basename(item['url'])}"
                content += f'<li style="margin-bottom:8px;"><a href="{link}">> {item["label"]}</a></li>'
            content += '</ul></div>'
        content += '</div>'

        bc = f'<a href="../index.html">HUB</a> <span class="breadcrumbs__separator">/</span> <span class="breadcrumbs__current">WIKI</span>'
        final_index = html_page(
            title=self.title,
            content=content,
            nav_links=index_nav,
            status_extra="WIKI INDEX",
            active_url="index.html",
            breadcrumbs_html=bc
        )
        html_save(final_index, os.path.join(self.output_dir, "index.html"))
