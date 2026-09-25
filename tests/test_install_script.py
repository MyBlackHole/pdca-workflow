"""Black-box checks for the one-command Git installer."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "install.sh"
REPOSITORY = "https://github.com/MyBlackHole/pdca-workflow.git"
RUNTIME_SKILLS = (
    "pdca", "pdca-assist", "pdca-plan", "pdca-do", "pdca-check", "pdca-act",
    "pdca-model", "pdca-implement", "pdca-verify",
)


class GitInstallerTests(unittest.TestCase):
    """Run the installer against isolated homes and a controllable Git binary."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="pdca-git-install-")
        self.base = Path(self.temp.name)
        self.home = self.base / "home"
        self.bin_dir = self.base / "bin"
        self.bin_dir.mkdir()
        self.git_log = self.base / "git.log"
        fake_git = self.bin_dir / "git"
        runtime_shell = " ".join(RUNTIME_SKILLS)
        fake_git.write_text(
            "#!/bin/sh\n"
            "printf '%s ' \"$@\" >> \"$GIT_LOG\"\n"
            "printf '\\n' >> \"$GIT_LOG\"\n"
            "if [ \"$1\" = clone ]; then\n"
            "  mkdir -p \"$3/.git\" \"$3/skills\"\n"
            f"  for skill in {runtime_shell}; do mkdir -p \"$3/skills/$skill\"; done\n"
            "  if [ \"$GIT_CREATE_SKILLS_DURING_CLONE\" = 1 ]; then\n"
            "    mkdir -p \"$HOME/.agents/skills\"\n"
            "    printf 'external\\n' > \"$HOME/.agents/skills/external-marker\"\n"
            "  fi\n"
            "  if [ \"$GIT_CREATE_SKILLS_LINK_DURING_CLONE\" = 1 ]; then\n"
            "    mkdir -p \"$HOME/.agents/external-skills\"\n"
            "    ln -s \"$HOME/.agents/external-skills\" \"$HOME/.agents/skills\"\n"
            "  fi\n"
            "  exit \"$GIT_CLONE_STATUS\"\n"
            "fi\n"
        )
        fake_git.chmod(0o755)
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "PATH": f"{self.bin_dir}:/usr/bin:/bin",
            "GIT_LOG": str(self.git_log),
            "GIT_CLONE_STATUS": "0",
            "GIT_CREATE_SKILLS_DURING_CLONE": "0",
            "GIT_CREATE_SKILLS_LINK_DURING_CLONE": "0",
        }

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_installer(self, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["/bin/sh", str(INSTALL)],
            cwd=ROOT,
            env=self.env if env is None else env,
            capture_output=True,
            text=True,
        )

    def assert_runtime_links(self) -> None:
        skills_dir = self.home / ".agents/skills"
        self.assertTrue(skills_dir.is_dir())
        for skill in RUNTIME_SKILLS:
            link = skills_dir / skill
            self.assertTrue(link.is_symlink(), skill)
            self.assertEqual(link.resolve(), self.home / f".agents/pdca/skills/{skill}")

    def test_clones_central_root_and_links_only_runtime_skills(self) -> None:
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.home / ".agents/pdca/.git").is_dir())
        self.assert_runtime_links()
        children = {path.name for path in (self.home / ".agents/skills").iterdir()}
        self.assertEqual(children, set(RUNTIME_SKILLS))
        self.assertNotIn("testing-strategy", children)
        self.assertNotIn("systematic-debugging", children)
        self.assertIn(f"clone {REPOSITORY}", self.git_log.read_text())

    def test_preserves_existing_unrelated_skill_directory(self) -> None:
        other = self.home / ".agents/skills/other-project"
        other.mkdir(parents=True)
        marker = other / "SKILL.md"
        marker.write_text("keep me")
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_runtime_links()
        self.assertEqual(marker.read_text(), "keep me")

    def test_refuses_an_existing_central_root_before_invoking_git(self) -> None:
        central_root = self.home / ".agents/pdca"
        central_root.mkdir(parents=True)
        result = self.run_installer()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.git_log.exists())

    def test_refuses_runtime_name_collision_before_invoking_git(self) -> None:
        collision = self.home / ".agents/skills/pdca-do"
        collision.mkdir(parents=True)
        result = self.run_installer()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.git_log.exists())
        self.assertTrue(collision.is_dir())

    def test_refuses_a_discovery_symlink_before_invoking_git(self) -> None:
        skills_dir = self.home / ".agents/skills"
        skills_dir.parent.mkdir(parents=True)
        external = self.base / "external-skills"
        external.mkdir()
        skills_dir.symlink_to(external, target_is_directory=True)
        result = self.run_installer()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.git_log.exists())
        self.assertTrue(skills_dir.is_symlink())
        self.assertFalse((self.home / ".agents/pdca").exists())

    def test_refuses_when_git_is_unavailable_before_creating_paths(self) -> None:
        env = {**self.env, "PATH": str(self.base / "missing-bin")}
        result = self.run_installer(env)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.home / ".agents").exists())

    def test_failed_clone_cleans_only_its_new_destination(self) -> None:
        existing = self.home / ".agents/skills/unrelated/keep.txt"
        existing.parent.mkdir(parents=True)
        existing.write_text("user data")
        result = self.run_installer({**self.env, "GIT_CLONE_STATUS": "7"})
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertFalse((self.home / ".agents/pdca").exists())
        self.assertEqual(existing.read_text(), "user data")
        self.assertEqual(
            {path.name for path in (self.home / ".agents/skills").iterdir()},
            {"unrelated"},
        )

    def test_refuses_discovery_directory_created_during_clone(self) -> None:
        result = self.run_installer(
            {**self.env, "GIT_CREATE_SKILLS_DURING_CLONE": "1"}
        )
        skills_dir = self.home / ".agents/skills"
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(skills_dir.is_dir())
        self.assertEqual((skills_dir / "external-marker").read_text(), "external\n")
        self.assertFalse((self.home / ".agents/pdca").exists())
        for skill in RUNTIME_SKILLS:
            self.assertFalse((skills_dir / skill).exists())

    def test_refuses_discovery_symlink_created_during_clone(self) -> None:
        result = self.run_installer(
            {**self.env, "GIT_CREATE_SKILLS_LINK_DURING_CLONE": "1"}
        )
        skills_dir = self.home / ".agents/skills"
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(skills_dir.is_symlink())
        self.assertEqual(skills_dir.resolve(), self.home / ".agents/external-skills")
        self.assertFalse((self.home / ".agents/pdca").exists())


if __name__ == "__main__":
    unittest.main()
