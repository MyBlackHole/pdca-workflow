---
name: code-review
description: |
  双轴代码审查。对照编码标准（标准轴）和原始 spec（规范轴）两个独立维度
  审查变更差异，在可用时用独立执行器运行双轴，否则在主会话保持两轴独立。
---

# 双轴代码审查

## 入口条件
- 编译通过、测试通过
- 有明确的对比基点（commit / branch / tag / merge-base）

## 流程

### 1. 确定对比基点
```bash
git diff <fixed-point>...HEAD
git log <fixed-point>..HEAD --oneline
```
基点 resolve 且 diff 非空，否则提前退出。

### 2. 确定规范来源（优先级）
1. commit message 中的 issue 引用（`#123`, `Closes #45`）
2. 用户直接传入的路径
3. `prd.md`、`knowledge/`、`specs/` 下的 spec 文件
4. 以上均无 → 规范轴跳过，报告"无可用 spec"

### 3. 确定标准来源
扫描项目中的 `CODING_STANDARDS.md`、`CONTRIBUTING.md` 等编码规范文件。
标准轴始终同时携带 Fowler 坏味基线（Mysterious Name / Duplicated Code / Feature Envy / Data Clumps / Primitive Obsession / Repeated Switches / Shotgun Surgery / Divergent Change / Speculative Generality / Message Chains / Middle Man / Refused Bequest — 见《Refactoring》ch.3）。
**规则**：项目标准优先于基线；基线坏味为 judgement call 非硬性违规；跳过工具已强制执行项。

### 4. 双轴独立审查
`agent.spawn` 可用时通过当前环境 Adapter 启动两个独立执行器；不可用时由主 session 依次执行，但不得让第一轴结论污染第二轴输入：
- **标准轴**：diff + 标准来源 + 坏味基线 → 报告硬违规（违反项目标准）和判断项（坏味），400 字以内
- **规范轴**：diff + spec → 报告 (a) spec 要求但缺失；(b) 额外功能（范围蔓延）；(c) 实现方式错误，引用 spec 原文，400 字以内

### 5. 聚合报告
以 `## 标准轴` 和 `## 规范轴` 独立呈现，不合并。结尾一行：每轴发现数 + 最严重问题。

## 门禁判定
| 严重度 | 标准 | 动作 |
|--------|------|------|
| Blocking | 规范缺失 / 安全漏洞 / 数据丢失 | 必须修复 |
| Warning | 坏味 / 风格不一致 | 建议修复 |
| Info | 可优化项 | 记录即可 |

**门禁**: Blocking = 0

## 退出
- 通过 → 继续 Do/Act 流程
- 未通过 → 修复 → 重新审查

## 已知坑

- 双轴审查勿只盯标准轴（编码风格）而忽略规范轴（原始 spec 是否满足）——偏离 spec 的"好代码"同样不合格。
