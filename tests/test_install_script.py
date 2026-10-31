"""Black-box tests for install.sh filesystem effects and rollback behavior."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "install.sh"
REMOTE = "https://github.com/MyBlackHole/pdca-workflow.git"
CATALOG = json.loads((ROOT / "skills/catalog.json").read_text(encoding="utf-8"))
RUNTIME_SKILLS = tuple(entry["name"] for entry in CATALOG["skills"])
REFERENCE_SKILL = next(
    (
        path
        for path in sorted((ROOT / "skills").iterdir())
        if path.is_dir() and path.name not in RUNTIME_SKILLS
    ),
    None,
)
REAL_GIT = shutil.which("git")
REAL_LN = shutil.which("ln")


def workspace_tmpdir() -> Path:
    """Resolve TMPDIR only when it points inside this checkout's tests tree."""
    configured = os.environ.get("TMPDIR", "")
    if not configured or not Path(configured).is_absolute():
        raise RuntimeError("Set TMPDIR to an absolute directory under the workspace tests/ before running tests")
    tests_root = (ROOT / "tests").resolve(strict=True)
    temp_root = Path(configured).resolve(strict=True)
    if temp_root != tests_root and tests_root not in temp_root.parents:
        raise RuntimeError(f"TMPDIR must resolve inside {tests_root}, got {temp_root}")
    return temp_root


def setUpModule() -> None:
    # Fail before any test fixture can fall back to the interpreter's default.
    workspace_tmpdir()


class WorkspaceTempDirectoryPolicyTests(unittest.TestCase):
    """Require callers to route tempfile users into the repository tests tree."""

    def test_tmpdir_is_inside_workspace_tests(self) -> None:
        tests_root = (ROOT / "tests").resolve(strict=True)
        temp_root = workspace_tmpdir()
        self.assertTrue(temp_root == tests_root or tests_root in temp_root.parents)


class InstallScriptTests(unittest.TestCase):
    """Exercise the production installer with an isolated HOME and local Git source."""

    def fixture_environment(self) -> dict[str, str]:
        return {
            "HOME": str(self.home),
            "PATH": os.defpath,
            "TMPDIR": str(self.base),
            "GIT_CONFIG_GLOBAL": str(self.git_config),
            "GIT_CONFIG_NOSYSTEM": "1",
        }

    def commit_source(self, message: str) -> None:
        env = self.fixture_environment()
        subprocess.run(
            [REAL_GIT, "-C", str(self.source), "add", "skills"],
            check=True,
            env=env,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [
                REAL_GIT,
                "-C",
                str(self.source),
                "-c",
                "user.name=PDCA installer test",
                "-c",
                "user.email=pdca-installer-test@example.invalid",
                "commit",
                "--quiet",
                "-m",
                message,
            ],
            check=True,
            env=env,
            capture_output=True,
            text=True,
        )

    def setUp(self) -> None:
        if REAL_GIT is None or REAL_LN is None:
            self.fail("git and ln are required to exercise the production installer")

        temp_root = workspace_tmpdir()
        self.temp = tempfile.TemporaryDirectory(prefix="pdca-install-test-", dir=temp_root)
        self.base = Path(self.temp.name)
        self.home = self.base / "home"
        self.home.mkdir()
        self.source = self.base / "source"
        self.source.mkdir()
        self.git_config = self.base / "gitconfig"
        self.git_config.write_text("", encoding="utf-8")
        self.call_log = self.base / "git-calls.log"
        self.bin_dir = self.base / "bin"
        self.bin_dir.mkdir()

        subprocess.run(
            [REAL_GIT, "init", "--quiet", "-b", "main", str(self.source)],
            check=True,
            env=self.fixture_environment(),
            capture_output=True,
            text=True,
        )
        for entry in CATALOG["skills"]:
            source_skill = ROOT / entry["path"]
            fixture_skill = self.source / Path(entry["path"]).parent
            fixture_skill.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source_skill.parent, fixture_skill)

        # Include one non-runtime skill when the source checkout has one.
        if REFERENCE_SKILL is not None:
            shutil.copytree(REFERENCE_SKILL, self.source / "skills" / REFERENCE_SKILL.name)

        self.commit_source("fixture")
        self.git_config.write_text(
            f'[url "{self.source.as_uri()}"]\n'
            f"\tinsteadOf = {REMOTE}\n",
            encoding="utf-8",
        )
        self.env = {
            "HOME": str(self.home),
            "PATH": os.pathsep.join((str(self.bin_dir), str(Path(REAL_GIT).parent), os.defpath)),
            "TMPDIR": str(self.base),
            "GIT_CONFIG_GLOBAL": str(self.git_config),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_CALL_LOG": str(self.call_log),
            "REAL_GIT": REAL_GIT,
            "REAL_LN": REAL_LN,
            "FAIL_BEFORE_CLONE": "0",
            "FAIL_AFTER_CLONE": "0",
            "ADD_COLLISION_DURING_CLONE": "0",
            "REPLACE_DISCOVERY_DURING_CLONE": "0",
            "LN_COLLISION_SKILL": "",
            "LN_REPLACE_REGISTERED_SKILL": "",
            "EXTERNAL_DISCOVERY": str(self.base / "external-skills"),
        }

    def tearDown(self) -> None:
        self.temp.cleanup()

    def install(self, *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["/bin/sh", str(INSTALL)],
            cwd=ROOT,
            env=self.env if env is None else env,
            capture_output=True,
            text=True,
        )

    def install_with_git_wrapper(self) -> None:
        wrapper = self.bin_dir / "git"
        wrapper.write_text(
            "#!/bin/sh\n"
            "printf '%s\\n' \"$*\" >>\"$GIT_CALL_LOG\"\n"
            "if [ \"$1\" = clone ] && [ \"$FAIL_BEFORE_CLONE\" = 1 ]; then exit 7; fi\n"
            "\"$REAL_GIT\" \"$@\"\n"
            "result=$?\n"
            "if [ \"$1\" = clone ] && [ \"$result\" -eq 0 ] && [ \"$ADD_COLLISION_DURING_CLONE\" = 1 ]; then\n"
            "  printf 'concurrent entry\\n' >\"$HOME/.agents/skills/pdca-do\"\n"
            "fi\n"
            "if [ \"$1\" = clone ] && [ \"$result\" -eq 0 ] && [ \"$REPLACE_DISCOVERY_DURING_CLONE\" = 1 ]; then\n"
            "  mv \"$HOME/.agents/skills\" \"$HOME/.agents/skills-original\" || exit 24\n"
            "  ln -s \"$EXTERNAL_DISCOVERY\" \"$HOME/.agents/skills\" || exit 25\n"
            "fi\n"
            "if [ \"$1\" = clone ] && [ \"$FAIL_AFTER_CLONE\" = 1 ] && [ \"$result\" -eq 0 ]; then\n"
            "  exit 23\n"
            "fi\n"
            "exit \"$result\"\n",
            encoding="utf-8",
        )
        wrapper.chmod(0o755)

    def install_with_link_collision_wrapper(self) -> None:
        wrapper = self.bin_dir / "ln"
        wrapper.write_text(
            "#!/bin/sh\n"
            "target_skill=${2##*/}\n"
            "if [ \"$1\" = -s ] && [ \"$target_skill\" = \"$LN_COLLISION_SKILL\" ]; then\n"
            "  if [ -n \"$LN_REPLACE_REGISTERED_SKILL\" ]; then\n"
            "    replacement=\"$HOME/.agents/skills/.replacement-link\"\n"
            "    destination=\"$HOME/.agents/skills/$LN_REPLACE_REGISTERED_SKILL\"\n"
            "    \"$REAL_LN\" -s \"$HOME/.agents/pdca/skills/$LN_REPLACE_REGISTERED_SKILL\" \"$replacement\" || exit 27\n"
            "    python3 -c 'import os,sys; os.replace(sys.argv[1], sys.argv[2])' \"$replacement\" \"$destination\" || exit 28\n"
            "  fi\n"
            "  skill=${2##*/}\n"
            "  directory=\"$HOME/.agents/skills/$skill\"\n"
            "  mkdir \"$directory\" || exit 26\n"
            "  printf 'concurrent directory entry\\n' >\"$directory/keep.txt\"\n"
            "fi\n"
            "exec \"$REAL_LN\" \"$@\"\n",
            encoding="utf-8",
        )
        wrapper.chmod(0o755)

    def install_with_term_wrapper(self) -> None:
        wrapper = self.bin_dir / "ln"
        wrapper.write_text(
            "#!/bin/sh\n"
            "target_skill=${2##*/}\n"
            "if [ \"$1\" = -s ] && [ \"$target_skill\" = \"$LN_TERM_SKILL\" ]; then\n"
            "  kill -TERM \"$PPID\"\n"
            "  exit 0\n"
            "fi\n"
            "exec \"$REAL_LN\" \"$@\"\n",
            encoding="utf-8",
        )
        wrapper.chmod(0o755)

    def assert_runtime_links(self) -> None:
        discovery = self.home / ".agents/skills"
        self.assertTrue(discovery.is_dir())
        for skill in RUNTIME_SKILLS:
            link = discovery / skill
            self.assertTrue(link.is_symlink(), skill)
            self.assertEqual(
                os.readlink(link),
                str(self.home / f".agents/pdca/skills/{skill}"),
            )
            self.assertEqual(link.resolve(), self.home / f".agents/pdca/skills/{skill}")

    def test_installs_central_checkout_and_catalogued_links(self) -> None:
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.home / ".agents/pdca/.git").is_dir())
        self.assert_runtime_links()
        installed_names = {p.name for p in (self.home / ".agents/skills").iterdir()}
        self.assertEqual(installed_names, set(RUNTIME_SKILLS))
        if REFERENCE_SKILL is not None:
            self.assertNotIn(REFERENCE_SKILL.name, installed_names)

    def test_reuses_existing_plain_discovery_directory_without_losing_other_entries(self) -> None:
        marker = self.home / ".agents/skills/other-project/SKILL.md"
        marker.parent.mkdir(parents=True)
        marker.write_text("preserve this entry\n", encoding="utf-8")

        result = self.install()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_runtime_links()
        self.assertEqual(marker.read_text(encoding="utf-8"), "preserve this entry\n")

    def test_refuses_existing_central_root_without_replacing_contents(self) -> None:
        marker = self.home / ".agents/pdca/keep.txt"
        marker.parent.mkdir(parents=True)
        marker.write_text("existing checkout\n", encoding="utf-8")
        self.install_with_git_wrapper()

        result = self.install()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("central root already exists", result.stderr)
        self.assertEqual(marker.read_text(encoding="utf-8"), "existing checkout\n")
        self.assertFalse(self.call_log.exists())

    def test_refuses_runtime_name_collision_before_cloning(self) -> None:
        collision = self.home / ".agents/skills/pdca-do"
        collision.parent.mkdir(parents=True)
        collision.write_text("user entry\n", encoding="utf-8")
        self.install_with_git_wrapper()

        result = self.install()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Runtime skill path already exists", result.stderr)
        self.assertEqual(collision.read_text(encoding="utf-8"), "user entry\n")
        self.assertFalse((self.home / ".agents/pdca").exists())
        self.assertFalse(self.call_log.exists())

    def test_refuses_discovery_symlink_without_touching_its_target(self) -> None:
        external = self.base / "external-skills"
        external.mkdir()
        marker = external / "keep.txt"
        marker.write_text("external entry\n", encoding="utf-8")
        agents = self.home / ".agents"
        agents.mkdir()
        discovery = agents / "skills"
        discovery.symlink_to(external, target_is_directory=True)
        self.install_with_git_wrapper()

        result = self.install()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Not a plain directory", result.stderr)
        self.assertTrue(discovery.is_symlink())
        self.assertEqual(marker.read_text(encoding="utf-8"), "external entry\n")
        self.assertFalse((agents / "pdca").exists())
        self.assertFalse(self.call_log.exists())

    def test_refuses_agents_symlink_without_writing_through_it(self) -> None:
        external = self.base / "external-agents"
        external.mkdir()
        agents = self.home / ".agents"
        agents.symlink_to(external, target_is_directory=True)
        self.install_with_git_wrapper()

        result = self.install()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing symlink", result.stderr)
        self.assertTrue(agents.is_symlink())
        self.assertEqual(list(external.iterdir()), [])
        self.assertFalse(self.call_log.exists())

    def test_requires_git_before_creating_agent_paths(self) -> None:
        missing_path = self.base / "missing-bin"
        missing_path.mkdir()
        result = self.install(env={**self.env, "PATH": str(missing_path)})

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.home / ".agents").exists())

    def test_failed_clone_retains_nonempty_checkout_and_preserves_other_entries(self) -> None:
        marker = self.home / ".agents/skills/other-project/keep.txt"
        marker.parent.mkdir(parents=True)
        marker.write_text("user data\n", encoding="utf-8")
        self.install_with_git_wrapper()

        result = self.install(env={**self.env, "FAIL_AFTER_CLONE": "1"})

        self.assertEqual(result.returncode, 23, result.stderr)
        self.assertTrue((self.home / ".agents/pdca/.git").is_dir())
        self.assertIn("Retained checkout for inspection", result.stderr)
        self.assertEqual(marker.read_text(encoding="utf-8"), "user data\n")
        self.assertEqual(
            {p.name for p in (self.home / ".agents/skills").iterdir()},
            {"other-project"},
        )

    def test_failed_clone_before_creating_checkout_removes_empty_owned_directories(self) -> None:
        self.install_with_git_wrapper()

        result = self.install(env={**self.env, "FAIL_BEFORE_CLONE": "1"})

        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertFalse((self.home / ".agents/pdca").exists())
        self.assertFalse((self.home / ".agents/skills").exists())
        agents = self.home / ".agents"
        self.assertTrue(agents.is_dir())
        self.assertEqual(list(agents.iterdir()), [])
        self.assertIn("clone", self.call_log.read_text(encoding="utf-8"))

    def test_collision_added_during_clone_is_preserved_before_linking(self) -> None:
        self.install_with_git_wrapper()

        result = self.install(env={**self.env, "ADD_COLLISION_DURING_CLONE": "1"})

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Runtime skill path appeared during installation", result.stderr)
        discovery = self.home / ".agents/skills"
        self.assertEqual({p.name for p in discovery.iterdir()}, {"pdca-do"})
        self.assertEqual(
            (discovery / "pdca-do").read_text(encoding="utf-8"),
            "concurrent entry\n",
        )
        self.assertTrue((self.home / ".agents/pdca/.git").is_dir())

    def test_directory_appearing_after_preflight_is_not_used_as_link_destination(self) -> None:
        self.install_with_link_collision_wrapper()

        result = self.install(env={**self.env, "LN_COLLISION_SKILL": "pdca"})

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unconfirmed link operation", result.stderr)
        collision = self.home / ".agents/skills/pdca"
        self.assertEqual(
            (collision / "keep.txt").read_text(encoding="utf-8"),
            "concurrent directory entry\n",
        )
        self.assertFalse((collision / "pdca").exists() or (collision / "pdca").is_symlink())
        self.assertEqual({p.name for p in (self.home / ".agents/skills").iterdir()}, {"pdca"})
        self.assertTrue((self.home / ".agents/pdca/.git").is_dir())

    def test_later_link_collision_removes_earlier_links_and_preserves_collision(self) -> None:
        self.install_with_link_collision_wrapper()

        result = self.install(env={**self.env, "LN_COLLISION_SKILL": "pdca-assist"})

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unconfirmed link operation; inspect entry: pdca-assist", result.stderr)
        self.assertFalse((self.home / ".agents/skills/pdca").exists())
        collision = self.home / ".agents/skills/pdca-assist"
        self.assertEqual(
            (collision / "keep.txt").read_text(encoding="utf-8"),
            "concurrent directory entry\n",
        )
        self.assertEqual({p.name for p in (self.home / ".agents/skills").iterdir()}, {"pdca-assist"})
        self.assertTrue((self.home / ".agents/pdca/.git").is_dir())

    def test_rollback_preserves_replaced_link_even_when_target_is_unchanged(self) -> None:
        self.install_with_link_collision_wrapper()

        result = self.install(
            env={
                **self.env,
                "LN_COLLISION_SKILL": "pdca-assist",
                "LN_REPLACE_REGISTERED_SKILL": "pdca",
            }
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Retained changed entry (not owned by this rollback): pdca", result.stderr)
        self.assertIn("Unconfirmed link operation; inspect entry: pdca-assist", result.stderr)
        replacement = self.home / ".agents/skills/pdca"
        self.assertTrue(replacement.is_symlink())
        self.assertEqual(
            os.readlink(replacement),
            str(self.home / ".agents/pdca/skills/pdca"),
        )
        self.assertTrue((self.home / ".agents/skills/pdca-assist/keep.txt").is_file())
        self.assertTrue((self.home / ".agents/pdca/.git").is_dir())

    def test_term_during_later_link_rolls_back_owned_links_and_retains_checkout(self) -> None:
        self.install_with_term_wrapper()
        process = subprocess.Popen(
            ["/bin/sh", str(INSTALL)],
            cwd=ROOT,
            env={**self.env, "LN_TERM_SKILL": "pdca-assist"},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            self.fail(f"installer did not stop after TERM; stdout={stdout!r}, stderr={stderr!r}")

        self.assertEqual(process.returncode, 143, f"stdout={stdout!r}, stderr={stderr!r}")
        self.assertIn("Unconfirmed link operation; inspect entry: pdca-assist", stderr)
        self.assertFalse((self.home / ".agents/skills").exists())
        self.assertTrue((self.home / ".agents/pdca/.git").is_dir())
        self.assertIn("Retained checkout for inspection", stderr)

    def test_discovery_directory_replacement_during_clone_is_not_followed(self) -> None:
        external = self.base / "external-skills"
        external.mkdir()
        marker = external / "keep.txt"
        marker.write_text("external data\n", encoding="utf-8")
        self.install_with_git_wrapper()

        result = self.install(
            env={
                **self.env,
                "REPLACE_DISCOVERY_DURING_CLONE": "1",
                "EXTERNAL_DISCOVERY": str(external),
            }
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Installation directory identity changed", result.stderr)
        discovery = self.home / ".agents/skills"
        self.assertTrue(discovery.is_symlink())
        self.assertEqual(os.readlink(discovery), str(external))
        self.assertEqual(marker.read_text(encoding="utf-8"), "external data\n")
        self.assertEqual(list(external.iterdir()), [marker])
        self.assertTrue((self.home / ".agents/skills-original").is_dir())
        self.assertTrue((self.home / ".agents/pdca/.git").is_dir())

    def test_rejects_invalid_checkout_without_publishing_links(self) -> None:
        skill_file = self.source / "skills/pdca/SKILL.md"
        skill_file.unlink()
        skill_file.symlink_to("missing-skill.md")
        self.commit_source("invalid skill fixture")

        result = self.install()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid checkout: require a readable, nonempty regular entry", result.stderr)
        self.assertTrue((self.home / ".agents/pdca/.git").is_dir())
        discovery = self.home / ".agents/skills"
        self.assertFalse(discovery.exists() or discovery.is_symlink())

    def test_rejects_runtime_skill_directory_symlink_in_checkout(self) -> None:
        external_skill = self.base / "external-skill"
        external_skill.mkdir()
        (external_skill / "SKILL.md").write_text("valid external skill\n", encoding="utf-8")
        runtime_skill = self.source / "skills/pdca"
        shutil.rmtree(runtime_skill)
        runtime_skill.symlink_to(external_skill, target_is_directory=True)
        self.commit_source("runtime skill directory symlink fixture")

        result = self.install()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid checkout: require a readable, nonempty regular entry", result.stderr)
        self.assertTrue((self.home / ".agents/pdca/.git").is_dir())
        discovery = self.home / ".agents/skills"
        self.assertFalse(discovery.exists() or discovery.is_symlink())


if __name__ == "__main__":
    unittest.main()
