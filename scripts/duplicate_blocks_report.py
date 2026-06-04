from __future__ import annotations

from duplicate_blocks_matcher import DuplicateGroup


def print_duplicate_report(groups: list[DuplicateGroup], max_results: int, min_lines: int) -> None:
    print(
        f"Potential duplicate groups: {len(groups)} "
        f"(showing up to {max_results}, min_lines={min_lines})"
    )

    for idx, group in enumerate(groups[:max_results], start=1):
        print(f"\n[{idx}] occurrences={group.occurrence_count} distinct_files={group.distinct_file_count}")
        for occurrence in group.locations[:12]:
            print(f"  - {occurrence.path}:{occurrence.line}")
        if len(group.locations) > 12:
            print(f"  - ... and {len(group.locations) - 12} more")
