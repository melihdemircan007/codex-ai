#!/usr/bin/env python3
"""Extract readable text from Jira PDF attachments for Codex workflow intake.

The script prefers the platform `pdftotext` binary when available. If it is not
installed, it falls back to a small deterministic PDF content-stream extractor
that handles the WeasyPrint-style PDFs commonly attached to Jira analysis
documents, including compressed object streams and ToUnicode CMaps.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zlib
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple


MIN_READABLE_CHARS = 200


@dataclass
class PdfObjects:
    objects: Dict[int, bytes]
    streams: Dict[int, bytes]


def run_pdftotext(pdf_path: str) -> Optional[str]:
    binary = shutil.which("pdftotext")
    if not binary:
        return None

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        subprocess.run(
            [binary, "-layout", "-enc", "UTF-8", pdf_path, tmp_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        with open(tmp_path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except (OSError, subprocess.CalledProcessError):
        return None
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def inflate_stream(body: bytes, stream: bytes) -> bytes:
    if b"/FlateDecode" not in body:
        return stream
    try:
        return zlib.decompress(stream)
    except zlib.error:
        return stream


def parse_pdf_objects(data: bytes) -> PdfObjects:
    objects: Dict[int, bytes] = {}
    streams: Dict[int, bytes] = {}

    object_pattern = re.compile(rb"(\d+)\s+0\s+obj(.*?)endobj", re.S)
    stream_pattern = re.compile(rb"stream\r?\n(.*?)\r?\nendstream", re.S)

    for match in object_pattern.finditer(data):
        number = int(match.group(1))
        body = match.group(2).strip()
        objects[number] = body
        stream_match = stream_pattern.search(body)
        if stream_match:
            streams[number] = inflate_stream(body, stream_match.group(1))

    unpack_object_streams(objects, streams)
    return PdfObjects(objects=objects, streams=streams)


def unpack_object_streams(objects: Dict[int, bytes], streams: Dict[int, bytes]) -> None:
    for number, body in list(objects.items()):
        if b"/Type /ObjStm" not in body or number not in streams:
            continue

        n_match = re.search(rb"/N\s+(\d+)", body)
        first_match = re.search(rb"/First\s+(\d+)", body)
        if not n_match or not first_match:
            continue

        first = int(first_match.group(1))
        stream = streams[number]
        header = stream[:first].decode("latin1", errors="ignore").strip().split()
        if len(header) < 2:
            continue

        pairs: List[Tuple[int, int]] = []
        for index in range(0, len(header) - 1, 2):
            try:
                pairs.append((int(header[index]), int(header[index + 1])))
            except ValueError:
                pairs = []
                break

        for index, (obj_id, offset) in enumerate(pairs):
            start = first + offset
            end = first + (pairs[index + 1][1] if index + 1 < len(pairs) else len(stream) - first)
            objects[obj_id] = stream[start:end].strip()


def parse_cmaps(streams: Dict[int, bytes]) -> Dict[int, Dict[int, str]]:
    cmaps: Dict[int, Dict[int, str]] = {}
    for number, stream in streams.items():
        text = stream.decode("latin1", errors="ignore")
        if "beginbfchar" not in text and "beginbfrange" not in text:
            continue

        cmap: Dict[int, str] = {}
        for source, target in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", text):
            if len(source) != 4:
                continue
            try:
                cmap[int(source, 16)] = "".join(
                    chr(int(target[index : index + 4], 16))
                    for index in range(0, len(target), 4)
                )
            except ValueError:
                continue
        if cmap:
            cmaps[number] = cmap
    return cmaps


def build_font_maps(objects: Dict[int, bytes], cmaps: Dict[int, Dict[int, str]]) -> Dict[str, Dict[int, str]]:
    font_resource_object = None
    for body in objects.values():
        if b"/Font" in body and b"/ExtGState" in body:
            font_match = re.search(rb"/Font\s+(\d+)\s+0\s+R", body)
            if font_match:
                font_resource_object = int(font_match.group(1))
                break

    if font_resource_object is None or font_resource_object not in objects:
        return {}

    resource_text = objects[font_resource_object].decode("latin1", errors="ignore")
    font_to_object = {
        name: int(obj_id)
        for name, obj_id in re.findall(r"/([A-Za-z0-9_.-]+)\s+(\d+)\s+0\s+R", resource_text)
    }

    result: Dict[str, Dict[int, str]] = {}
    for name, obj_id in font_to_object.items():
        font_body = objects.get(obj_id, b"").decode("latin1", errors="ignore")
        unicode_match = re.search(r"/ToUnicode\s+(\d+)\s+0\s+R", font_body)
        if unicode_match:
            cmap = cmaps.get(int(unicode_match.group(1)))
            if cmap:
                result[name] = cmap
    return result


def decode_hex_text(hex_text: str, cmap: Dict[int, str]) -> str:
    if not cmap:
        return bytes.fromhex(hex_text).decode("utf-16-be", errors="ignore")
    chars = []
    for index in range(0, len(hex_text), 4):
        try:
            code = int(hex_text[index : index + 4], 16)
        except ValueError:
            continue
        chars.append(cmap.get(code, ""))
    return "".join(chars)


def decode_literal_text(value: str) -> str:
    # Minimal literal string unescape. This intentionally avoids interpreting
    # arbitrary PDF syntax; it only makes common escaped text readable.
    value = value.replace(r"\(", "(").replace(r"\)", ")").replace(r"\\", "\\")
    return value.encode("latin1", errors="ignore").decode("utf-8", errors="ignore")


def extract_text_from_content_stream(stream: bytes, font_maps: Dict[str, Dict[int, str]]) -> List[str]:
    text = stream.decode("latin1", errors="ignore")
    current_font: Optional[str] = None
    lines: List[str] = []
    token_pattern = re.compile(
        r"/([A-Za-z0-9_.-]+)\s+[0-9.]+\s+Tf|\[(.*?)\]\s*TJ|<([0-9A-Fa-f]+)>\s*Tj|\((.*?)\)\s*Tj",
        re.S,
    )

    for match in token_pattern.finditer(text):
        if match.group(1):
            current_font = match.group(1)
            continue

        cmap = font_maps.get(current_font or "", {})
        line = ""
        if match.group(2) is not None:
            for hex_match in re.finditer(r"<([0-9A-Fa-f]+)>", match.group(2)):
                line += decode_hex_text(hex_match.group(1), cmap)
        elif match.group(3):
            line = decode_hex_text(match.group(3), cmap)
        elif match.group(4):
            line = decode_literal_text(match.group(4))

        line = re.sub(r"[ \t]+", " ", line).strip()
        if line:
            lines.append(line)
    return lines


def page_content_objects(objects: Dict[int, bytes]) -> Iterable[Tuple[int, int]]:
    pages: List[Tuple[int, int]] = []
    for object_id, body in objects.items():
        if b"/Type /Page" not in body or b"/Contents" not in body:
            continue
        content_match = re.search(rb"/Contents\s+(\d+)\s+0\s+R", body)
        if content_match:
            pages.append((object_id, int(content_match.group(1))))
    return sorted(pages)


def fallback_extract(pdf_path: str) -> str:
    with open(pdf_path, "rb") as handle:
        parsed = parse_pdf_objects(handle.read())

    font_maps = build_font_maps(parsed.objects, parse_cmaps(parsed.streams))
    page_chunks: List[str] = []

    for page_number, (_, content_object) in enumerate(page_content_objects(parsed.objects), start=1):
        stream = parsed.streams.get(content_object)
        if not stream:
            continue
        lines = extract_text_from_content_stream(stream, font_maps)
        if lines:
            page_chunks.append(f"--- PAGE {page_number} ---\n" + "\n".join(lines))

    if page_chunks:
        return "\n\n".join(page_chunks)

    # Last-resort plain strings extraction for simple PDFs.
    raw_strings = []
    with open(pdf_path, "rb") as handle:
        for match in re.finditer(rb"[\x20-\x7E]{4,}", handle.read()):
            raw_strings.append(match.group(0).decode("latin1", errors="ignore"))
    return "\n".join(raw_strings)


def readable_score(text: str) -> int:
    return sum(1 for char in text if char.isalnum())


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract readable text from a Jira PDF attachment.")
    parser.add_argument("pdf", help="Path to the PDF attachment")
    parser.add_argument("-o", "--output", help="Write extracted UTF-8 text to this file")
    args = parser.parse_args()

    if not os.path.exists(args.pdf):
        print(f"PDF not found: {args.pdf}", file=sys.stderr)
        return 2

    text = run_pdftotext(args.pdf)
    method = "pdftotext"
    if not text or readable_score(text) < MIN_READABLE_CHARS:
        text = fallback_extract(args.pdf)
        method = "python-fallback"

    if readable_score(text) < MIN_READABLE_CHARS:
        print(
            "No readable PDF text extracted; OCR/manual inspection required.",
            file=sys.stderr,
        )
        return 3

    text = text.rstrip() + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text)
    else:
        sys.stdout.write(text)

    print(f"PDF extraction method: {method}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
