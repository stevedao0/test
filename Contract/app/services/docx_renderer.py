from __future__ import annotations

from datetime import date
from pathlib import Path

import re
import shutil
import tempfile
import zipfile

from docxtpl import DocxTemplate, RichText
from lxml import etree


def _repair_template_placeholders(*, template_path: Path) -> Path:
    tmp_dir = Path(tempfile.mkdtemp(prefix="docx_tpl_repair_"))
    out_path = tmp_dir / template_path.name

    # Repair known malformed placeholders introduced by template conversion.
    # Example observed in templates: "&lt;nguoi_thuc_hien_{{\nemail}}&gt;"
    patterns: list[tuple[re.Pattern[str], str]] = [
        (
            re.compile(r"&lt;\s*\{\{\s*so_hop_dong\s*\}\}\s*_day_du\s*&gt;", re.IGNORECASE),
            "{{so_hop_dong_day_du}}",
        ),
        (
            re.compile(r"<\s*\{\{\s*so_hop_dong\s*\}\}\s*_day_du\s*>", re.IGNORECASE),
            "{{so_hop_dong_day_du}}",
        ),
        (
            re.compile(r"&lt;\s*nguoi_thuc_hien_\s*\{\{\s*email\s*\}\}\s*&gt;", re.IGNORECASE),
            "{{nguoi_thuc_hien_email}}",
        ),
        (
            re.compile(r"<\s*nguoi_thuc_hien_\s*\{\{\s*email\s*\}\}\s*>", re.IGNORECASE),
            "{{nguoi_thuc_hien_email}}",
        ),
        (
            re.compile(r"&lt;\s*(\{\{[^{}]+\}\})\s*&gt;"),
            r"\1",
        ),
        (
            re.compile(r"<\s*(\{\{[^{}]+\}\})\s*>", re.IGNORECASE),
            r"\1",
        ),
        (
            re.compile(r"&lt;\s*([a-zA-Z0-9_\-]+)\s*&gt;"),
            r"{{\1}}",
        ),
        (
            re.compile(r"<\s*([a-zA-Z0-9_\-]+)\s*>", re.IGNORECASE),
            r"{{\1}}",
        ),
    ]

    with zipfile.ZipFile(template_path, "r") as zin, zipfile.ZipFile(out_path, "w") as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.startswith("word/") and item.filename.endswith(".xml"):
                try:
                    text = data.decode("utf-8")
                    for pat, repl in patterns:
                        text = pat.sub(repl, text)
                    data = text.encode("utf-8")
                except Exception:
                    pass
            zout.writestr(item, data)

    return out_path


def render_contract_docx(*, template_path: Path, output_path: Path, context: dict) -> None:
    repaired_template_path = _repair_template_placeholders(template_path=template_path)
    tpl = DocxTemplate(str(repaired_template_path))

    # Work on a copy to avoid leaking RichText objects to other exporters.
    render_ctx = dict(context)

    # Make signature fields bold (Người đại diện và Chức vụ)
    bold_fields = ['nguoi_dai_dien', 'NGUOI_DAI_DIEN', 'chuc_vu', 'CHUC_VU']
    for field in bold_fields:
        if field in render_ctx and render_ctx[field] and isinstance(render_ctx[field], str):
            rt = RichText()
            rt.add(render_ctx[field], bold=True)
            render_ctx[field] = rt

    tpl.render(render_ctx)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tpl.save(str(output_path))
    normalize_docx_formatting(output_path)


def normalize_docx_formatting(docx_path: Path) -> None:
    tmp_dir = Path(tempfile.mkdtemp(prefix="docx_norm_"))
    tmp_zip = tmp_dir / "out.docx"

    ns = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    }

    try:
        with zipfile.ZipFile(docx_path, "r") as zin, zipfile.ZipFile(tmp_zip, "w") as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)

                if item.filename.startswith("word/") and item.filename.endswith(".xml"):
                    try:
                        parser = etree.XMLParser(recover=True, huge_tree=True)
                        root = etree.fromstring(data, parser=parser)

                        for el in root.xpath(".//w:highlight", namespaces=ns):
                            # Some templates store highlight in styles; removing or setting to none both work.
                            el.set(f"{{{ns['w']}}}val", "none")
                            parent = el.getparent()
                            if parent is not None:
                                parent.remove(el)

                        for el in root.xpath(".//w:shd", namespaces=ns):
                            # Clear shading (background). Remove element to avoid yellow blocks.
                            parent = el.getparent()
                            if parent is not None:
                                parent.remove(el)

                        for el in root.xpath(".//w:color", namespaces=ns):
                            el.set(f"{{{ns['w']}}}val", "000000")

                        data = etree.tostring(
                            root,
                            xml_declaration=True,
                            encoding="UTF-8",
                            standalone="yes",
                        )
                    except Exception:
                        # If any XML chunk fails to parse, keep original chunk
                        pass

                zout.writestr(item, data)

        shutil.copyfile(tmp_zip, docx_path)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def date_parts(d: date) -> dict:
    return {
        "ngay": f"{d.day:02d}",
        "thang": f"{d.month:02d}",
        "nam": f"{d.year}",
    }
