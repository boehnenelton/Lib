"""
Library:     bejson_html_table.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Export BEJSON data as styled HTML tables and tabled log files.
             Supports dark theme, sortable columns, entity tabs (104db),
             and log-file style row-by-row tabled output.
"""
"""

import argparse
import html
import json
import os
import sys
from pathlib import Path
from datetime import datetime

LIB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
if LIB_DIR not in sys.path:
    sys.path.append(LIB_DIR)

from lib_bejson_core import (
    bejson_core_load_file,
    bejson_core_get_version,
    bejson_core_get_stats,
    bejson_core_get_records_by_type,
)


class C:
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"


# ─── HTML Templates ──────────────────────────────────────────────────────

CSS_DARK = """
:root {
    --bg: #ffffff;
    --surface: #ffffff;
    --border: #d0d0d0;
    --text: #000000;
    --text-muted: #555555;
    --accent: #1a73e8;
    --accent-hover: #1557b0;
    --row-hover: #f0f4ff;
    --header-bg: #ffffff;
    --header-text: #000000;
    --null-color: #999999;
    --true-color: #0d8a3e;
    --false-color: #d32f2f;
    --entity-tab-bg: #f0f0f0;
    --entity-tab-active: #1a73e8;
    --entity-tab-text: #333333;
    --entity-tab-active-text: #ffffff;
    --log-timestamp: #555555;
    --log-entity: #6a1b9a;
    --log-field: #1565c0;
    --log-value: #000000;
    --zebra-bg: #f8f9fa;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif;
    background: var(--bg);
    color: var(--text);
    padding: 20px;
    line-height: 1.5;
}
.header {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px 24px;
    margin-bottom: 16px;
}
.header h1 { font-size: 1.4em; margin-bottom: 4px; color: #000000; }
.header .meta { color: var(--text-muted); font-size: 0.9em; }
.stats { display: flex; gap: 24px; margin-top: 8px; }
.stats span { color: var(--accent); font-weight: 600; }
.entity-tabs {
    display: flex;
    gap: 4px;
    margin-bottom: 16px;
    border-bottom: 2px solid var(--border);
    padding-bottom: 0;
}
.entity-tab {
    padding: 8px 16px;
    background: var(--entity-tab-bg);
    border: 1px solid var(--border);
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    cursor: pointer;
    font-size: 0.9em;
    color: var(--entity-tab-text);
    user-select: none;
}
.entity-tab.active {
    background: var(--entity-tab-active);
    color: var(--entity-tab-active-text);
    border-color: var(--entity-tab-active);
}
.entity-tab:hover:not(.active) {
    background: #e0e0e0;
}
table {
    width: 100%;
    border-collapse: collapse;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    font-size: 0.88em;
}
thead th {
    background: var(--header-bg);
    color: var(--header-text);
    padding: 10px 12px;
    text-align: left;
    font-weight: 700;
    border-bottom: 2px solid var(--border);
    position: sticky;
    top: 0;
    cursor: pointer;
    user-select: none;
    white-space: nowrap;
}
thead th:hover { background: #e8e8e8; }
thead th::after { content: ' ⇅'; opacity: 0.4; }
tbody td {
    padding: 8px 12px;
    border-top: 1px solid var(--border);
    vertical-align: top;
    max-width: 300px;
    overflow: hidden;
    text-overflow: ellipsis;
}
tbody tr:hover { background: var(--row-hover); }
tbody tr:nth-child(even) { background: var(--zebra-bg); }
tbody tr:nth-child(even):hover { background: var(--row-hover); }
.null-val { color: var(--null-color); font-style: italic; }
.bool-true { color: var(--true-color); font-weight: 600; }
.bool-false { color: var(--false-color); font-weight: 600; }
.json-val {
    background: #f0f2f5;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'SF Mono', 'Fira Code', monospace;
    font-size: 0.85em;
    max-height: 80px;
    overflow: auto;
    white-space: pre;
}
.idx-col { color: var(--text-muted); text-align: center; width: 40px; }
.entity-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 0.8em;
    font-weight: 600;
    background: var(--entity-tab-active);
    color: white;
}
.entity-panel { display: none; }
.entity-panel.active { display: block; }
.search-bar {
    margin-bottom: 12px;
    padding: 8px 12px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text);
    width: 100%;
    font-size: 0.9em;
}
.search-bar::placeholder { color: var(--text-muted); }
.record-count { color: var(--text-muted); font-size: 0.85em; margin-bottom: 8px; }
"""

CSS_MINIMAL = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: monospace; padding: 20px; background: #fff; color: #000; }
table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
th, td { border: 1px solid #ccc; padding: 6px 10px; text-align: left; font-size: 0.85em; }
th { background: #f0f0f0; }
tr:nth-child(even) { background: #fafafa; }
.null-val { color: #999; font-style: italic; }
h1 { margin-bottom: 8px; }
.meta { color: #666; margin-bottom: 16px; }
"""

CSS_DARK_THEME = """
:root {
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --text-muted: #8b949e;
    --accent: #58a6ff;
    --accent-hover: #79c0ff;
    --row-hover: #1c2333;
    --header-bg: #1a2030;
    --header-text: #e6edf3;
    --null-color: #484f58;
    --true-color: #3fb950;
    --false-color: #f85149;
    --entity-tab-bg: #21262d;
    --entity-tab-active: #1f6feb;
    --entity-tab-text: #c9d1d9;
    --entity-tab-active-text: #ffffff;
    --zebra-bg: rgba(255,255,255,0.02);
}
body { background: var(--bg); color: var(--text); }
.header { background: var(--surface); border-color: var(--border); }
.header h1 { color: #ffffff; }
.stats span { color: var(--accent); }
.entity-tabs { border-bottom-color: var(--border); }
.entity-tab { background: var(--entity-tab-bg); border-color: var(--border); color: var(--entity-tab-text); }
.entity-tab.active { background: var(--entity-tab-active); color: var(--entity-tab-active-text); border-color: var(--entity-tab-active); }
.entity-tab:hover:not(.active) { background: #30363d; }
table { background: var(--surface); border-color: var(--border); }
thead th { background: var(--header-bg); color: var(--header-text); border-bottom-color: var(--border); }
thead th:hover { background: #242d3d; }
tbody td { border-top-color: var(--border); }
tbody tr:hover { background: var(--row-hover); }
tbody tr:nth-child(even) { background: var(--zebra-bg); }
tbody tr:nth-child(even):hover { background: var(--row-hover); }
.json-val { background: rgba(255,255,255,0.05); }
.entity-badge { background: var(--entity-tab-active); }
.search-bar { background: var(--surface); border-color: var(--border); color: var(--text); }
.search-bar::placeholder { color: var(--text-muted); }
.record-count { color: var(--text-muted); }
"""

CSS_LOG_DARK = """
:root {
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --text-muted: #8b949e;
    --accent: #58a6ff;
    --timestamp: #8b949e;
    --entity: #d2a8ff;
    --field: #79c0ff;
    --value: #a5d6ff;
    --separator: #21262d;
}
body { background: var(--bg); color: var(--text); }
.log-header { border-bottom-color: var(--border); }
.log-header h1 { color: #ffffff; }
.log-header .meta { color: var(--text-muted); }
.log-entry { border-bottom-color: var(--separator); }
.log-entry:hover { background: rgba(255,255,255,0.02); }
.log-ts { color: var(--timestamp); }
.log-entity { color: var(--entity); }
.log-idx { color: var(--text-muted); }
.log-field-row { border-left-color: var(--border); }
.log-field-name { color: var(--field); }
.log-field-sep { color: var(--text-muted); }
.log-field-val { color: var(--value); }
.log-field-val.null { color: var(--text-muted); }
.filter-bar input, .filter-bar select { background: var(--surface); border-color: var(--border); color: var(--text); }
"""

CSS_LOG = """
:root {
    --bg: #ffffff;
    --surface: #ffffff;
    --border: #d0d0d0;
    --text: #000000;
    --text-muted: #555555;
    --accent: #1a73e8;
    --timestamp: #555555;
    --entity: #6a1b9a;
    --field: #1565c0;
    --value: #000000;
    --separator: #e8e8e8;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
    background: var(--bg);
    color: var(--text);
    padding: 20px;
    font-size: 13px;
    line-height: 1.6;
}
.log-header {
    border-bottom: 1px solid var(--border);
    padding-bottom: 12px;
    margin-bottom: 16px;
}
.log-header h1 { font-size: 1.1em; font-weight: 600; color: #000000; }
.log-header .meta { color: var(--text-muted); font-size: 0.85em; }
.log-entry {
    padding: 8px 0;
    border-bottom: 1px solid var(--separator);
}
.log-entry:hover { background: #f5f7ff; }
.log-entry:last-child { border-bottom: none; }
.log-line {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}
.log-ts { color: var(--timestamp); min-width: 140px; }
.log-entity { color: var(--entity); font-weight: 600; min-width: 80px; }
.log-idx { color: var(--text-muted); min-width: 30px; }
.log-field-row {
    margin-left: 230px;
    padding-left: 12px;
    border-left: 2px solid var(--border);
}
.log-field {
    margin: 2px 0;
    display: flex;
    gap: 8px;
}
.log-field-name { color: var(--field); min-width: 140px; }
.log-field-sep { color: var(--text-muted); }
.log-field-val {
    color: var(--value);
    word-break: break-all;
}
.log-field-val.null { color: var(--text-muted); font-style: italic; }
.log-field-val.bool-true { color: #0d8a3e; }
.log-field-val.bool-false { color: #f85149; }
.filter-bar {
    margin-bottom: 12px;
    display: flex;
    gap: 8px;
}
.filter-bar input, .filter-bar select {
    padding: 6px 10px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    color: var(--text);
    font-family: inherit;
    font-size: 0.85em;
}
.filter-bar input { flex: 1; }
"""

HTML_WRAPPER = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
{body}
{js}
</body>
</html>
"""


# ─── Value formatting ────────────────────────────────────────────────────

def fmt_value(val, minimal=False):
    """Format a value for HTML display."""
    if val is None:
        return '<span class="null-val">null</span>'
    if isinstance(val, bool):
        cls = "bool-true" if val else "bool-false"
        return f'<span class="{cls}">{str(val).lower()}</span>'
    if isinstance(val, (list, dict)):
        s = json.dumps(val, indent=2 if not minimal else None)
        s = html.escape(s)
        return f'<span class="json-val">{s}</span>'
    s = html.escape(str(val))
    if len(s) > 200 and not minimal:
        s = f'<details><summary>{s[:100]}...</summary>{s}</details>'
    return s


# ─── Renderers ────────────────────────────────────────────────────────────

def render_table(doc, dark=True):
    """Render as standard sortable table with entity tabs for 104db."""
    version = bejson_core_get_version(doc)
    stats = bejson_core_get_stats(doc)
    fnames = [f["name"] for f in doc["Fields"]]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # CSS: base is always white (CSS_DARK), overlay dark theme if requested
    css = CSS_DARK
    if dark:
        css += "\n" + CSS_DARK_THEME
    else:
        css += "\n" + CSS_MINIMAL
    title = f"BEJSON {version} — {Path(doc.get('_source_file', 'database')).name}"

    header_html = f"""<div class="header">
  <h1>BEJSON {version} Database</h1>
  <div class="meta">Generated {now} · {stats['field_count']} fields · {stats['record_count']} records</div>
  <div class="stats">
    <div>Types: <span>{', '.join(stats['records_types'])}</span></div>
  </div>
</div>"""

    # For 104db: entity tabs
    body_parts = [header_html]

    if version == "104db":
        tabs_html = '<div class="entity-tabs">\n'
        for i, et in enumerate(stats["records_types"]):
            active = "active" if i == 0 else ""
            tabs_html += f'  <div class="entity-tab {active}" data-entity="{et}">{et}</div>\n'
        tabs_html += '</div>\n'
        body_parts.append(tabs_html)

        search_html = '<input type="text" class="search-bar" placeholder="Search all visible rows..." oninput="filterTable(this.value)">\n'
        body_parts.append(search_html)

        for i, et in enumerate(stats["records_types"]):
            records = bejson_core_get_records_by_type(doc, et)
            panel_cls = "entity-panel active" if i == 0 else "entity-panel"
            body_parts.append(f'<div class="{panel_cls}" data-entity="{et}">')
            body_parts.append(f'<div class="record-count">{len(records)} {et} record(s)</div>')
            body_parts.append(_render_table_html(records, fnames, doc))
            body_parts.append('</div>')
    else:
        body_parts.append(_render_table_html(doc["Values"], fnames, doc))

    body = "\n".join(body_parts)
    js = ""
    if version == "104db":
        js = """<script>
document.querySelectorAll('.entity-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    const entity = tab.dataset.entity;
    document.querySelectorAll('.entity-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.entity-panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.querySelector(`.entity-panel[data-entity="${entity}"]`).classList.add('active');
  });
});
function filterTable(query) {
  const q = query.toLowerCase();
  document.querySelectorAll('.entity-panel.active tbody tr').forEach(tr => {
    const text = tr.textContent.toLowerCase();
    tr.style.display = text.includes(q) ? '' : 'none';
  });
}
document.querySelectorAll('th[data-col]').forEach(th => {
  th.addEventListener('click', () => {
    const col = parseInt(th.dataset.col);
    const tbody = th.closest('table').querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const asc = th.dataset.dir !== 'desc';
    rows.sort((a, b) => {
      const av = a.cells[col]?.textContent.trim() || '';
      const bv = b.cells[col]?.textContent.trim() || '';
      return asc ? av.localeCompare(bv) : bv.localeCompare(av);
    });
    rows.forEach(r => tbody.appendChild(r));
    th.dataset.dir = asc ? 'desc' : 'asc';
  });
});
</script>"""

    return HTML_WRAPPER.format(title=title, css=css, body=body, js=js)


def _render_table_html(records, fnames, doc):
    """Render a single table."""
    parts = ['<table><thead><tr><th class="idx-col">#</th>']
    for i, name in enumerate(fnames):
        parts.append(f'<th data-col="{i}">{html.escape(name)}</th>')
    parts.append('</tr></thead><tbody>')

    for ri, rec in enumerate(records):
        parts.append(f'<tr><td class="idx-col">{ri}</td>')
        for ci, val in enumerate(rec):
            parts.append(f'<td>{fmt_value(val)}</td>')
        parts.append('</tr>')
    parts.append('</tbody></table>')
    return "\n".join(parts)


def render_log(doc, dark=True):
    """Render as a tabled log file — each record is a log entry with fields."""
    version = bejson_core_get_version(doc)
    stats = bejson_core_get_stats(doc)
    fnames = [f["name"] for f in doc["Fields"]]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

    title = f"BEJSON Log — {stats['record_count']} records"

    # CSS: base is always white, overlay dark if requested
    css = CSS_LOG
    if dark:
        css += "\n" + CSS_LOG_DARK

    header_html = f"""<div class="log-header">
  <h1>BEJSON {version} Tabled Log</h1>
  <div class="meta">{ts} · {stats['field_count']} fields · {stats['record_count']} records · Types: {', '.join(stats['records_types'])}</div>
</div>"""

    filter_html = '<div class="filter-bar">'
    if version == "104db":
        filter_html += f'<select id="entityFilter" onchange="filterLog()"><option value="">All Entities</option>'
        for et in stats["records_types"]:
            filter_html += f'<option value="{et}">{et}</option>'
        filter_html += '</select>'
    filter_html += '<input type="text" id="logSearch" placeholder="Search log entries..." oninput="filterLog()"></div>'

    entries = []
    for ri, rec in enumerate(doc["Values"]):
        entity = rec[0] if version == "104db" else "—"
        fields_html = '<div class="log-field-row">'
        for ci, val in enumerate(rec):
            if version == "104db" and ci == 0:
                continue  # Skip discriminator, shown as entity
            vclass = "log-field-val"
            if val is None:
                vclass += " null"
            elif isinstance(val, bool):
                vclass += f" bool-{'true' if val else 'false'}"

            val_display = fmt_log_value(val)
            fields_html += f'<div class="log-field"><span class="log-field-name">{html.escape(fnames[ci])}</span><span class="log-field-sep">=</span><span class="{vclass}">{val_display}</span></div>'
        fields_html += '</div>'

        entry = f"""<div class="log-entry" data-entity="{html.escape(str(entity))}">
  <div class="log-line">
    <span class="log-ts">{ts}</span>
    <span class="log-entity">{html.escape(str(entity))}</span>
    <span class="log-idx">#{ri}</span>
  </div>
  {fields_html}
</div>"""
        entries.append(entry)

    body = header_html + "\n" + filter_html + "\n" + "\n".join(entries)

    js = """<script>
function filterLog() {
  const entity = document.getElementById('entityFilter')?.value || '';
  const query = document.getElementById('logSearch').value.toLowerCase();
  document.querySelectorAll('.log-entry').forEach(entry => {
    const e = entry.dataset.entity || '';
    const text = entry.textContent.toLowerCase();
    const matchEntity = !entity || e === entity;
    const matchQuery = !query || text.includes(query);
    entry.style.display = (matchEntity && matchQuery) ? '' : 'none';
  });
}
</script>"""

    return HTML_WRAPPER.format(title=title, css=CSS_LOG, body=body, js=js)


def fmt_log_value(val):
    """Format a value for log display."""
    if val is None:
        return "null"
    if isinstance(val, bool):
        return str(val).lower()
    if isinstance(val, (list, dict)):
        return html.escape(json.dumps(val))
    return html.escape(str(val))


# ─── Main ─────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="BEJSON → HTML Table / Log")
    ap.add_argument("file", help="BEJSON file")
    ap.add_argument("-o", "--output", help="Output HTML file")
    ap.add_argument("--dark", action="store_true", help="Dark theme overlay (default is white bg)")
    ap.add_argument("--minimal", action="store_true", help="Minimal light monospace theme")
    ap.add_argument("--log", action="store_true", help="Tabled log file format")
    ap.add_argument("--json-only", action="store_true", help="Output JSON array only (no HTML)")
    args = ap.parse_args()

    doc = bejson_core_load_file(args.file)
    doc["_source_file"] = args.file

    if args.json_only:
        fnames = [f["name"] for f in doc["Fields"]]
        records = [dict(zip(fnames, rec)) for rec in doc["Values"]]
        print(json.dumps(records, indent=2))
        return 0

    if args.log:
        html_out = render_log(doc, dark=args.dark)
    else:
        html_out = render_table(doc, dark=args.dark)

    output = args.output or Path(args.file).stem + ".html"
    Path(output).write_text(html_out, encoding="utf-8")
    mode = "Log" if args.log else "Table"
    theme = "Minimal" if args.minimal else "Dark"
    print(f"{C.GREEN}✓ {mode} ({theme}) → {output}{C.RESET}")
    print(f"  {C.BOLD}{bejson_core_get_stats(doc)['record_count']}{C.RESET} records, {len(doc['Fields'])} fields")
    return 0


if __name__ == "__main__":
    sys.exit(main())
