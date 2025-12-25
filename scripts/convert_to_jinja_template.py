#!/usr/bin/env python3
"""
Convert .docx file with <placeholder> format to {{placeholder}} format for docxtpl
Uses proper XML parsing to handle text nodes correctly
"""
import zipfile
import re
import sys
import tempfile
import shutil
from pathlib import Path
from lxml import etree


def convert_text_nodes(content: str) -> str:
    """Convert <placeholder> to {{placeholder}} in text, handling Word's text splitting"""

    # Step 1: Clean up spaces inside <...> that Word might have split
    # Example: "< nga y _ky_hop_dong >" → "<ngay_ky_hop_dong>"
    def clean_spaces(match):
        return '<' + ''.join(match.group(1).split()) + '>'

    content = re.sub(r'<\s*([a-z_][a-z0-9_\s]+)\s*>', clean_spaces, content)

    # Step 2: Convert <placeholder> to {{placeholder}}
    # Only match patterns that look like our placeholders
    content = re.sub(r'<([a-z_][a-z0-9_]+)>', r'{{\1}}', content)

    return content


def convert_docx_to_template(input_path: Path, output_path: Path) -> None:
    """Convert <placeholder> to {{placeholder}} in .docx XML files"""

    tmp_dir = Path(tempfile.mkdtemp(prefix="docx_convert_"))
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

    try:
        with zipfile.ZipFile(input_path, 'r') as zin:
            zin.extractall(tmp_dir)

        # Process all XML files in word/ directory
        word_dir = tmp_dir / 'word'
        if word_dir.exists():
            for xml_file in word_dir.glob('*.xml'):
                try:
                    tree = etree.parse(str(xml_file))
                    root = tree.getroot()

                    # Find all text nodes (w:t elements)
                    for t_elem in root.xpath('.//w:t', namespaces=ns):
                        if t_elem.text:
                            # Convert placeholders in text content
                            t_elem.text = convert_text_nodes(t_elem.text)

                    # Save modified XML
                    tree.write(
                        str(xml_file),
                        xml_declaration=True,
                        encoding='UTF-8',
                        standalone='yes'
                    )
                except Exception as e:
                    print(f"Warning: Could not process {xml_file.name}: {e}")
                    # If XML parsing fails, fallback to string replacement
                    content = xml_file.read_text(encoding='utf-8')
                    content = convert_text_nodes(content)
                    xml_file.write_text(content, encoding='utf-8')

        # Create new .docx from modified files
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for file in tmp_dir.rglob('*'):
                if file.is_file():
                    arcname = file.relative_to(tmp_dir)
                    zout.write(file, arcname)

        print(f"✓ Converted: {input_path.name} → {output_path.name}")

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 convert_to_jinja_template.py <input.docx> <output.docx>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    convert_docx_to_template(input_file, output_file)
    print(f"\n✓ Template created successfully!")
    print(f"  Input:  {input_file}")
    print(f"  Output: {output_file}")
