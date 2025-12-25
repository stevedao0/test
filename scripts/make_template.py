#!/usr/bin/env python3
"""
Convert Word document placeholders to Jinja2 template format.
Handles Word's tendency to split text across multiple <w:t> nodes.
"""
import zipfile
import re
import sys
import tempfile
import shutil
from pathlib import Path

import xml.etree.ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", W_NS)


def merge_text_runs(xml_content: str) -> str:
    """Merge consecutive <w:t> nodes to fix Word's text splitting"""

    # Pattern to find consecutive w:t elements
    pattern = r'(<w:t[^>]*>([^<]*)</w:t>)(\s*<w:t[^>]*>([^<]*)</w:t>)+'

    def merge_runs(match):
        # Extract all text content from consecutive w:t nodes
        text_pattern = r'<w:t[^>]*>([^<]*)</w:t>'
        texts = re.findall(text_pattern, match.group(0))
        merged_text = ''.join(texts)

        # Decode HTML entities for < and >
        merged_text = merged_text.replace('&lt;', '<').replace('&gt;', '>')

        # Return a single w:t node with merged text
        return f'<w:t>{merged_text}</w:t>'

    # Keep merging until no more changes
    prev_content = None
    while prev_content != xml_content:
        prev_content = xml_content
        xml_content = re.sub(pattern, merge_runs, xml_content)

    return xml_content


def merge_text_runs_xml(xml_bytes: bytes) -> bytes:
    ns = {"w": W_NS}
    root = ET.fromstring(xml_bytes)

    # Merge all text nodes within each paragraph to prevent placeholders being split across runs.
    for p in root.findall(".//w:p", ns):
        ts = p.findall(".//w:t", ns)
        if len(ts) <= 1:
            continue

        merged = "".join([(t.text or "") for t in ts])
        merged = merged.replace("&lt;", "<").replace("&gt;", ">")

        ts[0].text = merged
        for t in ts[1:]:
            t.text = ""

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def convert_placeholders_xml(xml_bytes: bytes, placeholders: list) -> tuple[bytes, int]:
    ns = {"w": W_NS}
    root = ET.fromstring(xml_bytes)

    count = 0
    for t in root.findall(".//w:t", ns):
        if not t.text:
            continue
        text_before = t.text
        text_after = text_before

        for placeholder in placeholders:
            text_after = text_after.replace(f"<{placeholder}>", f"{{{{{placeholder}}}}}")
            text_after = text_after.replace(f"< {placeholder} >", f"{{{{{placeholder}}}}}")
            text_after = text_after.replace(placeholder, f"{{{{{placeholder}}}}}") if text_after == text_before else text_after

        if text_after != text_before:
            t.text = text_after
            count += 1

    return ET.tostring(root, encoding="utf-8", xml_declaration=True), count


def convert_placeholders(xml_content: str, placeholders: list) -> tuple:
    """Convert specific placeholders to Jinja2 format"""

    count = 0
    for placeholder in placeholders:
        # Match placeholder in text nodes, with or without < > around it
        pattern = f'(<w:t[^>]*>)([^<]*{re.escape(placeholder)}[^<]*)(</w:t>)'

        def replace_in_text(match):
            nonlocal count
            prefix = match.group(1)
            text = match.group(2)
            suffix = match.group(3)

            # Replace <placeholder> and &lt;placeholder&gt; with {{placeholder}}
            new_text = re.sub(
                r'<\s*' + re.escape(placeholder) + r'\s*>',
                '{{' + placeholder + '}}',
                text
            )

            if new_text == text:
                new_text = re.sub(
                    r'&lt;\s*' + re.escape(placeholder) + r'\s*&gt;',
                    '{{' + placeholder + '}}',
                    text,
                )

            # Also replace bare placeholder (without < >) with {{placeholder}}
            if new_text == text:
                new_text = re.sub(
                    r'\b' + re.escape(placeholder) + r'\b',
                    '{{' + placeholder + '}}',
                    text
                )

            if new_text != text:
                count += 1
            return prefix + new_text + suffix

        xml_content = re.sub(pattern, replace_in_text, xml_content)

    return xml_content, count


def convert_docx_to_template(input_path: Path, output_path: Path, placeholders: list) -> int:
    """Convert .docx placeholders to Jinja2 template format"""
    
    tmp_dir = Path(tempfile.mkdtemp(prefix="docx_convert_"))
    total_conversions = 0
    
    try:
        # Extract docx
        with zipfile.ZipFile(input_path, 'r') as zin:
            zin.extractall(tmp_dir)
        
        # Process document.xml
        doc_xml = tmp_dir / 'word' / 'document.xml'
        if doc_xml.exists():
            xml_bytes = doc_xml.read_bytes()

            # Step 1: Merge split text runs (XML-safe)
            xml_bytes = merge_text_runs_xml(xml_bytes)

            # Step 2: Convert placeholders (XML-tree based, prefix-agnostic)
            xml_bytes, count = convert_placeholders_xml(xml_bytes, placeholders)
            total_conversions = count

            # Save modified XML
            doc_xml.write_bytes(xml_bytes)
        
        # Create new .docx
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for file in tmp_dir.rglob('*'):
                if file.is_file():
                    zout.write(file, file.relative_to(tmp_dir))
        
        return total_conversions
    
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == '__main__':
    # Define all placeholders for contracts and annexes
    CONTRACT_PLACEHOLDERS = [
        'so_hop_dong', 'linh_vuc', 'ten_kenh', 'link_kenh',
        'nguoi_dai_dien', 'chuc_vu', 'dia_chi', 'so_dien_thoai',
        'ma_so_thue', 'email', 'nguoi_thuc_hien_email',
        'so_CCCD', 'ngay_cap_CCCD',
        'ngay_ky_hop_dong', 'thang_ky_hop_dong', 'nam_ky_hop_dong',
        'so_tien_chua_GTGT', 'thue_GTGT', 'so_tien_GTGT',
        'so_tien_bang_chu',
        'TEN_DON_VI'
    ]
    
    ANNEX_PLACEHOLDERS = CONTRACT_PLACEHOLDERS + [
        'so_hop_dong_day_du', 'so_phu_luc', 'ten_don_vi',
        'ngay_ky_phu_luc', 'thang_ky_phu_luc', 'nam_ky_phu_luc'
    ]
    
    print("=" * 80)
    print("CONVERTING TEMPLATES")
    print("=" * 80)
    
    # Convert contract template
    print("\n[1] Converting Hợp đồng template...")
    count1 = convert_docx_to_template(
        Path("Mau hop dong/Nam_SHD_SCTT_Ten kenh_MR_new.docx"),
        Path("templates/HDQTGAN_PN_MR_template.docx"),
        CONTRACT_PLACEHOLDERS
    )
    print(f"    ✓ Converted {count1} placeholders")
    
    # Convert annex template
    print("\n[2] Converting Phụ lục template...")
    count2 = convert_docx_to_template(
        Path("Mau hop dong/Nam_SHD_SPL_SCTT_Ten kenh_MR_new.docx"),
        Path("templates/HDQTGAN_PN_MR_annex_template.docx"),
        ANNEX_PLACEHOLDERS
    )
    print(f"    ✓ Converted {count2} placeholders")
    
    print(f"\n{'=' * 80}")
    print(f"✅ DONE! Total: {count1 + count2} conversions")
    print(f"{'=' * 80}")
