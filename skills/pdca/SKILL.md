---
name: pdca
description: 用户显式选择 PDCA、绑定项目、查询状态或恢复已有任务时使用。定位集中 Git 工作副本与原会话，不自动创建任务或执行四阶段。
metadata:
  version: 5.0.0-rc.2
---

# PDCA：定位、绑定与运行入口分流

## 定位

先按[项目绑定契约](../../ontology/contracts/project-workspace.md)定位 **PDCA_ROOT**、
一个明确的 project/workspace 和真实 **TARGET_ROOT**。已有 task 绑定优先于 cwd/环境变量；
缺失、多个匹配、路径或入口根冲突时停止说明，不猜项目、不选“最新任务”，也不在 TARGET_ROOT 建第二套 `.pdca`。

已有 task 的状态查询、继续、恢复或取消再进入
[共同恢复入口](../../ontology/contracts/entry-recovery.md)；没有 task 时不要为“恢复”虚构一个。
项目绑定、Git 追溯和记录写入授权只按 project-workspace 执行，本 Skill 不维护第二份规则。

## 用户操作分流

- **绑定/改绑**：展示 project-workspace 要求的真实身份与待写路径；只有用户明确批准对应记录写入后才保存。
- **状态**：只读当前绑定项目的导航，报告实际 task/scene/phase、待用户事项和未决资源；涉及某 task 连续性时按 entry-recovery 核对原 Agent 与事件。
- **创建正式任务**：只有用户明确选择具名 task 后，按 [LOAD-MAP](../../ontology/LOAD-MAP.md) 的“新建正式任务”读集固定身份、上下文、宿主资格和创建授权，再由 [agent-dispatch](../../ontology/contracts/agent-dispatch.md) 原生创建一次；新 Agent 展示自己的 Plan 目标后等待。
- **阶段**：路由到 `pdca-plan/do/check/act`；**场景**：路由到 `pdca-model/implement/verify`；
  场景对象和跨场景终态只以 [SCENE-01](../../ontology/process/work-scenarios.md) 为准。
- **只读建议**：只有用户显式调用时进入 `pdca-assist`。
- **停止/撤权**：按 CONTROL-01 和 RESOURCE-01 优先安全收尾，不等待新的业务阶段授权。

普通请求、Skill 加载、binding 存在、任务 ready、阶段完成或 PASS 都不会自动创建 task、
启动 phase/scene、提交 Git 或扩大读写权。运行入口名称与职责见[Skill 索引](../README.md)。

## 报告与恢复

总入口只报告当前事实、可用入口、等待对象或阻断原因，不替 task 执行四阶段，也不轮询监工。
恢复/压缩只按 RECOVERY-01 使用原始 refs 和原 Agent；摘要只是索引，不能 spawn 一个“等价实例”接管。
