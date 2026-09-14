"""Small, standard-library-only helpers. Hashes fix bytes, not provenance."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re

MANIFEST = "release-manifest.md"
OWNER = "pdca-central-skills/v1"
SKILLS = (
    "pdca", "pdca-plan", "pdca-do", "pdca-check", "pdca-act",
    "pdca-ontology-modeling", "pdca-ontology-projection",
    "pdca-ontology-conformance-verification",
)

class Invalid(ValueError):
    """An input is unsafe, incomplete, or incompatible; do not guess."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(data: object) -> bytes:
    return (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        raise Invalid(f"Cannot read JSON {path}: {e}") from e
    if not isinstance(value, dict):
        raise Invalid(f"Expected an object: {path}")
    return value


def normal_path(raw: str | Path) -> Path:
    # Refuse multiline/Markdown-breaking names in generated instruction paths.
    text = os.fspath(raw)
    if any(ord(c) < 32 or c in '`<>' for c in text):
        raise Invalid("Control characters, backticks and angle brackets are not supported in paths")
    return Path(os.path.abspath(os.path.expanduser(text)))


def no_links(path: Path) -> None:
    for p in (path, *path.parents):
        if p.is_symlink():
            raise Invalid(f"Symlink in managed path: {p}")


def relative_name(name: str) -> str:
    p = PurePosixPath(name)
    if (not isinstance(name, str) or not name or p.is_absolute() or '..' in p.parts
            or '\\' in name or name != p.as_posix() or any(ord(c) < 32 for c in name)):
        raise Invalid(f"Unsafe release member: {name!r}")
    if p.parts[0] in {"records", "legacy", ".git"} or name.startswith('ontology/projects/'):
        raise Invalid(f"Mutable/history data cannot be a software member: {name}")
    return name


def read_manifest(root: Path) -> dict:
    no_links(root / MANIFEST)
    try:
        text = (root / MANIFEST).read_text(encoding="utf-8")
        blocks = re.findall(r'^```json\n(.*?)\n```', text, re.M | re.S)
        if len(blocks) != 1:
            raise Invalid("Manifest must contain one JSON block")
        m = json.loads(blocks[0])
        files, active = m['files'], m['active']
        if not isinstance(files, dict) or not isinstance(active, list) or len(active) != len(set(active)):
            raise Invalid("Invalid manifest file/active collections")
        if m.get('schema') != 'pdca.release-manifest/v1':
            raise Invalid("Unsupported release manifest schema")
        if MANIFEST in files:
            raise Invalid("Manifest cannot hash itself")
        for name, sha in files.items():
            relative_name(name)
            if not isinstance(sha, str) or not re.fullmatch(r'[0-9a-f]{64}', sha):
                raise Invalid(f"Invalid digest: {name}")
        if not set(active) <= files.keys():
            raise Invalid("Active member missing from files")
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,63}', m['version']):
            raise Invalid("Invalid release version")
        return m
    except (OSError, KeyError, TypeError, ValueError) as e:
        if isinstance(e, Invalid):
            raise
        raise Invalid(f"Cannot read manifest: {e}") from e


def verify_release(root: Path, active_only: bool = False) -> dict:
    m = read_manifest(root)
    for name in m['active'] if active_only else m['files']:
        p = root / name
        no_links(p)
        if not p.is_file() or digest(p.read_bytes()) != m['files'][name]:
            raise Invalid(f"Release bytes missing or changed: {name}")
    if (root / 'VERSION').read_text().strip() != m['version']:
        raise Invalid("VERSION does not match manifest")
    return m


def read_catalog(root: Path) -> list[dict]:
    data = read_json(root / 'skills/catalog.json')
    if data.get('version') != (root/'VERSION').read_text().strip():
        raise Invalid('Catalog version mismatch')
    entries = data.get('skills')
    if not isinstance(entries, list) or {e.get('name') for e in entries} != set(SKILLS) or len(entries) != 8:
        raise Invalid("Exactly the eight declared skills are required")
    for e in entries:
        if e.get('path') != f"skills/{e['name']}/SKILL.md":
            raise Invalid("Unexpected skill source path")
    return entries


def md_document(metadata: dict, body: str) -> bytes:
    # JSON is also valid YAML; no runtime YAML dependency needed for owned metadata.
    return b'---\n' + json_bytes(metadata) + b'---\n\n' + body.encode('utf-8') + b'\n'


def read_owned_md(path: Path) -> dict:
    no_links(path)
    try:
        text = path.read_text(encoding='utf-8')
        if not text.startswith('---\n'):
            raise Invalid(f"Not an owned structured record: {path}")
        metadata = json.loads(text.split('---\n', 2)[1])
        if not isinstance(metadata, dict):
            raise Invalid("Expected metadata object")
        return metadata
    except (OSError, ValueError, IndexError) as e:
        if isinstance(e, Invalid):
            raise
        raise Invalid(f"Unreadable registry record; no fallback: {path}: {e}") from e
