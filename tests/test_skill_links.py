"""Current document/link regression checks, not host or Agent acceptance."""
from pathlib import Path
import json
import re
import subprocess
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SHAPES = ROOT / 'ontology/contracts/record-shapes'
# The 18 active sources were 17 v4 records plus a format index. Keep this
# explicit migration inventory independent of the soon-to-be-removed files.
FORMER_TEMPLATE_CONTRACTS = {
    'project-task-context.md': ('project-task-context.md', 'pdca.project-task-context/v4'),
    'task.md': ('task.md', 'pdca.task/v4'),
    'agent-assignment.md': ('agent-assignment.md', 'pdca.agent-assignment/v4'),
    'dispatch.md': ('dispatch.md', 'pdca.dispatch/v4'),
    'capability-check.md': ('capability-check.md', 'pdca.capability-check/v4'),
    'baseline.md': ('baseline.md', 'pdca.baseline/v4'),
    'request.md': ('request.md', 'pdca.request/v4'),
    'response.md': ('response.md', 'pdca.response/v4'),
    'request-decision.md': ('request-decision.md', 'pdca.request-decision/v4'),
    'transition.md': ('transition.md', 'pdca.transition-receipt/v4'),
    'evidence.md': ('evidence.md', 'pdca.evidence/v4'),
    'conclusion.md': ('conclusion.md', 'pdca.conclusion/v4'),
    'delivery.md': ('delivery.md', 'pdca.delivery/v4'),
    'resource-reservation.md': ('resource-reservation.md', 'pdca.resource-reservation/v4'),
    'operation.md': ('operation.md', 'pdca.operation/v4'),
    'ontology-revision.md': ('ontology-revision.md', 'pdca.ontology-revision/v4'),
    'conformance-review.md': ('conformance-review.md', 'pdca.conformance-review/v4'),
    'README.md': ('index.md', None),
}
PHASES = ('pdca-plan', 'pdca-do', 'pdca-check', 'pdca-act')
SCENES = ('pdca-model', 'pdca-implement', 'pdca-verify')
REMOVED_PATHS = (
    'setup', 'scripts/install.py', 'scripts/common.py',
    'scripts/build_manifest.py', 'scripts/check_release.py',
    'tests/test_install.py', 'release-manifest.md', 'protocol-release.md',
    'SKILL.md', 'USE-PDCA.md', 'migration/v4.0.0-rc.2-MIGRATION.md',
    'bootstrap', 'templates',
)


def current_documents():
    for relative in ('AGENTS.md', 'README.md', 'INSTALL.md',
                     'ontology/README.md', 'ontology/INDEX.md'):
        yield ROOT / relative
    yield from sorted((ROOT / 'tests').glob('*.md'))
    yield from sorted((ROOT / 'skills').rglob('*.md'))
    for path in sorted((ROOT / 'ontology').rglob('*.md')):
        content = path.read_text()
        if not content.startswith('---\n'):
            continue
        frontmatter = content.split('---', 2)[1]
        if re.search(r'^(schema: pdca\.contract/v4|authority: normative)$',
                     frontmatter, re.MULTILINE):
            yield path


class CurrentLinkTests(unittest.TestCase):
    def test_superseded_package_layers_are_absent(self):
        for relative in REMOVED_PATHS:
            with self.subTest(removed_path=relative):
                path = ROOT / relative
                self.assertFalse(path.exists() or path.is_symlink(), relative)

    def test_current_documents_have_resolvable_relative_links(self):
        for path in current_documents():
            for target in re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)', path.read_text()):
                target = target.strip().strip('<>')
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                with self.subTest(document=str(path.relative_to(ROOT)), target=target):
                    resolved = (path.parent / unquote(parsed.path)).resolve()
                    for relative in REMOVED_PATHS:
                        removed = ROOT / relative
                        self.assertFalse(resolved == removed or removed in resolved.parents,
                                         f'link to removed path: {resolved}')
                    self.assertTrue(resolved.exists(), f'missing target: {resolved}')

    def test_current_documents_do_not_depend_on_removed_directories(self):
        for path in current_documents():
            with self.subTest(document=str(path.relative_to(ROOT))):
                content = path.read_text()
                self.assertNotIn('bootstrap/', content)
                self.assertNotIn('templates/', content)

    def test_active_record_contracts_preserve_schema_and_examples(self):
        for source, (target, schema) in FORMER_TEMPLATE_CONTRACTS.items():
            with self.subTest(former_template=source):
                path = SHAPES / target
                self.assertTrue(path.is_file(), f'missing record contract: {target}')
                content = path.read_text()
                self.assertIn('schema: pdca.contract/v4', content)
                if schema is not None:
                    self.assertIn('## 示例', content)
                    self.assertIn(f'schema: {schema}', content)
                else:
                    for contract, _ in FORMER_TEMPLATE_CONTRACTS.values():
                        if contract != target:
                            self.assertIn(f']({contract})', content)

    def test_central_records_and_models_are_trackable_but_private_data_is_not(self):
        cases = {
            'records/tasks/example/task.md': False,
            'records/projects/example/workspaces/main/project-context.md': False,
            'ontology/projects/example/model.md': False,
            'records/tasks/example/artifacts/private/evidence.md': True,
            'records/projects/example/private/secret.md': True,
            '.env': True,
            '.pdca-install.json': True,
            '.pdca-install-test.lock': True,
            'tests/__pycache__/example.pyc': True,
        }
        for path, ignored in cases.items():
            with self.subTest(path=path):
                result = subprocess.run(
                    ['git', 'check-ignore', '--no-index', '--quiet', path],
                    cwd=ROOT, capture_output=True, text=True,
                )
                self.assertIn(result.returncode, (0, 1), result.stderr)
                self.assertEqual(result.returncode == 0, ignored, path)


class SafetyDefinitionTests(unittest.TestCase):
    """Safety assertions migrated from the old installer-independent checks."""
    def test_read_only_git_queries_disable_optional_locks(self):
        for path in current_documents():
            content = path.read_text()
            for command in re.finditer(r'\bgit (?:rev-parse HEAD|status --porcelain)\b',
                                       content):
                with self.subTest(document=str(path.relative_to(ROOT)),
                                  command=command.group()):
                    self.assertTrue(content[:command.start()].endswith('GIT_OPTIONAL_LOCKS=0 '),
                                    'read-only queries must disable optional index writes')

    def test_assist_has_one_catalog_entry_and_index_link(self):
        catalog = json.loads((ROOT / 'skills/catalog.json').read_text())
        entries = catalog['skills']
        matches = [entry for entry in entries if entry['name'] == 'pdca-assist']
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['path'], 'skills/pdca-assist/SKILL.md')
        self.assertEqual(sum(entry['path'] == 'skills/pdca-assist/SKILL.md'
                             for entry in entries), 1)
        self.assertEqual({entry['name'] for entry in entries},
                         {'pdca', 'pdca-assist', *PHASES, *SCENES})
        self.assertIn('[pdca-assist](pdca-assist/SKILL.md)',
                      (ROOT / 'skills/README.md').read_text())

    def test_current_package_version_is_consistent(self):
        version = (ROOT / 'VERSION').read_text().strip()
        catalog = json.loads((ROOT / 'skills/catalog.json').read_text())
        self.assertEqual(version, '5.0.0-rc.1')
        self.assertEqual(catalog['version'], version)
        for entry in catalog['skills']:
            with self.subTest(skill=entry['name']):
                content = (ROOT / entry['path']).read_text()
                self.assertIn(f'version: {version}', content)

    def test_assist_is_bound_read_only_and_suggestion_only(self):
        path = ROOT / 'skills/pdca-assist/SKILL.md'
        self.assertTrue(path.is_file(), 'missing explicit assistant Skill')
        content = path.read_text()
        for requirement in ('用户显式调用', '当前已绑定的 TARGET_ROOT',
                            '不扫描其他项目', '用户选择', '不创建任务',
                            '不启动阶段', '不派发 Agent', '不创建记录',
                            '不创建资源预约', '不写入 TARGET_ROOT',
                            '任务地图', '项目上下文', '证据审阅', '协作交接',
                            '每个视角最多一个候选动作', '影响', '所需授权',
                            'git rev-parse HEAD', 'git status --porcelain'):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, content)

    def test_binding_records_git_state_and_separates_write_from_commit_consent(self):
        content = (ROOT / 'skills/pdca/SKILL.md').read_text()
        for requirement in ('记录写入授权', 'Git 提交授权', '另行明确',
                            'git rev-parse HEAD', 'git status --porcelain',
                            'project_id', 'workspace_id', 'target_root',
                            'pdca_root', 'records_root', 'rules_git_head',
                            'rules_git_status', '不自动提交',
                            '不在目标项目创建 `.pdca/`'):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, content)

    def test_assist_host_acceptance_remains_unverified(self):
        content = (ROOT / 'tests/host-acceptance.md').read_text()
        self.assertIn('catalog.json', content)
        self.assertIn('pdca-assist', content)
        self.assertNotIn('八个入口', content)
        rows = [line for line in content.splitlines()
                if re.match(r'\| H\d+ \|', line)]
        self.assertTrue(rows)
        self.assertTrue(all(row.endswith('| NOT_RUN |') for row in rows))

    def test_project_binding_contracts_use_git_provenance(self):
        paths = ('ontology/contracts/project-workspace.md',
                 'ontology/contracts/entry-recovery.md',
                 'ontology/contracts/record-shapes/project-task-context.md')
        for relative in paths:
            with self.subTest(contract=relative):
                content = (ROOT / relative).read_text()
                self.assertIn('rules_git_head', content)
                self.assertIn('rules_git_status', content)
                self.assertIn('记录写入授权', content)
                self.assertNotIn('快照是本任务规则根', content)
                self.assertNotIn('安装器项目登记', content)
        shape = (SHAPES / 'project-task-context.md').read_text()
        for field in ('project_id', 'workspace_id', 'target_root', 'pdca_root',
                      'records_root', 'rules_git_head', 'rules_git_status'):
            self.assertRegex(shape, rf'(?m)^{field}: ')

    def test_current_recovery_and_index_use_git_not_removed_release_layers(self):
        for relative in ('ontology/contracts/entry-recovery.md',
                         'ontology/concept/pdca-recovery.md',
                         'ontology/INDEX.md', 'ontology/concept/pdca.md'):
            with self.subTest(document=relative):
                content = (ROOT / relative).read_text()
                self.assertNotIn('发布清单', content)
                self.assertNotIn('集中协议快照', content)
        recovery = (ROOT / 'ontology/concept/pdca-recovery.md').read_text()
        self.assertIn('rules_git_head', recovery)
        self.assertIn('rules_git_status', recovery)

    def test_phase_entries_do_not_spawn(self):
        for name in PHASES:
            with self.subTest(skill=name):
                content = (ROOT / 'skills' / name / 'SKILL.md').read_text()
                self.assertIn('切换 Skill 不换 Agent', content)
                self.assertIn('不可路由就阻断', content)
                self.assertIn('原始用户回应', content)
                self.assertNotIn('context: fork', content)

    def test_scenes_have_read_only_method_mode(self):
        for name in SCENES:
            with self.subTest(skill=name):
                content = (ROOT / 'skills' / name / 'SKILL.md').read_text()
                self.assertIn('已有阶段任务读取方法', content)
                self.assertIn('不要再次触发创建', content)
                self.assertIn('| Plan |', content)
                self.assertIn('| Act |', content)

    def test_resource_contract_no_timeout_release(self):
        content = (ROOT / 'ontology/concept/resource-ownership.md').read_text()
        self.assertIn('canonical_actual_resources_across_all_projects_and_tasks', content)
        self.assertIn('lease_timeout_implies_release: false', content)
        self.assertIn('不是父Agent的阶段监督职责', content)
        self.assertIn('retained', content)
        self.assertIn('真实后端', content)

    def test_resource_shapes_are_current(self):
        for name in ('resource-reservation', 'operation'):
            with self.subTest(shape=name):
                path = SHAPES / f'{name}.md'
                self.assertTrue(path.is_file())
                content = path.read_text()
                self.assertIn('/v4', content)
                self.assertNotIn('历史指针', content)

    def test_no_local_data_root_in_current_control(self):
        content = (ROOT / 'ontology/concept/pdca.md').read_text()
        self.assertIn('project_data_root: PDCA_ROOT/records', content)
        path = SHAPES / 'project-task-context.md'
        self.assertTrue(path.is_file())
        self.assertIn('records_root=PDCA_ROOT/records', path.read_text())

    def test_user_controls_all_four_phases(self):
        content = (ROOT / 'ontology/concept/pdca-ai-friendly-confirmation.md').read_text()
        self.assertIn('future_blanket_approval: false', content)
        self.assertIn('Do 完成不是 Check 授权', content)

    def test_domain_source_is_not_logs(self):
        content = (ROOT / 'skills/pdca-model/SKILL.md').read_text()
        self.assertIn('稳定层', content)
        self.assertIn('假设层', content)
        content = (ROOT / 'skills/pdca-verify/SKILL.md').read_text()
        self.assertIn('递归创建', content)


if __name__ == '__main__':
    unittest.main()
