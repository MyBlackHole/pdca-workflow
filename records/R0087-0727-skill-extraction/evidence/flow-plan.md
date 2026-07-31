---
name: flow-plan
description: |
  计划阶段执行流。从问题定义到执行方案的完整流程。
  覆盖 grill、领域建模、spec 合成、任务拆解、方案确认。
---

# 计划阶段执行流（PDCA — Plan）

## 入口条件
- 用户提出一个需求、issue 或想法（不一定有 task.json）
- 如果 `task.json` 已存在且 `meta.phase` 为 `plan`，跳过 triage

## 步骤

### 0. Triage（分类与前处理）
加载 `skills/triage/SKILL.md`（`disable-model-invocation: true`）：

- 将模糊输入分类为 bug 或 enhancement
- 查重：搜索已有 task（含 archive/）、`knowledge/`、`knowledge/out-of-scope/`
- 验证 claim：代码 bug → 分析复现；需求缺陷 → 对照现有文档分析
- 信息不足时联动 grill 追问补齐
- 输出 `task.json`（`meta.phase: "plan"`，含 `scenario_type`）+ `prd.md` 骨架 + `triager-brief.md`

跳到步骤 1。

### 1. 需求澄清与假设收集
读取 `prd.md`、`design.md`、`implement.md`（若存在）。
收集问题陈述、目标、验收标准。

### 2. Grill + 领域建模 + 目标对齐确认
按以下顺序执行：

**阶段 2a — Grill 追问**
加载 `skills/grill/SKILL.md` 和 `skills/domain-modeling/SKILL.md`：

- 逐条追问设计遗漏、边界条件、备选方案
- 每个问题附带推荐答案，走完决策树
- 模糊术语立即写入 `pdca/CONTEXT.md`
- 硬决策写入 `docs/adr/ADR-NNNN-标题.md`
- Q&A 记录追加到 `clarifications.jsonl`（`source: "grill"`）

**阶段 2b — 对齐确认（关键门禁）**
走完决策树后，**必须**向用户做对齐总结：

```
我理解的目标是：<一句话>
    - 范围：<已确认的范围>
    - 方案方向：<已确认的设计方向>
    - 验收标准：<已确认的标准>
    - 关键决策：<已确认的取舍>

以上理解是否正确？请确认或指正。
```

**得到用户确认后**才能进入步骤 3（合成 PRD）。
用户提出修改 → 回到 2a 继续追问，直到对齐。

复杂的任务（3+ 模块/外部系统/数据变更）：
- 写 `design.md`（边界接口、数据流、验证方法）
- 写 `implement.md`（检查清单、验证命令、回滚点）

### 3. 合成 PRD（to-spec）
基于 grill 结果和 CONTEXT.md 完善 `prd.md`。

模板参考：加载 `templates/to-spec/SPEC.md`，按以下结构填充：

```markdown
## 问题陈述
## 解决方案
## 用户故事
## 实现决策
## 测试决策
## 范围外
## 备注
```

### 4. 拆解为任务
将大型目标拆解为多个子任务：
1. 在 `pdca/tasks/` 下创建子任务目录
2. 写子任务的 `task.json`（`parent` 指向父任务）
3. 更新父任务的 `children` 列表
4. 确保子任务可独立推进

### 5. 知识注入
搜索 `knowledge/` 下相关主题的可复用知识。
将相关文件引用追加到 `implement.jsonl`：

```
{"file": "knowledge/auth/authz-patterns.md", "reason": "目标涉及权限模型，可复用已有设计", "action": "read", "at": "..."}
```

### 6. 方案终审（最终确认）
向用户展示完整方案：
- 目标、范围、验收标准
- 设计决策和备选方案
- 任务拆解结构

此步骤是**最终签字确认**，区别于步骤 2b 的方向对齐。用户可通过此步骤：
- 确认方案完整，进入 Do
- 发现遗漏 → 回到步骤 2 补充追问
- 变更范围 → 回到步骤 1/2 重新澄清

### 7. 进入 Do 阶段
用户确认后，加载 `skills/advance-phase/SKILL.md`，目标 phase: `do`。

## 退出
- 完成: `meta.phase` = `"do"`
- 废弃: 移入 `archive/`