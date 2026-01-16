#!/usr/bin/env python3
"""Convert justice_position_analysis.md to PDF using weasyprint."""

import markdown
import os
from weasyprint import HTML, CSS

# Get directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Read the markdown file
with open(os.path.join(SCRIPT_DIR, 'justice_position_analysis.md'), 'r') as f:
    md_content = f.read()

# Convert markdown to HTML
html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

# Wrap in HTML document with styling
full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: Georgia, 'Times New Roman', serif;
            font-size: 11pt;
            line-height: 1.5;
            margin: 1in;
            color: #333;
        }}
        h1 {{
            font-size: 18pt;
            color: #1a1a1a;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
            margin-top: 30px;
        }}
        h2 {{
            font-size: 14pt;
            color: #2a2a2a;
            margin-top: 25px;
            border-bottom: 1px solid #666;
            padding-bottom: 5px;
        }}
        h3 {{
            font-size: 12pt;
            color: #3a3a3a;
            margin-top: 20px;
        }}
        h4 {{
            font-size: 11pt;
            color: #444;
            margin-top: 15px;
        }}
        p {{
            margin: 10px 0;
            text-align: justify;
        }}
        ul, ol {{
            margin: 10px 0 10px 20px;
        }}
        li {{
            margin: 5px 0;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ccc;
            margin: 30px 0;
        }}
        strong {{
            color: #1a1a1a;
        }}
        code {{
            background-color: #f5f5f5;
            padding: 2px 5px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ccc;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f0f0f0;
        }}
        @page {{
            size: letter;
            margin: 0.75in;
            @bottom-center {{
                content: counter(page);
            }}
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""

# Convert to PDF
output_path = os.path.join(SCRIPT_DIR, 'justice_position_analysis.pdf')
HTML(string=full_html).write_pdf(output_path)

print(f"PDF created: {output_path}")
