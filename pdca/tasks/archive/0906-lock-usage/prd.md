# 锁使用范式本体生产

## 背景
锁教学收官，用户要求生产"锁的使用"本体节点，沉淀调用方规范。

## 目标
新建 core-six-usage-discipline 节点：快慢分发、预标记写、持有跟踪、身份快照四规范。

## 功能需求
1. 基于教学内容编写节点，relations 关联锁相关节点
2. 三查 + validate 全绿

## 非功能需求
- 真实时间戳；只增修 .md

## 验收标准
- [ ] AC-1 节点内容详实，四规范有代码依据
- [ ] AC-2 三查 0 issues，validate 全绿
- [ ] AC-3 证据登记进Check归档

### 声明的测试接缝
- seam: scripts/ontology-validate.py -> ontology/domain/core-six-usage-discipline.md

## 风险与对策
- 风险：与现有锁节点重复。对策：本节点只讲调用方规范，不讲锁机制
