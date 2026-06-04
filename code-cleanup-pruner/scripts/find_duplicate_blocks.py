#!/usr/bin/env python3
"""
Report potential duplicate code blocks across source files.

The script uses normalized sliding windows of lines and reports repeated windows.
It is intentionally conservative and meant for triage, not automatic deletion.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from duplicate_blocks_files import DEFAULT_EXTENSIONS, collect_files
from duplicate_blocks_matcher import find_duplicates, ranked_duplicate_groups
from duplicate_blocks_report import print_duplicate_report


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


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        print(f"Root path not found: {root}")
        return 1

    extensions = {ext.strip() for ext in args.extensions.split(",") if ext.strip()}
    files = collect_files(root, extensions, args.max_file_size_kb * 1024)
    if not files:
        print("No source files found for the selected extensions.")
        return 0

    matches = find_duplicates(files, root, args.min_lines, args.min_chars)
    groups = ranked_duplicate_groups(matches)
    if not groups:
        print("No duplicate blocks found with current thresholds.")
        return 0

    print_duplicate_report(groups, args.max_results, args.min_lines)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
