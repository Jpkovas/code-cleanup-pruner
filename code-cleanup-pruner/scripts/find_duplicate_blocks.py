#!/usr/bin/env python3
"""
Report potential duplicate code blocks across source files.

The script uses normalized sliding windows of lines and reports repeated windows.
It is intentionally conservative and meant for triage, not automatic deletion.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


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


@dataclass(frozen=True)
class Occurrence:
    path: str
    line: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find potential duplicate code blocks.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root path.")
    parser.add_argument(
        "--min-lines",
        type=int,
        default=10,
        help="Minimum normalized lines per duplicate window (default: 10).",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=30,
        help="Maximum groups printed (default: 30).",
    )
    parser.add_argument(
        "--extensions",
        default=",".join(sorted(DEFAULT_EXTENSIONS)),
        help="Comma-separated file extensions to scan.",
    )
    parser.add_argument(
        "--max-file-size-kb",
        type=int,
        default=512,
        help="Skip files larger than this size in KB (default: 512).",
    )
    parser.add_argument(
        "--min-chars",
        type=int,
        default=60,
        help="Minimum normalized characters in each window (default: 60).",
    )
    return parser.parse_args()


def collect_files(root: Path, extensions: set[str], max_file_size_bytes: int) -> list[Path]:
    files: list[Path] = []
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        base = Path(current_root)
        for filename in filenames:
            path = base / filename
            if path.suffix not in extensions:
                continue
            try:
                if path.stat().st_size > max_file_size_bytes:
                    continue
            except OSError:
                continue
            files.append(path)
    return files


def normalize_lines(path: Path) -> tuple[list[str], list[int]]:
    try:
        raw_lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return [], []

    normalized: list[str] = []
    line_numbers: list[int] = []
    in_block_comment = False

    for idx, raw in enumerate(raw_lines, start=1):
        text = raw.strip()
        if not text:
            continue

        if in_block_comment:
            if "*/" in text:
                in_block_comment = False
            continue

        if text.startswith("/*"):
            if "*/" not in text:
                in_block_comment = True
            continue

        if text.startswith("//") or text.startswith("#"):
            continue

        compact = " ".join(text.split())
        if len(compact) < 2:
            continue

        normalized.append(compact)
        line_numbers.append(idx)

    return normalized, line_numbers


def window_hash(lines: list[str]) -> str:
    joined = "\n".join(lines).encode("utf-8", errors="ignore")
    return hashlib.sha1(joined).hexdigest()


def find_duplicates(
    files: list[Path], root: Path, min_lines: int, min_chars: int
) -> dict[str, list[Occurrence]]:
    matches: dict[str, list[Occurrence]] = defaultdict(list)

    for path in files:
        norm_lines, line_numbers = normalize_lines(path)
        if len(norm_lines) < min_lines:
            continue

        seen_in_file: set[tuple[str, int]] = set()
        for start in range(0, len(norm_lines) - min_lines + 1):
            window = norm_lines[start : start + min_lines]
            material = " ".join(window)
            if len(material) < min_chars:
                continue

            h = window_hash(window)
            start_line = line_numbers[start]
            key = (h, start_line)
            if key in seen_in_file:
                continue
            seen_in_file.add(key)

            rel = str(path.relative_to(root))
            matches[h].append(Occurrence(path=rel, line=start_line))

    return matches


def score_group(occurrences: list[Occurrence]) -> tuple[int, int]:
    distinct_files = len({o.path for o in occurrences})
    return (len(occurrences), distinct_files)


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        print(f"Root path not found: {root}")
        return 1

    extensions = {ext.strip() for ext in args.extensions.split(",") if ext.strip()}
    max_size = args.max_file_size_kb * 1024
    files = collect_files(root, extensions, max_size)

    if not files:
        print("No source files found for the selected extensions.")
        return 0

    groups = find_duplicates(files, root, args.min_lines, args.min_chars)
    filtered: list[tuple[str, list[Occurrence]]] = []

    for h, occurrences in groups.items():
        unique_locations = {(o.path, o.line) for o in occurrences}
        if len(unique_locations) < 2:
            continue
        filtered.append((h, sorted(unique_locations)))

    ranked = sorted(
        filtered,
        key=lambda item: score_group([Occurrence(path=p, line=l) for p, l in item[1]]),
        reverse=True,
    )

    if not ranked:
        print("No duplicate blocks found with current thresholds.")
        return 0

    print(
        f"Potential duplicate groups: {len(ranked)} "
        f"(showing up to {args.max_results}, min_lines={args.min_lines})"
    )

    for idx, (_hash, locations) in enumerate(ranked[: args.max_results], start=1):
        distinct_files = len({path for path, _line in locations})
        print(f"\n[{idx}] occurrences={len(locations)} distinct_files={distinct_files}")
        for path, line in locations[:12]:
            print(f"  - {path}:{line}")
        if len(locations) > 12:
            print(f"  - ... and {len(locations) - 12} more")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
