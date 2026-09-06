# EC四讲本体生产

## 背景
教学 EC 四讲（写洞/生命期/修复/重建）获用户确认，要求记录为本体。

## 目标
新建 core-ec-four-lectures 节点：四讲收束 + 教学路径。

## 功能需求
1. 基于四讲内容编写节点，每讲一句话 + 详述索引
2. 三查 + validate 全绿

## 非功能需求
- 真实时间戳；只增修 .md

## 验收标准
- [ ] AC-1 节点内容详实，四讲收束有代码依据
- [ ] AC-2 三查 0 issues，validate 全绿
- [ ] AC-3 证据登记进Check归档

### 声明的测试接缝
- seam: scripts/ontology-validate.py -> ontology/domain/core-ec-four-lectures.md

## 风险与对策
- 风险：与 EC 指南/修复节点重复。对策：本节点只做教学收束，不讲机制细节
