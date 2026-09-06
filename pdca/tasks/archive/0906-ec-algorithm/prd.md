# EC算法三层本体生产

## 背景
用户指出缺少 EC 算法本身本体，确认三层全建：RS 数学原理、条带几何布局、分配 widen 算法。

## 目标
新建 3 个 domain 节点：rs-math、stripe-geometry、stripe-alloc-widen。

## 功能需求
1. RS 数学：伽罗瓦域/P/Q 生成/syndrome 解码（对照 io.c 调用语义）
2. 条带几何：bch_stripe 结构/can_widen/nr_blocks/sectors（对照 format.h）
3. 分配 widen：centroid/离群重分配/拓宽（对照 create.c）
4. 三查 + validate 全绿

## 非功能需求
- 真实时间戳；只增修 .md

## 验收标准
- [ ] AC-1 三节点内容详实，每层有代码依据
- [ ] AC-2 三查 0 issues，validate 全绿
- [ ] AC-3 证据登记进Check归档

### 声明的测试接缝
- seam: scripts/ontology-validate.py -> ontology/domain/core-ec-rs-*.md

## 风险与对策
- 风险：RS 数学超出代码范围。对策：只讲 bcachefs 用到的子集（P/Q各一），不展开通用编码理论
