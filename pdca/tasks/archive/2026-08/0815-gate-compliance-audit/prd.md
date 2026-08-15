# 门禁有效性审计 + transition 拒绝留痕机制（第六轮）

## 问题陈述

- **现状**: PDCA 门禁（plan→do→check→act→archive 的 transition 语义校验、convergence、verdict、final_confirmation）在每轮强制执行，但从未被系统审计：(1) 全量归档任务的 receipts/verdict/convergence/final_confirmation 合规覆盖未知；(2) transition 被拒时只打印 stderr，**无持久记录**（第五轮 T0269 中多次被拒均无留痕），门禁拦截不可计数、不可审计。
- **目标**: 审计全量任务门禁合规度（覆盖 + 异常分类），并新增 **transition 拒绝留痕机制**（被拒时写 rejected receipt），使门禁拦截可计数、可审计，从而证明门禁体系的实际有效性。
- **差距**: 查重通过——scripts/tests 无 gate compliance 扫描、无 gate-rejection 记录；transition-receipts/ 只存成功 receipt。

## 解决方案

### 增量一：门禁合规扫描（审计既有）

新增 `scripts/audit-gate-compliance.py`：

- **全量扫描**: 遍历 `pdca/tasks`（含 archive/active/根目录）所有 `task.json`，对每个任务采集：
  - `transition-receipts/` 成功 receipt 数量（与 phase 对照：archive 应含 plan→do→check→act→archive）
  - `meta.verdict` 是否存在（check→act 门禁）
  - `meta.convergence` 是否非空（plan→do 门禁）
  - `clarifications.jsonl` 是否含 `final_confirmation`（plan→do 门禁）
  - `id` 唯一性（撞车检测）
  - 归档一致性（同一 slug 重复归档、active 残留）
- **异常分类**: 机制前任务（早期 T0xxx 未纳入门禁，仅报告不判违规）vs 真违规（phase 前进但缺要素）。
- **合规报告**: 输出 `gate-compliance-audit.md`（覆盖率统计 + 异常清单 + 分类 + 结论）。

### 增量二：transition 拒绝留痕机制（新机制）

修改 `scripts/transition-phase.py`：4 个拒绝点（NON_ADJACENT / PRD acceptance / gate_issues / schema_issues）统一写 **rejected receipt**：

- 文件: `transition-receipts/rejected-<ns>-<to>.json`
- schema: `pdca.gate-rejection/v1`
- 内容: `task_id`、`from`、`to`、`error`（error_code 或 issues 列表）、`at`
- 时间戳用纳秒保证唯一（多次拒绝不覆盖）
- 成功后不受影响（仍写成功 receipt）

### 增量三：拒收可审计性

- `audit-gate-compliance.py` 同时统计 rejected receipts 数量（若存在），证明门禁拦截有记录。
- 拒收率 = rejected receipts / (成功 + rejected)，可作为门禁有效性指标。

**硬指标**：
- **行为级**: 拒绝留痕 fixture 测试（无 final_confirmation 被拒 → 生成 rejected receipt，schema 合法）。
- **数据级**: 合规扫描覆盖率/异常数/拒收数可复现。
- **判定级**: 合规报告结论（门禁覆盖度、真违规清单、修复建议）。

## 测试决策

- 被测模块: `scripts/audit-gate-compliance.py`（扫描/分类/报告）、`scripts/transition-phase.py`（拒绝留痕）。
- 好测试: 拒绝留痕 fixture、合规扫描 fixture（构造含/缺要素的任务）、撞车检测 fixture、报告结构断言。
- 场景: research（审计主导）；transition-phase 修改有行为测试覆盖。
- 明确不做: 直接修改存量任务（报告给出清单，修复动作交后续）；重开 T0263 identity 观察（不重叠，本任务不含 identity 四维）。

## 用户故事

1. 作为流程负责人，我希望门禁合规覆盖可量化，以便确认门禁体系被完整执行。
2. 作为流程负责人，我希望 transition 拒绝有记录，以便计数门禁拦截、识别反复违规。
3. 作为审计者，我希望异常分类区分机制前任务与真违规，以便聚焦修复。

## 实现决策

- 语言: Python 3，单文件脚本，subprocess 调用（既有先例）。
- 合规报告: markdown 存 records/ 目录。
- 拒绝 receipt: 原子写（atomic_json 复用），不破坏既有成功 receipt 语义。
- 范围外: 存量任务修复执行、id 撞车修复（仅报告）。

## 备注

- 前置调查已发现真实信号：T0208/T0207/T0209 无 verdict 却归档、14 个 id 撞车（T0142 双任务、T0214 三路径）、嵌套重复归档、active 残留。
- T0263 identity 观察窗未触发（第 1 天，新任务不足 20 个），本任务不冲突。

## 验收标准

- [ ] AC-1: `scripts/audit-gate-compliance.py` 存在且可运行，扫描全量任务并采集 receipts/verdict/convergence/final_confirmation/id 唯一性/归档一致性。
- [ ] AC-2: 合规报告 `gate-compliance-audit.md` 含覆盖率统计 + 异常清单 + 分类（机制前 vs 真违规）。
- [ ] AC-3: `scripts/transition-phase.py` 4 个拒绝点写 rejected receipt（schema `pdca.gate-rejection/v1`，纳秒时间戳唯一）。
- [ ] AC-4: 拒绝留痕 fixture 测试：无 final_confirmation 被拒 → 生成 rejected receipt，内容含 from/to/error/at。
- [ ] AC-5: 合规扫描测试：构造含/缺要素任务 + 撞车检测 fixture，报告结构断言。
- [ ] AC-6: 拒收统计可复现（rejected 数量 + 拒收率），写入报告。
- [ ] AC-7: 既有 transition 成功路径不受影响（成功 receipt 仍写），新增测试通过，全量 4 失败保持非回归。
