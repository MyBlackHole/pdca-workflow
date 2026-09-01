from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_clash_module():
    spec = importlib.util.spec_from_file_location(
        "ontology_clash_check", ROOT / "scripts" / "ontology-clash-check.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_ont = _load_clash_module()
find_clashes = _ont.find_clashes


class OntologyClashCheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "ontology" / "concept").mkdir(parents=True)
        (self.root / "ontology" / "concept" / "tls-configuration.md").write_text(
            "---\nid: ontology:concept/tls-configuration\n---\n# tls-configuration\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_clash_detected_for_existing_node(self) -> None:
        report = find_clashes(self.root, ["tls-configuration", "0829-unrelated-task"])
        self.assertEqual(report["tls-configuration"], ["ontology:concept/tls-configuration"])
        self.assertEqual(report["0829-unrelated-task"], [])

    def test_clash_detected_for_date_prefixed_slug(self) -> None:
        report = find_clashes(self.root, ["0829-tls-configuration"])
        self.assertEqual(report["0829-tls-configuration"], ["ontology:concept/tls-configuration"])

    def test_cli_reports_clash(self) -> None:
        completed = subprocess_run(
            [
                "python3",
                str(ROOT / "scripts" / "ontology-clash-check.py"),
                str(self.root),
                "--candidates",
                "tls-configuration",
            ]
        )
        # clash 时为阻断门禁，exit 1
        self.assertEqual(1, completed.returncode, completed.stderr)
        report = json.loads(completed.stdout.splitlines()[-1])
        self.assertEqual(report["tls-configuration"], ["ontology:concept/tls-configuration"])


def subprocess_run(args: list[str]):
    import subprocess

    return subprocess.run(args, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
