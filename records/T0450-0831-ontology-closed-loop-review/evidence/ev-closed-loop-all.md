# 本体论完整闭环融入审查报告

**审查日期**: 2026-08-31  
**审查范围**: `/home/black/Documents/pdca-workflow-pro/ontology/` 及 `ontology/process/`  
**方法**: 文件读取、脚本执行、流程分析

---

## 一、各阶段本体消费机制

### 1.1 Plan 阶段（flow-plan）

| 机制 | 状态 | 说明 |
|------|------|------|
| ontology_fragment 声明 | 已实现 | development/bugfix 任务须声明 `meta.ontology_fragment` |
| ontology-ready 关卡 | 已实现 | Do 前置校验 `meta.ontology_fragment` 存在且结构合法 |
| final_confirmation 门禁 | 已实现 | 用户确认后经 `transition-phase.py` 进入 Do |
| 本体自举豁免 | 已实现 | `meta.ontology_exempt=true` 豁免 ontology-ready |

**缺口**: Plan 阶段本体消费为顾问式（不阻断），仅 final_confirmation 为硬门禁。

### 1.2 Do 阶段（flow-do）

| 机制 | 状态 | 说明 |
|------|------|------|
| ontology-ready 关卡 | 已实现 | `meta.ontology_fragment` 指向的领域片段须存在且结构合法 |
| 执行中对照本体 | 已实现 | 复用既有 `id`/`type`/`relations`，新概念落盘到 `ontology/` |
| 证据登记 | 已实现 | `register-evidence` 把产物锚定到 `pdca-evidence` 子类型 |
| Phase Boundary 决策树 | 已实现 | 5 选项决策树（continue/clear/handoff/subagent/compact） |

**缺口**: Do 阶段 ontology-ready 为硬门禁，但执行中的本体对照为顾问式。

### 1.3 Check 阶段（flow-check）

| 机制 | 状态 | 说明 |
|------|------|------|
| 对照验证 | 已实现 | 依据 PRD 验收标准、登记证据、convergence.json 逐项核验 |
| verify-convergence 门禁 | 已实现 | 阶段 Decision 必须引用证据；结论映射 pdca-verdict 三态 |
| 证据锚定 | 已实现 | `register-evidence --kind` 须命中 `pdca-evidence` 子类型 |
| 结论确认 | 已实现 | 用户 `check_confirmation` 确认 verdict 后进入 Act |

**缺口**: 证据锚定已实现（AC-1），结论锚定已实现（AC-2），但 `testable_signal` 不驱动测试生成。

### 1.4 Act 阶段（flow-act）

| 机制 | 状态 | 说明 |
|------|------|------|
| 知识处置 | 已实现 | 显式投影 `ontology/domain/<topic>-<slug>.md`，记来源记录/摘要/理由 |
| disposition 与 journal | 已实现 | 写入 `meta.disposition`，更新 journal |
| archive 本体自检 | 已实现 | `ontology-validate.py` + `islands=0` 校验 |
| 自我优化闭环 | 已实现 | 记录→分析→决策→受控实施→效果验证 |

**缺口**: 知识处置为顾问式（不阻断），archive 自检为硬门禁。

### 1.5 Archive 阶段

| 机制 | 状态 | 说明 |
|------|------|------|
| ontology-validate | 已实现 | 归档前必须通过 |
| islands=0 检查 | 已实现 | `ontology_graph.py --format summary` 检测 |
| CI 硬门禁 | 已实现 | `ci-ontology-gate.py` 在 push/PR 时复跑 |

---

## 二、硬门禁清单

### 已实现的硬门禁（T0414）

| 门禁 | 阶段 | 实现方式 |
|------|------|----------|
| 证据锚定 AC-1 | Check | `register-evidence.py` 枚举 `pdca-evidence` 子类型建允许表 |
| 结论锚定 AC-2 | Check/Act | `meta.verdict.outcome` 映射到 `verdict-<outcome>` 节点 |
| Archive 自检 AC-3 | Act→Archive | `transition-phase.py` 调用 `ontology-validate.py` + `islands=0` |
| CI/Hook AC-4 | 全阶段 | `ci-ontology-gate.py` + `install-git-hook.sh` + `.github/workflows/ontology-gate.yml` |

### 顾问式（非硬门禁）

| 消费 | 阶段 | 说明 |
|------|------|------|
| ontology_fragment 声明 | Plan | 仅声明，不阻断 |
| 执行中对照本体 | Do | 复用/落盘为顾问式 |
| 知识处置 | Act | 显式投影但不阻断 |
| 孤岛检查 | 日常 | 仅归档时触发 |

---

## 三、闭环完整性评估

### 3.1 已闭环的环节

1. **创建门禁**: ontology-check → ontology-validate.py → AC-1~AC-6
2. **证据锚定**: register-evidence → pdca-evidence 子类型 → evidence_type_ref
3. **结论锚定**: verdict → pdca-verdict 三态 → meta.verdict.outcome
4. **Archive 自检**: ontology-validate + islands=0 → 转换拒绝
5. **CI 门禁**: ci-ontology-gate.py → pre-commit + push/PR

### 3.2 未闭环的缺口

1. **testable_signal → 测试生成**: AC-4 仅校验存在性，不驱动测试
2. **实时门禁**: 写入过程中无实时拦截，仅 CI 兜底
3. **归纳→校验→写入自动化**: ontology_induction.py 仅打印候选
4. **本体错误修正**: 无专门技能处理本体节点修正

---

## 四、验证结果

- `python3 scripts/ontology-validate.py --ontology-dir ontology` → **OK: 0 issues**
- `python3 scripts/ontology_graph.py --format summary` → **340 nodes, 703 edges, 0 islands**
- 测试套件: **56/63 通过**（7 个失败均为测试夹具问题）

---

## 五、缺口清单

| 编号 | 缺口 | 严重程度 | 说明 |
|------|------|----------|------|
| GAP-01 | testable_signal 不驱动测试生成 | 高 | AC-4 仅校验存在性 |
| GAP-02 | 缺少本体错误修正技能 | 高 | 发现错误后只能人工手动编辑 |
| GAP-03 | ontology-validate.py 测试夹具不完整 | 高 | 临时目录缺少 ontology-rule-* 节点 |
| GAP-04 | 实时门禁缺失 | 中 | 写入过程中无实时拦截 |
| GAP-05 | 关系树驱动拆分未默认启用 | 中 | 仅当 PRD 含 ## 拆分映射时触发 |
| GAP-06 | 收敛验证测试被 ONTOLOGY_FRAGMENT_MISSING 拦截 | 中 | 测试夹具缺少 ontology_fragment |
| GAP-07 | CI 门禁因历史归档任务失败 | 中 | 归档任务缺少 convergence-map |
| GAP-08 | ontology_induction.py 仅支持知识草稿适配器 | 低 | code/web 适配器未实现 |
| GAP-09 | 孤岛节点检查仅在归档时触发 | 低 | 日常开发中不主动检查 |
