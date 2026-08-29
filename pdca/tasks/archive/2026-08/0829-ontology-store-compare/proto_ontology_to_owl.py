#!/usr/bin/env python3
"""T0406 原型：把 SSOT v3 与用户提案两套写法的本体节点各转一次 OWL/TTL，
输出映射完整度与脆弱度对比。仅用于调研佐证，不纳入长期维护。

用法：python3 proto_ontology_to_owl.py <task_dir>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

PDCA = "http://pdca.local/ontology/"
CONTROLLED = {"specializes", "composed_of", "configured_by", "guides", "relates_to"}
XSD_MAP = {"String": "xsd:string", "Boolean": "xsd:boolean",
           "Integer": "xsd:integer", "List[String]": "xsd:string"}


def iri_of(idref) -> str:
    if isinstance(idref, list):
        return iri_of(idref[0]) if idref else "<nil>"
    s = idref.strip().strip("[]")
    if s.startswith("ontology:"):
        s = s[len("ontology:"):]
    return f"<{PDCA}{s}>"


def parse_frontmatter(text: str):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text
    return yaml.safe_load(m.group(1)), text[m.end():]


def parse_ssot(path: Path):
    fm, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
    triples = []
    iri = iri_of(fm["id"])
    triples.append((iri, "a", "owl:Class"))
    for key, vals in (fm.get("relations") or {}).items():
        for v in (vals if isinstance(vals, list) else [vals]):
            if key == "specializes":
                triples.append((iri, "rdfs:subClassOf", iri_of(v)))
            else:
                triples.append((iri, f"pdca:{key}", iri_of(v)))
    for attr in fm.get("attributes") or []:
        triples.append((iri, f"pdca:attr/{attr.get('name')}", f'"{attr.get("desc") or ""}"'))
    return {"iri": iri, "triples": triples, "style": "ssot"}


WIKILINK_RE = re.compile(
    r"-\s+\*\*[^*]+\s*\((?P<pred>[^)]+)\)\*\*:\s*(?:对象属性，指向\s*)?\[\[(?P<target>[^\]]+)\]\]")
ATTR_RE = re.compile(r"-\s+\*\*(?P<name>[^*]+)\s*\((?P<en>[^)]+)\)\*\*:\s*数据类型\s*(?P<dtype>\w+)")


def parse_proposal(path: Path):
    fm, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    triples = []
    iri = f"<{PDCA}proposal/{path.stem}>"
    triples.append((iri, "a", "owl:NamedIndividual" if fm.get("type") == "Individual" else "owl:Class"))
    if fm.get("superClass"):
        triples.append((iri, "rdfs:subClassOf", iri_of(fm["superClass"])))
    ambig, lossy = [], []
    for m in WIKILINK_RE.finditer(body):
        triples.append((iri, f"pdca:{m.group('pred')}", iri_of(m.group("target"))))
        if m.group("pred") not in CONTROLLED:
            ambig.append(m.group("pred"))
    for m in ATTR_RE.finditer(body):
        dtype, en = m.group("dtype"), m.group("en")
        xsd = XSD_MAP.get(dtype, "xsd:string")
        triples.append((iri, f"pdca:attr/{en}", f'""^^{xsd}'))
        if dtype not in XSD_MAP:
            lossy.append((en, dtype))
    return {"iri": iri, "triples": triples, "style": "proposal",
            "ambiguous_predicates": ambig, "lossy_attrs": lossy}


def render(triples: list) -> str:
    return "\n".join(f"{s} {p} {o} ." for s, p, o in triples)


def main() -> int:
    root = Path(sys.argv[1])
    ssot_files = [
        Path("ontology/entity/x509-certificate.md"),
        Path("ontology/pattern/mtls-handshake-enum-unify.md"),
        Path("ontology/principle/structured-mtls-failure-diagnostics.md"),
        Path("ontology/concept/pdca.md"),
    ]
    proposal_dir = root / "samples/proposal"
    out = ["# T0406 原型转 OWL/TTL 对比输出\n"]
    for sf in ssot_files:
        s = parse_ssot(Path(sf))
        out += [f"\n## SSOT v3 样本：{sf}", "```turtle", render(s["triples"]), "```"]
    for pf in sorted(proposal_dir.glob("*.md")):
        p = parse_proposal(pf)
        out += [f"\n## 提案风格样本：samples/proposal/{pf.name}", "```turtle", render(p["triples"]), "```",
                f"- 模糊谓词(需归一化): {p['ambiguous_predicates'] or '无'}",
                f"- 属性类型丢失项: {p['lossy_attrs'] or '无'}"]
    out += ["\n## 映射完整度与脆弱度对比\n",
            "- SSOT v3：谓词受控(specializes/guides/...)、关系 range 由 ontology-validate 强制校验 → OWL 映射**无损且可机器验证**；代价是目录耦合(type==dir)、对人类可读性较弱。",
            "- 提案风格：谓词为自由文本(subClassOf/dependsOn/guidedBy) → OWL 映射需**谓词归一化**(否则属性爆炸/语义歧义)；属性类型仅标注中文'数据类型 X' → 非受控类型会**丢失 datatype**；wikilink 拼写错误会静默断图，无内置校验。"]
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
