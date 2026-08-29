# 试点 tls 域本体迁移与 record identity 保持

## 背景
父任务 T0399 已定稿 SSOT v3 实体本体模型（ontology/README.md）。本任务将其在 **tls 域**试点落地：把 `knowledge/` 下 16 个 tls 相关 md 物理迁移到 `ontology/`，按 v3 实体树组织（知识形态作 `KnowledgeArtifact` 子类实例，经 `guides` 挂接领域实体类），并保持 record identity（来源回链）。

## 范围
- **In**：`knowledge/` 下 16 个 tls 相关 md（见 migration-plan.md 清单）。
- **Out**：`records/*/evidence/` 下的 tls 代码/日志文件（约 20 个）留待 T0403 全量；`flows/`、`skills/`、`task.json` 等 PDCA 机制层不动（ADR-0030）。

## 验收标准
- [ ] AC-1: 16 个文件全部物理迁入 `ontology/<type>/<slug>.md`；`type` == 父目录名且 ∈ v3 受控词汇
- [ ] AC-2: 建立类节点层次（Entity 谱系）；`specializes` 形成以 `Entity` 为根的有向无环树
- [ ] AC-3: 每个 KnowledgeArtifact 实例含结构化 `attributes[]`（至少 applicability/constraints/testable_signal 之一，机读）
- [ ] AC-4: 每个 KnowledgeArtifact 实例至少 1 条 `guides` 指向 DomainEntity/Process 类节点
- [ ] AC-5: `ontology-validate.py` 对 `ontology/` 全 PASS（覆盖 AC-1~AC-6）
- [ ] AC-6: record identity 保持（节点 `source_task` 回链 + 原位置 redirect）
- [ ] AC-7: `records/*/evidence/` 的 tls 代码/日志文件不在本任务迁移

### 声明的测试接缝
- seam: scripts/ontology-validate.py -> ontology/
- seam: tests/test_ontology_validate.py -> scripts/ontology-validate.py

## 收敛条件
- `python3 scripts/ontology-validate.py --ontology-dir ontology` 退出码 0。
- 16 文件全部就位且 GUIDES 覆盖；类节点树无环。
- 来源回链字段齐备，原位置 redirect 无丢失引用。
