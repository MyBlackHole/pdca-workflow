# 分配自愈模式提炼pattern

## 背景
20 轮规划第 6 轮。从分配器与自愈 domain 节点提炼 pattern。

## 目标
提炼至少 2 个 pattern 节点（WFQ 加权分配、分级自愈调度、统一搬迁候选）。

## 功能需求
1. 重读源 domain 节点，提炼问题方案后果三要素
2. 新增至少 2 个 pattern 节点，type=pattern，specializes ontology:pattern
3. 全量 ontology-validate.py 0 issues

## 非功能需求
- 只读分析；真实时间戳；只增修 .md

## 验收标准
- [ ] AC-1 每个pattern有源节点与代码依据
- [ ] AC-2 新增至少 2 个不重复 pattern 节点且 frontmatter 合法
- [ ] AC-3 关联单向无环，有据可查
- [ ] AC-4 validate 全量 0 issues，信号非泛化，引用无空悬

### 声明的测试接缝
- seam: scripts/ontology-validate.py -> ontology/pattern/*.md（新增节点）

## 风险与对策
- 风险：pattern 与源 domain 重复。对策：体裁区分
