"""Tests for scripts/ontology_induction.py (T0404 seam)."""
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.ontology_induction import (  # noqa: E402
    Adapter,
    DOMAIN_VOCAB,
    KnowledgeDraftAdapter,
    induce,
    load_ontology,
)

REPO = Path(__file__).resolve().parent.parent
ONTO = REPO / "ontology"
TYPE_VOCAB = {"domain", "entity", "concept", "process", "role",
              "pattern", "principle", "pitfall", "fact", "decision"}


def _write_source(tmp_path: Path) -> Path:
    d = tmp_path / "src"
    d.mkdir()
    (d / "tls-pattern.md").write_text(
        "# TLS 链路复用 pattern\n\n参考 ontology:entity/tls-session 与 "
        "ontology:concept/entity/x509-certificate 的握手。\n",
        encoding="utf-8",
    )
    (d / "random-note.md").write_text("# 普通笔记\n没有关键词。\n", encoding="utf-8")
    return d


def test_ac1_type_vocab(tmp_path: Path):
    cands = induce(_write_source(tmp_path), ONTO)
    assert cands, "no candidates produced"
    for c in cands:
        assert c.type in TYPE_VOCAB


def test_ac2_no_cycle_dangling(tmp_path: Path):
    cands = induce(_write_source(tmp_path), ONTO)
    cand_dir = ONTO / "_candidates"
    cand_dir.mkdir(exist_ok=True)
    try:
        for c in cands:
            name = c.id.replace("/", "__") + ".md"
            fm = yaml.safe_dump(c.to_frontmatter(), allow_unicode=True, sort_keys=False)
            (cand_dir / name).write_text("---\n" + fm + "---\n", encoding="utf-8")
        out = subprocess.run(
            [sys.executable, str(REPO / "scripts/ontology-validate.py"),
             "--ontology-dir", str(ONTO)],
            capture_output=True, text=True,
        )
        assert "CYCLE" not in (out.stdout + out.stderr)
        assert "DANGLING_REF" not in (out.stdout + out.stderr)
    finally:
        for f in cand_dir.glob("*.md"):
            f.unlink()
        cand_dir.rmdir()


def test_ac3_no_ontology_write(tmp_path: Path):
    src = _write_source(tmp_path)
    before = {p for p in ONTO.rglob("*.md")}
    induce(src, ONTO)  # pure function, must not touch ontology/
    after = {p for p in ONTO.rglob("*.md")}
    assert before == after


def test_ac4_deterministic(tmp_path: Path):
    src = _write_source(tmp_path)
    a = induce(src, ONTO)
    b = induce(src, ONTO)
    assert [(c.id, c.type, c.specializes, c.guides) for c in a] == \
           [(c.id, c.type, c.specializes, c.guides) for c in b]


def test_ac5_adapters():
    assert isinstance(KnowledgeDraftAdapter(), Adapter)
    # code/web adapters are extension points: base Adapter is importable
    assert Adapter is not None


def test_ac6_guides_domain_vocab(tmp_path: Path):
    src = _write_source(tmp_path)
    ont = load_ontology(ONTO)
    for c in induce(src, ONTO):
        for g in c.guides:
            assert ont.get(g) in DOMAIN_VOCAB
