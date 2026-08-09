# grilling frontier 批量问法 — 规格文档

## 问题陈述

- **现状**: 本仓库 `skills/grilling/SKILL.md:11` 强制"一次只问一个，从不批量"，导致 Plan 对齐阶段（flow-plan P2）需要 N 轮用户交互才能覆盖 N 个独立决策。历史任务实测 clarifications 达 5-9 轮 grilling（如 0731-execution-contract-hardening=5、0731-pg-mysql-parquet-poc=9）。每轮一次往返，耗时且消耗用户注意力。
- **目标**: 借鉴 mattpocock/skills 的 frontier 批量问法，让一轮内覆盖所有当前可答的独立决策，将 N 决策对齐轮数降至约 ceil(N/每轮容量)，并把"效率提升"做成可回归验证的硬指标。
- **差距**: 交互轮数（用户可感知的往返次数）过大，且无自动化手段证明/回归验证该成本。

## 解决方案

将 grilling 从"一次只问一个"改为"每轮计算 frontier（当前可答的全部问题）→ 一轮内问完，每个问题编号并附推荐答案 → 用户一次性回复 → 重算 frontier 进入下一轮"，直至 frontier 为空。事实自行查找（子代理/工具），不占用用户提问额度。

## Seam 分析

### 测试接缝
- 测试目标：`skills/grilling/SKILL.md` 的行为规格（frontier 计算与轮数推导），通过独立 fixture 模拟决策树，断言批量法轮数上限。
- 现有测试先例：`tests/test_ai_friendliness_hardening.py`（契约驱动、fixture 化）、`tests/test_workflow_ai_usability.py`。
- Mock/Stub：无需外部依赖；纯逻辑 + 文件断言，fixture 内嵌决策树 JSON。

### 验收可测性
- 每个 AC 有明确 pass/fail 信号（见验收标准）。
- 边界条件：单决策、多独立决策、依赖链决策（需分轮）、无决策（空 frontier）四种 fixture 可独立构造。
- 单元测试为主，无端到端依赖。

## 用户故事

1. 作为 PDCA 用户，我想要 Plan 对齐阶段一轮问完所有可答问题，以便减少交互往返次数。
2. 作为 PDCA 用户，我想要每个问题都附推荐答案，以便我只需确认而非从头思考。
3. 作为 PDCA 维护者，我想要轮数对比测试，以便证明并持续守护 grilling 的效率收益。
4. 作为 PDCA AI，我想要保持"事实自己查、决策问用户"的边界，以便不问用户任何可查证的事实。

## 实现决策

- 新增/修改的模块：
  - 修改 `skills/grilling/SKILL.md`：frontier 批量问法（核心规则 1 从"一次一问"改为"批量问 frontier"）。
  - 修改 `flows/flow-plan/SKILL.md` P2 引用文案：从"一次只问一个需要用户决策的问题"改为"一轮内批量询问所有可答决策"。
  - 修改 `flows/flow-check/SKILL.md` 结论追问引用：保持与 grilling 新问法一致。
  - 新增 `tests/test_grilling_efficiency.py`：轮数对比测试。
- 技术澄清：
  - `clarifications.jsonl` schema 不变：同一轮内所有问题共享同一 `round` 号，每个问题一条 JSONL。
  - `source: "grilling"`、`source: "direction_confirm"`、`source: "final_confirmation"` 语义不变，门禁逻辑不受影响。
- 架构决策：无（不涉及不可逆或有权衡的架构变更，仅技能行为调整）。

## 测试决策

- 好的测试定义：仅测"轮数推导"与"frontier 语义"这一可观察行为，不测具体提问措辞。
- 被测模块：grilling 的批量问法轮数模型（N 决策、每轮容量 K、依赖分轮），用 fixture 决策树驱动。
- 现有测试先例：`test_ai_friendliness_hardening.py` 的 fixture + 契约模式；`test_workflow_ai_usability.py` 的回归模式。

## 验收标准

- [ ] AC-1: `skills/grilling/SKILL.md` 核心规则改为 frontier 批量问法（不再要求"一次只问一个"），且每问仍附推荐答案。
- [ ] AC-2: `flows/flow-plan/SKILL.md` P2 与 `flows/flow-check/SKILL.md` 中引用 grilling 的文案与批量问法一致。
- [ ] AC-3: 新增 `tests/test_grilling_efficiency.py`，含四种 fixture：单决策、多独立决策、依赖链决策、空 frontier。
- [ ] AC-4: 轮数断言通过：多独立决策（N≥3）批量法轮数 R 严格小于 N，且 R == ceil(N/K)（K 为每轮容量）；依赖链决策按依赖分批。
- [ ] AC-5: 既有测试套件全部通过（无回归），`python3 scripts/pdca-doctor.py --json` 健康。
- [ ] AC-6: `clarifications.jsonl` 同轮共 round 的记录规则在测试或文档中体现，门禁解析不受影响。

## 范围外

- 不新增 wait-what、wizard 等新技能（仅评估记录）。
- 不精简 ask-matt / 其他技能体积（本次仅 grilling + flow 引用）。
- 不修改 `pdca/CONTEXT.md` 术语（grilling 语义不变，仅节奏变）。
- 不改 `triage-work`、`wayfinding-work`、`wayfinding-chart` 中引用 grilling 的措辞（本轮刻意最小化）。
- 不做真实端到端 agent 交互计时（R0138 已记录需独立 runner 才评估）。

## 备注

- 借鉴来源：mattpocock/skills `grilling`（frontier 批量问）+ `writing-for-agents`（completion criteria 双维，间接）。
- 历史轮数基线：0731-execution-contract-hardening clarifications grilling=5、0731-pg-mysql-parquet-poc=9，为轮数证明提供现实参照。
- 完整审核结论见 `research-report.md`。
