"""T0272 self-audit 聚合诊断脚本测试。"""

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts/self-audit.py"


def run(*args):
    return subprocess.run(
        ["python3", str(SCRIPT), "--root", str(ROOT), *args],
        capture_output=True,
        text=True,
    )


class SelfAuditTest(unittest.TestCase):
    def test_json_output_structure(self):
        r = run("--json")
        self.assertEqual(0, r.returncode, r.stderr)
        d = json.loads(r.stdout)
        self.assertEqual("pdca.self-audit/v1", d["schema"])
        self.assertIn("summary", d)
        self.assertIn("gate_coverage", d)
        self.assertIn("issues", d)
        self.assertIn("candidates", d)

    def test_four_categories_covered(self):
        r = run("--json")
        d = json.loads(r.stdout)
        cats = set(d["summary"]["by_category"].keys())
        self.assertTrue(
            {"id_collision", "schema", "seam"}.issubset(cats),
            f"缺少核心类别: {cats}",
        )
        self.assertGreaterEqual(d["summary"]["by_category"].get("id_collision", 0), 1)

    def test_severity_grading(self):
        r = run("--json")
        d = json.loads(r.stdout)
        sev = set(d["summary"]["by_severity"].keys())
        self.assertTrue(sev.issubset({"blocking", "integrity", "noise"}))
        self.assertGreaterEqual(d["summary"]["by_severity"]["blocking"], 1)

    def test_root_cause_classification(self):
        r = run("--json")
        d = json.loads(r.stdout)
        roots = set(d["summary"]["by_root_cause"].keys())
        self.assertTrue(roots.issubset({"legacy", "external-project", "real-defect"}))
        seam_external = [
            i for i in d["issues"]
            if i["category"] == "seam" and i["root_cause"] == "external-project"
        ]
        self.assertTrue(seam_external, "round 系列 seam 缺失应归 external-project")

    def test_gate_coverage_present(self):
        r = run("--json")
        d = json.loads(r.stdout)
        g = d["gate_coverage"]
        self.assertGreater(g["total"], 0)
        self.assertGreaterEqual(g["receipts_pct"], 0)

    def test_candidates_not_empty_and_scoped(self):
        r = run("--json")
        d = json.loads(r.stdout)
        self.assertTrue(d["candidates"], "应输出修复候选清单")
        for c in d["candidates"]:
            self.assertTrue(c["title"])
            self.assertTrue(c["basis"])
            self.assertTrue(c["scope"])
            self.assertIn(c["priority"], {"high", "medium", "low"})

    def test_reproducible_digest(self):
        r1 = run("--json")
        d1 = json.loads(r1.stdout)
        r2 = run("--json")
        d2 = json.loads(r2.stdout)
        self.assertEqual(r1.stdout, r2.stdout)

    def test_markdown_report_rendered(self):
        out = ROOT / "records" / "T0272-0815-self-audit" / "health-audit.md"
        r = run("--out", str(out))
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertTrue(out.exists())
        content = out.read_text(encoding="utf-8")
        self.assertIn("# PDCA 体系健康度自我审查报告", content)
        self.assertIn("修复候选清单", content)

    def test_seam_task_id_resolved(self):
        r = run("--json")
        d = json.loads(r.stdout)
        seams = [i for i in d["issues"] if i["category"] == "seam"]
        for s in seams:
            self.assertTrue(s["task_id"].startswith("T"), f"seam task_id 应为 T 开头: {s['task_id']}")


if __name__ == "__main__":
    unittest.main()
