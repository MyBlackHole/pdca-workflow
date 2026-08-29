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


def induce(source: Path, ontology_dir: Path) -> list[Candidate]:
    drafts = KnowledgeDraftAdapter().parse(source)
    ontology = load_ontology(ontology_dir)
    cands: list[Candidate] = []
    for d in drafts:
        t = infer_type(d.title, d.text)
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
                    help="knowledge draft dir/file (adapters may extend to code/web)")
    ap.add_argument("--ontology-dir", type=Path, default=Path("ontology"))
    ap.add_argument("--out", choices=("print", "patch"), default="print")
    args = ap.parse_args()
    cands = induce(args.source, args.ontology_dir)
    for c in cands:
        if args.out == "print":
            print(render_candidate_md(c))
        else:
            print(f"# candidate: {c.id}")
            print(render_candidate_md(c))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
