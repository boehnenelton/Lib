"""
Library:     lib_bejson_html_wiki.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Static Wiki Builder for BEJSON & Markdown Backends.
             Supports category-based sidebars, tag extraction, and cross-linking.
"""
import os
import json
import re
import html as html_mod
from datetime import datetime

# Import html2 components
try:
    from lib_html2_page_templates import html_page, html_table
    from lib_html2_widgets import html_info_box
except ImportError:
    import sys
    sys.path.append("/storage/7B30-0E0B/Core-Command/Lib/py")
    from lib_html2_page_templates import html_page, html_table
    from lib_html2_widgets import html_info_box

class BEJSONWiki:
    def __init__(self, title="System Wiki", output_dir=None, header_widget="", footer_widget=""):
        self.title = title
        self.output_dir = output_dir or "/storage/7B30-0E0B/Core-Command/Logistics/Reports/Wiki"
        self.header_widget = header_widget
        self.footer_widget = footer_widget
        os.makedirs(self.output_dir, exist_ok=True)
        self.pages = [] # List of {name, url, category, tags}

    def _extract_tags(self, first_line):
        """Extracts #tags from the first line of a file."""
        if not first_line: return []
        return re.findall(r'#(\w+)', first_line)

    def _simple_md_to_html(self, text):
        """Basic MD converter for headers, lists and code."""
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

    def add_page_from_data(self, fields, values, page_name, category="General", title_field_idx=0, desc_field_idx=1):
        """Builds a wiki page directly from provided data fields and values."""
        content = '<div class="wiki-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem;">'
        for row in values:
            content += f"""
            <div class="wiki-card" style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 4px; border-left: 3px solid #DE2626;">
                <h4 style="margin: 0; color: #DE2626;">{html_mod.escape(str(row[title_field_idx]))}</h4>
                <p style="font-size: 0.85rem; color: #aaa;">{html_mod.escape(str(row[desc_field_idx]))}</p>
            </div>"""
        content += '</div>'
        content += f'<h3 style="margin-top: 2rem;">Data Table</h3>{html_table(values, fields, dark=True)}'
        
        url = f"{page_name.lower().replace(' ', '_').replace('.', '_')}.html"
        self.pages.append({"name": page_name, "url": url, "category": category, "tags": ["DATA", category.upper()], "content": content})

    def add_page_from_bejson(self, db_path, page_name, category="General", title_field_idx=0, desc_field_idx=1):
        if not os.path.exists(db_path): return
        with open(db_path, 'r') as f: data = json.load(f)
        
        headers = [f['name'] for f in data['Fields']]
        rows = data['Values']
        
        content = '<div class="wiki-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem;">'
        for row in rows:
            content += f"""
            <div class="wiki-card" style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 4px; border-left: 3px solid #DE2626;">
                <h4 style="margin: 0; color: #DE2626;">{html_mod.escape(str(row[title_field_idx]))}</h4>
                <p style="font-size: 0.85rem; color: #aaa;">{html_mod.escape(str(row[desc_field_idx]))}</p>
            </div>"""
        content += '</div>'
        content += f'<h3 style="margin-top: 2rem;">Data Source</h3>{html_table(rows, headers, dark=True)}'
        
        url = f"{page_name.lower().replace(' ', '_')}.html"
        self.pages.append({"name": page_name, "url": url, "category": category, "tags": ["BEJSON", category.upper()], "content": content})

    def add_page_from_md(self, md_path, page_name, category="Reports"):
        if not os.path.exists(md_path): return
        with open(md_path, 'r') as f: lines = f.readlines()
        
        tags = self._extract_tags(lines[0]) if lines else []
        md_content = "".join(lines[1:]) if tags else "".join(lines)
        html_content = self._simple_md_to_html(md_content)
        
        url = f"{page_name.lower().replace(' ', '_')}.html"
        self.pages.append({"name": page_name, "url": url, "category": category, "tags": tags, "content": html_content})

    def render_all(self):
        """Builds all pages with a unified category-based sidebar."""
        # 1. Build Navigation Map
        nav = {}
        for p in self.pages:
            nav.setdefault(p['category'], []).append((p['name'], p['url']))
            
        # 2. Render each page
        for p in self.pages:
            tag_html = "".join([f'<span class="wiki-tag">{t}</span>' for t in p['tags']])
            sidebar_html = '<div class="wiki-sidebar"><h3>Contents</h3>'
            for cat, links in nav.items():
                sidebar_html += f'<div style="margin-bottom: 15px;"><strong style="font-size: 11px; text-transform: uppercase; color: #666;">{cat}</strong>'
                for name, url in links:
                    style = 'font-weight: bold; color: #DE2626;' if url == p['url'] else ''
                    sidebar_html += f'<a href="{url}" style="display: block; font-size: 13px; margin: 4px 0; {style}">{name}</a>'
                sidebar_html += '</div>'
            sidebar_html += '</div>'

            full_body = f"""
            <div class="wiki-container">
                {sidebar_html}
                <div class="wiki-content">
                    <div class="wiki-breadcrumbs"><a href="index.html">Wiki</a> / {p['category']} / {p['name']}</div>
                    <header class="page-header">
                        <h1>{html_mod.escape(p['name'])}</h1>
                        <div style="margin-bottom: 1rem;">{tag_html}</div>
                    </header>
                    {p['content']}
                </div>
            </div>
            """
            
            final_html = html_page(
                title=f"{self.title} | {p['name']}",
                body=full_body,
                dark=True,
                header_widget=self.header_widget,
                footer_widget=self.footer_widget,
                template_sections={"wiki": True, "code": True}
            )
            
            with open(os.path.join(self.output_dir, p['url']), 'w') as f: f.write(final_html)

        # 3. Build Index
        self._build_index(nav)

    def _build_index(self, nav):
        index_content = '<div class="card-grid">'
        for cat, links in nav.items():
            index_content += f"""
            <div class="card" style="grid-column: span 2;">
                <h2 style="margin-top: 0; color: #DE2626;">{cat}</h2>
                <div style="display: flex; flex-wrap: wrap; gap: 10px;">"""
            for name, url in links:
                index_content += f'<a href="{url}" style="background: rgba(255,255,255,0.05); padding: 8px 15px; border-radius: 4px; border: 1px solid #333;">{name}</a>'
            index_content += '</div></div>'
        index_content += '</div>'

        final_index = html_page(
            title=self.title,
            body=f'<header class="page-header"><h1>{self.title}</h1><p>System Knowledge Hub</p></header>{index_content}',
            dark=True,
            header_widget=self.header_widget,
            footer_widget=self.footer_widget,
            template_sections={"wiki": True}
        )
        with open(os.path.join(self.output_dir, "index.html"), 'w') as f: f.write(final_index)
        print(f"Wiki rendered with {len(self.pages)} pages.")
