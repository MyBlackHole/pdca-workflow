# ADR-0003: Convergence 证据映射与 Do→Check 硬门禁

日期: 2026-07-28
状态: Accepted

## 背景

当前 evidence gate 能验证证据文件、摘要和单项 criteria，但不能证明全部 PRD 验收条件已覆盖，也不能证明 Plan 中每条 `meta.convergence` 有验收条件和证据支持。`verify-convergence` 依赖 AI 手工比对，可能遗漏缺失或悬空映射。

## 候选方案

### A. 继续在 Check 阶段由 AI 手工检查

- 优点：无需新增结构。
- 缺点：结果不可重复，提示可能被忽略，不能稳定阻止无证据结论。

### B. 执行后修改 `task.meta.convergence`，加入 AC 和 evidence ID

- 优点：数据集中在 task。
- 缺点：执行结果反向修改 Plan 原始目标，削弱计划基线的可审计性。

### C. 在 record evidence 中登记独立 `convergence.json`，并作为 Do→Check 硬门禁

- 优点：保留 Plan 原文；映射可由 JSON Schema 和代码确定性验证；登记摘要后不可静默修改。
- 缺点：Do 收尾增加一个小型结构化产物。

## 决策

采用 C：

1. `task.meta.convergence` 保持 Plan 阶段的原始目标。
2. Do 收尾生成并登记固定 ID、kind 均为 `convergence-map` 的结构化映射。
3. Do→Check 转换检查 PRD AC 全覆盖，以及每条 convergence 到 AC、evidence ID 的有效支撑链。
4. convergence map 只描述支撑关系，不得作为验收通过证据。
5. 已完成的阶段转换不追溯重放；所有未来 Do→Check 转换统一执行新门禁，不增加旧格式兼容分支。

## 影响

- 缺 AC、未知 AC、悬空 evidence ID、文本漂移或证据不支持指定 AC 时，阶段转换失败并返回稳定错误码。
- Check 仍负责判断证据语义是否充分；程序只验证可确定的结构和引用关系。
- 需要新增 convergence schema、验证命令、阶段门禁集成和正反例。
