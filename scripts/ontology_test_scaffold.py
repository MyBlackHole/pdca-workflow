#!/usr/bin/env python3
"""ontology_test_scaffold: 按 testable_signal 三模式自动生成测试骨架。

依据 ontology:pattern/testable-signal-to-test-derivation 的三派生：
  - 属性断言（Attribute Assertion）
  - 契约测试（Contract Test）
  - 收敛验证（Convergence Verification）

用法:
  python3 scripts/ontology_test_scaffold.py --node ontology:domain/ontology-deep-integration-overview --out tests/test_xxx.py
  python3 scripts/ontology_test_scaffold.py --node ontology:entity/ontology-deep-integration --out tests/
  python3 scripts/ontology_test_scaffold.py --node ontology:pattern/testable-signal-to-test-derivation

输出:
  - 测试骨架 .py 文件（pytest 可收集，含三模式示例）
  - scaffold-map.json（信号->测试映射，机器可读）
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parent.parent

def extract_fm(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}

def load_nodes(ont_dir: Path) -> dict:
    nodes = {}
    for md in sorted(ont_dir.rglob("*.md")):
        if md.name == "README.md":
            continue
        fm = extract_fm(md)
        oid = fm.get("id")
        if oid:
            nodes[oid] = (md, fm)
    return nodes

def classify_signal(signal: str) -> str:
    s = signal or ""
    if any(k in s for k in ["回链", "覆盖", "登记", "convergence", "收敛", "evidence", "AC-"]):
        return "convergence"
    if any(k in s for k in ["对比", "一致", "契约", "contract", "清单", "seam", "DesignVocab"]):
        return "contract"
    return "assertion"

TEMPLATE = '''# 自动生成：{node_id} 的 testable_signal 测试骨架
# 三模式：属性断言 / 契约测试 / 收敛验证（见 ontology:pattern/testable-signal-to-test-derivation）
# 运行: pytest {out_name} -v
import pathlib, subprocess, json, re

NODE_ID = "{node_id}"
NODE_TYPE = "{node_type}"
ONT_DIR = pathlib.Path("{ont_dir}")

def test_attr_{slug}_signals_non_generic():
    """属性断言：testable_signal 非空且非泛化（AC-4 补充）"""
    import yaml
    fm = yaml.safe_load(pathlib.Path("{src_path}").read_text().split("---")[1])
    for attr in (fm.get("attributes") or []):
        sig = str(attr.get("testable_signal",""))
        assert sig.strip(), f"{{attr.get('name')}} 缺 testable_signal"
        assert "由领域实践与测试验证" not in sig, f"{{attr.get('name')}} 为泛化信号"
        assert any(v in sig for v in ["检查","校验","运行","断言","验证","对比","回链","覆盖"]), f"{{attr.get('name')}} 无动词+判定"

def test_contract_{slug}_exists():
    """契约测试示例：声明 vs 实际一致性（按需精化）"""
    # 示例：校验本体节点存在且可被 ontology-validate
    ret = subprocess.run(["python3", "scripts/ontology-validate.py", "--ontology-dir", str(ONT_DIR)], capture_output=True, text=True)
    assert ret.returncode == 0, ret.stdout + ret.stderr

def test_convergence_{slug}_map():
    """收敛验证示例：convergence 需回链 AC 与 evidence（按需接入真实任务）"""
    # 本骨架仅示范结构；真实收敛验证由 scripts/validate-convergence.py --task-dir 承载
    assert NODE_ID.startswith("ontology:"), "node_id 须为本体 id"
'''

MAP_TEMPLATE = {
    "schema": "pdca.test-scaffold-map/v1",
}

def main() -> int:
    ap = argparse.ArgumentParser(description="本体 testable_signal 三模式测试骨架生成")
    ap.add_argument("--node", required=True, help="本体节点 id，如 ontology:entity/xxx")
    ap.add_argument("--ontology-dir", type=Path, default=ROOT / "ontology")
    ap.add_argument("--out", type=Path, default=None, help="输出文件或目录，默认 tests/test_<slug>.py")
    args = ap.parse_args()

    nodes = load_nodes(args.ontology_dir)
    if args.node not in nodes:
        print(f"[scaffold] ERROR: 节点不存在: {args.node}", file=sys.stderr)
        print(f"  可用示例: {list(nodes)[:3]}", file=sys.stderr)
        return 1
    md_path, fm = nodes[args.node]
    slug = args.node.split("/")[-1].replace("-", "_")
    node_type = fm.get("type", "unknown")
    src_path = md_path.relative_to(ROOT) if md_path.is_relative_to(ROOT) else md_path

    out_path = args.out
    if out_path is None:
        out_path = ROOT / f"tests/test_{slug}_scaffold.py"
    elif out_path.is_dir():
        out_path = out_path / f"test_{slug}_scaffold.py"

    out_path.parent.mkdir(parents=True, exist_ok=True)

    content = TEMPLATE.format(
        node_id=args.node,
        node_type=node_type,
        ont_dir=args.ontology_dir.relative_to(ROOT) if args.ontology_dir.is_relative_to(ROOT) else args.ontology_dir,
        src_path=str(src_path),
        slug=slug,
        out_name=out_path.name,
    )
    # 追加每个 attribute 的独立断言桩
    for attr in (fm.get("attributes") or []):
        name = re.sub(r"[^0-9a-zA-Z_]", "_", str(attr.get("name","attr")))
        sig = str(attr.get("testable_signal",""))[:80].replace('"','\\"')
        mode = classify_signal(str(attr.get("testable_signal","")))
        content += f'\n\ndef test_{mode}_{slug}_{name}():\n    """{mode}: {sig}"""\n    assert True  # TODO: 按 testable_signal 精化断言\n'

    out_path.write_text(content, encoding="utf-8")

    # scaffold-map.json
    map_path = out_path.with_suffix("").with_name(out_path.stem.replace("test_", "scaffold-map-") + ".json")
    # Fallback: same dir, scaffold-map-<slug>.json
    map_path = out_path.parent / f"scaffold-map-{slug}.json"
    mapping = {
        "schema": "pdca.test-scaffold-map/v1",
        "node_id": args.node,
        "node_type": node_type,
        "source": str(src_path),
        "out": str(out_path.relative_to(ROOT) if out_path.is_relative_to(ROOT) else out_path),
        "attributes": [
            {"name": a.get("name"), "mode": classify_signal(str(a.get("testable_signal",""))), "testable_signal": a.get("testable_signal"), "constraint": a.get("constraint")}
            for a in (fm.get("attributes") or [])
        ],
        "modes": {"assertion": "属性断言", "contract": "契约测试", "convergence": "收敛验证"},
    }
    map_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[scaffold] 生成 {out_path}  ({len(mapping['attributes'])} attributes)")
    print(f"[scaffold] 映射 {map_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
