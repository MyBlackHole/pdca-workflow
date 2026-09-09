"""research强制网络查询门禁回归测试（T2081）。

口径：research-report参考资料≥2 URL，且正文Source:行至少1条httpURL，否则阻断。
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check-research-web-evidence.py"


def run_gate(report: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--report", str(report)],
        capture_output=True, text=True,
    )


class ResearchWebEvidenceTest(unittest.TestCase):
    def _write(self, tmp: Path, text: str) -> Path:
        p = tmp / "research-report.md"
        p.write_text(text, encoding="utf-8")
        return p

    def test_missing_url_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = self._write(Path(td), "# R\n\nSource: 本地文件 file:line\n")
            r = run_gate(p)
            self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_satisfied_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            text = (
                "# R\n\nSource: https://example.com/a\n\n"
                "## 参考资料\n- https://example.com/a\n- https://example.com/b\n"
            )
            p = self._write(Path(td), text)
            r = run_gate(p)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_single_url_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            text = "# R\n\nSource: https://example.com/a\n\n## 参考资料\n- https://example.com/a\n"
            p = self._write(Path(td), text)
            r = run_gate(p)
            self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
