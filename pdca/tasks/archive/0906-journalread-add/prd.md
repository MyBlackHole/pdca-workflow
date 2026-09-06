# journal指南恢复读增补

## 背景
教学第六讲（恢复读执行）获用户确认，要求增补进指南节点。

## 目标
core-journal-study-guide 增补恢复读执行细节节。

## 功能需求
1. 增补多盘并发读/副本仲裁/桶定位/间隙重读四节
2. 三查 + validate 全绿

## 非功能需求
- 真实时间戳；只改指南文件

## 验收标准
- [ ] AC-1 增补内容详实，四节有代码依据
- [ ] AC-2 三查 0 issues，validate 全绿
- [ ] AC-3 证据登记进Check归档

### 声明的测试接缝
- seam: scripts/ontology-validate.py -> ontology/domain/core-journal-study-guide.md

## 风险与对策
- 风险：与现有恢复节重复。对策：只讲读执行，不讲定界语义
