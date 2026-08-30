# T0418 迁移清单（PDCA 流程本体化）

## AC-1 流程即本体实体（ontology/process/，type=process，specializes=ontology:concept/process）
- ontology/process/flow-plan.md
- ontology/process/flow-do.md
- ontology/process/flow-check.md
- ontology/process/flow-act.md

## AC-2 knowledge/pdca-flow 16 文件迁移映射（迁移后目录已删除）
| 原知识文件 | 本体节点 |
|---|---|
| knowledge/pdca-flow/architecture.md | ontology:concept/pdca-architecture |
| knowledge/pdca-flow/cli-behavior.md | ontology:concept/pdca-architecture |
| knowledge/pdca-flow/generic-ai-workflow-kernel.md | ontology:concept/pdca-architecture |
| knowledge/pdca-flow/executor-adapter-boundary.md | ontology:concept/executor-adapter |
| knowledge/pdca-flow/opencode-tmux-executor-adapter.md | ontology:concept/executor-adapter |
| knowledge/pdca-flow/external-project-workflow-injection.md | ontology:concept/executor-adapter |
| knowledge/pdca-flow/external-evidence-collection.md | ontology:concept/external-evidence-collection |
| knowledge/pdca-flow/destructive-cleanup-safety.md | ontology:concept/destructive-cleanup-safety |
| knowledge/pdca-flow/global-repo-config.md | ontology:concept/pdca-home |
| knowledge/pdca-flow/real-project-mechanism-validation.md | ontology:concept/real-project-mechanism-validation |
| knowledge/pdca-flow/real-usage-effectiveness-audit.md | ontology:concept/self-optimization-loop |
| knowledge/pdca-flow/record-knowledge-provenance.md | ontology:concept/knowledge-provenance |
| knowledge/pdca-flow/runtime-transition-coordinator.md | ontology:concept/runtime-transition-coordinator |
| knowledge/pdca-flow/self-optimization-loop.md | ontology:concept/self-optimization-loop |
| knowledge/pdca-flow/task-record-identity-invariants.md | ontology:concept/task-record-identity |
| knowledge/pdca-flow/timeline-integrity-gates.md | ontology:concept/timeline-integrity-gate |

## AC-3 knowledge/pdca-workflow 6 文件迁移映射（迁移后目录已删除）
| 原知识文件 | 本体节点 |
|---|---|
| knowledge/pdca-workflow/ai-friendly-confirmation.md | ontology:concept/pdca-ai-friendly-confirmation |
| knowledge/pdca-workflow/architecture-review-metrics.md | ontology:concept/pdca-architecture-review-metrics |
| knowledge/pdca-workflow/id-collision-remediation.md | ontology:concept/task-record-identity |
| knowledge/pdca-workflow/provable-skill-increments.md | ontology:concept/pdca-provable-skill-increments |
| knowledge/pdca-workflow/scenario-boundary-rule.md | ontology:concept/pdca-scenario-boundary-rule |
| knowledge/pdca-workflow/source-diagram-doc-verification.md | ontology:concept/pdca-source-diagram-doc-verification |

## AC-4 PDCA ADR 标注（superseded-by-ontology）
- docs/adr/ADR-0032-ontology-driven-pdca.md 已加 superseded-by-ontology 注记，决策沉淀至对应本体节点
- docs/adr/ADR-0033-ontology-guide-adoption.md 已加 superseded-by-ontology 注记，决策沉淀至对应本体节点
- docs/adr/ADR-0034-meta-ontology-gate.md 已加 superseded-by-ontology 注记，决策沉淀至对应本体节点
- docs/adr/ADR-0035-meta-ontology-gate-runtime.md 已加 superseded-by-ontology 注记，决策沉淀至对应本体节点
- docs/adr/ADR-0036-ontology-full-lifecycle-gate.md 已加 superseded-by-ontology 注记，决策沉淀至对应本体节点

## 说明
- 全部新节点经 scripts/ontology-validate.py 校验通过（见 evidence ontology-validate.json）。
- 迁移后 knowledge/pdca-flow/ 与 knowledge/pdca-workflow/ 目录已删除。
