# 泄漏pin讲解本体生产

## 背景
教学中校验封条深讲获用户确认，要求记录"泄漏 pin 换正确性"讲解为本体。

## 目标
新建 core-journal-pin-leak-tradeoff 节点：借条语义/错误泄漏/空间换正确性。

## 功能需求
1. 基于教学讲解编写节点，场景/冲突/决策三段
2. 三查 + validate 全绿

## 非功能需求
- 真实时间戳；只增修 .md

## 验收标准
- [ ] AC-1 节点内容详实，有代码依据
- [ ] AC-2 三查 0 issues，validate 全绿
- [ ] AC-3 证据登记进Check归档

### 声明的测试接缝
- seam: scripts/ontology-validate.py -> ontology/domain/core-journal-pin-leak-tradeoff.md

## 风险与对策
- 风险：与 Pin 钉住节点重复。对策：本节点只讲错误路径权衡，不讲正常钉住机制
