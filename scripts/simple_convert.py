#!/usr/bin/env python3
"""
Simple conversion: <placeholder> to {{placeholder}} using string replacement
"""
import zipfile
import re
import sys
import tempfile
import shutil
from pathlib import Path


def convert_docx_placeholders(input_path: Path, output_path: Path) -> None:
    """Convert <placeholder> to {{placeholder}} in .docx text nodes"""

    tmp_dir = Path(tempfile.mkdtemp(prefix="docx_convert_"))

    try:
        with zipfile.ZipFile(input_path, 'r') as zin:
            zin.extractall(tmp_dir)

        # Process all XML files in word/ directory
        word_dir = tmp_dir / 'word'
        placeholders_found = set()

        if word_dir.exists():
            for xml_file in word_dir.glob('*.xml'):
                content = xml_file.read_text(encoding='utf-8')
                original = content

                # Step 1: Clean up spaces between < and > that Word splits
                # Example: "< nga y _ky_hop_dong >" → "<ngay_ky_hop_dong>"
                def clean_spaces(match):
                    cleaned = ''.join(match.group(1).split())
                    placeholders_found.add(cleaned)
                    return '<' + cleaned + '>'

                content = re.sub(r'<\s*([a-z_][a-z0-9_\s]+?)\s*>', clean_spaces, content)

                # Step 2: Convert <placeholder> to {{placeholder}}
                def convert_placeholder(match):
                    placeholder = match.group(1)
                    placeholders_found.add(placeholder)
                    return '{{' + placeholder + '}}'

                content = re.sub(r'<([a-z_][a-z0-9_]+)>', convert_placeholder, content)

                if content != original:
                    xml_file.write_text(content, encoding='utf-8')

        # Create new .docx from modified files
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for file in tmp_dir.rglob('*'):
                if file.is_file():
                    arcname = file.relative_to(tmp_dir)
                    zout.write(file, arcname)

        print(f"✓ Converted: {input_path.name} → {output_path.name}")
        print(f"✓ Found {len(placeholders_found)} placeholders:")
        for p in sorted(placeholders_found):
            print(f"  - {{{{{p}}}}}")

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 simple_convert.py <input.docx> <output.docx>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    convert_docx_placeholders(input_file, output_file)
