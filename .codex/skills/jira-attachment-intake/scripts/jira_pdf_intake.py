#!/usr/bin/env python3
"""Extract text from Jira PDF attachments for Codex Jira intake."""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen


DEFAULT_OUT = "/tmp/codex-jira-attachments"
DEFAULT_TOKEN_ENV = "JIRA_PERSONAL_TOKEN"
DEFAULT_URL_ENV = "JIRA_BASE_URL"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract Jira PDF attachment text with pypdf."
    )
    parser.add_argument("issue_key", help="Jira issue key, for example DCECSS-3320")
    parser.add_argument(
        "--out",
        default=DEFAULT_OUT,
        help=f"Output root directory. Default: {DEFAULT_OUT}",
    )
    parser.add_argument(
        "--file",
        action="append",
        default=[],
        help="Local PDF file to extract. Can be provided multiple times.",
    )
    parser.add_argument(
        "--base64-file",
        action="append",
        default=[],
        help=(
            "File containing a base64 PDF blob, or JSON with a resource.blob/blob field. "
            "Can be provided multiple times."
        ),
    )
    parser.add_argument(
        "--base64-stdin",
        action="store_true",
        help="Read a base64 PDF blob, or JSON with a resource.blob/blob field, from stdin.",
    )
    parser.add_argument(
        "--mcp-json",
        action="append",
        default=[],
        help=(
            "Jira MCP JSON output containing embedded attachment resources. "
            "Can be a single object or a list of MCP content items."
        ),
    )
    parser.add_argument(
        "--attachment-url",
        action="append",
        default=[],
        help=(
            "Jira PDF attachment URL to download and extract without emitting a base64 blob. "
            "Can be provided multiple times."
        ),
    )
    parser.add_argument(
        "--jira-url",
        default=None,
        help=f"Jira base URL. Defaults to ${DEFAULT_URL_ENV} or Codex MCP config.",
    )
    parser.add_argument(
        "--token-env",
        default=DEFAULT_TOKEN_ENV,
        help=f"Environment variable containing the Jira personal token. Default: {DEFAULT_TOKEN_ENV}",
    )
    parser.add_argument(
        "--codex-config",
        default=None,
        help=(
            "Codex config TOML to read Jira URL/token headers from when env vars are absent. "
            "Use only Codex-owned config; token values are never printed."
        ),
    )
    parser.add_argument(
        "--auth-header",
        choices=("bearer", "jira-personal-token"),
        default="bearer",
        help="HTTP auth header style for --attachment-url downloads. Default: bearer.",
    )
    return parser.parse_args()


def decode_base64_pdf(value: str, source: str) -> bytes:
    candidate = value.strip()
    if candidate.startswith("data:"):
        _, _, candidate = candidate.partition(",")
    candidate = re.sub(r"\s+", "", candidate)
    try:
        data = base64.b64decode(candidate, validate=True)
    except binascii.Error as exc:
        raise SystemExit(f"Invalid base64 PDF data in {source}: {exc}") from exc
    if not data.startswith(b"%PDF"):
        raise SystemExit(f"Decoded data from {source} is not a PDF.")
    return data


def blob_items_from_json(payload: Any) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []

    def visit(value: Any) -> None:
        if isinstance(value, list):
            for item in value:
                visit(item)
            return
        if not isinstance(value, dict):
            return

        resource = value.get("resource")
        if isinstance(resource, dict) and isinstance(resource.get("blob"), str):
            uri = str(resource.get("uri") or "attachment.pdf")
            mime = str(resource.get("mimeType") or resource.get("mime_type") or "")
            if uri.lower().endswith(".pdf") or mime.lower() == "application/pdf":
                items.append({"filename": Path(uri).name or "attachment.pdf", "blob": resource["blob"]})

        if isinstance(value.get("blob"), str):
            filename = str(value.get("filename") or value.get("name") or value.get("uri") or "attachment.pdf")
            mime = str(value.get("mimeType") or value.get("mime_type") or "")
            if filename.lower().endswith(".pdf") or mime.lower() == "application/pdf":
                items.append({"filename": Path(filename).name or "attachment.pdf", "blob": value["blob"]})

        for key in ("content", "contents", "attachments", "resources", "result"):
            if key in value:
                visit(value[key])

    visit(payload)
    return items


def read_blob_items(raw: str, source: str, fallback_filename: str) -> list[dict[str, str]]:
    stripped = raw.strip()
    if not stripped:
        raise SystemExit(f"No base64 or JSON data found in {source}.")
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON in {source}: {exc}") from exc
        items = blob_items_from_json(payload)
        if not items:
            raise SystemExit(f"No embedded PDF resource blob found in {source}.")
        return items
    return [{"filename": fallback_filename, "blob": stripped}]


def safe_filename(name: str, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip())
    cleaned = cleaned.strip("._")
    return cleaned or fallback


def load_codex_config(path: str | None) -> dict[str, str]:
    config_path = Path(path).expanduser() if path else Path.home() / ".codex" / "config.toml"
    if not config_path.exists():
        return {}
    try:
        import tomllib
    except ImportError:
        return {}

    try:
        data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    atlassian = (
        data.get("mcp_servers", {})
        .get("atlassian", {})
    )
    headers = atlassian.get("headers", {}) if isinstance(atlassian, dict) else {}
    result: dict[str, str] = {}
    token = headers.get("X-Atlassian-Jira-Personal-Token")
    jira_url = headers.get("X-Atlassian-Jira-Url")
    if isinstance(token, str) and token:
        result["token"] = token
    if isinstance(jira_url, str) and jira_url:
        result["jira_url"] = jira_url
    return result


def attachment_filename(url: str, index: int) -> str:
    path_name = Path(unquote(urlparse(url).path)).name
    filename = safe_filename(path_name, f"attachment-{index}.pdf")
    if not filename.lower().endswith(".pdf"):
        filename = f"{filename}.pdf"
    return filename


def resolve_jira_auth(args: argparse.Namespace) -> tuple[str | None, str | None]:
    config = load_codex_config(args.codex_config)
    token = os.environ.get(args.token_env) or config.get("token")
    jira_url = args.jira_url or os.environ.get(DEFAULT_URL_ENV) or config.get("jira_url")
    return token, jira_url


def normalize_attachment_url(url: str, jira_url: str | None) -> str:
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc:
        return url
    if not jira_url:
        raise SystemExit("Relative attachment URL requires --jira-url, JIRA_BASE_URL, or Codex config Jira URL.")
    return jira_url.rstrip("/") + "/" + url.lstrip("/")


def download_attachment(url: str, issue_dir: Path, index: int, token: str | None, jira_url: str | None, auth_header: str) -> Path:
    if not token:
        raise SystemExit(
            "Missing Jira token for --attachment-url. Set JIRA_PERSONAL_TOKEN, pass --token-env, "
            "or pass --codex-config pointing at Codex-owned MCP config."
        )
    full_url = normalize_attachment_url(url, jira_url)
    pdf_path = issue_dir / attachment_filename(full_url, index)
    headers = {"Accept": "application/pdf"}
    if auth_header == "bearer":
        headers["Authorization"] = f"Bearer {token}"
    else:
        headers["X-Atlassian-Jira-Personal-Token"] = token

    request = Request(full_url, headers=headers)
    try:
        with urlopen(request, timeout=60) as response:
            data = response.read()
    except HTTPError as exc:
        raise SystemExit(f"Failed to download attachment {pdf_path.name}: HTTP {exc.code}") from exc
    except URLError as exc:
        raise SystemExit(f"Failed to download attachment {pdf_path.name}: {exc.reason}") from exc

    if not data.startswith(b"%PDF"):
        raise SystemExit(f"Downloaded data for {pdf_path.name} is not a PDF.")
    pdf_path.write_bytes(data)
    return pdf_path


def extract_text(pdf_path: Path) -> tuple[str, int]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise SystemExit(
            "Missing Python package 'pypdf'. Install it or use an environment that provides it."
        ) from exc

    reader = PdfReader(str(pdf_path))
    parts: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            parts.append(f"\n\n--- page {index} ---\n{text.strip()}")
    return "".join(parts).strip() + ("\n" if parts else ""), len(reader.pages)


def process_pdf(pdf_path: Path) -> dict[str, Any]:
    text_path = pdf_path.with_suffix(".txt")
    text, page_count = extract_text(pdf_path)
    text_path.write_text(text, encoding="utf-8")
    return {
        "pdf": str(pdf_path),
        "text": str(text_path),
        "pages": page_count,
        "status": "ok" if text.strip() else "no_text",
        "chars": len(text),
    }


def write_embedded_pdf(
    issue_dir: Path, blob: str, filename: str, index: int, source: str
) -> Path:
    safe_name = safe_filename(filename, f"embedded-{index}.pdf")
    if not safe_name.lower().endswith(".pdf"):
        safe_name = f"{safe_name}.pdf"
    pdf_path = issue_dir / safe_name
    pdf_path.write_bytes(decode_base64_pdf(blob, source))
    return pdf_path


def main() -> int:
    args = parse_args()
    issue_dir = Path(args.out).expanduser() / safe_filename(args.issue_key, "issue")
    issue_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    local_files: list[Path] = []
    if args.attachment_url:
        token, jira_url = resolve_jira_auth(args)
        for index, url in enumerate(args.attachment_url, start=1):
            local_files.append(
                download_attachment(url, issue_dir, index, token, jira_url, args.auth_header)
            )

    for index, path in enumerate(args.file, start=1):
        source = Path(path).expanduser()
        if not source.exists():
            raise SystemExit(f"PDF file does not exist: {source}")
        filename = safe_filename(source.name, f"local-{index}.pdf")
        if not filename.lower().endswith(".pdf"):
            filename = f"{filename}.pdf"
        copied = issue_dir / filename
        if source.resolve() != copied.resolve():
            shutil.copyfile(source, copied)
        local_files.append(copied)

    embedded_items: list[tuple[str, dict[str, str]]] = []
    for path in args.base64_file:
        source = Path(path).expanduser()
        if not source.exists():
            raise SystemExit(f"Base64 file does not exist: {source}")
        embedded_items.extend(
            (str(source), item)
            for item in read_blob_items(source.read_text(encoding="utf-8"), str(source), source.name)
        )

    for path in args.mcp_json:
        source = Path(path).expanduser()
        if not source.exists():
            raise SystemExit(f"MCP JSON file does not exist: {source}")
        embedded_items.extend(
            (str(source), item)
            for item in read_blob_items(source.read_text(encoding="utf-8"), str(source), "attachment.pdf")
        )

    if args.base64_stdin:
        embedded_items.extend(
            ("stdin", item)
            for item in read_blob_items(sys.stdin.read(), "stdin", "stdin.pdf")
        )

    for index, (source, item) in enumerate(embedded_items, start=1):
        local_files.append(
            write_embedded_pdf(
                issue_dir,
                item["blob"],
                item.get("filename") or f"embedded-{index}.pdf",
                index,
                source,
            )
        )

    if not local_files:
        print(
            json.dumps(
                {
                    "issue": args.issue_key,
                    "output_dir": str(issue_dir),
                    "status": "no_pdf_attachments",
                    "files": [],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    for pdf_path in local_files:
        if not pdf_path.exists():
            raise SystemExit(f"PDF file does not exist: {pdf_path}")
        results.append(process_pdf(pdf_path))

    print(
        json.dumps(
            {
                "issue": args.issue_key,
                "output_dir": str(issue_dir),
                "status": "ok",
                "files": results,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
