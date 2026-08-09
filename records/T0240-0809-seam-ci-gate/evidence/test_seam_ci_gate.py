"""seam 契约仓库级门禁测试。

证明目标（AC-1..AC-5）：scripts/check-seam-contracts.py 扫描活跃任务 spec
并批量校验 seam 声明；全通过退出 0，存在失败退出非 0；归档任务不扫描。

同构先例：T0233 seam 契约（单任务 P6 门禁）+ T0240 将其提升为仓库级门禁。
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _scaffold(root: Path) -> tuple[Path, Path]:
    """构造最小仓库：一个含 seam 的活跃 spec + 对应测试文件。"""
    task_dir = root / "pdca/tasks/0809-fixture"
    task_dir.mkdir(parents=True)
    (root / "flows/flow-plan").mkdir(parents=True)
    (root / "flows/flow-plan/SKILL.md").write_text("# plan\n", encoding="utf-8")
    tests_dir = root / "tests"
    tests_dir.mkdir()
    (task_dir / "prd.md").write_text(
        "# PRD\n\n### 声明的测试接缝\n\n- seam: tests/test_fixture.py -> src/fixture.py\n",
        encoding="utf-8",
    )
    (tests_dir / "test_fixture.py").write_text(
        "from src.fixture import hello\n",
        encoding="utf-8",
    )
    return task_dir / "prd.md", tests_dir / "test_fixture.py"


class CheckSeamContractsTest(unittest.TestCase):
    def test_find_active_specs_excludes_archive(self) -> None:
        module = _load_module("check_seam_contracts", ROOT / "scripts/check-seam-contracts.py")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            active = root / "pdca/tasks/0809-fixture"
            archived = root / "pdca/tasks/archive/2026-08/0809-old"
            active.mkdir(parents=True)
            archived.mkdir(parents=True)
            seam = "### 声明的测试接缝\n- seam: tests/test_x.py -> src/x.py\n"
            (active / "prd.md").write_text(seam, encoding="utf-8")
            (archived / "prd.md").write_text(seam, encoding="utf-8")
            specs = module.find_active_specs(root)
            self.assertEqual(len(specs), 1)
            self.assertIn("0809-fixture", str(specs[0]))
            self.assertNotIn("archive", str(specs[0]))

    def test_spec_without_seam_not_checked(self) -> None:
        module = _load_module("check_seam_contracts", ROOT / "scripts/check-seam-contracts.py")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            task_dir = root / "pdca/tasks/0809-noseam"
            task_dir.mkdir(parents=True)
            (task_dir / "prd.md").write_text("# PRD\n\n无 seam 声明。\n", encoding="utf-8")
            self.assertEqual(module.find_active_specs(root), [])

    def test_clean_scan_returns_valid(self) -> None:
        module = _load_module("check_seam_contracts", ROOT / "scripts/check-seam-contracts.py")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            spec_path, _ = _scaffold(root)
            issues_per_spec, clean = module.check_all([spec_path], root)
            self.assertEqual(issues_per_spec, {})
            self.assertEqual(clean, [str(spec_path)])

    def test_broken_seam_reported(self) -> None:
        module = _load_module("check_seam_contracts", ROOT / "scripts/check-seam-contracts.py")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            spec_path, test_path = _scaffold(root)
            test_path.unlink()
            issues_per_spec, _ = module.check_all([spec_path], root)
            self.assertIn(str(spec_path), issues_per_spec)
            self.assertTrue(any("测试文件缺失" in i for i in issues_per_spec[str(spec_path)]))

    def test_exit_code_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            spec_path, _ = _scaffold(root)
            base = [sys.executable, str(ROOT / "scripts/check-seam-contracts.py"), "--root", str(root)]
            clean_run = subprocess.run(base, capture_output=True, text=True)
            self.assertEqual(0, clean_run.returncode)
            self.assertEqual(True, json.loads(clean_run.stdout)["valid"])

            (root / "pdca/tasks/0809-fixture/prd.md").write_text(
                "# PRD\n\n### 声明的测试接缝\n\n- seam: tests/missing_test.py -> src/fixture.py\n",
                encoding="utf-8",
            )
            broken_run = subprocess.run(base, capture_output=True, text=True)
            self.assertNotEqual(0, broken_run.returncode)
            self.assertEqual(False, json.loads(broken_run.stdout)["valid"])


if __name__ == "__main__":
    unittest.main()
