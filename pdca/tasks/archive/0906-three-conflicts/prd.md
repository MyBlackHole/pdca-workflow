# 三矛盾讲解本体生产

## 背景
教学中三矛盾讲解（场景化）获用户确认，要求记录为本体。

## 目标
新建 core-journal-three-conflicts 节点：保序/空间/回收三矛盾场景化讲解。

## 功能需求
1. 基于教学讲解内容编写节点，每矛盾含场景/冲突/解法三段
2. 三查 + validate 全绿

## 非功能需求
- 真实时间戳；只增修 .md

## 验收标准
- [ ] AC-1 节点内容详实，三矛盾场景化且有代码依据
- [ ] AC-2 三查 0 issues，validate 全绿
- [ ] AC-3 证据登记进Check归档

### 声明的测试接缝
- seam: scripts/ontology-validate.py -> ontology/domain/core-journal-three-conflicts.md

## 风险与对策
- 风险：与现有 journal 节点重复。对策：本节点只讲场景化教学，不讲机制细节
