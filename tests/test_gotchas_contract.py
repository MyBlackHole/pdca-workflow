"""Gotchas 段契约测试（T0267）。

断言全量正式 skill 含非空 gotchas 段，且核心 9 个 skill 的 gotchas 段含
真实来源引用（记录/归档 id，抽检目标目录存在）。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check-skill-structure.py"
SKILLS_DIR = ROOT / "ontology" / "domain" / "pdca"
PYTHON = sys.executable

GOTCHAS_HEADERS = ("## 已知坑", "## Gotchas")

CORE_SKILLS_SOURCES = {
    "triage-work": ["T0266"],
    "register-evidence": ["T0266"],
    "resolving-merge-conflicts": ["T0266"],
    "write-conclusion": ["T0265"],
    "advance-phase": ["T0265"],
    "write-journal": ["T0264"],
    "design-it-twice": ["T0266"],
    "to-tickets": ["T0265"],
    "wayfinding-work": ["T0265"],
}


def gotchas_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    for h in GOTCHAS_HEADERS:
        idx = text.find(h)
        if idx != -1:
            return text[idx:]
    return ""


def scan_payload() -> dict:
    r = subprocess.run(
        [PYTHON, str(SCRIPT), "--dir", str(SKILLS_DIR), "--json"],
        capture_output=True, text=True,
    )
    assert r.returncode in (0, 1, 2), r.stderr
    return __import__("json").loads(r.stdout)


def test_core_skills_gotchas_reference_sources():
    for skill, tokens in CORE_SKILLS_SOURCES.items():
        p = SKILLS_DIR / f"skill-{skill}.md"
        assert p.exists(), f"缺 {skill}/SKILL.md"
        body = gotchas_body(p)
        assert body, f"{skill} 缺 gotchas 段"
        for t in tokens:
            assert t in body, f"{skill} gotchas 段缺来源引用 {t}"


def test_core_skills_source_targets_exist():
    import json
    import re

    records = ROOT / "records"
    archive = ROOT / "pdca" / "tasks" / "archive" / "2026-08"
    for skill in CORE_SKILLS_SOURCES:
        p = SKILLS_DIR / f"skill-{skill}.md"
        body = gotchas_body(p)
        targets = re.findall(r"T02\d\d", body)
        assert targets, f"{skill} gotchas 段无记录 id 引用"
        for t in targets:
            record_match = any(r.name.startswith(t) for r in records.iterdir())
            archive_match = any(
                (a / "task.json").exists()
                and json.loads((a / "task.json").read_text()).get("id") == t
                for a in archive.iterdir()
            )
            assert record_match or archive_match, f"{skill} 引用 {t} 不存在"


def test_all_gotchas_headers_non_empty():
    payload = scan_payload()
    assert payload["error_count"] == 0, "全量 gotchas 契约存在错误（见 check-skill-structure 输出）"
    for skill in payload["skills"]:
        codes = {e["code"] for e in skill["errors"]}
        assert "GOTCHAS_MISSING" not in codes, f"{skill['name']} 缺 gotchas 段"
        assert "GOTCHAS_EMPTY" not in codes, f"{skill['name']} gotchas 段为空"


def test_drafts_excluded_from_scan():
    """drafts 草稿区不参与扫描。"""
    payload = scan_payload()
    names = {s["name"] for s in payload["skills"]}
    assert "drafts" not in names
    assert not any("/drafts/" in s["path"] for s in payload["skills"])
