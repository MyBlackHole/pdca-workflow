# T0141 Triage

- 分类：enhancement
- 场景：development
- 查重：T0135 建立严格 evidence 合约，T0140 提出本改进，但当前没有可执行 convergence 支撑验证器；本任务是独立实现周期。
- Claim 核验：
  - `scripts/pdca_core.py:evidence_issues` 验证 manifest schema、文件边界、size 和 digest。
  - 当前代码不解析 PRD AC，也不检查所有 AC 是否被 evidence criteria 覆盖。
  - `meta.convergence` 是字符串数组，没有到 AC 或 evidence ID 的结构化映射。
- 关键缺口：需要确认映射载体；推荐保留 Plan 中的 convergence 原文，并在 record 中增加 Check 阶段生成的结构化映射，避免执行后反向修改计划目标。
- 推荐下一步：确认映射边界后完成 PRD、错误码、测试矩阵和终审。
