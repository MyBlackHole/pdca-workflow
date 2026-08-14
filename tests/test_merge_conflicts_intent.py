from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MERGE_SKILL = ROOT / "skills" / "resolving-merge-conflicts" / "SKILL.md"


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed: {result.stderr}")
    return result.stdout


def git_allow_failure(repo: Path, *args: str) -> subprocess.CompletedProcess:
    """允许非零返回码（如 merge 产生冲突返回 1）。"""
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
    )


class MergeConflictIntentFixtureTest(unittest.TestCase):
    """intent-based 冲突解析的真实 git fixture（T0266 增量 2）。

    构造一次真实 merge 冲突，按 intent-based 规则解析：
    找 primary source（历史 commit）→ 保留双方意图 → 绝不 abort → 无残留标记。
    """

    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.repo = Path(self._temp.name)
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.repo)], check=True)
        git(self.repo, "config", "user.email", "test@example.com")
        git(self.repo, "config", "user.name", "Test")

    def tearDown(self) -> None:
        self._temp.cleanup()

    def make_conflict(self) -> None:
        """main 上有 base config；feature 分支改为 8080，main 改为 3000。"""
        (self.repo / "config.txt").write_text("port=80\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "base: default port 80")
        git(self.repo, "checkout", "-qb", "feature")
        (self.repo / "config.txt").write_text("port=8080\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "feature: use port 8080 (primary source)")
        git(self.repo, "checkout", "-q", "main")
        (self.repo / "config.txt").write_text("port=3000\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "main: use port 3000")
        merged = git_allow_failure(self.repo, "merge", "feature")  # 产生冲突（返回 1）

    def test_merge_fixture_produces_real_conflict(self) -> None:
        self.make_conflict()
        status = git(self.repo, "status", "--porcelain")
        self.assertIn("UU", status, "fixture must produce a real merge conflict")

    def test_resolve_preserves_both_intents_and_never_aborts(self) -> None:
        self.make_conflict()
        conflicted = git(self.repo, "diff", "--name-only", "--diff-filter=U").split()
        self.assertTrue(conflicted)

        for filename in conflicted:
            content = (self.repo / filename).read_text(encoding="utf-8")
            has_ours = "port=3000" in content
            has_theirs = "port=8080" in content
            # intent-based：找 primary source（feature 8080），但 main 的 3000 也要记录
            resolved = f"port=8080\n# merged: main wanted port=3000 (ours), feature port=8080 (theirs)\n"
            if has_ours and has_theirs:
                (self.repo / filename).write_text(resolved, encoding="utf-8")
                git(self.repo, "add", filename)

        diff_check = subprocess.run(
            ["git", "-C", str(self.repo), "diff", "--check"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, diff_check.returncode, "no leftover conflict markers after resolution")
        git(self.repo, "commit", "-qm", "resolve conflict preserving both intents")
        merged = (self.repo / "config.txt").read_text(encoding="utf-8")
        self.assertIn("port=8080", merged, "theirs intent preserved")
        self.assertIn("main wanted port=3000", merged, "ours intent recorded")

    def test_skill_document_contains_intent_contracts(self) -> None:
        text = MERGE_SKILL.read_text(encoding="utf-8")
        for marker in ("primary source", "preserve both intents", "--abort", "automated checks", "typecheck"):
            self.assertIn(marker, text, f"merge skill missing intent marker: {marker}")


if __name__ == "__main__":
    unittest.main()
