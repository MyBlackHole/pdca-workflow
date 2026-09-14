# 模板：草稿不等于运行记录

<!-- pdca:current-template-version:start -->
当前基础模板 `protocol_revision=3.4.11`；实际采用固定[发布清单](../protocol-release.md)及其摘要。
<!-- pdca:current-template-version:end -->

schema 与资产 revision 独立演进；现有 work-node/baseline/delivery/work-tree 及控制/测试 schema 不机械升级。模板的 protocol_revision 是本分发快照的采用版本，不表示同号 schema。空字段/fixture 不产生授权、运行或 PASS。

| 场景 | 模板 |
|---|---|
| 启动与当前基线 | [task](task.md)、[dispatch](dispatch.md)、[capability-check](capability-check.md)、[baseline](baseline.md)、[subject-snapshot](subject-snapshot.md) |
| 确认与逐项门禁 | [request](request.md)、[response](response.md)、[request-decision](request-decision.md)、[gate-check](gate-check.md)、[transition](transition.md) |
| 测试与回归 | [test-suite](test-suite.md)、[test-case](test-case.md)、[test-case-binding](test-case-binding.md)、[test-run](test-run.md)、[regression-extension](regression-extension.md)、[rework](rework.md)、[work-budget](work-budget.md) |
| 证据与交付 | [evidence](evidence.md)、[observation-binding](observation-binding.md)、[claim-review](claim-review.md)、[review-package](review-package.md)、[conclusion](conclusion.md)、[delivery](delivery.md)、[archive-receipt](archive-receipt.md)、[conformance-review](conformance-review.md) |
| 目标树与技术就绪 | [work-node](work-node.md)、[work-tree](work-tree.md)、[tree-spec](tree-spec.md)、[tree-manifest](tree-manifest.md)、[tree-readiness](tree-readiness.md)、[scenario-coverage](scenario-coverage.md) |
| 依赖与整树确认 | [dependency-snapshot](dependency-snapshot.md)、[dependency-check](dependency-check.md)、[tree-confirmation-request](tree-confirmation-request.md)、[tree-confirmation-response](tree-confirmation-response.md)、[tree-freeze-receipt](tree-freeze-receipt.md) |
| 工作产物发布 | [work-release-manifest](work-release-manifest.md)、[work-release-receipt](work-release-receipt.md) |
| 控制、资源、异常 | [wait-policy](wait-policy.md)、[control-event](control-event.md)、[control-state](control-state.md)、[resource-reservation](resource-reservation.md)、[operation](operation.md)、[termination](termination.md)、[integrity-event](integrity-event.md) |
| 知识复用与发布 | [reuse-decision](reuse-decision.md)、[ontology-revision](ontology-revision.md)、[ontology-release](ontology-release.md)、[ontology-publication](ontology-publication.md)、[knowledge-catalog](knowledge-catalog.md)、[ontology-adoption](ontology-adoption.md)、[ontology-impact](ontology-impact.md)、[ontology-advisory](ontology-advisory.md) |

每个逻辑对象须唯一身份、明确作用域、固定引用；可以在一个不可变文件中分节承载多个对象，不要求每字段一个文件或新服务。字节摘要只证明完整性，身份/时间/写权来自真实宿主。只读复核另存完整性事件，不修改旧records。

历史模式与旧验证保留在migration；新任务按当前权威运行，不能仅改旧schema就宣称新证据齐全。未来产物可尚未生成，必需测试语义不能尚未定义。

## 显式跨项目接入

[project-workspace](project-workspace.md)、[project-task-context](project-task-context.md)、[project-index](project-index.md)是 cross-project.2 的独立模板；两个根由单变量入口推导，标识内部生成，不要求用户填写四个参数。shared/split与入口事实显式保留。旧task使用已有extensions；baseline通过已有resource_scope与契约正文固定同一上下文，不向通用记录加入未登记顶层字段。其他模板继续复用，不为目标项目复制一整套。
