# to-tickets blocking edges + design-it-twice — 规格文档

## 问题陈述

- **现状**: PDCA 的 `to-tickets` 只顺序拆解子任务，无显式依赖边；无法校验 DAG 无环、无法计算可并行任务集。接口设计无"双方案对比"机制，术语（module/interface/seam/adapter）在跨技能产出中无强制一致性。
- **目标**: 子任务可显式声明前置依赖，能校验 DAG 无环并计算 ready-set（可执行任务集）；接口设计用强制词汇表做双方案对比。
- **差距**: 无 `dependencies` 字段、无 DAG 校验、无 ready-set 计算、无 design-it-twice 机制、无词汇契约校验器。

## 解决方案

1. **blocking edges**：`to-tickets` 拆解时，子 `task.json` 声明 `dependencies: ["Txxxx"]`（仅直接前置）。拆解完成后立即校验 DAG 无环；计算 ready-set（所有直接前置已完成的任务集合）供 dispatch 并行调度。
2. **design-it-twice**：独立技能，接口设计时并行产出 2+ 根本不同候选方案，用强制词汇表对比（module/interface/seam/adapter/depth/leverage/locality），产出文档经 `check-design-vocab.py` 校验只允许词汇表术语。

## Seam 分析

### 测试接缝
- `compute_ready_set(tasks)` 纯函数：输入任务列表（含 `dependencies`），输出 ready-set 或抛环错误。**测试直测此函数**，不测技能措辞。
- `check-design-vocab.py` 纯函数：输入文档文本 + 词汇表，输出违规术语列表。测试直测违规检测。
- 隔离：无外部依赖（纯内存数据结构），无需 mock。

### 验收可测性
- 每项验收均有明确 pass/fail（见下）。
- 边界条件：有环 DAG、无环 DAG、多级依赖、无依赖、缺失 id 引用，均可独立构造 fixture。

## 用户故事

1. 作为拆解执行者，我想要子任务声明直接前置依赖，以便调度器知道哪些任务可并行。
2. 作为任务审核者，我想要 DAG 无环校验，以便发现拆解中的循环依赖错误。
3. 作为调度者，我想要 ready-set 计算，以便一次取出全部可并行任务。
4. 作为接口设计者，我想要双方案对比 + 强制词汇，以便做出非锚定设计决策。

## 实现决策

**架构决策已记入 ADR-0017**。要点：

- 新增/修改模块：
  - `schemas/task.schema.json`：新增 `dependencies`（`array of ^T[0-9]{4,}$`，`uniqueItems`）。旧任务缺失即无依赖。
  - `skills/to-tickets/SKILL.md`：拆解流程新增 dependencies 声明 + DAG 无环校验 + ready-set 计算规则。
  - 新增 `scripts/compute-frontier.py`：独立调用验证 ready-set 与 DAG。
  - 新增 `skills/design-it-twice/SKILL.md`：双方案并行设计流程 + 词汇表。
  - 新增 `scripts/check-design-vocab.py`：词汇契约校验。
- 数据模型：子 task.json 新增 `dependencies` 数组（仅直接前置）。
- 术语：`ready-set`（可执行任务集）替代 frontier，避免与 grilling frontier 混淆（记入 CONTEXT.md）。

## 测试决策

- 好的测试定义：仅测 `compute_ready_set` 的可观察行为（无环输出 / 有环抛错），不测技能措辞。
- 被测模块：
  - `compute_ready_set` 纯函数：四类 fixture（有环/无环/多级依赖/无依赖）。
  - `check-design-vocab` 纯函数：词汇表内通过、表外违规、边界词。
  - schema：`dependencies` 字段类型/格式校验 + doctor valid。
- 先例参考：`tests/test_grilling_efficiency.py` 的纯函数 fixture 模式。

## 验收标准

- [ ] AC-1: `to-tickets` 支持子 task.json `dependencies` 字段声明直接前置依赖（仅直接前置，传递闭包由校验器推导）
- [ ] AC-2: `compute_ready_set` 纯函数通过四类 fixture（无依赖/多级依赖/有环/缺失 id 引用），有环时抛出明确错误
- [ ] AC-3: DAG 无环时 ready-set 正确（=所有直接前置已完成的任务集合）
- [ ] AC-4: `task.schema.json` 新增 `dependencies` 属性且 doctor valid=true
- [ ] AC-5: `check-design-vocab.py` 拒绝词汇表外术语（如 component/service/API/boundary），接受词汇表内术语
- [ ] AC-6: 全量测试无回归（现有测试 + 新增）

## 范围外

- 不实现子任务实际并行调度（仅计算 ready-set 供调度用）。
- 不改造 grilling frontier 术语（只新增 ready-set 消歧）。
- 不强制旧任务补齐 `dependencies`。
- 不落地 expand-contract（#1）与 deletion test（#4）。

## 备注

- 词汇表直接采用 mattpocock（不本土化），跨项目一致是 design-it-twice 的 whole point。
- 并行执行复用 to-tickets dispatch 模式（agent.spawn 可用时并行，否则主会话顺序）。
