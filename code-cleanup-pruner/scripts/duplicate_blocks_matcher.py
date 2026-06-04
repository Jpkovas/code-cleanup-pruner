from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from duplicate_blocks_files import normalize_lines


@dataclass(frozen=True)
class Occurrence:
    path: str
    line: int


@dataclass(frozen=True)
class DuplicateGroup:
    locations: list[Occurrence]

    @property
    def occurrence_count(self) -> int:
        return len(self.locations)

    @property
    def distinct_file_count(self) -> int:
        return len({occurrence.path for occurrence in self.locations})


def window_hash(lines: list[str]) -> str:
    joined = "\n".join(lines).encode("utf-8", errors="ignore")
    return hashlib.sha1(joined).hexdigest()


def find_duplicates(
    files: list[Path], root: Path, min_lines: int, min_chars: int
) -> dict[str, list[Occurrence]]:
    matches: dict[str, list[Occurrence]] = defaultdict(list)
    for path in files:
        for block_hash, occurrence in duplicate_windows_for_file(path, root, min_lines, min_chars):
            matches[block_hash].append(occurrence)
    return matches


def duplicate_windows_for_file(
    path: Path, root: Path, min_lines: int, min_chars: int
) -> Iterable[tuple[str, Occurrence]]:
    norm_lines, line_numbers = normalize_lines(path)
    seen_in_file: set[tuple[str, int]] = set()
    rel = str(path.relative_to(root))

    for start, window in enumerate(windows(norm_lines, min_lines)):
        if len(" ".join(window)) < min_chars:
            continue

        block_hash = window_hash(window)
        start_line = line_numbers[start]
        key = (block_hash, start_line)
        if key in seen_in_file:
            continue

        seen_in_file.add(key)
        yield block_hash, Occurrence(path=rel, line=start_line)


def windows(lines: list[str], size: int) -> Iterable[list[str]]:
    stop = max(0, len(lines) - size + 1)
    return (lines[start : start + size] for start in range(stop))


def ranked_duplicate_groups(matches: dict[str, list[Occurrence]]) -> list[DuplicateGroup]:
    groups = [
        DuplicateGroup(sorted(set(occurrences), key=occurrence_key))
        for occurrences in matches.values()
        if len(set(occurrences)) >= 2
    ]
    return sorted(groups, key=score_group, reverse=True)


def occurrence_key(occurrence: Occurrence) -> tuple[str, int]:
    return occurrence.path, occurrence.line


def score_group(group: DuplicateGroup) -> tuple[int, int]:
    return (group.occurrence_count, group.distinct_file_count)
