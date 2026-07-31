# Triage Brief

## 分类

- category: enhancement
- scenario_type: development
- state: ready-to-plan

## 查重结果

- `T0119`：首次七维度 AI 友好度审查，已归档。
- `T0131`：八维度自我审查，已归档，但证据和生命周期状态存在不一致。
- 本任务不是重复审查，而是将已有发现工程化为可执行合约、环境诊断和可重复评测。
- `T0130` 已做过以行数和引用次数为主的压缩；本任务新增 token、重复度、信息密度、渐进披露及任务效果保持审查，不重复采用“越短越好”的假设。

## 已验证问题

1. `AGENTS.md` 引用的根目录 `SKILLS-INDEX.md` 不存在。
2. 当前环境没有 `pdca` CLI，但 `context-retrieval` 将其作为硬依赖。
3. 流程硬编码 `task()` 子代理接口，缺少能力协商。
4. `validate-gate.sh` 对 archive 阶段直接成功，不验证终态一致性。
5. T0131 为 `phase=archive`、`status=InProgress`、`states.archive=null`，仍被校验为通过。
6. T0131 缺少 `final_confirmation`，与入口规定的 Plan 门禁不一致。

## 待用户决策

- 第一轮实施是严格限定为 P0 安全与可执行性修复，还是同时纳入完整评测基准。
- skill 内容量审查是只产出量化报告，还是同时实施通过配对验证的精简。
- 是否修复历史任务数据，或仅报告存量异常并保证新增数据正确。
- 工具适配的目标边界：通用能力协议，还是同时实现当前平台适配器。
