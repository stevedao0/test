from __future__ import annotations

import re
import zipfile
from pathlib import Path


def main() -> None:
    p = Path(r"F:\Dev\Contract\templates\HDQTGAN_PN_MR_template.docx")
    if not p.exists():
        raise FileNotFoundError(p)

    with zipfile.ZipFile(p, "r") as z:
        for xml_name in ["word/document.xml", "word/glossary/document.xml"]:
            if xml_name not in z.namelist():
                continue
            s = z.read(xml_name).decode("utf-8", "ignore")

            tags = re.findall(r"w:tag w:val=\"([^\"]+)\"", s)
            uniq = sorted(set(tags))

            print("=")
            print("xml:", xml_name)
            print("unique tags:", len(uniq))

            # Print common patterns first
            for t in [x for x in uniq if x.lower().startswith("txt")]:
                print("tag:", t)

            # Find where '1234' is and show nearby tags
            idx = s.find("1234")
            print("idx1234:", idx)
            if idx != -1:
                ctx = s[max(0, idx - 1000) : idx + 1000]
                ctx_tags = sorted(set(re.findall(r"w:tag w:val=\"([^\"]+)\"", ctx)))
                print("tags near 1234:", ctx_tags)

            # Find dotted-year remnants
            m = re.search(r"\.{2,}\s*\d{4}", s)
            print("dotted-year found:", bool(m))
            if m:
                ctx = s[max(0, m.start() - 400) : m.end() + 400]
                print("dotted-year sample:")
                print(ctx)


if __name__ == "__main__":
    main()
