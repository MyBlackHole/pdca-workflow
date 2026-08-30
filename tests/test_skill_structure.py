"""skill 结构契约检查器测试（T0267）。

通过 subprocess 真实调用 `scripts/check-skill-structure.py`（与 out-of-scope
测试同模式），断言违规 fixture 报告、退出码行为与全量正式 skill 无结构错误。
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check-skill-structure.py"
SKILLS_DIR = ROOT / "skills"
PYTHON = sys.executable


def run_checker(skills_root: Path, exit_code: bool = False) -> subprocess.CompletedProcess:
    cmd = [PYTHON, str(SCRIPT), "--dir", str(skills_root), "--json"]
    if exit_code:
        cmd.append("--exit-code")
    return subprocess.run(cmd, capture_output=True, text=True)


def make_skill(root: Path, name: str, frontmatter: str, body: str = "") -> Path:
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    p = d / "SKILL.md"
    p.write_text(f"---\n{frontmatter}\n---\n\n{body}", encoding="utf-8")
    return p


GOOD_FM = "name: fixture-skill\ndescription: 使用规则生成。当需要规范时触发。"
GOOD_BODY = """# Fixture

## 已知坑

占位坑内容，至少二十字以满足非空判断且包含足够长度。
"""


def test_valid_skill_no_errors(tmp_path):
    make_skill(tmp_path, "fixture-skill", GOOD_FM, GOOD_BODY)
    r = run_checker(tmp_path)
    payload = json.loads(r.stdout)
    assert payload["error_count"] == 0, r.stdout


def test_bad_name_reported(tmp_path):
    make_skill(tmp_path, "fixture-skill", "name: Bad.Name\ndescription: 使用规则生成。", GOOD_BODY)
    r = run_checker(tmp_path)
    payload = json.loads(r.stdout)
    codes = {e["code"] for e in payload["skills"][0]["errors"]}
    assert "NAME_FORMAT" in codes


def test_long_name_reported(tmp_path):
    make_skill(tmp_path, "fixture-skill", f"name: {'x'*65}\ndescription: 使用规则生成。", GOOD_BODY)
    r = run_checker(tmp_path)
    payload = json.loads(r.stdout)
    codes = {e["code"] for e in payload["skills"][0]["errors"]}
    assert "NAME_LENGTH" in codes


def test_long_description_reported(tmp_path):
    make_skill(tmp_path, "fixture-skill", f"name: fixture-skill\ndescription: {'长'*1100}", GOOD_BODY)
    r = run_checker(tmp_path)
    payload = json.loads(r.stdout)
    codes = {e["code"] for e in payload["skills"][0]["errors"]}
    assert "DESC_LENGTH" in codes


def test_xml_in_name_reported(tmp_path):
    make_skill(tmp_path, "fixture-skill", 'name: "<evil>"\ndescription: 使用规则生成。', GOOD_BODY)
    r = run_checker(tmp_path)
    payload = json.loads(r.stdout)
    codes = {e["code"] for e in payload["skills"][0]["errors"]}
    assert "NAME_XML" in codes


def test_windows_path_reported(tmp_path):
    body = "# F\n\nC:\\Users\\black\\repo\n\n## 已知坑\n\n占位坑内容，至少二十字满足非空。\n"
    make_skill(tmp_path, "fixture-skill", GOOD_FM, body)
    r = run_checker(tmp_path)
    payload = json.loads(r.stdout)
    codes = {e["code"] for e in payload["skills"][0]["errors"]}
    assert "WINDOWS_PATH" in codes


def test_overlong_file_reported(tmp_path):
    p = make_skill(tmp_path, "fixture-skill", GOOD_FM, GOOD_BODY)
    p.write_text(p.read_text() + "\n# filler\n" * 600, encoding="utf-8")
    r = run_checker(tmp_path)
    payload = json.loads(r.stdout)
    codes = {e["code"] for e in payload["skills"][0]["errors"]}
    assert "LINES" in codes


def test_missing_gotchas_reported(tmp_path):
    make_skill(tmp_path, "fixture-skill", GOOD_FM, "# Fixture\n")
    r = run_checker(tmp_path)
    payload = json.loads(r.stdout)
    codes = {e["code"] for e in payload["skills"][0]["errors"]}
    assert "GOTCHAS_MISSING" in codes


def test_empty_gotchas_reported(tmp_path):
    make_skill(tmp_path, "fixture-skill", GOOD_FM, "# Fixture\n\n## 已知坑\n")
    r = run_checker(tmp_path)
    payload = json.loads(r.stdout)
    codes = {e["code"] for e in payload["skills"][0]["errors"]}
    assert "GOTCHAS_EMPTY" in codes


def test_person_warning_reported(tmp_path):
    make_skill(tmp_path, "fixture-skill", "name: fixture-skill\ndescription: 根据你的描述推荐入口。", GOOD_BODY)
    r = run_checker(tmp_path)
    payload = json.loads(r.stdout)
    codes = {e["code"] for e in payload["skills"][0]["warnings"]}
    assert "DESC_PERSON" in codes


def test_error_exit_code(tmp_path):
    make_skill(tmp_path, "fixture-skill", "name: Bad.Name\ndescription: 使用规则生成。", "# F\n")
    r = run_checker(tmp_path)
    assert r.returncode == 1


def test_warning_default_does_not_block(tmp_path):
    make_skill(tmp_path, "fixture-skill", "name: fixture-skill\ndescription: 根据你的描述推荐入口。", GOOD_BODY)
    r = run_checker(tmp_path)
    assert r.returncode == 0


def test_warning_blocks_with_exit_code_flag(tmp_path):
    make_skill(tmp_path, "fixture-skill", "name: fixture-skill\ndescription: 根据你的描述推荐入口。", GOOD_BODY)
    r = run_checker(tmp_path, exit_code=True)
    assert r.returncode == 2


def test_all_official_skills_pass_structure_contract():
    """全量正式 skill（ontology/domain/*/SKILL.md）无结构契约 error。"""
    r = run_checker(SKILLS_DIR)
    payload = json.loads(r.stdout)
    assert len(payload["skills"]) >= 39, f"期望 >=39 个正式 skill，实得 {len(payload['skills'])}"
    assert payload["error_count"] == 0, r.stdout
