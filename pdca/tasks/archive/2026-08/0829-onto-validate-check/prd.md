# 实现 ontology-validate.py 与 ontology-check skill 门禁

## 验收标准
- [ ] AC-1: `ontology-validate.py` 校验"目录即真理"——资产 frontmatter `type` 必须等于其所在 `<type>/` 父目录名，违规时报错并指出文件
- [ ] AC-2: 校验关系与领域引用非空悬——`relations.*` 与 `domain` 中引用的 ontology id 必须在 `ontology/` 中存在对应节点
- [ ] AC-3: 校验关系无环——`specializes`/`instance_of`/`composed_of`/`part_of`/`depends_on`/`relates_to` 构成的引用图必须为 DAG，检测到环时报错
- [ ] AC-4: 校验属性→测试覆盖——每个 `attributes[].testable_signal` 非空，且可派生测试回链本体 `id`
- [ ] AC-5: `skills/ontology-check/SKILL.md` 定义新资产写入门禁流程（合法 `type`、引用非空悬、`attributes` 有测试覆盖），并说明与 `ontology-validate.py` 的衔接
- [ ] AC-6: 用现有 `ontology/` 资产（README 说明 + schema）冒烟运行 `ontology-validate.py`，产出合规/违规报告且可解析

### 声明的测试接缝
- seam: tests/test_ontology_validate.py -> scripts/ontology-validate.py

## 范围与边界
- 仅实现校验与门禁，不执行任何知识迁移（迁移在 T0402/T0403）
- 不修改既有 flows/skills/task.json 机制
