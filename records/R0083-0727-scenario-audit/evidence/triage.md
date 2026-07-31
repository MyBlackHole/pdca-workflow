---
name: triage
description: |
  将模糊需求/issue 分类为 bug 或 enhancement，查重、验证 claim、
  信息不足时联动 grill 追问，输出 ready-to-plan 的 task.json + prd.md 骨架。
disable-model-invocation: true
---

# Triage — 问题分类与前处理

## 状态机

```
needs-triage → needs-info → ready-to-plan
                   ↑              │
               (grill 追问)   输出 task.json + prd.md + brief
                   │
              wontfix（写入 knowledge/out-of-scope/）
```

两种 category：`bug`（已有代码/设计缺陷）、`enhancement`（新功能/改进）。

## 流程

### 1. 初始分类 + 场景类型推断

用户输入需求/issue 后，判断 category 和 scenario_type：

**category**（bug / enhancement）：

- **bug** — 现有代码或流程行为不符合预期，有复现路径
- **enhancement** — 新功能、性能优化、重构、流程改进

**scenario_type**（决定 Do 阶段执行路径）：

| 输入形态 | 推断的 scenario_type |
|----------|---------------------|
| 用户报 bug / 缺陷 | `bugfix` |
| 需求明确是新增功能/模块/特性 | `development` |
| "调研/调查/分析一下 XXX" | `research` |
| "把需求转为文档/写技术文档" | `documentation` |
| "设计 XXX 的架构" | `design` |
| "审查/Review XXX 的代码" | `review` |
| 纯 enhancement（重构/优化/替换） | `development` |
| 不确定 | 留空，Plan 阶段补充

### 2. 查重
搜索以下位置确认不是已有事项：

1. `pdca/tasks/**/task.json`（含 `archive/`）— 按 title 和 description 匹配
2. `knowledge/out-of-scope/*.md` — 已被拒的类似请求
3. `knowledge/**/*.md` — 已实现的方案

### 3. 验证 claim

**bug 验证**：
- 代码缺陷 → 检查 `git diff`、相关文件逻辑，尝试确认复现条件
- 设计缺陷 → 对照 `prd.md`、`CONTEXT.md`、ADRs 分析

**enhancement 验证**：
- 搜索代码库确认是否已存在类似实现
- 如果涉及新增模块，检查现有模块能否扩展

### 4. Grill 联动（信息不足时）
信息不足以做出分类判断时，加载 `skills/grill/SKILL.md` 追问补齐：

- 对 bug：复现步骤、环境、预期 vs 实际行为
- 对 enhancement：解决的问题、用户场景、验收标准

Q&A 记录追加到 `clarifications.jsonl`（`source: "triage"`）。

### 5. 输出

**ready-to-plan**：创建 `pdca/tasks/<MMDD-slug>/`，写入：

- `task.json` — `meta.phase: "plan"`，`status: "Pending"`，category 标记，`scenario_type`（根据步骤 1 推断的值）
- `prd.md` — 骨架（问题陈述 + 已知信息 + 信息缺口）
- `triager-brief.md` — 结构化 brief：

```markdown
# Triage Brief

## 分类
- category: bug | enhancement
- scenario_type: development | bugfix | research | documentation | design | review
- 描述: <一句话>

## 验证结果
- <已确认/待确认/无法复现>

## 信息缺口
- <待补充的问题清单>

## 查重结果
- <相关已有 task 或知识>

## 下一步建议
- <推荐 Plan 阶段重点关注>
```

**wontfix**：在 `knowledge/out-of-scope/` 创建 `<slug>.md`：

```markdown
# <标题>

## 请求描述
<原始需求>

## 拒绝原因
- <原因 1>
- <原因 2>

## 日期
YYYY-MM-DD
```

关闭 issue（无对应 task 则无需操作）。

## 退出条件
- `ready-to-plan` → Plan 阶段接手
- `wontfix` → 记录归档，无需推进