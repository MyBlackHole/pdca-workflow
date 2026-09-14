"""Current document/link regression checks, not host or Agent acceptance."""
from pathlib import Path
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
SCENES = ('pdca-ontology-modeling', 'pdca-ontology-projection',
          'pdca-ontology-conformance-verification')


def current_documents():
    yield from sorted((ROOT / 'skills').rglob('SKILL.md'))
    for path in sorted((ROOT / 'ontology').rglob('*.md')):
        content = path.read_text()
        if not content.startswith('---\n'):
            continue
        frontmatter = content.split('---', 2)[1]
        if re.search(r'^(schema: pdca\.contract/v4|authority: normative)$',
                     frontmatter, re.MULTILINE):
            yield path


class CurrentLinkTests(unittest.TestCase):
    def test_current_documents_have_resolvable_relative_links(self):
        for path in current_documents():
            for target in re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)', path.read_text()):
                target = target.strip().strip('<>')
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                with self.subTest(document=str(path.relative_to(ROOT)), target=target):
                    resolved = (path.parent / unquote(parsed.path)).resolve()
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
        content = (ROOT / 'skills/pdca-ontology-modeling/SKILL.md').read_text()
        self.assertIn('稳定对象ID', content)
        self.assertIn('工作节点实例', content)
        content = (ROOT / 'skills/pdca-ontology-conformance-verification/SKILL.md').read_text()
        self.assertIn('不递归创建新审查任务', content)


if __name__ == '__main__':
    unittest.main()
