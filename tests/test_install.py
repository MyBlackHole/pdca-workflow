"""Actual temporary-directory operations; does not launch any coding host."""
from __future__ import annotations
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import install as tool
from common import Invalid, MANIFEST, SKILLS, digest, read_json, read_owned_md, verify_release
from build_manifest import build
from check_release import check


def tree(root):
    return {p.relative_to(root).as_posix():digest(p.read_bytes()) for p in root.rglob('*')
            if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts}


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='pdca-rc2-test-')
        self.base=Path(self.temp.name)
        self.root=self.base/'home/.agents/pdca'
        self.skills=self.base/'home/.agents/skills'
        self.project=self.base/'project';self.project.mkdir()
        (self.project/'AGENTS.md').write_bytes(b'# Own rules\r\nDo not erase.  \r\n')
        (self.project/'code.txt').write_text('business data')
        self.before=tree(self.project)
    def tearDown(self):self.temp.cleanup()
    def install(self):return tool.install(ROOT,self.root,self.skills,True,False)
    def clone(self):
        p=self.base/'new-source'
        shutil.copytree(ROOT,p,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        return p
    def new_release(self):
        p=self.clone()
        for f in p.rglob('*'):
            if f.is_file() and f.suffix in ('.md','.json') and f.name!=MANIFEST:
                f.write_text(f.read_text().replace('4.0.0-rc.2','4.0.0-rc.3-test'))
        (p/'VERSION').write_text('4.0.0-rc.3-test\n')
        build(p);return p

    def test_01_preview_has_no_writes(self):
        r=tool.install(ROOT,self.root,self.skills,False,False)
        self.assertEqual(r['status'],'preview');self.assertFalse(self.root.parent.exists())
        self.assertEqual(tree(self.project),self.before)
    def test_02_install_eight_full_entries(self):
        r=self.install();self.assertEqual(r['skill_entries'],8)
        self.assertEqual({p.name for p in self.skills.iterdir()},set(SKILLS))
        for name in SKILLS:
            s=(self.skills/name/'SKILL.md').read_text()
            self.assertIn(f'name: {name}',s);self.assertIn(str(self.root),s)
            self.assertGreater(len(s),900)
            self.assertNotIn('](../../',s)
        self.assertFalse((self.project/'.pdca').exists())
    def test_03_check_installed_and_snapshot(self):
        self.install();r=tool.check_install(self.root,self.skills)
        self.assertEqual(r['status'],'checked');self.assertEqual(r['host_acceptance'],'NOT_RUN')
        state=read_json(self.root/tool.STATE)
        snap=Path(state['snapshot']);m=verify_release(snap,True)
        self.assertEqual(sum(p.is_file() for p in snap.rglob('*')),len(m['active'])+1)
    def test_04_repeat_is_idempotent(self):
        self.install();a=tree(self.root);b=tree(self.skills)
        r=self.install();self.assertEqual(r['status'],'already_installed')
        self.assertEqual(a,tree(self.root));self.assertEqual(b,tree(self.skills))
    def test_05_foreign_entry_blocks_all_before_writes(self):
        p=self.skills/'pdca-do';p.mkdir(parents=True);(p/'SKILL.md').write_text('foreign')
        with self.assertRaises(Invalid):self.install()
        self.assertFalse(self.root.exists());self.assertEqual((p/'SKILL.md').read_text(),'foreign')
        self.assertEqual(len(list(self.skills.iterdir())),1)
    def test_06_modified_export_blocks_update_and_uninstall(self):
        self.install();p=self.skills/'pdca-act/SKILL.md';p.write_text('local edits')
        before=tree(self.root)
        for call in (lambda:self.install(),lambda:tool.uninstall(self.root,self.skills,True)):
            with self.assertRaises(Invalid):call()
        self.assertEqual(p.read_text(),'local edits');self.assertEqual(tree(self.root),before)
    def test_07_added_file_in_skill_is_not_deleted(self):
        self.install();p=self.skills/'pdca/private.txt';p.write_text('user data')
        with self.assertRaises(Invalid):tool.uninstall(self.root,self.skills,True)
        self.assertEqual(p.read_text(),'user data')
    def test_08_foreign_symlink_blocks(self):
        self.skills.mkdir(parents=True);other=self.base/'foreign';other.mkdir()
        (self.skills/'pdca').symlink_to(other,target_is_directory=True)
        with self.assertRaises(Invalid):self.install()
        self.assertFalse(self.root.exists());self.assertEqual(list(other.iterdir()),[])
    def test_09_nonempty_unowned_root_blocks(self):
        self.root.mkdir(parents=True);(self.root/'notes').write_text('keep')
        with self.assertRaises(Invalid):self.install()
        self.assertEqual((self.root/'notes').read_text(),'keep')
    def test_10_local_owned_changes_block_update(self):
        self.install();p=self.root/'README.md';p.write_text('local knowledge changes')
        with self.assertRaises(Invalid):tool.install(self.new_release(),self.root,self.skills,True,True)
        self.assertEqual(p.read_text(),'local knowledge changes')
    def test_11_update_is_explicit_and_preserves_central_data(self):
        self.install();s=read_json(self.root/tool.STATE);old_snap=Path(s['snapshot']);before=tree(old_snap)
        sentinel=self.root/'records/tasks/real-task/private.md';sentinel.parent.mkdir();sentinel.write_text('do not lose')
        model=self.root/'ontology/projects/my-model.md';model.write_text('domain model')
        extra=self.root/'my-note.txt';extra.write_text('additional file')
        src=self.new_release()
        with self.assertRaises(Invalid):tool.install(src,self.root,self.skills,True,False)
        r=tool.install(src,self.root,self.skills,True,True)
        self.assertEqual(r['version'],'4.0.0-rc.3-test')
        self.assertEqual(tree(old_snap),before);self.assertEqual(sentinel.read_text(),'do not lose')
        self.assertEqual(model.read_text(),'domain model');self.assertEqual(extra.read_text(),'additional file')
        self.assertEqual(tool.check_install(self.root,self.skills)['status'],'checked')
    def test_12_snapshot_tampering_is_detected(self):
        self.install();snap=Path(read_json(self.root/tool.STATE)['snapshot'])
        f=snap/'USE-PDCA.md';f.chmod(0o644);f.write_text('tampered')
        with self.assertRaises(Invalid):self.install()
        with self.assertRaises(Invalid):tool.check_install(self.root,self.skills)
    def test_13_install_second_discovery_dir_same_center(self):
        self.install();other=self.base/'home/.claude/skills'
        tool.install(ROOT,self.root,other,True,False)
        self.assertEqual(tool.check_install(self.root,other)['skill_entries'],8)
        tool.uninstall(self.root,other,True)
        self.assertEqual(tool.check_install(self.root,self.skills)['skill_entries'],8)
    def test_14_second_root_cannot_take_same_entries(self):
        self.install();other=self.base/'another-center'
        with self.assertRaises(Invalid):tool.install(ROOT,other,self.skills,True,False)
        self.assertFalse(other.exists())
    def test_15_uninstall_only_entries_preserves_data_and_snapshots(self):
        self.install();f=self.root/'records/tasks/important';f.write_text('not a plugin cache')
        model=self.root/'ontology/projects/important';model.write_text('central model')
        snap=Path(read_json(self.root/tool.STATE)['snapshot']);before=tree(snap)
        r=tool.uninstall(self.root,self.skills,True)
        self.assertEqual(r['status'],'uninstalled');self.assertEqual(list(self.skills.iterdir()),[])
        self.assertEqual(f.read_text(),'not a plugin cache');self.assertEqual(model.read_text(),'central model')
        self.assertEqual(tree(snap),before)
        self.assertEqual(tool.uninstall(self.root,self.skills,True)['status'],'already_uninstalled')
        self.install();self.assertEqual(tool.check_install(self.root,self.skills)['status'],'checked')
    def test_16_register_preview_writes_nothing(self):
        self.install();before=tree(self.root)
        r=tool.register(self.root,str(self.project),'p','main',False)
        self.assertEqual(r['status'],'preview');self.assertEqual(tree(self.root),before)
        self.assertEqual(tree(self.project),self.before)
    def test_17_project_registration_is_central_and_has_no_approval(self):
        self.install();r=tool.register(self.root,str(self.project),'p','main',True)
        d=read_owned_md(Path(r['context_ref']))
        self.assertEqual(d['records_root'],str(self.root/'records'))
        self.assertEqual(d['target_writes'],[]);self.assertIsNone(d['task_id'])
        self.assertEqual(r['agents_started'],0);self.assertEqual(r['authorization'],'NOT_GRANTED')
        self.assertEqual(tree(self.project),self.before)
    def test_18_registration_idempotence(self):
        self.install();a=tool.register(self.root,str(self.project),'p','main',True)
        before=tree(self.root)
        b=tool.register(self.root,str(self.project),'p','main',True)
        self.assertEqual(b['status'],'already_registered');self.assertEqual(tree(self.root),before)
    def test_19_multiple_projects_and_workspaces_share_resource_root(self):
        self.install()
        for pid,wid in [('p','main'),('p','branch'),('q','main')]:
            path=self.base/f'{pid}-{wid}';path.mkdir()
            tool.register(self.root,str(path),pid,wid,True)
            r=tool.locate(self.root,str(path));self.assertEqual(r['bindings'][0]['project_id'],pid)
            self.assertFalse((path/'.pdca').exists())
        ds=[d for _,d in tool.bindings(self.root)]
        self.assertEqual(len(ds),3);self.assertEqual(len({d['records_root'] for d in ds}),1)
    def test_20_rebind_and_duplicate_real_target_rejected(self):
        self.install();tool.register(self.root,str(self.project),'p','main',True)
        other=self.base/'other';other.mkdir()
        with self.assertRaises(Invalid):tool.register(self.root,str(other),'p','main',True)
        with self.assertRaises(Invalid):tool.register(self.root,str(self.project),'q','main',True)
    def test_21_project_alias_does_not_create_duplicate(self):
        self.install();tool.register(self.root,str(self.project),'p','main',True)
        alias=self.base/'alias';alias.symlink_to(self.project,target_is_directory=True)
        r=tool.locate(self.root,str(alias));self.assertEqual(r['status'],'found')
        with self.assertRaises(Invalid):tool.register(self.root,str(alias),'other','main',True)
    def test_22_no_implicit_upgrade_of_binding(self):
        self.install();r=tool.register(self.root,str(self.project),'p','main',True)
        p=Path(r['context_ref']);before=p.read_bytes()
        tool.install(self.new_release(),self.root,self.skills,True,True)
        r=tool.register(self.root,str(self.project),'p','main',True)
        self.assertEqual(r['version'],'4.0.0-rc.2');self.assertEqual(p.read_bytes(),before)
    def test_23_legacy_project_state_not_silently_registered(self):
        self.install();d=self.project/'.pdca';d.mkdir();f=d/'project-context.md';f.write_text('legacy record')
        with self.assertRaises(Invalid):tool.register(self.root,str(self.project),'p','main',True)
        self.assertEqual(f.read_text(),'legacy record');self.assertEqual(tool.bindings(self.root),[])
    def test_24_managed_data_symlink_rejected(self):
        self.install();d=self.root/'records/projects';d.rmdir()
        d.symlink_to(self.project,target_is_directory=True)
        with self.assertRaises(Invalid):tool.register(self.root,str(self.project),'p','main',True)
        self.assertEqual(tree(self.project),self.before)
    def test_25_target_and_center_cannot_overlap(self):
        self.install()
        with self.assertRaises(Invalid):tool.register(self.root,str(self.root),'p','main',True)
        with self.assertRaises(Invalid):tool.register(self.root,str(self.root.parent),'p','main',True)
    def test_26_locate_subdirectory_without_scanning_task_contents(self):
        self.install();tool.register(self.root,str(self.project),'p','main',True)
        sub=self.project/'src';sub.mkdir()
        r=tool.locate(self.root,str(sub));self.assertEqual(r['status'],'found')
        self.assertEqual(r['bindings'][0]['workspace_id'],'main')
    def test_27_missing_binding_reports_unregistered(self):
        self.install();r=tool.locate(self.root,str(self.project))
        self.assertEqual(r['status'],'unregistered');self.assertFalse((self.project/'.pdca').exists())
    def test_28_spaces_unicode_and_hash_path_render(self):
        root=self.base/'中文 #资源/center';skills=self.base/'中文 skills/discovery'
        tool.install(ROOT,root,skills,True,False)
        self.assertEqual(tool.check_install(root,skills)['status'],'checked')
        s=(skills/'pdca-do/SKILL.md').read_text();self.assertIn('%23',s)
    def test_29_cli_default_home_and_explicit_apply(self):
        env=dict(os.environ,HOME=str(self.base/'cli-home'),PYTHONDONTWRITEBYTECODE='1')
        def run(*args):
            r=subprocess.run([str(ROOT/'setup'),*args],cwd=self.project,env=env,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr+r.stdout);return json.loads(r.stdout)
        self.assertEqual(run()['status'],'preview')
        self.assertFalse((self.base/'cli-home').exists())
        self.assertEqual(run('--apply')['status'],'installed')
        self.assertEqual(run('check')['skill_entries'],8)
        self.assertEqual(run('register','--project',str(self.project),'--project-id','cli','--apply')['status'],'registered')
        self.assertEqual(tree(self.project),self.before)
    def test_30_lock_contention_fails_without_racing(self):
        self.install()
        with tool.locked(self.root,self.skills):
            r=subprocess.run([sys.executable,str(ROOT/'scripts/install.py'),'--root',str(self.root),'--skills-dir',str(self.skills),'--apply'],capture_output=True,text=True)
            self.assertEqual(r.returncode,1);self.assertIn('holds this namespace',r.stdout)
        self.assertEqual(tool.check_install(self.root,self.skills)['status'],'checked')
    def test_31_exception_rolls_back_owned_writes(self):
        original=tool.Transaction.atomic;calls=[0]
        def broken(p,data,mode):
            calls[0]+=1
            if calls[0]==5:raise OSError('injected write failure')
            return original(p,data,mode)
        with patch.object(tool.Transaction,'atomic',side_effect=broken):
            with self.assertRaises(OSError):self.install()
        self.assertFalse(self.root.exists());self.assertFalse(self.skills.exists())
    def test_32_source_manifest_tampering_blocks_install(self):
        s=self.clone();(s/'skills/pdca-do/SKILL.md').write_text('modified without manifest')
        with self.assertRaises(Invalid):tool.install(s,self.root,self.skills,True,False)
        self.assertFalse(self.root.exists())
    def test_33_installer_uninstall_does_not_claim_host_execution(self):
        self.install();r=tool.check_install(self.root,self.skills)
        self.assertEqual(r['host_discovery'],'NOT_RUN')
    def test_34_in_place_first_install_preserves_extra_records(self):
        s=self.clone();d=s/'records/tasks';d.mkdir(parents=True);f=d/'prior';f.write_text('prior record')
        r=tool.install(s,s,self.skills,True,False)
        self.assertEqual(r['status'],'installed');self.assertEqual(f.read_text(),'prior record')
    def test_35_new_source_cannot_overwrite_user_extension(self):
        self.install();f=self.root/'future.md';f.write_text('user extension')
        src=self.new_release();(src/'future.md').write_text('new release file');build(src)
        with self.assertRaises(Invalid):tool.install(src,self.root,self.skills,True,True)
        self.assertEqual(f.read_text(),'user extension')

    def test_36_binding_outside_central_snapshot_rejected(self):
        self.install();r=tool.register(self.root,str(self.project),'p','main',True)
        f=Path(r['context_ref']);d=read_owned_md(f)
        d['protocol_baseline_ref']=str(self.project/'protocol-release.md')
        d['manifest_ref']=str(self.project/MANIFEST)
        f.write_bytes(tool.md_document(d,'invalid relocated rules'))
        with self.assertRaises(Invalid):tool.locate(self.root,str(self.project))
    def test_37_binding_version_mismatch_rejected(self):
        self.install();r=tool.register(self.root,str(self.project),'p','main',True)
        f=Path(r['context_ref']);d=read_owned_md(f);d['protocol_revision']='invented'
        f.write_bytes(tool.md_document(d,'invalid version'))
        with self.assertRaises(Invalid):tool.register(self.root,str(self.project),'p','main',True)
    def test_38_binding_snapshot_tamper_rejected(self):
        self.install();r=tool.register(self.root,str(self.project),'p','main',True)
        d=read_owned_md(Path(r['context_ref']));f=Path(d['protocol_baseline_ref'])
        f.chmod(0o644);f.write_text('tampered rules')
        with self.assertRaises(Invalid):tool.locate(self.root,str(self.project))
    def test_39_manifest_cannot_install_into_mutable_records(self):
        src=self.clone();m=verify_release(src)
        m['files']['records/tasks/overwrite']=digest(b'payload')
        (src/MANIFEST).write_text('# malicious manifest\n```json\n'+json.dumps(m)+'\n```\n')
        with self.assertRaises(Invalid):tool.install(src,self.root,self.skills,True,False)
        self.assertFalse(self.root.exists())
    def test_40_central_data_not_software_owned_or_removed(self):
        self.install();state=read_json(self.root/tool.STATE)
        self.assertFalse(any(p.startswith(('records/','ontology/projects/')) for p in state['files']))
        data=self.root/'records/resources/held.md';data.write_text('backend state still held')
        tool.uninstall(self.root,self.skills,True)
        self.assertEqual(data.read_text(),'backend state still held')


class DefinitionTests(unittest.TestCase):
    """Static regression pins, explicitly not behavioral Agent tests."""
    def test_release(self):self.assertTrue(check(ROOT)['passed'])
    def test_phase_entries_do_not_spawn(self):
        for name in ('pdca-plan','pdca-do','pdca-check','pdca-act'):
            s=(ROOT/'skills'/name/'SKILL.md').read_text()
            self.assertIn('切换 Skill 不换 Agent',s);self.assertIn('不可路由就阻断',s)
            self.assertIn('原始用户回应',s);self.assertNotIn('context: fork',s)
    def test_scenes_have_read_only_method_mode(self):
        for name in SKILLS[5:]:
            s=(ROOT/'skills'/name/'SKILL.md').read_text()
            self.assertIn('已有阶段任务读取方法',s)
            self.assertIn('不要再次触发创建',s);self.assertIn('| Plan |',s);self.assertIn('| Act |',s)
    def test_resource_contract_no_timeout_release(self):
        s=(ROOT/'ontology/concept/resource-ownership.md').read_text()
        self.assertIn('canonical_actual_resources_across_all_projects_and_tasks',s)
        self.assertIn('lease_timeout_implies_release: false',s)
        self.assertIn('不是父Agent的阶段监督职责',s)
        self.assertIn('retained',s);self.assertIn('真实后端',s)
    def test_resource_templates_are_current(self):
        for name in ('resource-reservation','operation'):
            s=(ROOT/'templates'/f'{name}.md').read_text()
            self.assertIn('/v4',s);self.assertNotIn('历史指针',s)
    def test_no_local_data_root_in_current_control(self):
        s=(ROOT/'protocol-release.md').read_text();self.assertIn('records_root: PDCA_ROOT/records',s)
        s=(ROOT/'ontology/concept/pdca.md').read_text();self.assertIn('project_data_root: PDCA_ROOT/records',s)
    def test_user_controls_all_four_phases(self):
        s=(ROOT/'ontology/concept/pdca-ai-friendly-confirmation.md').read_text()
        self.assertIn('future_blanket_approval: false',s)
        self.assertIn('Do 完成不是 Check 授权',s)
    def test_domain_source_is_not_logs(self):
        s=(ROOT/'skills/pdca-ontology-modeling/SKILL.md').read_text()
        self.assertIn('稳定对象ID',s);self.assertIn('工作节点实例',s)
        s=(ROOT/'skills/pdca-ontology-conformance-verification/SKILL.md').read_text()
        self.assertIn('不递归创建新审查任务',s)

if __name__=='__main__':unittest.main()
