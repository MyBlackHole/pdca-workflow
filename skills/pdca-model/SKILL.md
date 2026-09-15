---
name: pdca-model
description: 用户明确选择本体建模场景，或已有建模任务需要场景方法时使用。定义领域模型与工作实例交付；不以知识地图冒充模型，不自动开始 Plan。
metadata:
  version: 5.0.0-rc.2
---

# 本体建模

## 先定位，不以加载当授权

核对本文件经符号链接解析后的真实路径，定位集中 Git 工作副本 **PDCA_ROOT**。既有任务绑定优先于 cwd 或环境变量；与入口所在根冲突时停止，不在目标项目创建 `.pdca/` 或另一份 records。定位不等于批准业务操作。

先读[共同恢复入口](../../ontology/contracts/entry-recovery.md)，再读当前绑定项目 context、自己的 task/原 Agent 绑定、最后完整事件和当前请求。核对记录的 `rules_git_head`/`rules_git_status`；每次获准写入记录前按共同入口重新采集当前 Git 来源。已有任务不自动改绑或升级规则，原依据缺失或规则冲突时停止；不复制规则、不自动 checkout，不以新规则改写原授权。

## 两种读取方式，禁止递归创建

- **用户选择场景入口**：先定位具名work/node/scene。已有该场景任务就回原Agent；没有任务时只提出范围、输入、交付和创建请求，用户明确批准后按[派发入口](../../ontology/contracts/agent-dispatch.md)创建独立可交互任务。创建成功还须由任务Agent展示Plan目标并等待启动，不连续跑四阶段。
- **已有阶段任务读取方法**：核对 task.scene 匹配后，只读下面的阶段方法。不要再次触发创建/选择分支，不调用总入口生成另一个任务。场景不匹配就停止，不能静默更改scene。

一个场景里的每个节点都是独立完整PDCA，同一任务四阶段由原Agent/会话执行；场景Skill不是一个阶段，也不是额外Agent。所有过程记录和资源回到同一PDCA_ROOT，各任务只读获准输入、不共享活动历史。阶段完成报告后等待，不自动开始下阶段或下一场景。

## 本体分层

- **稳定层**：职责边界、依赖性质、验收标准 → 修改触发 revision
- **假设层**：接口、约束、实现、测试 → 修改不触发 revision

**边界判定**：改变此陈述需要重新冻结本体树 → 稳定层；改变此陈述不影响其他节点的职责边界 → 假设层。详细规则见[设计文档](../../docs/superpowers/specs/2026-09-14-ontology-tree-agent-design-goals.md#假设层与稳定层的边界判定)。

## 节点状态索引

每个本体节点维护可重建的 `ontology-node-state` 索引，包含节点状态、依赖、假设等信息。详细 schema 见[设计文档](../../docs/superpowers/specs/2026-09-14-ontology-tree-agent-design-goals.md#节点状态索引)。

## 就绪与用户确认

状态流转：`draft → awaiting_ontology_freeze_confirmation → ontology_frozen → implement_ready → ...`。任意阶段可为 `blocked`、`failed` 或 `stale`。详细规则见[设计文档](../../docs/superpowers/specs/2026-09-14-ontology-tree-agent-design-goals.md#就绪与用户确认)。

## 阶段方法

| 阶段 | 动作与交付 |
|---|---|
| Plan | 确认要建模的问题、范围、定义粒度、来源、可复用对象、需求覆盖与验收方式；已获用户批准才开展正式调查 |
| Do | 形成稳定层（对象ID、关系、约束）和假设层（接口、约束、实现、测试假设） |
| Check | 核对原需求→定义/实例覆盖、关系可解析性、约束可检验性与事实来源 |
| Act | 只按批准范围固定模型；整树冻结、共享知识发布，未运行投影不宣称完成 |

详细规则见[设计文档](../../docs/superpowers/specs/2026-09-14-ontology-tree-agent-design-goals.md)。
