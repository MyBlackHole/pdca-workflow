# T2153 triage brief（PDCA流程本体优化空间调研）

- **scenario_type**: research（纯结论性调研，优化清单与改进候选，无代码产出）
- **current behavior**: PDCA 流程本体（pdca 1.0.3/flow-do 1.0.2 + 四 flow + 门禁链）运行中；已知未立项项：退役机制、AC-5 收紧、transition 依赖校验、role/ 待补、ci 悬空引用（T2149 待定）
- **expected behavior**: 系统性扫描流程本体优化空间，分级清单 + research-report 过门禁 + 改进候选或无优化结论
- **boundary**: 只调研不实施；语义改动全部走后续 Improvement Task；不碰领域子树（bcachefs/zfs 等），聚焦 PDCA 流程本体（pdca/flow-*/门禁/任务机制）
- **evidence**: T2135 结构审查（archive）、T2148 治理结论（archive）、方向审查（ev2147-direction-review）
