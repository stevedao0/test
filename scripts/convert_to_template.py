#!/usr/bin/env python3
"""
Convert .docx file with <placeholder> format to {{placeholder}} format for docxtpl
"""
import zipfile
import re
import sys
import tempfile
import shutil
from pathlib import Path


def convert_docx_to_template(input_path: Path, output_path: Path) -> None:
    """Convert <placeholder> to {{placeholder}} in .docx XML files"""

    tmp_dir = Path(tempfile.mkdtemp(prefix="docx_convert_"))

    try:
        with zipfile.ZipFile(input_path, 'r') as zin:
            # Extract all files
            zin.extractall(tmp_dir)

        # Process all XML files in word/ directory
        word_dir = tmp_dir / 'word'
        if word_dir.exists():
            for xml_file in word_dir.glob('*.xml'):
                content = xml_file.read_text(encoding='utf-8')

                # Step 1: Remove spaces inside <...> tags that break placeholders
                # Example: < nga y _ky_hop_dong > → <ngay_ky_hop_dong>
                def clean_placeholder(match):
                    inner = ''.join(match.group(1).split())
                    return f'<{inner}>'

                content = re.sub(
                    r'<\s*([a-z_][a-z0-9_]*(?:\s+[a-z0-9_]+)*)\s*>',
                    clean_placeholder,
                    content
                )

                # Step 2: Convert <placeholder> to {{placeholder}}
                # Only match <xxx> where xxx doesn't contain : (not XML namespace)
                # and starts with lowercase letter or underscore
                def convert_placeholder(match):
                    tag_content = match.group(1)
                    # Check if it's a XML tag (has : or starts with /)
                    if ':' in tag_content or tag_content.startswith('/'):
                        return match.group(0)  # Keep as is
                    # Check if it matches placeholder pattern
                    if re.match(r'^[a-z_][a-z0-9_]*$', tag_content):
                        return '{{' + tag_content + '}}'
                    return match.group(0)

                content = re.sub(r'<([^>]+)>', convert_placeholder, content)

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
        print("Usage: python3 convert_to_template.py <input.docx> <output.docx>")
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
