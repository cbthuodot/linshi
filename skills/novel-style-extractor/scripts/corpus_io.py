#!/usr/bin/env python3
"""Corpus loading and normalization helpers for Chinese fiction style analysis."""
from __future__ import annotations

import html
import io
import re
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Iterator
import xml.etree.ElementTree as ET

SUPPORTED = {".txt", ".md", ".markdown", ".docx"}
CHAPTER_RE = re.compile(
    r"^\s*(?:第\s*[零〇一二三四五六七八九十百千万两0-9]+\s*[章节回卷篇部]|"
    r"chapter\s+\d+|卷\s*[零〇一二三四五六七八九十百千万两0-9]+).*?$",
    re.IGNORECASE,
)

@dataclass
class SourceDoc:
    source: str
    text: str
    chars: int
    paragraphs: int

    def metadata(self) -> dict:
        data = asdict(self)
        data.pop("text", None)
        return data


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u3000", " ").replace("\ufeff", "")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def _decode_bytes(data: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "gb18030", "big5"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _read_docx_bytes(data: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        try:
            xml_data = zf.read("word/document.xml")
        except KeyError as exc:
            raise ValueError("Invalid DOCX: word/document.xml is missing") from exc
    root = ET.fromstring(xml_data)
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paragraphs: list[str] = []
    for p in root.iter(ns + "p"):
        parts: list[str] = []
        for node in p.iter():
            if node.tag == ns + "t" and node.text:
                parts.append(node.text)
            elif node.tag == ns + "tab":
                parts.append("\t")
            elif node.tag in {ns + "br", ns + "cr"}:
                parts.append("\n")
        paragraph = "".join(parts).strip()
        if paragraph:
            paragraphs.append(paragraph)
    return "\n\n".join(paragraphs)


def read_supported_bytes(name: str, data: bytes) -> str:
    suffix = Path(name).suffix.lower()
    if suffix == ".docx":
        return _read_docx_bytes(data)
    if suffix in {".txt", ".md", ".markdown"}:
        return _decode_bytes(data)
    raise ValueError(f"Unsupported file type: {suffix}")


def iter_inputs(source: Path) -> Iterator[tuple[str, bytes]]:
    if source.is_dir():
        for path in sorted(source.rglob("*")):
            if path.is_file() and path.suffix.lower() in SUPPORTED:
                yield str(path), path.read_bytes()
        return
    if source.suffix.lower() == ".zip":
        with zipfile.ZipFile(source) as zf:
            for info in sorted(zf.infolist(), key=lambda x: x.filename):
                if info.is_dir() or Path(info.filename).suffix.lower() not in SUPPORTED:
                    continue
                if info.file_size > 50 * 1024 * 1024:
                    raise ValueError(f"Archive member too large: {info.filename}")
                yield f"{source}!/{info.filename}", zf.read(info)
        return
    if source.is_file() and source.suffix.lower() in SUPPORTED:
        yield str(source), source.read_bytes()
        return
    raise ValueError(
        "Source must be a TXT/MD/DOCX file, a directory containing them, or a ZIP archive."
    )


def load_corpus(source: str | Path) -> list[SourceDoc]:
    src = Path(source).expanduser().resolve()
    docs: list[SourceDoc] = []
    for name, data in iter_inputs(src):
        text = normalize_text(read_supported_bytes(name, data))
        if not text:
            continue
        paragraphs = len([p for p in re.split(r"\n\s*\n|\n", text) if p.strip()])
        docs.append(SourceDoc(name, text, len(text), paragraphs))
    if not docs:
        raise ValueError("No supported non-empty text was found in the corpus.")
    return docs


def join_corpus(docs: Iterable[SourceDoc]) -> str:
    parts = []
    for doc in docs:
        parts.append(f"\n\n<<<SOURCE: {html.escape(doc.source)}>>>\n\n{doc.text}")
    return "".join(parts).strip()


def split_chapters(text: str) -> list[str]:
    lines = text.splitlines()
    chapters: list[list[str]] = []
    current: list[str] = []
    saw_heading = False
    for line in lines:
        if CHAPTER_RE.match(line.strip()):
            saw_heading = True
            if current:
                chapters.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        chapters.append(current)
    if not saw_heading:
        return [text]
    return [normalize_text("\n".join(c)) for c in chapters if normalize_text("\n".join(c))]
