# 本体知识产生→任务拆分→单元测试依赖链闭环调研报告

**调研日期**: 2026-08-31  
**调研范围**: `/home/black/Documents/pdca-workflow-pro`  
**方法**: 文件读取、脚本执行、测试套件运行、图谱分析

---

## 一、本体知识产生→任务拆分→单元测试的完整依赖链描述

### 1.1 链全景

```
[Grilling 用户追问] → [Domain Modeling 领域建模] → [Writing-for-Agents 写作原则]
        ↓                        ↓                              ↓
  产生决策/术语              硬决策→ontology节点            写作规范/信息层级
        ↓                        ↓                              ↓
  [ontology/ 节点写入] ←── [ontology_induction.py 半自动归纳] ← [知识草稿/代码/Web]
        ↓
  [ontology-validate.py 门禁校验] ←── [ontology-check skill 人工入口]
        ↓
  [task.json meta.ontology_fragment 继承]
        ↓
  [to-tickets skill 消费本体]
        ├── ontology-clash-check.py (冲突预检)
        ├── ontology_tree_split.py (关系树驱动拆分)
        └── task_identity.py (创建子任务 + 自动继承)
        ↓
  [compute-frontier.py DAG 校验 + ready-set 计算]
        ↓
  [Do 阶段执行 → 单元测试/契约测试]
        ├── skill-tdd.md (红绿重构循环)
        ├── skill-testing-strategy.md (测试策略)
        └── testable_signal (本体属性驱动的测试信号)
        ↓
  [register-evidence.py 证据登记] ←── [evidence_type_ref 锚定 ontology 节点]
        ↓
  [verify-convergence.py 收敛验证]
        └── convergence-map: PRD AC → registered evidence 确定性支撑链
        ↓
  [CI 硬门禁: ci-ontology-gate.py]
        ├── ontology-validate.py (本体契约校验)
        └── validate-convergence.py (收敛校验)
        ↓
  [archive_ontology_ready_issues: 归档前本体自检 + 孤岛检查]
```

### 1.2 各环节详细说明

#### 环节 A: 本体知识产生（Grilling → Domain Modeling → Writing-for-Agents → ontology/ 写入）

**Grilling（skill-grilling.md）** 是知识产生的源头：
- 通过设计树（design tree）逐轮追问用户，每个问题附带推荐答案
- Q&A 记录到 `clarifications.jsonl`（`source: "grilling"`），遵守 HITL 双态规则
- 模糊术语 → 立即更新 `pdca/CONTEXT.md`
- 不可逆决策 → 记录到对应的 `ontology/` 节点（添加"决策背景"节）
- 协作接口：`Collaboration with domain-modeling` 节明确了与领域建模的交接点

**Domain Modeling（skill-domain-modeling.md）** 是共享语言的构建者：
- 在 Grill 过程中或独立对话中主动构建和打磨项目的共享语言
- 模糊术语落定后立即写入 `CONTEXT.md`
- 硬决策记录为 ADR（现演进为 `ontology/` 节点）
- 调用 `skills/domain-modeling-work/SKILL.md`

**Writing-for-Agents（ontology:concept/writing-for-agents）** 是面向 Agent 的写作规范：
- 定义了 Grounding 依赖图：概念必须 grounding 后才能被后续块依赖
- 信息层级：步骤 → 文件中引用 → 披露引用
- `co-location`、`context-pointer`、`grounding-dependency` 等子概念支撑知识组织
- `ai-efficiency-writing-for-agents-levers.md` 提供了 4 个写作杠杆（锚定词/指针措辞/双负载/no-op 模型相对判定）

**Ontology Induction（`scripts/ontology_induction.py`）** 是半自动归纳工具：
- 读取知识草稿（知识文件），通过启发式规则推断 type/specializes/guides
- 提出候选 frontmatter 骨架，**仅打印候选、不自动落盘**（HITL 保留）
- 确定性执行（无 LLM 调用），同一输入产生相同候选
- 扩展点：`Adapter` 基类支持 code/web 适配器

**ontology/ 目录结构**（340 节点，703 条边，0 孤岛）：
- 受控类型词表：`domain/entity/concept/process/role/pattern/principle/pitfall/fact/decision`
- 四层资产全部物理归并到 `ontology/`（T0418~T0423 知识层合并）
- 节点通过 `relations` 字段表达 `specializes`/`composed_of`/`guides`/`relates_to` 等关系

#### 环节 B: 任务拆分消费本体（to-tickets → 本体一致性预检 → 关系树驱动拆分 → task_identity）

**本体一致性预检**（`skill-to-tickets.md` 步骤 3）：
- 调用 `scripts/ontology-clash-check.py` 检测候选 slug/标题是否与既有 ontology 节点重名
- 仅提示、不阻断拆解产出（告警式，退出码恒为 0）
- 候选与本体节点 token 级别匹配（去掉日期前缀后比较 slug 片段）

**关系树驱动拆分**（`skill-to-tickets.md` 步骤 3.5，可选）：
- 仅当 PRD 含 `## 拆分映射` 且父任务 `meta.ontology_fragment` 非空时启用
- 调用 `scripts/ontology_tree_split.py --ontology-dir "<meta.ontology_fragment>" --prd prd.md`
- 脚本解析 `## 拆分映射`（章节→节点），结合 `composed_of`/`specializes` 关系树输出候选子任务
- 每个候选自动携带 `ontology_node_type`（由本体节点 type 推导）与依赖边
- 映射节点若有 `composed_of` 子实体 → 每个子实体成为子任务候选，映射节点自身成为集成任务（依赖所有子）
- 映射节点不存在、关系图成环时脚本报错退出
- **仅打印候选、不自动落盘**，确认后由调用方经 `task_identity.py` 逐个创建

**task_identity.py 自动继承**（`skill-to-tickets.md` 步骤 4）：
- 子任务创建时自动继承父任务的 `meta.ontology_fragment` 和 `meta.ontology_node_type`
- `--ontology-fragment` 指向存在的本体目录时做轻量存在性校验
- `ontology_node_type` 从本体 `ontology-asset` 节点的 `node_types` 声明读取，缺失时回退 `FALLBACK_NODE_TYPES`
- 拒绝不在本体词表中的 `ontology_node_type`（`ONTOLOGY_NODE_TYPE_INVALID`）
- 锚定默认指向 `ontology:concept/pdca-task`，可通过 `ontology_exempt: true` 豁免

**Ready-set 计算**（`skill-to-tickets.md` 步骤后）：
- 调用 `scripts/compute-frontier.py` 从 stdin 读 DAG JSON
- 输出 `{valid, ready_set, batches}`
- 依赖图非法（有环/缺失引用/自环）→ 拒绝拆解产出

#### 环节 C: 单元测试验证（testable_signal → 派生测试 → 契约测试 → convergence 验证）

**TDD（skill-tdd.md）**：
- 红→绿循环，通过公共接口验证行为
- Seam（接缝）概念：测试写在预先约定的公共边界上
- 抗模式：实现耦合/同义反复/水平切片
- 进入 TDD 循环前阅读 `pdca/CONTEXT.md` 和 `ontology/` 节点

**测试策略（skill-testing-strategy.md）**：
- unit 覆盖业务逻辑，integration 覆盖边界交互，e2e 覆盖核心路径
- CI 分层：lint → 并行 2min → unit test → 并行 5min → integration → 串行 15min → e2e

**本体属性 testable_signal**：
- `ontology-check` 门禁要求每个 `attributes[].testable_signal` 非空（AC-4）
- `testable_signal` 是本体属性级别的测试信号声明，但目前**仅做存在性校验**，不自动生成测试

**Convergence 验证（skill-verify-convergence.md）**：
- 生成 `convergence.json`：`{schema: pdca.convergence/v1, items: [{index, text, criteria, evidence_ids}]}`
- 每条 convergence 写且只写一个 item
- `convergence-map` 固定使用 `--kind convergence-map` 登记
- 调用 `scripts/validate-convergence.py` 做程序验证
- 验证链：convergence → PRD AC → registered evidence

**证据登记（skill-register-evidence.py）**：
- `--kind` 必须命中允许集合：`pdca-evidence` 子类型短名 或 支持型 kind
- 命中 `ontology:entity/evidence-<short>` 时写入 `evidence_type_ref` 锚定到本体节点
- `--kind convergence-map` → `evidence_type_ref: ontology:entity/evidence-convergence-map`

**CI 硬门禁（`scripts/ci-ontology-gate.py`）**：
- 退出码 0 = 通过；非 0 = 阻断
- 步骤 1: `ontology-validate.py` 本体契约硬校验
- 步骤 2: 相关任务的收敛校验（check/act/archive 阶段且登记了 convergence-map 的任务）
- 供 `.git/hooks/pre-commit` 与 `.github/workflows/ontology-gate.yml` 复用

#### 环节 D: 本体补充（Check 阶段发现缺口 → Act 阶段创建本体补强任务 → 新节点写入 ontology/domain/）

- `skill-advance-phase.md` 定义了阶段推进规则：check→act 需要 conclusion、verdict、check_confirmation
- `skill-code-review.md` 定义了双轴代码审查：标准轴 + 规范轴，Blocking=0 方可通过
- `skill-grilling.md` 的 `Check→Act` 视图明确：What are the limits of this conclusion? What parts are reusable knowledge?
- 本体补强任务通过 `to-tickets` 创建，新节点写入 `ontology/domain/` 或对应的类型目录
- `ontology-check` 门禁确保新资产写入前/后通过校验

---

## 二、每个环节的当前实现状态

### 2.1 本体知识产生

| 组件 | 状态 | 说明 |
|------|------|------|
| skill-grilling.md | 活跃 | Grill 流程完整，Q&A 落盘规则明确，HITL 双态实现 |
| skill-domain-modeling.md | 活跃 | 调用 `skills/domain-modeling-work/SKILL.md`，共享语言构建 |
| writing-for-agents.md | 活跃 | 340 节点本体图，Grounding 依赖图已定义 |
| ontology_induction.py | 半自动 | 适配器模式 + 启发式推断，仅打印候选不落盘（HITL 保留） |
| ai-efficiency-writing-for-agents-levers.md | 活跃 | 4 个写作杠杆已落地为 ontology 节点 |

### 2.2 任务拆分消费本体

| 组件 | 状态 | 说明 |
|------|------|------|
| skill-to-tickets.md | 活跃 | 6 个步骤完整：预检→树拆分→创建→更新父→复制 prd→ready-set |
| ontology-clash-check.py | 活跃 | 告警式，不阻断；token 级别匹配 |
| ontology_tree_split.py | 活跃 | 解析拆分映射 + 关系树生成 WBS；成环/节点不存在时报错 |
| task_identity.py | 活跃 | 自动继承 ontology_fragment/ontology_node_type；类型词表校验 |
| compute-frontier.py | 活跃 | DAG 校验 + ready-set + 分批 |
| test_ontology_tree_split.py | 全部通过 | 5 个测试用例覆盖：生成、缺失节点、环检测、叶节点、空映射 |
| test_ontology_clash.py | 全部通过 | 3 个测试用例覆盖：冲突检测、日期前缀、CLI |
| test_pdca_task_consumption.py | 全部通过 | 6 个测试用例覆盖：锚定、豁免、类型校验、继承 |

### 2.3 单元测试验证

| 组件 | 状态 | 说明 |
|------|------|------|
| skill-tdd.md | 活跃 | 红绿重构循环，Seam 概念，抗模式 |
| skill-testing-strategy.md | 活跃 | 多语言测试策略，CI 分层 |
| skill-verify-convergence.md | 活跃 | convergence → PRD AC → evidence 支撑链 |
| skill-register-evidence.md | 活跃 | kind 锚定到 pdca-evidence 子类型 |
| validate-convergence.py | 活跃 | 程序化验证收敛链 |
| test_convergence.py | 大部分通过 | 19 个测试中 18 个通过，1 个因 ONTOLOGY_FRAGMENT_MISSING 拦截 |
| test_register_evidence_anchor.py | 全部通过 | 3 个测试用例覆盖：锚定、向后兼容、未知 kind 拒绝 |
| test_ontology_validate.py | 部分失败 | 3 个测试失败（原因：测试夹具缺少 ontology-rule-* 节点） |
| test_ontology_validator_from_nodes.py | 全部通过 | 5 个测试验证 rule_spec 从节点读取 |
| test_ontology_full_lifecycle.py | 部分失败 | 5 个测试中 4 个通过，1 个因旧归档任务缺少 convergence-map 失败 |

### 2.4 本体检查门禁

| 组件 | 状态 | 说明 |
|------|------|------|
| skill-ontology-check.md | 活跃 | AC-1~AC-6 完整，权威依据来自 ontology-rule-* 节点 |
| ontology-validate.py | 活跃 | 校验 AC-1~AC-6 + COMPOSED_OF_RANGE + CONFIGURED_BY_RANGE + REDIRECT_DANGLING |
| ontology-validate.py (生产环境) | 通过 | `python3 scripts/ontology-validate.py --ontology-dir ontology` → OK: 0 issues |
| ontology_graph.py | 活跃 | 340 节点，703 条边，0 孤岛 |
| ci-ontology-gate.py | 活跃 | CI 硬门禁，但有一个历史归档任务导致失败 |
| test_ontology_validator_from_nodes.py | 全部通过 | 5 个测试验证 rule_spec 驱动校验行为 |

### 2.5 修复机制

| 组件 | 状态 | 说明 |
|------|------|------|
| remediate-id-collisions.py | 活跃 | ID 撞车全链路重分配，幂等，dry-run 预览 |
| remediate-gate-compliance.py | 活跃 | 门禁合规修复，dry-run + apply |
| audit-gate-compliance.py | 活跃 | 门禁合规审计 |
| rollback-phase.sh | 活跃 | 阶段回滚（仅恢复 transition-receipts） |
| skill-advance-phase.md | 活跃 | 阶段推进 + 回滚机制 |
| **专门的本体错误修正技能** | **缺失** | 无专门技能处理本体节点本身的错误修正 |

---

## 三、闭环缺口清单（按严重程度分级）

### 3.1 严重缺口（High）

#### GAP-01: testable_signal → 自动生成单元测试的管道缺失

**严重程度**: 高  
**描述**: 本体属性 `testable_signal` 是 AC-4 门禁要求（`attributes[].testable_signal` 非空），但目前仅做存在性校验。`skill-tdd.md` 描述了手动 TDD 流程，`skill-testing-strategy.md` 描述了测试策略，但**没有任何机制读取 `testable_signal` 并自动生成测试用例**。  
**影响**: 本体的测试信号声明与实际的单元测试之间存在断层。testable_signal 仅作为元数据存在，不驱动测试生成。  
**当前状态**: testable_signal 被 `ontology-validate.py` AC-4 校验存在性，但未被任何测试生成工具消费。  
**修复建议**: 在 `scripts/` 中新增 `testable-signal-extractor.py`，读取本体节点的 `attributes[].testable_signal`，生成测试骨架或契约测试用例。

#### GAP-02: 缺少专门的本体错误修正技能

**严重程度**: 高  
**描述**: 当本体节点存在错误（如错误的 type、不合法的 relations、缺少 testable_signal）时，`ontology-check` skill 仅做门禁校验和拒绝，**没有专门的技能来修正本体错误**。现有的 `remediate-id-collisions.py` 和 `remediate-gate-compliance.py` 处理的是任务级别的修复，不涉及本体节点修正。  
**影响**: 发现本体错误后需要人工手动编辑文件，没有标准化的修正流程和技能入口。  
**当前状态**: `skill-ontology-check.md` 是门禁入口，`ontology-validate.py` 是执行者，但缺少 `skill-remediate-ontology` 之类的修正技能。  
**修复建议**: 创建 `skills/remediate-ontology-work/SKILL.md`，提供：定位错误节点 → 分析错误类型 → 生成修正方案 → 应用修正 → 重新校验的完整流程。

#### GAP-03: ontology-validate.py 在测试夹具中不可用（规则节点依赖）

**严重程度**: 高  
**描述**: `ontology-validate.py` 的 `load_rule_specs()` 函数要求 `ontology-rule-*` 节点必须存在于校验目录中。测试 `test_ontology_validate.py` 在临时目录中只创建了单一测试节点，不包含规则节点，导致所有 3 个测试用例失败（`ERROR: 缺失规则节点`）。  
**影响**: 3 个测试用例无法验证最基本的校验功能（类型不检测、悬空引用检测）。虽然生产环境通过（0 issues），但测试覆盖存在盲区。  
**当前状态**: `test_ontology_validate.py::test_clean_passes`、`test_type_mismatch_detected`、`test_dangling_detected` 均失败。  
**修复建议**: 测试夹具应包含完整的 `ontology-rule-*` 节点副本，或为 `load_rule_specs` 提供回退常量。

### 3.2 中等缺口（Medium）

#### GAP-04: 本体知识产生后无自动验证机制（实时门禁缺失）

**严重程度**: 中  
**描述**: 本体知识写入 `ontology/` 后，验证仅在以下时机触发：
- `ontology-check` skill 的人工入口（手动触发）
- CI 硬门禁（commit/push 时）
- `archive_ontology_ready_issues`（归档前）

但**在写入过程中**（如 `ontology_induction.py` 生成候选后人工编辑写入），没有实时门禁阻止不符合规范的中间状态。  
**影响**: 存在短暂的不一致窗口，虽有 CI 兜底，但非实时。  
**当前状态**: `ci-ontology-gate.py` 提供 commit 级硬门禁，但无 pre-write 拦截。  
**修复建议**: 在 `skills/ontology-check` 中增加 `--on-write` 选项，作为文件写入后的立即校验钩子。

#### GAP-05: 关系树驱动拆分未默认启用

**严重程度**: 中  
**描述**: `ontology_tree_split.py` 的调用条件是"仅当 PRD 含 `## 拆分映射` 且父任务 `meta.ontology_fragment` 非空时启用"（步骤 3.5）。这意味着大多数任务拆分不经过关系树驱动，仅依赖人工章节划分。  
**影响**: 本体关系树对任务拆分的指导作用被限制在显式声明了拆分映射的 PRD 上，大量任务拆分可能未充分利用本体结构。  
**当前状态**: 可选、顾问式，不声明 `## 拆分映射` 时跳过。  
**修复建议**: 考虑将关系树驱动拆分为默认行为（当 `meta.ontology_fragment` 存在时自动启用），或至少提供提示引导 PRD 作者添加拆分映射。

#### GAP-06: 收敛验证测试因 ONTOLOGY_FRAGMENT_MISSING 被拦截

**严重程度**: 中  
**描述**: `test_convergence.py::test_do_to_check_transition_fails_closed` 测试期望 `CONVERGENCE_ITEM_MISSING`，但实际报错为 `ONTOLOGY_FRAGMENT_MISSING`。这是因为 `ontology_gate.py` 的 `ontology_ready_issues` 在 `do→check` 转换时先校验 `ontology_fragment` 存在性，而测试夹具的任务缺少该字段。  
**影响**: 收敛验证的完整测试链路被阻断，无法验证"缺少收敛项→Do→Check 转换失败"的核心路径。  
**当前状态**: 测试失败，实际错误码为 `ONTOLOGY_FRAGMENT_MISSING`。  
**修复建议**: 测试夹具应添加 `meta.ontology_fragment` 字段，或调整 `ontology_gate.py` 的校验顺序使收敛校验优先于 ontology_fragment 校验。

#### GAP-07: CI 门禁因历史归档任务失败

**严重程度**: 中  
**描述**: `test_ci_gate_ok_on_clean_repo` 因 `pdca/tasks/archive/2026-08/0831-old-arch-refs-audit` 缺少 convergence-map 而失败。该任务是 2026-08-31 创建的归档任务，`phase: "archive"` 但 `records/T0447-0831-old-arch-refs-audit/evidence/` 下无 `convergence-map.json`。  
**影响**: CI 门禁被历史数据问题污染，无法作为可靠的流水线门禁。  
**当前状态**: `ci-ontology-gate.py` 返回非零退出码。  
**修复建议**: 为该任务补登记 convergence-map，或在 `ci-ontology-gate.py` 中增加对已归档任务的豁免逻辑。

### 3.3 低优先级缺口（Low）

#### GAP-08: ontology_induction.py 仅支持知识草稿适配器

**严重程度**: 低  
**描述**: `ontology_induction.py` 当前仅实现 `KnowledgeDraftAdapter`，code/web 适配器仅为扩展点（AC-5），尚未实现。  
**影响**: 知识归纳的来源局限于 markdown 文件，无法从代码库或 Web 源自动提取本体候选。  
**当前状态**: `Adapter` 基类已定义，`KnowledgeDraftAdapter` 已实现，code/web 适配器为 TODO。

#### GAP-09: 孤岛节点检查仅在归档时触发

**严重程度**: 低  
**描述**: `ontology_graph.py` 可检测孤岛节点（当前 0 孤岛），但 `islands` 检查仅在 `archive_ontology_ready_issues`（归档前）中触发。日常开发中不主动检查孤岛节点。  
**影响**: 孤岛节点在日常开发中可能累积，仅在归档时才发现。  
**当前状态**: `archive_ontology_ready_issues` 调用 `ontology_graph.py --format summary` 检测孤岛。

---

## 四、本体知识不断补充与完善的机制分析

### 4.1 补充管道

本体知识的补充通过以下管道完成：

```
知识产生源                    归纳工具                      门禁校验                    写入
─────────                    ───────                      ────────                    ────
Grilling Q&A ──→ CONTEXT.md  │                            │
领域建模决策 ──→ ontology/   │  ontology_induction.py     │  ontology-check skill     │  ontology/<type>/<slug>.md
知识草稿文件 ──→ _candidates │  (适配器→推断→输出)        │  (AC-1~AC-6 校验)        │
Web/代码源(待实现)           │                            │
```

### 4.2 当前机制评估

**已实现的机制**：
1. **人工写入 + 校验**：`ontology-check` skill 提供人工门禁入口，`ontology-validate.py` 执行自动化校验
2. **半自动归纳**：`ontology_induction.py` 从知识草稿推断候选，HITL 保留（不自动落盘）
3. **CI 硬门禁**：`ci-ontology-gate.py` 在 commit/push 时执行本体校验
4. **归档自检**：`archive_ontology_ready_issues` 在归档前执行本体校验 + 孤岛检查
5. **规则节点驱动**：`ontology-rule-*` 节点的 `rule_spec` 作为校验参数唯一来源，改节点即改校验行为

**缺失的机制**：
1. **自动触发归纳**：没有 cron/job 自动运行 `ontology_induction.py` 扫描新增知识草稿
2. **归纳→校验→写入的自动化闭环**：`ontology_induction.py` 仅打印候选，需要人工编辑后手动写入
3. **错误修正技能**：无专门技能处理本体错误修正
4. **实时门禁**：写入过程中无实时拦截
5. **反馈回路**：测试失败或运行时错误不自动触发本体更新建议

### 4.3 本体版本控制与溯源

- 每个本体节点有 `source_ids` 字段（如 `T0245-0809-writing-for-agents-levers`）追溯来源任务
- `skill-grilling.md` 明确"不可逆决策记录到对应的 ontology 节点（添加决策背景节）"
- `ontology-creation-gate.md` 记录决策背景（原 ADR-0033/0034/0036）
- `records/<record-id>/` 保留空壳 + redirect（T0418 物理归并后）

---

## 五、修复机制分析

### 5.1 现有修复机制

| 修复类型 | 脚本/技能 | 覆盖范围 | 自动化程度 |
|----------|-----------|----------|------------|
| ID 撞车重分配 | `remediate-id-collisions.py` | task.json + records + 归档目录 + 引用链 | dry-run + apply |
| 门禁合规修复 | `remediate-gate-compliance.py` | verdict 补齐、豁免标记、嵌套副本清理、active 残留移除 | dry-run + apply |
| 阶段回滚 | `rollback-phase.sh` | task.json 状态回滚（保留 evidence/conclusion/journal） | 手动触发 |
| 任务引用替换 | `remediate-id-collisions.py::_rewrite_references` | parent/children/dependencies 中的旧 ID（上下文感知） | apply |
| 记录流事件同步 | `remediate-id-collisions.py::_sync_record_flow_events` | flow-events 中的 record_id/task_id | apply |

### 5.2 修复机制的覆盖盲区

**本体节点层面的修复**：
- 无专用修复脚本：当本体节点的 `type` 不匹配目录名、`relations` 引用悬空、`testable_signal` 缺失时，需要人工手动编辑
- `ontology-clash-check.py` 仅检测冲突，不提供修复建议
- `ontology_tree_split.py` 报错退出但不提供修复建议

**测试层面的修复**：
- `test_ontology_validate.py` 的失败测试用例需要修复测试夹具（补充规则节点）
- `test_convergence.py` 的失败测试需要调整测试夹具（添加 ontology_fragment）
- `test_ci_gate_ok_on_clean_repo` 需要修复历史归档任务数据

### 5.3 修复流程建议

```
发现本体错误
    │
    ├── 运行时发现（CI 门禁 / 归档自检）
    │     └── → 人工分析错误码 → 手动编辑 ontology/ 节点 → 重新校验
    │
    ├── 测试发现（test_ontology_*.py）
    │     └── → 修复测试夹具或修复本体节点 → 重新运行测试
    │
    └── 归纳发现（ontology_induction.py）
          └── → 人工审核候选 → 编辑写入 → 重新校验
```

**建议新增的修复技能**：
- `skill-remediate-ontology`：提供本体错误定位 → 分类 → 修正 → 验证的标准化流程
- `skill-regenerate-tests`：从 `testable_signal` 和本体关系自动生成/更新测试用例

### 5.4 修复机制与本体补充的闭环

当前修复机制与本体补充之间存在以下断点：

1. **修复 → 补充**：人工修正本体错误后，没有自动触发 `ontology-validate.py` 重新校验（除非手动运行或等待 CI）
2. **测试失败 → 补充**：测试失败不自动触发本体更新或归纳流程
3. **归纳候选 → 校验**：`ontology_induction.py` 生成的候选不经过 `ontology-validate.py` 校验后才写入（需要人工判断）

**闭环建议**：
- 在 `ontology_induction.py` 的输出阶段增加 `ontology-validate.py` 预校验
- 在 `skill-remediate-ontology` 中集成 `ontology-validate.py` 的重新校验步骤
- 在 CI 门禁中增加归纳候选的自动校验步骤

---

## 六、验证结果摘要

### 6.1 脚本执行结果

| 命令 | 结果 | 说明 |
|------|------|------|
| `python3 scripts/ontology-validate.py --ontology-dir ontology` | OK: 0 issues | 生产环境本体通过全部校验 |
| `python3 scripts/ontology_graph.py --format summary --root ontology` | nodes: 340, edges: 703, islands: 0 | 无孤岛节点 |
| `python3 scripts/ontology_graph.py --format dot --root ontology` | 340 nodes, 703 edges | 图谱完整 |

### 6.2 测试套件结果

| 测试文件 | 结果 | 失败数 |
|----------|------|--------|
| test_ontology_validate.py | 3/3 失败 | 3（测试夹具缺少规则节点） |
| test_ontology_tree_split.py | 5/5 通过 | 0 |
| test_ontology_clash.py | 3/3 通过 | 0 |
| test_ontology_reason.py | 6/6 通过 | 0 |
| test_ontology_induction.py | 6/6 通过 | 0 |
| test_ontology_validator_from_nodes.py | 5/5 通过 | 0 |
| test_convergence.py | 18/19 通过 | 1（ONTOLOGY_FRAGMENT_MISSING 拦截） |
| test_register_evidence_anchor.py | 3/3 通过 | 0 |
| test_pdca_task_consumption.py | 6/6 通过 | 0 |
| test_ontology_full_lifecycle.py | 4/5 通过 | 1（历史归档任务缺少 convergence-map） |
| **合计** | **56/63 通过** | **7** |

### 6.3 失败原因分类

- **测试夹具不完整**（4 个失败）：`test_ontology_validate.py` 的临时目录缺少 `ontology-rule-*` 节点，`test_convergence.py` 的任务缺少 `ontology_fragment`
- **历史数据问题**（2 个失败）：`test_ci_gate_ok_on_clean_repo` 因归档任务缺少 convergence-map
- **校验顺序问题**（1 个失败）：`test_do_to_check_transition_fails_closed` 中 `ONTOLOGY_FRAGMENT_MISSING` 优先于 `CONVERGENCE_ITEM_MISSING` 报错

---

## 七、结论

### 7.1 依赖链整体评估

本体知识产生→任务拆分→单元测试的依赖链在**宏观结构上是完整的**：
- 本体知识通过 Grill → Domain Modeling → Writing-for-Agents → ontology/ 节点 的路径产生
- 任务拆分通过 clash-check → tree-split → task_identity → compute-frontier 的管道消费本体
- 单元测试通过 testable_signal → TDD → convergence → CI 门禁 的链路验证
- 本体补充通过 Check→Act → 新节点写入 → ontology-check 门禁 的闭环完善

### 7.2 核心缺口

1. **testable_signal 不驱动测试生成**：这是最严重的缺口，本体的测试信号声明与测试执行之间存在断层
2. **无本体错误修正技能**：发现本体错误后只能人工手动修复，没有标准化流程
3. **归纳→校验→写入未自动化**：`ontology_induction.py` 仅做候选生成，需要人工介入完成闭环
4. **测试夹具不完整导致 7 个测试失败**：影响测试套件作为质量门禁的可靠性

### 7.3 改进优先级建议

1. **P0（立即）**：修复测试夹具，使 `test_ontology_validate.py` 和 `test_convergence.py` 通过
2. **P1（短期）**：创建 `skill-remediate-ontology` 修正技能，填补本体错误修正空白
3. **P2（中期）**：实现 `testable_signal` → 测试生成的自动管道
4. **P3（长期）**：实现归纳→校验→写入的全自动闭环，消除人工干预点
