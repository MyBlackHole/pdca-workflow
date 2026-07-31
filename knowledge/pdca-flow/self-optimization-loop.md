# PDCA 自我优化反馈链

## 核心认识

流程问题记录只是自我优化的观测层。完整闭环必须同时具备：

1. **记录**：在流程事件发生时保存结构化问题、阶段、时间和证据。
2. **分析**：跨任务聚合问题代码、频次、影响和趋势，区分偶发执行错误与系统性流程缺陷。
3. **决策**：形成可追溯的改进候选，说明依据、影响范围、风险和预期效果。
4. **受控实施**：候选仍进入正常 Plan、Grill 和 final confirmation，不能由审计器直接修改权威流程。
5. **效果验证**：在后续周期比较问题发生率或门禁失败模式，判断改善、无效或退化，并把结果重新作为下一轮输入。

## 设计边界

- 审计发现是诊断信号，不是自动变更授权。
- 单次 fail 不足以证明流程规则需要修改；需要结合频次、影响和根因。
- 控制产物不能循环自证：改进效果必须由后续周期的新执行证据支持。
- 自我优化不能绕过 final confirmation、Check verdict 或 Act disposition。

## 最小反馈模型

`flow-audit records → issue backlog → improvement candidate → confirmed PDCA task → post-change observations → effectiveness verdict`

该模型把“发现问题”和“授权改流程”明确分离，同时使每次改进都能追溯到原始问题记录及后续效果证据。

## 首次实现护栏

首次将模型落地时，应把下列护栏视为闭环合约的一部分：

1. **事实不可变且可重试**：每个 occurrence 都是独立文件；由调用方稳定幂等键确定事件 ID。相同内容重试只能返回 `unchanged`，相同键的不同内容必须拒绝，不能通过更新共享日志修正历史。
2. **投影可删除重建**：issue backlog 只是按版本化 fingerprint 生成的派生产物。稳定排序、规范化内容和输入 digest 让两次聚合可比较；损坏事实输入必须带路径 fail-closed，不能静默跳过。
3. **确认必须精确绑定治理对象**：用户确认不能只证明“曾经同意”。decision receipt 必须绑定 action、issue ID 和 candidate ID；candidate 先 dry-run，promotion 只创建 `phase=plan` 的严格任务，不写 final confirmation，也不自动推进阶段。
4. **cutover 是显式事实**：历史 `flow-audit/v1` 保持不变。只有全局 cutover receipt 存在后，转换审计问题才写入新 occurrence，避免把新旧观测模型混为同一事实层。
5. **效果是下一周期的判定，不是候选自证**：冻结 baseline、指标和观察计划后，verdict 只能为 improved、neutral 或 regressed。只有 improved 可形成 verified decision；regressed 只生成待用户确认的回滚候选。

这些结论目前由 Linux 上的确定性 CLI、并发和端到端夹具验证。它们不等同于真实模型成功率，也不包含 Windows 文件锁兼容性；若扩大运行平台，必须先补充锁适配和配对回归。
