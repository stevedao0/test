#!/usr/bin/env python3
import zipfile
import re
import sys
from pathlib import Path

def extract_placeholders_from_docx(docx_path):
    """Extract all placeholders like {{variable}} from a .docx file"""
    placeholders = set()

    with zipfile.ZipFile(docx_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.startswith('word/') and file_name.endswith('.xml'):
                content = zip_ref.read(file_name).decode('utf-8', errors='ignore')
                found = re.findall(r'\{\{([^}]+)\}\}', content)
                placeholders.update(found)

    return sorted(placeholders)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 extract_placeholders.py <path_to_docx>")
        sys.exit(1)

    docx_path = sys.argv[1]

    if not Path(docx_path).exists():
        print(f"File not found: {docx_path}")
        sys.exit(1)

    placeholders = extract_placeholders_from_docx(docx_path)

    print(f"\n=== Placeholders found in {Path(docx_path).name} ===")
    print(f"Total: {len(placeholders)}\n")

    for i, placeholder in enumerate(placeholders, 1):
        print(f"{i:3d}. {{{{{placeholder}}}}}")
