#!/usr/bin/env python3
"""PDCA skill 结构契约检查器（T0267）。

对 `skills/*/SKILL.md` 全量执行结构契约检查，融合 Anthropic skill authoring
best practices 与 agentskills.io 规范（pedronauck validate-metadata.py 同源）。

硬错误（exit-code 非 0）：
  - name 契约：长度 1-64；仅 `^[a-z0-9]+(-[a-z0-9]+)*$`；无 XML 标记
  - description 契约：长度 1-1024；无 XML 标记
  - 体积契约：SKILL.md <= 500 行；无 Windows 路径（反斜杠引用）
  - gotchas 契约：含非空 `## 已知坑` 或 `## Gotchas` 段

软警告（报告但不阻塞 exit-code）：
  - description 含第一/二人称词（应为第三人称命令式）
  - description 缺触发词（面向模型 invocation 的触发语）
  - 流程类步骤缺显式完成准则（completion criterion 启发式）

用法：
  check-skill-structure.py                     # 全量检查，违规时退出码 1
  check-skill-structure.py --dir skills        # 指定目录
  check-skill-structure.py --exit-code         # 违规/警告均返回非 0（供 CI 强校验）
  check-skill-structure.py --json              # 输出 JSON 报告
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

MAX_NAME_LEN = 64
MAX_DESC_LEN = 1024
MAX_LINES = 500

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
XML_RE = re.compile(r"<[a-zA-Z/][^>]*>")
INSTRUCTION_XML_RE = re.compile(
    r"<(/?)(?:thinking|instructions|system|assistant|human|tool|output|claude|anthropic|role)[^>]*>"
)
WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:[\\/]")
FIRST_PERSON = {"i", "me", "my", "we", "our", "you", "your"}
FIRST_PERSON_ZH = {"你", "您", "我", "我们", "你们", "你的", "您的", "我的", "我们的"}
TRIGGER_RE = re.compile(r"当|使用|用于|when|use |using|按|根据|生成|绘制|将|在\S{0,6}时")
GOTCHAS_HEADERS = ("## 已知坑", "## Gotchas")
COMPLETION_HINTS = ("完成标准", "completion criterion", "检查完成", "判定", "如何验证", "验收")


@dataclass
class Issue:
    level: str  # "error" | "warning"
    code: str
    message: str


@dataclass
class SkillReport:
    path: Path
    name: str
    issues: list[Issue] = field(default_factory=list)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "warning"]


def extract_frontmatter(text: str) -> dict[str, str]:
    """解析 YAML frontmatter 的 name/description（支持块标量 |）。"""
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    body = m.group(1)
    fields: dict[str, str] = {}
    name_m = re.search(r"^name:\s*(.+)$", body, re.M)
    if name_m:
        fields["name"] = name_m.group(1).strip()
    desc_m = re.search(r"^description:\s*(.*)$", body, re.M)
    if desc_m:
        raw = desc_m.group(1).strip()
        if raw == "|":
            rest = body[desc_m.end():]
            lines: list[str] = []
            for ln in rest.splitlines():
                if ln.startswith(("  ", "\t")):
                    lines.append(ln.strip())
                elif not ln.strip() and not lines:
                    continue
                elif not lines:
                    continue
                else:
                    break
            fields["description"] = " ".join(lines)
        else:
            fields["description"] = raw
    return fields


def check_skill(path: Path) -> SkillReport:
    report = SkillReport(path=path, name=path.parent.name)
    text = path.read_text(encoding="utf-8")
    fm = extract_frontmatter(text)
    name = fm.get("name", "")
    desc = fm.get("description", "")

    if not name:
        report.issues.append(Issue("error", "NAME_MISSING", "frontmatter 缺 name"))
    else:
        if not (1 <= len(name) <= MAX_NAME_LEN):
            report.issues.append(
                Issue("error", "NAME_LENGTH", f"name 长度 {len(name)}，须 1-{MAX_NAME_LEN}"))
        if not NAME_RE.match(name):
            report.issues.append(
                Issue("error", "NAME_FORMAT",
                      f"name '{name}' 须仅小写字母/数字/单连字符"))
        if XML_RE.search(name):
            report.issues.append(Issue("error", "NAME_XML", "name 含 XML 标记"))

    if not desc:
        report.issues.append(Issue("error", "DESC_MISSING", "frontmatter 缺 description"))
    else:
        if len(desc) > MAX_DESC_LEN:
            report.issues.append(
                Issue("error", "DESC_LENGTH", f"description 长度 {len(desc)}，须 <= {MAX_DESC_LEN}"))
        if INSTRUCTION_XML_RE.search(desc):
            report.issues.append(Issue("error", "DESC_XML", "description 含 XML 指令标记"))
        words = set(re.findall(r"[A-Za-z]+", desc.lower()))
        found = (words & FIRST_PERSON) or (FIRST_PERSON_ZH & set(desc))
        if found:
            report.issues.append(
                Issue("warning", "DESC_PERSON",
                      f"description 含第一/二人称词 {sorted(found)[:4]}，建议第三人称命令式"))
        if not TRIGGER_RE.search(desc):
            report.issues.append(
                Issue("warning", "DESC_TRIGGER",
                      "description 缺触发词（当/使用/用于/when/use 等）"))

    line_count = len(text.splitlines())
    if line_count > MAX_LINES:
        report.issues.append(
            Issue("error", "LINES", f"SKILL.md {line_count} 行，须 <= {MAX_LINES}"))

    if WINDOWS_PATH_RE.search(text):
        report.issues.append(
            Issue("error", "WINDOWS_PATH", "内容含 Windows 路径（盘符反斜杠）"))

    has_gotchas = any(h in text for h in GOTCHAS_HEADERS)
    if not has_gotchas:
        report.issues.append(
            Issue("error", "GOTCHAS_MISSING", "缺 `## 已知坑` 或 `## Gotchas` 段"))
    else:
        for h in GOTCHAS_HEADERS:
            idx = text.find(h)
            if idx != -1:
                body = text[idx + len(h):].strip()
                if not body or len(body) < 20:
                    report.issues.append(
                        Issue("error", "GOTCHAS_EMPTY", f"`{h}` 段为空或过短"))
                break

    if COMPLETION_HINTS and not any(h in text for h in COMPLETION_HINTS):
        report.issues.append(
            Issue("warning", "NO_COMPLETION_CRITERION",
                  "未检出显式完成准则关键词（completion criterion 启发式）"))

    return report


def scan(root: Path) -> list[SkillReport]:
    reports: list[SkillReport] = []
    for skill_dir in sorted(root.glob("*/")):
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            reports.append(check_skill(skill_md))
    return reports


def render_markdown(reports: list[SkillReport]) -> str:
    lines: list[str] = ["# Skill 结构契约检查报告"]
    n_err = sum(len(r.errors) for r in reports)
    n_warn = sum(len(r.warnings) for r in reports)
    lines.append(f"\n共 {len(reports)} 个 skill，错误 {n_err}，警告 {n_warn}\n")
    for r in reports:
        if not r.issues:
            continue
        lines.append(f"## {r.name} ({r.path})")
        for i in r.issues:
            lines.append(f"- [{i.level.upper()}] {i.code}: {i.message}")
        lines.append("")
    return "\n".join(lines)


def render_json(reports: list[SkillReport]) -> str:
    payload = {
        "skills": [
            {
                "name": r.name,
                "path": str(r.path),
                "errors": [{"code": i.code, "message": i.message} for i in r.errors],
                "warnings": [{"code": i.code, "message": i.message} for i in r.warnings],
            }
            for r in reports
        ],
        "error_count": sum(len(r.errors) for r in reports),
        "warning_count": sum(len(r.warnings) for r in reports),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description="skill 结构契约检查器")
    parser.add_argument("--dir", default="skills", help="skills 根目录")
    parser.add_argument("--exit-code", action="store_true",
                        help="警告也计入退出码（CI 强校验）")
    parser.add_argument("--json", action="store_true", help="输出 JSON 报告")
    args = parser.parse_args()

    root = Path(args.dir)
    reports = scan(root)
    n_err = sum(len(r.errors) for r in reports)
    n_warn = sum(len(r.warnings) for r in reports)

    if args.json:
        print(render_json(reports))
    else:
        print(render_markdown(reports))
        if n_warn:
            print(f"警告 {n_warn} 条（不阻塞，--exit-code 时计入）")

    if n_err:
        return 1
    if args.exit_code and n_warn:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
