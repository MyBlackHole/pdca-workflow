#!/usr/bin/env python3
"""Semi-automatic ontology induction aid.

Reads multi-source input (knowledge drafts / code / web; first version implements
the knowledge-draft adapter; code/web adapters are extension points), applies
rule/heuristic induction to propose candidate frontmatter skeletons
(type / specializes / candidate guides), and emits PR/diff for human review.
Does NOT write into ontology/ directly (HITL preserved).

Design: adapter -> induction -> output. Deterministic (no LLM call), so the same
input yields the same candidates (AC-4).
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

TYPE_VOCAB = {"domain", "entity", "concept", "process", "role",
              "pattern", "principle", "pitfall", "fact", "decision"}
KNOWLEDGE_VOCAB = {"pattern", "principle", "pitfall", "fact", "decision"}
DOMAIN_VOCAB = {"domain", "entity", "concept", "process", "role"}

# heuristic keyword -> type (case-insensitive substring match on title + head)
TYPE_KEYWORDS = {
    "pattern": "pattern", "模式": "pattern",
    "principle": "principle", "原则": "principle",
    "pitfall": "pitfall", "陷阱": "pitfall", "坑": "pitfall",
    "fact": "fact", "事实": "fact",
    "decision": "decision", "决策": "decision",
}


@dataclass
class Candidate:
    id: str
    type: str
    summary: str
    specializes: list[str] = field(default_factory=list)
    guides: list[str] = field(default_factory=list)

    def to_frontmatter(self) -> dict:
        return {
            "schema": "pdca.asset/v1",
            "id": self.id,
            "type": self.type,
            "layer": "Knowledge",
            "status": "active",
            "summary": self.summary,
            "relations": {
                "specializes": self.specializes,
                "guides": self.guides,
            },
            "attributes": [],
        }


@dataclass
class RawDraft:
    path: Path
    title: str
    text: str


class Adapter:
    """Base adapter: source -> list of raw drafts.

    Code/web adapters are extension points (AC-5): subclass and implement parse().
    """

    def parse(self, path: Path) -> list[RawDraft]:
        raise NotImplementedError


class KnowledgeDraftAdapter(Adapter):
    def parse(self, path: Path) -> list[RawDraft]:
        if path.is_dir():
            files = sorted(path.rglob("*.md"))
        else:
            files = [path]
        drafts = []
        for f in files:
            text = f.read_text(encoding="utf-8")
            drafts.append(RawDraft(f, self._title(text, f), text))
        return drafts

    @staticmethod
    def _title(text: str, f: Path) -> str:
        m = re.search(r"^#\s+(.+)$", text, re.M)
        if m:
            return m.group(1).strip()
        return f.stem


class EvidenceAdapter(Adapter):
    """Evidence -> RawDraft adapter：从 records/*/evidence/manifest.jsonl 归纳候选。

    将每条 evidence 按 evidence_type_ref / kind 聚合，生成 RawDraft，
    其 text 携带 kind 与关联本体引用，供后续 induce 生成候选 guides。
    若传入 path 为 manifest.jsonl 直链则仅读该文件；若为目录则递归扫描。
    """

    def parse(self, path: Path) -> list[RawDraft]:
        import json

        manifests: list[Path] = []
        if path.is_file() and path.name == "manifest.jsonl":
            manifests = [path]
        elif path.is_file():
            # 单条 evidence 文件，也视为一条 draft
            text = path.read_text(encoding="utf-8", errors="ignore")[:2000]
            return [RawDraft(path, path.stem, text)]
        else:
            # 目录：递归找所有 manifest.jsonl
            manifests = sorted(path.rglob("manifest.jsonl"))
            # 若目录本身不含 manifest，尝试直接找 evidence 文件
            if not manifests and path.is_dir():
                files = sorted(path.rglob("*.md")) + sorted(path.rglob("*.json"))
                drafts = []
                for f in files[:20]:
                    try:
                        txt = f.read_text(encoding="utf-8", errors="ignore")[:2000]
                    except Exception:
                        continue
                    drafts.append(RawDraft(f, f.stem, txt))
                if drafts:
                    return drafts

        drafts: list[RawDraft] = []
        seen: dict[str, list[Path]] = {}
        for mf in manifests:
            try:
                lines = mf.read_text(encoding="utf-8").splitlines()
            except Exception:
                continue
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except Exception:
                    continue
                if entry.get("superseded_by"):
                    continue
                kind = str(entry.get("kind", "evidence"))
                ref = str(entry.get("evidence_type_ref") or "")
                key = ref or f"kind:{kind}"
                seen.setdefault(key, []).append(mf)
                # 每条 evidence 生成一个 draft；聚合去重在 induce 阶段完成
                eid = str(entry.get("id", kind))
                title = f"evidence-{kind}-{eid}"
                # 构造携带本体引用的文本，供 propose_guides 命中
                parts = [f"# {title}", f"kind: {kind}"]
                if ref:
                    parts.append(f"evidence_type_ref: {ref} 关联 {ref}")
                # 关联 pdca-evidence 子类型便于 guides 命中 domain 实体
                criteria = entry.get("criteria") or []
                if criteria:
                    parts.append(f"criteria: {', '.join(str(c) for c in criteria)}")
                text = "\n".join(parts)
                drafts.append(RawDraft(mf, title, text))

        # 去重：同一 key 保留一条代表
        deduped: dict[str, RawDraft] = {}
        for d in drafts:
            deduped.setdefault(d.title, d)
        return list(deduped.values())


def infer_type(title: str, text: str) -> str:
    blob = (title + "\n" + text[:800]).lower()
    for kw, t in TYPE_KEYWORDS.items():
        if kw.lower() in blob:
            return t
    return "concept"


def propose_specializes(type_: str) -> list[str]:
    # instance specializes its morphology class node (keeps the is-a tree acyclic)
    if type_ in KNOWLEDGE_VOCAB:
        return [f"ontology:{type_}"]
    return []


def load_ontology(ontology_dir: Path) -> dict[str, str]:
    """Return mapping id -> type for existing ontology nodes."""
    res: dict[str, str] = {}
    for md in sorted(ontology_dir.rglob("*.md")):
        if md.name == "README.md":
            continue
        text = md.read_text(encoding="utf-8")
        m_id = re.search(r"^id:\s*(\S+)", text, re.M)
        m_type = re.search(r"^type:\s*(\S+)", text, re.M)
        if m_id and m_type:
            res[m_id.group(1)] = m_type.group(1)
    return res


def propose_guides(text: str, ontology: dict[str, str]) -> list[str]:
    found = []
    for oid, t in ontology.items():
        if t not in DOMAIN_VOCAB:
            continue
        if re.search(r"(?<![\w/])" + re.escape(oid) + r"(?![\w/])", text):
            found.append(oid)
    return found


def _slug(title: str, path: Path) -> str:
    s = re.sub(r"[^\w一-鿿]+", "-", title).strip("-").lower()
    if not s:
        s = path.stem
    return s[:60]


def induce(source: Path, ontology_dir: Path, adapter: str = "knowledge") -> list[Candidate]:
    if adapter == "evidence":
        drafts = EvidenceAdapter().parse(source)
    else:
        drafts = KnowledgeDraftAdapter().parse(source)
    ontology = load_ontology(ontology_dir)
    cands: list[Candidate] = []
    for d in drafts:
        t = infer_type(d.title, d.text)
        # evidence 场景：优先映射到 concept/domain，且保留 evidence 关联
        if adapter == "evidence" and t == "concept":
            # evidence 产生的候选默认挂到 pdca 体系，避免孤岛
            pass
        spec = propose_specializes(t)
        guides = propose_guides(d.text, ontology)
        cid = "ontology:" + t + "/" + _slug(d.title, d.path)
        cands.append(Candidate(cid, t, d.title, spec, guides))
    return cands


def render_candidate_md(c: Candidate) -> str:
    import yaml

    fm = yaml.safe_dump(c.to_frontmatter(), allow_unicode=True, sort_keys=False)
    return "---\n" + fm + "---\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Semi-automatic ontology induction aid")
    ap.add_argument("--source", required=True, type=Path,
                    help="knowledge draft dir/file or records dir for evidence adapter")
    ap.add_argument("--ontology-dir", type=Path, default=Path("ontology"))
    ap.add_argument("--adapter", choices=("knowledge", "evidence"), default="knowledge",
                    help="选择 adapter：knowledge（默认）或 evidence")
    ap.add_argument("--out", choices=("print", "patch"), default="print")
    args = ap.parse_args()
    cands = induce(args.source, args.ontology_dir, adapter=args.adapter)
    for c in cands:
        if args.out == "print":
            print(render_candidate_md(c))
        else:
            print(f"# candidate: {c.id}")
            print(render_candidate_md(c))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
