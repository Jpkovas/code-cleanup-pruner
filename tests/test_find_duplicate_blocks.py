from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "find_duplicate_blocks.py"


def write_source(path: Path, function_name: str) -> None:
    path.write_text(
        "\n".join(
            [
                f"def {function_name}(items):",
                "    total = 0",
                "    for item in items:",
                "        if item:",
                "            total += item",
                "    return total",
                "",
            ]
        ),
        encoding="utf-8",
    )


def run_duplicate_scan(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(root), *args],
        check=False,
        text=True,
        capture_output=True,
    )


class FindDuplicateBlocksTests(unittest.TestCase):
    def test_cli_reports_duplicate_blocks(self) -> None:
        with self.subTest("duplicate files are reported"):
            from tempfile import TemporaryDirectory

            with TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                write_source(root / "one.py", "sum_one")
                write_source(root / "two.py", "sum_two")

                result = run_duplicate_scan(root, "--min-lines", "5", "--min-chars", "20")

                self.assertEqual(result.returncode, 0)
                self.assertIn("Potential duplicate groups:", result.stdout)
                self.assertIn("one.py:", result.stdout)
                self.assertIn("two.py:", result.stdout)

    def test_cli_ignores_configured_directories(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_source(root / "one.py", "sum_one")
            ignored = root / "node_modules"
            ignored.mkdir()
            write_source(ignored / "two.py", "sum_two")

            result = run_duplicate_scan(root, "--min-lines", "5", "--min-chars", "20")

            self.assertEqual(result.returncode, 0)
            self.assertIn("No duplicate blocks found", result.stdout)
            self.assertNotIn("node_modules", result.stdout)

    def test_cli_respects_material_threshold(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_source(root / "one.py", "sum_one")
            write_source(root / "two.py", "sum_two")

            result = run_duplicate_scan(root, "--min-lines", "5", "--min-chars", "1000")

            self.assertEqual(result.returncode, 0)
            self.assertIn("No duplicate blocks found", result.stdout)

    def test_missing_root_fails_cleanly(self) -> None:
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as temp_dir:
            result = run_duplicate_scan(Path(temp_dir) / "missing")

        self.assertEqual(result.returncode, 1)
        self.assertIn("Root path not found:", result.stdout)


if __name__ == "__main__":
    unittest.main()
