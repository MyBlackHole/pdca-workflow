# 原则节点提炼

## 背景
20 轮规划第 7 轮。从兼容、可观测、失败语义 domain 节点提炼 principle。

## 目标
提炼至少 2 个 principle 节点（兼容审慎、可观测优先、显式失败候选）。

## 功能需求
1. 重读源 domain 节点，提炼原则陈述
2. 新增至少 2 个 principle 节点，type=principle，specializes ontology:principle
3. 全量 ontology-validate.py 0 issues

## 非功能需求
- 只读分析；真实时间戳；只增修 .md

## 验收标准
- [ ] AC-1 每个principle有源节点依据
- [ ] AC-2 新增至少 2 个不重复 principle 节点且 frontmatter 合法
- [ ] AC-3 关联单向无环，有据可查
- [ ] AC-4 validate 全量 0 issues，信号非泛化，引用无空悬

### 声明的测试接缝
- seam: scripts/ontology-validate.py -> ontology/principle/*.md（新增节点）

## 风险与对策
- 风险：principle 与源 domain 重复。对策：原则陈述体裁，不复述机制
