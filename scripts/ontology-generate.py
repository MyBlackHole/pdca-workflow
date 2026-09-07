#!/usr/bin/env python3
"""代码→本体自动生成：从代码静态分析自动提取实体、属性、关系，生成本体草案。

用法：
  python3 scripts/ontology-generate.py --source src/ --output ontology/domain/
  python3 scripts/ontology-generate.py --source src/ --output ontology/domain/ --check
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def analyze_source(source_dir: Path) -> list[dict]:
    """从代码目录静态分析提取实体信息。"""
    entities = []
    source_dir = Path(source_dir).resolve()
    root = ROOT.resolve()
    if not source_dir.is_dir():
        print(f"WARN: source dir {source_dir} does not exist", file=sys.stderr)
        return entities
    for py_file in source_dir.rglob("*.py"):
        try:
            rel_path = py_file.relative_to(root)
        except ValueError:
            rel_path = py_file
        text = py_file.read_text(encoding="utf-8")
        class_pattern = re.compile(r'(?:class|struct)\s+(\w+).*?(?::\s*(\w+))?\s*\n(?:\s*"""(.*?)""")?', re.DOTALL)
        for match in class_pattern.finditer(text):
            class_name = match.group(1)
            parent = match.group(2) or None
            doc = match.group(3) or ""
            entities.append({
                "name": class_name,
                "file": str(rel_path),
                "parent": parent,
                "doc": doc.strip()[:200],
            })
        func_pattern = re.compile(r'(?:def|function)\s+(\w+)\s*\(', re.DOTALL)
        for match in func_pattern.finditer(text):
            func_name = match.group(1)
            if not func_name.startswith('_'):
                entities.append({
                    "name": func_name,
                    "file": str(rel_path),
                    "type": "function",
                })
    return entities


def generate_ontology(entities: list[dict], output_dir: Path) -> list[dict]:
    """从实体信息生成本体节点。"""
    generated = []
    output_dir.mkdir(parents=True, exist_ok=True)
    for entity in entities:
        slug = entity["name"].lower()
        ont_dir = output_dir / "entity"
        ont_dir.mkdir(parents=True, exist_ok=True)
        ont_file = ont_dir / f"{slug}.md"
        if ont_file.exists():
            continue  # 跳过已存在的节点
        content = f"""---
schema: pdca.asset/v1
id: ontology:entity/{slug}
type: entity
layer: Knowledge
status: active
summary: {entity.get('doc', entity['name'])[:100]}
relations:
  specializes:
    - ontology:domain/core
attributes:
  - name: applicability
    desc: 自动生成
    constraint: 见正文
    testable_signal: grep -q '{entity['name']}' {entity['file']}
---

# {entity['name']}

自动生成自代码分析。

来源: `{entity['file']}`
"""
        ont_file.write_text(content, encoding="utf-8")
        generated.append({"id": f"ontology:entity/{slug}", "file": str(ont_file), "source": entity["file"]})
    return generated


def main() -> int:
    ap = argparse.ArgumentParser(description="代码→本体自动生成")
    ap.add_argument("--source", type=Path, default=ROOT / "src")
    ap.add_argument("--output", type=Path, default=ROOT / "ontology" / "domain" / "auto-generated")
    ap.add_argument("--check", action="store_true", help="生成后运行 ontology-validate 检查")
    args = ap.parse_args()

    entities = analyze_source(args.source)
    if not entities:
        print("No entities found in source directory")
        return 1

    generated = generate_ontology(entities, args.output)
    print(f"Generated {len(generated)} ontology nodes from {len(entities)} entities")
    for g in generated:
        print(f"  {g['id']} <- {g['source']}")

    if args.check:
        import subprocess
        val = subprocess.run([sys.executable, str(ROOT / "scripts" / "ontology-validate.py"),
                               "--ontology-dir", str(args.output)], capture_output=True, text=True)
        print(val.stdout)
        return val.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
