#!/usr/bin/env python3
"""Explicit file installation/registration, NOT an Agent scheduler or permission backend.

Python 3.10+, POSIX. No shell interpolation, network calls, package installation,
user-project writes, or deletion of central task/ontology data.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
from urllib.parse import unquote, quote
import uuid
from common import (Invalid, MANIFEST, OWNER, SKILLS, digest, json_bytes, md_document,
                    no_links, normal_path, read_catalog, read_json, read_owned_md,
                    relative_name, verify_release)

STATE = '.pdca-install.json'
ENTRY_MARK = '.pdca-entry.json'
SOURCE = Path(__file__).resolve().parent.parent


def require_layout(root: Path, skills: Path) -> None:
    no_links(root); no_links(skills)
    if root == skills or root.is_relative_to(skills) or skills.is_relative_to(root):
        raise Invalid('Central root and discovery directory must be disjoint, not nested')


def load_state(root: Path) -> dict | None:
    p = root / STATE
    no_links(p)
    if not p.exists():
        return None
    s = read_json(p)
    if s.get('owner') != OWNER or s.get('root') != str(root):
        raise Invalid('Central root ownership/path mismatch; do not silently relocate')
    if not isinstance(s.get('install_id'), str) or not isinstance(s.get('files'), dict):
        raise Invalid('Incomplete installation state')
    for name, sha in s['files'].items():
        if name != MANIFEST: relative_name(name)
        if not re.fullmatch('[0-9a-f]{64}', str(sha)):
            raise Invalid('Invalid owned-file digest')
    return s


def verify_installed_bytes(root: Path, state: dict) -> None:
    for name, sha in state['files'].items():
        p = root / name; no_links(p)
        if not p.is_file() or digest(p.read_bytes()) != sha:
            raise Invalid(f'Installed file locally modified or missing: {name}; preserve it before update')


def snapshot_path(root: Path, source: Path, manifest: dict) -> Path:
    return root/'records/protocol'/(manifest['version']+'-'+digest((source/MANIFEST).read_bytes())[:16])


def render(source: Path, entry: dict, root: Path, snapshot: Path) -> bytes:
    text = (source/entry['path']).read_text(encoding='utf-8')
    # Preserve complete actionable body; rebase relative references into pinned rules.
    def rebase(match):
        label, target = match.groups()
        clean, sep, fragment = target.partition('#')
        if not clean or ':' in clean or clean.startswith('/'):
            return match.group(0)
        p = ((source/entry['path']).parent/unquote(clean)).resolve()
        if not p.is_relative_to(source):
            raise Invalid(f'Escaping skill link: {target}')
        absolute = snapshot/p.relative_to(source)
        return f'[{label}](<{quote(str(absolute), safe="/")}{sep}{fragment}>)'
    text = re.sub(r'\[([^\]\n]+)\]\(([^)\n]+)\)', rebase, text)
    split = text.find('\n---\n', 4)
    if split < 0: raise Invalid('Skill frontmatter delimiter missing')
    pos = split+5
    note = (f'\n<!-- PDCA installed entry; edit the maintained source, not this export. -->\n'
            f'集中资源根 PDCA_ROOT：`{root}`。\n'
            f'本入口发布快照：`{snapshot}`。\n'
            '已有任务优先采用自身 context 和 protocol_baseline_ref。版本或摘要不匹配时，'
            '本入口只定位原任务，不用当前方法推进旧任务；根不可访问就阻断，不创建项目本地 .pdca。\n')
    return (text[:pos]+note+text[pos:]).encode('utf-8')


def entry_status(directory: Path, name: str, root: Path, state: dict | None) -> dict | None:
    no_links(directory)
    if not directory.exists(): return None
    if not directory.is_dir(): raise Invalid(f'Foreign skill entry: {directory}')
    if set(p.name for p in directory.iterdir()) != {'SKILL.md', ENTRY_MARK}:
        raise Invalid(f'Foreign or user-extended skill directory; not overwritten: {directory}')
    for child in directory.iterdir(): no_links(child)
    m = read_json(directory/ENTRY_MARK)
    if (state is None or m.get('owner') != OWNER or m.get('root') != str(root)
            or m.get('name') != name or m.get('install_id') != state['install_id']):
        raise Invalid(f'Skill entry belongs to another installation: {directory}')
    if not (directory/'SKILL.md').is_file() or digest((directory/'SKILL.md').read_bytes()) != m.get('sha256'):
        raise Invalid(f'Skill export locally modified; not overwritten: {directory}')
    return m


class Transaction:
    """Rollback ordinary exceptions, atomic individual files. Not power-loss atomic."""
    def __init__(self):
        self.changes: list[tuple[Path, bytes | None, int]] = []
        self.created: list[Path] = []

    def mkdir(self, p: Path):
        no_links(p)
        if p.exists():
            if not p.is_dir(): raise Invalid(f'Expected directory: {p}')
            return
        self.mkdir(p.parent)
        p.mkdir(mode=0o700)
        self.created.append(p)

    @staticmethod
    def atomic(p: Path, data: bytes, mode: int):
        no_links(p)
        fd, tmp = tempfile.mkstemp(prefix='.pdca-tmp-', dir=p.parent)
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(data); f.flush(); os.fsync(f.fileno())
            os.chmod(tmp, mode)
            os.replace(tmp, p)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)

    def write(self, p: Path, data: bytes, mode: int = 0o600):
        no_links(p); self.mkdir(p.parent)
        if p.exists() and not p.is_file(): raise Invalid(f'Expected file: {p}')
        before = p.read_bytes() if p.exists() else None
        oldmode = stat.S_IMODE(p.stat().st_mode) if p.exists() else mode
        if before == data: return
        self.changes.append((p, before, oldmode))
        self.atomic(p, data, mode)

    def remove(self, p: Path):
        no_links(p)
        self.changes.append((p, p.read_bytes(), stat.S_IMODE(p.stat().st_mode)))
        p.unlink()

    def rollback(self):
        for p, before, mode in reversed(self.changes):
            if before is None:
                if p.exists(): p.unlink()
            else:
                p.parent.mkdir(parents=True, exist_ok=True)
                self.atomic(p, before, mode)
        for p in reversed(self.created):
            if p.exists():
                try: p.rmdir()
                except OSError: pass


@contextmanager
def locked(root: Path, skills: Path):
    # Both namespaces are locked: two different roots cannot race on one skill dir.
    # Locks control installer metadata only, never business/PDCA resources.
    descriptors = []
    try:
        for target in sorted({root, skills}, key=str):
            no_links(target.parent)
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            path = target.parent/('.pdca-install-'+digest(str(target).encode())[:16]+'.lock')
            no_links(path)
            fd = os.open(path, os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0), 0o600)
            descriptors.append(fd)
            try: fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as e: raise Invalid('Another installer/registry writer holds this namespace') from e
        yield
    finally:
        for fd in reversed(descriptors): os.close(fd)


def installation_plan(source: Path, root: Path, skills: Path, update: bool):
    require_layout(root, skills)
    m = verify_release(source)
    catalog = read_catalog(source)
    state = load_state(root)
    if root.exists() and not root.is_dir(): raise Invalid('Central root is not a directory')
    if state is None and root.exists() and any(root.iterdir()) and root != source:
        raise Invalid('Nonempty unowned root; no automatic adoption/copy over existing resources')
    if state:
        verify_installed_bytes(root, state)
        changed = state['files'].get(MANIFEST) != digest((source/MANIFEST).read_bytes())
        if changed and not update:
            raise Invalid('Different release; use a fresh source tree and explicit --update after review')
    for name in [*m['files'], MANIFEST]:
        p = root/name; no_links(p)
        if p.exists() and root != source and (not state or name not in state['files']):
            raise Invalid(f'Unowned central file conflicts with this release: {name}')
    for p in ('records', 'records/projects', 'records/tasks', 'records/works', 'records/resources', 'records/protocol', 'ontology/projects'):
        dest = root/p; no_links(dest)
        if dest.exists() and not dest.is_dir(): raise Invalid(f'Central data path is not a directory: {dest}')
    exported = []
    snap = snapshot_path(root, source, m)
    no_links(snap)
    if snap.exists():
        if (snap/MANIFEST).read_bytes() != (source/MANIFEST).read_bytes():
            raise Invalid('Existing rule snapshot differs; never overwrite')
        verify_release(snap, active_only=True)
    for entry in catalog:
        old = entry_status(skills/entry['name'], entry['name'], root, state)
        exported.append((entry['name'], render(source, entry, root, snap), old))
    return m, state, snap, exported


def install(source: Path, root: Path, skills: Path, apply: bool, update: bool):
    m, old, snap, exports = installation_plan(source, root, skills, update)
    result = {'status':'preview','version':m['version'],'root':str(root),'skills_dir':str(skills),
              'skill_entries':8,'snapshot':str(snap),'project_files_written':0,
              'agents_started':0,'host_discovery':'NOT_RUN','host_acceptance':'NOT_RUN'}
    if not apply: return result
    tx = Transaction()
    try:
        tx.mkdir(root)
        for name in [*m['files'], MANIFEST]:
            mode = stat.S_IMODE((source/name).stat().st_mode) & 0o777
            tx.write(root/name, (source/name).read_bytes(), mode or 0o600)
        for p in ('records/projects','records/tasks','records/works','records/resources','records/protocol','ontology/projects'):
            tx.mkdir(root/p)
        if not snap.exists():
            for name in [*m['active'], MANIFEST]:
                tx.write(snap/name, (source/name).read_bytes(), 0o444)
        identity = old['install_id'] if old else str(uuid.uuid4())
        for name, content, _ in exports:
            tx.write(skills/name/'SKILL.md', content)
            marker = {'owner':OWNER,'root':str(root),'install_id':identity,'name':name,
                      'version':m['version'],'sha256':digest(content)}
            tx.write(skills/name/ENTRY_MARK, json_bytes(marker))
        state = {'owner':OWNER,'root':str(root),'install_id':identity,'version':m['version'],
                 'files':{**m['files'], MANIFEST:digest((source/MANIFEST).read_bytes())},
                 'snapshot':str(snap),'skills_dirs':sorted(set((old or {}).get('skills_dirs',[]))|{str(skills)})}
        tx.write(root/STATE, json_bytes(state))
    except Exception:
        tx.rollback(); raise
    result['status'] = 'installed' if tx.changes else 'already_installed'
    result['files_changed'] = len(tx.changes)
    return result


def check_install(root: Path, skills: Path):
    require_layout(root, skills)
    s = load_state(root)
    if s is None: raise Invalid('No installation state')
    verify_installed_bytes(root, s)
    m = verify_release(root)
    snap = snapshot_path(root, root, m)
    if s.get('snapshot') != str(snap): raise Invalid('Installed snapshot path mismatch')
    verify_release(snap, active_only=True)
    if (snap/MANIFEST).read_bytes() != (root/MANIFEST).read_bytes(): raise Invalid('Snapshot manifest mismatch')
    for e in read_catalog(root):
        marker = entry_status(skills/e['name'], e['name'], root, s)
        if marker is None: raise Invalid(f'Missing registered skill: {e["name"]}')
        if (skills/e['name']/'SKILL.md').read_bytes() != render(root, e, root, snap):
            raise Invalid('Stale generated skill; rerun installer')
    return {'status':'checked','skill_entries':8,'root':str(root),'version':m['version'],
            'central_data_preserved':True,'host_discovery':'NOT_RUN','host_acceptance':'NOT_RUN'}


def uninstall(root: Path, skills: Path, apply: bool):
    require_layout(root, skills)
    s=load_state(root)
    if s is None: raise Invalid('No owned installation; nothing may be removed')
    present=[]
    for name in SKILLS:
        if entry_status(skills/name, name, root, s) is not None: present.append(name)
    result={'status':'preview','entries_to_remove':present,'root_preserved':str(root),
            'records_preserved':True,'ontology_preserved':True,'snapshots_preserved':True}
    if not apply:return result
    tx=Transaction()
    try:
        for name in present:
            tx.remove(skills/name/'SKILL.md');tx.remove(skills/name/ENTRY_MARK)
        s['skills_dirs']=[x for x in s.get('skills_dirs',[]) if x!=str(skills)]
        tx.write(root/STATE,json_bytes(s))
    except Exception:
        tx.rollback();raise
    # Only known empty entry dirs. Never recursive removal.
    for name in present: (skills/name).rmdir()
    result['status']='uninstalled' if present else 'already_uninstalled'
    return result


def bindings(root: Path) -> list[tuple[Path,dict]]:
    base=root/'records/projects';no_links(base)
    values=[]
    if not base.exists():return values
    for p in sorted(base.glob('*/workspaces/*/project-context.md')):
        d=read_owned_md(p)
        if d.get('schema')!='pdca.project-task-context/v4' or d.get('pdca_root')!=str(root):
            raise Invalid(f'Unknown or mismatched central binding: {p}; explicit migration required')
        for k in ('project_id','workspace_id','target_root','records_root','protocol_baseline_ref',
                  'manifest_ref','protocol_revision','protocol_baseline_digest','manifest_digest'):
            if not isinstance(d.get(k),str) or not d[k]:raise Invalid(f'Binding missing {k}: {p}')
        baseline=normal_path(d['protocol_baseline_ref'])
        manifest=normal_path(d['manifest_ref'])
        if (baseline.name!='protocol-release.md' or manifest.name!=MANIFEST
                or baseline.parent!=manifest.parent
                or not baseline.parent.is_relative_to(root/'records/protocol')):
            raise Invalid(f'Binding must reference a central pinned snapshot: {p}')
        for f,key in ((baseline,'protocol_baseline_digest'),(manifest,'manifest_digest')):
            no_links(f)
            if not f.is_file() or digest(f.read_bytes())!=d[key]:
                raise Invalid(f'Binding snapshot bytes missing or changed: {p}')
        if verify_release(baseline.parent,active_only=True)['version']!=d['protocol_revision']:
            raise Invalid(f'Binding version differs from its snapshot: {p}')
        if d['records_root']!=str(root/'records'):raise Invalid(f'Noncentral binding: {p}')
        if d['project_id']!=p.parents[2].name or d['workspace_id']!=p.parent.name:
            raise Invalid(f'Binding identity/path mismatch: {p}')
        values.append((p,d))
    return values


def target_path(raw: str, root: Path) -> Path:
    p=normal_path(raw).resolve(strict=True)
    if not p.is_dir():raise Invalid('Business project is not a directory')
    if p==root or p.is_relative_to(root) or root.is_relative_to(p):
        raise Invalid('Business target and central root must be disjoint')
    return p


def register(root: Path, project: str, project_id: str, workspace_id: str, apply: bool):
    s=load_state(root)
    if s is None:raise Invalid('Install before central registration')
    for name in (project_id,workspace_id):
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}',name):raise Invalid('IDs must be lowercase slug names, 1..64 chars')
    target=target_path(project,root)
    out=root/'records/projects'/project_id/'workspaces'/workspace_id/'project-context.md'
    no_links(out)
    all_bindings=bindings(root)
    if not out.exists() and (target/'.pdca/project-context.md').exists():
        raise Invalid('Legacy project-local PDCA binding exists; explicit migration required, no second binding')
    if out.exists():
        existing=read_owned_md(out)
        if existing['target_root']!=str(target):raise Invalid('Existing workspace targets another path; no silent rebind')
        return {'status':'already_registered','context_ref':str(out),'version':existing['protocol_revision'],
                'target_files_written':0,'agents_started':0,'authorization':'NOT_GRANTED'}
    for path,data in all_bindings:
        if Path(data['target_root']).resolve()==target:
            raise Invalid(f'Target already registered under {path}; do not create duplicate identity')
    m=verify_release(root)
    verify_installed_bytes(root,s)
    snap=Path(s['snapshot']);no_links(snap);verify_release(snap,active_only=True)
    if snap != snapshot_path(root,root,m):raise Invalid('Snapshot mismatch')
    metadata={'schema':'pdca.project-task-context/v4','protocol_revision':m['version'],
              'task_id':None,'attempt':None,'project_id':project_id,'workspace_id':workspace_id,
              'target_root':str(target),'pdca_root':str(root),'records_root':str(root/'records'),
              'ontology_root':str(root/'ontology/projects'/project_id),
              'protocol_baseline_ref':str(snap/'protocol-release.md'),
              'protocol_baseline_digest':digest((snap/'protocol-release.md').read_bytes()),
              'manifest_ref':str(snap/MANIFEST),'manifest_digest':digest((snap/MANIFEST).read_bytes()),
              'reference_library_roots':[str(root/'ontology')],'record_dir':None,'record_writes':[], 'target_writes':[]}
    result={'status':'preview','context_ref':str(out),'project_id':project_id,'workspace_id':workspace_id,
            'target_root':str(target),'target_files_written':0,'agents_started':0,'authorization':'NOT_GRANTED'}
    if not apply:return result
    tx=Transaction()
    try:
        tx.write(out,md_document(metadata,'# 集中项目登记\n\n仅登记项目、工作区与规则快照；未创建任务、未批准阶段、未授予业务写权。恢复时再定位自己的任务和真实用户操作。'))
        tx.mkdir(root/'ontology/projects'/project_id)
    except Exception:
        tx.rollback();raise
    result['status']='registered';return result


def locate(root: Path, project: str):
    if load_state(root) is None:raise Invalid('No central installation')
    target=target_path(project,root)
    matches=[(p,d) for p,d in bindings(root) if target==Path(d['target_root']) or target.is_relative_to(Path(d['target_root']))]
    if matches:
        most=max(len(Path(d['target_root']).parts) for _,d in matches)
        matches=[(p,d) for p,d in matches if len(Path(d['target_root']).parts)==most]
    return {'status':'found' if len(matches)==1 else 'unregistered' if not matches else 'ambiguous',
            'bindings':[{'project_id':d['project_id'],'workspace_id':d['workspace_id'],'context_ref':str(p),'protocol_revision':d['protocol_revision']} for p,d in matches],
            'agents_started':0,'authorization':'NOT_GRANTED'}


def main(argv=None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',nargs='?',choices=['install','check','uninstall','register','locate'],default='install')
    p.add_argument('--root',default=str(Path.home()/'.agents/pdca'))
    p.add_argument('--skills-dir',default=str(Path.home()/'.agents/skills'))
    p.add_argument('--apply',action='store_true',help='Explicitly write installation/registration changes')
    p.add_argument('--update',action='store_true',help='Allow reviewed release update; local edits still block')
    p.add_argument('--project',help='Existing business project; never written by this tool')
    p.add_argument('--project-id');p.add_argument('--workspace-id',default='main')
    a=p.parse_args(argv)
    try:
        root,skills=normal_path(a.root),normal_path(a.skills_dir)
        require_layout(root,skills)
        if a.command in ('register','locate') and not a.project:raise Invalid('--project is required')
        if a.command=='register' and not a.project_id:raise Invalid('--project-id is required')
        if a.update and a.command!='install':raise Invalid('--update is only valid for installation')
        if a.command in ('check','locate') and a.apply:raise Invalid('Read-only command does not accept --apply')
        def action():
            if a.command=='install':return install(SOURCE,root,skills,a.apply,a.update)
            if a.command=='check':return check_install(root,skills)
            if a.command=='uninstall':return uninstall(root,skills,a.apply)
            if a.command=='register':return register(root,a.project,a.project_id,a.workspace_id,a.apply)
            return locate(root,a.project)
        # Preflight before any managed write; under the lock preflight is repeated.
        if a.apply:
            if a.command=='install':installation_plan(SOURCE,root,skills,a.update)
            elif a.command=='uninstall':uninstall(root,skills,False)
            elif a.command=='register':register(root,a.project,a.project_id,a.workspace_id,False)
            with locked(root,skills):result=action()
        else:result=action()
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (Invalid,OSError) as e:
        print(json.dumps({'status':'blocked','error':str(e),'agents_started':0},ensure_ascii=False,indent=2));return 1

if __name__=='__main__':sys.exit(main())
