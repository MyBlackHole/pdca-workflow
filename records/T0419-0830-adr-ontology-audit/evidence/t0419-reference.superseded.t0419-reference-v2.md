# T0419 引用改写审计

## 改写文件（docs/adr → ontology 决策记录）
- README.md（目录树注释）
- AGENTS.md（硬决策同步位置）
- pdca/CONTEXT.md（术语表 ADR 定义 + dependencies 引用 ADR-0017 → pdca-task 决策背景）
- flows/flow-plan/SKILL.md（不可逆决策写入位置）
- skills/grilling/SKILL.md
- skills/domain-modeling-work/SKILL.md（硬决策/ADR 格式/扫描目录/查看已有 共 5 处）
- skills/improve-codebase-architecture/SKILL.md
- skills/tdd/SKILL.md
- templates/to-spec/SPEC.md（两处）
- docs/project-architecture-design.md
- docs/ONTOLOGY_GUIDE.md（ADR-0036 引用）
- ontology/README.md（ADR-0035/0036 引用）
- ontology/concept/pdca-architecture-review-metrics.md（ADR-0025 悬空引用）
- knowledge/linux-epoll-eventloop/rpc-conn-idle-reclaim.md（ADR-0016 悬空引用）

## 残留核对
- grep `scripts/SKILL/flows/docs/templates` 无 `docs/adr` 残留（已验证）。
- 历史 `records/`、`pdca/journal/`、`pdca/tasks/` 下任务 PRD 保留为不可变记录（按 AC-6 例外），其 docs/adr 引用为历史溯源，不改动。
