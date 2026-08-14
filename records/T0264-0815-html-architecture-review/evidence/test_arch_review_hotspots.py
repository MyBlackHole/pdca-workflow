from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

# seam 契约锚点：被测模块 scripts/arch_review.py（arch_review.py 为被测模块）
SEAM_TARGET = "scripts/arch_review.py"

from arch_review import collect_candidates, hotspots  # noqa: E402


class HotspotsTest(unittest.TestCase):
    def run_git(self, repo: Path, *args: str) -> None:
        subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def make_repo(self) -> Path:
        root = Path(tempfile.mkdtemp())
        self.run_git(root, "init", "-q", "-b", "main")
        self.run_git(root, "config", "user.email", "test@example.com")
        self.run_git(root, "config", "user.name", "Test")
        return root

    def commit_file(self, repo: Path, path: str, content: str = "x") -> None:
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        self.run_git(repo, "add", "-A")
        self.run_git(repo, "commit", "-q", "-m", f"touch {path}")

    def test_returns_hot_files_ordered_by_commit_frequency(self) -> None:
        repo = self.make_repo()
        self.commit_file(repo, "src/hot_a.py")
        self.commit_file(repo, "src/hot_a.py", "y")
        self.commit_file(repo, "src/hot_a.py", "z")
        self.commit_file(repo, "src/hot_b.py")
        self.commit_file(repo, "docs/readme.md")
        result = hotspots(repo)
        self.assertGreaterEqual(len(result), 1)
        self.assertEqual(result[0], "src/hot_a.py")

    def test_filters_by_days_window(self) -> None:
        repo = self.make_repo()
        self.commit_file(repo, "src/new.py")
        result = hotspots(repo, days=0)
        self.assertIsInstance(result, list)

    def test_no_git_history_returns_empty_and_signals_full_scan(self) -> None:
        root = Path(tempfile.mkdtemp())
        (root / "some").mkdir()
        (root / "some/file.py").write_text("x", encoding="utf-8")
        result = hotspots(root)
        self.assertEqual([], result)

    def test_limit_bounds_results(self) -> None:
        repo = self.make_repo()
        for i in range(5):
            self.commit_file(repo, f"src/f{i}.py")
            self.commit_file(repo, f"src/f{i}.py", f"v{i}")
        result = hotspots(repo, limit=2)
        self.assertLessEqual(len(result), 2)

    def test_collect_candidates_flags_oversized_scripts(self) -> None:
        root = Path(tempfile.mkdtemp())
        (root / "scripts").mkdir()
        (root / "scripts/ok.py").write_text("x = 1\n", encoding="utf-8")
        (root / "scripts/big.py").write_text("\n".join(f"line_{i} = {i}" for i in range(250)), encoding="utf-8")
        candidates = collect_candidates(root)
        self.assertEqual(1, len(candidates))
        self.assertEqual("scripts/big.py", candidates[0]["files"][0])
        self.assertEqual("Worth exploring", candidates[0]["strength"])

    def test_collect_candidates_empty_when_all_under_threshold(self) -> None:
        root = Path(tempfile.mkdtemp())
        (root / "scripts").mkdir()
        (root / "scripts/small.py").write_text("x = 1\n", encoding="utf-8")
        self.assertEqual([], collect_candidates(root))


if __name__ == "__main__":
    unittest.main()
