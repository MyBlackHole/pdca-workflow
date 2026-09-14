#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys
from urllib.parse import unquote
from common import Invalid, verify_release, read_catalog, MANIFEST


def check(root: Path) -> dict:
    m=verify_release(root)
    catalog=read_catalog(root)
    for entry in catalog:
        text=(root/entry['path']).read_text()
        if not text.startswith(f"---\nname: {entry['name']}\n"):
            raise Invalid(f"Skill directory/name mismatch: {entry['name']}")
        if 'context: fork' in text or re.search(r'(^|\n)agent:\s*\S+', text):
            raise Invalid('Phase/scene entry must not auto-spawn an Agent')
    if 'records_root: PDCA_ROOT/records\n' not in (root/'protocol-release.md').read_text():
        raise Invalid('Central records root regressed')
    links=0
    # Only current read set. Retired stubs intentionally do not resolve removed legacy.
    for name in m['active']:
        if not name.endswith('.md'): continue
        text=(root/name).read_text()
        for link in re.findall(r'\[[^\]\n]+\]\(([^)]+)\)',text):
            link=unquote(link.strip('<>').split('#')[0])
            if not link or ':' in link or link.startswith('/') or '<' in link: continue
            path=((root/name).parent/link).resolve()
            if not path.is_relative_to(root) or not path.exists():
                raise Invalid(f"Broken current file link: {name} -> {link}")
            if path.is_file():
                rel=path.relative_to(root).as_posix()
                if rel != MANIFEST and rel not in m['active']:
                    raise Invalid(f"Active snapshot omits linked file: {name} -> {rel}")
            links+=1
    return {'passed':True,'version':m['version'],'files':len(m['files']),
            'active':len(m['active']),'skill_entries':len(catalog),'current_links':links,
            'host_acceptance':'NOT_RUN','runtime_isolation':'NOT_PROVEN'}

if __name__=='__main__':
    try: print(json.dumps(check(Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()),ensure_ascii=False,indent=2))
    except (Invalid,OSError) as e:
        print(json.dumps({'passed':False,'error':str(e)},ensure_ascii=False));sys.exit(1)
