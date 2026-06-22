#!/usr/bin/env python3
"""Extract readable text from Jira DOCX (.docx) attachments for workflow intake.

Companion to ``extract_jira_pdf_text.py`` — same CLI and exit-code contract, but
for Word ``.docx`` files (this script does NOT handle PDFs; use the PDF helper
for those).

A ``.docx`` is a ZIP container of XML parts, so the dependable path is a
deterministic stdlib extractor that reads ``word/document.xml`` (plus any
headers/footers) directly from the archive — no third-party packages required.
For parity with the PDF helper it first tries an external converter
(``pandoc``) when one is installed, then falls back to the stdlib parser.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from typing import List, Optional, Tuple


# A successfully parsed DOCX is valid even when short, so the bar is "any text".
MIN_READABLE_CHARS = 1

# WordprocessingML main namespace.
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def run_external(docx_path: str) -> Tuple[Optional[str], Optional[str]]:
    """Best-effort external conversion. Returns (text, method) or (None, None)."""
    pandoc = shutil.which("pandoc")
    if not pandoc:
        return None, None
    try:
        result = subprocess.run(
            [pandoc, "-f", "docx", "-t", "plain", docx_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        text = result.stdout.decode("utf-8", errors="replace")
        if text.strip():
            return text, "pandoc"
    except (OSError, subprocess.CalledProcessError):
        pass
    return None, None


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _paragraph_text(paragraph: ET.Element) -> str:
    """Concatenate a paragraph's text, honoring tabs and line breaks in order."""
    parts: List[str] = []
    for element in paragraph.iter():
        name = _local(element.tag)
        if name == "t":
            parts.append(element.text or "")
        elif name == "tab":
            parts.append("\t")
        elif name in ("br", "cr"):
            parts.append("\n")
    return "".join(parts)


def _table_text(table: ET.Element) -> str:
    rows: List[str] = []
    for row in table.findall(f"{{{W_NS}}}tr"):
        cells: List[str] = []
        for cell in row.findall(f"{{{W_NS}}}tc"):
            cell_text = " ".join(
                _paragraph_text(p).strip()
                for p in cell.findall(f"{{{W_NS}}}p")
                if _paragraph_text(p).strip()
            )
            cells.append(cell_text)
        rows.append(" | ".join(cells))
    return "\n".join(rows)


def _render(element: ET.Element, out: List[str]) -> None:
    """Walk the tree in document order; render paragraphs and tables as blocks.

    Tables are rendered whole and not recursed into (their cell paragraphs are
    handled by ``_table_text``), so nothing is counted twice. Paragraphs nested
    in wrappers like ``w:sdt`` are still reached via recursion.
    """
    name = _local(element.tag)
    if name == "tbl":
        block = _table_text(element)
        if block.strip():
            out.append(block)
        return
    if name == "p":
        line = _paragraph_text(element).strip()
        if line:
            out.append(line)
        return
    for child in element:
        _render(child, out)


def _part_text(xml_bytes: bytes) -> str:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return ""
    out: List[str] = []
    _render(root, out)
    return "\n".join(out)


def fallback_extract(docx_path: str) -> str:
    try:
        archive = zipfile.ZipFile(docx_path)
    except (zipfile.BadZipFile, OSError):
        return ""

    chunks: List[str] = []
    with archive:
        names = archive.namelist()

        if "word/document.xml" in names:
            body = _part_text(archive.read("word/document.xml"))
            if body.strip():
                chunks.append(body)

        for name in sorted(names):
            if not re.match(r"word/(header|footer)\d*\.xml$", name):
                continue
            part = _part_text(archive.read(name))
            if part.strip():
                kind = "HEADER" if "header" in name else "FOOTER"
                chunks.append(f"--- {kind} ({name}) ---\n{part}")

    return "\n\n".join(chunks)


def readable_score(text: str) -> int:
    return sum(1 for char in text if char.isalnum())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract readable text from a Jira DOCX (.docx) attachment."
    )
    parser.add_argument("docx", help="Path to the .docx attachment")
    parser.add_argument("-o", "--output", help="Write extracted UTF-8 text to this file")
    args = parser.parse_args()

    if not os.path.exists(args.docx):
        print(f"DOCX not found: {args.docx}", file=sys.stderr)
        return 2

    text, method = run_external(args.docx)
    if not text or readable_score(text) < MIN_READABLE_CHARS:
        text = fallback_extract(args.docx)
        method = "python-fallback"

    if not text or readable_score(text) < MIN_READABLE_CHARS:
        print(
            "No readable DOCX text extracted; manual inspection required.",
            file=sys.stderr,
        )
        return 3

    text = text.rstrip() + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text)
    else:
        sys.stdout.write(text)

    print(f"DOCX extraction method: {method}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
