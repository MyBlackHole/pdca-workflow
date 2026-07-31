# T0141 实施计划

1. 新增 convergence map schema 与合法/非法 schema 测试。
2. 在核心验证模块实现 PRD AC 提取和 convergence 支撑链检查。
3. 将核心函数接入 Do→Check 的现有 `gate_issues`。
4. 新增独立 JSON CLI，复用同一核心函数。
5. 更新 Do 收尾、verify-convergence 和规格模板，说明 map 生成、登记和错误修复方式。
6. 建立完整路径与逐错误故障夹具，包含旧 gate 接受、新 gate 拒绝的配对实验。
7. 运行单元测试、12 个既有确定性夹具、doctor、skill index 和内容审查。
8. 若没有新增错误发现能力，删除 schema、CLI 和门禁改动。

该任务是单一 PDCA 周期，不拆子任务；实现共享同一核心模块，拆分会增加协调成本。
