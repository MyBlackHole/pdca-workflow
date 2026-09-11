# T2156 triage brief（PDCA设计核心 B/A/C 命名适配性复核）

- **scenario_type**: research
- **current behavior**: T2153 已完成全库调研并归档，`ontology:decision/t2153-opt-backlog` 承载 P0/P1/P2 优化候选；本次请求再次提出检查“PDCA 流程本体核心是否需要优化”。
- **refined goal**: 用户纠偏为检查 `ontology:concept/pdca` 里“设计核心：本体树驱动（B→A→C）”的 A、B、C 是否应成为核心场景划分；六个具体场景不作为核心场景保留，只作为 tool/skill 选择层处理。
- **expected behavior**: 不重复全库扫描，聚焦当前 B=建树、A=按树实现、C=逐项校验是否比六个 `scenario_type` 更适合作为核心路由，产出候选方案与迁移边界。
- **boundary**: 只调研场景分层和命名适配性，不直接改权威流程正文；若建议改动，后续迁移另立 Improvement Task。
- **dedupe**: 与 T2153 主题相近，但 T2153 已 archive；本任务定位为二次复核与收敛，不是重复立项。
