# ADR-0017: to-tickets 显式依赖边（blocking edges）与 ready-set 术语

- 日期: 2026-08-09
- 状态: 已确认（plan 阶段固化决策方向）

## 背景

T0230/T0231 落地 grilling frontier 批量问法后，审查 mattpocock/skills 确认
两项尚未借鉴且"可证明"的机制：

1. **blocking edges**（`to-tickets/SKILL.md`）：子任务显式声明前置依赖，
   计算"所有 blocker 已完成的可执行任务集合"。PDCA 的 `to-tickets` 只顺序
   拆解，无显式依赖边，无法校验 DAG 无环、无法计算可并行任务集。
2. **design-it-twice**（`codebase-design/DESIGN-IT-TWICE.md`）：接口设计时
   并行产出 2+ 根本不同候选方案，用强制词汇表（module/interface/seam/
   adapter/depth/leverage/locality）对比。PDCA 无该机制与词汇契约。

既有事实：`schemas/task.schema.json` 的 `additionalProperties: false`，
新增 `dependencies` 字段必须同步改 schema，否则 doctor 校验失败。

## 决策

- **blocking edges 落在 `to-tickets` 技能内扩展**（不独立成技能）。
- **依赖边载体**：子 `task.json` 新增 `dependencies: ["Txxxx"]` 数组，
  仅存**直接前置**（标准 DAG 语义），传递闭包由校验器推导。
- **schema 变更**：`task.schema.json` 新增 `dependencies` 属性
  （`array of ^T[0-9]{4,}$`，`uniqueItems: true`）；旧任务不强制补齐
  （缺失即无依赖），严格 schema 冻结前不兼容旧格式。
- **校验时机**：to-tickets 拆解完成后立即校验 DAG 无环（违反则拒绝产出）。
- **可执行集合术语**：新术语 **`ready-set`**（所有直接前置已完成的任务集合），
  替代 frontier，避免与 grilling 的 frontier（可答问题集合）混淆。
- **实现形态**：纯函数 `compute_ready_set(tasks)` + 四类 fixture
  （有环/无环/多级依赖/无依赖）单测；可独立调用的 `scripts/compute-frontier.py`；
  技能规则与脚本并存。
- **design-it-twice**：独立 `skills/design-it-twice/SKILL.md`，采用 mattpocock
  词汇表（不本土化，跨仓库一致），并行执行复用 to-tickets 的 dispatch 模式
  （`agent.spawn` 可用时并行，否则主会话顺序）。
- **词汇契约**：`scripts/check-design-vocab.py` 校验 design-it-twice 产出文档
  只允许词汇表术语（同构 T0231 source 术语契约测试）。

## 备选方案与取舍

- **不独立成技能**：blocking edges 是 to-tickets 拆解步骤的天然组成，独立成
  技能引入跨技能引用开销；验证 T0231 已证明"修改现有技能 + 契约测试"可行。
- **全量传递依赖 vs 仅直接前置**：全量冗余且破坏 DAG 单源事实；仅直接前置由
  校验器推导，最小数据冗余。
- **frontier 术语沿用 vs ready-set**：沿用会造成两处 frontier 语义冲突
  （grilling 可答问题集 vs 可并行任务集），引入 ready-set 消歧。
- **词汇本土化 vs 直接采用**：design-it-twice 的"whole point"是跨项目一致语言，
  本土化破坏可比性，直接采用。

## 影响

- `schemas/task.schema.json`：新增 `dependencies` 属性。
- `skills/to-tickets/SKILL.md`：拆解流程 + ready-set 计算规则。
- 新增 `scripts/compute-frontier.py`、`scripts/check-design-vocab.py`。
- 新增 `skills/design-it-twice/SKILL.md`。
- `pdca/CONTEXT.md`：记录 `ready-set`、`dependencies`、词汇表术语。
