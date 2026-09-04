from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

# seam 契约锚点：被测模块 scripts/arch_review.py（arch_review.py 为被测模块）
SEAM_TARGET = "scripts/arch_review.py"

from arch_review import render_html  # noqa: E402

CANDIDATES = [
    {
        "id": "c1",
        "title": "Deepen the flow-audit module",
        "files": ["scripts/flow_audit.py"],
        "problem": "Interface is as complex as the implementation",
        "solution": "Extract a deep audit engine behind one entry point",
        "benefits": "Locality and leverage improve; tests get a seam",
        "strength": "Strong",
    },
    {
        "id": "c2",
        "title": "Collapse duplicated step patterns",
        "files": ["ontology/process/flow-do.md", "ontology/process/flow-check.md"],
        "problem": "Same step text repeated",
        "solution": "One shared reference doc",
        "benefits": "Single source of truth",
        "strength": "Worth exploring",
    },
]

METRICS = {"candidates": 2, "strong": 1, "worth": 1, "speculative": 0, "top": "c1"}


class HtmlRenderTest(unittest.TestCase):
    def test_html_contains_required_sections(self) -> None:
        html = render_html(CANDIDATES, metrics=METRICS, title="Arch Review")
        for section in ("<head>", "candidate-card", "mermaid", "Metrics", "Top recommendation"):
            self.assertIn(section, html, f"missing section: {section}")

    def test_each_candidate_field_is_present(self) -> None:
        html = render_html(CANDIDATES, metrics=METRICS, title="Arch Review")
        self.assertIn("Deepen the flow-audit module", html)
        self.assertIn("scripts/flow_audit.py", html)
        self.assertIn("Strong", html)
        self.assertIn("Worth exploring", html)

    def test_metrics_block_is_machine_parseable(self) -> None:
        html = render_html(CANDIDATES, metrics=METRICS, title="Arch Review")
        match = re.search(r'id="metrics" data-metrics=\'(\{.*?\})\'', html)
        self.assertIsNotNone(match, "metrics data attribute missing")
        import json

        parsed = json.loads(match.group(1))
        self.assertEqual(2, parsed["candidates"])
        self.assertEqual("c1", parsed["top"])

    def test_empty_candidates_still_yields_valid_html(self) -> None:
        html = render_html([], metrics={"candidates": 0, "strong": 0, "worth": 0, "speculative": 0, "top": None}, title="Empty")
        self.assertIn("candidate-card", html)
        self.assertIn("Metrics", html)
        self.assertIn("Top recommendation", html)


if __name__ == "__main__":
    unittest.main()
