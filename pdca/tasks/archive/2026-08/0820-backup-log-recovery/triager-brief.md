# Triage Brief — 0820-backup-log-recovery

- **category**: enhancement
- **scenario_type**: research
- **summary**: 备份出来的 PG/MySQL 数据文件在非正常关闭下不一致，需用齐全日志（redo/WAL）恢复到等价正常关闭快照，再走既有物理直读转 Parquet 工具链。
- **current behavior**: 现有 mysqlbin/pgbin 物理直读仅覆盖正常关闭快照（T0325 边界：运行中复制需 undo/trx_sys、IN_PROGRESS/ItemIdIsDead，已划为范围外）。备份产物（在线/非正常关闭）直接直读会产生错误结果或漏读。
- **desired behavior**: 给出"有齐全 redo/WAL 日志如何恢复数据一致性"的完整方法论与路径选型：恢复起点定位、前滚（redo/WAL REDO）、回滚（undo/clog aborted）、一致性校验、与既有物理直读工具链的衔接。目标态 = 等价正常关闭快照。
- **key interfaces**: 备份产物（数据文件 + 日志集）、恢复引擎/工具、一致性校验方法、物理直读转换器（mysqlbin/pgbin）、可见性判定（T0325 复用）。
- **acceptance criteria**: 每条独立可验证，格式"运行 X 得到 Y"（详见 prd.md 验收标准）。
- **out of scope**: 恢复引擎实现（本任务仅选型+方法论）；Oracle；真实生产备份产物（环境无样本，容器构造验证）；增量/CDC。
- **information gaps**: 本机是否有可离线重放的 redo/WAL 参考实现源码；PG 恢复是否需要 pg_control 一致点；MySQL undo 表空间在备份产物中的形态。
- **dedup results**: 与 T0325（正常关闭边界，本任务为其范围外延伸）、T0300/T0301（版本转换，复用工具链）、T0163（逻辑导出性能，不同路径）无冲突。
- **recommended next steps**: 调研两类恢复路径（借力现有工具 vs 自研离线重放）适用边界 → 容器构造在线备份样本验证 → 产出路径选型报告 → 建议后续实现方向。