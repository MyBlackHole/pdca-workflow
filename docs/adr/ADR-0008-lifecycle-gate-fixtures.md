# ADR-0008: 用真实生命周期夹具评测 PDCA 门禁

日期: 2026-07-30
状态: Accepted

## 背景

现有 AI 友好度 harness 对部分错误码直接构造或只做结构校验，未覆盖 Check 所需的 evidence/convergence、Act 所需的 conclusion/verdict/check confirmation，以及 archive 所需的 disposition。这会使“生命周期门禁已验证”的结论超出实际测试范围。

需要扩大评测覆盖，但不能为每个 scenario 复制同一组阶段语义，也不能用测试自身拼接预期错误码取代真实门禁。

## 候选方案

### A. 保持当前按 scenario 分散的单点故障夹具

- 优点：夹具数量少。
- 缺点：后续阶段缺失，且一些错误不经过实际 gate。

### B. 为六个 scenario 各复制完整生命周期矩阵

- 优点：表面覆盖数量高。
- 缺点：阶段门禁与 scenario 无关，复制会制造维护漂移和无判别力案例。

### C. 一个完整成功夹具加按转换分组的真实失败矩阵

- 优点：完整路径证明产物可协同存在；每个门禁至少有一个实际失败反例；共享语义避免按 scenario 重复。
- 缺点：临时仓库 fixture 需要构造最小有效 evidence、conclusion 和确认记录。

## 决策

选择 C：fixture 通过真实 `gate_issues` 或 `transition-phase.py` 构造一个 Plan→Do→Check→Act→archive 成功路径，并为 Plan→Do、Do→Check、Check→Act、Act→archive 分别注入至少一个关键缺失项。测试断言实际错误码和转换结果，不允许测试代码直接返回预期错误。

scenario 路由仍由独立路由合约测试；生命周期矩阵只负责共享的阶段语义。

## 影响

- fixture 工具需要最小有效 record、evidence manifest、convergence、conclusion、verdict、确认和 disposition 构造器。
- 需要稳定错误码、重复执行和跨 phase 清理测试。
- 场景数不因共享门禁成倍增长；route 和 lifecycle 两类失败可独立定位。
- T0160 已于 2026-07-30 完成 P6 终审，本 ADR 自该确认起生效。
