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

### 2. Grill + 领域建模
加载 `skills/grill/SKILL.md` 和 `skills/domain-modeling/SKILL.md`：

- 逐条追问设计遗漏、边界条件、备选方案
- 每个问题附带推荐答案，走完决策树
- 模糊术语立即写入 `pdca/CONTEXT.md`
- 硬决策写入 `docs/adr/ADR-NNNN-标题.md`
- Q&A 记录追加到 `clarifications.jsonl`（`source: "grill"`）

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

### 6. 方案确认展示
向用户展示：
- 目标、范围、验收标准
- 设计决策和备选方案
- 任务拆解结构

等待用户确认或修改。

### 7. 进入 Do 阶段
用户确认后，更新 `task.json`：
- `meta.phase` → `"do"`
- `status` → `InProgress`（非 pending 任务）

## 退出
- 完成: `meta.phase` = `"do"`
- 废弃: 移入 `archive/`