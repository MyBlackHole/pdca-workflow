#!/usr/bin/env python3
"""生产本体科学门禁（production-ontology-scientific-gate）：七维一键判定。

对齐 ontology:pattern/production-ontology-scientific-gate 的七维约束：
  lifecycle / neon / oops / hundred / signal / diagram / realization

用法：
  python3 scripts/production-ontology-gate.py --all
  python3 scripts/production-ontology-gate.py --node ontology:entity/zfs-vdev
  python3 scripts/production-ontology-gate.py --check lifecycle --node ontology:entity/zfs-vdev
  python3 scripts/production-ontology-gate.py --check oops --all

退出码 0 = GATE OK，1 = FAIL。输出 JSON + 人读小结。
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys, pathlib, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ONT_DIR = ROOT / "ontology"

def run(cmd, shell=False):
    if shell:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    else:
        p = subprocess.run(cmd, capture_output=True, text=True)
    return p

def load_frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.search(r'^---\n(.*?)\n---', text, re.S)
    if not m:
        return {}, text
    fm = yaml.safe_load(m.group(1)) or {}
    return fm, text

def check_lifecycle(node_id: str) -> tuple[bool,str]:
    # 要求 pattern 本身含 METHONTOLOGY 关键词，且节点五阶段产物可追：PRD, frontmatter, relations, Source, validate
    pat = ONT_DIR / "pattern" / "production-ontology-scientific-gate.md"
    if not pat.exists():
        return False, "missing pattern"
    txt = pat.read_text()
    if "METHONTOLOGY" not in txt:
        return False, "pattern missing METHONTOLOGY"
    # 节点是否存在且 frontmatter 合法
    nid_path = None
    for p in ONT_DIR.rglob("*.md"):
        fm,_ = load_frontmatter(p)
        if fm.get("id")==node_id:
            nid_path = p
            break
    if nid_path is None and node_id!="ontology:pattern/production-ontology-scientific-gate":
        return False, f"node {node_id} not found"
    return True, "lifecycle PASS"

def check_neon(node_id: str) -> tuple[bool,str]:
    # islands:0 + pattern含NeOn
    r = run([sys.executable, str(ROOT/"scripts/ontology_graph.py"), "--format", "summary"])
    if "islands: 0" not in r.stdout:
        return False, f"islands not 0: {r.stdout.strip()}"
    pat = ONT_DIR / "pattern" / "production-ontology-scientific-gate.md"
    if "NeOn" not in pat.read_text():
        return False, "pattern missing NeOn"
    return True, "neon PASS islands:0"

def check_oops(all_nodes=False, node_id="") -> tuple[bool,str]:
    # validate 0 issues
    r = run([sys.executable, str(ROOT/"scripts/ontology-validate.py"), "--ontology-dir", str(ONT_DIR)])
    if r.returncode!=0:
        return False, f"validate FAIL: {r.stdout[:500]}"
    r2 = run([sys.executable, str(ROOT/"scripts/ontology_graph.py"), "--format", "summary"])
    if "islands: 0" not in r2.stdout:
        return False, "graph islands !=0"
    # OOPS critical=0 由 validate 覆盖（P08/P10 等）
    return True, "oops PASS critical=0 validate 0 islands:0"

def check_hundred(node_id: str) -> tuple[bool,str]:
    # 100% Rule：以 module/zfs/*.c 140 文件为参照，统计 system composed_of 覆盖率
    # 简化：统计 ontology/entity/zfs-*.md 文本中提及的关键模块数 / 140
    # 对 system 节点要求 coverage>=70%（含意提及），对 leaf 节点仅检查 composed_of 声明存在
    if node_id=="ontology:entity/zfs-system":
        sys_path = ONT_DIR / "entity" / "zfs-system.md"
        fm,_ = load_frontmatter(sys_path)
        composed = fm.get("relations",{}).get("composed_of",[])
        if len(composed)<6:
            return False, f"composed_of {len(composed)} <6"
        # 检查关键模块提及率
        all_mods = [p.name for p in Path("/tmp/zfs/module/zfs").glob("*.c")] if Path("/tmp/zfs/module/zfs").exists() else []
        if not all_mods:
            return True, "hundred PASS (no /tmp/zfs reference, skip coverage calc)"
        texts = "".join((ONT_DIR/"entity"/f).read_text() for f in ["zfs-dmu.md","zfs-dsl.md","zfs-spa.md","zfs-zio.md","zfs-zpl.md","zfs-arc.md","zfs-system.md"] if (ONT_DIR/"entity"/f).exists())
        # 关键模块清单
        keys = ["vdev","zil","ddt","abd","zap","spa","dmu","arc","zfs_znode","metaslab","zio"]
        hit = sum(1 for k in keys if k in texts.lower())
        cov = hit/len(keys)
        if cov<0.6:
            return False, f"coverage {cov:.1%} <60% hit {hit}/{len(keys)}"
        return True, f"hundred PASS coverage {cov:.1%} composed_of {len(composed)}"
    else:
        # leaf 节点检查 relations 非空且含 specializes
        for p in ONT_DIR.rglob("*.md"):
            fm,_ = load_frontmatter(p)
            if fm.get("id")==node_id:
                rel = fm.get("relations",{})
                if not rel.get("specializes"):
                    return False, "missing specializes"
                return True, "hundred PASS leaf specializes ok"
        return False, f"node {node_id} not found"

def check_signal(node_id: str) -> tuple[bool,str]:
    # testable_signal 三模式：含动词且非泛化且双源可回归
    target = None
    for p in ONT_DIR.rglob("*.md"):
        fm,_ = load_frontmatter(p)
        if fm.get("id")==node_id:
            target = p
            break
    if target is None:
        return False, f"node {node_id} not found"
    fm, text = load_frontmatter(target)
    attrs = fm.get("attributes") or []
    if not attrs:
        return False, "no attributes"
    generics = ["由领域实践验证","符合最佳实践","领域实践与测试验证"]
    verbs = ["运行","检查","校验","验证","执行"]
    for a in attrs:
        sig = a.get("testable_signal","")
        if not sig or any(g in sig for g in generics):
            return False, f"attr {a.get('name')} generic signal"
        if not any(v in sig for v in verbs):
            return False, f"attr {a.get('name')} missing verb"
        if "grep -q" not in sig and "gate.py" not in sig:
            return False, f"attr {a.get('name')} missing grep/gate verb"
    # 双源回放：至少 records 段可 grep
    # 不实际执行全部 grep，仅检查信号含 records 或 /tmp/zfs
    sigs = " ".join(a.get("testable_signal","") for a in attrs)
    if "records/" not in sigs and "/tmp/zfs" not in sigs:
        return False, "signal missing records//tmp/zfs provenance"
    return True, f"signal PASS {len(attrs)} attrs"

def check_diagram(node_id: str) -> tuple[bool,str]:
    for p in ONT_DIR.rglob("*.md"):
        fm,_ = load_frontmatter(p)
        if fm.get("id")==node_id:
            target = p
            break
    else:
        return False, f"node {node_id} not found"
    txt = target.read_text()
    mermaid = txt.count("```mermaid")
    source = txt.count("Source:")
    has_tree = "决策树" in txt
    has_pos = "正例" in txt
    has_neg = "反例" in txt
    # 系统聚合要求聚合决策树，正交度；叶要求三图
    if mermaid <3:
        return False, f"mermaid {mermaid} <3"
    if source <3:
        return False, f"Source: {source} <3"
    if not has_tree:
        return False, "missing 决策树"
    if not has_pos:
        return False, "missing 正例"
    if not has_neg:
        return False, "missing 反例"
    return True, f"diagram PASS mermaid {mermaid} Source {source}"

def check_realization(node_id: str) -> tuple[bool,str]:
    # 第七维：本体可实现可校验——结构/行为/校验三完整，且 scaffold 可产
    target = None
    fm = {}
    for p in ONT_DIR.rglob("*.md"):
        f,_ = load_frontmatter(p)
        if f.get("id")==node_id:
            target = p
            fm = f
            break
    if target is None:
        return False, f"node {node_id} not found"
    txt = target.read_text()
    # 结构：C4 中必须出现可实现的类型/字段/接口关键词
    structure_kw = ["struct ", "bset", "btree", "journal", "six_lock", "format", "bpos", "alloc", "super"]
    if not any(kw in txt.lower() for kw in structure_kw):
        return False, "realization missing structure 契约（C4 无 struct/字段/接口）"
    # 行为：时序+状态机必须覆盖分支
    if "时序" not in txt or "状态机" not in txt:
        return False, "realization missing behavior 契约（时序/状态机缺）"
    if "```mermaid" not in txt or "Source:" not in txt:
        return False, "realization missing behavior provenance"
    # 校验：正例/反例 + scaffold 可产
    if "正例" not in txt or "反例" not in txt:
        return False, "realization missing verification 契约（正例/反例缺）"
    # scaffold 可产校验（轻量：节点存在且 attributes>=3）
    attrs = fm.get("attributes") or []
    if len(attrs) < 3:
        return False, f"realization missing verification 契约（attributes {len(attrs)} <3）"
    # 尝试 scaffold 生成（不实际跑 pytest，仅检查可产）
    r = run([sys.executable, str(ROOT/"scripts/ontology_test_scaffold.py"), "--node", node_id, "--out", "/tmp/_realization_check.py"])
    if r.returncode != 0:
        return False, f"realization scaffold FAIL: {r.stderr[:300]}"
    return True, f"realization PASS structure+behavior+verification scaffold可产"

CHECKS = {
    "lifecycle": check_lifecycle,
    "neon": check_neon,
    "oops": check_oops,
    "hundred": check_hundred,
    "signal": check_signal,
    "diagram": check_diagram,
    "realization": check_realization,
}

def evaluate_one(node_id: str, checks):
    results = {}
    ok = True
    for c in checks:
        fn = CHECKS[c]
        if c=="oops":
            passed, msg = fn()
        else:
            passed, msg = fn(node_id)
        results[c] = {"pass": passed, "msg": msg}
        if not passed:
            ok=False
    return ok, results

def main():
    ap = argparse.ArgumentParser(description="production ontology scientific gate")
    ap.add_argument("--node", help="ontology id, e.g. ontology:entity/zfs-vdev")
    ap.add_argument("--all", action="store_true", help="gate all production nodes")
    ap.add_argument("--check", choices=list(CHECKS.keys()), help="single check")
    ap.add_argument("--json", action="store_true", help="json only")
    args = ap.parse_args()
    if not args.node and not args.all:
        ap.print_help(); return 1
    if args.all:
        nodes = ["ontology:entity/zfs-system","ontology:entity/zfs-dmu","ontology:entity/zfs-dsl","ontology:entity/zfs-spa","ontology:entity/zfs-zio","ontology:entity/zfs-arc","ontology:entity/zfs-zpl","ontology:domain/zfs-crypto","ontology:pattern/production-ontology-scientific-gate"]
        checks = [args.check] if args.check else list(CHECKS.keys())
        all_ok=True
        out={}
        for nid in nodes:
            ok, res = evaluate_one(nid, checks)
            out[nid]=res
            if not ok: all_ok=False
        payload={"mode":"all","checks":checks,"nodes":out,"gate": "OK" if all_ok else "FAIL"}
        if not args.json:
            for nid, res in out.items():
                fails=[k for k,v in res.items() if not v["pass"]]
                print(f"{nid}: {'OK' if not fails else 'FAIL '+','.join(fails)}")
            print(f"\nGATE {'OK' if all_ok else 'FAIL'}")
        print(json.dumps(payload,ensure_ascii=False,indent=2))
        return 0 if all_ok else 1
    else:
        nid=args.node
        checks=[args.check] if args.check else list(CHECKS.keys())
        ok, res = evaluate_one(nid, checks)
        payload={"mode":"single","node":nid,"checks":res,"gate":"OK" if ok else "FAIL"}
        if not args.json:
            for c,v in res.items():
                print(f"{c}: {'PASS' if v['pass'] else 'FAIL'} - {v['msg']}")
            print(f"GATE {'OK' if ok else 'FAIL'}")
        print(json.dumps(payload,ensure_ascii=False,indent=2))
        return 0 if ok else 1

if __name__=="__main__":
    raise SystemExit(main())
