from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable


IGNORE_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    ".next",
    ".nuxt",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "vendor",
    "tmp",
    "__pycache__",
}

DEFAULT_EXTENSIONS = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".py",
    ".go",
    ".java",
    ".kt",
    ".swift",
    ".rb",
    ".rs",
    ".php",
    ".cs",
}


def collect_files(root: Path, extensions: set[str], max_file_size_bytes: int) -> list[Path]:
    return [
        path
        for path in walk_candidate_files(root)
        if is_scannable_source(path, extensions, max_file_size_bytes)
    ]


def walk_candidate_files(root: Path) -> Iterable[Path]:
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [dirname for dirname in dirnames if dirname not in IGNORE_DIRS]
        base = Path(current_root)
        yield from (base / filename for filename in filenames)


def is_scannable_source(path: Path, extensions: set[str], max_file_size_bytes: int) -> bool:
    try:
        return path.suffix in extensions and path.stat().st_size <= max_file_size_bytes
    except OSError:
        return False


def normalize_lines(path: Path) -> tuple[list[str], list[int]]:
    try:
        raw_lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return [], []

    in_block_comment = False
    normalized: list[str] = []
    line_numbers: list[int] = []

    for idx, raw in enumerate(raw_lines, start=1):
        maybe_line, in_block_comment = normalize_line(raw, in_block_comment)
        if maybe_line is None:
            continue
        normalized.append(maybe_line)
        line_numbers.append(idx)

    return normalized, line_numbers


def normalize_line(raw: str, in_block_comment: bool) -> tuple[str | None, bool]:
    text = raw.strip()
    if not text:
        return None, in_block_comment
    if in_block_comment:
        return None, "*/" not in text
    if text.startswith("/*"):
        return None, "*/" not in text
    if text.startswith(("//", "#")):
        return None, in_block_comment

    compact = " ".join(text.split())
    return (compact, in_block_comment) if len(compact) >= 2 else (None, in_block_comment)
