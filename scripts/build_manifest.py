#!/usr/bin/env python3
"""Maintainer-only byte projection. Never include central task data."""
from pathlib import Path
import json
import sys
from common import MANIFEST, digest, relative_name


def build(root: Path) -> dict:
    files = {}
    for p in sorted(root.rglob('*')):
        if not p.is_file():
            continue
        name = p.relative_to(root).as_posix()
        if (name == MANIFEST or name == '.pdca-install.json' or name.startswith(('records/', 'legacy/', '.git/', 'ontology/projects/'))
                or '__pycache__' in p.parts or name.endswith('.pyc') or name.startswith('.pdca-install')):
            continue
        if p.is_symlink():
            raise ValueError(f"No symlinks in source release: {name}")
        files[relative_name(name)] = digest(p.read_bytes())
    active = []
    for name in files:
        text = (root/name).read_text(encoding='utf-8') if name.endswith('.md') else ''
        if (name in ('README.md', 'AGENTS.md', 'SKILL.md', 'USE-PDCA.md', 'INSTALL.md', 'protocol-release.md', 'VERSION', 'setup')
                or name.startswith(('bootstrap/', 'skills/', 'scripts/'))
                or name in ('ontology/INDEX.md', 'ontology/LOAD-MAP.md', 'ontology/README.md', 'templates/README.md')
                or name.startswith('ontology/concept/') and 'authority: normative\n' in text and 'revision: 4.0.0-rc.' in text
                or name.startswith('ontology/process/') and 'authority: normative\n' in text and 'revision: 4.0.0-rc.' in text
                or name.startswith('ontology/contracts/') and 'schema: pdca.contract/v4' in text
                or name.startswith('templates/') and text.startswith('---\nschema: pdca.') and '/v4\n' in text
                or name in ('tests/README.md', 'tests/host-acceptance.md', 'migration/v4.0.0-rc.2-MIGRATION.md')):
            active.append(name)
    m = {'schema':'pdca.release-manifest/v1','version':(root/'VERSION').read_text().strip(),
         'active':active,'files':files,'host_acceptance':'NOT_RUN'}
    (root/MANIFEST).write_text('# 当前发布字节清单\n\n由 `python3 scripts/build_manifest.py .` 生成。files用于安装校验；active用于集中任务快照。清单不自哈希，项目绑定另固定其摘要。SHA-256不认证发布者或运行事实。\n\n```json\n'+json.dumps(m,ensure_ascii=False,indent=2,sort_keys=True)+'\n```\n')
    return m

if __name__ == '__main__':
    m=build(Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve())
    print(json.dumps({'version':m['version'],'files':len(m['files']),'active':len(m['active'])}))
