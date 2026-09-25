---
name: pdca-implement
description: 用户明确选择本体投影场景，或已有投影任务需要场景方法时使用。不脱离模型。
metadata:
  version: 5.0.0-rc.2
---

# 本体投影

## 先定位，不以加载当授权

核对本文件经符号链接解析后的真实路径，定位集中 Git 工作副本 **PDCA_ROOT**。
既有任务绑定优先于 cwd 或环境变量；与入口所在根冲突时停止，不在目标项目创建 `.pdca/`
或另一份 records。定位不等于批准业务操作。

先读[共同恢复入口](../../ontology/contracts/entry-recovery.md)，再读当前绑定项目 context、
自己的 task/原 Agent 绑定、最后完整事件和当前请求。核对记录的
`rules_git_head`/`rules_git_status`；每次获准写入记录前按共同入口重新采集当前 Git 来源。
已有任务不自动改绑或升级规则，原依据缺失或规则冲突时停止；不复制规则、不自动 checkout。

## 两种读取方式，禁止递归创建

- **用户选择场景入口**：先定位具名 work/node/scene。已有该场景任务就回原 Agent；
  没有任务时只提出范围、输入、交付和创建请求，用户明确批准后按
  [派发入口](../../ontology/contracts/agent-dispatch.md)创建独立可交互任务。
  创建成功后任务 Agent 先展示 Plan 目标并等待，不连续跑四阶段。
- **已有阶段任务读取方法**：核对 task.scene 匹配后，只读下面的阶段方法。
  **不要再次触发创建**/选择分支，不调用总入口生成另一个任务。

一个正式场景节点是独立完整 PDCA，同一任务四阶段由原 Agent/会话执行。
阶段完成报告后等待，不自动开始下阶段或下一场景。

## 假设反馈与失效传播

反馈类型为 validated/invalidated/revised/pending；置信度必须由证据支持。
本体实质变化产生新 `ontology_revision`，旧 PASS 不得静默迁移；
直接修改节点及真实依赖节点按规则标 stale。详细规则见
[设计文档](../../docs/superpowers/specs/2026-09-14-ontology-tree-agent-design-goals.md)。

## 阶段方法

| 阶段 | 动作与交付 |
|---|---|
| Plan | 固定获准模型版本、原需求、目标位置、映射规则、验收标准、业务写域，并区分正式节点与 Do-only Work Unit |
| Do | 生成真实代码、文档、配置等实体；记录模型→目标映射、假设反馈和证据；执行切片使用 Work Unit Contract，不隐藏创建新 PDCA |
| Check | 双向检查 source→target 遗漏、target→source 无依据增加，并运行产品级验证 |
| Act | 固定目标版本、映射、实际验证范围和缺项 |

**分解规则：** 不用 LOC、预计工时或 Agent 置信度作为硬阈值。
具有独立可拒收成果和验证边界的部分，按
[DECOMP-01](../../ontology/concept/task-decomposition.md)生成正式节点候选并等待用户创建；
其余执行切片留在当前 Do，使用
[CONTRACT-01](../../ontology/concept/pdca-execution-contract.md) 的 Do-only Work Unit。
详细设计见[Do 工作单元与正式节点拆分](../../docs/superpowers/specs/2026-09-15-subtask-splitting-design.md)。

**棘轮规则：** 投影发现模型缺失或根本错误时，报告阻断并由用户决定是否启动 pdca-model；
不能在当前投影任务中静默改 scene 或跳过建模。

详细规则见[设计文档](../../docs/superpowers/specs/2026-09-14-ontology-tree-agent-design-goals.md)。
