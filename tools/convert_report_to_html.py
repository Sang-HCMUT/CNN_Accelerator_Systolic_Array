# -*- coding: utf-8 -*-
"""
Script: convert_report_to_html.py
Converts BaoCao_TienDo_50_CNN_Systolic_SoC.md into a standalone, publication-grade HTML report
with base64 embedded images, responsive typography, and print-ready CSS for direct PDF/Word export.
"""

import os
import re
import sys
import base64

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

MD_PATH = 'BaoCao_TienDo_50_CNN_Systolic_SoC.md'
HTML_PATH = 'BaoCao_TienDo_50_CNN_Systolic_SoC.html'

with open(MD_PATH, 'r', encoding='utf-8') as f:
    md_text = f.read()

# Base64 cache for images
def get_base64_image(rel_path):
    clean_path = rel_path.strip().replace('/', os.sep)
    if clean_path.startswith(os.sep) and len(clean_path) > 2 and clean_path[2] == ':':
        clean_path = clean_path[1:]
    
    if os.path.exists(clean_path):
        with open(clean_path, 'rb') as img_f:
            b64_data = base64.b64encode(img_f.read()).decode('utf-8')
            mime = "image/gif" if clean_path.lower().endswith(".gif") else "image/png"
            return f"data:{mime};base64,{b64_data}"
            
    # Check in figures/
    basename = os.path.basename(clean_path)
    fig_path = os.path.join('figures', basename)
    if os.path.exists(fig_path):
        with open(fig_path, 'rb') as img_f:
            b64_data = base64.b64encode(img_f.read()).decode('utf-8')
            mime = "image/gif" if clean_path.lower().endswith(".gif") else "image/png"
            return f"data:{mime};base64,{b64_data}"
            
    return rel_path

# Parser helper
lines = md_text.splitlines()
html_lines = []

in_code_block = False
code_lang = ""
code_buffer = []

in_table = False
table_header = []
table_rows = []

def flush_table():
    global in_table, table_header, table_rows
    if not in_table:
        return ""
    
    html = ['<div class="table-container"><table>']
    if table_header:
        html.append('<thead><tr>')
        for th in table_header:
            html.append(f'<th>{th}</th>')
        html.append('</tr></thead>')
    
    if table_rows:
        html.append('<tbody>')
        for row in table_rows:
            html.append('<tr>')
            for td in row:
                html.append(f'<td>{td}</td>')
            html.append('</tr>')
        html.append('</tbody>')
        
    html.append('</table></div>')
    in_table = False
    table_header = []
    table_rows = []
    return '\n'.join(html)

def format_inline(text):
    # Images: ![alt](url) -> <div class="figure-box"><img src="..." alt="..."><p class="caption">...</p></div>
    def replace_img(match):
        alt = match.group(1)
        url = match.group(2)
        b64 = get_base64_image(url)
        return f'<div class="figure-box"><img src="{b64}" alt="{alt}" loading="lazy"/></div>'
    
    text = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_img, text)
    
    # Bold italic
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # Code inline
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    
    return text

for line in lines:
    stripped = line.strip()
    
    # Check code block
    if stripped.startswith('```'):
        if in_table:
            html_lines.append(flush_table())
            
        if not in_code_block:
            in_code_block = True
            code_lang = stripped[3:].strip()
            code_buffer = []
        else:
            in_code_block = False
            code_content = '\n'.join(code_buffer)
            # escape html
            code_content = code_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html_lines.append(f'<pre><code class="language-{code_lang}">{code_content}</code></pre>')
        continue

    if in_code_block:
        code_buffer.append(line)
        continue

    # Tables
    if stripped.startswith('|') and stripped.endswith('|'):
        parts = [p.strip() for p in stripped[1:-1].split('|')]
        # check if divider row
        if all(re.match(r'^:?-+:?$', p) for p in parts):
            continue
            
        if not in_table:
            in_table = True
            table_header = [format_inline(p) for p in parts]
            table_rows = []
        else:
            table_rows.append([format_inline(p) for p in parts])
        continue
    else:
        if in_table:
            html_lines.append(flush_table())

    if not stripped:
        html_lines.append('<div class="spacer"></div>')
        continue

    # Horizontal rule
    if stripped in ['---', '***', '___']:
        html_lines.append('<hr/>')
        continue

    # Headings
    if stripped.startswith('# '):
        html_lines.append(f'<h1 id="{re.sub(r"[^a-zA-Z0-9_-]", "", stripped[2:].lower())}">{format_inline(stripped[2:])}</h1>')
        continue
    if stripped.startswith('## '):
        html_lines.append(f'<h2 id="{re.sub(r"[^a-zA-Z0-9_-]", "", stripped[3:].lower())}">{format_inline(stripped[3:])}</h2>')
        continue
    if stripped.startswith('### '):
        html_lines.append(f'<h3 id="{re.sub(r"[^a-zA-Z0-9_-]", "", stripped[4:].lower())}">{format_inline(stripped[4:])}</h3>')
        continue
    if stripped.startswith('#### '):
        html_lines.append(f'<h4>{format_inline(stripped[5:])}</h4>')
        continue

    # Blockquotes / Callouts
    if stripped.startswith('> '):
        b_content = stripped[2:]
        callout_type = "note"
        if '[!NOTE]' in b_content:
            callout_type = "note"
            b_content = b_content.replace('[!NOTE]', '<strong>GHI CHÚ:</strong>')
        elif '[!IMPORTANT]' in b_content:
            callout_type = "important"
            b_content = b_content.replace('[!IMPORTANT]', '<strong>QUAN TRỌNG:</strong>')
        elif '[!TIP]' in b_content:
            callout_type = "tip"
            b_content = b_content.replace('[!TIP]', '<strong>GỢI Ý:</strong>')
            
        html_lines.append(f'<div class="callout callout-{callout_type}">{format_inline(b_content)}</div>')
        continue

    # Unordered Lists
    if stripped.startswith('- ') or stripped.startswith('* '):
        html_lines.append(f'<ul><li>{format_inline(stripped[2:])}</li></ul>')
        continue
        
    # Ordered Lists
    match_num = re.match(r'^(\d+)\.\s+(.*)$', stripped)
    if match_num:
        html_lines.append(f'<ol start="{match_num.group(1)}"><li>{format_inline(match_num.group(2))}</li></ol>')
        continue

    # Standard Paragraph
    html_lines.append(f'<p>{format_inline(stripped)}</p>')

if in_table:
    html_lines.append(flush_table())

# Wrap into full styled HTML document
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Báo Cáo Tiến Độ 50% — Đồ Án Tốt Nghiệp Thiết Kế Bộ Tăng Tốc CNN Mảng Tâm Thu SoC</title>
<!-- KaTeX for math rendering -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"
        onload="renderMathInElement(document.body, {delimiters: [{left: '$$', right: '$$', display: true}, {left: '$', right: '$', display: false}]});"></script>
<style>
  :root {
    --primary: #0d47a1;
    --primary-light: #e3f2fd;
    --text: #212121;
    --text-muted: #555555;
    --bg: #ffffff;
    --border: #e0e0e0;
    --code-bg: #f5f7f9;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: var(--text);
    background-color: #f8f9fa;
    line-height: 1.65;
    margin: 0;
    padding: 0;
  }
  .document-container {
    max-width: 1040px;
    margin: 30px auto;
    background: var(--bg);
    padding: 50px 70px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border-radius: 8px;
  }
  h1 {
    color: var(--primary);
    font-size: 26px;
    border-bottom: 2px solid var(--primary);
    padding-bottom: 10px;
    margin-top: 40px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  h2 {
    color: #1565c0;
    font-size: 21px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin-top: 35px;
  }
  h3 {
    color: #1976d2;
    font-size: 17px;
    margin-top: 25px;
  }
  h4 {
    color: #0288d1;
    font-size: 15px;
    margin-top: 20px;
  }
  p, li {
    font-size: 15px;
    color: var(--text);
  }
  ul, ol {
    padding-left: 25px;
    margin: 10px 0;
  }
  li {
    margin-bottom: 6px;
  }
  code {
    font-family: "Consolas", "Courier New", monospace;
    background: var(--code-bg);
    color: #c2185b;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 13.5px;
    border: 1px solid #e0e0e0;
  }
  pre {
    background: #263238;
    color: #eceff1;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 13.5px;
    line-height: 1.5;
  }
  pre code {
    background: transparent;
    color: inherit;
    padding: 0;
    border: none;
  }
  .table-container {
    overflow-x: auto;
    margin: 20px 0;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
  }
  th, td {
    padding: 10px 14px;
    border: 1px solid var(--border);
    text-align: left;
  }
  th {
    background: var(--primary-light);
    color: var(--primary);
    font-weight: 700;
  }
  tr:nth-child(even) td {
    background-color: #fafafa;
  }
  .figure-box {
    text-align: center;
    margin: 30px 0;
  }
  .figure-box img {
    max-width: 100%;
    height: auto;
    border-radius: 6px;
    border: 1px solid #cfd8dc;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
  }
  .callout {
    padding: 14px 18px;
    border-left: 4px solid #1976d2;
    background: #e3f2fd;
    border-radius: 0 6px 6px 0;
    margin: 20px 0;
    font-size: 14.5px;
  }
  .callout-important {
    border-left-color: #d32f2f;
    background: #ffebee;
  }
  .callout-tip {
    border-left-color: #388e3c;
    background: #e8f5e9;
  }
  hr {
    border: 0;
    height: 1px;
    background: #e0e0e0;
    margin: 40px 0;
  }
  a {
    color: #1976d2;
    text-decoration: none;
  }
  a:hover {
    text-decoration: underline;
  }
  @media print {
    body { background: #fff; }
    .document-container { box-shadow: none; padding: 0; margin: 0; }
  }
</style>
</head>
<body>
<div class="document-container">
""" + '\n'.join(html_lines) + """
</div>
</body>
</html>
"""

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(HTML_TEMPLATE)

print(f"[SUCCESS] Generated {HTML_PATH} (Size: {len(HTML_TEMPLATE):,} bytes)")

# Optional copy to current artifact directory
import os
conv_id = "5df3e537-4347-4cef-b9f4-2393c487f3e3"
curr_art_dir = os.path.join(r"C:\Users\hoang\.gemini\antigravity\brain", conv_id)
if os.path.exists(curr_art_dir):
    try:
        art_html = os.path.join(curr_art_dir, HTML_PATH)
        with open(art_html, 'w', encoding='utf-8') as f:
            f.write(HTML_TEMPLATE)
        print(f"[SUCCESS] Copied to active artifact dir: {art_html}")
    except Exception as e:
        print(f"[INFO] Skipping artifact copy: {e}")
