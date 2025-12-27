#!/usr/bin/env python3
"""
Convert Markdown documentation to HTML format suitable for printing to PDF
"""

import markdown
import os
import sys

def convert_markdown_to_html():
    # Path to the markdown file
    md_file = "docs/GUI-Stride技术说明文档.md"
    html_file = "docs/GUI-Stride技术说明文档.html"

    # Check if markdown file exists
    if not os.path.exists(md_file):
        print(f"Error: Markdown file not found at {md_file}")
        sys.exit(1)

    try:
        print(f"Converting {md_file} to HTML...")

        # Read markdown file
        with open(md_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # Convert markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=[
                'fenced_code',
                'tables',
                'toc',
                'codehilite',
                'attr_list'
            ]
        )

        # Create HTML file directly with proper structure
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GUI-Stride 多模态反盗版监控系统技术说明文档</title>
    <style>
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: "Microsoft YaHei", "SimSun", sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 1.5em;
            margin-bottom: 0.8em;
        }
        h1 {
            font-size: 28px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            text-align: center;
        }
        h2 {
            font-size: 22px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
        }
        h3 {
            font-size: 18px;
            color: #34495e;
        }
        h4 {
            font-size: 16px;
            color: #2c3e50;
        }
        p {
            margin-bottom: 1em;
            text-align: justify;
            line-height: 1.8;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "Consolas", "Monaco", monospace;
            font-size: 0.9em;
            color: #e74c3c;
        }
        pre {
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
            margin-bottom: 1.5em;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        pre code {
            background-color: transparent;
            padding: 0;
            color: #333;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 1.5em;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
            color: #2c3e50;
        }
        td {
            vertical-align: top;
        }
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1.5em auto;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .toc {
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 2em;
        }
        .toc ul {
            list-style-type: none;
            padding-left: 20px;
        }
        .toc a {
            color: #3498db;
            text-decoration: none;
        }
        .toc a:hover {
            text-decoration: underline;
        }
        blockquote {
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin: 1.5em 0;
            color: #666;
            font-style: italic;
        }
        hr {
            border: none;
            border-top: 1px solid #ddd;
            margin: 2em 0;
        }
        .page-break {
            page-break-before: always;
        }
        @media print {
            body {
                font-size: 12pt;
                padding: 15mm;
            }
            h1 {
                font-size: 20pt;
            }
            h2 {
                font-size: 16pt;
            }
            h3 {
                font-size: 14pt;
            }
            .no-print {
                display: none;
            }
        }
        @media screen {
            .print-only {
                display: none;
            }
        }
    </style>
</head>
<body>
""")
            # Write the converted markdown content
            f.write(html_content)

            # Write the closing HTML and print instructions
            f.write("""
    <div class="no-print" style="margin-top: 50px; padding: 20px; background: #f0f0f0; border-radius: 5px;">
        <h3>打印说明</h3>
        <p>要生成PDF文档，请按以下步骤操作：</p>
        <ol>
            <li>按 Ctrl+P 打印对话框</li>
            <li>选择"另存为PDF"作为打印机</li>
            <li>在更多设置中：</li>
            <ul>
                <li>页面缩放：实际大小</li>
                <li>纸张大小：A4</li>
                <li>方向：纵向</li>
            </ul>
            <li>点击"保存"按钮保存PDF文件</li>
        </ol>
    </div>
</body>
</html>""")

        print(f"HTML file created at {html_file}")
        print(f"Open this file in a web browser and use 'Save as PDF' or 'Print to PDF'")

        # File size information
        html_size = os.path.getsize(html_file)
        print(f"HTML file size: {html_size / 1024 / 1024:.2f} MB")

        # Provide alternative conversion method using browser
        print("\nAlternative conversion methods:")
        print("1. Open the HTML file in a web browser (Chrome, Firefox, Edge)")
        print("2. Press Ctrl+P to open the print dialog")
        print("3. Choose 'Save as PDF' or 'Microsoft Print to PDF'")
        print("4. Set the following print settings:")
        print("   - Layout: Portrait")
        print("   - Paper size: A4")
        print("   - Margins: Normal")
        print("   - Background graphics: Enabled (for colored elements)")
        print("5. Click 'Save' to generate the PDF")

        # Also create a simple batch script for Windows users
        batch_script = """@echo off
echo Opening HTML file in default browser...
start "" "{}"
echo.
echo After the file opens in browser:
echo 1. Press Ctrl+P
echo 2. Select "Microsoft Print to PDF" or "Save as PDF"
echo 3. Choose A4 paper size
echo 4. Click Save
""".format(html_file.replace('/', '\\'))

        with open("docs/convert_to_pdf.bat", 'w', encoding='utf-8') as f:
            f.write(batch_script)

        print(f"\nBatch script created at docs/convert_to_pdf.bat")
        print("Double-click this script to open the HTML file in browser")

    except Exception as e:
        print(f"Error converting to HTML: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    convert_markdown_to_html()