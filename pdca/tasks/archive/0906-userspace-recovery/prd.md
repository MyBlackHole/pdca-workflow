# 用户态恢复运维工具本体化

## 背景
20 轮规划第 2 轮。T0490 深挖 fsck/scrub/reconcile/usage 机制但未建本体。本次沉淀（基于现树核实）。

## 目标
深挖 fsck 双向中继、scrub 进度、reconcile 双模、usage 矩阵；新增至少 2 个不重复 domain 节点。

## 功能需求
1. 深挖 src/commands/fsck.rs、scrub.rs、reconcile.rs、fs_usage.rs，每条带 file:line 佐证
2. 新增至少 2 个 domain 节点，specializes ontology:domain/core
3. 全量 ontology-validate.py 0 issues

## 非功能需求
- 只读分析；真实时间戳；只增修 .md

## 验收标准
- [ ] AC-1 深挖每条有代码位置佐证
- [ ] AC-2 新增至少 2 个不重复 domain 节点且 frontmatter 合法
- [ ] AC-3 关联单向无环，有据可查
- [ ] AC-4 validate 全量 0 issues，信号非泛化，引用无空悬

### 声明的测试接缝
- seam: scripts/ontology-validate.py -> ontology/domain/core-*.md（新增节点）

## 风险与对策
- 风险：本地 main 落后导致机制与 T0490 描述不一致。对策：按现树核实为准
