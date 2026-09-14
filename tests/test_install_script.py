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
        fake_git.write_text(
            "#!/bin/sh\n"
            "printf '%s ' \"$@\" >> \"$GIT_LOG\"\n"
            "printf '\\n' >> \"$GIT_LOG\"\n"
            "if [ \"$1\" = clone ]; then\n"
            "  mkdir -p \"$3/.git\"\n"
            "fi\n"
        )
        fake_git.chmod(0o755)
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "PATH": f"{self.bin_dir}:/usr/bin:/bin",
            "GIT_LOG": str(self.git_log),
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

    def test_clones_central_root_and_links_skill_discovery(self) -> None:
        result = self.run_installer()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.home / ".agents/pdca/.git").is_dir())
        self.assertEqual(
            (self.home / ".agents/skills").resolve(),
            self.home / ".agents/pdca/skills",
        )
        self.assertIn(f"clone {REPOSITORY}", self.git_log.read_text())

    def test_refuses_an_existing_central_root_before_invoking_git(self) -> None:
        central_root = self.home / ".agents/pdca"
        central_root.mkdir(parents=True)

        result = self.run_installer()

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.git_log.exists())
        self.assertFalse((self.home / ".agents/skills").exists())

    def test_refuses_an_existing_discovery_path_before_invoking_git(self) -> None:
        skills_dir = self.home / ".agents/skills"
        skills_dir.mkdir(parents=True)

        result = self.run_installer()

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.git_log.exists())
        self.assertFalse((self.home / ".agents/pdca").exists())

    def test_refuses_when_git_is_unavailable_before_creating_paths(self) -> None:
        env = {**self.env, "PATH": str(self.base / "missing-bin")}

        result = self.run_installer(env)

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.home / ".agents").exists())


if __name__ == "__main__":
    unittest.main()
