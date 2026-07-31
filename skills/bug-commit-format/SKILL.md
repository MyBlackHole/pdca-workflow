---
name: bug-commit-format
description: Use when fixing bugs and committing changes — commit messages must include bug description, root cause, solution, impact scope, and performance impact
---

# Bug Commit Format

## 模板
```
【B-xxxx】: {简短标题}

## 问题描述
<现象+复现步骤>

## 根因
<为什么会发生>

## 解决方案
<怎么修复的>

## 影响范围
<影响的模块/用户/版本>

## 测试验证
- [ ] 复现步骤已验证通过
- [ ] 回归测试通过
```

## 铁律
- 每个 commit 只修复一个 bug
- 标题 ≤72 字符，动词开头（fix/修复）
- 根因 ≠ 现象，必须追到代码层面
- 影响范围必须有具体模块名
