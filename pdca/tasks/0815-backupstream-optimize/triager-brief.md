# Triage Brief — 0815-backupstream-optimize

- **category**: enhancement
- **scenario_type**: development
- **summary**: 对 backupstream 80.0.0 程序做进一步优化（方向待定，需 Grill 澄清）
- **current behavior**: v80 已完成非阻塞 plain ingress 前置隔离；业务层 TREE/FILE/System RPC 仍占阻塞 worker；存在 1 个 -Wmisleading-indentation 警告（与文档"0 warnings"不符）；文档滞后（TEST_REPORT.md 标注 27.0）。
- **desired behavior**: 待澄清（候选：架构演进 v81 后续控制帧非阻塞化 / 警告清零与门禁修复 / 文档一致性刷新 / 性能量化）
- **key interfaces**: 非阻塞 ingress、reactor、会话池、work_pool、TREE/FILE 状态机、数据通道
- **acceptance criteria**: 待定（依赖 Grill 结果，每条件需"运行 X 得到 Y"可验证）
- **out of scope**: 待定
- **information gaps**: 用户"进一步优化"的具体意图未指明
- **dedup results**: 无重复（T0287 为架构分析已归档；无 out-of-scope 拒绝记录）
- **recommended next steps**: Grill 澄清优化目标（正确性/性能/资源/架构/门禁），再定 PRD
