---
name: code-review
description: |
  双轴代码审查。对照编码标准（标准轴）和原始 spec（规范轴）两个独立维度
  审查变更差异，并行子代理运行、合并报告。
---

# 双轴代码审查（PDCA — 质量门禁）

## 入口条件
- 编译通过、测试通过
- 有明确的对比基点（commit / branch / tag / merge-base）

## 流程

### 1. 确定对比基点
用户提供的固定点（commit SHA、分支名、tag、`HEAD~N` 等）。
```bash
git diff <fixed-point>...HEAD    # 三点 diff，针对 merge-base
git log <fixed-point>..HEAD --oneline
```

确认基点 resolve 且 diff 非空。基点无效或 diff 为空时提前退出。

### 2. 确定规范来源
按优先级查找：

1. commit message 中的 issue 引用（`#123`, `Closes #45` 等）
2. 用户直接传入的路径
3. `prd.md`、`docs/`、`specs/` 下的 spec 文件
4. 以上均无 → 规范轴跳过，报告"无可用 spec"

### 3. 确定标准来源
扫描 repo 中记录编码规范的文件（`CODING_STANDARDS.md`、`CONTRIBUTING.md` 等）。

除项目文档外，标准轴始终携带以下 **Fowler 坏味基线**（《Refactoring》ch.3）：

| 坏味 | 识别方式 | 处理 |
|------|----------|------|
| Mysterious Name | 名称不揭示用途 | 重命名 |
| Duplicated Code | 相同逻辑在多处出现 | 提取共用 |
| Feature Envy | 方法更多操作外部数据 | 移到被依赖对象 |
| Data Clumps | 同组参数反复出现 | 封装为类型 |
| Primitive Obsession | 原始类型替代领域概念 | 定义专有类型 |
| Repeated Switches | 相同 switch/if 级联 | 多态 / 映射表 |
| Shotgun Surgery | 单次改动散落多处 | 合并到同一模块 |
| Divergent Change | 同一文件因多原因修改 | 拆分模块 |
| Speculative Generality | 为不存在需求的抽象 | 删除 / 内联 |
| Message Chains | 长调用链 `a.b().c().d()` | 隐藏遍历 |
| Middle Man | 类/函数仅委托转发 | 直调目标 |
| Refused Bequest | 子类忽略大部分继承 | 组合替代继承 |

**规则**：项目文档标准优先于基线；基线坏味始终是判断（judgement call）而非硬性违规；跳过工具已强制执行的事项。

### 4. 并行子代理审查
一个 message 内启动两个子代理，独立运行：

**标准轴子代理** — 收到：
- diff 命令与 commit 列表
- 标准来源文件列表 + 以上坏味基线全文
- 指令："报告每个文件/hunk 中 (a) 违反项目标准之处：引用标准文件+规则；(b) 基线坏味：命名+引用 hunk。区分硬违规（违反文档标准）和判断（基线坏味）。跳过工具已执行项。400 字以内。"

**规范轴子代理** — 收到：
- diff 命令与 commit 列表
- spec 内容或路径
- 指令："报告 (a) spec 要求但缺失或未完成的功能；(b) diff 中存在但 spec 未要求的功能（范围蔓延）；(c) 已实现但实现方式错误的功能。引用 spec 原文。400 字以内。"

### 5. 聚合报告
分别以 `## 标准轴` 和 `## 规范轴` 标题呈现两个报告，**不合并、不排序**。

结尾一行总结：每轴发现数 + 最严重问题（如有）。

## 门禁判定

| 严重度 | 标准 | 动作 |
|--------|------|------|
| 🔴 Blocking | 规范缺失 / 安全漏洞 / 数据丢失 | 必须修复 |
| 🟠 Warning | 基线坏味 / 代码异味 / 风格不一致 | 建议修复 |
| 🟢 Info | 可优化项 | 记录即可 |

**门禁**: Blocking 数量 = 0

## 退出
- 通过 → 继续 Do/Act 流程
- 未通过 → 修复 → 重新审查

## 双轴分离目的
同一变更可能通过一轴而失败另一轴：
- **标准通过、规范失败**：代码合规但实现错误功能
- **规范通过、标准失败**：功能正确但破坏编码规范

独立报告防止某一轴掩盖另一轴的问题。